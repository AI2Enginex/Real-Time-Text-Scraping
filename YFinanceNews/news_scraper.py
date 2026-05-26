import yfinance as yf
import requests
from langchain_core.documents import Document
from datetime import datetime
from newspaper import Article


def get_date_time(value: str):

    try:
        published_dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

        date = published_dt.date()
        time = published_dt.time()

        return str(date), str(time)

    except Exception:
        return None, None


# Class for extracting article text using the newspaper3k library.
class ArticleExtractor:
    """
    Responsible for extracting article text from a URL
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    def extract(self, url: str):

        try:
            # Add headers here
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return None

            article = Article(url)
            article.set_html(response.text)  # use fetched HTML
            article.parse()

            text = article.text

            if text:
                return text  # limit for embeddings

        except Exception as e:
            print(f"Article extraction failed: {e}")

        return None

# Class for retrieving and processing news text using the yfinance library.
class FetchNews:
    """
    Responsible for fetching Yahoo Finance news metadata
    """

    def __init__(self, ticker: str):

        self.ticker = ticker

    def fetch_news(self):

        try:

            ticker = yf.Ticker(self.ticker)

            news = ticker.news

            if not news:
                return []

            return news

        except Exception as e:

            print(f"Error fetching Yahoo Finance news: {e}")

            return []


class YahooFinanceNewsScraper(FetchNews):

    def __init__(self, ticker):

        super().__init__(ticker)

        self.article_extractor = ArticleExtractor()

    def get_news_documents(self):

        documents = []

        news_list = self.fetch_news()

        for news in news_list:

            try:

                content = news.get("content", {})

                title = content.get("title")
                summary = content.get("summary")
                publisher = content.get("provider", {}).get("displayName")
                url = content.get("canonicalUrl", {}).get("url")
                published = content.get("pubDate")

                if not url:
                    continue

                date, time = get_date_time(published)

                # Extract full article
                article_text = self.article_extractor.extract(url)
                
                # fallback to summary
                body = article_text if article_text else summary

                if not body:
                    continue

                page_content = f"""
                              {body}
                                """

                doc = Document(
                    page_content=page_content.strip(),
                    metadata={
                        "title": title,
                        "publisher": publisher,
                        "source": url,
                        "publisher": publisher,
                        "ticker": self.ticker,
                        "date": date,
                        "time": time,
                        "type": "news"
                    }
                )

                documents.append(doc)

            except Exception as e:
                print(f"Error processing article: {e}")

        return documents


if __name__ == "__main__":

    news_scraper = YahooFinanceNewsScraper("TCS.NS")

    news_documents = news_scraper.get_news_documents()

    print(news_documents)

    print("Total Documents:", len(news_documents))