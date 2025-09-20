"""
Database operations for job application tracking
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "job_tracker_speech_to_speech")

print(f"Using database: {DATABASE_NAME}")
print(f"Using MongoDB URI: {MONGODB_URI}")

# Initialize database connection
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Flag to track if indexes have been created
_indexes_created = False

# Default user ID for demo purposes (in production, this would come from authentication)
DEFAULT_USER_ID = "507f1f77bcf86cd799439011"  # Valid 24-character hex string

async def get_db():
    """Get database instance and ensure indexes are created"""
    global _indexes_created
    if not _indexes_created:
        await initialize_database()
        _indexes_created = True
    return db

def utcnow():
    """Get current UTC time"""
    return datetime.utcnow()

def serialize_document(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format"""
    if not doc:
        return doc
    
    serialized = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    
    return serialized

def get_user_id(user_id: str = None) -> str:
    """Get a valid user ID, creating one if needed"""
    if user_id and len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
        return user_id
    return DEFAULT_USER_ID

async def create_application_with_dedup(application_data: dict, user_id: str = None) -> dict:
    """Create application with deduplication check"""
    try:
        # Get valid user ID
        valid_user_id = get_user_id(user_id)
        
        # Normalize fields
        company_norm = application_data["company"].lower().strip()
        role_title_norm = application_data["role_title"].lower().strip()
        
        # Check for recent duplicate (14 days)
        recent_app = await find_recent_application(
            user_id=valid_user_id,
            company_norm=company_norm,
            role_title_norm=role_title_norm,
            days=14
        )
        
        if recent_app:
            # Update existing application
            updated_app = await update_application(
                app_id=recent_app["_id"],
                updates=application_data,
                user_id=valid_user_id
            )
            return {
                "application_id": str(recent_app["_id"]),
                "message": f"Updated existing {role_title_norm} position at {company_norm}",
                "updated": True
            }
        else:
            # Create new application
            app_id = await create_application({
                **application_data,
                "company_norm": company_norm,
                "role_title_norm": role_title_norm,
                "user_id": ObjectId(valid_user_id)
            })
            return {
                "application_id": str(app_id),
                "message": f"Added {role_title_norm} position at {company_norm}",
                "updated": False
            }
    except Exception as e:
        raise Exception(f"Failed to create application: {str(e)}")

async def create_application(app_data: dict) -> str:
    """Create a new application"""
    # Add timestamps
    app_data["created_at"] = utcnow()
    app_data["updated_at"] = utcnow()
    
    # Set default status if not provided
    if "status_stage" not in app_data:
        app_data["status_stage"] = "draft"
    
    result = await db.applications.insert_one(app_data)
    return str(result.inserted_id)

async def find_recent_application(user_id: str, company_norm: str, role_title_norm: str, days: int = 14) -> Optional[dict]:
    """Find recent application for upsert logic"""
    # Calculate date threshold
    threshold_date = utcnow() - timedelta(days=days)
    
    # Search for matching application within time window
    doc = await db.applications.find_one({
        "user_id": ObjectId(user_id),
        "company_norm": company_norm,
        "role_title_norm": role_title_norm,
        "created_at": {"$gte": threshold_date}
    })
    
    return doc

