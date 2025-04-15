import json
import os
from typing import Dict, List

class EventsProgressManager:
    def __init__(self, progress_file: str = "events_progress.json"):
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
        return self.progress_data.get(email, {}).get(educational_stage, {}).get("solved_questions", [])

    def update_progress(self, email: str, educational_stage: str, question_data: Dict, is_correct: bool) -> Dict:
        if email not in self.progress_data:
            self.progress_data[email] = {}
            
        if educational_stage not in self.progress_data[email]:
            self.progress_data[email][educational_stage] = {
                "solved_questions": [],
                "total_attempts": 0,
                "correct_answers": 0
            }
            
        progress = self.progress_data[email][educational_stage]
        
        if is_correct:
            progress["correct_answers"] += 1
            progress["solved_questions"].append({
                "date": question_data["date"],
                "event": question_data["event"]
            })
            
        progress["total_attempts"] += 1
        
        self._save_progress()
        return progress
