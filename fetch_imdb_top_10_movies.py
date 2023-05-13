import csv

import requests
from bs4 import BeautifulSoup
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
headers = {
    "User-Agent": user_agent
}

# Configure the headless chrome driver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(f'--user-agent="{user_agent}"')
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the IMDB website and retrieve the top 10 movies
driver.get("https://www.imdb.com/chart/top/")
movies_rows = driver.find_elements(By.XPATH, "//tbody[@class='lister-list']/tr")

# Copy cookies from Selenium WebDriver to requests Session
session = requests.Session()
for cookie in driver.get_cookies():
    session.cookies.set(cookie['name'], cookie['value'])

# Traverse through each movie element rows
movies = []
for movie in movies_rows[:10]:
    movie_link = movie.find_element(By.CSS_SELECTOR, "td.titleColumn a")
    title = movie_link.text
    rating = movie.find_element(By.CSS_SELECTOR, "td.ratingColumn strong").text
    print(f"Crawling summary for '{title}'...")
    summary_response = session.get(movie_link.get_attribute('href'), headers=headers)
    summary_soup = BeautifulSoup(summary_response.text, 'html.parser')
    summary = summary_soup.select_one('p[data-testid="plot"]').text.strip()
    movies.append([title, rating, summary])


# Format Markdown-style table for output file
writer = MarkdownTableWriter(
    headers=["Title", "Rating", "Summary"],
    column_styles=[Style(align="left"), Style(align="left"), Style(align="left")],
    value_matrix=movies,
    margin=1,
)
writer.write_table()

# Create a CSV file and write the movie data to it
with open('top_movies.csv', 'w+') as file:
    file.write(writer.dumps())


# Close the headless chrome driver
driver.quit()
