"""Generate process design map PDF for K9 Agent submission."""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import HRFlowable

ZURICH_BLUE  = colors.HexColor("#003882")
MID_BLUE     = colors.HexColor("#0057b8")
LIGHT_BLUE   = colors.HexColor("#e8f0fb")
WHITE        = colors.white
GRAY         = colors.HexColor("#f5f7fa")
DARK_GRAY    = colors.HexColor("#444444")
GREEN        = colors.HexColor("#1a7a4a")
LIGHT_GREEN  = colors.HexColor("#e8f5ee")

OUTPUT = "/Users/LIVIU.GHENGHEA/k9-agent/LiviuGhenghea_Retail_Agentic_Commerce_processmap.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=landscape(A4),
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
)

styles = getSampleStyleSheet()

def style(name, **kw):
    return ParagraphStyle(name, parent=styles["Normal"], **kw)

title_style    = style("T",  fontSize=18, textColor=WHITE,     fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
subtitle_style = style("ST", fontSize=10, textColor=LIGHT_BLUE, fontName="Helvetica",     alignment=TA_CENTER)
h2_style       = style("H2", fontSize=11, textColor=ZURICH_BLUE, fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
h3_style       = style("H3", fontSize=9,  textColor=MID_BLUE,    fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=2)
body_style     = style("B",  fontSize=8,  textColor=DARK_GRAY,   fontName="Helvetica",      leading=12)
small_style    = style("S",  fontSize=7,  textColor=DARK_GRAY,   fontName="Helvetica",      leading=10)
tag_style      = style("TAG",fontSize=7,  textColor=WHITE,        fontName="Helvetica-Bold", alignment=TA_CENTER)
green_style    = style("G",  fontSize=8,  textColor=GREEN,        fontName="Helvetica-Bold")

elements = []

# ── Title banner ──────────────────────────────────────────────────────────────
title_table = Table(
    [[Paragraph("🐾  K9 Agent — Process Design Map", title_style)],
     [Paragraph("Retail_Agentic_Commerce_LiviuGhenghea  ·  DA Direkt Dog Insurance  ·  Zurich Hyper Challenge 2026", subtitle_style)]],
    colWidths=[26*cm],
)
title_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), ZURICH_BLUE),
    ("ROWPADDING", (0,0), (-1,-1), 8),
    ("ROUNDEDCORNERS", [6]),
]))
elements.append(title_table)
elements.append(Spacer(1, 0.4*cm))

