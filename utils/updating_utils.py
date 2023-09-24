import re
from datetime import datetime

import ebooklib
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from ebooklib import epub

# Date patterns to get the last date in the file (either Completed, Updated, or Published)
date_patterns = [
    (r'Completed: (\d{4}-\d{2}-\d{2})', 'Completed'),
    (r'Updated: (\d{4}-\d{2}-\d{2})', 'Updated'),
    (r'Published: (\d{4}-\d{2}-\d{2})', 'Published')
]


def extract_epub_date(file_path):
    epub_book = ebooklib.epub.read_epub(file_path)

    text_content = ""

    for item in epub_book.get_items():
        if isinstance(item, ebooklib.epub.EpubHtml):
            text_content += item.get_body_content().decode('utf-8')

    for pattern, label in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            file_date = match.group(1)
            file_date = datetime.strptime(file_date, "%Y-%m-%d")
            return file_date

    return None


def extract_pdf_date(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)

        text_content = ""

        page = pdf_reader.pages[0]
        text_content += page.extract_text()

        for pattern, label in date_patterns:
            match = re.search(pattern, text_content)
            if match:
                file_date = match.group(1)
                file_date = datetime.strptime(file_date, "%Y-%m-%d")
                return file_date

    return None


# Extracts the date from an HTML file
def extract_html_date(file_path):
    with open(file_path, 'r', encoding='utf-8') as html_file:
        html_content = html_file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text()

    for pattern, label in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            file_date = match.group(1)
            file_date = datetime.strptime(file_date, "%Y-%m-%d")

            return file_date

    return None
