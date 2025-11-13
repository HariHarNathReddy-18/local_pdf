import fitz  # PyMuPDF
import pathlib
import sys

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    out_lines = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            out_lines.append(f"\n--- Page {page_num} ---\n")
            out_lines.append(text)
    return "\n".join(out_lines)

def main():
    default_pdf = pathlib.Path(__file__).resolve().parents[1] / "data" / "sample.pdf"
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else str(default_pdf)

    try:
        pdf_path = pathlib.Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        text = extract_text_from_pdf(str(pdf_path))
        if not text.strip():
            print("No extracted text (PDF may be scanned as images).")
        else:
            print(text)  # print all text for now
        return text
    except Exception as e:
        print("Error:", e)
        return None

if __name__ == "__main__":
    text = main()  # capture returned text

    if text:
        project_root = pathlib.Path(__file__).resolve().parents[1]
        data_folder = project_root / "data"
        data_folder.mkdir(parents=True, exist_ok=True)

        output_path = data_folder / "sample_text.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Saved extracted text to: {output_path}")
