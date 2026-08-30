# Real-Time Text Scraping & Financial News Analysis

A Python-based web scraping and financial news processing project that collects article links and full-text news, stores the data in MongoDB, retrieves Yahoo Finance news for individual stock tickers, and performs financial sentiment analysis using a BERT-based model.

## Overview

This repository brings together two related workflows:

1. **Website news scraping** – Uses Selenium and Chrome to discover article hyperlinks, extract article titles, publication date/time, and article text, and store the results in MongoDB.
2. **Financial news analysis** – Uses `yfinance` to retrieve stock-related news metadata, `newspaper3k` to extract article text, and a FinancialBERT model to classify news sentiment with a confidence score.

The project also contains helper utilities for stock ticker lookup, historical market data retrieval, filtering stored news, visualization with Plotly, and an exploratory LSTM notebook.

## Architecture

```text
                         ┌──────────────────────────┐
                         │      News Web Page       │
                         │      (e.g. Moneycontrol) │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   Selenium WebScraper    │
                         │  Link discovery + text   │
                         │       extraction         │
                         └────────────┬─────────────┘
                                      │
                         ┌────────────▼─────────────┐
                         │       ScrapeData         │
                         │ Link filtering, cleaning │
                         │ and document generation │
                         └────────────┬─────────────┘
                                      │
                         ┌────────────▼─────────────┐
                         │         MongoDB           │
                         │ Links + scraped articles │
                         └──────────────────────────┘

        Yahoo Finance Workflow

 ┌──────────────┐    ┌────────────────┐    ┌──────────────────┐
 │ Stock Ticker │───►│   yfinance     │───►│ ArticleExtractor │
 │   e.g. TCS   │    │  News metadata  │    │  newspaper3k     │
 └──────────────┘    └────────────────┘    └────────┬─────────┘
                                                    │
                                                    ▼
                                           ┌──────────────────┐
                                           │ FinancialBERT    │
                                           │ Sentiment Model  │
                                           └────────┬─────────┘
                                                    │
                                                    ▼
                                           Positive / Negative /
                                           Neutral + confidence
```

## Features

- Dynamic hyperlink discovery using Selenium.
- Duplicate hyperlink removal before database insertion.
- MongoDB-backed storage for scraped links and news documents.
- Tracking of visited article links to support incremental scraping workflows.
- Extraction of article title, date/time, and body text from web pages.
- Batch-based scraping through the application driver.
- Yahoo Finance news retrieval for a supplied stock ticker.
- Full article extraction with `newspaper3k`, with the Yahoo Finance summary used as a fallback when article extraction fails.
- Financial sentiment classification using a BERT-based model.
- Confidence scores attached to sentiment predictions.
- Stock symbol discovery with `yahooquery`.
- Historical stock-price retrieval with `yfinance`.
- Basic filtering and visualization utilities using Pandas and Plotly.
- Exploratory stock/LSTM work in `stock_lstm.ipynb`.

## Repository Structure

```text
Real-Time-Text-Scraping/
│
├── MongoDBManager/
│   └── pymongo_conn.py
│
├── ScrapeData/
│   ├── scrape_hyperlinks.py
│   └── scraping_data.py
│
├── WebScraper/
│   └── scraper.py
│
├── YFinanceNews/
│   ├── news_scraper.py
│   └── sentiment_analysis.py
│
├── all_tickers.py
├── driver_code.py
├── stock_lstm.ipynb
└── .gitignore
```

## Module Description

### `WebScraper/scraper.py`

Contains the Selenium-based scraping layer.

- `WebScraping` opens a web page, finds elements, and extracts hyperlinks.
- `ExtractText` opens individual article pages and extracts the title, publication information, and article content.
- Selenium waits for and attempts to click a **READ MORE** button before extracting the complete article body.
- ChromeDriver is managed through `webdriver-manager`.

### `ScrapeData/scrape_hyperlinks.py`

Provides a higher-level workflow for discovering and storing article links.

The current example targets:

```text
https://www.moneycontrol.com/news/business/stocks/
```

The discovered links are deduplicated and converted into MongoDB documents such as:

```python
{"link": "https://example.com/article"}
```

### `ScrapeData/scraping_data.py`

Handles the transition from stored links to scraped article documents.

The workflow is:

