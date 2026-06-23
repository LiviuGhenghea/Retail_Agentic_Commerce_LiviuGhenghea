"""Generate pitch deck PDF for K9 Agent hackathon submission."""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus.flowables import HRFlowable

ZURICH_BLUE  = colors.HexColor("#003882")
MID_BLUE     = colors.HexColor("#0057b8")
LIGHT_BLUE   = colors.HexColor("#e8f0fb")
ACCENT_BLUE  = colors.HexColor("#4a90d9")
WHITE        = colors.white
GRAY         = colors.HexColor("#f5f7fa")
DARK_GRAY    = colors.HexColor("#333333")
MID_GRAY     = colors.HexColor("#666666")
GREEN        = colors.HexColor("#1a7a4a")
LIGHT_GREEN  = colors.HexColor("#e8f5ee")
ORANGE       = colors.HexColor("#e07b00")
LIGHT_ORANGE = colors.HexColor("#fff4e0")

OUTPUT = "/Users/LIVIU.GHENGHEA/k9-agent/LiviuGhenghea_Retail_Agentic_Commerce.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=landscape(A4),
    leftMargin=0, rightMargin=0,
    topMargin=0, bottomMargin=0,
)

def S(name, **kw):
    base = ParagraphStyle(name, fontName="Helvetica", fontSize=10, textColor=DARK_GRAY, leading=14)
    for k, v in kw.items():
        setattr(base, k, v)
    return base

W, H = landscape(A4)
CW = W  # full width

def full_page_table(rows, col_widths, style_cmds):
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle(style_cmds))
    return t

elements = []

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — ONE-PAGER EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

def header_banner(title, subtitle=""):
    rows = [[
        Paragraph(f"<b>{title}</b>", S("HT", fontSize=22, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]]
    if subtitle:
        rows.append([Paragraph(subtitle, S("HS", fontSize=10, textColor=LIGHT_BLUE, alignment=TA_CENTER))])
    t = Table(rows, colWidths=[W - 2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), ZURICH_BLUE),
        ("ROWPADDING",  (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING",(0,0), (-1,-1), 20),
    ]))
    return t

def info_card(label, content, bg=LIGHT_BLUE, label_color=ZURICH_BLUE, w=None):
    rows = [
        [Paragraph(f"<b>{label}</b>", S("CL", fontSize=7.5, textColor=label_color, fontName="Helvetica-Bold"))],
        [Paragraph(content, S("CC", fontSize=9, textColor=DARK_GRAY, leading=13))],
    ]
    t = Table(rows, colWidths=[w or 12*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,0), bg),
        ("BACKGROUND",  (0,1), (0,1), WHITE),
        ("ROWPADDING",  (0,0), (-1,-1), 7),
        ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
    ]))
    return t

# Outer wrapper — 1cm margin all around
inner_w = W - 2*cm

# Title
p1_title = Table(
    [[Paragraph("<b>K9 Agent</b>", S("P1T", fontSize=26, textColor=WHITE, fontName="Helvetica-Bold")),
      Paragraph("Hyper<b>challenge</b> 2026", S("P1S", fontSize=12, textColor=LIGHT_BLUE, alignment=TA_RIGHT))]],
    colWidths=[inner_w * 0.7, inner_w * 0.3]
)
p1_title.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,-1), ZURICH_BLUE),
    ("ROWPADDING",  (0,0), (-1,-1), 14),
    ("LEFTPADDING", (0,0), (0,-1), 20),
    ("RIGHTPADDING",(1,0), (1,-1), 20),
    ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
]))

# Top meta row
meta_row = Table([[
    info_card("Name of the Team", "Retail_Agentic_Commerce_LiviuGhenghea", w=inner_w*0.32),
    info_card("Selected Use Case", "01 — Agentic Commerce for the Personal Agent Era", w=inner_w*0.38),
    info_card("Main Learning from Experience",
              "Building directly on the Anthropic API (no framework) kept the system transparent and fast. "
              "Agent-to-agent commerce patterns are technically feasible today with existing APIs.",
              w=inner_w*0.28),
]], colWidths=[inner_w*0.33, inner_w*0.39, inner_w*0.28])
meta_row.setStyle(TableStyle([
    ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 3),
    ("RIGHTPADDING",(0,0), (-1,-1), 3),
]))

members_card = info_card("Team Members", "Liviu Ghenghea · liviu.ghenghea@zurich.com", w=inner_w)

