import sys
import csv
import re
import time
import socket

import requests
from bs4 import BeautifulSoup
from colorama import Fore
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Program started.")


# Prints the welcome message
def print_welcome():
    print(Fore.CYAN + """
 _______  _______  _______      _______  _______  ______    _______  _______  _______  ______   
|   _   ||       ||       |    |       ||       ||    _ |  |   _   ||       ||       ||    _ |  
|  |_|  ||   _   ||___    |    |  _____||       ||   | ||  |  |_|  ||    _  ||    ___||   | ||  
|       ||  | |  | ___|   |    | |_____ |       ||   |_||_ |       ||   |_| ||   |___ |   |_||_ 
|       ||  |_|  ||___    |    |_____  ||      _||    __  ||       ||    ___||    ___||    __  |
|   _   ||       | ___|   |     _____| ||     |_ |   |  | ||   _   ||   |    |   |___ |   |  | |
|__| |__||_______||_______|    |_______||_______||___|  |_||__| |__||___|    |_______||___|  |_|
""" + Fore.RESET)


# Prints the goodbye message and exits the program
def print_goodbye():
    print(Fore.CYAN + "\nThank you for using AO3 Bookmark Scraper!" + Fore.RESET)
    logger.info("Exiting the program.")
    input("\nPress Enter to exit.")


# Asks the user if they want to log in
def ask_if_log_in():
    while True:
        user_choice = input("\nWould you like to log in?\nLogged in users can access private bookmarks and bookmarks "
                            "that are only visible to logged in users.\n1. Yes\n2. No\n")

        if user_choice == "1":
            logger.info("User chose to log in.")
            return True
        elif user_choice == "2":
            logger.info("User chose not to log in.")
            return False
        else:
            handle_invalid_input("Please enter a valid choice. 1 or 2.")


# Creates a session and returns the authenticity token
def create_session():
    print("\nCreating a session...")

    try:
        # Create a session and make a GET request
        with requests.Session() as session:
            response = session.get("https://archiveofourown.org/users/login")
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        token = soup.find('input', {'name': 'authenticity_token'})

        if token is None:
            handle_token_not_found()
            return None, None
        else:
            token = token['value']
            print("\nSession created.")
            logger.info("Session created.")
            return token, session

    except requests.exceptions.RequestException as error:
        handle_request_error(error)
        return None, None


# Gets username/email and password from the user and logs in
def get_login_info(token, session):
    if session is None or token is None:
        handle_token_not_found()
        return False

    while True:
        # Prompt for user input
        username_or_email = input("\nEnter your username or email: ")
        password = input("\nEnter your password: ")
        print("\nChecking if login is successful...")

        # Create a payload
        payload = {
            "utf8": "✓",
            "authenticity_token": token,
            "user[login]": username_or_email,
            "user[password]": password,
            "commit": "Log in"
        }

        try:
            # Make a POST request
            response = session.post("https://archiveofourown.org/users/login", data=payload)
            response.raise_for_status()

        except requests.exceptions.RequestException as error:
            handle_request_error(error)
            continue

        # Check if login was successful
        if "Successfully logged in" in response.text:
            print(Fore.CYAN + "\nLogin successful." + Fore.RESET)
            logger.info("Login successful.")
            return True
        else:
            handle_invalid_input("Login failed. Please try again.")


