"""
Generate a detailed PDF describing Gemini integration opportunities and implementation
for the Flood Analysis Project.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_FILE = Path("Gemini_Integration_Strategy_Flood_Analysis_Project.pdf")
PROJECT_NAME = "Gemini Integration Strategy for Delhi Flood Intelligence Platform"
AUTHOR = "Prepared by OpenAI Codex for CodeNovaXNamit"


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0B1F33"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtitleCustom",
            parent=styles["Heading2"],
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#36516B"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#0F3D63"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubsectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor("#184E77"),
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#1F2933"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13,
            alignment=TA_LEFT,
            leftIndent=10,
            textColor=colors.HexColor("#1F2933"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallMuted",
            parent=styles["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5C6B7A"),
        )
    )
    return styles


def page_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#B9C7D6"))
    canvas.line(doc.leftMargin, height - 1.3 * cm, width - doc.rightMargin, height - 1.3 * cm)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor("#0F3D63"))
    canvas.drawString(doc.leftMargin, height - 1.05 * cm, "Gemini Integration Strategy")
    canvas.setFont("Helvetica", 8.2)
    canvas.setFillColor(colors.HexColor("#5C6B7A"))
    canvas.drawRightString(width - doc.rightMargin, height - 1.05 * cm, "Delhi Flood Intelligence Platform")
    canvas.line(doc.leftMargin, 1.2 * cm, width - doc.rightMargin, 1.2 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5C6B7A"))
    canvas.drawString(doc.leftMargin, 0.85 * cm, AUTHOR)
    canvas.drawRightString(width - doc.rightMargin, 0.85 * cm, f"Page {doc.page}")
    canvas.restoreState()


def p(text: str, styles, style_name: str = "BodyCustom"):
    return Paragraph(text, styles[style_name])


def section(title: str, styles):
    return Paragraph(title, styles["SectionTitle"])


def subsection(title: str, styles):
    return Paragraph(title, styles["SubsectionTitle"])


def bullets(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["BulletCustom"])) for item in items],
        bulletType="bullet",
        leftIndent=16,
    )


def code_block(code: str, styles):
    return Preformatted(
        code.strip(),
        ParagraphStyle(
            "CodeBlock",
            parent=styles["BodyCustom"],
            fontName="Courier",
            fontSize=8.1,
            leading=10,
            backColor=colors.HexColor("#F5F8FB"),
            borderWidth=0.5,
            borderColor=colors.HexColor("#D5E1EC"),
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
        ),
    )


def table(data, widths=None):
    tbl = Table(data, colWidths=widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F3D63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.4),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FBFD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F8FB")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D3DF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tbl


def build_story():
    styles = build_styles()
    story = []
    today = datetime.now().strftime("%d %B %Y")

    story.append(Spacer(1, 4.8 * cm))
    story.append(Paragraph(PROJECT_NAME, styles["TitleCustom"]))
    story.append(
        Paragraph(
            "A complete technical and strategic document covering current Gemini usage, immediate next features, "
            "competition value, architecture changes, prompt grounding, demo flow, and production roadmap.",
            styles["SubtitleCustom"],
        )
    )
    story.append(Spacer(1, 1.1 * cm))
    story.append(Paragraph(f"<b>Author</b>: {AUTHOR}", styles["BodyCustom"]))
    story.append(Paragraph(f"<b>Date</b>: {today}", styles["BodyCustom"]))
    story.append(Spacer(1, 1.8 * cm))
    story.append(
        p(
            "This report is written specifically for competition submission, technical presentation, viva discussion, "
            "and engineering implementation planning.",
            styles,
            "SmallMuted",
        )
    )
    story.append(PageBreak())

    story.append(section("1. Executive Summary", styles))
    story.append(
        p(
            "The Flood Analysis Project already contains a meaningful and competition-valid Gemini integration path. "
            "Gemini is best used not as a generic chatbot, but as an intelligence layer on top of the project’s "
            "existing flood-risk pipeline. The deterministic machine-learning and geospatial components continue to "
            "produce the quantitative risk signals, while Gemini transforms those signals into actionable operational "
            "advice, explainable summaries, ward-level priorities, public advisories, and incident-response planning "
            "guidance. This document explains in full detail what Gemini can do now, what features can be added next, "
            "what data each feature uses, why those features make sense for a Google competition, and how to present "
            "the integration credibly to judges.",
            styles,
        )
    )

    story.append(section("2. Current Gemini Position in the Project", styles))
    story.append(
        bullets(
            [
                "The project already has Genkit and the Google GenAI plugin installed in the frontend runtime.",
                "A dedicated AI flow file exists and can call Gemini from server-side code in the Next.js application.",
                "The UI already has an advisory dialog component that is a natural place to display Gemini output.",
                "The backend already exposes structured flood pipeline results that can be used as grounding context.",
                "The ward map, hotspots, rainfall, readiness score, and uploaded scenario results provide rich structured input for Gemini.",
            ],
            styles,
        )
    )
    story.append(
        code_block(
            """
