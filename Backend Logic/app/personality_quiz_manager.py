import pandas as pd
import numpy as np
from typing import List, Dict
import random
from .config import Config

class PersonalityQuizManager:
    def __init__(self):

        self.data = pd.read_pickle(Config.PERSONALITY_FILE)

    def generate_quiz(self, educational_stage: str, solved_questions: List[Dict], num_questions: int = 5) -> Dict:
        filtered_data = self.data[self.data['Educational stage'] == educational_stage]
        
        # Extract solved personality names
        solved_personality_names = [solved['Personality Name'] for solved in solved_questions]
        
        personalities = []
        descriptions = []
        counter = 0
        
        while len(personalities) < num_questions and counter < len(filtered_data):
            row = filtered_data.iloc[counter]
            personality_name = row['Personality Name']
            
            if personality_name not in solved_personality_names:
                personalities.append({
                    'id': counter,
                    'name': personality_name,
                    'image_link': row['image_link']
                })
                
                descriptions.append({
                    'id': counter,
                    'text': row['Content']
                })
                
            counter += 1
        
        random.shuffle(descriptions)
        
        return {
            'personalities': personalities,
            'descriptions': descriptions
        }

    def validate_answer(self, personality_id: int, description_id: int) -> bool:
        return personality_id == description_id
