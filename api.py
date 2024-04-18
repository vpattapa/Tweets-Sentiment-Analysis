from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException 
from selenium.webdriver.chrome.options import Options
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import time
import os
import time
from bs4 import BeautifulSoup
import regex as re
import nltk
from sqlalchemy import create_engine
from sqlalchemy.sql import text
nltk.download('vader_lexicon')

app = Flask(__name__)
app.secret_key = os.urandom(24)
webdrivers = {}

def create_webdriver():
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_webdriver():
    session_id = session.get('session_id')
    if session_id not in webdrivers:
        webdrivers[session_id] = create_webdriver()
    return webdrivers[session_id]

def login_twitter(username, password):
    driver = get_webdriver()
    try:
        driver.get("https://twitter.com/login")
        wait = WebDriverWait(driver, 30)
        username_field = wait.until(EC.visibility_of_element_located((By.NAME, "text")))
        username_field.send_keys(username + Keys.RETURN)
        password_field = wait.until(EC.visibility_of_element_located((By.NAME, "password")))
        password_field.send_keys(password + Keys.RETURN)
        explore_link = wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@data-testid="AppTabBar_Explore_Link"]')))
        if explore_link:
            return 1  
    except TimeoutException:
        driver.quit()
        return 0

    driver.quit()
    return -1  

@app.route('/plot_graphs', methods=['POST'])
def plot_graphs():
    return 

def insert_data(data):

    engine = create_engine('postgresql://postgres:writeuser@localhost:5433/postgres')
    temp_table_name = "temp_tweets"
    data.to_sql(temp_table_name, engine, if_exists='replace', index=False)

    with engine.connect() as conn:
        insert_sql = text(f"""
            INSERT INTO "Tweets" 
            SELECT * FROM {temp_table_name}
            ON CONFLICT ("TweetID", "Hashtag") DO NOTHING
        """)
        conn.execute(insert_sql)
        conn.commit()
        drop_sql = text(f"DROP TABLE {temp_table_name}")
        conn.execute(drop_sql)  
        conn.commit()

def scrape_tweets(driver, hashtag):
    driver.get(f"https://twitter.com/search?q=%23{hashtag}&src=typed_query")
    len_of_page = driver.execute_script("return document.body.scrollHeight")
    all_tweets = {}
    while True:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(5)
        new_len_of_page = driver.execute_script("return document.body.scrollHeight")
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tweets = soup.find_all('article', attrs={'data-testid': 'tweet'})
        for tweet in tweets:
            tweet_text = tweet.find('div', lang='en')
            tweet_id = None
            if tweet_text:
                tweet_text = tweet_text.text
                tweet_link = [a['href'] for a in tweet.find_all('a', href=True) if '/status/' in a['href'] and '/analytics' in a['href']]
                parts = tweet_link[0].split('/')
                tweet_id = parts[3] if len(parts) > 3 else None
            if tweet_id:
                all_tweets[tweet_id] = tweet_text
        if new_len_of_page == len_of_page:
            break
        len_of_page = new_len_of_page

    return all_tweets

def cleanTweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

def analyze_sentiment(tweet_text):
    processed_data = cleanTweet(tweet_text)
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(processed_data)
    return sentiment_scores, processed_data

def analyze_tweets(tweets, hashtag):
    analyzed_tweets = []
    for index, tweet in tweets.items():
        sentiment_score, processed_data = analyze_sentiment(tweet)
        if sentiment_score['compound'] <= -0.05:
            sentiment = 'Negative'
        elif sentiment_score['compound'] >= 0.05:
            sentiment = 'Positive'
        else:
            sentiment = 'Neutral'
        analyzed_tweets.append({
            'TweetID' : int(index),
            'Hashtag' : hashtag, 
            'Tweet' : tweet,
            'ProcessedTweet': processed_data,
            'PositiveScore': sentiment_score['pos'], 
            'NegativeScore' : sentiment_score['neg'], 
            'NeutralScore': sentiment_score['neu'], 
            'CompoundScore' : sentiment_score['compound'],
            'Sentiment': sentiment})
    sentiment_tweets = pd.DataFrame(analyzed_tweets, columns= ['TweetID', 
                                                                'Hashtag',
                                                                'Tweet', 
                                                                'ProcessedTweet',
                                                                'PositiveScore',
                                                                'NegativeScore' ,
                                                                'NeutralScore',
                                                                'CompoundScore',
                                                                'Sentiment'])  
    
    insert_data(sentiment_tweets)
    return

@app.route('/')
def home():
    """ Render the homepage """
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    """ Handle the login form and start a session with Twitter if credentials are valid """
    data = request.get_json()
    username = data['username']
    password = data['password']
    session['session_id'] = os.urandom(24).hex()

    login_state = login_twitter(username, password)
    if login_state == 1: 
        return jsonify({"status": "success", "redirect": url_for('enter_hashtag')})
    elif login_state == 0:
        return jsonify({"status": "failure", "message": "Login Timeout"})
    else:
        return jsonify({"status": "failure", "message": "Invalid Credentials"})

@app.route('/hashtag', methods=['GET'])
def enter_hashtag():
    return render_template('hashtag.html')

@app.route('/process_hashtag', methods=['POST'])
def process_hashtag():
    """ Process the submitted hashtag and provide feedback """
    hashtag = request.form['hashtag']
    driver = get_webdriver()
    scraped_tweets = scrape_tweets(driver, hashtag)
    analyze_tweets(scraped_tweets, hashtag)
    plot_graphs(hashtag)
    



if __name__ == '__main__':
    app.run(debug=True)