# ── Architecture layers ───────────────────────────────────────────────────────
def layer_box(title, tag, items, bg, tag_bg=MID_BLUE):
    rows = [[
        Paragraph(title, style("LT", fontSize=10, textColor=ZURICH_BLUE, fontName="Helvetica-Bold")),
        Paragraph(tag,   style("TAG2", fontSize=7, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]]
    t = Table(rows, colWidths=[14*cm, 3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,0), bg),
        ("BACKGROUND",   (1,0), (1,0), tag_bg),
        ("ROWPADDING",   (0,0), (-1,-1), 6),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t

# Layer 1 — Customer Agent
l1_data = [
    [Paragraph("<b>LAYER 1 — CUSTOMER AGENT</b>", style("L1H", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("claude-haiku-4-5", tag_style)],
    [Paragraph(
        "Acts on behalf of the dog owner. Holds the owner profile (name, address, DOB, IBAN) and dog profile "
        "(breed, DOB, gender). Drives the conversation: introduces the dog, asks about plans, evaluates options, "
        "asks about exclusions and waiting periods, provides owner details on request, and gives explicit purchase consent.",
        small_style), ""],
    [Paragraph("↕  Natural language messages (turn-by-turn)", style("ARR", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-BoldOblique")), ""],
]
l1 = Table(l1_data, colWidths=[23*cm, 3*cm])
l1.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("BACKGROUND",  (1,0), (1,0), MID_BLUE),
    ("BACKGROUND",  (0,1), (-1,1), LIGHT_BLUE),
    ("BACKGROUND",  (0,2), (-1,2), WHITE),
    ("SPAN",        (0,1), (1,1)),
    ("SPAN",        (0,2), (1,2)),
    ("ROWPADDING",  (0,0), (-1,-1), 6),
    ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
]))
elements.append(l1)
elements.append(Spacer(1, 0.3*cm))

# Arrow
elements.append(Paragraph("▼", style("ARR2", fontSize=14, textColor=MID_BLUE, alignment=TA_CENTER)))
elements.append(Spacer(1, 0.1*cm))

# Layer 2 — Zurich Agent
l2_data = [
    [Paragraph("<b>LAYER 2 — ZURICH K9 AGENT (Orchestrator)</b>", style("L2H", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("claude-sonnet-4-6", tag_style)],
    [Paragraph(
        "Receives messages, decides which tools to call, executes them, appends results to conversation history, "
        "loops until a text response is ready. Owns the lead UUID and full conversation state. "
        "Enforces consent before bind. Never calls bind_coverage until check_missing_fields confirms all required fields are present.",
        small_style), ""],
    [Paragraph(
        "<b>Agentic loop:</b>  receive message  →  call Claude API  →  if tool_use: execute tools + loop  →  if end_turn: return response",
        style("LOOP", fontSize=7.5, textColor=MID_BLUE, fontName="Helvetica-BoldOblique")), ""],
    [Paragraph("↕  Tool calls via httpx (live REST APIs)", style("ARR", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-BoldOblique")), ""],
]
l2 = Table(l2_data, colWidths=[23*cm, 3*cm])
l2.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("BACKGROUND",  (1,0), (1,0), MID_BLUE),
    ("BACKGROUND",  (0,1), (-1,2), LIGHT_BLUE),
    ("BACKGROUND",  (0,3), (-1,3), WHITE),
    ("SPAN",        (0,1), (1,1)),
    ("SPAN",        (0,2), (1,2)),
    ("SPAN",        (0,3), (1,3)),
    ("ROWPADDING",  (0,0), (-1,-1), 6),
    ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
]))
elements.append(l2)
elements.append(Spacer(1, 0.3*cm))

elements.append(Paragraph("▼", style("ARR2", fontSize=14, textColor=MID_BLUE, alignment=TA_CENTER)))
elements.append(Spacer(1, 0.1*cm))

# Layer 3 — Tools
tools_data = [
    [Paragraph("<b>LAYER 3 — 12 TOOLS</b>", style("L3H", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("tool_use", tag_style)],
]
tool_cols = [
    [("search_breeds",        "Resolve breed name → breed_id"),
     ("get_all_plans",        "List all 6 coverage options"),
     ("get_plan_details",     "Plain-language plan description"),
     ("get_coverage_faq",     "Waiting periods, GOT, exclusions"),
     ("get_available_start_dates", "Valid contract start dates")],
    [("get_price",            "Price a single plan"),
     ("get_all_prices",       "Full comparison across all plans")],
    [("create_lead",          "Open a new lead in DA Direkt"),
     ("update_lead",          "Progressively enrich lead data"),
     ("get_lead",             "Retrieve current lead state"),
     ("check_missing_fields", "Validate before bind"),
     ("bind_coverage",        "Submit insurance application")],
]
labels = ["RESEARCH & FAQ", "PRICING", "LEAD LIFECYCLE"]

def tool_cell(tool_list, label):
    lines = [Paragraph(f"<b>{label}</b>", style("TL", fontSize=7, textColor=MID_BLUE, fontName="Helvetica-Bold"))]
    for name, desc in tool_list:
        lines.append(Paragraph(f"<b>{name}</b>", style("TN", fontSize=7, textColor=DARK_GRAY, fontName="Helvetica-Bold")))
        lines.append(Paragraph(desc, style("TD", fontSize=6.5, textColor=DARK_GRAY, fontName="Helvetica", leading=9)))
    return lines

tool_row = [[tool_cell(tool_cols[i], labels[i]) for i in range(3)]]
tool_inner = Table(tool_row, colWidths=[8.5*cm, 6*cm, 8.5*cm])
tool_inner.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (0,0), LIGHT_BLUE),
    ("BACKGROUND",  (1,0), (1,0), GRAY),
    ("BACKGROUND",  (2,0), (2,0), LIGHT_BLUE),
    ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ("ROWPADDING",  (0,0), (-1,-1), 6),
    ("LINEBEFORE",  (1,0), (1,-1), 0.5, MID_BLUE),
    ("LINEBEFORE",  (2,0), (2,-1), 0.5, MID_BLUE),
]))

l3_outer = Table(
    [[Paragraph("<b>LAYER 3 — 12 TOOLS</b>", style("L3H", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")),
      Paragraph("tool_use", tag_style)],
     [tool_inner, ""]],
    colWidths=[23*cm, 3*cm],
)
l3_outer.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("BACKGROUND",  (1,0), (1,0), MID_BLUE),
    ("SPAN",        (0,1), (1,1)),
    ("ROWPADDING",  (0,0), (-1,0), 6),
    ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
]))
elements.append(l3_outer)
elements.append(Spacer(1, 0.3*cm))

elements.append(Paragraph("▼", style("ARR2", fontSize=14, textColor=MID_BLUE, alignment=TA_CENTER)))
elements.append(Spacer(1, 0.1*cm))

# Layer 4 — APIs
api_data = [
    ["Breeds API\nGET /v1/breeds", "Policies API\nGET /v1/policies", "Price API\nGET /v1/price",
     "Leads API\nPOST/PUT/GET\n/v1/leads", "Recurring\nPOST /v1/leads/\ncheck_recurring", "Start Dates\nGET /v1/contracts/\navailable_start_dates"],
]
api_table = Table(api_data, colWidths=[4.2*cm]*6)
api_table.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,-1), LIGHT_BLUE),
    ("TEXTCOLOR",   (0,0), (-1,-1), ZURICH_BLUE),
    ("FONTNAME",    (0,0), (-1,-1), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0), (-1,-1), 7.5),
    ("ALIGN",       (0,0), (-1,-1), "CENTER"),
    ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ("ROWPADDING",  (0,0), (-1,-1), 8),
    ("GRID",        (0,0), (-1,-1), 0.5, MID_BLUE),
    ("BOX",         (0,0), (-1,-1), 1,   ZURICH_BLUE),
]))

