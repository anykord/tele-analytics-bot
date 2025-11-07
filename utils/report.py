import io, csv, json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class ReportGenerator:
    def __init__(self, google_service_file="google.json"):
        self.google_service_file = google_service_file

    def to_pdf(self, title, report_text, out_path):
        c = canvas.Canvas(out_path, pagesize=A4)
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
        return out_path

    def to_csv(self, messages, out_path):
        keys = ["id","date","sender","text"]
        with open(out_path, "w", encoding="utf-8-sig", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for m in messages:
                writer.writerow({k: m.get(k,"") for k in keys})
        return out_path

    def to_json(self, messages, out_path):
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return out_path

    def to_google_sheet(self, title, messages):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.google_service_file, scope)
        gc = gspread.authorize(creds)
        sh = gc.create(title)
        worksheet = sh.get_worksheet(0)
        header = ["id","date","sender","text"]
        worksheet.append_row(header)
        for m in messages:
            worksheet.append_row([m.get("id"), m.get("date"), m.get("sender"), m.get("text")])
        sh.share(None, perm_type='anyone', role='reader')
        return sh.url
