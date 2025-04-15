
# %%
import pprint
from typing import List
import json
import random
from groq import Groq
from typing import Dict, List
import os
from tashaphyne.stemming import ArabicLightStemmer
import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import pickle

# Load the data from the pickle file
data = pd.read_pickle('data_with_alibaba_embeddings.pkl')


# %%
data


model_name = "Alibaba-NLP/gte-multilingual-base"
embedding_model = SentenceTransformer(model_name, trust_remote_code=True)

# %%
# function to clean the query


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


# %%

# Load the embeddnig
embedding_matrix = np.vstack(data['Embeddings'].to_numpy())
index = faiss.IndexFlatL2(embedding_matrix.shape[1])
index.add(embedding_matrix)

# Example query function to retrieve relevant historical content


def query_history(query_text, model, index, data, top_k=3):
    # Stem and embed the query
    query_text = clean_arabic_content(query_text)
    ArListem = ArabicLightStemmer()
    stemmed_query = ' '.join([ArListem.light_stem(word)
                             for word in query_text.split()])
    query_embedding = model.encode([stemmed_query])

    # search for top relevant docs
    distances, indices = index.search(query_embedding, top_k)

    results = [
        {
            'HistoricalEra': data.iloc[idx]['HistoricalEra'],
            'Topic': data.iloc[idx]['Topic'],
            'Content': data.iloc[idx]['Content']
        }
        for idx in indices[0]
    ]
    return results


# Test with a sample query
sample_query = "التخطيط للإستيلاء على القواعد العسكرية البحرية"
result = query_history(sample_query, embedding_model, index, data)
print(result)


# Get a free API key from https://console.groq.com/keys
os.environ["GROQ_API_KEY"] = "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"

DEFAULT_MODEL = "gemma2-9b-it"

client = Groq()

# def assistant(content: str):
#     return { "role": "assistant", "content": content }

# def user(content: str):
#     return { "role": "user", "content": content }


def chat_completion(
    messages: List[Dict],
    model=DEFAULT_MODEL,
    temperature: float = 0.2,
    top_p: float = 0.9,
) -> str:
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        top_p=top_p,
    )
    return response.choices[0].message.content


def completion(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    top_p: float = 0.9,
) -> str:
    return chat_completion(
        prompt,
        model=model,
        temperature=temperature,
        top_p=top_p,
    )


def complete_and_print(prompt: str, model: str = DEFAULT_MODEL):
    print(f'==============\n{prompt}\n==============')
    response = completion(prompt, model)
    print(response, end='\n\n')


# %%
# Generate question based on the context using the model
def generate_question(educational_stage, level, data):
    """Generates a question based on the educational stage and historical era."""

    # Step 1: Retrieve relevant data based on the provided educational stage and level
    relevant_data = data[(data['EducationalStage'] ==
                          educational_stage) & (data['Level'] == level)]
    if relevant_data.empty:
        print(f"No relevant content found for EducationalStage: {
              educational_stage} with level: {level}.")

    questions = []
    for _, row in relevant_data.iterrows():
        context = row['Content']

        # Use the model to generate a question based on the content
        messages = [
            {"role": "system", "content": "You are a history teacher answering questions in Arabic. In the context of Algerian history, you will be given a context, and you need to analyze it and generate a question for a quiz. only provide the question in arabic."},
            {"role": "user", "content": context}
        ]

        # Generate question using the model
        question = chat_completion(messages)
        questions.append((question.strip(), context))

    return questions


educational_stage = "HSS3"
level = 1
questions = generate_question(educational_stage, level, data)

for q, c in questions:
    print(f"Question: {q}\nContext: {c}\n")

# %%


