import sys


# Handles the "Retry later" message (unneeded?)
def handle_retry_later(response, logger):
    if "Retry later" in response.text:
        logger.error("Received 'Retry later' message. Too many requests, stopping scraping.")
        print("\nReceived 'Retry later' message. Please try again later, consider increasing the delay.")
        return True
    return False


# Handles request errors
def handle_request_error(error, logger):
    if "429" in str(error):  # HTTP 429: Too Many Requests
        logger.error("Too many requests, stopping scraping.")
        print("\nToo many requests. Please try again later, consider increasing the delay.")
    else:
        logger.error(f"An error occurred while making the request: {error}")
        print("\nAn error occurred while making the request. Please try again later. Check the logs for more details.")


# Handles invalid input
def handle_invalid_input(context, logger):
    logger.error(f"Invalid input: {context}")
    print(f"\nInvalid input: {context}")


# Handles token not found error
def handle_token_not_found(logger):
    logger.error("Authenticity token not found. Cannot log in.")
    print("\nAn error occurred while logging in. Skipping. Please try again later. Check the logs for more details.")


# Handles parse errors
def handle_parse_error(logger):
    logger.error("Error parsing HTML.")
    print("\nAn error occurred while parsing the HTML. Please try again later. Check the logs for more details.")


# Handles keyboard interrupts
def handle_keyboard_interrupt(logger):
    logger.error("Keyboard Interrupt detected.")
    print("\nKeyboardInterrupt received. Exiting gracefully...")
    sys.exit(0)
