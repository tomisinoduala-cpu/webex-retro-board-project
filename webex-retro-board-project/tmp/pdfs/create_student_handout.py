from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Preformatted,
)

OUT = "/Users/tomrobin/T-Level-Projects/webex-retro-board-project/output/pdf/webex-retro-board-student-guide.pdf"
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#087E9B")
CYAN = colors.HexColor("#DDF5F7")
MINT = colors.HexColor("#E7F5EF")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#526579")
PALE = colors.HexColor("#F2F6F9")
GOLD = colors.HexColor("#F2B544")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=29, leading=34, textColor=WHITE, alignment=TA_LEFT, spaceAfter=8))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=19, textColor=colors.HexColor("#D9EEF4")))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=21, leading=25, textColor=NAVY, spaceBefore=0, spaceAfter=8))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=BLUE, spaceBefore=9, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.5, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.2, leading=11, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="Bulletx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=12.8, textColor=INK, leftIndent=12, firstLineIndent=-8, bulletIndent=0, spaceAfter=3))
styles.add(ParagraphStyle(name="CodeBlock", fontName="Courier", fontSize=9, leading=13, textColor=WHITE, backColor=NAVY, borderPadding=9, leftIndent=6, rightIndent=6, spaceBefore=3, spaceAfter=7))
styles.add(ParagraphStyle(name="Callout", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=NAVY, backColor=CYAN, borderPadding=8, spaceBefore=4, spaceAfter=7))
styles.add(ParagraphStyle(name="WhiteSmall", fontName="Helvetica", fontSize=9, leading=13, textColor=WHITE))
styles.add(ParagraphStyle(name="TileHead", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=NAVY))
styles.add(ParagraphStyle(name="TileBody", fontName="Helvetica", fontSize=8.5, leading=11.4, textColor=INK))

def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])

def bullets(items):
    rows = [[Paragraph("- " + item, styles["Bulletx"])] for item in items]
    t = Table(rows, colWidths=[174*mm])
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0), ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
    return t

def code(text):
    t = Table([[Preformatted(text, styles["CodeBlock"])]], colWidths=[174*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    return t

def box(content, bg=PALE, width=174*mm, padding=9):
    if not isinstance(content, list):
        content = [content]
    t = Table([[content]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#D7E2EA")),
        ("LEFTPADDING", (0,0), (-1,-1), padding),
        ("RIGHTPADDING", (0,0), (-1,-1), padding),
        ("TOPPADDING", (0,0), (-1,-1), padding),
        ("BOTTOMPADDING", (0,0), (-1,-1), padding),
    ]))
    return t

def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, h-14*mm, w, 14*mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18*mm, h-9*mm, "WEBEX RETRO BOARD  /  STUDENT GUIDE")
        canvas.setFillColor(GOLD)
        canvas.circle(w-18*mm, h-7*mm, 2*mm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#D7E2EA"))
    canvas.line(18*mm, 14*mm, w-18*mm, 14*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(18*mm, 9*mm, "Build it. Debug it. Make it yours.")
    canvas.drawRightString(w-18*mm, 9*mm, str(doc.page))
    canvas.restoreState()

class HandoutDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=22*mm, bottomMargin=20*mm, title="Webex Retro Board - Student Guide", author="Webex Retro Board Project")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=header_footer)])

story = []

