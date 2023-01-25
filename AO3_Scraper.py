import requests
from bs4 import BeautifulSoup
import time
import csv
from tqdm import tqdm

# Starting message
print("")
print("Hello and welcome to AO3 Bookmark Scraper")
print("")

while True:
    # Get the user's AO3 username
    username = input("Your username: ")
    # Check if the input is valid
    if not username.isalnum() or not len(username):
        print("Invalid input: Please enter a valid username")
        continue
    # Send a GET request to the user's profile page
    response = requests.get(f"https://archiveofourown.org/users/{username}")
    soup = BeautifulSoup(response.text, 'html.parser')
    # check if the response contain a specific element
    if soup.find("div", class_="user"):
        print("Checking...")
        print(f"Username {username} is valid.")
        break
    else:
        print(f"Username {username} does not exist. Please enter a valid username")
        continue

# Create base URL for the user's AO3 bookmarks
base_url = "https://archiveofourown.org/users/" + username + "/bookmarks?page="

# Initialize page2 to a default value
page2 = None

while True:
    try:
        # Get the starting page number to scrape from
        page1 = int(input("Start scraping from page: "))
        # Send a GET request to the first page
        response = requests.get(base_url + str(page1))
        soup = BeautifulSoup(response.text, 'html.parser')
        bookmarks = soup.find_all("li", class_="bookmark")
        if len(bookmarks) == 0:
            print("Error: Start page is out of range.")
            continue
        # Get the ending page number to scrape to
        page2 = int(input("Stop scraping at page: "))
        if page1 >= page2:
            print("Invalid input: End page should be bigger than start page")
            continue
        # Send a GET request to the last page
        # Move this to avoid asking for the start page if the end page is invalid
        response = requests.get(base_url + str(page2))
        soup = BeautifulSoup(response.text, 'html.parser')
        bookmarks = soup.find_all("li", class_="bookmark")
        if len(bookmarks) == 0:
            print("Error: End page is out of range.")
            continue
        break
    # Handle any errors that may occur
    except ValueError:
        print("Invalid input: Please enter a valid number")

while True:
    try:
        # Prompt for delay
        delay = int(input("Pick request interval (in seconds). 5 or more "))
        # Check if the input is valid
        if delay < 5:
            print("Invalid input: Please enter a valid number")
            continue
        break
    # Handle any errors that may occur
    except ValueError:
        print("Invalid input: Please enter a valid number")

# Print loading page message
print("Loading... Please wait")

# Open a CSV file for writing
with open(username + '_bookmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer object
    csvwriter = csv.writer(csvfile)
    # Write the header row
    csvwriter.writerow(
        ['URL', 'Title', 'Authors', 'Fandoms', 'Warnings', 'Rating', 'Categories', 'Characters', 'Relationships',
         'Tags', 'Words', 'Date Bookmarked'])

    # Calculate the total number of pages to scrape
    total_pages = page2 - page1 + 1

    # Use tqdm to create a progress bar with the total number of pages to scrape
    for page in tqdm(range(page1, page2 + 1), total=total_pages, desc="Scraping"):
        start_time = time.time()
        try:
            # Send a GET request to the current page
            response = requests.get(base_url + str(page))
            # Add delay between requests to be respectful to the website
            time.sleep(delay)
            # Parse the HTML of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            break
        end_time = time.time()

    # Extract the data using the provided selectors
        for bookmark in soup.select("li.bookmark"):
            title_element = bookmark.select_one("h4 a:nth-of-type(1)")
            if title_element:
                title = title_element.text
            # Skip the bookmark if it doesn't have a title
            else:
                continue

            if title:
                # Extract the data using the provided selectors
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
                url = bookmark.select_one("h4 a:nth-of-type(1)")["href"]

                # Check if the bookmark has authors
                authors.element = bookmark.select("a[rel='author']")
                if authors.element:
                    authors = [author.text for author in authors]
                    if authors:
                        authors = ', '.join(authors)
                else:
                    authors = ""

                # Check if the bookmark has fandoms
                fandoms.element = bookmark.select(".fandoms a")
                if fandoms.element:
                    fandoms = [fandom.text for fandom in fandoms]
                    if fandoms:
                        fandoms = ', '.join(fandoms)

                # Check if the bookmark has warnings
                warnings_element = bookmark.select("span.warnings")
                if warnings_element:
                    warnings = [warning.text for warning in warnings_element]
                    if warnings:
                        warnings = ', '.join(warnings)
                else:
                    warnings = ""

                # Check if the bookmark has a rating
                rating.element = bookmark.select("span.rating")
                if rating.element:
                    rating = [rating.text for rating in rating.element]
                    if rating:
                        rating = ', '.join(rating)

                # Check if the bookmark has categories
                categories.element = bookmark.select("span.category")
                if categories.element:
                    categories = [category.text for category in categories.element]
                    if categories:
                        categories = ', '.join(categories)

                # Check if the bookmark has tags
                tags_element = bookmark.select("li.freeforms")
                if tags_element:
                    tags = [tag.text for tag in tags_element]
                    if tags:
                        tags = ', '.join(tags)
                else:
                    tags = ""

                # Check if the bookmark has characters
                characters_element = bookmark.select("li.characters")
                if characters_element:
                    characters = [character.text for character in characters_element]
                    if characters:
                        characters = ', '.join(characters)
                else:
                    characters = ""

                # Check if the bookmark has relationships
                relationships_element = bookmark.select("li.relationships")
                if relationships_element:
                    relationships = [relationship.text for relationship in relationships_element]
                    if relationships:
                        relationships = ', '.join(relationships)
                else:
                    relationships = ""

                # Check if the bookmark has a date
                dates = dates.text if dates else ""

                # Check if the bookmark has a word count
                words = words.text if words else ""

                # Check if the bookmark has a URL
                url = "https://archiveofourown.org" + url if url else ""

                # Write the data to the CSV file
                csvwriter.writerow([url, title, authors, fandoms, warnings, rating, categories,
                                    characters, relationships, tags, words, dates])

# Message at the end of the program
print("All done!")
print("Your bookmarks have been saved to " + username + "_bookmarks.csv")
