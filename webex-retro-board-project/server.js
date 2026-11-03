/*
 * Copyright (c) 2026 Cisco Systems, Inc. and/or its affiliates
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const http = require("node:http");
const path = require("node:path");
const { WebSocketServer, WebSocket } = require("ws");

const PORT = Number(process.env.PORT) || 3000;
const DATA_DIR = path.join(__dirname, "data");
const DATA_FILE = path.join(DATA_DIR, "board.json");
const COLUMNS = new Set(["start", "stop", "continue"]);
const MAX_CARD_LENGTH = 500;
const MAX_MESSAGE_BYTES = 16 * 1024;

let board = { cards: [] };
let writeQueue = Promise.resolve();

const staticFiles = {
  "/": ["index.html", "text/html; charset=utf-8"],
  "/index.html": ["index.html", "text/html; charset=utf-8"],
  "/app.js": ["app.js", "text/javascript; charset=utf-8"],
  "/styles.css": ["styles.css", "text/css; charset=utf-8"],
};

function sendJson(response, statusCode, value) {
  response.writeHead(statusCode, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  response.end(JSON.stringify(value));
}

async function loadBoard() {
  try {
    const saved = JSON.parse(await fs.readFile(DATA_FILE, "utf8"));
    if (saved && Array.isArray(saved.cards)) board = saved;
  } catch (error) {
    if (error.code !== "ENOENT") {
      console.warn("Could not read saved board; starting with an empty board:", error);
    }
  }
}

async function saveBoard() {
  await fs.mkdir(DATA_DIR, { recursive: true });
  const temporaryFile = DATA_FILE + ".tmp";
  await fs.writeFile(temporaryFile, JSON.stringify(board, null, 2), "utf8");
  await fs.rename(temporaryFile, DATA_FILE);
}

function applyAction(action) {
  if (!action || typeof action !== "object") return false;

  if (action.type === "add") {
    const text = typeof action.text === "string" ? action.text.trim() : "";
    if (!text || text.length > MAX_CARD_LENGTH || !COLUMNS.has(action.column)) {
      return false;
    }
    const author = typeof action.author === "string" ? action.author.trim() : "";
    board.cards.push({
      id: crypto.randomUUID(),
      text,
      column: action.column,
      votes: 0,
      author: author.slice(0, 80) || "Guest",
    });
    return true;
  }

  if (action.type === "delete") {
    const remaining = board.cards.filter((card) => card.id !== action.id);
    if (remaining.length === board.cards.length) return false;
    board.cards = remaining;
    return true;
  }

  if (action.type === "vote") {
    const card = board.cards.find((item) => item.id === action.id);
    if (!card) return false;
    card.votes += 1;
    return true;
  }

  return false;
}

function broadcastBoard() {
  const message = JSON.stringify({ type: "board", board });
  for (const client of webSockets.clients) {
    if (client.readyState === WebSocket.OPEN) client.send(message);
  }
}

const server = http.createServer(async (request, response) => {
  const url = new URL(request.url, "http://localhost");

  if (url.pathname === "/api/board") {
    if (request.method !== "GET") {
      sendJson(response, 405, { error: "Method not allowed" });
      return;
    }
    sendJson(response, 200, board);
    return;
  }

  const file = staticFiles[url.pathname];
  if (request.method === "GET" && file) {
    try {
      const contents = await fs.readFile(path.join(__dirname, file[0]));
      response.writeHead(200, {
        "Content-Type": file[1],
        "Cache-Control": "no-store",
      });
      response.end(contents);
    } catch (error) {
      sendJson(response, 500, { error: "Could not load app file" });
    }
    return;
  }

  sendJson(response, 404, { error: "Not found" });
});

const webSockets = new WebSocketServer({ noServer: true, maxPayload: MAX_MESSAGE_BYTES });

server.on("upgrade", (request, socket, head) => {
  const url = new URL(request.url, "http://localhost");
  if (url.pathname !== "/ws") {
    socket.destroy();
    return;
  }
  webSockets.handleUpgrade(request, socket, head, (webSocket) => {
    webSockets.emit("connection", webSocket);
  });
});

webSockets.on("connection", (webSocket) => {
  webSocket.send(JSON.stringify({ type: "board", board }));

  webSocket.on("message", (data, isBinary) => {
    if (isBinary) return;
    let action;
    try {
      action = JSON.parse(data.toString());
    } catch (error) {
      return;
    }

    writeQueue = writeQueue
      .then(async () => {
        if (!applyAction(action)) return;
        await saveBoard();
        broadcastBoard();
      })
      .catch((error) => console.error("Could not save board update:", error));
  });
});

loadBoard().then(() => {
  server.listen(PORT, "0.0.0.0", () => {
    console.log(`Retro board server running at http://localhost:${PORT}`);
    console.log("Open this page in another browser to try shared updates.");
  });
});
