from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import sqlite3

def generate_report():
    doc = SimpleDocTemplate("autosense_report.pdf")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AutoSense – AI System Intelligence Report", styles["Title"]))
    story.append(Spacer(1,10))

    conn = sqlite3.connect("autosense.db")
    c = conn.cursor()
    rows = c.execute("SELECT cpu, ram, disk FROM system_stats ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()

    avg_cpu = sum(r[0] for r in rows)/len(rows)
    avg_ram = sum(r[1] for r in rows)/len(rows)
    avg_disk = sum(r[2] for r in rows)/len(rows)

    story.append(Paragraph(f"Average CPU Usage: {round(avg_cpu,2)}%", styles["BodyText"]))
    story.append(Paragraph(f"Average RAM Usage: {round(avg_ram,2)}%", styles["BodyText"]))
    story.append(Paragraph(f"Average Disk Usage: {round(avg_disk,2)}%", styles["BodyText"]))

    doc.build(story)
    return "autosense_report.pdf"
