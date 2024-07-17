from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import mysql.connector
from sqlalchemy import create_engine

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

driver.get("https://mb.com.ph/category/news")

urls = []

wait = WebDriverWait(driver, 10)



more_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.more-btn.mb-font-more-button.v-btn.v-btn--text.theme--light.v-size--default.indigo--text')))
driver.execute_script("arguments[0].scrollIntoView();", more_button)
more_button.click()
time.sleep(5)
driver.execute_script("arguments[0].scrollIntoView();", more_button)
more_button.click()
time.sleep(5)
driver.execute_script("arguments[0].scrollIntoView();", more_button)
more_button.click()
time.sleep(5)
driver.execute_script("arguments[0].scrollIntoView();", more_button)
more_button.click()


get_url = driver.find_elements(By.TAG_NAME, 'a')

urls.extend([element.get_attribute('href') for element in get_url])

time.sleep(15)

get_url = driver.find_elements(By.TAG_NAME, 'a')

urls.extend([element.get_attribute('href') for element in get_url])

time.sleep(15)

get_url = driver.find_elements(By.TAG_NAME, 'a')

urls.extend([element.get_attribute('href') for element in get_url])

date_pattern = re.compile(r'https:\/\/mb.com.ph\/\d\d\d\d')



filtered_hrefs = list(
    set(
        href
        for href in urls
        if href is not None and date_pattern.search(href)
    )
)


#for href in filtered_hrefs:
    #print(href)

driver.quit()

root = 'https://mb.com.ph/'
baseurl = 'https://mb.com.ph/category/news'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

r = requests.get('https://mb.com.ph/category/news', headers=header)
soup = BeautifulSoup(r.content, 'lxml')

links_upper = []
article_name = []
main_body = []
author_name = []
time = []
links = []

df = pd.DataFrame(columns=['title', 'author', 'date', 'article'])

for article in filtered_hrefs:
    r = requests.get(article, headers=header)
    soup = BeautifulSoup(r.content, 'lxml')
    box = soup.find('div', class_='col-md-8 col-xl-8 col-12')

    try:
        title = box.find('h1', class_='pt-3 mb-font-article-title').get_text()
    except:
        title = None
    try:
        author = box.find('span', class_='pb-0').get_text()
    
    except:
        author = None
    
    date = box.find('span', class_='mb-font-article-date').get_text()
    body = box.find('div', class_='pt-8 custom-article-body mb-font-article-body').get_text()
    article_name.append(title)
    main_body.append(body)
    author_name.append(author)
    time.append(date)
    print("success: ", title)


df['title'] = article_name
df['author'] = author_name
df['date'] = time
df['article'] = main_body
df['link'] = filtered_hrefs

df['date'] = df['date'].str.split(' ').str[:3].str.join(' ')

df['date'] = df['date'].str.replace('June', 'Jun')

df['date'] = df['date'].str.replace('July', 'Jul')

df['date'] = df['date'].str.replace('April', 'Apr')

df['date'] = df['date'].str.replace(',', '')

df['date'] = pd.to_datetime(df['date'], format='%b %d %Y')

df['date'] = df['date'].astype('datetime64[ns]')

import textwrap
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")

sentiment = pipeline("text-classification", model=model, tokenizer=tokenizer)

sentiment_scores = []
label = []

for title in df['title']:
    score = sentiment(title)
    sentiment_scores.append(score[0]['score'])
    label.append(score[0]['label'])


transformers_data = {
    'score': sentiment_scores,
    'label': label
}

df2 = pd.DataFrame(transformers_data)

df2['label'] = df2['label'].str.replace('LABEL_0', 'NEGATIVE')
df2['label'] = df2['label'].str.replace('LABEL_1', 'NEUTRAL')
df2['label'] = df2['label'].str.replace('LABEL_2', 'POSITIVE')

df3 = pd.concat([df, df2], axis=1)

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="****",
    database="ph_newspaper"
)

cursor = db_connection.cursor()

engine = create_engine('mysql+mysqlconnector://root:****@localhost/ph_newspaper')

df3.to_sql('philstar', con=engine, if_exists='append', index=False)

try:
    cursor.execute("""
        SELECT title, MIN(article_id) AS min_article_id
        FROM philstar
        GROUP BY title
        HAVING COUNT(*) > 1
    """)
    duplicate_titles = cursor.fetchall()

    for title, min_article_id in duplicate_titles:
        cursor.execute("""
            DELETE FROM philstar
            WHERE title = %s AND article_id <> %s
        """, (title, min_article_id))
    
    cursor.execute("""UPDATE philstar
    SET date = REPLACE(date, ' , / ', '')""")

    cursor.execute("""UPDATE philstar
    SET date = TRIM(date)""")

    db_connection.commit()
    print("Duplicate entries have been deleted.")

except mysql.connector.Error as e:
    print("Error:", e)

finally:
    cursor.close()
    db_connection.close()
