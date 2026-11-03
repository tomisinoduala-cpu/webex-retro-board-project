/*
 * Copyright (c) 2026 Cisco Systems, Inc. and/or its affiliates
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/*
 * Team Retro Board — Webex Embedded App
 * Organised into four areas:
 *   1) webexHelper  — everything that talks to the Webex SDK
 *   2) State        — the board data + how it changes (+ persistence)
 *   3) Render       — turning state into DOM
 *   4) Events       — wiring buttons/forms to state, then re-rendering
 */

// ----- The three columns, defined once -----
const COLUMNS = ["start", "stop", "continue"];

// ----- App state: one object holds the whole board -----
let board = { cards: [] };
let sharedMode = false;
let boardSocket = null;
let reconnectTimer = null;

/* =========================================================
 * 1) WEBEX SDK HELPER
 * Wraps the v2 Embedded Apps SDK so the rest of the app
 * doesn't need to know SDK details.
 * ========================================================= */
const webexHelper = {
  app: null,

  // Create the SDK app object and wait until it's ready.
  async init() {
    if (!window.webex || !window.webex.Application) {
      console.warn("Webex SDK not found — running outside Webex? UI still works.");
      return false;
    }
    this.app = new window.webex.Application();
    await this.app.onReady();
    return true;
  },

  // Read the signed-in user's display name (may be empty if PII disabled).
  getUserName() {
    try {
      const user = this.app && this.app.application.states.user;
      if (user && user.displayName) return user.displayName;
    } catch (e) {
      // fall through to default
    }
    return "there";
  },

  // Apply LIGHT/DARK theme to the page by setting a data attribute.
  applyTheme(theme) {
    const value = theme === "DARK" ? "DARK" : "LIGHT";
    document.documentElement.dataset.theme = value;
    const badge = document.getElementById("theme-badge");
    if (badge) badge.textContent = value;
  },

  // Match Webex's theme now, and keep matching when the user changes it.
  watchTheme() {
    if (!this.app) return;
    this.applyTheme(this.app.theme);
    this.app.listen().then(() => {
      this.app.on("application:themeChanged", (theme) => this.applyTheme(theme));
    }).catch((reason) => console.warn("Could not listen for theme changes:", reason));
  },

  // Share the board with everyone in the meeting/space.
  shareBoard() {
    if (!this.app) {
      alert("Sharing only works when the app is running inside Webex.");
      return;
    }
    if (this.app.isShared) return; // already shared — do nothing
    const url = window.location.href;
    this.app.setShareUrl(url, "", "Team Retro Board")
      .catch((code) => console.warn("setShareUrl failed:", code));
  },
};

/* =========================================================
 * 2) STATE — how the board changes
 * ========================================================= */

// Make a reasonably unique id for a new card.
function makeId() {
  return "c_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
}

// Add a card to a column. Returns the new card, or null if rejected.
function addCard(text, column) {
  const clean = (text || "").trim();
  if (clean === "") return null;                 // validation: no empty cards
  if (!COLUMNS.includes(column)) return null;    // validation: real column only
  if (sharedMode) {
    const sent = sendSharedAction({
      type: "add",
      text: clean,
      column,
      author: webexHelper.getUserName(),
    });
    return sent ? { pending: true } : null;
  }
  const card = {
    id: makeId(),
    text: clean,
    column: column,
    votes: 0,
    author: webexHelper.getUserName(),
  };
  board.cards.push(card);
  saveState();
  return card;
}

// Delete a card by its unique id.
function deleteCard(id) {
  if (sharedMode) {
    sendSharedAction({ type: "delete", id });
    return;
  }
  board.cards = board.cards.filter((card) => card.id !== id);
  saveState();
}

// Add one vote to a card by id.
function voteCard(id) {
  if (sharedMode) {
    sendSharedAction({ type: "vote", id });
    return;
  }
  const card = board.cards.find((c) => c.id === id);
  if (card) {
    card.votes += 1;
    saveState();
  }
}

// Persist locally when the static app is used. The Node server stores shared state
// in its own JSON file and sends updates over a WebSocket instead.
function saveState() {
  if (sharedMode) return;
  try {
    localStorage.setItem("retroBoard", JSON.stringify(board));
  } catch (e) {
    console.warn("Could not save board:", e);
  }
}

async function loadState() {
  try {
    const response = await fetch("/api/board", { cache: "no-store" });
    if (!response.ok) throw new Error("Shared board server is unavailable");
    const saved = await response.json();
    if (!saved || !Array.isArray(saved.cards)) {
      throw new Error("Shared board response is invalid");
    }
    board = saved;
    sharedMode = true;
    setConnectionStatus("Connecting to shared board…");
    connectSharedBoard();
    return;
  } catch (e) {
    sharedMode = false;
    setConnectionStatus("Local only — start the Node server to share this board");
  }

  try {
    const saved = localStorage.getItem("retroBoard");
    if (saved) board = JSON.parse(saved);
  } catch (e) {
    console.warn("Could not load board:", e);
    board = { cards: [] };
  }
}

function setConnectionStatus(message) {
  const status = document.getElementById("sync-status");
  if (status) status.textContent = message;
}

