# Personality Quiz API Documentation

## Overview
The Personality Quiz is a drag-and-drop matching game where students match historical personalities with their descriptions. Each personality is displayed with their name and image.

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Generate Quiz
Generates a new personality quiz with randomized descriptions.

**Endpoint:** `/personality/quiz/generate`
**Method:** `POST`

**Request:**
```json
{
    "email": "student@example.com",
    "educational_stage": "HSS3",
    "num_questions": 5
}
```

**Response:**
```json
{
    "quiz": {
        "personalities": [
            {
                "id": 1,
                "name": "وودرو ويلسن",
                "image_link": "https://example.com/wilson.jpg"
            }
            // ... more personalities
        ],
        "descriptions": [
            {
                "id": 3,
                "text": "رئيس الو م أ بين عامي 1913 و 1921..."
            }
            // ... more descriptions (shuffled)
        ]
    },
    "total_questions": 5
}
```

### 2. Submit Quiz Answers
Submit the matches made by the student.

**Endpoint:** `/personality/quiz/submit`
**Method:** `POST`

**Request:**
```json
{
    "email": "student@example.com",
    "educational_stage": "HSS3",
    "matches": [
        {
            "personality_id": 1,
            "description_id": 3,
            "personality_name": "وودرو ويلسن",
            "description": "رئيس الو م أ بين عامي 1913 و 1921...",
            "image_link": "https://example.com/wilson.jpg"
        }
        // ... more matches
    ]
}
```

**Response:**
```json
{
    "results": [
        {
            "personality_id": 1,
            "correct": true
        }
        // ... more results
    ],
    "progress": {
        "solved_personalities": [
            {
                "Personality Name": "وودرو ويلسن",
                "Description": "رئيس الو م أ بين عامي 1913 و 1921...",
                "image_link": "https://example.com/wilson.jpg"
            }
            // ... more solved personalities
        ]
    }
}
```

### 3. Get Progress
Retrieve student's progress in personality quizzes.

**Endpoint:** `/personality/progress`
**Method:** `GET`

**Query Parameters:**
- `email`: Student's email
- `educational_stage`: Educational stage code

**Response:**
```json
{
    "progress": [
        {
            "Personality Name": "وودرو ويلسن",
            "Description": "رئيس الو م أ بين عامي 1913 و 1921...",
            "image_link": "https://example.com/wilson.jpg"
        }
        // ... more solved personalities
    ]
}
```

## Implementation Notes

### Quiz Generation
- Questions are filtered based on the student's educational stage
- Previously solved personalities are excluded
- Descriptions are randomly shuffled for each quiz
- Each personality includes name and image URL
- Images are pre-stored in the database (no dynamic image fetching)

### Drag and Drop Implementation
1. Display two columns:
   - Left: Personalities with names and images
   - Right: Shuffled descriptions
2. Each personality and description should be draggable
3. Match is made when a personality is dropped onto a description or vice versa

### Progress Tracking
- System tracks:
  - Total solved personalities
  - Total attempts
  - Correct matches
- Progress is persistent across sessions
- Progress is specific to educational stage

### Error Handling
Common error responses:
```json
{
    "error": "Missing required fields"
}
```
Status codes:
- 200: Success
- 400: Bad request (missing fields)
- 401: Unauthorized
- 500: Server error

### Educational Stages
Available stages:
- HSS1: First year secondary
- HSS2: Second year secondary
- HSS3: Third year secondary

## Example Implementation Flow
1. Load quiz:
   ```javascript
   await fetch('/personality/quiz/generate', {
     method: 'POST',
     body: JSON.stringify({
       email: userEmail,
       educational_stage: 'HSS3',
       num_questions: 5
     })
   });
   ```

2. Display quiz:
   - Create draggable elements for personalities and descriptions
   - Show personality images and names in left column
   - Show shuffled descriptions in right column

3. Submit answers:
   ```javascript
   await fetch('/personality/quiz/submit', {
     method: 'POST',
     body: JSON.stringify({
       email: userEmail,
       educational_stage: 'HSS3',
       matches: [/* array of matches */]
     })
   });
   ```

4. Show results:
   - Highlight correct/incorrect matches
   - Update progress display
   - Show congratulations message if all correct