# Cover and project overview
cover = Table([[[
    P("WEBEX EMBEDDED APP WORKSHOP", "WhiteSmall"),
    Spacer(1, 13*mm),
    P("Build a team<br/>retro board", "CoverTitle"),
    P("A student guide to exploring a real codebase, fixing bugs, and creating an app that runs inside Webex.", "CoverSub"),
    Spacer(1, 11*mm),
    P("FOUR TASKS  ·  ONE TEAM PROJECT  ·  YOUR OWN APP AT THE END", "WhiteSmall"),
]]], colWidths=[174*mm], rowHeights=[78*mm])
cover.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), NAVY),
    ("LEFTPADDING", (0,0), (-1,-1), 11*mm), ("RIGHTPADDING", (0,0), (-1,-1), 11*mm),
    ("TOPPADDING", (0,0), (-1,-1), 8*mm), ("BOTTOMPADDING", (0,0), (-1,-1), 8*mm),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
]))
story += [Spacer(1, 4*mm), cover, Spacer(1, 8*mm), P("What you are building", "H1x"),
          P("A <b>retrospective</b> is a team meeting to reflect on how work is going. This project gives your team a shared board with three columns: <b>Start</b>, <b>Stop</b>, and <b>Continue</b>. Add cards, vote on ideas, and discuss what to improve."),
          P("You will work with HTML, CSS, JavaScript, a small Node.js server, and the Webex Embedded Apps SDK. The project follows a typical engineering journey: get an existing app running, understand it, improve it, then design something of your own."),
          P("Your route through the workshop", "H2x")]
tiles = [
    [P("01  GET STARTED", "TileHead"), P("Run Hello Retro locally and open it in Webex.", "TileBody")],
    [P("02  EXPLORE", "TileHead"), P("Trace how events, state, and rendering fit together.", "TileBody")],
    [P("03  IMPROVE", "TileHead"), P("Investigate behaviour, fix bugs, and add features.", "TileBody")],
    [P("04  CREATE", "TileHead"), P("Build an embedded app idea and present your work.", "TileBody")],
]
grid = Table([[tiles[0], tiles[1]], [tiles[2], tiles[3]]], colWidths=[87*mm,87*mm], rowHeights=[22*mm,22*mm])
grid.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), PALE), ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#D7E2EA")),
    ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#D7E2EA")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story += [grid, Spacer(1, 7*mm), P("What you need", "H2x"),
          P("Install <b>Git</b>, <b>Node.js (LTS)</b>, and a code editor such as VS Code. You will also need a GitHub account, <b>cloudflared</b> for a temporary HTTPS tunnel, and access to a <b>Webex Developer Sandbox</b>. A standard free Webex account cannot create embedded apps."),
          P('Install links: <link href="https://git-scm.com/download/" color="#087E9B">Git</link> · <link href="https://nodejs.org/" color="#087E9B">Node.js</link> · <link href="https://code.visualstudio.com/" color="#087E9B">VS Code</link> · <link href="https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" color="#087E9B">cloudflared</link>', "Smallx"),
          P("Work in teams: one person can host the shared board. Each student can still run a separate local copy for development.", "Callout"), PageBreak()]

# Task 1 setup
story += [P("Task 1  /  Set up and run Hello Retro", "H1x"),
          P("Start by getting the project running on your computer. You will run the app locally for quick feedback, then use a temporary public URL so Webex can load it."),
          P("1. Fork and clone the project", "H2x"),
          P("Use the <b>Fork</b> button on the project’s GitHub page. Clone your copy, then enter the project folder:"),
          code("git clone https://github.com/<your-username>/webex-retro-board-project.git\ncd webex-retro-board-project\nls"),
          P("The main app files are <font name='Courier'>index.html</font>, <font name='Courier'>styles.css</font>, and <font name='Courier'>app.js</font>."),
          P("2. Install dependencies and start the app", "H2x"),
          code("npm install\nnpm start"),
          P("Open <font name='Courier'>http://localhost:3000</font>. Look for <b>Shared board connected</b>. The server stores the board in <font name='Courier'>data/board.json</font>, so it survives a restart. Run <font name='Courier'>npm install</font> once; run <font name='Courier'>npm start</font> whenever you work on the project."),
          P("A warning that the Webex SDK is unavailable in a normal browser is expected. The rest of the app still works."),
          P("3. Set up a Developer Sandbox", "H2x"),
          P("Embedded apps need a licensed Webex organisation. One person on your team should request a free sandbox from the <link href='https://developer.webex.com/docs/developer-sandbox-guide' color='#087E9B'>Developer Sandbox guide</link>. Use an email address that is not already registered with Webex; a plus alias can help. The sandbox admin adds teammates in <link href='https://admin.webex.com' color='#087E9B'>Control Hub</link> (up to 10 people). Everyone signs into Webex with their sandbox account."),
          P("4. Give Webex a temporary public address", "H2x"),
          P("Keep <font name='Courier'>npm start</font> running. Open a second Terminal window and start a Quick Tunnel:"),
          code("cloudflared tunnel --url http://localhost:3000"),
          P("When a URL appears, open it in a browser and check that the board loads. Keep both Terminal windows open. The tunnel URL is temporary and may change when restarted."),
          P("<b>Shared team board:</b> One person runs the Node server and tunnel, then shares the URL. Everyone visiting it sees the same live board. The host computer must stay on. Anyone with the URL can change the trial board, so use demo data only and stop the tunnel when finished.", "Callout"),
          PageBreak()]

