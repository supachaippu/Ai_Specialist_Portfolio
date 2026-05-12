import pdfplumber
import sys

def test_extract(pdf_path, password=''):
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            print(f"Total Pages: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages):
                print(f"--- PAGE {i+1} ---")
                text = page.extract_text()
                print(text[:500]) # Print first 500 chars to see structure
                print("-------------")
                
                # Try table extraction
                tables = page.extract_tables()
                if tables:
                    print(f"Found {len(tables)} tables on page {i+1}")
                    for j, table in enumerate(tables):
                        print(f"Table {j+1} top 3 rows:")
                        for row in table[:3]:
                            print(row)
                break # Just first page for now
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error details: {repr(e)}")

if __name__ == '__main__':
    test_extract('../AcctSt_May26.pdf')
