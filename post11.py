
from pypdf import PdfReader, PdfWriter
import requests

url = "https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1037036209"

response = requests.get(url)

with open("sample_pdf.pdf", "wb") as file:
    file.write(response.content)

print("download complete")

# Path to your PDF file
pdf_path = "sample_pdf.pdf"

# Create a PdfReader object
reader = PdfReader(pdf_path)

# Extract text from all pages
with open("text_file.txt", "w") as file2: 
    for page_num, page in enumerate(reader.pages):
        file2.write(f"\n\n--- Page {page_num + 1} ---")
        file2.write(page.extract_text())

print("writing complete")