# Webex app and static alternative
story += [P("Task 1  /  Open the app in Webex", "H1x"),
          P("5. Create an Embedded App", "H2x"),
          P("Sign in to <link href='https://developer.webex.com' color='#087E9B'>developer.webex.com</link> with your sandbox account. Open <b>My Webex Apps → Create a New App → Create Embedded App</b>, then enter:"),
          bullets([
              "<b>Where does your app work?</b> Select Meeting and Messaging.",
              "<b>App name:</b> for example, Team Retro Board.",
              "<b>Start Page URL:</b> your current tunnel URL plus <font name='Courier'>/index.html</font>.",
              "<b>Valid domains:</b> only the tunnel host, without <font name='Courier'>https://</font> or a path."
          ]),
          P("Example: if your tunnel is <font name='Courier'>https://some-words.trycloudflare.com</font>, use <font name='Courier'>https://some-words.trycloudflare.com/index.html</font> as the Start Page URL and <font name='Courier'>some-words.trycloudflare.com</font> as the valid domain."),
          P("6. Launch it", "H2x"),
          bullets([
              "In the Webex desktop app, start a meeting or open a space.",
              "Open the Apps area and find your in-development app.",
              "Choose <b>Open and share my personal information</b>. The greeting should include your name."
          ]),
          box([P("If it does not load", "TileHead"), P("First open the tunnel URL in a browser. Check that the Node server and tunnel are running, the Start Page URL ends in <font name='Courier'>/index.html</font>, and the valid domain matches the current tunnel host. If the tunnel restarted, update the app settings. Make sure you are signed into the sandbox account.", "TileBody")], CYAN),
          P("Static demo option: GitHub Pages", "H2x"),
          P("For a front-end-only demo, deploy the <font name='Courier'>main</font> branch from the repository root using <b>Settings → Pages</b>. Use the Pages URL plus <font name='Courier'>/index.html</font> as the Start Page URL, and its host as the valid domain. Pages has a stable URL, but changes appear after pushing and deployment; without the Node backend, each browser stores its own board."),
          P("The name says ‘Hi there’?", "H2x"),
          P("That is expected in a regular browser. Inside Webex, the app needs permission to access your name. Reopen it and grant the personal information permission; if needed, close and reopen the app because embedded apps can cache content."),
          P("Keep your local server running while you develop. Most changes can be tried in a browser at <font name='Courier'>http://localhost:3000</font>.", "Callout"), PageBreak()]

# Task 2 understanding and debugging
story += [P("Task 2  /  Explore the code", "H1x"),
          P("Open <font name='Courier'>app.js</font>. Follow one action from the user interface through the code and back to the screen."),
          P("Four areas to know", "H2x")]