# Three main content cards
approach_card = Table([
    [Paragraph("<b>How your approach is solving the problem</b>",
               S("ACL", fontSize=8, textColor=ZURICH_BLUE, fontName="Helvetica-Bold"))],
    [Paragraph(
        "K9 Agent replaces the existing linear web funnel with a fully AI-native, conversational insurance journey. "
        "A Zurich-hosted AI agent (powered by Claude Sonnet) understands natural language, calls 12 live DA Direkt APIs in real time, "
        "and guides customers from their first question to a bound policy — without a single form or dropdown.\n\n"
        "The architecture is built for agent-to-agent commerce: a customer-owned personal AI agent can interact "
        "directly with the Zurich K9 Agent, enabling autonomous quote and bind with no human in the loop. "
        "This directly addresses the five AS-IS pain points: relevance, understanding, engagement, transparency and purchase guidance.",
        S("ACC", fontSize=9, textColor=DARK_GRAY, leading=13))],
], colWidths=[inner_w])
approach_card.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (0,0), LIGHT_BLUE),
    ("BACKGROUND",  (0,1), (0,1), WHITE),
    ("ROWPADDING",  (0,0), (-1,-1), 8),
    ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
]))

results_scale = Table([[
    Table([
        [Paragraph("<b>What the results of the prototype are</b>",
                   S("RCL", fontSize=8, textColor=ZURICH_BLUE, fontName="Helvetica-Bold"))],
        [Paragraph(
            "• <b>Live working prototype</b> deployed at https://k9agent.streamlit.app\n"
            "• Full journey demonstrated: breed lookup → live pricing → lead creation → bind\n"
            "• <b>18/18 API smoke tests passing</b> against DA Direkt beta environment\n"
            "• Real leads created in DA Direkt's system with valid reference numbers\n"
            "• Handles natural language, follow-up questions, and edge cases without breaking\n"
            "• Cost per full journey: ~€0.05 (Sonnet + Haiku models)",
            S("RCC", fontSize=9, textColor=DARK_GRAY, leading=13))],
    ], colWidths=[inner_w * 0.49]),
    Table([
        [Paragraph("<b>What are the next steps for scaling your solution</b>",
                   S("SCL", fontSize=8, textColor=ZURICH_BLUE, fontName="Helvetica-Bold"))],
        [Paragraph(
            "• <b>MCP server</b>: expose tools as Model Context Protocol server — any personal agent can discover and call the Zurich Agent\n"
            "• <b>Production APIs</b>: swap beta URL → production, rotate API key\n"
            "• <b>Multi-channel</b>: same agent core serves WhatsApp, web chat, voice\n"
            "• <b>Multi-product</b>: extend to cat insurance, liability, life with minimal changes\n"
            "• <b>Prompt caching</b>: reduce Sonnet costs by ~80% at scale\n"
            "• <b>Session persistence</b>: Redis for conversation state across channels",
            S("SCC", fontSize=9, textColor=DARK_GRAY, leading=13))],
    ], colWidths=[inner_w * 0.49]),
]], colWidths=[inner_w * 0.5, inner_w * 0.5])
results_scale.setStyle(TableStyle([
    ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 3),
    ("RIGHTPADDING",(0,0), (-1,-1), 3),
]))

# Assemble page 1
page1 = Table([
    [p1_title],
    [Spacer(1, 0.2*cm)],
    [meta_row],
    [Spacer(1, 0.15*cm)],
    [members_card],
    [Spacer(1, 0.15*cm)],
    [approach_card],
    [Spacer(1, 0.15*cm)],
    [results_scale],
], colWidths=[inner_w])

wrapper1 = Table([[page1]], colWidths=[W])
wrapper1.setStyle(TableStyle([
    ("LEFTPADDING",  (0,0), (-1,-1), 1*cm),
    ("RIGHTPADDING", (0,0), (-1,-1), 1*cm),
    ("TOPPADDING",   (0,0), (-1,-1), 0.8*cm),
    ("BOTTOMPADDING",(0,0), (-1,-1), 0.8*cm),
    ("BACKGROUND",   (0,0), (-1,-1), WHITE),
]))
elements.append(wrapper1)
elements.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SLIDE 1: PROBLEM APPROACH & SOLUTION DESIGN
# ══════════════════════════════════════════════════════════════════════════════

