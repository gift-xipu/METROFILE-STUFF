"""
OCR extraction for uploaded invoices. Since real-world invoices here are
scanned/photographed with variable quality, this is intentionally a
BEST-EFFORT first pass -- every field it finds gets shown back to the
user as an editable form field, never submitted blindly. Getting a
credit note wrong is a financial/audit problem, so human confirmation
of every extracted value is a permanent part of this workflow, not a
temporary safeguard.
"""
import re
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def extract_text_from_pdf(pdf_path):
    """Try native text extraction first (fast, accurate for digital PDFs);
    fall back to OCR page-by-page if no text layer is found (scanned PDF)."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    if len(text.strip()) < 20:
        # No usable text layer -- this is a scanned PDF, OCR it
        images = convert_from_path(pdf_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    return text

def extract_invoice_fields(text):
    """
    Best-effort pattern matching for common Metrofile invoice fields.
    Returns a dict -- any field not found is left blank for the user
    to fill in manually rather than guessed.
    """
    fields = {
        "invoice_no": "",
        "invoice_date": "",
        "account_no": "",
        "client_name": "",
        "region": "",
        "invoice_amount_excl": "",
        "invoice_amount_incl": "",
    }

    m = re.search(r"INVOICE\s*No\.?\s*[:\-]?\s*(\w+)", text, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(ZM\d{5,})\b", text)
    if not m:
        m = re.search(r"\b(BM\d{5,})\b", text)
    if not m:
        m = re.search(r"\b(SIMRM\w+\d+)\b", text)
    if m:
        fields["invoice_no"] = m.group(1)

    m = re.search(r"Invoice Date\s*[:\-]?\s*(\d{1,4}[/\-]\d{1,2}[/\-]\d{1,4})", text, re.IGNORECASE)
    if m:
        fields["invoice_date"] = m.group(1)

    m = re.search(r"Customer\s*[:\-]?\s*(\d{4,})", text, re.IGNORECASE)
    if not m:
        m = re.search(r"Account\s*(?:No\.?|Number)\s*[:\-]?\s*([\w\-]+)", text, re.IGNORECASE)
    if m:
        fields["account_no"] = m.group(1)

    m = re.search(r"^(.*?\(PTY\)\s*LTD.*?)$", text, re.IGNORECASE | re.MULTILINE)
    if m:
        fields["client_name"] = m.group(1).strip()

    m = re.search(r"Invoice Amount Excl\.?\s*=?>?\s*R?\s*([\d,]+\.\d{2})", text, re.IGNORECASE)
    if m:
        fields["invoice_amount_excl"] = m.group(1).replace(",", "")

    m = re.search(r"Invoice Amount Incl\.?\s*=?>?\s*R?\s*([\d,]+\.\d{2})", text, re.IGNORECASE)
    if m:
        fields["invoice_amount_incl"] = m.group(1).replace(",", "")

    return fields

def process_upload(file_path, file_ext):
    """Main entry point: takes a file path + extension, returns (raw_text, extracted_fields)."""
    ext = file_ext.lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        text = extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    fields = extract_invoice_fields(text)
    return text, fields