areas = [
    [P("WEBEX SDK HELPER", "TileHead"), P("Gets user details, applies the theme, and shares the app.", "TileBody")],
    [P("STATE", "TileHead"), P("Stores the board and handles add, delete, vote, save, and load.", "TileBody")],
    [P("RENDER", "TileHead"), P("Turns board data into cards, columns, and counts on screen.", "TileBody")],
    [P("EVENTS", "TileHead"), P("Connects clicks and form submissions to state changes and rendering.", "TileBody")],
]
at = Table([[areas[0], areas[1]], [areas[2], areas[3]]], colWidths=[87*mm,87*mm], rowHeights=[19*mm,19*mm])
at.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,-1),PALE),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#D7E2EA")),("INNERGRID",(0,0),(-1,-1),0.5,colors.HexColor("#D7E2EA")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6)]))
story += [at, P("Example: adding a card", "H2x"),
          P("The form event in <font name='Courier'>wireEvents()</font> calls <font name='Courier'>addCard()</font>. That updates the board state, then <font name='Courier'>renderBoard()</font> draws the updated board."),
          P("Explore the shared board", "H2x"),
          bullets(["Add a card to Start, Stop, and Continue.", "Vote on a teammate’s card and delete a card.", "Open the same host URL on another screen. Do the changes appear there too?"]),
          P("Debug with a plan", "H2x"),
          bullets([
              "Reproduce the issue and note what you expected versus what happened.",
              "Use the browser developer tools: F12 or Ctrl+Shift+I (Windows/Linux), Cmd+Option+I (Mac). In Webex, right-click inside the embedded app and choose Inspect if available.",
              "Check the Console for errors. The SDK warning in a normal browser is expected.",
              "Use Sources to set a breakpoint in <font name='Courier'>app.js</font>; inspect Variables and Call Stack while stepping through the action.",
              "Use Network to check <font name='Courier'>GET /api/board</font> and the <font name='Courier'>/ws</font> WebSocket. Use Elements to inspect layout."
          ]),
          P("VS Code debugging", "H2x"),
          P("Open the project folder and choose a configuration under <b>Run and Debug</b>, then press F5. <b>Debug Node backend</b> runs <font name='Courier'>server.js</font> (stop any server already on port 3000 first). <b>Debug Retro Board in Chrome</b> uses the running local server; set breakpoints in <font name='Courier'>app.js</font>."),
          P("Temporary logs can help you follow the flow. Add a small <font name='Courier'>console.log()</font> near the event, state change, and render, then remove it when you are done. Backend messages appear in the terminal running <font name='Courier'>npm start</font>.", "Callout"), PageBreak()]

