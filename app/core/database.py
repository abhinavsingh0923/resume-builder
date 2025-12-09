import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "resume_builder")

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.users = self.db.users
        self.sessions = self.db.sessions

    def get_user(self, email):
        return self.users.find_one({"email": email})

    def create_user(self, user_data):
        return self.users.insert_one(user_data)

    def update_user_profile(self, email, profile_data):
        return self.users.update_one(
            {"email": email},
            {"$set": {"profile": profile_data}},
            upsert=True
        )

    def get_user_profile(self, email):
        user = self.get_user(email)
        return user.get("profile", {}) if user else {}

    def create_session(self, email, job_description, initial_data=None):
        """Creates a new resume building session."""
        session_data = {
            "email": email,
            "job_description": job_description,
            "resume_data": initial_data or {},
            "created_at": None # You might want to add a timestamp here
        }
        result = self.sessions.insert_one(session_data)
        return str(result.inserted_id)

    def get_user_sessions(self, email):
        """Returns all sessions for a user."""
        return list(self.sessions.find({"email": email}))

    def get_session(self, session_id):
        """Returns a specific session by ID."""
        from bson.objectid import ObjectId
        try:
            return self.sessions.find_one({"_id": ObjectId(session_id)})
        except:
            return None

    def update_session(self, session_id, resume_data):
        """Updates the resume data for a specific session."""
        from bson.objectid import ObjectId
        return self.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"resume_data": resume_data}}
        )

db = Database()