# Gets the username of the user whose bookmarks are to be scraped
def get_username(logged_in):
    while True:
        username = input("\nEnter the username of the user whose bookmarks you want to scrape: ")
        if not username:
            handle_invalid_input("Please enter a username.")
            continue

        print("\nChecking if the username is valid...")

        # Check if the username follows guidelines (3-40 characters, alphanumeric and underscore)
        username_pattern = r"^[A-Za-z0-9_]{3,40}$"
        if not re.match(username_pattern, username):
            handle_invalid_input("Please enter a valid username.")
            continue
        logger.info(f"{username} is a valid username.")

        try:
            print("\nChecking if username exists...")
            response = requests.get(f"https://archiveofourown.org/users/{username}")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            if len(soup.find_all("div", class_="user")) > 0:
                print(f"\nScraping bookmarks of user: {Fore.CYAN}{username}{Fore.RESET}")
                url = f"https://archiveofourown.org/users/{username}/bookmarks"

                if logged_in:
                    url += "?private=true"
                logger.info(f"{username} exists. URL: {url}")
                return username, url
            else:
                handle_invalid_input(f"Username {username} does not exist. Please enter a valid username.")

        except requests.exceptions.RequestException as error:
            handle_request_error(error)
            continue


# Gets the number of pages of bookmarks available (with error handling)
def get_available_pages(username, session, url):
    while True:
        try:
            # Construct the URL based on the login status
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            bookmarks = soup.find_all("li", class_="bookmark")

            if len(bookmarks) == 0:
                handle_invalid_input(f"{username} has no bookmarks.")
                return None

            # Extract pagination information
            pagination = soup.find("ol", class_="actions")
            if pagination is not None:
                pagination = pagination.find_all("li")
                last_page = int(pagination[-2].text)
            else:
                handle_parse_error()
                return None  # Return None in case of pagination parse error

            print(f"\nThe user has {Fore.CYAN}{last_page}{Fore.RESET} pages of bookmarks available.")
            logger.info(f"{username} has {last_page} pages of bookmarks available.")
            return last_page

        except requests.exceptions.RequestException as error:
            handle_request_error(error)
            continue

        except (AttributeError, ValueError):
            handle_parse_error()
            return None


# Gets the page range from the user
def get_page_range(session, url):
    while True:
        try:
            start_page = int(input("\nEnter the starting page number: "))
            if start_page < 1:
                handle_invalid_input("The starting page number must be positive.")
                continue

            end_page = int(input("\nEnter the ending page number: "))
            if end_page < 1 or end_page < start_page:
                handle_invalid_input("The ending page number must be positive and greater than the starting page "
                                     "number.")
                continue

            # Check if the starting page exists
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            if response.status_code != 200:
                handle_invalid_input(f"Starting page {start_page} does not exist.")
                continue

            # Extract pagination information
            pagination = BeautifulSoup(response.text, 'html.parser').find("ol", class_="actions")
            if pagination is not None:
                pagination = pagination.find_all("li")
                last_page = int(pagination[-2].text)
                if start_page > last_page:
                    handle_invalid_input(f"Starting page {start_page} is out of range. Available starting pages are"
                                         f" those between 1 - {last_page}.")
                    continue
            else:
                handle_parse_error()
                continue

            # Check if the ending page exists
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            if response.status_code != 200:
                handle_invalid_input(f"Ending page {end_page} does not exist.")
                continue

            if end_page > last_page:
                handle_invalid_input(f"Ending page {end_page} is out of range. The last available page is {last_page}.")
                continue

            logger.info(f"Page range: {start_page} - {end_page}")
            return start_page, end_page

        except ValueError:
            handle_invalid_input("Please enter a valid number.")


# Gets the delay between requests
def get_delay():
    while True:
        try:
            print("\nEnter delay between requests (in seconds).")
            print("Consider longer delays if you are scraping a large number of pages.")
            delay = int(input("Should be at least 5: "))
            if delay < 5:
                handle_invalid_input("Please enter a delay of at least 5 seconds.")
                continue
            break

        except ValueError:
            handle_invalid_input("Please enter a valid number.")

    logger.info(f"Delay: {delay} seconds")
    return delay


# Gets the text of an element
def get_element_text(element):
    return element.text.strip() if element else ""


# Gets the text of a list of elements
def get_element_text_list(elements):
    return [element.text.strip() for element in elements] if elements else []