def generate_question_with_options(educational_stage, level, data, num_of_questions=3):
    """Generates questions with 3 options (2 wrong, 1 correct) based on the educational stage, historical era, and the number of questions."""

    # Step 1: Retrieve relevant data based on the provided educational stage and level
    relevant_data = data[(data['EducationalStage'] ==
                          educational_stage) & (data['Level'] == level)]
    if relevant_data.empty:
        print(f"No relevant content found for EducationalStage: {
              educational_stage} with level: {level}.")
        return []  # Return an empty list if no relevant data is found

    # Limit the number of rows to 3
    # Randomly sample 3 rows (or fewer if there aren't enough)
    relevant_data = relevant_data.sample(min(3, len(relevant_data)))

    # Step 2: Concatenate all the content from the 3 rows
    combined_context = "\n".join(row['Content']
                                 for _, row in relevant_data.iterrows())

    # Step 3: Generate questions and options based on the combined context
    questions_with_options = []

    # Generate the question using the combined context
    messages = [
        {"role": "system", "content": f"You are a history teacher answering questions in Arabic. In the context of Algerian history, you will be given a context, and you need to analyze it and generate a question for a quiz. Only provide the question in Arabic. Generate {num_of_questions} questions."},
        {"role": "user", "content": combined_context}
    ]

    question = chat_completion(messages).strip()

    # Now generate 3 options: 1 correct and 2 wrong answers
    options_messages = [
        {"role": "system", "content": "You are a history teacher. You will generate 3 possible answers for the question. Only 1 answer is correct, the other two are wrong. Ensure that the correct answer is factually accurate, while the wrong answers should be plausible but incorrect. Provide the options in Arabic in the following format:\nquestion 1:\n- wrong: <wrong answer 1>\n- wrong: <wrong answer 2>\n- correct: <correct answer>\nDo the same for the other questions. Make sure the options have almost the same length."},
        {"role": "user", "content": f"Question: {
            question}\nContext: {combined_context}"}
    ]

    options = chat_completion(options_messages).strip()

    # Append the question with options to the list
    questions_with_options.append(options)

    return questions_with_options


# Example usage:
educational_stage = "HSS3"
level = 1
num_of_questions = 5
questions_with_options = generate_question_with_options(
    educational_stage, level, data, num_of_questions)

# Displaying the results
for options in questions_with_options:
    print(options)
    print("\n")

# Simulate student data (for the sake of demonstration, assume it's loaded from a real JSON file)
with open('students.json', 'r') as file:
    student_data = json.load(file)

# Extract questions the student has already answered


def extract_answered_questions(student_data, email, educational_stage, level):
    answered_questions = []

    # Check if the student exists in the data
    if email not in student_data:
        print(f"No data found for student with email: {email}")
        return answered_questions

    student_info = student_data[email]

    # Check if the educational stage exists for the student
    if educational_stage not in student_info:
        print(f"No data found for educational stage: {educational_stage}")
        return answered_questions

    # Traverse the quizzes in the educational stage
    for quiz_name, quiz_data in student_info[educational_stage].items():
        for question_set in quiz_data:
            if isinstance(question_set, dict):  # Ensure it's a dictionary
                for key, questions in question_set.items():
                    if key == level:  # Check if the level matches
                        for question in questions:
                            if "question" in question:
                                answered_questions.append(question["question"])

    return answered_questions


# Example usage
email = "student1@gmail.com"
educational_stage = "HSS3"
level = "1"

answered_questions = extract_answered_questions(
    student_data, email, educational_stage, level)
print(f"Answered Questions: {answered_questions}")

# %%
# Approach 1: Generate questions with instructions to avoid repeats


def generate_question_with_instructions(educational_stage, level, data, answered_questions, num_of_questions=3):
    """Generates questions with instructions to avoid repeating previously answered ones."""

    # Step 1: Retrieve relevant data based on the provided educational stage and level
    relevant_data = data[(data['EducationalStage'] ==
                          educational_stage) & (data['Level'] == level)]
    if relevant_data.empty:
        print(f"No relevant content found for EducationalStage: {
              educational_stage} with level: {level}.")
        return []  # Return an empty list if no relevant data is found

    # Limit the number of rows to 6
    relevant_data = relevant_data.sample(min(6, len(relevant_data)))
    # Step 2: Concatenate all the content from the relevant rows
    combined_context = "\n".join(row['Content']
                                 for _, row in relevant_data.iterrows())

    # Step 3: Generate questions and options based on the combined context
    questions_with_options = []

    # Instruction to the model to avoid repeating questions that the student has already answered
    instructions = f"Avoid generating questions that are similar or identical to the following:\n{
        answered_questions}\n"

    # Generate the questions using the combined context, while telling the model not to repeat answered questions
    messages = [
        {"role": "system", "content": f"You are a history teacher answering questions in Arabic. In the context of Algerian history, you will be given a context, and you need to analyze it and generate {
            num_of_questions} questions for a quiz. Only provide the questions in Arabic. {instructions}"},
        {"role": "user", "content": combined_context}
    ]

    questions = chat_completion(messages).strip()

    # Generate options for each question
    options_messages = [
        {"role": "system", "content": "You are a history teacher. You will generate 3 possible answers for each question. Only 1 answer is correct, the other two are wrong. Ensure that the correct answer is factually accurate, while the wrong answers should be plausible but incorrect. Provide the options in Arabic in the following format:\nquestion 1:\n- wrong: <wrong answer 1>\n- wrong: <wrong answer 2>\n- correct: <correct answer>\nDo the same for the other questions. Make sure the options have almost the same length."},
        {"role": "user", "content": f"Questions: {
            questions}\nContext: {combined_context}"}
    ]

    options = chat_completion(options_messages).strip()

    # Append the questions with options to the list
    questions_with_options.append(options)

    return questions_with_options