```text
MongoDB hyperlink collection
        ↓
ReadData
        ↓
Filter links by path/category
        ↓
ExtractText
        ↓
Title + Date/Time + Article Text
        ↓
List of MongoDB-ready dictionaries
```

Scraped documents use the following structure:

```python
{
    "title": "Article title",
    "date_time": "Publication date/time",
    "text": "Article body"
}
```

### `MongoDBManager/pymongo_conn.py`

Provides a small MongoDB wrapper around `pymongo`.

Supported operations include:

- MongoDB connection management
- Database/collection access
- Collection document counts
- Single or bulk inserts
- Reading an entire collection into a Pandas DataFrame
- Closing the MongoDB client

The current implementation connects to a local MongoDB instance:

```text
mongodb://localhost:27017/
```

### `driver_code.py`

Acts as the main orchestration layer for the website-scraping workflow.

`NewsScraperApp`:

1. Reads the number of previously logged/visited links.
2. Uses that count to determine a scraping range.
3. Scrapes a configurable batch of articles.
4. Saves the resulting documents into MongoDB.

The current `run()` example enables scraping with:

```python
app.run(scrape=True)
```

### `YFinanceNews/news_scraper.py`

Provides a separate financial-news ingestion workflow.

`YahooFinanceNewsScraper`:

1. Receives a ticker symbol such as `TCS.NS`.
2. Fetches news metadata using `yfinance`.
3. Extracts title, publisher, URL, summary, and publication timestamp.
4. Attempts to download and parse the article using `requests` + `newspaper3k`.
5. Falls back to the Yahoo Finance summary if full-text extraction is unavailable.
6. Returns LangChain `Document` objects containing article text and metadata.

Example metadata:

```python
{
    "title": "...",
    "publisher": "...",
    "source": "...",
    "ticker": "TCS.NS",
    "date": "2026-...",
    "time": "...",
    "type": "news"
}
```

### `YFinanceNews/sentiment_analysis.py`

Runs financial sentiment analysis over the documents returned by the Yahoo Finance scraper.

The pipeline performs:

```text
Yahoo Finance News
        ↓
Article extraction
        ↓
Text cleaning
        ↓
BERT tokenizer
        ↓
FinancialBERT model
        ↓
Softmax probabilities
        ↓
Sentiment + confidence
```

The sentiment label and confidence score are added to the document metadata.

The module can also export the processed documents to CSV.

### `all_tickers.py`

Contains utility classes for:

- Searching for a company ticker symbol with `yahooquery`.
- Downloading historical stock prices using `yfinance`.
- Reading/filtering news records from CSV files.
- Filtering news by company, label, or date.
- Creating basic line and scatter plots with Plotly.

### `stock_lstm.ipynb`

An exploratory notebook containing stock-data retrieval, visualization, and LSTM-related experimentation.

## Requirements

The repository does not currently include a `requirements.txt`, so install the packages used by the source code.

Core dependencies include:

```text
pandas
pymongo
selenium
webdriver-manager
python-dotenv
yfinance
yahooquery
requests
newspaper3k
langchain-core
torch
transformers
plotly
jupyter
```

For the LSTM notebook, additional packages such as TensorFlow/Keras and their compatible dependencies may be required.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/AI2Enginex/Real-Time-Text-Scraping.git
cd Real-Time-Text-Scraping
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pandas pymongo selenium webdriver-manager python-dotenv yfinance yahooquery requests newspaper3k langchain-core torch transformers plotly jupyter
```

## MongoDB Setup

The scraping workflow expects MongoDB to be available locally on the default MongoDB port.

Start MongoDB and create/configure the collections referenced by the environment variables.

Create a `.env` file in the project root:

```env
DATABASE=your_database_name
HYPERLINK_COLLECTION=your_hyperlink_collection
NEWS_COLLECTION=your_news_collection
SCRAPED_LINKS=your_scraped_links_collection
CHROME_DRIVER_VERSION=your_chrome_driver_version
```

The repository already ignores `.env`, so secrets and local configuration do not need to be committed to Git. fileciteturn9file0L2-L2

> **Important:** The MongoDB connection string is currently hard-coded as `mongodb://localhost:27017/` in `MongoDBManager/pymongo_conn.py`. The `.env` variables configure database and collection names, not the MongoDB host itself.

## Running the Web Scraper

