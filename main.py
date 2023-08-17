import atexit

import error_handling
import logging_utils
import user_input
import user_interface
import scraping_utils
import session_utils


# Main function
def main():
    logger = logging_utils.setup_logging()
    atexit.register(logging_utils.log_program_closure, logger)
    try:
        user_interface.print_welcome()
        # Ask if the user wants to log in (for now here)
        log_in = user_input.ask_if_log_in(logger)
        token, session = None, None  # Initialize variables for the session

        while True:
            if log_in and session is None:  # Create a session if logging in
                token, session = session_utils.create_session(logger)
                user_input.get_login_info(token, session, logger)
                logged_in = True
            else:
                logged_in = False

            # Get the info needed to scrape the bookmarks
            username, url = user_input.get_username(logged_in, logger)
            if user_input.get_available_pages(username, session, url, logger):
                start_page, end_page = user_input.get_page_range(session, url, logger)
                delay = user_input.get_delay(logger)

                # Scrape the bookmarks
                scraping_utils.scrape_bookmarks(username, start_page, end_page, session, delay, logger)

                if not user_input.ask_again(logger):
                    # If the user doesn't want to try again, print goodbye message and exit the loop
                    user_interface.print_goodbye()
                    break

    except KeyboardInterrupt:
        error_handling.handle_keyboard_interrupt(logger)


if __name__ == "__main__":
    main()