# Example usage:
educational_stage = "HSS3"
level = 1
num_of_questions = 3
questions_with_options = generate_question_with_instructions(
    educational_stage, level, data, answered_questions, num_of_questions)

# Displaying the results
for options in questions_with_options:
    print(options)
    print("\n")


# %%
answered_questions_embeddings = embedding_model.encode(answered_questions)

# %%
# Function to calculate cosine similarity between two embeddings


def calculate_similarity(embedding1, embedding2):
    # Ensure the embeddings are numpy arrays before performing operations
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)

    return np.dot(embedding1, embedding2.T) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


# %%
def filter_similar_content(data, level, educational_stage, answered_questions_embeddings, threshold=0.8, max_rows=3):

    # Filter relevant data based on educational stage and level
    relevant_data = data[(data['EducationalStage'] ==
                          educational_stage) & (data['Level'] == level)]
    if relevant_data.empty:
        print(f"No relevant content found for EducationalStage: {
              educational_stage} with level: {level}.")
        return pd.DataFrame()  # Return an empty DataFrame

    filtered_data = []
    # Shuffle the relevant data to randomize selection
    relevant_data = relevant_data.sample(frac=1).reset_index(drop=True)
    for _, row in relevant_data.iterrows():
        # Load the precomputed embedding from the 'Embeddings' column
        context_embedding = np.array(row['Embeddings'])

        # Calculate similarity with each answered question embedding
        max_similarity = -1  # Initialize with a value lower than the minimum possible similarity
        for answered_embedding in answered_questions_embeddings:
            similarity = calculate_similarity(
                context_embedding, answered_embedding)

            if similarity > max_similarity:
                max_similarity = similarity  # Track the maximum similarity

        # If the maximum similarity is below the threshold, include this content
        if max_similarity < threshold:
            filtered_data.append(row)

        # Stop the loop if filtered_data reaches approximately max_rows
        if len(filtered_data) >= max_rows:
            break

    return pd.DataFrame(filtered_data)


# Example usage:
educational_stage = "HSS3"
level = 1
threshold = 0.84
max_rows = 3

filtered_data = filter_similar_content(
    data, level, educational_stage, answered_questions_embeddings, threshold, max_rows)

# Display the filtered data
print(filtered_data['Content'])

# %%


def generate_question_without_repeats(filtered_data, num_of_questions=3):
    """Generates questions based on filtered data, avoiding similar content to previously answered questions."""

    # Step 1: Concatenate all the content from the filtered rows
    combined_context = "\n".join(row['Content']
                                 for _, row in filtered_data.iterrows())

    # Step 2: Generate questions and options based on the combined context
    questions_with_options = []

    # Generate the questions using the combined context
    messages = [
        {"role": "system", "content": f"You are a history teacher answering questions in Arabic. In the context of Algerian history, you will be given a context, and you need to analyze it and generate {
            num_of_questions} questions for a quiz. Only provide the questions in Arabic."},
        {"role": "user", "content": combined_context}
    ]

    questions = chat_completion(messages).strip()

    # Generate options for each question
    options_messages = [
        {"role": "system", "content": "You are a history teacher. You will generate 3 possible answers for each question. Only 1 answer is correct, the other two are wrong. Ensure that the correct answer is factually accurate, while the wrong answers should be plausible but incorrect. Provide the options in Arabic in the following format:\nquestion 1:\n- wrong: <wrong answer 1>\n- wrong: <wrong answer 2>\n- correct: <correct answer>\nDo the same for the other questions. Make sure the options have almost the same length."},
        {"role": "user", "content": f"Questions: {
            questions}\nContext: {combined_context}"}
    ]

    options = chat_completion(options_messages).strip()

    # Append the questions with options to the list
    questions_with_options.append(options)

    return questions_with_options