Existing technical fit:
- Next.js frontend
- Genkit runtime
- @genkit-ai/google-genai plugin
- AI advisory dialog in UI
- Flood pipeline summaries from backend
- Ward and hotspot data already available in memory
            """,
            styles,
        )
    )

    story.append(section("3. What Gemini Can Do Now", styles))
    story.append(
        p(
            "With the currently available project data, Gemini can immediately act as a grounded decision-support model. "
            "The key principle is that Gemini should not replace the flood-risk model. Instead, Gemini should interpret, "
            "explain, prioritize, summarize, and communicate the outputs of the deterministic and ML-driven system. "
            "This makes the integration technically honest and architecturally strong.",
            styles,
        )
    )

    story.append(subsection("3.1 Flood Response Copilot", styles))
    story.append(
        bullets(
            [
                "Generate a strategic summary from city readiness, rainfall, hotspot count, top wards, and latest pipeline run.",
                "Assign an escalation category such as severe, elevated, guarded, or stable.",
                "Recommend ranked municipal actions such as pumping, drain clearance, staff deployment, and traffic control.",
                "Highlight the wards that deserve the fastest intervention and explain why.",
                "Generate a short public advisory message for citizen communication or command-center briefings.",
            ],
            styles,
        )
    )

    story.append(subsection("3.2 Explanation Layer for Model Outputs", styles))
    story.append(
        bullets(
            [
                "Explain why the system is showing many hotspots in plain language for judges or civic officials.",
                "Translate technical fields such as max risk, mean risk, hotspot density, and rainfall intensity into a human-readable explanation.",
                "Clarify what the latest pipeline output means operationally rather than numerically.",
                "Help users understand which indicators suggest drain stress, localized waterlogging, or escalating inundation risk.",
            ],
            styles,
        )
    )

    story.append(subsection("3.3 Run Summary Generator", styles))
    story.append(
        bullets(
            [
                "Create a short executive report after each CSV scenario upload.",
                "Summarize how risky the current upload is compared to the default dashboard condition.",
                "Turn numerical outputs into a brief command note that can be copied into presentations.",
                "Generate a formatted textual explanation of the uploaded rainfall scenario for non-technical stakeholders.",
            ],
            styles,
        )
    )

    story.append(subsection("3.4 Ward Priority Narrative", styles))
    story.append(
        bullets(
            [
                "Describe the top 3 to 5 wards in order of attention required.",
                "Explain whether risk is driven by trend, population exposure, or current flood-risk score.",
                "Recommend different action types for different ward profiles.",
                "Produce a narrative that judges can understand without reading raw map layers or CSV rows.",
            ],
            styles,
        )
    )

    story.append(section("4. Detailed Use Cases Enabled by Gemini", styles))
    story.append(
        table(
            [
                ["Use Case", "Input Data", "Gemini Output", "Why It Matters"],
                ["Flood Response Copilot", "Rainfall, readiness, hotspots, top wards, latest pipeline summary", "Action plan, escalation level, public advisory", "Turns analytics into operations"],
                ["Scenario Upload Summary", "Uploaded scenario result and latest run", "Executive summary and next-step recommendations", "Useful after every prediction run"],
                ["Ward Attention Ranking", "Top wards with risk, population, trend", "Narrative ranking with reasons", "Improves explainability"],
                ["Viva / Judge Explanation Mode", "System metrics and architecture facts", "Human-readable explanation of what the system is doing", "Great for competition demo storytelling"],
                ["Officer Briefing Generator", "Latest run stats and current weather", "1-minute briefing note", "Useful for command center style presentation"],
                ["Citizen Advisory Draft", "Current conditions and severe wards", "Short advisory text", "Supports real public communication workflows"],
            ],
            widths=[4.0 * cm, 5.3 * cm, 4.8 * cm, 4.0 * cm],
        )
    )

    story.append(section("5. Best Immediate Gemini Feature", styles))
    story.append(
        p(
            "The strongest immediate feature is the Gemini Flood Response Copilot. It is the best first integration because it "
            "already matches the project architecture, uses real project data, improves the demo significantly, and can be defended "
            "technically in front of judges. This feature works by passing structured telemetry into Gemini and asking it to produce "
            "an operationally useful response constrained to known municipal flood-response behavior.",
            styles,
        )
    )
    story.append(
        bullets(
            [
                "It is grounded in real numerical data from the existing system.",
                "It does not replace the predictive model; it complements it.",
                "It creates an obvious Google AI story for the competition.",
                "It can be demonstrated quickly and clearly in the UI.",
                "It is aligned with public-sector disaster management use cases.",
            ],
            styles,
        )
    )

    story.append(section("6. Exact Data Gemini Should Receive", styles))
    story.append(
        p(
            "Gemini should receive only structured, meaningful, and bounded context. This reduces hallucination risk and makes the "
            "output easier to validate. The data should be concise enough to fit comfortably in a prompt but rich enough to support "
            "good reasoning.",
            styles,
        )
    )
    story.append(
        table(
            [
                ["Field", "Source", "Purpose in Prompt"],
                ["cityReadiness", "Frontend computed readiness score", "Expresses overall pre-monsoon preparedness"],
                ["hotspotsCount", "Frontend hotspot computation", "Shows concentration of critical areas"],
                ["rainfallMm", "Weather widget / live feed", "Represents current precipitation pressure"],
                ["weatherCondition", "Weather data", "Adds environmental context"],
                ["avgRiskPercent", "Ward aggregation in frontend", "Shows average city risk level"],
                ["totalPopulationAtRisk", "Ward aggregation in frontend", "Adds severity in human terms"],
                ["topWards", "Top ward list by flood risk", "Enables ward-specific recommendations"],
                ["latestPipelineRun.summary", "Backend API", "Grounds Gemini in actual upload-derived predictions"],
                ["latestPredictionDate", "Backend API", "Ties output to a known prediction window"],
            ],
            widths=[4.2 * cm, 5.2 * cm, 6.6 * cm],
        )
    )

    story.append(section("7. Prompt Design Strategy", styles))
    story.append(
        p(
            "Prompt quality matters more than merely calling the model. The project should use a highly constrained prompt that "
            "tells Gemini exactly what role it plays, what data it can trust, what output structure it must follow, and what it "
            "must not invent. This is especially important in a civic-risk application.",
            styles,
        )
    )
    story.append(
        code_block(
            """
