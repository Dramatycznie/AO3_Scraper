import csv
import re
import time

import requests
from bs4 import BeautifulSoup
from colorama import Fore
from tqdm import tqdm


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
    input("\nPress Enter to exit.")


# Asks the user if they want to log in
def ask_if_log_in():
    while True:
        user_choice = input("\nWould you like to log in?\nLogged in users can access private bookmarks and bookmarks "
                            "that are only visible to logged in users.\n1. Yes\n2. No\n")

        if user_choice == "1":
            return True
        elif user_choice == "2":
            return False
        else:
            print("\nInvalid input. Please enter 1 or 2.")


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
            print("\nAuthenticity token not found. Cannot log in.")
            return None, None
        else:
            token = token['value']
            print("\nSession created.")
            return token, session

    except requests.exceptions.RequestException as e:
        # Handle errors
        print(f"\nAn error occurred while making the GET request: {e}")
        return None, None


def get_login_info(token, session):
    if session is None or token is None:
        print("\nSession or token is None. Cannot log in.")
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
        except requests.exceptions.RequestException as e:
            # Handle request errors
            print(f"\nAn error occurred while making the POST request: {e}")
            continue

        # Check if login was successful
        if "Successfully logged in" in response.text:
            print(Fore.CYAN + "\nLogin successful." + Fore.RESET)
            return True
        else:
            print(Fore.CYAN + "\nLogin failed." + Fore.RESET)
            print("\nPlease try again.")


# Gets the username of the user whose bookmarks are to be scraped
def get_username(logged_in):
    while True:
        username = input("\nEnter the username of the user whose bookmarks you want to scrape: ")
        if not username:
            print("\nPlease enter a username.")
            continue

        print("\nChecking if the username is valid...")

        # Check if the username follows guidelines (3-40 characters, alphanumeric and underscore)
        username_pattern = r"^[A-Za-z0-9_]{3,40}$"
        if not re.match(username_pattern, username):
            print("\nInvalid input: Please enter a valid username.")
            continue

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
                return username, url
            else:
                print(f"\nUsername {username} does not exist or the user has no bookmarks to be scraped. "
                      f"Please enter a valid username.")

        except requests.exceptions.RequestException as e:
            # Handle request errors
            print(f"\nAn error occurred while making the GET request: {e} \nPlease try again.")


# Gets the number of pages of bookmarks available
def get_available_pages(username, session, url):
    while True:
        try:
            # Construct the URL based on the login status
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            bookmarks = soup.find_all("li", class_="bookmark")

            if len(bookmarks) == 0:
                print(f"\nUser {Fore.CYAN}{username}{Fore.RESET} has no bookmarks.\n")
                return None

            # Extract pagination information
            pagination = soup.find("ol", class_="actions")
            if pagination is not None:
                pagination = pagination.find_all("li")
                last_page = int(pagination[-2].text)
            else:
                last_page = 1

            print(f"\nThe user has {Fore.CYAN}{last_page}{Fore.RESET} pages of bookmarks available.")
            break

        except requests.exceptions.RequestException as e:
            # Handle request errors
            print("Error connecting to the server:", e)
            break

        except (AttributeError, ValueError):
            # Handle parsing errors
            print("Error parsing the HTML: pagination element not found.")
            break


# Gets the starting and ending page numbers from the user
def get_page_range(session, url):
    while True:
        try:
            start_page = int(input("\nEnter the starting page number: "))
            end_page = int(input("\nEnter the ending page number: "))

            if start_page < 1 or end_page < 1 or end_page < start_page:
                print(
                    "\nInvalid page numbers. Please enter positive integers with the ending page greater than or "
                    "equal to the starting page.")
                continue

            # Check if the starting page exists
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            if response.status_code != 200:
                print(f"\nStarting page {start_page} does not exist.")
                continue

            # Extract pagination information
            pagination = BeautifulSoup(response.text, 'html.parser').find("ol", class_="actions")
            if pagination is not None:
                pagination = pagination.find_all("li")
                last_page = int(pagination[-2].text)
                if start_page > last_page:
                    print(
                        f"\nStarting page {start_page} is out of range. Available starting pages are "
                        f"those between 1 - {last_page}.")
                    continue
            else:
                print("\nPagination information not found. Cannot determine last page.")
                continue

            # Check if the ending page exists
            response = session.get(url, timeout=60) if session else requests.get(url, timeout=60)
            response.raise_for_status()

            if response.status_code != 200:
                print(f"\nEnding page {end_page} does not exist.")
                continue

            if end_page > last_page:
                print(f"\nEnding page {end_page} is out of range. The last available page is {last_page}.")
                continue

            return start_page, end_page

        except ValueError:
            print("\nInvalid input, please enter valid page numbers.")


