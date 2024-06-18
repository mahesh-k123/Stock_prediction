import requests
import json
from textblob import TextBlob
import pandas as pd
import yfinance as yf

# Step 1: Define your RapidAPI key and endpoint
RAPIDAPI_KEY = '94f9b156f2msh04caa31d238743ap187692jsn95f450596fe3'
NEWS_API_URL = 'https://reuters-business-and-financial-news.p.rapidapi.com/news/v2/list'

# Step 2: Define parameters for the API request
query = 'Apple'
params = {
    'category': 'businessNews',  # Adjust category as needed
    'region': 'US',
    'date': '2023-12-31'
}

headers = {
    'x-rapidapi-host': 'reuters-business-and-financial-news.p.rapidapi.com',
    'x-rapidapi-key': RAPIDAPI_KEY
}

# Step 3: Make the API request
try:
    response = requests.get(NEWS_API_URL, headers=headers, params=params)
    response.raise_for_status()  # Check for HTTP errors

    # Print the entire response JSON to understand its structure
    print(json.dumps(response.json(), indent=2))
    
    news_data = response.json().get('articles', [])  # Adjust this based on the actual response structure

    # Extract relevant information if 'articles' is present
    if news_data:
        news_headlines = [item['title'] for item in news_data]
        news_dates = [item['published'] for item in news_data]

        # Step 4: Perform sentiment analysis on the news headlines
        sentiment_scores = []
        for headline in news_headlines:
            blob = TextBlob(headline)
            sentiment_score = blob.sentiment.polarity
            sentiment_scores.append(sentiment_score)

        # Step 5: Create a DataFrame to store sentiment scores with corresponding dates
        sentiment_df = pd.DataFrame({
            'Date': pd.to_datetime(news_dates),
            'Sentiment_Score': sentiment_scores
        })

        # Step 6: Load stock data from Yahoo Finance
        ticker = 'AAPL'
        df = yf.download(tickers=ticker, period='1mo', interval='1d')

        # Merge sentiment scores with stock data based on dates
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        sentiment_df['Date'] = sentiment_df['Date'].dt.date
        df['Date'] = df['Date'].dt.date
        df = df.merge(sentiment_df, how='left', on='Date')
        df.set_index('Date', inplace=True)

        # Print or use the DataFrame with sentiment scores
        print(df[['Close', 'Sentiment_Score']])
    else:
        print('No articles found in API response.')

except requests.exceptions.RequestException as e:
    print(f'HTTP Request failed: {e}')
except Exception as e:
    print(f'General Error: {str(e)}')