The main entry point for the website/news scraping pipeline is:

```bash
python driver_code.py
```

The current implementation creates a `NewsScraperApp`, determines a batch range from the scraped-link collection, extracts article data, and writes the scraped documents to MongoDB. fileciteturn2file0L2-L2

The scraper currently uses selectors tailored to the target website, including values for article containers, title elements, publication information, paragraphs, and a `READ MORE` button. These selectors may need to be updated if the target website changes its HTML structure. fileciteturn2file0L2-L2

## Running Yahoo Finance News Scraping

You can use the Yahoo Finance scraper directly:

```python
from YFinanceNews.news_scraper import YahooFinanceNewsScraper

scraper = YahooFinanceNewsScraper("TCS.NS")
documents = scraper.get_news_documents()

print("Total documents:", len(documents))
```

The scraper retrieves Yahoo Finance news metadata and attempts full article extraction before falling back to the provider summary. fileciteturn6file0L2-L2

## Running Financial Sentiment Analysis

Example:

```python
from YFinanceNews.sentiment_analysis import FinBERTSentiment

sentiment_analyzer = FinBERTSentiment(label="RELIANCE.NS")
documents = sentiment_analyzer.predict()

for doc in documents:
    print(doc.metadata.get("title"))
    print(doc.metadata.get("sentiment"))
    print(doc.metadata.get("confidence"))
```

The sentiment implementation cleans the article text, tokenizes it with a BERT tokenizer, runs the FinancialBERT classifier, converts logits to probabilities, and stores the selected sentiment label and confidence in the document metadata. fileciteturn7file0L2-L2

## Example Yahoo Finance Output

A processed `Document` conceptually looks like:

```python
Document(
    page_content="Cleaned article text...",
    metadata={
        "title": "Example financial news",
        "publisher": "Publisher Name",
        "source": "https://example.com/article",
        "ticker": "RELIANCE.NS",
        "date": "2026-08-30",
        "time": "12:30:00",
        "type": "news",
        "sentiment": "positive",
        "confidence": 0.91
    }
)
```

## Incremental Scraping Concept

The website-scraping pipeline maintains a separate MongoDB collection containing visited links. During document creation, each processed URL is written to the scraped-link collection. This provides a simple mechanism for tracking progress and supports batch-based execution. fileciteturn3file0L2-L2

The main driver uses the number of records in that collection as the starting point for its next batch. fileciteturn2file0L2-L2

## Data Flow in Detail

### Web scraping pipeline

```text
Target website
   ↓
Selenium opens page
   ↓
Find article links
   ↓
Remove duplicate links
   ↓
Store links in MongoDB
   ↓
Read/filter stored links
   ↓
Open each article
   ↓
Extract title + date/time + body
   ↓
Store structured news documents in MongoDB
```

The hyperlink workflow uses Selenium to collect links, converts them to a DataFrame, removes duplicates, and converts the cleaned links to dictionaries ready for MongoDB insertion. fileciteturn11file0L2-L2

### Financial-news pipeline

```text
Ticker symbol
   ↓
Yahoo Finance news
   ↓
Article URL
   ↓
HTTP request
   ↓
newspaper3k parsing
   ↓
Full article text / summary fallback
   ↓
LangChain Document
   ↓
FinancialBERT
   ↓
Sentiment + confidence
```

## Notes and Limitations

- The current website scraper is **site-specific**. CSS class names, HTML tags, and button text are passed into the scraper and therefore depend on the target site's structure. fileciteturn4file0L2-L2
- MongoDB is currently configured for a local server at `localhost:27017`. fileciteturn5file0L2-L2
- The repository currently has no dependency lockfile or `requirements.txt`.
- `CHROME_DRIVER_VERSION` is read from the environment, so Chrome/ChromeDriver compatibility should be checked when setting up a new machine. fileciteturn4file0L2-L2
- Web pages can change their HTML structure, which may require selector updates.
- Some publishers may block automated requests or restrict scraping. Always respect the target website's terms, robots policies, and applicable laws.
- Financial sentiment predictions are model outputs and should not be treated as investment advice.



## Disclaimer

This project is intended for educational, research, and engineering purposes. Web scraping should be performed responsibly and in accordance with the terms and policies of the websites being accessed. Financial sentiment outputs are for analysis only and do not constitute financial or investment advice.


