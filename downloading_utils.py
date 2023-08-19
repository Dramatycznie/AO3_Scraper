import os
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import error_handling
# add error handling to functions


# Cleans the folder name to be used as a folder name
def clean_folder_name(name):
    forbidden_characters = r'<>:"/\|?*'
    return ''.join(char for char in name if char not in forbidden_characters)


# Cleans the work title to be used as a file name
def clean_work_title(title):
    forbidden_characters = r'<>:"/\|?*'
    cleaned_title = ''.join(char for char in title if char not in forbidden_characters)
    return cleaned_title[:50]


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
        return

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
        return

    return series_work_urls


# Downloads the works from the given work URLs
def download_works_from_urls(work_url, session, chosen_format, delay, logger):
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
                                logger.info(
                                    f"'{file_name}' already exists in '{cleaned_fandom}' folder. "
                                    f"Skipping download.")
                            else:
                                response_format = requests.get(format_url)
                                if response_format.status_code == 200:
                                    with open(file_path, "wb") as file:
                                        file.write(response_format.content)
                                    logger.info(
                                        f"'{file_name}' downloaded successfully to '{cleaned_fandom}' "
                                        f"folder.")
                                    time.sleep(delay)

    except requests.RequestException as error:
        error_handling.handle_request_error(error, logger)
        return


def download_bookmarks(url, start_page, end_page, session, chosen_format, delay, logger):
    for page in range(start_page, end_page + 1):
        bookmark_page_url = f"{url}?page={page}"
        work_urls = extract_work_urls_from_page(bookmark_page_url, session, logger)

        # Loop through extracted work URLs and download
        for work_url in tqdm(work_urls, desc=f"Downloading works from page {page}", leave=True):
            download_works_from_urls(work_url, session, chosen_format, delay, logger)