def slide_header(num, title, subtitle=""):
    row = [[
        Paragraph(f"<b>{num}</b>", S("SN", fontSize=28, textColor=ACCENT_BLUE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Table([
            [Paragraph(f"<b>{title}</b>", S("SHT", fontSize=16, textColor=WHITE, fontName="Helvetica-Bold"))],
            [Paragraph(subtitle, S("SHS", fontSize=9, textColor=LIGHT_BLUE))],
        ], colWidths=[inner_w * 0.88]),
    ]]
    t = Table(row, colWidths=[inner_w * 0.08, inner_w * 0.92])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), ZURICH_BLUE),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWPADDING",  (0,0), (-1,-1), 12),
    ]))
    return t

def pain_card(icon, title, body, w):
    t = Table([
        [Paragraph(f"{icon}  <b>{title}</b>", S("PT", fontSize=8.5, textColor=ZURICH_BLUE, fontName="Helvetica-Bold"))],
        [Paragraph(body, S("PB", fontSize=8, textColor=DARK_GRAY, leading=11))],
    ], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,0), LIGHT_BLUE),
        ("BACKGROUND",  (0,1), (0,1), WHITE),
        ("ROWPADDING",  (0,0), (-1,-1), 7),
        ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
    ]))
    return t

def solution_card(icon, title, body, w, bg=LIGHT_BLUE):
    t = Table([
        [Paragraph(f"{icon}  <b>{title}</b>", S("ST2", fontSize=8.5, textColor=WHITE, fontName="Helvetica-Bold"))],
        [Paragraph(body, S("SB2", fontSize=8, textColor=DARK_GRAY, leading=11))],
    ], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,0), MID_BLUE),
        ("BACKGROUND",  (0,1), (0,1), WHITE),
        ("ROWPADDING",  (0,0), (-1,-1), 7),
        ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
    ]))
    return t

cw4 = inner_w / 4 - 0.2*cm
cw3 = inner_w / 3 - 0.2*cm

pain_row = Table([[
    pain_card("😕", "Relevance", "Customers can't see how the product connects to their pet's specific needs. Answers don't match their actual questions.", cw4),
    pain_card("❓", "Understanding", "Complex terminology, unclear plan differences, no breed/age-specific guidance. Surgery vs full coverage not intuitive.", cw4),
    pain_card("👻", "Engagement", "Customers can't visualise what the claims experience looks like. Network coverage and real-life usage unclear.", cw4),
    pain_card("💸", "Transparency + Drop-off", "Premium logic opaque. Pre-existing conditions cause drop-offs. Application process feels complex and error-prone.", cw4),
]], colWidths=[cw4 + 0.2*cm]*4)
pain_row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))

solution_row = Table([[
    solution_card("🤖", "AI-native conversation", "Natural language replaces forms. Claude understands 'my Golden Retriever is 2 years old' in one message.", cw3),
    solution_card("📊", "Live pricing + transparency", "Real-time prices from DA Direkt APIs. Explains GOT factors, deductibles, and exclusions in plain language.", cw3),
    solution_card("🔗", "Agent-to-agent commerce", "Personal AI agents can call the Zurich K9 Agent directly via tool-use protocol. No human in the loop.", cw3),
]], colWidths=[cw3 + 0.3*cm]*3)
solution_row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))

arch_row = Table([[
    Paragraph(
        "<b>Customer Agent</b>  (Haiku — fast, cheap)  →  natural language  →  "
        "<b>Zurich K9 Agent</b>  (Sonnet — reasoning + 12 tools)  →  REST calls  →  "
        "<b>DA Direkt Petolo APIs</b>  (live breeds / pricing / leads / bind)",
        S("AR", fontSize=9, textColor=WHITE, fontName="Helvetica", alignment=TA_CENTER, leading=14)),
]], colWidths=[inner_w])
arch_row.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,-1), ZURICH_BLUE),
    ("ROWPADDING",  (0,0), (-1,-1), 10),
    ("BOX",         (0,0), (-1,-1), 0, WHITE),
]))