You are Gemini acting as a municipal flood response copilot for Delhi.
Use only the structured telemetry provided below.
Do not invent external sensor values.
Do not claim certainty beyond the provided data.

Required tasks:
- Summarize the current situation
- Set escalation level
- Recommend ranked actions
- Identify priority wards
- Generate a short public advisory
- Mention any caveat if the latest pipeline run is missing
            """,
            styles,
        )
    )
    story.append(
        bullets(
            [
                "Role-based prompting improves consistency.",
                "Structured schema output reduces parsing errors.",
                "Operational constraints reduce hallucinated actions.",
                "Explicit caveat handling improves trust and judge confidence.",
            ],
            styles,
        )
    )

    story.append(section("8. Current Implemented Gemini Integration", styles))
    story.append(
        bullets(
            [
                "A server-side Genkit flow exists in the frontend AI layer.",
                "Gemini is called through `googleAI.model('gemini-2.5-flash')`.",
                "The flow uses structured input and structured output validation.",
                "If no key is available or the model request fails, the system falls back to deterministic local advice.",
                "The advisory dialog surfaces source, model identity, recommendation set, ward focus, and grounding notes.",
            ],
            styles,
        )
    )
    story.append(
        code_block(
            """
Current implemented outcome:
- Source-aware AI response
- Structured output schema
- Real flood telemetry grounding
- Fallback mode for resilience
- UI integration in Gemini Flood Copilot dialog
            """,
            styles,
        )
    )

    story.append(section("9. Additional Gemini Features That Can Be Added Next", styles))
    story.append(subsection("9.1 Incident Brief Generator", styles))
    story.append(
        bullets(
            [
                "After every pipeline run, Gemini generates a formal incident brief.",
                "The brief can include severity, priority wards, possible consequences, and immediate actions.",
                "This is useful for PDF export, email summaries, or presentations.",
            ],
            styles,
        )
    )
    story.append(subsection("9.2 Queryable Flood Intelligence Assistant", styles))
    story.append(
        bullets(
            [
                "Users can ask natural-language questions about the latest run.",
                "Examples: Which wards are highest risk? Why did readiness drop? Which areas need pump deployment first?",
                "Gemini can answer using run summaries and ward metadata.",
            ],
            styles,
        )
    )
    story.append(subsection("9.3 Comparative Scenario Explanation", styles))
    story.append(
        bullets(
            [
                "Compare the current uploaded scenario with the last successful run.",
                "Explain whether the flood outlook is worsening or improving.",
                "Summarize delta in hotspot count, max risk, and exposed wards.",
            ],
            styles,
        )
    )
    story.append(subsection("9.4 Administrative Report Writer", styles))
    story.append(
        bullets(
            [
                "Auto-generate a project-report section or command memo from current outputs.",
                "Useful for judges, professors, and municipal demo audiences.",
                "Could export to PDF, plain text, or markdown.",
            ],
            styles,
        )
    )
    story.append(subsection("9.5 Multilingual Advisory Output", styles))
    story.append(
        bullets(
            [
                "Generate advisories in English and Hindi.",
                "This would make the project stronger for public-sector deployment relevance.",
                "Gemini is naturally suited to multilingual instruction and controlled output format.",
            ],
            styles,
        )
    )

    story.append(section("10. Why Gemini Is a Better Fit Than Vision AI Here", styles))
    story.append(
        p(
            "This project is primarily built around CSV-based rainfall data, structured geospatial information, ward features, "
            "and prediction summaries. It does not currently rely on image-heavy inputs such as satellite frames, street flood "
            "photography, or scanned administrative forms. Because of that, forcing Vision AI into the submission would likely "
            "look artificial. Gemini is the better match because the project’s strongest need is interpretation and grounded "
            "decision support over structured numerical and geospatial outputs.",
            styles,
        )
    )
    story.append(
        bullets(
            [
                "Gemini fits the existing data shape.",
                "Gemini improves explainability, which the project currently lacks most.",
                "Gemini supports natural-language outputs required in a polished competition demo.",
                "Vision AI would only make sense later if flood images or satellite products are added.",
            ],
            styles,
        )
    )

    story.append(section("11. Competition Storyline for Judges", styles))
    story.append(
        p(
            "The project should be presented as a two-layer intelligence system. The first layer is the quantitative flood engine "
            "that predicts risk through rainfall processing, interpolation, engineered features, and a model ensemble. The second "
            "layer is Google Gemini, which interprets those predictions for action. This storyline is strong because it clearly "
            "separates deterministic analytics from generative reasoning.",
            styles,
        )
    )
    story.append(
        bullets(
            [
                "Layer 1: Predict where flood risk is building.",
                "Layer 2: Explain what city operators should do about it.",
                "Google AI is therefore used for response intelligence, not as a decorative chatbot.",
            ],
            styles,
        )
    )

    story.append(section("12. Demo Script for Presentation", styles))
    story.append(
        bullets(
            [
                "Open the dashboard and show ward map and readiness metrics.",
                "Upload a rainfall scenario CSV and run the prediction pipeline.",
                "Show that the system generates new hotspot outputs.",
                "Open the Gemini Flood Copilot dialog.",
                "Explain that Gemini is receiving real telemetry and latest run summary.",
                "Show escalation level, recommended actions, ward focus, and public advisory.",
                "Conclude by explaining that custom ML predicts risk while Gemini converts risk into operational planning guidance.",
            ],
            styles,
        )
    )

    story.append(section("13. Technical Architecture with Gemini Added", styles))
    story.append(
        code_block(
            """
