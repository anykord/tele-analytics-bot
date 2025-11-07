import os, csv, json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        pass

    def to_pdf(self, title, report_text, out_dir="reports"):
        os.makedirs(out_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out_dir, f"report_{timestamp}.pdf")
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica", 12)
        y = height - 50
        c.drawString(40, y, title)
        y -= 30
        for line in report_text.split("\n"):
            c.drawString(40, y, line[:1000])
            y -= 14
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        return path

    def to_csv(self, messages, out_dir="reports", title="report"):
        os.makedirs(out_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out_dir, f"{title}_{timestamp}.csv")
        keys = ["id","date","sender","text"]
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for m in messages:
                writer.writerow({k: m.get(k,"") for k in keys})
        return path

    def to_json(self, messages, out_dir="reports", title="report"):
        os.makedirs(out_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(out_dir, f"{title}_{timestamp}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return path