s1_label_pain = Table([[Paragraph("<b>THE PROBLEM — 5 AS-IS PAIN POINTS</b>", S("SEC", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s1_label_pain.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))
s1_label_sol  = Table([[Paragraph("<b>THE SOLUTION — HOW K9 AGENT SOLVES IT</b>", S("SEC2", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s1_label_sol.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))
s1_label_arch = Table([[Paragraph("<b>ARCHITECTURE IN ONE LINE</b>", S("SEC3", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s1_label_arch.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))

page2_inner = Table([
    [slide_header("1", "Problem Approach & Solution Design", "Replacing the linear web funnel with an AI-native, agent-to-agent insurance journey")],
    [Spacer(1,0.2*cm)],
    [s1_label_pain],
    [pain_row],
    [Spacer(1,0.2*cm)],
    [s1_label_sol],
    [solution_row],
    [Spacer(1,0.2*cm)],
    [s1_label_arch],
    [arch_row],
], colWidths=[inner_w])

wrapper2 = Table([[page2_inner]], colWidths=[W])
wrapper2.setStyle(TableStyle([
    ("LEFTPADDING",  (0,0), (-1,-1), 1*cm),
    ("RIGHTPADDING", (0,0), (-1,-1), 1*cm),
    ("TOPPADDING",   (0,0), (-1,-1), 0.8*cm),
    ("BOTTOMPADDING",(0,0), (-1,-1), 0.8*cm),
    ("BACKGROUND",   (0,0), (-1,-1), GRAY),
]))
elements.append(wrapper2)
elements.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — SLIDE 2: RESULTS & KEY INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════

def metric_card(value, label, sub, bg, w):
    t = Table([
        [Paragraph(f"<b>{value}</b>", S("MV", fontSize=22, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER))],
        [Paragraph(label, S("ML", fontSize=8.5, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER))],
        [Paragraph(sub,   S("MS", fontSize=7,   textColor=LIGHT_BLUE, alignment=TA_CENTER))],
    ], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), bg),
        ("ROWPADDING",  (0,0), (-1,-1), 6),
        ("BOX",         (0,0), (-1,-1), 0, WHITE),
    ]))
    return t

def insight_card(icon, title, body, w):
    t = Table([
        [Paragraph(f"{icon}  <b>{title}</b>", S("IT", fontSize=8.5, textColor=WHITE, fontName="Helvetica-Bold"))],
        [Paragraph(body, S("IB", fontSize=8, textColor=DARK_GRAY, leading=11))],
    ], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,0), MID_BLUE),
        ("BACKGROUND",  (0,1), (0,1), WHITE),
        ("ROWPADDING",  (0,0), (-1,-1), 7),
        ("BOX",         (0,0), (-1,-1), 0.5, MID_BLUE),
    ]))
    return t

mw = inner_w / 5 - 0.3*cm
metrics = Table([[
    metric_card("18/18",  "API Tests",      "All smoke tests passing",       GREEN,    mw),
    metric_card("12",     "Tools",          "Live DA Direkt API calls",      MID_BLUE, mw),
    metric_card("6",      "Plans Quoted",   "Real-time pricing all tiers",   ZURICH_BLUE, mw),
    metric_card("~€0.05", "Cost/Journey",   "Sonnet + Haiku combined",       ORANGE,   mw),
    metric_card("100%",   "Conversational", "No forms, no dropdowns",        GREEN,    mw),
]], colWidths=[mw + 0.3*cm]*5)
metrics.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))

iw = inner_w / 3 - 0.3*cm
insights = Table([[
    insight_card("✅", "Full journey end-to-end",
                 "From first message to insurance application submission — live leads created in DA Direkt's beta system with real reference numbers. "
                 "Deployed at https://k9agent.streamlit.app.", iw),
    insight_card("🧠", "Genuine AI understanding",
                 "Agent handles natural language, follow-up questions, breed ambiguity, and unexpected inputs without breaking. "
                 "No rigid step sequence — the conversation adapts to the customer.", iw),
    insight_card("🔌", "Agent-to-agent ready",
                 "Architecture designed so any MCP-compatible personal agent can discover and call the Zurich K9 Agent tools directly. "
                 "No UI required — pure agent-to-agent API interaction.", iw),
]], colWidths=[iw + 0.3*cm]*3)
insights.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))