# Gets the delay between requests
def get_delay():
    while True:
        try:
            print("\nEnter delay between requests (in seconds).")
            print("Consider longer delays if you are scraping a large number of pages.")
            delay = int(input("Should be at least 5: "))
            if delay < 5:
                print("\nInvalid input: Please enter a valid number.")
                continue
            break
        except ValueError:
            print("\nInvalid input: Please enter a valid number.")
    return delay


# Gets the text of an element
def get_element_text(element):
    return element.text.strip() if element else ""


# Gets the text of a list of elements
def get_element_text_list(elements):
    return [element.text.strip() for element in elements] if elements else []


# Scrapes the bookmarks of a user
def scrape_bookmarks(username, start_page, end_page, session, delay, base_url):
    with open(username + '_bookmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write header row to CSV file
        csvwriter.writerow(
            ['URL', 'Title', 'Authors', 'Fandoms', 'Warnings', 'Rating', 'Categories', 'Characters',
             'Relationships', 'Tags', 'Words', 'Date Bookmarked', 'Date Updated'])

        num_bookmarks = 0
        total_pages = end_page - start_page + 1

        # Loop through pages and scrape bookmarks
        for page in tqdm(range(start_page, end_page + 1), total=total_pages, desc="Scraping"):
            try:
                # Construct page URL
                page_url = f"{base_url}?page={page}"
                response = session.get(page_url) if session else requests.get(page_url)
                time.sleep(delay)
                soup = BeautifulSoup(response.text, 'html.parser')
            except requests.exceptions.RequestException as e:
                tqdm.write("Error: " + str(e))  # Use tqdm.write to ensure clean line break
                break

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
                rating = get_element_text(bookmark.select_one("span.rating"))
                categories = get_element_text_list(bookmark.select("span.category"))
                words = get_element_text(bookmark.select_one("dd.words") or bookmark.select_one("dd"))
                tags = get_element_text_list(bookmark.select("li.freeforms"))
                characters = get_element_text_list(bookmark.select("li.characters"))
                relationships = get_element_text_list(bookmark.select("li.relationships"))
                date_bookmarked = get_element_text(bookmark.select_one("div.user p.datetime"))
                url = "https://archiveofourown.org" + bookmark.select_one("h4 a:nth-of-type(1)")["href"]
                date_updated = get_element_text(bookmark.select_one("p.datetime"))

                # Write bookmark data to CSV
                csvwriter.writerow([url, title, '; '.join(authors), '; '.join(fandoms), '; '.join(warnings),
                                    rating, '; '.join(categories), '; '.join(characters), '; '.join(relationships),
                                    '; '.join(tags), words, date_bookmarked, date_updated])
                num_bookmarks += 1

        # Print completion message
        print("\nAll done! \nYour bookmarks have been saved to {}{}{}_bookmarks.csv{}.".format(Fore.CYAN,
                                                                                               username, Fore.RESET,
                                                                                               Fore.RESET))
        print("Scraped {}{}{} bookmarks.".format(Fore.CYAN, num_bookmarks, Fore.RESET))


# Asks if the user wants to log in
def ask_again():
    while True:
        answer = input("\nWould you like to try again? \n1. Yes \n2. No\n")
        if answer == "1":
            return True
        elif answer == "2":
            return False
        else:
            print("\nInvalid input, please enter 1 or 2.")


# Main function
def main():
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

        # Get the username, available pages, page range, and delay
        username, url = get_username(logged_in)
        get_available_pages(username, session, url)
        start_page, end_page = get_page_range(session, url)
        delay = get_delay()

        # Scrape the bookmarks
        scrape_bookmarks(username, start_page, end_page, session, delay, url)

        if not ask_again():
            # If the user doesn't want to try again, print goodbye message and exit the loop
            print_goodbye()
            break


if __name__ == "__main__":
    main()
