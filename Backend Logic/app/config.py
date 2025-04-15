import os


class Config:
    SECRET_KEY = 'your_secret_key'
    # GROQ_API_KEY = "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"
    GROQ_API_KEY = "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"

    # Paths
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, '..', 'models')
    # MODELS_DIR = '/media/moon/linu/models'
    EMBEDDINGS_DIR = os.path.join(BASE_DIR, '..', 'embeddings')

    # Model configurations
    SENTENCE_TRANSFORMER_MODEL = 'Alibaba-NLP/gte-multilingual-base'
    LOCAL_MODEL_PATH = os.path.join(MODELS_DIR, 'gte-multilingual-base')
    EMBEDDINGS_FILE = os.path.join(
        EMBEDDINGS_DIR, 'merged_data_with_alibaba_embeddings.pkl')
    PERSONALITY_FILE = os.path.join(EMBEDDINGS_DIR, 'person_embeddings.pkl')
    EVENTS_DATA_FILE = os.path.join(EMBEDDINGS_DIR, 'dates_events_with_embeddings.pkl')
    FAISS_INDEX_FILE = os.path.join(EMBEDDINGS_DIR, 'faiss_index.pkl')

    # Caching configuration
    RESPONSE_CACHE_SIZE = 1000
    EMBEDDING_CACHE_SIZE = 5000

    # Performance settings
    GPU_ENABLED = True  # Will fallback to CPU if GPU is not available
    MAX_WORKERS = 4     # Number of thread workers for concurrent operations