comparison_data = [
    [Paragraph("<b>Dimension</b>",     S("TH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>AS-IS (Today)</b>", S("TH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>K9 Agent (TO-BE)</b>", S("TH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold"))],
    ["Customer effort",    "Navigate 5-step web form", "Single conversation, any device"],
    ["Coverage clarity",   "PDF documents, buried terms", "Plain-language explanation on demand"],
    ["Pricing transparency","Calculator with fixed inputs","Live prices across all plans, scenario-based"],
    ["Pre-existing conditions","Drop-off, unclear guidance","Proactive FAQ, guided disclosure"],
    ["Agent-to-agent",     "Not supported",            "Native — personal agents can call directly"],
]
cmp_widths = [inner_w*0.22, inner_w*0.37, inner_w*0.41]
comparison = Table(comparison_data, colWidths=cmp_widths)
comparison.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
    ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
    ("BACKGROUND",  (0,1), (-1,1), LIGHT_BLUE),
    ("BACKGROUND",  (0,2), (-1,2), WHITE),
    ("BACKGROUND",  (0,3), (-1,3), LIGHT_BLUE),
    ("BACKGROUND",  (0,4), (-1,4), WHITE),
    ("BACKGROUND",  (0,5), (-1,5), LIGHT_BLUE),
    ("FONTSIZE",    (0,0), (-1,-1), 8),
    ("ROWPADDING",  (0,0), (-1,-1), 6),
    ("GRID",        (0,0), (-1,-1), 0.5, MID_BLUE),
    ("TEXTCOLOR",   (2,1), (2,-1), GREEN),
    ("FONTNAME",    (2,1), (2,-1), "Helvetica-Bold"),
]))

