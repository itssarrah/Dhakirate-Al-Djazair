import json
import os
from typing import Dict, List

class PersonalityProgressManager:
    def __init__(self, progress_file: str = "personality_progress.json"):
        self.progress_file = progress_file
        self._load_progress()

    def _load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress_data = json.load(f)
        else:
            self.progress_data = {}
            self._save_progress()

    def _save_progress(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress_data, f, ensure_ascii=False, indent=4)

    def get_solved_questions(self, email: str, educational_stage: str) -> List[Dict]:
        return self.progress_data.get(email, {}).get(educational_stage, {}).get("solved_personalities", [])

    def update_progress(self, email: str, educational_stage: str, personality_id: int, data: Dict) -> Dict:
        if email not in self.progress_data:
            self.progress_data[email] = {}
            
        if educational_stage not in self.progress_data[email]:
            self.progress_data[email][educational_stage] = {
                "solved_personalities": [],
                "total_solved": 0,
                "total_attempts": 0,
                "correct_matches": 0
            }
            
        stage_data = self.progress_data[email][educational_stage]
        
        personality_data = {
            "Personality Name": data['name'],
            "Description": data['description'],
            "image_link": data['image_link']
        }
        
        if not any(p["Personality Name"] == data['name'] for p in stage_data["solved_personalities"]):
            stage_data["solved_personalities"].append(personality_data)
            stage_data["total_solved"] += 1
        
        stage_data["total_attempts"] += 1
        stage_data["correct_matches"] += 1
            
        self._save_progress()
        return {
            "total_solved": stage_data["total_solved"],
            "total_attempts": stage_data["total_attempts"],
            "correct_matches": stage_data["correct_matches"],
            "personalities": stage_data["solved_personalities"]
        }