async def update_application(app_id: str, update_data: dict, user_id: str) -> bool:
    """Update an existing application"""
    # Add update timestamp
    update_data["updated_at"] = utcnow()
    
    result = await db.applications.update_one(
        {"_id": ObjectId(app_id), "user_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    return result.modified_count > 0

async def update_application_status(app_id: str, status_stage: str, user_id: str) -> bool:
    """Update application status"""
    return await update_application(app_id, {"status_stage": status_stage}, user_id)

async def find_application_by_reference(application_ref: str, user_id: str = None) -> Optional[dict]:
    """Find application by company name or role title"""
    valid_user_id = get_user_id(user_id)
    
    # Try to find by company name first
    doc = await db.applications.find_one({
        "user_id": ObjectId(valid_user_id),
        "company": {"$regex": application_ref, "$options": "i"}
    }, sort=[("created_at", -1)])
    
    if doc:
        return serialize_document(doc)
    
    # Try to find by role title
    doc = await db.applications.find_one({
        "user_id": ObjectId(valid_user_id),
        "role_title": {"$regex": application_ref, "$options": "i"}
    }, sort=[("created_at", -1)])
    
    return serialize_document(doc) if doc else None

async def add_note_to_application(application_id: str, content: str, user_id: str = None) -> str:
    """Add a note to an application"""
    valid_user_id = get_user_id(user_id)
    
    note_data = {
        "application_id": ObjectId(application_id),
        "user_id": ObjectId(valid_user_id),
        "content": content,
        "created_at": utcnow()
    }
    
    result = await db.notes.insert_one(note_data)
    return str(result.inserted_id)

async def schedule_followup(application_id: str, due_at: str, channel: str, user_id: str = None, note: Optional[str] = None) -> str:
    """Create a new followup reminder"""
    valid_user_id = get_user_id(user_id)
    
    # Parse ISO date
    try:
        due_date = datetime.fromisoformat(due_at.replace('Z', '+00:00'))
    except:
        # If parsing fails, assume it's a relative date and add days
        if "next" in due_at.lower() and "friday" in due_at.lower():
            due_date = utcnow() + timedelta(days=7)  # Next Friday
        elif "tomorrow" in due_at.lower():
            due_date = utcnow() + timedelta(days=1)
        else:
            due_date = utcnow() + timedelta(days=7)  # Default to next week
    
    followup_data = {
        "application_id": ObjectId(application_id),
        "user_id": ObjectId(valid_user_id),
        "due_at": due_date,
        "channel": channel,
        "status": "pending",
        "created_at": utcnow(),
        "updated_at": utcnow()
    }
    
    if note:
        followup_data["note"] = note
    
    result = await db.followups.insert_one(followup_data)
    return str(result.inserted_id)

async def search_applications(criteria: dict, user_id: str = None) -> List[dict]:
    """Search applications with various criteria"""
    valid_user_id = get_user_id(user_id)
    
    # Build query
    query = {"user_id": ObjectId(valid_user_id)}
    
    if "status_stage" in criteria:
        query["status_stage"] = criteria["status_stage"]
    
    if "company" in criteria:
        query["company"] = criteria["company"]
    
    # Handle time range
    if "time_range" in criteria:
        start_date, end_date = get_time_range(criteria["time_range"])
        query["created_at"] = {"$gte": start_date, "$lt": end_date}
    
    # Execute query
    cursor = db.applications.find(query).sort("created_at", -1).limit(50)
    applications = []
    async for doc in cursor:
        # Serialize document for JSON
        serialized_doc = serialize_document(doc)
        applications.append(serialized_doc)
    
    return applications

def get_time_range(time_range: str) -> tuple:
    """Get time range with proper calendar boundaries"""
    now = utcnow()
    
    if time_range == "last_week":
        # Previous calendar week (Monday to Sunday)
        start = now - timedelta(days=now.weekday() + 7)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif time_range == "this_week":
        # Current calendar week
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif time_range == "last_month":
        # Previous calendar month
        start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        end = now.replace(day=1)
    elif time_range == "this_month":
        # Current calendar month
        start = now.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    else:
        # Default to last 7 days
        end = now
        start = end - timedelta(days=7)
    
    return start, end

async def get_application_summary(user_id: str = None) -> dict:
    """Get summary statistics for voice commands"""
    valid_user_id = get_user_id(user_id)
    
    pipeline = [
        {
            "$match": {"user_id": ObjectId(valid_user_id)}
        },
        {
            "$group": {
                "_id": "$status_stage",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    cursor = db.applications.aggregate(pipeline)
    status_counts = {}
    total = 0
    
    async for doc in cursor:
        status_counts[doc["_id"]] = doc["count"]
        total += doc["count"]
    
    # Calculate active applications
    active_stages = ["applied", "hr_screen", "tech_screen", "onsite"]
    active_count = sum(status_counts.get(stage, 0) for stage in active_stages)
    
    # Calculate success rate
    success_count = status_counts.get("offer", 0)
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "status_breakdown": status_counts,
        "active_applications": active_count,
        "success_rate": round(success_rate, 1),
        "offers": success_count
    }

async def get_due_followups(user_id: str = None) -> List[dict]:
    """Get all due followups (for cron jobs)"""
    valid_user_id = get_user_id(user_id)
    
    now = utcnow()
    cursor = db.followups.find({
        "user_id": ObjectId(valid_user_id),
        "due_at": {"$lte": now},
        "status": "pending"
    }).sort("due_at", 1)
    
    followups = []
    async for doc in cursor:
        serialized_doc = serialize_document(doc)
        followups.append(serialized_doc)
    
    return followups

async def get_application_notes(application_id: str, user_id: str = None) -> List[dict]:
    """Get all notes for an application"""
    valid_user_id = get_user_id(user_id)
    
    cursor = db.notes.find({
        "application_id": ObjectId(application_id),
        "user_id": ObjectId(valid_user_id)
    }).sort("created_at", -1)
    
    notes = []
    async for doc in cursor:
        serialized_doc = serialize_document(doc)
        notes.append(serialized_doc)
    
    return notes

# Initialize database indexes
async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        print(f"Creating indexes for database: {DATABASE_NAME}")
        
        # Applications indexes
        await db.applications.create_index([("user_id", 1), ("company_norm", 1), ("role_title_norm", 1), ("created_at", -1)])
        await db.applications.create_index([("user_id", 1), ("status_stage", 1), ("created_at", -1)])
        await db.applications.create_index([("user_id", 1), ("next_follow_up_at", 1)])
        
        # Notes indexes
        await db.notes.create_index([("user_id", 1), ("application_id", 1), ("created_at", -1)])
        
        # Followups indexes
        await db.followups.create_index([("user_id", 1), ("status", 1), ("due_at", 1)])
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

async def ensure_collections_exist():
    """Ensure all required collections exist"""
    try:
        print(f"Ensuring collections exist in database: {DATABASE_NAME}")
        
        # List existing collections
        collections = await db.list_collection_names()
        print(f"Existing collections: {collections}")
        
        # Required collections
        required_collections = ["applications", "notes", "followups"]
        
        for collection_name in required_collections:
            if collection_name not in collections:
                # Create collection by inserting and removing a test document
                await db[collection_name].insert_one({"test": True, "created_at": utcnow()})
                await db[collection_name].delete_one({"test": True})
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection exists: {collection_name}")
                
    except Exception as e:
        print(f"Error ensuring collections exist: {e}")

# Initialize database on module import
async def initialize_database():
    """Initialize database on first use"""
    try:
        await ensure_collections_exist()
        await create_indexes()
        print(f"Database '{DATABASE_NAME}' initialized successfully!")
    except Exception as e:
        print(f"Database initialization failed: {e}")
