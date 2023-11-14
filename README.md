# AO3_Scraper
A web scraper that extracts bookmark metadata from Archive of Our Own and saves it to a CSV file. Has an option to download the bookmarks and neatly organize them into folders based on fandoms.

**Works on public and private bookmarks if you log into your AO3 account.**

## Table of Contents
- [Features](#features)
- [Dependencies](#dependencies)
- [How to Use](#how-to-use)
- [Contact](#contact)
- [Bug Reports and Feature Requests](#bug-reports-and-feature-requests)

# Features

Scrapes or downloads bookmarks from Archive of Our Own. Allows user to log into their account to access private bookmarks and works that are only available to registered users.

### Scraping
- Extracts bookmark metadata such as URL, title, authors, fandoms, warnings, ratings, categories, characters, relationships, tags, wordcounts, date bookmarked, date updated.
- Writes extracted data to a CSV file.

### Downloading
- Downloads bookmarks to different folders based on fandoms, and names the files based on the title and authors.
- Supports downloading bookmarked series.
- Allows user to choose format when downloading bookmarks (HTML, MOBI, EPUB, PDF, AZW3).

### Updating
- Checks bookmarks for updates and downloads them accordingly (HTML, EPUB, PDF). 
- Works only if bookmarks are in the correct folder and named correctly.


# Dependencies
- Python 3
- PIP
- requests
- BeautifulSoup 
- tqdm
- colorama
- ebooklib
- pypdf2

# How to use
Run the script yourself or use the release.

### Running the script
- Download or clone the repository.
- Install the required dependencies by running `pip install -r requirements.txt` in the correct directory where the `requirements.txt` file is located.
- Run the script by running `python main.py` in command prompt or terminal. Make sure you're in the correct directory.
- Scrape or download the bookmarks.

### Use the release
Instead of downloading the script, you can download the [latest release](https://github.com/Dramatycznie/AO3_Scraper/releases) and run it directly.

- Download the release.
- Unpack it.
- Run `AO3_Scraper.exe`.
- Scrape or download the bookmarks.

# Contact
If you have any questions or feedback about this project, please feel free to reach out to me.
- Email: mellodramat@gmail.com
- GitHub: https://github.com/Dramatycznie

# Bug reports and feature requests
For bug reports and feature requests, please open an issue on my GitHub repository: https://github.com/Dramatycznie/AO3_Scraper/issues
