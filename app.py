from flask import Flask, render_template, jsonify
from flask_cors import CORS
import mysql.connector
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Initialize Flask application
app = Flask(__name__)

CORS(app)

# Azure Database for MySQL Configuration
DATABASE_CONFIG = {
    'host': "quotesmysql.mysql.database.azure.com",
    'user': "piyush",
    'password': "Walkingdolphin@2023",
    'database': "quotes",
    'port': 3306,
    #'ssl_ca': 'path_to_ca_certificate.pem'  # Path to CA certificate if required
}

# Azure AI Service Configuration
KEY = '9b6e114fc9fd41069a8a49c59d61db8c'
ENDPOINT = 'https://quotesai.cognitiveservices.azure.com/'

# Connect to Azure Database for MySQL
def get_database_connection():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Initialize Azure AI Service Client
def initialize_text_analytics_client():
    credential = AzureKeyCredential(KEY)
    text_analytics_client = TextAnalyticsClient(endpoint=ENDPOINT, credential=credential)
    return text_analytics_client

# Fetch quote from Azure Database for MySQL
def fetch_quote_from_database():
    conn = get_database_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Quote FROM Quotes ORDER BY RAND() LIMIT 1")  # Randomly fetch a quote
        quote = cursor.fetchone()[0]
        conn.close()
        return quote
    else:
        return "Database connection error"

# Analyze quote using Azure AI Service
def analyze_quote(quote):
    text_analytics_client = initialize_text_analytics_client()
    document = [quote]
    
    # Sentiment Analysis
    response = text_analytics_client.analyze_sentiment(documents=document)[0]
    sentiment = response.sentiment
    
    # Text Summarization (Basic example: First few words)
    summary = " ".join(quote.split()[:10]) + "." if len(quote.split()) > 10 else quote
    
    return sentiment, summary

@app.route('/')
def index():
    quote = fetch_quote_from_database()
    sentiment, summary = analyze_quote(quote)
    return render_template('index.html', quote=quote, sentiment=sentiment, summary=summary)

@app.route('/new')
def new_quote():
    quote = fetch_quote_from_database()
    sentiment, summary = analyze_quote(quote)
    return jsonify({'quote': quote, 'sentiment': sentiment, 'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
