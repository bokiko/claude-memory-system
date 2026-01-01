---
title: API Reference Template
category: apis
tags: [api, rest, endpoints, template]
---

# API Name

Base URL: `https://api.example.com/v1`

## Authentication

```bash
# Header
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### GET /users
List all users

```bash
curl -X GET "https://api.example.com/v1/users" \
  -H "Authorization: Bearer $API_KEY"
```

Response:
```json
{
  "users": [
    {"id": 1, "name": "John"}
  ]
}
```

### POST /users
Create a user

```bash
curl -X POST "https://api.example.com/v1/users" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "email": "jane@example.com"}'
```

## Rate Limits

- 100 requests per minute
- 10,000 requests per day

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 429 | Rate limited |
| 500 | Server error |
