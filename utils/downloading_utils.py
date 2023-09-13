import os
import re
import time
from datetime import datetime
import warnings

import ebooklib
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
from tqdm import tqdm

from . import error_handling

# Before importing ebooklib, filter out the specific warning
warnings.filterwarnings("ignore", category=UserWarning,
                        message="In the future version we will turn default option ignore_ncx to True.")


# Cleans the folder name to be used as a folder name
def clean_folder_name(name):
    forbidden_characters = r'<>:"/\|?*'
    return ''.join(char for char in name if char not in forbidden_characters)


# Cleans the work title to be used as a file name
def clean_work_title(title):
    forbidden_characters = r'<>:"/\|?*'
    cleaned_title = ''.join(char for char in title if char not in forbidden_characters)
    return cleaned_title[:50]


# Date patterns to get the last date in the file (either Completed, Updated, or Published)
date_patterns = [
    (r'Completed: (\d{4}-\d{2}-\d{2})', 'Completed'),
    (r'Updated: (\d{4}-\d{2}-\d{2})', 'Updated'),
    (r'Published: (\d{4}-\d{2}-\d{2})', 'Published')
]


# Extracts the date from an EPUB file
def extract_epub_date(file_path):
    if not file_path.endswith('.epub'):
        # This file is not an EPUB file, so return None or handle it accordingly.
        return None

    # Open the EPUB file
    book = ebooklib.epub.read_epub(file_path)  # You need to open the EPUB file using ebooklib

    # Initialize an empty string to store the text content
    text_content = ""

    # Extract the text content from the EPUB
    for item in book.get_items():
        if isinstance(item, ebooklib.epub.EpubHtml):  # Use ebooklib.epub.EpubHtml for HTML content
            text_content += item.get_body_content().decode('utf-8')

    # Search for date patterns in the text content
    for pattern, label in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            epub_date = match.group(1)
            epub_date = datetime.strptime(epub_date, "%Y-%m-%d")
            return epub_date

    # Return a default message if no date is found
    return None


# Extracts the work URLs from a page of bookmarks
def extract_work_urls_from_page(url, session, logger):
    work_urls = []

    try:
        response = session.get(url) if session else requests.get(url)
        response.raise_for_status()  # Check for request errors

        soup = BeautifulSoup(response.content, 'html.parser')

        for bookmark in soup.select("li.bookmark"):
            work_url_element = bookmark.select_one("h4 a:nth-of-type(1)")
            if work_url_element:
                work_url = "https://archiveofourown.org" + work_url_element["href"]
                if "/series/" in work_url:
                    series_work_urls = extract_work_urls_from_series(work_url, session, logger)
                    work_urls.extend(series_work_urls)
                else:
                    work_urls.append(work_url)

    except requests.exceptions.RequestException as error:
        error_handling.handle_request_error(error, logger)

    return work_urls


# Extracts the work URLs from series
def extract_work_urls_from_series(series_url, session, logger):
    series_work_urls = []

    try:
        response = session.get(series_url) if session else requests.get(series_url)
        response.raise_for_status()  # Check for request errors

        soup = BeautifulSoup(response.content, 'html.parser')

        series_work_elements = soup.select("ul.series.work.index.group li.work.blurb.group")
        for series_work_element in series_work_elements:
            series_work_url_element = series_work_element.select_one("h4 a:nth-of-type(1)")
            if series_work_url_element:
                series_work_url = "https://archiveofourown.org" + series_work_url_element["href"]
                series_work_urls.append(series_work_url)

    except requests.exceptions.RequestException as error:
        error_handling.handle_request_error(error, logger)  # Handle request error

    return series_work_urls


