#!/usr/bin/python3
import webbrowser
from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import cProfile

app = Flask(__name__)

# URL to send the GET request to
url = 'https://mentfx.com/sentiment-viewer/index.php'

# Headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# List of symbols to include
desired_symbols = {'EURUSD', 'AUDUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'EURAUD'}

@app.route('/')
def index():
    sentiment_data = fetch_sentiment_data()
    return render_template('index.html', sentiment_data=sentiment_data)

def fetch_sentiment_data():
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parsing the response content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all rows in the sentiment table
        rows = soup.select('table.sentiment-table tbody tr')

        # Extract data into a list of dictionaries
        sentiment_data = []
        for row in rows:
            cells = row.find_all('td')
            symbol = cells[0].text.strip()

            # Check if the symbol is in the desired list
            if symbol in desired_symbols:
                intraday_bullish = cells[1].find('div', class_='bullish').text.strip().replace('%', '')
                daily_bullish = cells[2].find('div', class_='bullish').text.strip().replace('%', '')

                # Convert string percentages to integers
                intraday_bullish = int(intraday_bullish)
                daily_bullish = int(daily_bullish)

                # Determine sentiment indicator
                sentiment_indicator = 'Bullish' if daily_bullish > (100 - daily_bullish) else 'Bearish'
                if (intraday_bullish > 54 and daily_bullish > 69):
                    sentiment_data.append({
                        'symbol': symbol,
                        'sentiment_indicator': 'Bullish',
                        'intraday_bullish': intraday_bullish,
                        'daily_bullish': daily_bullish
                    })

                # Check if the conditions are met for bearish sentiment
                if (100 - intraday_bullish > 54 and 100 - daily_bullish > 69):
                    sentiment_data.append({
                        'symbol': symbol,
                        'sentiment_indicator': 'Bearish',
                        'intraday_bullish': intraday_bullish,
                        'daily_bullish': daily_bullish
                    })

        return sentiment_data

    except requests.exceptions.Timeout:
        print("The request timed out")
        return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == '__main__':
    # Open the web page in the default web browser
    webbrowser.open('http://127.0.0.1:5000')
    # Run the Flask application
    app.run(debug=False)
