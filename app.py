from flask import Flask, Blueprint, jsonify, request
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson.objectid import ObjectId
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a separate blueprint for API endpoints
api = Blueprint('api', __name__)

# MongoDB Atlas Configuration
MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://marsalded:db-password@tutedude.hs4khbf.mongodb.net/?retryWrites=true&w=majority&appName=tutedude")
DATABASE_NAME = "tutedude"
COLLECTION_NAME = "todos docker"

# Global variables for connection status
mongo_client = None
db = None
collection = None
db_connected = False

def connect_to_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, db, collection, db_connected
    print("Connecting to MongoDB Atlas... ")
    logger.info("Connecting to MongoDB Atlas...")
    logger.info(f"mongo_uri: {MONGO_URI}")
    logger.info(f"database_name: {DATABASE_NAME}")
    try:
        # Create a new client with the ServerApi version 1
        mongo_client = MongoClient(MONGO_URI)
        # Test the connection by sending a ping
        mongo_client.admin.command('ping')
        db = mongo_client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        db_connected = True
        logger.info("Successfully connected to MongoDB Atlas")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        db_connected = False
        return False

def get_db_status():
    """Check current database connection status"""
    global mongo_client, db_connected
    if not mongo_client:
        return False
    try:
        mongo_client.admin.command('ping')
        db_connected = True
        return True
    except Exception as e:
        logger.error(f"Database connection lost: {e}")
        db_connected = False
        return False

def expose(route, **options):
    """
    Custom decorator to register API endpoints in the blueprint.
    """
    def decorator(func):
        api.route(route, **options)(func)
        return func
    return decorator

def get_todos():
    """
    Get todos from MongoDB.
    """
    try:
        if not get_db_status():
            logger.error("Database connection not available")
            return []
        
        # Fetch all todos from MongoDB, sorted by creation date (newest first)
        todos = list(collection.find().sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for todo in todos:
            todo['_id'] = str(todo['_id'])
            # Ensure we have an 'id' field for compatibility
            if 'id' not in todo:
                todo['id'] = todo['_id']
        
        return todos
    except Exception as e:
        logger.error(f"Error fetching todos: {e}")
        return []

def save_todo(todo_data):
    """
    Save a single todo to MongoDB.
    """
    try:
        if not get_db_status():
            logger.error("Database connection not available")
            return False
        
        result = collection.insert_one(todo_data)
        if result.inserted_id:
            logger.info(f"Todo saved successfully with ID: {result.inserted_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error saving todo: {e}")
        return False

@expose('/api', methods=['GET'])
def get_data():
    """
    API endpoint to fetch all data including todos from MongoDB.
    This endpoint is called by the frontend to get all todos.
    """
    try:
        if not get_db_status():
            return jsonify({"error": "Database connection not available", "todos": []}), 500
        
        todos = get_todos()
        
        # Return the data in the format expected by the frontend
        data = {
            "todos": todos,
            "metadata": {
                "version": "2.0",
                "last_updated": datetime.now().strftime('%Y-%m-%d'),
                "total_todos": len(todos),
                "database": "MongoDB Atlas"
            }
        }
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in get_data endpoint: {e}")
        return jsonify({"error": str(e), "todos": []}), 500

@expose('/submittodoitem', methods=['POST'])
def add_todo():
    """
    Add a new todo item to MongoDB.
    This endpoint receives form data from the frontend.
    """
    try:
        # Get form data - handle both form-encoded and JSON data
        if request.content_type == 'application/json':
            data = request.get_json()
            item_name = data.get('item_name', '').strip()
            item_description = data.get('item_description', '').strip()
        else:
            item_name = request.form.get('item_name', '').strip()
            item_description = request.form.get('item_description', '').strip()
        
        if not item_name or not item_description:
            return jsonify({"error": "Both item name and description are required!"}), 400
        
        # Check database connection
        if not get_db_status():
            return jsonify({"error": "Database connection error. Please try again later."}), 500
        
        # Create new todo document
        new_todo = {
            'name': item_name,
            'description': item_description,
            'completed': False,
            'created_at': datetime.utcnow(),
            'ip_address': request.remote_addr
        }
        
        # Save to MongoDB
        if save_todo(new_todo):
            logger.info(f'Todo item "{item_name}" added successfully!')
            return jsonify({"message": f'Todo item "{item_name}" added successfully!', "success": True}), 201
        else:
            return jsonify({"error": "Error saving todo item. Please try again."}), 500
        
    except Exception as e:
        logger.error(f"Error adding todo: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@expose('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify backend status and database connection.
    """
    db_status = get_db_status()
    return jsonify({
        "status": "healthy" if db_status else "unhealthy",
        "database_connected": db_status,
        "timestamp": datetime.now().isoformat()
    }), 200 if db_status else 503

# Create the Flask app and register the blueprint
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.register_blueprint(api)

# Add CORS support for frontend communication
from flask_cors import CORS
CORS(app)

@app.route('/')
def home():
    """
    Root endpoint to show basic API information.
    """
    db_status = "Connected to MongoDB" if get_db_status() else "MongoDB Connection Failed"
    return jsonify({
        "message": "Todo Backend API",
        "status": db_status,
        "database_connected": get_db_status(),
        "endpoints": {
            "/api": "GET - Fetch all todos",
            "/submittodoitem": "POST - Add new todo",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    # Initialize MongoDB connection
    connect_to_mongodb()
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=8000, debug=True)