+--------------------------+
| Rainfall CSV / Weather   |
+------------+-------------+
             |
             v
+--------------------------+
| Flood Prediction Engine  |
| - standardize input      |
| - interpolate to grid    |
| - engineer features      |
| - ensemble prediction    |
+------------+-------------+
             |
             v
+--------------------------+
| Structured Risk Context  |
| readiness, hotspots,     |
| top wards, latest run    |
+------------+-------------+
             |
             v
+--------------------------+
| Gemini via Genkit        |
| - strategic summary      |
| - actions                |
| - ward focus             |
| - public advisory        |
+------------+-------------+
             |
             v
+--------------------------+
| Dashboard AI Copilot UI  |
+--------------------------+
            """,
            styles,
        )
    )

    story.append(section("14. Security and Responsible AI Considerations", styles))
    story.append(
        bullets(
            [
                "Gemini should be used only with structured, low-risk operational metadata, not private citizen data.",
                "API keys must be stored in environment files and excluded from version control.",
                "The output should be framed as decision support, not as a final legal or emergency authority.",
                "Fallback logic is valuable because it prevents a blank failure state if Gemini is unavailable.",
                "Prompt instructions should explicitly restrict invention of external sensor values or false certainty.",
            ],
            styles,
        )
    )

    story.append(section("15. Risks and Limitations", styles))
    story.append(
        table(
            [
                ["Risk", "Description", "Mitigation"],
                ["Hallucinated advice", "Gemini may over-generalize beyond available data", "Use structured prompts, output schema, and grounding notes"],
                ["Missing AI key", "Feature silently downgrades without credentials", "Show source field and fallback mode visibly"],
                ["Over-reliance on AI text", "Users may prefer Gemini wording over quantitative outputs", "Keep original risk metrics visible beside AI response"],
                ["No historical comparison yet", "Gemini cannot compare trends deeply without stored run history analysis", "Add comparative prompt inputs in future version"],
                ["Prompt drift", "Unconstrained prompt changes may reduce reliability", "Version and test prompts like code"],
            ],
            widths=[3.6 * cm, 7.0 * cm, 6.0 * cm],
        )
    )

    story.append(section("16. Future Google AI Expansion Roadmap", styles))
    story.append(
        bullets(
            [
                "Gemini for incident report generation after every scenario run.",
                "Gemini for multilingual citizen advisories and administrative notes.",
                "Vertex AI if the project moves toward managed deployment, scaling, governance, and observability.",
                "Vision AI only if the project later adds satellite imagery or street-level flood image analysis.",
                "Gemini retrieval or context-augmented answering over archived flood runs and city preparedness documents.",
            ],
            styles,
        )
    )

    story.append(section("17. Recommended Submission Positioning", styles))
    story.append(
        p(
            "For submission, the project should be positioned as a Google AI-enhanced urban resilience system. The narrative should be: "
            "the platform predicts flood-risk hotspots through custom analytics and machine learning, then Google Gemini turns those "
            "results into actionable disaster-response intelligence for civic operators. This framing is specific, technically credible, "
            "and aligned with the practical value judges look for in real-world solution competitions.",
            styles,
        )
    )

    story.append(section("18. Final Recommendation", styles))
    story.append(
        p(
            "The project should continue using Gemini as a grounded decision-support copilot, not as a decorative chatbot. That is "
            "the most defensible Google AI use case for this system today. It uses existing real project data, improves clarity, "
            "increases practical usefulness, and makes the solution stronger in both technical and product terms. The next two best "
            "extensions are incident brief generation and comparative scenario explanation. Together, these additions would make the "
            "Google AI layer feel central to operations rather than optional.",
            styles,
        )
    )

    story.append(Spacer(1, 0.4 * cm))
    story.append(p("End of document.", styles, "SmallMuted"))
    return story


def generate_pdf(output_path: Path) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=2.1 * cm,
        bottomMargin=1.8 * cm,
        title=PROJECT_NAME,
        author=AUTHOR,
        subject="Detailed Gemini integration plan and capability report",
    )
    doc.build(build_story(), onFirstPage=page_header_footer, onLaterPages=page_header_footer)


if __name__ == "__main__":
    generate_pdf(OUTPUT_FILE)
    print(f"PDF generated successfully: {OUTPUT_FILE.resolve()}")
