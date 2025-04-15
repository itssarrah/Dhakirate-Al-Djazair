import pandas as pd
import numpy as np
from datetime import datetime
import random
from typing import List, Dict
from .config import Config

class EventsQuizManager:
    def __init__(self):
        # Load data with embeddings
        self.data = pd.read_pickle(Config.EVENTS_DATA_FILE)
        self.embeddings = np.vstack(self.data['embeddings'].apply(
            lambda x: np.array(x, dtype=np.float32)).values)

    def generate_quiz(self, educational_stage: str, solved_questions: List[Dict], num_questions: int = 5) -> List[Dict]:
        filtered_data = self.data[self.data['Educational stage'] == educational_stage]
        
        # Get indices of solved questions
        solved_indices = set()
        for solved in solved_questions:
            matching_rows = filtered_data[
                (filtered_data['Date'] == solved['date']) & 
                (filtered_data['Content'] == solved['event'])
            ].index
            solved_indices.update(matching_rows)

        # Generate new questions
        questions = []
        available_indices = list(set(filtered_data.index) - solved_indices)
        
        if len(available_indices) < num_questions:
            return []  # Not enough unique questions available

        selected_indices = random.sample(available_indices, num_questions)
        
        for idx in selected_indices:
            row = filtered_data.loc[idx]
            
            # If date contains hyphen (interval), force type 0 (date→event)
            # Otherwise randomly choose between type 0 and 1
            if '-' in str(row['Date']):
                question_type = 0
            else:   
                question_type = random.randint(0, 1)
            
            # Extract the first date for sorting (in case of intervals)
            sort_date = row['Date'].split('-')[0] if '-' in str(row['Date']) else row['Date']
            
            questions.append({
                'id': int(idx),
                'date': row['Date'],
                'event': row['Content'],
                'type': question_type,
                'sort_date': sort_date  # Add temporary field for sorting
            })
        
        # Sort questions by date
        def get_sort_key(q):
            date_str = q['sort_date']
            parts = date_str.split('/')
            # Handle different date formats
            if len(parts) == 3:  # Full date
                return datetime.strptime(date_str, '%Y/%m/%d')
            elif len(parts) == 2:  # Year and month
                return datetime.strptime(f"{date_str}/01", '%Y/%m/%d')
            else:  # Year only
                return datetime.strptime(f"{date_str}/01/01", '%Y/%m/%d')

        questions.sort(key=get_sort_key)
        
        # Remove the temporary sort_date field
        for q in questions:
            del q['sort_date']
            
        return questions

    def validate_date_answer(self, user_date: str, correct_date: str) -> bool:
        try:
            if len(user_date.split('/')) == 3 and len(correct_date.split('/')) < 3:
                return False

            if '-' in correct_date:  # Date range
                start_date_str, end_date_str = correct_date.split('-')
                start_date = datetime.strptime(start_date_str, '%Y/%m/%d')
                end_date = datetime.strptime(end_date_str, '%Y/%m/%d')
                user_date_obj = datetime.strptime(user_date, '%Y/%m/%d')
                return user_date_obj == start_date or user_date_obj == end_date

            # Exact date match
            if len(correct_date.split('/')) == 3:
                return user_date == correct_date

            # Year only
            return user_date.split('/')[0] == correct_date

        except ValueError:
            return False

    def validate_event_answer(self, user_answer: str, question_id: int, similarity_threshold: float = 0.82) -> bool:
        try:
            # Get the correct event's embedding
            correct_embedding = self.data.loc[question_id, 'embeddings']
            
            # Calculate similarity
            similarity = np.dot(user_answer, correct_embedding) / (
                np.linalg.norm(user_answer) * np.linalg.norm(correct_embedding)
            )
            print(f"Similarity: {similarity}")
            boole = bool(similarity > similarity_threshold)
            print(f"Bool: {boole}")
            # Convert numpy.bool_ to Python bool
            return bool(similarity > similarity_threshold)
        except:
            print("Error in validate_event_answer")

            return False
