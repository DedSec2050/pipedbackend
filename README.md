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

## Jenkins CI/CD Pipeline

This project includes a Jenkins pipeline for automated deployment and CI/CD. The pipeline is defined in the `JenkinsFile` at the root of the repository.

### Jenkins Pipeline Stages

- **Stop Service**: Stops the running Flask service using `systemctl`.
- **Checkout Code**: Pulls the latest code from the `master` branch of the repository.
- **Deploy to Server Directory**: Copies the project files to the deployment directory on the server.
- **Load Environment Variables**: Loads environment variables from a script (e.g., `/home/ubuntu/loadenv.sh`).
- **Install Dependencies**: Sets up a Python virtual environment and installs dependencies from `requirements.txt`.
- **Start Service**: Starts the Flask service using `systemctl`.

### Usage

1. **Configure Jenkins**: Ensure Jenkins is installed and has access to the server where the app will be deployed.
2. **Set Up Credentials**: Make sure Jenkins can access the repository and has permissions to run commands on the server.
3. **Environment Script**: Place your environment variable script at the specified path (default: `/home/ubuntu/loadenv.sh`).
4. **Service File**: Ensure a `systemd` service file exists for your Flask app (e.g., `flaskapp.service`).
5. **Run the Pipeline**: Trigger the Jenkins pipeline to deploy and start the backend automatically.

You can customize the pipeline by editing the `JenkinsFile` as needed for your environment.

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
