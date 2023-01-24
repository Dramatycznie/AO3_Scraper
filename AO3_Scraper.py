import sys
import requests
from bs4 import BeautifulSoup
import time
import csv
from tqdm import tqdm


# Starting message
print("")
print("Hello and welcome to AO3 Bookmark Scraper")
print("")

# Prompt for username, pages to scrape, delay
username = input("Your username: ")
while True:
    try:
        page1 = int(input("Start scraping from page: "))
        page2 = int(input("Stop scraping at page: "))
        if page1 >= page2:
            print("Invalid input: End page should be bigger than start page")
            continue
        break
    except ValueError:
        print("Invalid input: Please enter a valid number")
while True:
    try:
        delay = int(input("Pick request interval (in seconds). 5 or more "))
        break
    except ValueError:
        print("Invalid input: Please enter a valid number")

# Base URL
base_url = "https://archiveofourown.org/users/" + username + "/bookmarks?page="

# Check the status code of the last page
try:
    response = requests.get(base_url + str(page2))
    if response.status_code != 200:
        print("Error: End page is out of range.")
        # Prompt the user for a new end page
        while True:
            try:
                page2 = int(input("Enter a new end page: "))
                response = requests.get(base_url + str(page2))
                if response.status_code == 200:
                    break
                else:
                    print("Error: End page is out of range.")
                    continue
            except ValueError:
                print("Invalid input: Please enter a valid number")
        print("Loading... Please wait")
except requests.exceptions.RequestException as e:
    print("Error: ", e)
    sys.exit(1)
print("Loading... Please wait")
# Open a CSV file for writing
with open(username + '_bookmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer object
    csvwriter = csv.writer(csvfile)
    # Write the header row
    csvwriter.writerow(
        ['URL', 'Title', 'Authors', 'Fandoms', 'Warnings', 'Rating', 'Categories', 'Characters', 'Relationships',
         'Tags', 'Words', 'Date Bookmarked'])

    for page in tqdm(range(page1, page2 + 1)):
        try:
            response = requests.get(base_url + str(page))
            time.sleep(delay)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            break

        # Extract the data using the provided selectors
        for bookmark in soup.select("li.bookmark"):
            title = bookmark.select_one("h4 a:nth-of-type(1)").text
            if title:
                authors = bookmark.select("a[rel='author']")
                fandoms = bookmark.select(".fandoms a")
                warnings = bookmark.select("li.warnings")
                rating = bookmark.select_one("span.rating")
                categories = bookmark.select("span.category")
                words = bookmark.select_one("dd.words") or bookmark.select_one("dd")
                tags = bookmark.select("li.freeforms")
                characters = bookmark.select("li.characters")
                relationships = bookmark.select("li.relationships")
                dates = bookmark.select_one("div.user p.datetime")
                url_str = bookmark.select_one("h4 a:nth-of-type(1)").attrs["href"]
                url = "https://archiveofourown.org" + url_str
                if authors:
                    author_str = ', '.join([author.text for author in authors])
                    author_list = author_str.split(', ')
                else:
                    author_str = "None"
                if fandoms:
                    fandom_str = ', '.join([fandom.text for fandom in fandoms])
                    fandom_list = fandom_str.split(', ')
                else:
                    fandom_str = "None"
                if warnings:
                    warning_str = ', '.join([warning.text for warning in warnings])
                    warning_list = warning_str.split(', ')
                else:
                    warning_str = "None"
                if rating:
                    rating_str = rating.text
                else:
                    rating_str = "None"
                if categories:
                    category_str = ', '.join([category.text for category in categories])
                    category_list = category_str.split(', ')
                else:
                    category_str = "None"
                if tags:
                    tag_str = ', '.join([tag.text for tag in tags])
                    tag_list = tag_str.split(', ')  # split the string by a comma and space
                else:
                    tag_list = "None"
                if characters:
                    character_str = ', '.join([character.text for character in characters])
                    character_list = character_str.split(', ')
                else:
                    character_list = "None"
                if relationships:
                    relationship_str = ', '.join([relationship.text for relationship in relationships])
                    relationship_list = relationship_str.split(', ')
                else:
                    relationship_str = "None"
                if dates:
                    date_str = dates.text
                else:
                    date_str = "None"
                if words:
                    words_str = words.text
                else:
                    words_str = "None"
                if url:
                    url = "https://archiveofourown.org" + bookmark.select_one("h4 a:nth-of-type(1)")["href"]
                else:
                    url = "None"

                # Write the data to the CSV file
                csvwriter.writerow([url, title, author_str, fandom_str, warning_str, rating_str, category_str,
                                    character_str, relationship_str, tag_str, words_str, date_str])
            else:
                print("Title not found for bookmark on page: ", page)
print("All done!")
