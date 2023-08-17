import csv
import socket
import time
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from tqdm import tqdm
import error_handling


# Gets the text of an element
def get_element_text(element):
    return element.text.strip() if element else ""


# Gets the text of a list of elements
def get_element_text_list(elements):
    return [element.text.strip() for element in elements] if elements else []


# Scrapes a single bookmark entry
def scrape_single_bookmark(bookmark, csvwriter):

    # Get title from the bookmark
    title_element = bookmark.select_one("h4 a:nth-of-type(1)")
    if title_element:
        title = get_element_text(title_element)
    else:
        return

    # Get the other data from the bookmark
    authors = get_element_text_list(bookmark.select("a[rel='author']"))
    fandoms = get_element_text_list(bookmark.select(".fandoms a"))
    warnings = get_element_text_list(bookmark.select("li.warnings"))
    ratings = get_element_text_list(bookmark.select_one("span.rating"))
    categories = get_element_text_list(bookmark.select("span.category"))
    words = get_element_text(bookmark.select_one("dd.words") or bookmark.select_one("dd"))
    tags = get_element_text_list(bookmark.select("li.freeforms"))
    characters = get_element_text_list(bookmark.select("li.characters"))
    relationships = get_element_text_list(bookmark.select("li.relationships"))
    date_bookmarked = get_element_text(bookmark.select_one("div.user p.datetime"))
    url = "https://archiveofourown.org" + bookmark.select_one("h4 a:nth-of-type(1)")["href"]
    date_updated = get_element_text(bookmark.select_one("p.datetime"))

    # Replace commas with semicolons in ratings and categories (important when bookmark is a series)
    ratings = [rating.replace(',', ';') for rating in ratings]
    categories = [category.replace(',', ';') for category in categories]

    # Write bookmark data to CSV, replace empty author with "Anonymous"
    csvwriter.writerow([
        url, title, '; '.join(authors) if authors else 'Anonymous', '; '.join(fandoms), '; '.join(warnings),
        '; '.join(ratings), '; '.join(categories), '; '.join(characters),
        '; '.join(relationships), '; '.join(tags), words, date_bookmarked, date_updated
    ])


# Scrape the bookmarks of a user
def scrape_bookmarks(username, start_page, end_page, session, delay, logger):
    with open(username + '_bookmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        logger.info(f"CSV file created: {username}_bookmarks.csv")

        # Write header row to CSV file
        csvwriter.writerow(
            ['URL', 'Title', 'Authors', 'Fandoms', 'Warnings', 'Rating', 'Categories', 'Characters',
             'Relationships', 'Tags', 'Words', 'Date Bookmarked', 'Date Updated'])
        logger.info("Header row written to CSV file")

        num_bookmarks = 0
        total_pages = end_page - start_page + 1

        # Loop through pages and scrape bookmarks
        for page in tqdm(range(start_page, end_page + 1), total=total_pages, desc="Scraping"):
            try:
                response = session.get(
                    f"https://archiveofourown.org/users/{username}/bookmarks?private=true&page={page}") if \
                    session else requests.get(f"https://archiveofourown.org/users/{username}/bookmarks?page={page}")
                time.sleep(delay)
                soup = BeautifulSoup(response.text, 'html.parser')
                logger.info(f"Scraping page {page}")

            except (requests.exceptions.RequestException, socket.timeout) as error:
                error_handling.handle_request_error(error, logger)
                return

            if error_handling.handle_retry_later(response, logger):
                return

            # Loop through each bookmark on the page
            for bookmark in soup.select("li.bookmark"):
                scrape_single_bookmark(bookmark, csvwriter)
                num_bookmarks += 1

        # Print completion message
        logger.info(f"Scraping complete. Scraped {num_bookmarks} bookmarks.")
        print("\nAll done! \nYour bookmarks have been saved to {}{}{}_bookmarks.csv{}.".format(Fore.CYAN,
                                                                                               username, Fore.RESET,
                                                                                               Fore.RESET))
        print("Scraped {}{}{} bookmarks.".format(Fore.CYAN, num_bookmarks, Fore.RESET))
