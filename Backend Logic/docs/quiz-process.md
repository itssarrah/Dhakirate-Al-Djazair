# POST /quiz/submit

## Payload Format
The frontend should send a JSON payload with the following structure:

```json
{
  "email": "student@example.com",
  "educational_stage": "PS5",
  "level": "1",
  "answers": {
    "question_id": selected_answer_index,
    "1": 2,
    "2": 1
  },
  // just send the same data i sent to you in 'quiz/generate' endpoint
  "quiz_data": [
    {
      "id": 1,
      "question": "ما هي أهم الأحداث الدولية التي أثرت على الجزائر في الفترة ما بين 1954 و 1975؟",
      "answers": [
        {
          "index": 0,
          "isCorrect": 0,
          "optionLabel": "..."
        },
        {
          "index": 1,
          "isCorrect": 0,
          "optionLabel": "..."
        },
        {
          "index": 2,
          "isCorrect": 1,
          "optionLabel": "..."
        }
      ]
    },
    ...
  ]
}
```

**Where:**

email: The user's email.

educational_stage: The user’s current 
educational stage or level.

level: Specific quiz or chapter level (optional usage details).

answers: A key-value map of question IDs to the selected answer index.

quiz_data: The full quiz questions array provided by the server or stored locally.

## Response
The backend returns a JSON response:

```json{
  "results": [
    {
      "question_id": "1",
      "correct": true,
      "progress": {
        "email": "student@example.com",
        "stage": "HighSchool",
        "level": "1",
        "score": 30
      }
    },
    {
      "question_id": "2",
      "correct": false
    }
  ]
}
```

**Where:**

correct: Indicates whether the submitted answer is correct.

progress: (optional) Reflects updated progress if the answer is correct.