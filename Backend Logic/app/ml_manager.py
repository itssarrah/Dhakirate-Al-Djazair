from sentence_transformers import SentenceTransformer
from groq import Groq
import pickle
import faiss
import numpy as np
import os
from functools import lru_cache
from typing import Dict, List

from .config import Config


class MLManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLManager, cls).__new__(cls)
            # Load everything in memory on first initialization
            if not os.path.exists(Config.LOCAL_MODEL_PATH):
                print(f"Model not found at {Config.LOCAL_MODEL_PATH}, downloading...")
                # First create the directory if it doesn't exist
                os.makedirs(os.path.dirname(Config.LOCAL_MODEL_PATH), exist_ok=True)
                # Download and save the model
                temp_model = SentenceTransformer(Config.SENTENCE_TRANSFORMER_MODEL, trust_remote_code=True)
                temp_model.save(Config.LOCAL_MODEL_PATH)
                print("Model downloaded and saved successfully!")

            print("Loading model from:", Config.LOCAL_MODEL_PATH)
            cls._instance.embedding_model = SentenceTransformer(
                Config.LOCAL_MODEL_PATH,
                trust_remote_code=True
            )
            print("Model loaded successfully!")

            # Initialize Groq client
            cls._instance.groq_client = Groq(api_key=Config.GROQ_API_KEY)
            cls._instance.DEFAULT_MODEL = "gemma2-9b-it"

            # Load data and create index
            print("Loading embeddings data from:", Config.EMBEDDINGS_FILE)
            # print if path exists
            with open(Config.EMBEDDINGS_FILE, 'rb') as f:
                cls._instance.data = pickle.load(f)

            # # Build index in memory
            # print("Building FAISS index...")
            # vectors = np.vstack(cls._instance.data['Embeddings'].to_numpy())
            # cls._instance.faiss_index = faiss.IndexFlatL2(vectors.shape[1])
            # cls._instance.faiss_index.add(vectors.astype('float32'))

            cls._instance.cache = {}
            print("MLManager initialization complete!")
        return cls._instance

    def chat_completion(self, messages: List[Dict], temperature: float = 0.5, top_p: float = 0.9) -> str:
        """Execute chat completion using Groq"""
        response = self.groq_client.chat.completions.create(
            messages=messages,
            model=self.DEFAULT_MODEL,
            temperature=temperature,
            top_p=top_p,
        )
        return response.choices[0].message.content

    @lru_cache(maxsize=5000)
    def encode_text(self, text):
        return self.embedding_model.encode(text)

    def get_cached_response(self, question):
        return self.cache.get(question)

    def cache_response(self, question, response):
        self.cache[question] = response

    def get_model(self):
        return self.embedding_model

    def get_data(self):
        return self.data

    def get_faiss_index(self):
        return self.faiss_index
