import uuid
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from arabicStemmer import Arabic_stemmer
from tashaphyne.stemming import ArabicLightStemmer
import re
from datetime import datetime
import json
import pandas as pd
import pickle
from groq import Groq
from typing import Dict, List
import os

os.environ["GROQ_API_KEY"] = "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"

DEFAULT_MODEL = "gemma2-9b-it"

client = Groq()


def chat_completion(
    messages: List[Dict],
    model=DEFAULT_MODEL,
    temperature: float = 0.5,
    top_p: float = 0.9,
) -> str:
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        top_p=top_p,
    )
    return response.choices[0].message.content


def clean_arabic_content(text):
    # Remove English letters
    # text = re.sub(r'[a-zA-Z]+', '', text)

    # Remove non-Arabic characters and symbols while keeping digits
    text = re.sub(r'[^\u0600-\u06FF\s0-9]', '', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing spaces
    text = text.strip()

    return text

# get the row of one topic 
def getTopic(topic, data, educational_stage):
    data = data[data['EducationalStage'] == educational_stage]
    return data[data['Topic'] == topic]
    
def combine_embeddings(question_embedding, history_embeddings, current_weight=0.7):
    """
    Combines the current question embedding with history embeddings using weights.
    Current question gets higher weight to maintain focus while history adds context.
    """
    if not history_embeddings:
        return question_embedding
        
    history_embedding = np.mean(history_embeddings, axis=0)
    history_weight = 1 - current_weight
    
    combined = (current_weight * question_embedding + history_weight * history_embedding)
    # Normalize the combined embedding
    combined = combined / np.linalg.norm(combined)
    return combined

def relevantContent(question, model, data, history=None, educationalStage=None, historicalEra=None, max_words=1000, similarity_threshold=55):
    """
    Get relevant content based on the user's query and conversation history.
    
    Parameters:
    - question: The user's question (string)
    - model: The sentence transformer model used for embedding
    - data: DataFrame containing content, topics, and embeddings
    - history: List of previous Q&A pairs
    - educationalStage: Optional, the educational stage to filter by
    - historicalEra: Optional, the historical era to filter by
    - max_words: Maximum number of words to collect (default: 1000)
    - similarity_threshold: Minimum similarity score to consider content relevant (default: 55)
    """
    # Initial filtering
    data = data.dropna(subset=['Content'])
    filtered_data = data[data['Content'].notnull()]
    if educationalStage:
        filtered_data = filtered_data[filtered_data['EducationalStage'] == educationalStage]
    if historicalEra and not filtered_data.empty and historicalEra != 'None':
        filtered_data = filtered_data[filtered_data['HistoricalEra'] == historicalEra]

    if filtered_data.empty:
        return []

    # use the Arabic stemmer to stem the question
    ArListem = ArabicLightStemmer()
    question = ' '.join(ArListem.light_stem(x) for x in question.split())

    # Get embeddings for current question and history
    question_embedding = model.encode([question])
    
    # Process history to maintain context
    history_embeddings = []
    if history:
        # Get last 2 Q&A pairs for context
        recent_history = history[-2:] if len(history) > 2 else history
        for entry in recent_history:
            # Combine question and answer to capture full context
            history_text = f"{entry['question']} {entry['answer']}"
            history_embeddings.append(model.encode([history_text])[0])
    
    # Combine current question embedding with history context
    combined_embedding = combine_embeddings(question_embedding[0], history_embeddings)
    combined_embedding = combined_embedding.reshape(1, -1)

    # Normalize embeddings
    embedding_matrix = np.vstack(filtered_data['Embeddings'].to_numpy())
    embedding_matrix = embedding_matrix / np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
    
    # Create FAISS index
    index = faiss.IndexFlatIP(embedding_matrix.shape[1])
    index.add(embedding_matrix.astype('float32'))
    
    # Search with combined embedding
    D, I = index.search(combined_embedding.astype('float32'), 20)

    # Collect content until reaching maximum word count
    top_results = []
    total_words = 0
    
    for idx, similarity in zip(I[0], 100 * D[0]):
        if similarity >= similarity_threshold:
            content = filtered_data.iloc[idx]['Content']
            if content and str(content) != 'nan':
                content_words = str(content).split()
                words_remaining = max_words - total_words
                
                if len(content_words) <= words_remaining:
                    top_results.append(str(content))
                    total_words += len(content_words)
                else:
                    truncated_content = ' '.join(content_words[:words_remaining])
                    if not truncated_content.endswith('.'):
                        truncated_content += '.'
                    top_results.append(truncated_content)
                    total_words = max_words
                    break
    
    return top_results

def answer_question_with_relevant_content_GN(email, query, session_manager, data, model, session_nonce, EducationalStage=None, HistoricalEra=None, Topic=None):
    session = session_manager.get_session(email, session_nonce)
    history = session["content"] if session else []
    history_text = "\n".join([f"Q: {entry['question']}\nA: {entry['answer']}" for entry in history])

    if Topic is not None:
        relevant_content = getTopic(Topic, data, EducationalStage)
        relevant_content = relevant_content['Content'].values[0]
    else:
        # Get relevant content using both query and history
        relevant_content_results = relevantContent(
            query, 
            model, 
            data, 
            history=history,  # Pass conversation history
            educationalStage=EducationalStage, 
            historicalEra=HistoricalEra
        )
        
        relevant_content = "\n".join(relevant_content_results) if relevant_content_results else ""

    # Construct the prompt with both content and history
    prompt = f"""
    Relevant Context:
    {relevant_content}
    
    History of Q&A:
    {history_text}

    Current Question: {query}
    Answer:
    """

    # Enhanced system message with educational stage complexity guidance
    stage_complexity = {
        "PS": "Use simple vocabulary and short sentences. Explain concepts in very basic terms. Avoid complex historical terms.",
        "JS": "Use moderate vocabulary with clear explanations. Define any complex terms. Keep sentences straightforward.",
        "HSS": "Use academic vocabulary with detailed explanations. Include historical context and connections.",
        "HSL": "Use sophisticated vocabulary and complex analysis. Include historical debates and interpretations.",
        "UNI": "Use advanced academic language with scholarly depth. Include historiographical perspectives."
    }

    # Determine complexity level from educational stage
    stage_prefix = EducationalStage[:2] if EducationalStage else "JS"  # Default to JS level if none specified
    complexity_guide = stage_complexity.get(stage_prefix, stage_complexity["JS"])


    messages = [
        {"role": "system", "content": f"""You are an AI history teacher answering questions in Arabic.
            {complexity_guide}
            Provide structured responses specifically tailored for {EducationalStage} level students.
            Focus on clarity and appropriate examples for this educational level."""},
        {"role": "user", "content": prompt}
    ]

    # Get response from the model
    response = chat_completion(messages, model=DEFAULT_MODEL)

    # Save the interaction using session manager
    session_manager.add_to_session(
        email, EducationalStage, session_nonce, query, response)

    return response
