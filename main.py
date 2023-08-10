import csv
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from colorama import Fore
from requests.exceptions import RequestException
from tqdm import tqdm

# Set global variables
token = None
session = None
ask_username = True
username_or_email = None

# Starting message
print(Fore.CYAN + "")
print("Hello and welcome to AO3 Bookmark Scraper")
print("")
print("You can scrape public bookmarks of any user")
print("Or scrape your private bookmarks if you log in")
print("Please note that some works may only be visible to logged-in users")
print("Happy scraping!" + Fore.RESET)

while True:
    while True:
        # Ask the user if they want to log in
        while True:
            print("")
            login = input("Do you want to log in? Logged in users can scrape their private bookmarks (1-2) \n 1. yes "
                          "\n 2. no \n")
            # Check if the input is valid
            if login in ["1"]:
                # Create a session to log in
                session = requests.Session()
                try:
                    # Make a GET request to the login page
                    r = session.get("https://archiveofourown.org/users/login")

                    # Parse the HTML content of the page
                    soup = BeautifulSoup(r.content, 'html.parser')

                    # Find the authenticity token in the page source code
                    token = soup.find('input', {'name': 'authenticity_token'})
                    if token is None:
                        # If the authenticity token is not found, print an error message
                        print("")
                        print("Authenticity token not found. Please check the page source code.")
                    else:
                        # If the authenticity token is found, get the value of the token
                        token = token['value']

                except requests.exceptions.RequestException as e:
                    # Handle exceptions that may occur during the GET request
                    print("")
                    print(f"An error occurred while making the GET request: {e}")

                # Get the user's username or email and password
                print("")
                username_or_email = input("Enter your username or email: ")
                print("")
                password = input("Enter your password: ")

                print("")
                print("Checking if credentials are valid...")
                # Check if the credentials are valid
                if session is not None and token is not None:
                    # Creates payload to login to ao3
                    payload = {"utf8": "✓",
                               "authenticity_token": token,
                               "user[password]": password,
                               "commit": "Log in"}
                    # Check if the input is an email
                    if '@' in username_or_email:
                        payload["user[login]"] = username_or_email
                        ask_username = True
                        # If the input is an email, set the value of the payload key "user[login]" to the email
                    else:
                        payload["user[login]"] = username_or_email
                        ask_username = False
                        # If the input is not an email, set the value of the payload key "user[login]" to the username
                else:
                    # If the session or token is None, print an error message
                    payload = {}
                try:
                    # POST request to ao3 to login
                    p = session.post("https://archiveofourown.org/users/login", data=payload)
                except requests.exceptions.RequestException as e:
                    # Handle exceptions that may occur during the POST request
                    print("")
                    print(f"An error occurred while making the POST request: {e}")
                    continue
                    # If the POST request fails, ask the user to enter the credentials again

                # Check if the response indicates a successful login
                if "Successfully logged in" in p.text:
                    # Login successful
                    print("")
                    print(Fore.CYAN + "Login successful" + Fore.RESET)
                    break
                    # If the login is successful, break out of the loop
                else:
                    # Login failed
                    print("")
                    print(Fore.CYAN + "Login failed" + Fore.RESET)
                continue
                # If the login is not successful, ask the user to enter the credentials again

            elif login in ["2"]:
                print("")
                print("All right! You can still scrape public bookmarks of any user")
                break
                # If the user does not want to log in, break out of the loop
            else:
                print("")
                print("Invalid input: Please enter 1 or 2")
                # If the input is invalid, restart the loop

        while True:
            # Get the user's AO3 username
            if login in ["1"]:
                if ask_username is True:
                    print("")
                    username = input("You provided an email address. Now enter your username: ")
                    # If the user provided an email address, ask the user to enter their username
                else:
                    username = username_or_email
                    print("")
                    print("Scraping bookmarks of user: " + Fore.CYAN + username + Fore.RESET)
                    # If the user provided a username, scrape the bookmarks of that user
            else:
                # If the user does not want to log in, ask the user to enter the username of the user whose bookmarks
                # they want to scrape
                print("")
                username = input("Enter the username of the user whose bookmarks you want to scrape: ")

            # Check if the input is valid
            pattern = r"^[\w\d._-]+$"
            if re.match(pattern, username):
                # The input is valid
                print("")
                print("Checking if the user has bookmarks...")
            else:
                # The input is invalid
                print("")
                print("Invalid input: Please enter a valid username")
                continue
                # If the input is invalid, restart the loop

            # Check if the username exists
            try:
                response = requests.get(f"https://archiveofourown.org/users/{username}")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                if len(soup.find_all("div", class_="user")) > 0:
                    # If the username exists, break out of the loop
                    break
                else:
                    # If the username does not exist, print an error message
                    print("")
                    print(f"Username {username} does not exist, please enter a valid username")

            # Handle exceptions that may occur during the GET request
            except RequestException as e:
                print("")
                print("Error connecting to the server. Please check your internet connection and try again")

        # Create base URL for the user's AO3 bookmarks
        base_url = "https://archiveofourown.org/users/" + username + "/bookmarks?page="

        # Initialize page2 to a default value
        page2 = None

        # Get the number of pages of bookmarks available
        while True:
            try:
                if login in ["1"]:
                    # If the user logged in, make a GET request to the user's bookmarks page private=true
                    response = session.get(f"https://archiveofourown.org/users/{username}/bookmarks?private=true")
                else:
                    # If the user did not log in, make a GET request to the user's bookmarks page
                    response = requests.get(f"https://archiveofourown.org/users/{username}/bookmarks")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                bookmarks = soup.find_all("li", class_="bookmark")
                if len(bookmarks) == 0:
                    print("")
                    print("User " + Fore.CYAN + "{username}" + Fore.RESET + " has no bookmarks")
                    # Close the program after enter is pressed
                    print("")
                    print("Please run the program again and enter an username that has bookmarks")
                    input("Press enter to exit")
                    sys.exit()

                pagination = soup.find("ol", class_="actions")
                if pagination is not None:
                    pagination = pagination.find_all("li")
                    last_page = int(pagination[-2].text)
                else:
                    last_page = 1

                print("")
                print(f"The user has {Fore.CYAN}{last_page}{Fore.RESET} pages of bookmarks available")
                break
            except requests.exceptions.HTTPError as e:
                print("")
                print(f"Error connecting to the server: {e}")
            except (AttributeError, ValueError):
                print("")
                print("Error parsing the HTML: pagination element not found")
                break

        while True:
            try:
                # Get the starting page number to scrape from
                print("")
                page1 = int(input("Start scraping from page: "))
                if page1 < 1:
                    print("")
                    print("Invalid input: Please enter a valid number")
                    continue
                print("")
                print("Checking if the page exists...")
                # check if page1 is out of range
                try:
                    if login in ["yes", "y"]:
                        response = session.get(
                            f"https://archiveofourown.org/users/{username}/bookmarks?private=true" + str(page1))
                    else:
                        response = requests.get(
                            f"https://archiveofourown.org/users/{username}/bookmarks?page=" + str(page1))
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    bookmarks = soup.find_all("li", class_="bookmark")
                    if len(bookmarks) == 0:
                        print("")
                        print("Start page is out of range")
                        continue
                except ValueError:
                    print("")
                    print("Invalid input: Please enter a valid number")
                    continue
                except RequestException as e:
                    print("")
                    print("Error connecting to the server. Please check your internet connection and try again")
                    continue
                while True:
                    try:
                        # Get the ending page number to scrape to
                        print("")
                        page2 = int(input("Stop scraping at page: "))
                        print("")
                        print("Checking if the page exists...")
                        if page2 < 1:
                            print("")
                            print("Invalid input: Please enter a valid number")
                            continue
                        if page1 > page2:
                            print("")
                            print("Invalid input: End page should be bigger or equal to start page")
                            continue
                        try:
                            if login in ["yes", "y"]:
                                response = session.get(
                                    f"https://archiveofourown.org/users/{username}/bookmarks?private=true" + str(page2))
                            else:
                                response = requests.get(
                                    f"https://archiveofourown.org/users/{username}/bookmarks?page=" + str(page2))
                            response.raise_for_status()
                            soup = BeautifulSoup(response.text, 'html.parser')
                            bookmarks = soup.find_all("li", class_="bookmark")
                            if len(bookmarks) == 0:
                                print("")
                                print("End page is out of range")
                                continue
                        except ValueError:
                            print("")
                            print("Invalid input: Please enter a valid number")
                        except RequestException as e:
                            print("")
                            print("Error connecting to the server. Please check your internet connection and try "
                                  "again")
                            continue
                        break
                    except ValueError:
                        print("")
                        print("Invalid input: Please enter a valid number")
                break
            # Handle any errors that may occur
            except ValueError:
                print("")
                print("Invalid input: Please enter a valid number")

        while True:
            try:
                # Prompt for delay
                print("")
                print("Enter delay between requests (in seconds).")
                print("Consider longer delays if you are scraping a large number of pages.")
                delay = int(input("Should be at least 5: "))
                print("")
                # Check if the input is valid
                if delay < 5:
                    print("")
                    print("Invalid input: Please enter a valid number")
                    continue
                break
            # Handle any errors that may occur
            except ValueError:
                print("")
                print("Invalid input: Please enter a valid number")

        # Open a CSV file for writing
        with open(username + '_bookmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
            # Create a CSV writer object
            csvwriter = csv.writer(csvfile)
            # Write the header row
            csvwriter.writerow(
                ['URL', 'Title', 'Authors', 'Fandoms', 'Warnings', 'Rating', 'Categories', 'Characters',
                 'Relationships',
                 'Tags', 'Words', 'Date Bookmarked', 'Date Updated'])

            # Calculate the total number of pages to scrape
            total_pages = page2 - page1 + 1

            # Use tqdm to create a progress bar with the total number of pages to scrape
            for page in tqdm(range(page1, page2 + 1), total=total_pages, desc="Scraping"):
                start_time = time.time()
                try:
                    if login in ["yes", "y"]:
                        # Send a GET request to the current page
                        response = session.get(
                            f"https://archiveofourown.org/users/{username}/bookmarks?private=true&page={page}")
                    else:
                        response = requests.get(f"https://archiveofourown.org/users/{username}/bookmarks?page={page}")
                    # Add delay between requests to be respectful to the website
                    time.sleep(delay)
                    # Parse the HTML of the page using BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                except requests.exceptions.RequestException as e:
                    print("")
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
                        date_bookmarked = bookmark.select_one("div.user p.datetime")
                        url = bookmark.select_one("h4 a:nth-of-type(1)")["href"]
                        date_updated = bookmark.select_one("p.datetime")

                        # Check if the bookmark has authors
                        authors.element = bookmark.select("a[rel='author']")
                        if authors.element:
                            authors = [author.text for author in authors]
                            if authors:
                                authors = ' ' + authors[0] + '; ' + '; '.join(authors[1:])
                        else:
                            authors = ""

                        # Check if the bookmark has fandoms
                        fandoms.element = bookmark.select(".fandoms a")
                        if fandoms.element:
                            fandoms = [fandom.text for fandom in fandoms]
                            if fandoms:
                                fandoms = ' ' + fandoms[0] + '; ' + '; '.join(fandoms[1:])
                        else:
                            fandoms = ""

                        # Check if the bookmark has warnings
                        warnings_element = bookmark.select("span.warnings")
                        if warnings_element:
                            warnings = [warning.text for warning in warnings_element]
                            if warnings:
                                warnings = ' ' + warnings[0] + '; ' + '; '.join(warnings[1:])
                        else:
                            warnings = ""

                        # Check if the bookmark has a rating
                        rating.element = bookmark.select("span.rating")
                        if rating.element:
                            rating = [rating.text for rating in rating.element]
                            if rating:
                                rating = ' ' + rating[0] + '; ' + '; '.join(rating[1:])
                        else:
                            rating = ""

                        # Check if the bookmark has categories
                        categories.element = bookmark.select("span.category")
                        if categories.element:
                            categories = [category.text for category in categories.element]
                            if categories:
                                categories = ' ' + categories[0] + '; ' + '; '.join(categories[1:])
                        else:
                            categories = ""

                        tags_element = bookmark.select("li.freeforms")
                        if tags_element:
                            tags = [tag.text for tag in tags_element]
                            if tags:
                                tags = ' ' + tags[0] + '; ' + '; '.join(tags[1:])
                        else:
                            tags = ""

                        # Check if the bookmark has characters
                        characters_element = bookmark.select("li.characters")
                        if characters_element:
                            characters = [character.text for character in characters_element]
                            if characters:
                                characters = ' ' + characters[0] + '; ' + '; '.join(characters[1:])
                        else:
                            characters = ""

                        # Check if the bookmark has relationships
                        relationships_element = bookmark.select("li.relationships")
                        if relationships_element:
                            relationships = [relationship.text for relationship in relationships_element]
                            if relationships:
                                relationships = ' ' + relationships[0] + '; ' + '; '.join(relationships[1:])
                        else:
                            relationships = ""

                        # Check if the bookmark has a date
                        date_bookmarked = date_bookmarked.text if date_bookmarked else ""

                        # Check if the bookmark has a word count
                        words = words.text if words else ""

                        # Check if the bookmark has a URL
                        url = "https://archiveofourown.org" + url if url else ""

                        # Check if the bookmark has a date updated
                        date_updated = date_updated.text if date_updated else ""

                        # Write the data to the CSV file
                        csvwriter.writerow([url, title, authors, fandoms, warnings, rating, categories,
                                            characters, relationships, tags, words, date_bookmarked, date_updated])
                from requests.exceptions import RequestException

                try:
                    if login in ["yes", "y"]:
                        # Send a GET request to the current page
                        response = session.get(
                            f"https://archiveofourown.org/users/{username}/bookmarks?private=true" + str(page),
                            timeout=60)
                    else:
                        response = requests.get(f"https://archiveofourown.org/users/{username}/bookmarks" + str(page),
                                                timeout=60)
                except RequestException as e:
                    print("")
                    print(f"Error loading page {page}. {e}")
                    print("Please try again later.")
                    print("If the problem persists, consider longer delay times between requests.")
                    break

        num_bookmarks = sum(1 for line in open(username + '_bookmarks.csv', encoding='utf-8')) - 1

        # Message at the end of the program
        print("")
        print("All done!")
        print("Your bookmarks have been saved to {}{}{}_bookmarks.csv{}".format(Fore.CYAN, username, Fore.RESET,
                                                                                Fore.RESET))
        print("Scraped {}{}{} bookmarks.".format(Fore.CYAN, num_bookmarks, Fore.RESET))

        while True:
            # Ask the user if they want to start scraping again
            print("")
            choice = input("Do you want to start scraping again? (1-2) \n 1. yes \n 2. no \n").lower()

            # If the user enters "1"
            if choice in ["1"]:
                # Restart the program
                break

            # If the user enters "2"
            elif choice in ["2"]:
                # Close the program
                print("")
                print("Thank you for using the AO3 Bookmark Scraper!")
                print("Press", Fore.CYAN + "Enter" + Fore.RESET, "to exit...", end='')
                input()
                sys.exit()

            # If the user enters something other than that
            else:
                # Ask the user to enter valid input
                print("")
                print("Invalid input. Please enter 1 or 2")
