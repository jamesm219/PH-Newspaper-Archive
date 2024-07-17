from flask import Flask, request, render_template
import csv
import logging
import os
import re
from datetime import datetime

app = Flask(__name__)

CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phnews.csv')

logging.basicConfig(level=logging.DEBUG)

def read_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            data = [row for row in csv_reader]
        logging.debug(f"CSV data read successfully: {data}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')  # Adjust format as per your CSV
    except ValueError:
        logging.error(f"Date parsing error for date: {date_str}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_article():
    if request.method == 'POST':
        keyword = request.form['keyword']
        chosen_date = request.form.get('chosen_date')

        logging.debug(f"Keyword received: {keyword}")
        logging.debug(f"Chosen date received: {chosen_date}")
        data = read_csv(CSV_FILE_PATH)

        regex = re.compile(fr'\b{keyword}\b', re.IGNORECASE)
        results = [row for row in data if regex.search(row['article'])]

        if chosen_date:
            chosen_date_parsed = parse_date(chosen_date)
            results = [row for row in results if parse_date(row['date']) == chosen_date_parsed]

        results.sort(key=lambda row: parse_date(row['date']), reverse=True)
        logging.debug(f"Search results: {results}")

        return render_template('search_results.html', results=results)

    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
