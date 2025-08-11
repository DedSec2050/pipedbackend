# Todo Backend API

Flask backend service that connects to MongoDB Atlas for managing todo items.

## Features

- MongoDB Atlas integration
- RESTful API endpoints
- CORS support for frontend communication
- Health check endpoint
- Docker support

## API Endpoints

### GET /api

Fetch all todos from MongoDB

- Returns: JSON object with todos array and metadata

### POST /submittodoitem

Add a new todo item

- Body: `item_name` (string), `item_description` (string)
- Returns: Success/error message

### GET /health

Health check endpoint

- Returns: Service status and database connection status

### GET /

Root endpoint with API information

## Environment Variables

- `MONGO_URI`: MongoDB connection string
- `SECRET_KEY`: Flask secret key
- `FLASK_ENV`: Flask environment (development/production)

## Running the Backend

### With Docker

```bash
docker build -t todo-backend .
docker run -p 5000:5000 todo-backend
```

### Local Development

```bash
pip install -r requirements.txt
python app.py
```

## Database Schema

Todo items are stored with the following structure:

```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "completed": "boolean",
  "created_at": "datetime",
  "ip_address": "string"
}
```
