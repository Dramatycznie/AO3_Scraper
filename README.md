# AO3_Scraper
Web scraper that extracts bookmark metadata from Archive of Our Own and saves it to a CSV file. Works on public and private bookmarks if you log into your AO3 account. Now with an option to download the bookmarks and neatly organize them into folders based on fandoms.

## Table of Contents
- [Features](#features)
- [Dependencies](#dependencies)
- [How to Use](#how-to-use)
- [What Can Be Done with the Data?](#what-can-be-done-with-the-data)
- [Contact](#contact)
- [Bug Reports and Feature Requests](#bug-reports-and-feature-requests)

# Features
- Extracts bookmark metadata such as URL, title, authors, fandoms, warnings, ratings, categories, characters, relationships, tags, wordcounts, date bookmarked, date updated.
- Downloads bookmarks to different folders based on fandoms, and names the files based on the title and authors.
- Allows user to log into their AO3 account to access private bookmarks and works that are only available to registered users.
- Allows user to choose scraping or downloading bookmarks.
- Implements logging for better error tracking and troubleshooting.
- Shows the number of pages available.
- Allows user to specify a range of pages.
- Allows user to specify an interval delay between requests.
- Displays a progress bar.
- Allows user to choose format when downloading bookmarks (HTML, MOBI, EPUB, PDF, AZW3).
- Writes extracted data to a CSV file.

# Dependencies
- Python 3
- PIP
- requests library
- BeautifulSoup library
- tqdm library

# How to use
Run the script yourself or use the release.

### Running the script
- Install `Python 3` and `PIP`
- Install the required dependencies by running `pip install -r requirements.txt` in the correct directory where the `requirements.txt` file is located.
- Run the script by running `python main.py` in command prompt or terminal. Make sure you're in the correct directory.
- Scrape or download the bookmarks.

### Use the release
Instead of downloading the script, you can download the [latest release](https://github.com/Dramatycznie/AO3_Scraper/releases) and run it directly.

- Download the release.
- Unpack it.
- Run `AO3_Scraper.exe`.
- Scrape or download the bookmarks.

# What can be done with the data?
The script saves the extracted data in a CSV file with the format of `username_bookmarks.csv.` This file can be easily imported into a spreadsheet program such as Microsoft Excel, Google Sheets, or LibreOffice Calc. Once imported, you can then manipulate the data as you like. For example, you can use Excel's Power Query to split the delimited data from one column into new rows.

Here are the steps to split the delimited data you're interested in from one column into new rows using Power Query in Excel:

- Open the CSV file in Excel.
- Go to the "Data" tab and click on "From Text/CSV" to import the CSV file.
- Go to the "Data" tab and click on "From Table/Range to open Power Query.
- Select the column that contains the delimited data.
- Click on "Split Column" and then "By Delimiter".
- Select the delimiter (semicolon and a space after it).
- Click "Advanced Options" and pick "Split by Rows".

You can now manipulate the data further as needed. Data visualization, statistical analysis, or even machine learning? The possibilities are endless!

# Contact
If you have any questions or feedback about this project, please feel free to reach out to me.
- Email: mellodramat@gmail.com
- GitHub: https://github.com/Dramatycznie

# Bug reports and feature requests
For bug reports and feature requests, please open an issue on my GitHub repository: https://github.com/Dramatycznie/AO3_Scraper/issues