# Scrapes the bookmarks of a user, author is missing if the author is anonymous
def scrape_bookmarks(username, start_page, end_page, session, delay):
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
                handle_request_error(error)
                return

            if handle_retry_later(response):
                return

            # Loop through each bookmark on the page
            for bookmark in soup.select("li.bookmark"):
                title_element = bookmark.select_one("h4 a:nth-of-type(1)")
                if title_element:
                    title = get_element_text(title_element)
                else:
                    continue

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

                # Write bookmark data to CSV
                csvwriter.writerow([
                    url, title, '; '.join(authors), '; '.join(fandoms), '; '.join(warnings),
                    '; '.join(ratings), '; '.join(categories), '; '.join(characters),
                    '; '.join(relationships), '; '.join(tags), words, date_bookmarked, date_updated
                ])

                num_bookmarks += 1
                logger.info(f"Bookmark {num_bookmarks}: {title} written to CSV file")  # delete if everything works

        # Print completion message
        logger.info(f"Scrapping complete. Scraped {num_bookmarks} bookmarks.")
        print("\nAll done! \nYour bookmarks have been saved to {}{}{}_bookmarks.csv{}.".format(Fore.CYAN,
                                                                                               username, Fore.RESET,
                                                                                               Fore.RESET))
        print("Scraped {}{}{} bookmarks.".format(Fore.CYAN, num_bookmarks, Fore.RESET))


# Asks if the user wants to log in
def ask_again():
    while True:
        answer = input("\nWould you like to try again? \n1. Yes \n2. No\n")
        if answer == "1":
            logger.info("User chose to try again.")
            return True
        elif answer == "2":
            logger.info("User chose not to try again.")
            return False
        else:
            handle_invalid_input("Please enter a valid choice. 1 or 2.")


# Handles the "Retry later" message
def handle_retry_later(response):
    if "Retry later" in response.text:
        logger.error("Received 'Retry later' message. Too many requests, stopping scraping.")
        print("\nReceived 'Retry later' message. Please try again later, consider increasing the delay.")
        return True
    return False


# Handles invalid input
def handle_invalid_input(context):
    logger.error(f"Invalid input: {context}")
    print(f"\nInvalid input: {context}")


# Handles request errors
def handle_request_error(error):
    logger.error(f"An error occurred while making the request: {error}")
    print("\nAn error occurred while making the request. Please try again later. Check the logs for more details.")


# Handles token not found error
def handle_token_not_found():
    logger.error("Authenticity token not found. Cannot log in.")
    print("\nAn error occurred while logging in. Please try again later.Check the logs for more details.")


# Handles parse errors
def handle_parse_error():
    logger.error("Error parsing HTML.")
    print("\nAn error occurred while parsing the HTML. Please try again later. Check the logs for more details.")


# Handles keyboard interrupts
def handle_keyboard_interrupt():
    logger.error("Keyboard Interrupt detected.")
    print("\nKeyboardInterrupt received. Exiting gracefully...")
    sys.exit(0)


# Main function
def main():
    try:
        print_welcome()
        # Ask if the user wants to log in (for now here)
        log_in = ask_if_log_in()
        while True:
            # Initialize variables (important for when the user doesn't log in)
            token, session = None, None

            if log_in:
                # If the user wants to log in, create a session and get the login info, set logged_in to True
                token, session = create_session()
                get_login_info(token, session)
                logged_in = True
            else:
                # If the user doesn't want to log in, set logged_in to False
                logged_in = False

            # Get the info needed to scrape the bookmarks
            username, url = get_username(logged_in)
            if get_available_pages(username, session, url):
                start_page, end_page = get_page_range(session, url)
                delay = get_delay()

                # Scrape the bookmarks
                scrape_bookmarks(username, start_page, end_page, session, delay)

                if not ask_again():
                    # If the user doesn't want to try again, print goodbye message and exit the loop
                    print_goodbye()
                    break

    except KeyboardInterrupt:
        handle_keyboard_interrupt()


if __name__ == "__main__":
    main()
