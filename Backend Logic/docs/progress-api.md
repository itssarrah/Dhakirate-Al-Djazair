# Progress API Endpoints

## GET /quiz/progress

Gets the progress for all levels within an educational stage.

### Request

```http
GET /quiz/progress?email=student@example.com&educational_stage=PS5
```

### Query Parameters

- `email` (required): The user's email address
- `educational_stage` (required): The educational stage code (e.g., PS5)

### Response

```json
{
    "progress": {
        "1": 40,  // Level 1: 40% complete
        "2": 20,  // Level 2: 20% complete
        "3": 0    // Level 3: Not started
    }
}
```

### Notes

- Progress values range from 0 to 100 (percentage)
- Each correct answer adds 10% to the progress
- If a level hasn't been started, it will show 0 progress
- All levels (1 through 3) are always included in the response
- The endpoint will never error, returning 0 progress for non-existent users/stages
