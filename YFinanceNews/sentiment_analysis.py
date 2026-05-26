import torch
import re
import torch.nn.functional as F
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from langchain_core.documents import Document
from transformers import pipeline
from YFinanceNews.news_scraper import YahooFinanceNewsScraper
import warnings
warnings.filterwarnings('ignore')


def batch_documents(documents, batch_size=2):
    for i in range(0, len(documents), batch_size):
        yield documents[i:i + batch_size]

def clean_text(text: str):
    try:
        # Fix encoding issues
        text = text.encode("utf-8", "ignore").decode("utf-8")
        
        text = text.lower()
        # Replace common bad characters
        replacements = {
            "â€œ": '"',
            "â€": '"',
            "â€˜": "'",
            "â€™": "'",
            "â€“": "-",
            "â€”": "-",
            "â€¦": "...",
            "â€‹": " ",
            "\u00a0": " ",  # non-breaking space
            "\n": " ",
            "\n\n": " "
        }

        for bad, good in replacements.items():
            text = text.replace(bad, good)

        # Remove excessive quotes
        text = re.sub(r'"+', '"', text)

        # Remove URLs (optional but recommended)
        text = re.sub(r'http\S+', '', text)

        # Remove special characters (keep financial symbols)
        text = re.sub(r'[^A-Za-z0-9₹$€£.,:;!?()\'"\-\s]', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    except Exception as e:
        print(f"Text cleaning failed: {e}")
        return text



# Class for retrieving and processing 
# news text using the yfinance library.
class ReadDocuments:

    def __init__(self, ticker: str):
        self.ticker = ticker
    

    # Returns a list of generated documents 
    # along with their associated metadata.
    def read_news_docx(self):

        try:

            news_scraper = YahooFinanceNewsScraper(ticker=self.ticker)
            news_documents = news_scraper.get_news_documents()
            return news_documents
        
        except Exception as e:
            return e
        
# Implements the FinBERT model to perform News sentiment classification 
# into Positive, Negative, and Neutral categories.
class FinBERTSentiment(ReadDocuments):

    def __init__(self, model_name="ahmedrachid/FinancialBERT-Sentiment-Analysis", labels=3, allow_mismatch=True,label=None):

        super().__init__(ticker=label)
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=labels,
            ignore_mismatched_sizes=allow_mismatch
        )
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
    


    # Executes sentiment analysis on news content, 
    # handling two documents simultaneously for efficiency.
    def predict(self, max_length: int = 512, batch_size: int = 2):
        """
        Takes a list of Documents and returns enriched Documents with sentiment.
        """

        try:
            documents = self.read_news_docx() # get News Documents
            enriched_documents = list()
            
            # Process two Documents at a time
            for i in range(0, len(documents), batch_size):

                try:
                    batch_docs = documents[i:i + batch_size]
                    
                    # Cleaning the news text before passing it to the model
                    texts = [
                        clean_text(doc.page_content) if doc.page_content else ""
                        for doc in batch_docs
                    ]

                    batch = self.tokenizer(
                        text=texts,
                        padding=True,
                        truncation=True,
                        max_length=max_length,
                        return_tensors="pt"
                    )

                    with torch.no_grad():
                        outputs = self.model(**batch)
                        probs = F.softmax(outputs.logits, dim=1)
                        labels = torch.argmax(probs, dim=1)

                        label_names = [
                            self.model.config.id2label[i] for i in labels.tolist()
                        ]

                        scores = [float(p.max()) for p in probs]

                    for doc, label, score in zip(batch_docs, label_names, scores):

                        metadata = doc.metadata.copy() if doc.metadata else {}

                        metadata.update({
                            "sentiment": label,
                            "confidence": score
                        })

                        enriched_doc = Document(
                            page_content=clean_text(doc.page_content),
                            metadata=metadata
                        )
                        
                        # Returns a list of Documents with news text, Sentiment and confidence
                        # with the metadata while preserving the original Document Structure
                        enriched_documents.append(enriched_doc)

                except Exception as batch_error:
                    print(f"Error processing batch starting at index {i}: {str(batch_error)}")
                    continue

            return enriched_documents

        except Exception as e:
            raise RuntimeError(f"Sentiment analysis failed: {str(e)}")



if __name__ == "__main__":
    
    
    sentiment_analyzer = FinBERTSentiment(label="RELIANCE.NS")
    
    
    data_documents = sentiment_analyzer.predict()

    def documents_to_csv(documents, file_name="news_output.csv"):

        data = []

        for doc in documents:
            row = {
                "title": doc.metadata.get("title"),
                "publisher": doc.metadata.get("publisher"),
                "source": doc.metadata.get("source"),
                "ticker": doc.metadata.get("ticker"),
                "date": doc.metadata.get("date"),
                "time": doc.metadata.get("time"),
                "type": doc.metadata.get("type"),
                "sentiment": doc.metadata.get("sentiment"),
                "confidence": doc.metadata.get("confidence"),
                "content": doc.page_content  # full text
            }

            data.append(row)

        df = pd.DataFrame(data)

        df.to_csv(file_name, index=False)

        print(f"CSV saved as {file_name}")
    
    documents_to_csv(data_documents)