l4_outer = Table(
    [[Paragraph("<b>LAYER 4 — PETOLO BETA APIs</b>  ·  https://beta.dentolo-test.de  ·  Auth: x-api-key header",
                style("L4H", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")),
      Paragraph("REST/JSON", tag_style)],
     [api_table, ""]],
    colWidths=[23*cm, 3*cm],
)
l4_outer.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("BACKGROUND",  (1,0), (1,0), MID_BLUE),
    ("SPAN",        (0,1), (1,1)),
    ("ROWPADDING",  (0,0), (-1,0), 6),
    ("ROWPADDING",  (0,1), (-1,1), 8),
    ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
]))
elements.append(l4_outer)
elements.append(Spacer(1, 0.4*cm))

# ── Journey flow ──────────────────────────────────────────────────────────────
journey_steps = [
    ("1\nRESEARCH", "Customer asks about\nplans and coverage\ndifferences"),
    ("2\nQUOTE", "Agent calls\nget_all_prices +\nsearch_breeds"),
    ("3\nCOLLECT", "Customer provides\nowner + dog\ndata + IBAN"),
    ("4\nVALIDATE", "check_missing\n_fields() verifies\nreadiness"),
    ("5\nCONFIRM", "Agent shows full\nsummary + explicit\nconsent required"),
    ("6\nBIND", "bind_coverage()\nApplication\nsubmitted ✓"),
]
flow_data = [[Paragraph(f"<b>{s[0]}</b>", style("FS", fontSize=7.5, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)) for s in journey_steps],
             [Paragraph(s[1], style("FD", fontSize=6.5, textColor=DARK_GRAY, fontName="Helvetica", alignment=TA_CENTER, leading=9)) for s in journey_steps]]

flow_table = Table(flow_data, colWidths=[4.2*cm]*6)
flow_table.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), MID_BLUE),
    ("BACKGROUND",  (5,0), (5,0), GREEN),
    ("BACKGROUND",  (0,1), (-1,1), WHITE),
    ("BACKGROUND",  (5,1), (5,1), LIGHT_GREEN),
    ("ROWPADDING",  (0,0), (-1,-1), 6),
    ("GRID",        (0,0), (-1,-1), 0.5, MID_BLUE),
    ("BOX",         (0,0), (-1,-1), 1,   ZURICH_BLUE),
]))

journey_outer = Table(
    [[Paragraph("<b>JOURNEY FLOW</b>  (non-linear — any step can loop back to ask questions)",
                style("JH", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold"))],
     [flow_table]],
    colWidths=[26*cm],
)
journey_outer.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("ROWPADDING",  (0,0), (-1,0), 6),
    ("ROWPADDING",  (0,1), (-1,1), 8),
    ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
]))
elements.append(journey_outer)

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(elements)
print(f"PDF created: {OUTPUT}")