# Task 3 challenges
story += [P("Task 3  /  Fix and extend the board", "H1x"),
          P("Before changing the code, try the board as a group. Make a prediction, test it, then agree on what behaviour would be better."),
          P("Part A: investigate", "H2x"),
          bullets([
              "What happens if one person votes on the same card several times?",
              "What happens to the five-minute timer after a page refresh?",
              "What if two people start a timer on their own screens?",
              "What happens if you delete a card someone else added?"
          ]),
          P("Exercise: make votes count once per person", "H2x"),
          P("Change <font name='Courier'>voteCard</font> so a person can vote only once on each card. The app will need to remember who voted, not only a number of votes. Inspect how <font name='Courier'>card.votes</font> is represented in the State area."),
          P("Part B: add features", "H2x"),
          P("1. Sort cards by votes", "H2x"),
          P("Show the most-voted cards first in each column. When votes change, the card order should update. Look at <font name='Courier'>renderColumn()</font>; sorting can happen when cards are drawn."),
          P("2. Let people delete their own cards", "H2x"),
          P("Use <font name='Courier'>card.author</font> and <font name='Courier'>webexHelper.getUserName()</font> to check who created a card. Update the delete action and consider hiding the delete button on cards belonging to others."),
          P("3. Add a facilitator action to complete the retro", "H2x"),
          P("Add a <b>Complete retro</b> button that summarizes the top-voted card or tied cards in each column, then clears the board for everyone. Show it only to the meeting host or co-host."),
          bullets([
              "Find the current role using the Webex SDK <font name='Courier'>meeting:roleChanged</font> event.",
              "Find the top card(s) in each column from the board state.",
              "Add a clear action alongside add, delete, and vote. In shared mode, update <font name='Courier'>server.js</font> <font name='Courier'>applyAction</font> too.",
              "Use the role to show or hide the button. Discuss why a browser-only role check is not production security."
          ]),
          P("Bonus: make the timer shared", "H2x"),
          P("Move timer data into the shared board so everyone sees the same countdown and refreshes do not reset it. Store an end timestamp rather than only a remaining-seconds number; clients can calculate the remaining time locally. Add an action so timer changes are broadcast by the server."),
          P("Stretch challenge: post the summary to the Webex space", "H2x"),
          P("Use the Webex Messages API to post the completion summary. This needs an OAuth Integration with <font name='Courier'>spark:messages_write</font>, the space ID, and a server-side token exchange. Read the <link href='https://developer.webex.com/docs/api/v1/messages' color='#087E9B'>Messages API guide</link> and plan the authorization flow before coding."),
          box([P("Safe team demo", "TileHead"), P("The trial backend has no login. The role check is a user interface guard, not authorization enforced by the server. Keep the tunnel temporary and use demo data.", "TileBody")], MINT), PageBreak()]

# Task 4 and checklist
story += [P("Task 4  /  Make it your own", "H1x"),
          P("Use what you have learned to design a new embedded app. Pick a small problem your team could solve during a meeting."),
          P("Ideas to get you started", "H2x"),
          bullets([
              "Planning poker for estimating work items.",
              "A stand-up board for yesterday, today, and blockers.",
              "A team icebreaker or quiz to start a meeting."
          ]),
          P("Explore more ideas in the <link href='https://apphub.webex.com/embedded-apps' color='#087E9B'>Webex App Hub Embedded Apps</link>."),
          P("Prepare your presentation", "H2x"),
          bullets([
              "Demo your new embedded app running inside Webex.",
              "Explain one issue you found in the retro board and how you tracked it down.",
              "Show a feature you added and explain the choices you made."
          ]),
          P("Team check-in", "H2x")]
check = [
    [P("[ ]", "TileHead"), P("The retro board runs at localhost:3000.", "TileBody")],
    [P("[ ]", "TileHead"), P("The team can open the same shared board URL.", "TileBody")],
    [P("[ ]", "TileHead"), P("We traced an action through events, state, and render.", "TileBody")],
    [P("[ ]", "TileHead"), P("We tested and discussed the behaviour we changed.", "TileBody")],
    [P("[ ]", "TileHead"), P("We can demo our own app and describe our decisions.", "TileBody")],
]
ct = Table(check, colWidths=[12*mm,162*mm])
ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PALE),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#D7E2EA")),("INNERGRID",(0,0),(-1,-1),0.4,colors.HexColor("#D7E2EA")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
story += [ct, Spacer(1, 8*mm),
          box([P("The engineering loop", "TileHead"), P("Observe -> make a prediction -> trace the code -> try a change -> check the result -> explain what you learned.", "TileBody")], CYAN),
          Spacer(1, 7*mm), P("Project resources", "H2x"),
          P('<link href="https://developer.webex.com/docs/developer-sandbox-guide" color="#087E9B">Request a Developer Sandbox</link>  ·  <link href="https://developer.webex.com" color="#087E9B">Webex Developer Portal</link>  ·  <link href="https://developer.webex.com/docs/api/v1/messages" color="#087E9B">Messages API</link>'),
          P("Workshop source: Webex Retro Board Project README. For project-specific instructions and the latest code, use the repository README.", "Smallx")]

doc = HandoutDoc(OUT)
doc.build(story)
print(OUT)