# Downloads the works from the given work URLs
def download_works_from_urls(work_url, session, chosen_format, action, logger):
    no_update_needed = False
    try:
        response = session.get(work_url) if session else requests.get(work_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            work_title = soup.find("h2", class_="title heading").get_text(strip=True)
            author_elements = soup.select(".byline a[rel='author']")
            max_display_authors = 3
            work_authors = [author.get_text(strip=True) for author in author_elements[:max_display_authors]]
            if not work_authors:
                work_authors = ["Anonymous"]

            work_fandoms = [fandom.get_text(strip=True) for fandom in soup.select(".fandom a")]

            update_date_element = soup.select_one("dd.status") or soup.select_one("dd.published")
            if update_date_element:
                update_date_element = datetime.strptime(update_date_element.get_text(strip=True), "%Y-%m-%d")

            download_menu = soup.find("li", class_="download")
            if download_menu:
                format_links = {
                    "EPUB": "EPUB", "MOBI": "MOBI", "PDF": "PDF", "HTML": "HTML", "AZW3": "AZW3"
                }

                format_name = format_links.get(chosen_format)
                if format_name:
                    format_link = download_menu.find("a", href=True, string=format_name)
                    if format_link:
                        format_url = "https://archiveofourown.org" + format_link["href"]

                        for fandom in work_fandoms:
                            cleaned_fandom = clean_folder_name(fandom)
                            folder_path = os.path.join("Downloaded Works", cleaned_fandom)
                            os.makedirs(folder_path, exist_ok=True)

                            cleaned_work_title = clean_work_title(work_title)
                            authors_string = ' & '.join(work_authors)
                            file_name = f"{cleaned_work_title} by {authors_string}.{format_name.lower()}"
                            file_path = os.path.join(folder_path, file_name)

                            if os.path.exists(file_path):
                                if action == "download updates":
                                    epub_date = extract_epub_date(file_path)
                                    if update_date_element > epub_date or epub_date is None or update_date_element \
                                            is None:
                                        download_file(file_path, format_url, file_name, cleaned_fandom, logger)
                                    else:
                                        logger.info(f"'{file_name}' in '{cleaned_fandom}' does not need to be updated.")
                                        no_update_needed = True  # (assumes all works are up-to-date)
                                        print("All works are up-to-date.")
                                else:
                                    logger.info(f"'{file_name}' in '{cleaned_fandom}' already exists. Skipping.")
                            else:
                                download_file(file_path, format_url, file_name, cleaned_fandom, logger)

    except requests.RequestException as error:
        error_handling.handle_request_error(error, logger)

    return no_update_needed


# Define a separate function for downloading a file
def download_file(file_path, format_url, file_name, cleaned_fandom, logger):
    response_format = requests.get(format_url)
    if response_format.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response_format.content)
        logger.info(
            f"'{file_name}' downloaded successfully to '{cleaned_fandom}' folder."
        )


def download_bookmarks(username, logged_in, start_page, end_page, session, chosen_format, delay, action, logger):
    if action == "download updates":
        base_url = f"https://archiveofourown.org/users/{username}/bookmarks?bookmark_search%5Bbookmark_query%5D" \
                   f"=&bookmark_search%5Bbookmarkable_query%5D=&bookmark_search%5Bexcluded_bookmark_tag_names%5D" \
                   f"=&bookmark_search%5Bexcluded_tag_names%5D=&bookmark_search%5Blanguage_id%5D=&bookmark_search" \
                   f"%5Bother_bookmark_tag_names%5D=&bookmark_search%5Bother_tag_names%5D=&bookmark_search%5Brec%5D=0" \
                   f"&bookmark_search%5Bsort_column%5D=bookmarkable_date&bookmark_search%5Bwith_notes%5D=0&commit" \
                   f"=Sort+and+Filter"
        logged_in_base_url = base_url + "&private=true"
    else:
        base_url = f"https://archiveofourown.org/users/{username}/bookmarks"
        logged_in_base_url = base_url + "?private=true"

    page_number = start_page

    while page_number <= end_page:
        if action == "download updates":
            bookmark_page_url = f"{logged_in_base_url}&page={page_number}" if logged_in else \
                f"{base_url}&page={page_number}"
        else:
            bookmark_page_url = f"{logged_in_base_url}&page={page_number}" if logged_in else f"{base_url}?page=" \
                                                                                             f"{page_number}"
        work_urls = extract_work_urls_from_page(bookmark_page_url, session, logger)

        if not work_urls:
            break

        # Loop through extracted work URLs and download
        for work_url in tqdm(work_urls, desc=f"Downloading works from page {page_number}", leave=True):
            no_update_needed = download_works_from_urls(work_url, session, chosen_format, action, logger)
            if no_update_needed:
                return
            time.sleep(delay)

        page_number += 1
