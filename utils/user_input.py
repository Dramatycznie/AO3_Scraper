import re
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from . import error_handling


# Asks the user if they want to log in
def ask_if_log_in(logger):
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
            error_handling.handle_invalid_input("Please enter a valid choice. 1 or 2.", logger)


# Asks if the user wants to log in
def ask_again(logger):
    while True:
        answer = input("\nWould you like to run the program again? \n1. Yes \n2. No\n")
        if answer == "1":
            logger.info("User chose to try again.")
            return True
        elif answer == "2":
            logger.info("User chose not to try again.")
            return False
        else:
            error_handling.handle_invalid_input("Please enter a valid choice. 1 or 2.", logger)


# Gets username/email and password from the user and logs in
def get_login_info(token, session, logger):
    if session is None or token is None:
        error_handling.handle_token_not_found(logger)
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
            error_handling.handle_request_error(error, logger)
            continue

        # Check if login was successful
        if "Successfully logged in" in response.text:
            print(Fore.CYAN + "\nLogin successful." + Fore.RESET)
            logger.info("Login successful.")
            return True
        else:
            error_handling.handle_invalid_input("Login failed. Please try again.", logger)


# Gets the username of the user whose bookmarks are to be scraped
def get_username(logged_in, action, logger):
    while True:
        username = input(f"\nEnter the username of the user whose bookmarks you want to {action}: ")
        if not username:
            error_handling.handle_invalid_input("Please enter a username.", logger)
            continue

        print("\nChecking if the username is valid...")

        # Check if the username follows guidelines (3-40 characters, alphanumeric and underscore)
        username_pattern = r"^[A-Za-z0-9_]{3,40}$"
        if not re.match(username_pattern, username):
            error_handling.handle_invalid_input("Please enter a valid username.", logger)
            continue
        logger.info(f"{username} is a valid username.")

        try:
            print("\nChecking if username exists...")
            response = requests.get(f"https://archiveofourown.org/users/{username}")
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            if len(soup.find_all("div", class_="user")) > 0:
                if action == "scrape":
                    print(f"\nScraping bookmarks of user: {Fore.CYAN}{username}{Fore.RESET}")
                elif action == "download":
                    print(f"\nDownloading bookmarks of user: {Fore.CYAN}{username}{Fore.RESET}")
                url = f"https://archiveofourown.org/users/{username}/bookmarks"

                if logged_in:
                    url += "?private=true"
                logger.info(f"{username} exists. URL: {url}")
                return username, url
            else:
                error_handling.handle_invalid_input(f"Username {username} does not exist. Please enter a valid "
                                                    f"username.", logger)

        except requests.exceptions.RequestException as error:
            error_handling.handle_request_error(error, logger)


# Gets the number of pages of bookmarks available (with error handling)
def get_available_pages(username, session, url, logger):
    try:
        # Construct the URL based on the login status
        response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        bookmarks = soup.find_all("li", class_="bookmark")

        if len(bookmarks) == 0:
            error_handling.handle_invalid_input(f"{username} has no bookmarks.", logger)
            return None

        # Extract pagination information
        pagination = soup.find("ol", class_="actions")
        if pagination is not None:
            pagination = pagination.find_all("li")
            last_page = int(pagination[-2].text)
        else:
            error_handling.handle_parse_error(logger)
            return None  # Return None in case of pagination parse error

        print(f"\nThe user has {Fore.CYAN}{last_page}{Fore.RESET} pages of bookmarks available.")
        logger.info(f"{username} has {last_page} pages of bookmarks available.")
        return last_page

    except requests.exceptions.RequestException as error:  # works ok if not logged in (check for logged in)
        error_handling.handle_request_error(error, logger)
        return None  # Return None to indicate an error

    except (AttributeError, ValueError):
        error_handling.handle_parse_error(logger)
        return None


# Gets the page range from the user
def get_page_range(session, url, logger):
    while True:
        try:
            start_page = int(input("\nEnter the starting page number: "))
            if start_page < 1:
                error_handling.handle_invalid_input("The starting page number must be positive.", logger)
                continue

            end_page = int(input("\nEnter the ending page number: "))
            if end_page < 1 or end_page < start_page:
                error_handling.handle_invalid_input("The ending page number must be positive and greater than the "
                                                    "starting page number.", logger)
                continue

            # Check if the starting page exists
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            if response.status_code != 200:
                error_handling.handle_invalid_input(f"Starting page {start_page} does not exist.", logger)
                continue

            # Extract pagination information
            pagination = BeautifulSoup(response.text, 'html.parser').find("ol", class_="actions")
            if pagination is not None:
                pagination = pagination.find_all("li")
                last_page = int(pagination[-2].text)
                if start_page > last_page:
                    error_handling.handle_invalid_input(f"Starting page {start_page} is out of range. Available "
                                                        f"starting pages are those between 1 - {last_page}.", logger)
                    continue
            else:
                error_handling.handle_parse_error(logger)
                continue

            # Check if the ending page exists
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            if response.status_code != 200:
                error_handling.handle_invalid_input(f"Ending page {end_page} does not exist.", logger)
                continue

            if end_page > last_page:
                error_handling.handle_invalid_input(f"Ending page {end_page} is out of range. The last available "
                                                    f"page is {last_page}.", logger)
                continue

            logger.info(f"Page range: {start_page} - {end_page}")
            return start_page, end_page

        except ValueError:
            error_handling.handle_invalid_input("Please enter a valid number.", logger)


# Gets the delay between requests
def get_delay(logger):
    while True:
        try:
            delay = int(input("\nEnter the interval delay between requests (at least 1 second, suggested value "
                              "is 5 seconds): "))
            if delay < 1:
                error_handling.handle_invalid_input("Please enter a delay of at least 1 second.", logger)
                continue
            break

        except ValueError:
            error_handling.handle_invalid_input("Please enter a valid number.", logger)

    logger.info(f"Delay: {delay} seconds")
    return delay


# Gets the input for the download or scrape choice
def download_or_scrape(logger):
    while True:
        choice = input("\nDo you want to scrape the bookmarks or download them?\n1. Scrape\n2. Download\n"
                       "3. Download updates (for now EPUB only)\n")
        choices = ['1', '2', '3']
        if choice in choices:
            action = ["scrape", "download", "download updates"][int(choice) - 1]
            logger.info(f"User chose to {action} bookmarks.")
            return action
        else:
            error_handling.handle_invalid_input("Invalid choice. Please enter a valid number.", logger)


# Gets the input for the download format
def get_download_format(logger, action):
    while True:
        if action == "download updates":
            user_format = input("\nChoose the download format:\n1. EPUB\n2. PDF\n3. HTML\n")
            formats = ['1', '2', '3']
        else:
            user_format = input("\nChoose the download format:\n1. AZW3\n2. EPUB\n3. MOBI\n4. PDF\n5. HTML\n")
            formats = ['1', '2', '3', '4', '5']

        if user_format in formats:
            if action == "download updates":
                chosen_format = ["EPUB", "PDF", "HTML"][int(user_format) - 1]
            else:
                chosen_format = ["AZW3", "EPUB", "MOBI", "PDF", "HTML"][int(user_format) - 1]

            logger.info(f"User chose to download in {chosen_format} format.")
            return chosen_format
        else:
            error_handling.handle_invalid_input("Invalid choice. Please enter a valid number.", logger)
