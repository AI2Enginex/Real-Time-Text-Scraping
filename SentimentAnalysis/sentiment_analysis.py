import torch
import re
import torch.nn.functional as F
import os
from itertools import islice
from transformers import BertTokenizer, BertForSequenceClassification
from langchain_core.documents import Document
from MongoDBManager.pymongo_conn import MongoDBManagerClass
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')


# Implements the FinBERT model to perform News sentiment classification 
# into Positive, Negative, and Neutral categories.
class FinBERTSentiment():

    def __init__(self, model_name="ahmedrachid/FinancialBERT-Sentiment-Analysis", labels=3, allow_mismatch=True,label=None):

        # Load the FinBERT model and tokenizer. The model is set to evaluation mode to disable dropout and other training-specific layers.
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=labels,
            ignore_mismatched_sizes=allow_mismatch
        )
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model.eval()

    # Batch the documents for processing. Creates an iterator that yields batches of documents of a specified size.
    @staticmethod
    def batch_documents(documents, batch_size=2):
        while True:
            batch = list(islice(documents, batch_size))
            if not batch:
                return
            yield batch

    # Clean the text by fixing encoding issues, replacing bad characters, removing URLs and special characters, and normalizing whitespace.
    @staticmethod
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
            return re.sub(r'\s+', ' ', text).strip()

        except Exception as e:
            print(f"Text cleaning failed: {e}")
            return text

    # Predict sentiment for a list of texts. Tokenizes the texts, runs them through the model,
    #  and returns the predicted sentiment labels and confidence scores.
    def predict_texts(self, texts, max_length: int = 512, batch_size: int = 2):
        """Return a sentiment label and confidence score for each text."""
        predictions = []

        for i in range(0, len(texts), batch_size):
            batch_texts = [self.clean_text(text or "") for text in texts[i:i + batch_size]]
            batch = self.tokenizer(
                text=batch_texts,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt"
            )

            with torch.no_grad():
                outputs = self.model(**batch)
                probabilities = F.softmax(outputs.logits, dim=1)
                labels = torch.argmax(probabilities, dim=1)

            predictions.extend(
                {
                    "sentiment": self.model.config.id2label[label_index],
                    "score": float(probabilities[row_index, label_index])
                }
                for row_index, label_index in enumerate(labels.tolist())
            )

        return predictions

    # Analyze news in a MongoDB collection in batches, predict sentiment, and upsert results into another collection.
    def analyze_moneycontrol_news(
        self,
        db_name: str,
        source_collection: str = "moneycontrol_news",
        target_collection: str = "sentiment_analysis",
        max_length: int = 512,
        collection_batch_size: int = 4,
        model_batch_size: int = 2,
    ):
        """Analyze news in collection batches and upsert results into MongoDB."""

        # Initialize MongoDB connections for source and target collections.
        source_db = MongoDBManagerClass(
            db_name=db_name,
            collection_name=source_collection
        )
        target_db = MongoDBManagerClass(
            db_name=db_name,
            collection_name=target_collection
        )

        processed = 0 # Count of processed documents
        try:

            # Get already processed source_ids and legacy keys to avoid reprocessing.
            # This ensures that documents already analyzed are not processed again, preventing duplicates in the target collection.
            processed_source_ids = {
                document["source_id"]
                for document in target_db.collection.find(
                    {"source_id": {"$exists": True}},
                    {"_id": 0, "source_id": 1}
                )
            }

            # Get legacy keys (title, date_time, text) for documents without source_id to avoid duplicates.
            processed_legacy_keys = {
                (
                    document.get("title", ""),
                    document.get("date_time", ""),
                    document.get("text", "")
                )
                for document in target_db.collection.find(
                    {"source_id": {"$exists": False}},
                    {"_id": 0, "title": 1, "date_time": 1, "text": 1}
                )
            }

            # Fetch documents from the source collection that have a text field of type string.
            documents = source_db.collection.find(
                {"text": {"$exists": True, "$type": "string"}},
                {"_id": 1, "title": 1, "date_time": 1, "text": 1}
            )

            new_documents = (
                document for document in documents
                if document["_id"] not in processed_source_ids
                and (
                    document.get("title", ""),
                    document.get("date_time", ""),
                    document["text"]
                ) not in processed_legacy_keys
            )

            # Process the new documents in batches, predict sentiment, and upsert results into the target collection.
            for source_batch in self.batch_documents(new_documents, collection_batch_size):
                predictions = self.predict_texts(
                    [document["text"] for document in source_batch],
                    max_length=max_length,
                    batch_size=model_batch_size
                )

                for document, prediction in zip(source_batch, predictions):
                    result = {
                        "source_id": document["_id"],
                        "title": document.get("title", ""),
                        "date_time": document.get("date_time", ""),
                        "text": document["text"],
                        **prediction
                    }
                    target_db.collection.update_one(
                        {"source_id": result["source_id"]},
                        {"$set": result},
                        upsert=True
                    )
                    processed += 1

            return processed
        finally:
            source_db.close_conn()
            target_db.close_conn()
    


if __name__ == "__main__":

    load_dotenv()

    sentiment_analyzer = FinBERTSentiment()
    processed_count = sentiment_analyzer.analyze_moneycontrol_news(
        db_name=os.getenv("DATABASE", "Vibhor"),
        source_collection=os.getenv("NEWS_COLLECTION", "moneycontrol_news"),
        target_collection=os.getenv("SENTIMENT_COLLECTION", "sentiment_analysis"),
        collection_batch_size=4,
        model_batch_size=2
    )
    print(f"Processed {processed_count} news documents.")