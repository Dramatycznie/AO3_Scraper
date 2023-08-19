import atexit

import error_handling
import logging_utils
import user_input
import user_interface
import scraping_utils
import session_utils
import downloading_utils


# Main function
def main():
    logger = logging_utils.setup_logging()
    atexit.register(logging_utils.log_program_closure, logger)
    try:
        user_interface.print_welcome()
        log_in = user_input.ask_if_log_in(logger)
        token, session = None, None  # Initialize variables for the session

        while True:
            if log_in and session is None:  # Create a session if logging in
                token, session = session_utils.create_session(logger)
                user_input.get_login_info(token, session, logger)
                logged_in = True
            else:
                logged_in = False

            action = user_input.download_or_scrape(logger)

            # Get the info needed to scrape the bookmarks
            username, url = user_input.get_username(logged_in, action, logger)

            # Call get_available_pages and check the result
            available_pages = user_input.get_available_pages(username, session, url, logger)

            if available_pages is not None:
                start_page, end_page = user_input.get_page_range(session, url, logger)
                delay = user_input.get_delay(logger)

                if action == "download":
                    chosen_format = user_input.get_download_format(logger)
                    downloading_utils.download_bookmarks(url, start_page, end_page, session, chosen_format, delay,
                                                         logger)
                elif action == "scrape":
                    scraping_utils.scrape_bookmarks(username, start_page, end_page, session, delay, logger)

                if not user_input.ask_again(logger):
                    user_interface.print_goodbye()
                    break  # Exit the loop if the user chooses not to try again

    except KeyboardInterrupt:
        error_handling.handle_keyboard_interrupt(logger)


if __name__ == "__main__":
    main()
