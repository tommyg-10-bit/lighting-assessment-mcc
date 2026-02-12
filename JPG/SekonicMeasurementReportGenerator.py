import os
import pandas as pd
from PIL import Image
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from openai import OpenAI

# Initialize OpenAI client from environment (do not hardcode API keys)
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None
else:
    client = None

def csv_to_pdf(csv_path, output_pdf):
    """Converts CSV to PDF with full-width first column."""
    df = pd.read_csv(csv_path)
    data = [df.columns.to_list()] + df.values.tolist()
    
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    # Set colWidths: First column is 200pts to ensure full visibility
    table = Table(data, colWidths=[200] + [None]*(len(df.columns)-1))
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    doc.build([table])

def create_fixture_report(fixture_id, files):
    writer = PdfWriter()
    
    # 1. Order files: Fixture (Image), SPD (Image), CCT (Image), CSV
    # Custom logic to identify which JPG is which based on keywords in filename
    img_order = {"fixture": None, "spd": None, "cct": None}
    csv_file = None
    
    for f in files:
        low = f.lower()
        if f.endswith('.csv'): csv_file = f
        elif "fixture" in low: img_order["fixture"] = f
        elif "spd" in low or "spectral" in low: img_order["spd"] = f
        elif "cct" in low: img_order["cct"] = f

    # Add images to PDF in order
    for key in ["fixture", "spd", "cct"]:
        img_path = img_order[key]
        if img_path:
            temp_pdf = f"temp_{key}.pdf"
            Image.open(img_path).convert("RGB").save(temp_pdf, "PDF")
            writer.add_page(PdfReader(temp_pdf).pages[0])
            os.remove(temp_pdf)

    # 2. Add CSV last
    if csv_file:
        csv_pdf = "temp_csv.pdf"
        csv_to_pdf(csv_file, csv_pdf)
        writer.add_page(PdfReader(csv_pdf).pages[0])
        os.remove(csv_pdf)

    combined_filename = f"Merged_{fixture_id}.pdf"
    with open(combined_filename, "wb") as f:
        writer.write(f)
    
    # 3. Submit to ChatGPT for Maui Ordinance Summary
    generate_summary_and_prepend(combined_filename, csv_file)

def generate_summary_and_prepend(pdf_path, csv_path=None):
    """Generate a one-page summary using OpenAI and prepend it to the PDF.

    This implementation sends a CSV snippet (if available) as plain text to the
    model and receives a text summary. The summary is converted to a PDF page
    and prepended to the given PDF. Requires OPENAI_API_KEY in environment.
    """
    if client is None:
        print("OpenAI client not configured (OPENAI_API_KEY missing). Skipping summary generation.")
        return

    # First attempt: upload full PDF to OpenAI (preferred)
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    summary_text = None

    try:
        with open(pdf_path, "rb") as pdf_file:
            try:
                upload = client.files.upload(file=pdf_file, file_name=os.path.basename(pdf_path))
                file_id = getattr(upload, "id", None) or upload.get("id")
            except Exception:
                # Some SDK versions expect file= or different params; re-open and try generic call
                pdf_file.seek(0)
                upload = client.files.upload(file=pdf_file)
                file_id = getattr(upload, "id", None) or upload.get("id")

        if file_id:
            system_msg = {"role": "system", "content": "You are a lighting compliance expert for Maui County. Provide a concise one-page summary evaluating shielding, downward direction, and the spectral ratio 400-500nm to 400-700nm (threshold 0.02)."}
            user_msg = {"role": "user", "content": f"Attached file id: {file_id}. Analyze the attached measurement report PDF and state whether the fixture meets Maui's outdoor lighting ordinance. Provide a short compliance recommendation and the key supporting numbers."}

            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[system_msg, user_msg],
                    file_ids=[file_id],
                    max_tokens=800,
                )
                try:
                    summary_text = resp.choices[0].message.content
                except Exception:
                    summary_text = getattr(resp.choices[0].message, 'content', None) or str(resp)
            except Exception:
                # Some SDKs accept 'files' or other param names; try an alternative call
                try:
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[system_msg, user_msg],
                        files=[file_id],
                        max_tokens=800,
                    )
                    summary_text = resp.choices[0].message.content
                except Exception as e:
                    print(f"Full-PDF chat request failed: {e}")

    except Exception as e:
        print(f"PDF upload attempt failed: {e}")

    # If full-PDF path failed, fall back to CSV snippet (previous behavior)
    if not summary_text:
        csv_snippet = None
        if csv_path and os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path, header=None)
                snippet = df.head(60).to_csv(index=False, header=False)
                csv_snippet = snippet
            except Exception as e:
                print(f"Failed to read CSV for summary: {e}")

        system_msg = {"role": "system", "content": "You are a lighting compliance expert for Maui County. Provide a concise one-page summary evaluating shielding, downward direction, and the spectral ratio 400-500nm to 400-700nm (threshold 0.02)."}
        user_content = "Analyze the attached measurement report and state whether the fixture meets Maui's outdoor lighting ordinance. Provide a short compliance recommendation and the key supporting numbers."
        if csv_snippet:
            user_content += "\n\nCSV_SNIPPET:\n" + csv_snippet

        messages = [system_msg, {"role": "user", "content": user_content}]

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=800,
            )
            try:
                summary_text = resp.choices[0].message.content
            except Exception:
                summary_text = getattr(resp.choices[0].message, 'content', None) or str(resp)
        except Exception as e:
            print(f"OpenAI request failed: {e}")

    if not summary_text:
        print(f"No summary generated for {pdf_path}")
        return

    # Convert summary_text to a PDF and prepend
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    summary_pdf = "summary_temp.pdf"
    c = canvas.Canvas(summary_pdf, pagesize=letter)
    width, height = letter
    margin = 72
    y = height - margin
    c.setFont("Helvetica", 10)

    import textwrap
    lines = []
    for paragraph in summary_text.split("\n"):
        wrapped = textwrap.wrap(paragraph, 90)
        if not wrapped:
            lines.append("")
        else:
            lines.extend(wrapped)

    for line in lines:
        if y < margin + 12:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - margin
        c.drawString(margin, y, line)
        y -= 12

    c.save()

    try:
        reader_orig = PdfReader(pdf_path)
        reader_summary = PdfReader(summary_pdf)
        writer = PdfWriter()
        for p in reader_summary.pages:
            writer.add_page(p)
        for p in reader_orig.pages:
            writer.add_page(p)

        out_path = f"Summarized_{os.path.basename(pdf_path)}"
        with open(out_path, "wb") as out_f:
            writer.write(out_f)

        os.replace(out_path, pdf_path)
        os.remove(summary_pdf)
        print(f"Prepended summary to {pdf_path}")

    except Exception as e:
        print(f"Failed to prepend summary PDF: {e}")

# Main execution loop
directory = "./"
all_files = os.listdir(directory)
groups = {}

for f in all_files:
    if "SL_" in f:
        # Extract 13 chars following SL_
        idx = f.find("SL_") + 3
        fid = f[idx : idx + 13]
        groups.setdefault(fid, []).append(os.path.join(directory, f))

for fid, files in groups.items():
    if len(files) == 4:
        create_fixture_report(fid, files)