function connectSharedBoard() {
  if (!sharedMode) return;
  if (reconnectTimer) clearTimeout(reconnectTimer);

  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  const socket = new WebSocket(scheme + "//" + window.location.host + "/ws");
  boardSocket = socket;

  socket.addEventListener("open", () => {
    setConnectionStatus("Shared board connected");
  });

  socket.addEventListener("message", (event) => {
    try {
      const message = JSON.parse(event.data);
      if (message.type === "board" && message.board && Array.isArray(message.board.cards)) {
        board = message.board;
        renderBoard();
      }
    } catch (e) {
      console.warn("Could not read shared board update:", e);
    }
  });

  socket.addEventListener("close", () => {
    if (boardSocket === socket && sharedMode) {
      setConnectionStatus("Reconnecting to shared board…");
      reconnectTimer = setTimeout(connectSharedBoard, 2000);
    }
  });

  socket.addEventListener("error", () => socket.close());
}

function sendSharedAction(action) {
  if (!boardSocket || boardSocket.readyState !== WebSocket.OPEN) {
    setConnectionStatus("Shared board is reconnecting — please try again");
    return false;
  }
  boardSocket.send(JSON.stringify(action));
  return true;
}

/* =========================================================
 * 3) RENDER — turning state into DOM
 * ========================================================= */

// Escape user text so it can't inject HTML into the page.
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// Build the DOM element for a single card.
function createCardElement(card) {
  const li = document.createElement("li");
  li.className = "card";
  li.dataset.id = card.id;
  li.innerHTML =
    '<p class="card-text">' + escapeHtml(card.text) + "</p>" +
    '<div class="card-footer">' +
      '<span class="card-author">' + escapeHtml(card.author) + "</span>" +
      '<span class="card-actions">' +
        '<button type="button" class="vote-btn">▲ <span class="vote-count">' + card.votes + "</span></button>" +
        '<button type="button" class="delete-btn">Delete</button>' +
      "</span>" +
    "</div>";
  return li;
}

// Render one column's cards.
function renderColumn(columnKey) {
  const section = document.querySelector('.column[data-column="' + columnKey + '"]');
  if (!section) return;
  const list = section.querySelector(".card-list");
  list.innerHTML = "";
  board.cards
    .filter((card) => card.column === columnKey)
    .forEach((card) => list.appendChild(createCardElement(card)));
}

// Update the little count badge on each column.
function updateCounts() {
  COLUMNS.forEach((key) => {
    const section = document.querySelector('.column[data-column="' + key + '"]');
    if (!section) return;
    const count = board.cards.filter((card) => card.column === key).length;
    section.querySelector(".column-count").textContent = count;
  });
}

// Render the whole board.
function renderBoard() {
  COLUMNS.forEach((key) => renderColumn(key));
  updateCounts();
}

/* =========================================================
 * 4) EVENTS — wire the UI to state, then re-render
 * ========================================================= */

function wireEvents() {
  // Add card form
  const form = document.getElementById("add-form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const textEl = document.getElementById("card-text");
    const columnEl = document.getElementById("column-select");
    const added = addCard(textEl.value, columnEl.value);
    if (added) {
      textEl.value = "";
      renderBoard();
    }
  });

  // Vote / delete via event delegation on the board
  document.querySelector(".board").addEventListener("click", (e) => {
    const cardEl = e.target.closest(".card");
    if (!cardEl) return;
    const id = cardEl.dataset.id;
    if (e.target.closest(".delete-btn")) {
      deleteCard(id);
      renderBoard();
    } else if (e.target.closest(".vote-btn")) {
      voteCard(id);
      renderBoard();
    }
  });

  // Share button
  document.getElementById("share-btn")
    .addEventListener("click", () => webexHelper.shareBoard());

  // Timer button (simple 5-minute countdown)
  wireTimer();
}

function wireTimer() {
  const btn = document.getElementById("timer-btn");
  const display = document.getElementById("timer-display");
  let remaining = 5 * 60;
  let handle = null;

  function format(s) {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return String(m).padStart(2, "0") + ":" + String(sec).padStart(2, "0");
  }

  btn.addEventListener("click", () => {
    if (handle) {                      // running -> stop/reset
      clearInterval(handle);
      handle = null;
      remaining = 5 * 60;
      display.hidden = true;
      btn.textContent = "Start 5-min timer";
      return;
    }
    remaining = 5 * 60;
    display.hidden = false;
    display.textContent = format(remaining);
    btn.textContent = "Stop timer";
    handle = setInterval(() => {
      remaining -= 1;
      display.textContent = format(remaining);
      if (remaining <= 0) {
        clearInterval(handle);
        handle = null;
        btn.textContent = "Start 5-min timer";
      }
    }, 1000);
  });
}

/* =========================================================
 * BOOTSTRAP
 * ========================================================= */
async function init() {
  await loadState();
  wireEvents();
  renderBoard();

  const ready = await webexHelper.init();
  if (ready) {
    document.getElementById("greeting").textContent = webexHelper.getUserName();
    webexHelper.watchTheme();
  }
}

document.addEventListener("DOMContentLoaded", init);
