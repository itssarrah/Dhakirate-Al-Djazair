from typing import List, Dict
import numpy as np
import re
from .config import Config
from .ml_manager import MLManager
import pandas as pd

class QuizManager:
    def __init__(self, ml_manager: MLManager):
        self.ml_manager = ml_manager
        self.similarity_threshold = 0.86  # Exact value from quiz1.py
        self.temperatures = {
            'question_generation': 0.7,  # Medium-high for creative but focused questions
            'answer_generation': 0.3     # Lower for more controlled, accurate answers
        }

    def calculate_similarity(self, embedding1, embedding2):
        """Exactly as implemented in quiz1.py"""
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        return np.dot(embedding1, embedding2.T) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def filter_similar_content(self, level, educational_stage, answered_questions_embeddings, max_rows=25):
        """Exact implementation from quiz1.py"""
        data = self.ml_manager.get_data()
        relevant_data = data[
            (data['EducationalStage'] == educational_stage) & 
            (data['Level'] == level)
        ]

        if relevant_data.empty:
            relevant_data = data[data['EducationalStage'] == educational_stage]
        
        if relevant_data.empty:
            return pd.DataFrame()

        filtered_data = []
        relevant_data = relevant_data.sample(frac=1).reset_index(drop=True)
        
        for _, row in relevant_data.iterrows():
            context_embedding = np.array(row['Embeddings'])
            max_similarity = -1
            
            for answered_embedding in answered_questions_embeddings:
                similarity = self.calculate_similarity(context_embedding, answered_embedding)
                if similarity > max_similarity:
                    max_similarity = similarity

            if max_similarity < self.similarity_threshold:
                filtered_data.append(row)

            if len(filtered_data) >= max_rows:
                break

        return pd.DataFrame(filtered_data)

    def generate_quiz(self, educational_stage: str, level: int, answered_questions: List[str], num_questions: int = 5) -> List[Dict]:
        """Implementation exactly matching quiz1.py's generate_question_without_repeats"""
        try:
            answered_embeddings = [
                self.ml_manager.encode_text(q) for q in answered_questions
            ] if answered_questions else []

            filtered_data = self.filter_similar_content(
                level, 
                educational_stage, 
                answered_embeddings
            )
            
            if filtered_data.empty:
                return []

            # Add error handling for Content column
            contents = []
            for _, row in filtered_data.iterrows():
                try:
                    content = row['Content']
                    # Convert float or any other type to string
                    if not isinstance(content, str):
                        content = str(content)
                    contents.append(content)
                except Exception as e:
                    print(f"Error processing content: {e}")
                    continue
            # Skip if no valid contents found
            if not contents:
                return []
                
            combined_context = "\n".join(contents)
            # Limit context to 5000 words
            words = combined_context.split()
            combined_context = ' '.join(words[:500])


            # Enhanced question generation prompt that includes previously correct questions
            correct_questions_str = "\n".join(f"- {q}" for q in answered_questions) if answered_questions else "None"

            # Enhanced question generation prompt with educational stage complexity
            stage_complexity = {
                "PS": "Create very simple questions using basic vocabulary. Focus on direct facts and simple recall.",
                "JS": "Create clear questions with moderate complexity. Use straightforward historical concepts.",
                "HSS": "Create challenging questions that test understanding of historical concepts and relationships.",
                "HSL": "Create sophisticated questions that test analytical and critical thinking skills.",
                "UNI": "Create advanced questions that test deep historical understanding and interpretation."
            }

            stage_prefix = educational_stage[:2]
            complexity_guide = stage_complexity.get(stage_prefix, stage_complexity["JS"])


            question_messages = [
                {"role": "system", "content": f"""You are a history teacher creating quiz 
                questions in Arabic ONLY.
                {complexity_guide}
                Educational level: {educational_stage}

                Previously correctly answered questions:
                {correct_questions_str}

                Please generate {num_questions} NEW questions that are different from the above correctly answered questions and appropriate for this educational level."""},
                {"role": "user", "content": combined_context}
            ]

            questions = self.ml_manager.chat_completion(
                question_messages,
                temperature=self.temperatures['question_generation']
            ).strip()

            # Then generate options for the questions with improved prompt
            options_messages = [
                {"role": "system", "content": """You are a history teacher. Generate 3 possible answers for each question following these rules:
                1. Only 1 answer should be correct
                2. All options must be of similar length and detail level
                3. Wrong answers must be historically plausible but incorrect
                4. Avoid making the correct answer more detailed than others
                5. Each option should be 10-15 words maximum
                
                Format your response as the following for the 3 questions and do not write anything else:
                question <question>:
                - wrong: <wrong answer 1>
                - wrong: <wrong answer 2>
                - correct: <correct answer>
                Do the same for the other questions."""},
                {"role": "user", "content": f"Questions: {questions}\nContext: {combined_context}"}
            ]


            options = self.ml_manager.chat_completion(
                options_messages,
                temperature=self.temperatures['answer_generation']
                ).strip()
            quiz_questions = self._parse_questions([options])
            # check if parsing succeeded, else regenerate the answers for the questions for 3 attempts 

            if not quiz_questions:
                for _ in range(3):
                    options = self.ml_manager.chat_completion(options_messages, self.temperatures['answer_generation']).strip()
                    quiz_questions = self._parse_questions([options])
                    if quiz_questions:
                        break
            # Shuffle answers for each question
            for question in quiz_questions:
                self._shuffle_answers(question)
                
            return quiz_questions

        except Exception as e:
            print(f"Error generating quiz: {e}")
            return []

    def _shuffle_answers(self, question):
        """Shuffle the answers and update their indices."""
        answers = question['answers']
        np.random.shuffle(answers)
        
        # Update indices after shuffling
        for idx, answer in enumerate(answers):
            answer['index'] = idx
            
        question['answers'] = answers

    def _parse_questions(self, data):
        questions = []
        question_id = 1
        #clean all asterisks
        data = [re.sub(r'\*', '', block) for block in data]

        for block in data:
            # Split by question numbers (now handling Arabic numbers too)
            question_blocks = [q.strip() for q in re.split(r'\n\s*\d+\.\s+', block) if q.strip()]
            
            for question_block in question_blocks:
                try:
                    # Split into question and answers
                    parts = question_block.split('\n-', 1)
                    if len(parts) != 2:
                        continue

                    # Get question text (first line)
                    question_text = parts[0].strip()
                    options_text = '-' + parts[1]

                    # Extract answers
                    answers = []
                    option_matches = re.findall(r'-\s*(wrong|correct):\s*(.+?)(?=\n-|\n\d+\.|\Z)', options_text, re.DOTALL)
                    
                    if len(option_matches) != 3:
                        print(f"Wrong number of options for question {question_id}")
                        continue

                    for idx, (ans_type, ans_text) in enumerate(option_matches):
                        answers.append({
                            "optionLabel": ans_text.strip(),
                            "isCorrect": 1 if ans_type == "correct" else 0,
                            "index": idx
                        })

                    if answers and question_text:
                        questions.append({
                            "id": question_id,
                            "question": question_text,
                            "answers": answers
                        })
                        question_id += 1

                except Exception as e:
                    print(f"Error parsing question {question_id}: {str(e)}")
                    continue

        return questions

    def evaluate_answer(self, question_id: int, selected_option: int, quiz_data: List[Dict]) -> bool:
        try:
            question_id = int(question_id)
            selected_option = int(selected_option)
            
            question = next((q for q in quiz_data if q['id'] == question_id), None)
            if not question:
                print(f"Question not found for ID: {question_id}")
                return False

            # Find the selected answer
            selected_answer = next((ans for ans in question['answers'] 
                                 if ans['index'] == selected_option), None)
            
            if not selected_answer:
                print(f"No answer found with index {selected_option}")
                return False
                
            print(f"Debug - Selected answer: {selected_answer}")
            return selected_answer['isCorrect'] == 1

        except (ValueError, TypeError) as e:
            print(f"Error evaluating answer: {str(e)}")
            return False
