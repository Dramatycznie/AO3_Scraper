import re
from datetime import datetime
import ebooklib
from ebooklib import epub


# Date patterns to get the last date in the file (either Completed, Updated, or Published)
date_patterns = [
    (r'Completed: (\d{4}-\d{2}-\d{2})', 'Completed'),
    (r'Updated: (\d{4}-\d{2}-\d{2})', 'Updated'),
    (r'Published: (\d{4}-\d{2}-\d{2})', 'Published')
]


# Extracts the date from an EPUB file
def extract_epub_date(file_path):
    if not file_path.endswith('.epub'):
        return None

    book = ebooklib.epub.read_epub(file_path)

    text_content = ""

    for item in book.get_items():
        if isinstance(item, ebooklib.epub.EpubHtml):
            text_content += item.get_body_content().decode('utf-8')

    for pattern, label in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            epub_date = match.group(1)
            epub_date = datetime.strptime(epub_date, "%Y-%m-%d")
            return epub_date

    return None
