import requests
from bs4 import BeautifulSoup
from . import error_handling


# Creates a session and returns the authenticity token
def create_session(logger):
    print("\nCreating a session...")
    logger.info("Creating a session...")

    # Create a session with custom user agent
    headers = {
        'User-Agent': 'Bookmark Scraper Bot'
    }

    try:
        # Create a session and make a GET request
        with requests.Session() as session:
            session.headers.update(headers)
            response = session.get("https://archiveofourown.org/users/login")
            response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        token = soup.find('input', {'name': 'authenticity_token'})

        if token is None:
            error_handling.handle_token_not_found(logger)
            return None, None
        else:
            token = token['value']
            print("\nSession created.")
            logger.info("Session created.")
            return token, session

    except requests.exceptions.RequestException as error:
        error_handling.handle_request_error(error, logger)
        return None, None
