# Events Quiz API Documentation

## Overview
The Events Quiz system tests students' knowledge of historical dates and events. Questions can be of two types:
1. Given a date → Find the corresponding event (type: 0)
2. Given an event → Provide the correct date (type: 1)

## Endpoints

### 1. Generate Events Quiz
Generates a new quiz excluding previously solved questions.

**Endpoint:** `POST /events/quiz/generate`

**Request Body:**
```json
{
    "email": "student@example.com",
    "educational_stage": "HSS3,   
}
```

**Response:**
```json
{
    "quiz": [
        {
            "id": 321,
            "date": "1954/09/08",
            "event": "تأسيس حلف جنوب شرق آسیا",
            "type": 0  // date→event question
        },
        {
            "id": 367,
            "date": "1955/06/13",
            "event": "تأسيس الاتحاد العام للطلبة المسلمين الجزائريين",
            "type": 0  // date→event question
        },
        {
            "id": 375,
            "date": "1957/01/28",
            "event": "إضراب ثمانية أيام",
            "type": 0  // date→event question
        },
        {
            "id": 328,
            "date": "1956/07/26",
            "event": "تأميم قناة السويس بكالوريا 08 آف 11 ل أ",
            "type": 0  // date→event question
        },
        {
            "id": 310,
            "date": "1947/10/06",
            "event": "تأسيس مكتب الإعلام الشيوعي الكومنفورم بكالوريا 109 آف ل أ",
            "type": 0  // date→event question
        }
    ],
    "total_questions": 5
}
```

2. Submit Quiz Answers
Submits and evaluates student answers.

Endpoint: POST /events/quiz/submit

Request Body:
```json
{
    "email": "student@example.com",
    "educational_stage": "HSS3",
    "answers": [
        {
            "question_id": 321,
            "type": 0,
            "answer": "تأسيس حلف جنوب شرق آسیا"  // For type 0 (date→event)
        },
        {
            "question_id": 367,
            "type": 0,
            "answer": "تأسيس الاتحاد العام للطلبة المسلمين الجزائريين"  // For type 0 (date→event)
        },
        {
            "question_id": 375,
            "type": 0,
            "answer": "إضراب ثمانية أيام"  // For type 0 (date→event)
        },
        {
            "question_id": 328,
            "type": 0,
            "answer": "تأميم قناة السويس بكالوريا 08 آف 11 ل أ"  // For type 0 (date→event)
        },
        {
            "question_id": 310,
            "type": 0,
            "answer": "تأسيس مكتب الإعلام الشيوعي الكومنفورم بكالوريا 109 آف ل أ"  // For type 0 (date→event)
        }
    ]
}
```

Response:
```json
{
    "results": [
        {
            "question_id": 321,
            "correct": true,
            "progress": {
                "solved_questions": [...],
                "total_attempts": 1,
                "correct_answers": 1
            }
        },
        {
            "question_id": 367,
            "correct": true,
            "progress": {
                "solved_questions": [...],
                "total_attempts": 2,
                "correct_answers": 2
            }
        },
        {
            "question_id": 375,
            "correct": true,
            "progress": {
                "solved_questions": [...],
                "total_attempts": 3,
                "correct_answers": 3
            }
        },
        {
            "question_id": 328,
            "correct": true,
            "progress": {
                "solved_questions": [...],
                "total_attempts": 4,
                "correct_answers": 4
            }
        },
        {
            "question_id": 310,
            "correct": true,
            "progress": {
                "solved_questions": [...],
                "total_attempts": 5,
                "correct_answers": 5
            }
        }
    ]
}
```