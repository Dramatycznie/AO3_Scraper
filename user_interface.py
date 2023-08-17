from colorama import Fore


# put printing in a different module?
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
    print(Fore.CYAN + "\nThank you for using AO3 Scraper!" + Fore.RESET)
    input("\nPress Enter to exit.")