# Example usage:
educational_stage = "HSS3"
level = 1
num_of_questions = 3
filtered_data = filter_similar_content(
    data, level, educational_stage, answered_questions_embeddings)
questions_with_options = generate_question_without_repeats(
    filtered_data, num_of_questions)

# Displaying the results
for options in questions_with_options:
    print(options)
    print("\n")

# %% [markdown]
# ##Parse output

# %%


def parse_questions(data):
    questions = []
    question_id = 1  # Initialize ID counter

    for block in data:
        # Split the block into individual question sections
        # Split by question number
        question_blocks = re.split(r"\n\n\d+\.\s+", block)
        for question_block in question_blocks:
            if not question_block.strip():  # Skip empty blocks
                continue

            # Skip the header block (e.g., "## أسئلة الاختبار حول تاريخ الجزائر في سياق الحرب الباردة:")
            if question_block.startswith("##"):
                continue

            # Extract the question and answers
            question_match = re.search(r"\*\*(.+?)\*\*", question_block)
            if not question_match:
                print(f"Skipping block (no question found): {question_block}")
                continue

            question = question_match.group(1).strip()
            answers = re.findall(r"- (wrong|correct): (.+)", question_block)
            if not answers:
                print(f"No answers found for question: {question}")
                continue

            # Convert answers to the desired format
            parsed_answers = []
            for idx, (ans_type, ans_text) in enumerate(answers):
                parsed_answers.append({
                    "optionLabel": ans_text.strip(),  # Original text
                    "isCorrect": 1 if ans_type == "correct" else 0,  # 0 for wrong, 1 for correct
                    "index": idx  # Index of the answer (0-based)
                })

            # Add the question with ID and answers
            questions.append({
                "id": question_id,  # Unique ID for the question
                "question": question,
                "answers": parsed_answers
            })

            question_id += 1  # Increment ID for the next question

    return questions


# Parse the data
print(questions_with_options)
parsed_data = parse_questions(questions_with_options)
# Output the result
pprint.pprint(parsed_data)

# %% [markdown]
# **Evaluation and update solved questions**

# %%


def update_student_results(email, educational_stage, level, student_answers, parsed_data, path_json_file):
    """
    Updates the student's quiz results based on their answers and writes the updated data to a JSON file.

    Parameters:
        email (str): The student's email.
        educational_stage (str): The educational stage (e.g., "HSS3").
        level (str): The level (e.g., "1").
        student_answers (dict): The student's answers (question_id: chosen_option_index).
        parsed_data (list): The parsed questions and answers.
        path_json_file (str): Path to the JSON file containing the student data.
    """
    # Load the existing student data from the JSON file
    with open(path_json_file, "r", encoding="utf-8") as file:
        student_data = json.load(file)

    # Compare student answers with parsed data
    for question in parsed_data:
        question_id = question["id"]
        if question_id in student_answers:
            chosen_option_index = student_answers[question_id]
            correct_option_index = next(
                (ans["index"] for ans in question["answers"] if ans["isCorrect"] == 1), None)

            # If the student's answer is correct, add the question to the quiz
            if chosen_option_index == correct_option_index:
                question_text = question["question"]
                student_data[email][educational_stage]["Quiz 1"][int(
                    level) - 1][level].append({"question": question_text})

    # Write the updated student data back to the JSON file
    with open(path_json_file, "w", encoding="utf-8") as file:
        json.dump(student_data, file, ensure_ascii=False, indent=4)

    print("updated Sucessfuly")


# Example usage
student_answers = {
    1: 0,  # choose first option for question 1
    2: 2,
    3: 1
}
email = "student1@gmail.com"
educational_stage = "HSS3"
level = "1"
path_json_file = "students.json"

# Update the student's results and write to the JSON file
updated_student_data = update_student_results(
    email, educational_stage, level, student_answers, parsed_data, path_json_file)


# %%
