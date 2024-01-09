import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import mysql.connector
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Azure Database for MySQL Configuration
DATABASE_CONFIG = {
    'host': os.getenv("DATABASE_HOST"),
    'user': os.getenv("DATABASE_USER"),
    'password': os.getenv("DATABASE_PASSWORD"),
    'database': os.getenv("DATABASE_NAME"),
    'port': 3306,
}

# Azure AI Service Configuration
KEY = os.getenv("AZURE_KEY")
ENDPOINT = os.getenv("AZURE_ENDPOINT")

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
        cursor.execute("SELECT Quote FROM Quotes ORDER BY RAND() LIMIT 1")
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

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(debug=True)
