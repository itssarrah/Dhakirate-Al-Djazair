import json
import os
from typing import Dict, List
import logging

class ProgressManager:
    def __init__(self, progress_file: str = "progress.json"):
        self.progress_file = os.path.abspath(progress_file)
        self.MAX_LEVELS = 3
        self.MAX_HISTORY = 10
        logging.info(f"Initializing ProgressManager with file: {self.progress_file}")
        self._load_progress()

    def _load_progress(self):
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    self.progress_data = json.load(f)
                    logging.info(f"Successfully loaded progress data with {len(self.progress_data)} users")
            else:
                logging.warning(f"Progress file not found at {self.progress_file}, creating new file")
                self.progress_data = {}
                self._save_progress()
        except Exception as e:
            logging.error(f"Error loading progress data: {str(e)}")
            self.progress_data = {}
    
    def _save_progress(self):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=4)
                logging.info("Successfully saved progress data")
        except Exception as e:
            logging.error(f"Error saving progress data: {str(e)}")

    def get_user_progress(self, email: str, educational_stage: str, level: int) -> dict:
        if email not in self.progress_data:
            return {"progress": 0, "answered_questions": [], "total_correct": 0, "total_incorrect": 0}

        user_data = self.progress_data[email]
        stage_data = user_data.get(educational_stage, {})
        level_data = stage_data.get(
            str(level), {"progress": 0, "answered_questions": [], "total_correct": 0, "total_incorrect": 0})

        return level_data

    def get_stage_progress(self, email: str, educational_stage: str) -> dict:
        """Get progress for all levels in a given educational stage"""
        try:
            progress_by_level = {str(i): {"progress": 0, "mastery": 0} for i in range(1, self.MAX_LEVELS + 1)}
            
            if email in self.progress_data and educational_stage in self.progress_data[email]:
                stage_data = self.progress_data[email][educational_stage]
                logging.info(f"Found progress data for {email} in stage {educational_stage}")
                
                for level_str in progress_by_level.keys():
                    level_progress = stage_data.get(level_str, {}).get('progress', 0)
                    mastery_stats = self.get_mastery_stats(email, educational_stage, int(level_str))
                    
                    progress_by_level[level_str] = {
                        "progress": level_progress,
                        "mastery_score": mastery_stats["mastery_score"],
                        "total_correct": mastery_stats["total_correct"],
                        "questions_attempted": mastery_stats["questions_attempted"]
                    }
                        
            return progress_by_level
            
        except Exception as e:
            logging.error(f"Error getting stage progress: {str(e)}")
            return {str(i): {"progress": 0, "mastery": 0} for i in range(1, self.MAX_LEVELS + 1)}

    def get_incorrect_questions(self, email: str, educational_stage: str, level: int) -> List[str]:
        """Get list of incorrectly answered questions for retaking."""
        if email not in self.progress_data:
            return []
            
        user_data = self.progress_data[email]
        if educational_stage not in user_data or str(level) not in user_data[educational_stage]:
            return []
            
        level_data = user_data[educational_stage][str(level)]
        return level_data.get("incorrect_questions", [])

    def calculate_level_progress(self, email: str, educational_stage: str, level: int) -> float:
        """Calculate the overall progress for a specific level."""
        try:
            level_data = self.get_user_progress(email, educational_stage, level)
            total_questions = level_data.get('total_questions_seen', 0)
            correct_answers = level_data.get('total_correct', 0)
            
            if total_questions == 0:
                return 0
                
            # Calculate progress based on both accuracy and number of questions
            base_progress = correct_answers * 10 
            return min(100, base_progress)
        except Exception as e:
            logging.error(f"Error calculating level progress: {str(e)}")
            return 0

    def update_progress(self, email: str, educational_stage: str, level: int, question: str, is_correct: bool):
        if email not in self.progress_data:
            self.progress_data[email] = {}

        if educational_stage not in self.progress_data[email]:
            self.progress_data[email][educational_stage] = {}

        if str(level) not in self.progress_data[email][educational_stage]:
            self.progress_data[email][educational_stage][str(level)] = {
                "progress": 0,
                "answered_questions": [],
                "incorrect_questions": [],
                "total_correct": 0,
                "total_incorrect": 0
            }

        level_data = self.progress_data[email][educational_stage][str(level)]
        
        # Initialize incorrect_questions if it doesn't exist
        if "incorrect_questions" not in level_data:
            level_data["incorrect_questions"] = []

        # Handle the question result
        if is_correct:
            if question in level_data["incorrect_questions"]:
                level_data["incorrect_questions"].remove(question)
                level_data["total_incorrect"] -= 1
            if question not in level_data["answered_questions"]:
                level_data["answered_questions"].append(question)
                level_data["total_correct"] += 1
        else:
            if question not in level_data["incorrect_questions"]:
                level_data["incorrect_questions"].append(question)
                level_data["total_incorrect"] += 1

        # Update total questions seen
        if 'total_questions_seen' not in level_data:
            level_data['total_questions_seen'] = 0
        level_data['total_questions_seen'] += 1

        # Calculate the new progress
        new_progress = self.calculate_level_progress(email, educational_stage, level)
        level_data['progress'] = new_progress

        # Add timestamp and quiz history
        from datetime import datetime
        quiz_entry = {
            "question": question,
            "correct": is_correct,
            "timestamp": datetime.now().isoformat(),
            "level": level
        }
        
        if "quiz_history" not in level_data:
            level_data["quiz_history"] = []
            
        level_data["quiz_history"].insert(0, quiz_entry)
        level_data["quiz_history"] = level_data["quiz_history"][:self.MAX_HISTORY]

        self._save_progress()
        return {
            "progress": new_progress,
            "total_correct": level_data["total_correct"],
            "total_incorrect": level_data["total_incorrect"],
            "incorrect_questions": level_data["incorrect_questions"],
            "total_questions_seen": level_data["total_questions_seen"]
        }

    def get_user_stats(self, email: str, educational_stage: str = None) -> dict:
        """Get detailed statistics for a user"""
        stats = {
            "total_questions_answered": 0,
            "total_correct": 0,
            "total_incorrect": 0,
            "accuracy": 0,
            "levels_completed": 0,
            "stages_progress": {}
        }
        
        if email not in self.progress_data:
            return stats
            
        user_data = self.progress_data[email]
        
        if educational_stage:
            stages = [educational_stage] if educational_stage in user_data else []
        else:
            stages = user_data.keys()
            
        for stage in stages:
            stage_data = user_data[stage]
            stage_stats = {
                "progress": 0,
                "levels": {}
            }
            
            for level, level_data in stage_data.items():
                total_questions = len(level_data.get("quiz_history", []))
                correct_answers = level_data.get("total_correct", 0)
                incorrect_answers = level_data.get("total_incorrect", 0)
                
                stage_stats["levels"][level] = {
                    "progress": level_data.get("progress", 0),
                    "total_questions": total_questions,
                    "correct_answers": correct_answers,
                    "incorrect_answers": incorrect_answers,
                    "accuracy": (correct_answers / total_questions * 100) if total_questions > 0 else 0
                }
                
                if level_data.get("progress", 0) == 100:
                    stats["levels_completed"] += 1
                    
                stats["total_questions_answered"] += total_questions
                stats["total_correct"] += correct_answers
                stats["total_incorrect"] += incorrect_answers
            
            stage_stats["progress"] = sum(l["progress"] for l in stage_stats["levels"].values()) / len(stage_stats["levels"])
            stats["stages_progress"][stage] = stage_stats
            
        stats["accuracy"] = (stats["total_correct"] / stats["total_questions_answered"] * 100) if stats["total_questions_answered"] > 0 else 0
        
        return stats

    def get_answered_questions(self, email: str, educational_stage: str, level: int) -> List[str]:
        level_data = self.get_user_progress(email, educational_stage, level)
        return level_data.get("answered_questions", [])

    def get_mastery_stats(self, email: str, educational_stage: str, level: int) -> dict:
        """Get mastery statistics for a specific level"""
        if email not in self.progress_data:
            return {"total_correct": 0, "questions_attempted": 0, "mastery_score": 0}

        user_data = self.progress_data[email]
        stage_data = user_data.get(educational_stage, {})
        level_data = stage_data.get(str(level), {})

        total_correct = level_data.get('total_correct', 0)
        total_questions = level_data.get('total_questions_seen', 0)
        
        # Calculate mastery score (can go beyond 100)
        mastery_score = total_correct * 10  # Each correct answer adds 10 points

        return {
            "total_correct": total_correct,
            "questions_attempted": total_questions,
            "mastery_score": mastery_score
        }
