# AO3_Scraper
This script is a web scraper that extracts bookmarks from the Archive of Our Own website (AO3) and saves the data to a CSV file. Works only on public bookmarks.

# Features
- Extracts public bookmark data such as URL, title, authors, fandoms, warnings, ratings, categories, characters, relationships, tags, wordcounts and date bookmarked.
- Allows user to specify a range of pages to scrape.
- Allows user to specify an interval delay between requests.
- Displays a progress bar while scraping.
- Writes extracted data to a CSV file.

# Dependencies
- Python 3
- PIP
- requests library
- BeautifulSoup library
- tqdm library

# How to use
- Install `Python 3`
- Install `PIP`
- Install the required dependencies by running `pip install -r requirements.txt` or install them individually by running `pip install requests`, `pip install beautifulsoup4`, `pip install tqdm` in command prompt or terminal. Before running the command, make sure that you are in the correct directory where the `requirements.txt` file is located. You can navigate to the correct directory in the command prompt or terminal by using the `cd` command.
- Run the script by running `python ao3_scraper.py` in command prompt or terminal. Make sure you're in the correct directory.
- When prompted, enter your AO3 username, the starting and ending page of bookmarks to scrape, and an interval delay between requests. Suggested delay time is 5 seconds or more.
- The script will begin scraping the bookmarks and will save the extracted data to a CSV file with the format of `username_bookmarks.csv`.

Note: Be mindful of the delay time and the number of pages to scrape, as it may take a long time to execute and also it may put a lot of burden on AO3's server. A suggested delay time of 5 seconds or more is recommended to prevent overwhelming the server with requests. Consider longer delays if you're scraping a lot of data.

# Or use the relase instead
Instead of downloading the script, you can download the release AO3_Scraper.exe which is the compiled version of the script. This allows you to run the script without having to install Python, PIP or any other dependencies.

- Download the release.
- Unpack it.
- Run `AO3_Scraper.exe`.
- When prompted, enter your AO3 username, the starting and ending page of bookmarks to scrape, and an interval delay between requests. Suggested delay time is 5 seconds or more.
- The script will begin scraping the bookmarks and will save the extracted data to a CSV file with the format of `username_bookmarks.csv`.

# What can be done with the data?
The script saves the extracted data in a CSV file with the format of `username_bookmarks.csv.` This file can be easily imported into a spreadsheet program such as Microsoft Excel, Google Sheets, or LibreOffice Calc. Once imported, you can then manipulate the data as you like. For example, you can use Excel's Power Query to split the delimited data from one column into new rows.

Here are the steps to split the delimited data you're interested in from one column into new rows using Power Query in Excel:

- Open the CSV file in Excel.
- Go to the "Data" tab and click on "From Text/CSV" to import the CSV file.
- Go to the "Data" tab and click on "From Table/Range to open Power Query.
- Select the column that contains the delimited data.
- Click on "Split Column" and then "By Delimiter".
- Select the delimiter (e.g. comma, semicolon, etc.) that separates the values in the selected column.
- Click "Advanced Options" and pick "Split by Rows"

You can now manipulate the data further as needed. Data visualization, statistical analysis, or even machine learning? The possibilities are endless!
