import html
import re
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Preformatted, HRFlowable,
)

ROOT = Path("/Users/tomrobin/T-Level-Projects/webex-retro-board-project")
SOURCE = ROOT / "README.md"
OUTPUT = ROOT / "output/pdf/webex-retro-board-readme.pdf"
NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#087E9B")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#526579")
PALE = colors.HexColor("#EAF1F5")

base = getSampleStyleSheet()
styles = {
    "title": ParagraphStyle("ReadmeTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=NAVY, spaceAfter=12),
    "h1": ParagraphStyle("ReadmeH1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=5, spaceAfter=8, keepWithNext=True),
    "h2": ParagraphStyle("ReadmeH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=BLUE, spaceBefore=9, spaceAfter=4, keepWithNext=True),
    "h3": ParagraphStyle("ReadmeH3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=INK, spaceBefore=7, spaceAfter=3, keepWithNext=True),
    "body": ParagraphStyle("ReadmeBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.1, leading=12.4, textColor=INK, spaceAfter=5, splitLongWords=True),
    "list": ParagraphStyle("ReadmeList", parent=base["BodyText"], fontName="Helvetica", fontSize=8.9, leading=12, textColor=INK, leftIndent=14, firstLineIndent=-9, spaceAfter=2.5, splitLongWords=True),
    "quote": ParagraphStyle("ReadmeQuote", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=8.9, leading=12, textColor=MUTED, leftIndent=12, rightIndent=6, spaceBefore=2, spaceAfter=3),
    "summary": ParagraphStyle("ReadmeSummary", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=9.2, leading=12.2, textColor=NAVY, backColor=PALE, borderPadding=6, spaceBefore=4, spaceAfter=5),
    "code": ParagraphStyle("ReadmeCode", fontName="Courier", fontSize=7.8, leading=10, textColor=colors.HexColor("#F1F6FA"), backColor=NAVY, borderPadding=8, leftIndent=7, rightIndent=7, spaceBefore=3, spaceAfter=7),
}

def inline_markup(text):
    text = text.replace("<b>", "**").replace("</b>", "**")
    text = text.replace("<br>", " ").replace("<br/>", " ")
    tokens = []

    def hold(markup):
        token = f"ZXQMARK{len(tokens)}QXZ"
        tokens.append((token, markup))
        return token

    # README badges contain linked image syntax; represent each as linked text.
    text = re.sub(
        r"\[!\[([^\]]+)\]\(([^)]+)\)\]\(([^)]+)\)",
        lambda m: hold(f'<link href="{html.escape(m.group(3), quote=True)}" color="#087E9B">{html.escape(m.group(1))}</link>'),
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: hold(f'<link href="{html.escape(m.group(2), quote=True)}" color="#087E9B">{html.escape(m.group(1))}</link>'),
        text,
    )
    text = re.sub(
        r"(?<![\w\"=])(https?://[^\s<>]+)",
        lambda m: hold(f'<link href="{html.escape(m.group(1).rstrip(".,)"), quote=True)}" color="#087E9B">{html.escape(m.group(1))}</link>'),
        text,
    )
    text = re.sub(r"`([^`]+)`", lambda m: hold(f'<font name="Courier">{html.escape(m.group(1))}</font>'), text)
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for token, markup in tokens:
        text = text.replace(token, markup)
    return text

def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, h-13*mm, w, 13*mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.drawString(18*mm, h-8.5*mm, "WEBEX RETRO BOARD PROJECT  /  README")
    canvas.setStrokeColor(colors.HexColor("#D7E2EA"))
    canvas.line(18*mm, 14*mm, w-18*mm, 14*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18*mm, 9*mm, "README formatted for print; wording preserved")
    canvas.drawRightString(w-18*mm, 9*mm, str(doc.page))
    canvas.restoreState()

class ReadmeDoc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=21*mm, bottomMargin=19*mm, title="Webex Retro Board Project README", author="Webex Retro Board Project")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="main")
        self.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=header_footer)])

def render_readme(source):
    lines = source.splitlines()
    flow = []
    paragraph = []
    code_lines = []
    in_code = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            text = " ".join(part.strip() for part in paragraph)
            flow.append(Paragraph(inline_markup(text), styles["body"]))
            paragraph = []

    def flush_code():
        nonlocal code_lines
        if code_lines:
            wrapped = []
            for line in code_lines:
                wrapped.extend(textwrap.wrap(line, width=92, subsequent_indent="  ", replace_whitespace=False, drop_whitespace=False) or [""])
            flow.append(Preformatted("\n".join(wrapped), styles["code"]))
            code_lines = []

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if line.startswith("```"):
            flush_paragraph()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            continue
        if line.strip() in ("---", "***", "___"):
            flush_paragraph()
            flow.append(Spacer(1, 3))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#D7E2EA"), spaceBefore=1, spaceAfter=5))
            continue
        if stripped.startswith("<details") or stripped.startswith("</details") or stripped.startswith("</summary"):
            flush_paragraph()
            continue
        if stripped.startswith("<summary"):
            flush_paragraph()
            summary = re.sub(r"</?summary[^>]*>", "", stripped).strip()
            if summary:
                flow.append(Paragraph(inline_markup(summary), styles["summary"]))
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            level, text = len(heading.group(1)), heading.group(2)
            if level == 1 and text.startswith("Task "):
                flow.append(PageBreak())
            kind = "title" if level == 1 and not text.startswith("Task ") else {1: "h1", 2: "h2", 3: "h3"}[level]
            flow.append(Paragraph(inline_markup(text), styles[kind]))
            continue
        if line.startswith(">"):
            flush_paragraph()
            quote_lines = []
            while line.startswith(">"):
                quote_lines.append(line[1:].strip())
                # Peek by consuming the next line in an index-free manner below.
                break
            flow.append(Paragraph(inline_markup(" ".join(quote_lines)), styles["quote"]))
            continue
        list_match = re.match(r"^(\s*)([-+*]|\d+\.)\s+(.*)$", line)
        if list_match:
            flush_paragraph()
            indent = len(list_match.group(1).expandtabs(2))
            marker = list_match.group(2)
            text = list_match.group(3)
            bullet = f"{marker} " if marker.endswith(".") else "- "
            style = ParagraphStyle(f"list{indent}", parent=styles["list"], leftIndent=14 + indent*4, firstLineIndent=-9)
            flow.append(Paragraph(inline_markup(bullet + text), style))
            continue
        if line.startswith("<") and line.endswith(">") and re.fullmatch(r"</?[A-Za-z][^>]*>", line):
            # Ignore layout-only HTML wrappers while preserving their text elsewhere.
            continue
        paragraph.append(line)
    flush_paragraph()
    flush_code()
    return flow

source = SOURCE.read_text(encoding="utf-8")
document = ReadmeDoc(str(OUTPUT))
document.build(render_readme(source))
print(f"Created {OUTPUT}")