s2_label_m  = Table([[Paragraph("<b>KEY METRICS</b>", S("S2M", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s2_label_m.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))
s2_label_i  = Table([[Paragraph("<b>KEY INSIGHTS</b>", S("S2I", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s2_label_i.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))
s2_label_c  = Table([[Paragraph("<b>AS-IS vs TO-BE COMPARISON</b>", S("S2C", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s2_label_c.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))

page3_inner = Table([
    [slide_header("2", "Results & Key Insights", "Working prototype validated against live DA Direkt beta APIs")],
    [Spacer(1,0.2*cm)],
    [s2_label_m],
    [metrics],
    [Spacer(1,0.2*cm)],
    [s2_label_i],
    [insights],
    [Spacer(1,0.2*cm)],
    [s2_label_c],
    [comparison],
], colWidths=[inner_w])

wrapper3 = Table([[page3_inner]], colWidths=[W])
wrapper3.setStyle(TableStyle([
    ("LEFTPADDING",  (0,0), (-1,-1), 1*cm),
    ("RIGHTPADDING", (0,0), (-1,-1), 1*cm),
    ("TOPPADDING",   (0,0), (-1,-1), 0.8*cm),
    ("BOTTOMPADDING",(0,0), (-1,-1), 0.8*cm),
    ("BACKGROUND",   (0,0), (-1,-1), GRAY),
]))
elements.append(wrapper3)
elements.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — SLIDE 3: NEXT STEPS & RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════

def step_card(phase, title, items, bg, w):
    bullets = "".join(f"• {i}<br/>" for i in items)
    t = Table([
        [Paragraph(phase, S("SP", fontSize=7, textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
         Paragraph(f"<b>{title}</b>", S("ST3", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold"))],
        ["", Paragraph(bullets, S("SB3", fontSize=8, textColor=DARK_GRAY, leading=12))],
    ], colWidths=[0.8*cm, w - 0.8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (0,-1), bg),
        ("BACKGROUND",  (1,0), (1,0), bg),
        ("BACKGROUND",  (1,1), (1,1), WHITE),
        ("SPAN",        (0,0), (0,1)),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("VALIGN",      (1,1), (1,1), "TOP"),
        ("ROWPADDING",  (0,0), (-1,-1), 7),
        ("BOX",         (0,0), (-1,-1), 0.5, bg),
    ]))
    return t

sw = inner_w / 3 - 0.3*cm
steps_row = Table([[
    step_card("NOW\n0–1\nmo", "Production Readiness", [
        "Swap beta URL → production Petolo API",
        "Rotate API key to production credential",
        "Add Redis for session state persistence",
        "Implement customer identity verification",
        "Subscribe to policy issuance webhooks",
    ], MID_BLUE, sw),
    step_card("NEXT\n1–3\nmo", "Scale & Multi-channel", [
        "Expose tools as MCP server — discoverable by any personal agent",
        "Add WhatsApp / voice channel wrappers",
        "Extend to cat insurance and liability products",
        "Enable prompt caching (80% cost reduction at scale)",
        "Add conversation analytics dashboard",
    ], ZURICH_BLUE, sw),
    step_card("FUTURE\n3–12\nmo", "Enterprise Distribution", [
        "Open the MCP server to approved personal agent platforms",
        "B2B: white-label the Zurich Agent for broker networks",
        "Cross-sell signals: agent detects life events and triggers relevant products",
        "Claims co-pilot: extend same architecture to claims journey",
        "Group rollout: replicate for other DA Direkt / Zurich markets",
    ], GREEN, sw),
]], colWidths=[sw + 0.3*cm]*3)
steps_row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))

cost_data = [
    [Paragraph("<b>Stage</b>",          S("CTH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>Model</b>",          S("CTH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>Cost per journey</b>",S("CTH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>At 10k journeys/mo</b>",S("CTH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
     Paragraph("<b>With prompt caching</b>",S("CTH", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold"))],
    ["Zurich Agent", "claude-sonnet-4-6", "~€0.05",  "~€500/mo",   "~€100/mo"],
    ["Customer Agent","claude-haiku-4-5", "~€0.003", "~€30/mo",    "~€6/mo"],
    [Paragraph("<b>Total</b>", S("TB", fontSize=8, fontName="Helvetica-Bold")),
     Paragraph("<b>—</b>",    S("TB", fontSize=8, fontName="Helvetica-Bold")),
     Paragraph("<b>~€0.05</b>",    S("TB", fontSize=8, fontName="Helvetica-Bold", textColor=GREEN)),
     Paragraph("<b>~€530/mo</b>",  S("TB", fontSize=8, fontName="Helvetica-Bold", textColor=GREEN)),
     Paragraph("<b>~€106/mo</b>",  S("TB", fontSize=8, fontName="Helvetica-Bold", textColor=GREEN))],
]
ccw = [inner_w*0.2, inner_w*0.2, inner_w*0.18, inner_w*0.2, inner_w*0.22]
cost_table = Table(cost_data, colWidths=ccw)
cost_table.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,0), ZURICH_BLUE),
    ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
    ("BACKGROUND",  (0,1), (-1,1), LIGHT_BLUE),
    ("BACKGROUND",  (0,2), (-1,2), WHITE),
    ("BACKGROUND",  (0,3), (-1,3), LIGHT_GREEN),
    ("FONTNAME",    (0,3), (-1,3), "Helvetica-Bold"),
    ("FONTSIZE",    (0,0), (-1,-1), 8),
    ("ROWPADDING",  (0,0), (-1,-1), 6),
    ("GRID",        (0,0), (-1,-1), 0.5, MID_BLUE),
    ("TEXTCOLOR",   (4,1), (4,3), GREEN),
]))

vision_box = Table([[
    Paragraph(
        "<b>Vision:</b>  The K9 Agent architecture is the blueprint for Zurich's agentic distribution layer. "
        "The same pattern — Zurich Agent + tool layer + product APIs — can power any insurance product, "
        "any channel, and any personal agent platform that adopts MCP. "
        "Built once, distributed everywhere.",
        S("VB", fontSize=9, textColor=WHITE, fontName="Helvetica", leading=14, alignment=TA_CENTER)),
]], colWidths=[inner_w])
vision_box.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,-1), ZURICH_BLUE),
    ("ROWPADDING",  (0,0), (-1,-1), 12),
]))

s3_label_r = Table([[Paragraph("<b>ROADMAP</b>", S("S3R", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s3_label_r.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))
s3_label_c = Table([[Paragraph("<b>COST MODEL</b>", S("S3C", fontSize=8, textColor=MID_BLUE, fontName="Helvetica-Bold"))]], colWidths=[inner_w])
s3_label_c.setStyle(TableStyle([("ROWPADDING",(0,0),(-1,-1),4)]))

page4_inner = Table([
    [slide_header("3", "Next Steps & Recommendations", "From hackathon prototype to enterprise-grade agentic distribution")],
    [Spacer(1,0.2*cm)],
    [s3_label_r],
    [steps_row],
    [Spacer(1,0.2*cm)],
    [s3_label_c],
    [cost_table],
    [Spacer(1,0.2*cm)],
    [vision_box],
], colWidths=[inner_w])

wrapper4 = Table([[page4_inner]], colWidths=[W])
wrapper4.setStyle(TableStyle([
    ("LEFTPADDING",  (0,0), (-1,-1), 1*cm),
    ("RIGHTPADDING", (0,0), (-1,-1), 1*cm),
    ("TOPPADDING",   (0,0), (-1,-1), 0.8*cm),
    ("BOTTOMPADDING",(0,0), (-1,-1), 0.8*cm),
    ("BACKGROUND",   (0,0), (-1,-1), GRAY),
]))
elements.append(wrapper4)

doc.build(elements)
print(f"PDF created: {OUTPUT}")
