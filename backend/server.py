from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import secrets
import re
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import csv
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBasic()

# Admin password from env or default
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'dadrock2024')

# Define Models
class Video(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    song: str
    artist: str
    youtube_url: str
    thumbnail: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VideoCreate(BaseModel):
    song: str
    artist: str
    youtube_url: str
    thumbnail: Optional[str] = None

class VideoUpdate(BaseModel):
    song: Optional[str] = None
    artist: Optional[str] = None
    youtube_url: Optional[str] = None
    thumbnail: Optional[str] = None

class VideoResponse(BaseModel):
    id: str
    song: str
    artist: str
    youtube_url: str
    thumbnail: Optional[str] = None
    created_at: str

class SearchResponse(BaseModel):
    videos: List[VideoResponse]
    total: int

class AdminLogin(BaseModel):
    password: str

class AdminLoginResponse(BaseModel):
    success: bool
    message: str

def extract_youtube_thumbnail(url: str) -> str:
    """Extract video ID and generate thumbnail URL"""
    video_id = None
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
    elif 'youtube.com/embed/' in url:
        video_id = url.split('embed/')[1].split('?')[0]
    
    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
    return ""

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify admin credentials"""
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not correct_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# Public Routes
@api_router.get("/")
async def root():
    return {"message": "DadRock Tabs API"}

@api_router.get("/videos", response_model=SearchResponse)
async def get_videos(
    search: Optional[str] = None,
    search_type: Optional[str] = "all",  # all, song, artist
    skip: int = 0,
    limit: int = 50
):
    """Get all videos or search by song/artist"""
    query = {}
    
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        if search_type == "song":
            query = {"song": search_regex}
        elif search_type == "artist":
            query = {"artist": search_regex}
        else:  # all
            query = {"$or": [{"song": search_regex}, {"artist": search_regex}]}
    
    total = await db.videos.count_documents(query)
    videos = await db.videos.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    
    # Convert datetime to ISO string
    for video in videos:
        if isinstance(video.get('created_at'), datetime):
            video['created_at'] = video['created_at'].isoformat()
        elif not video.get('created_at'):
            video['created_at'] = datetime.now(timezone.utc).isoformat()
    
    return {"videos": videos, "total": total}

@api_router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    """Get a single video by ID"""
    video = await db.videos.find_one({"id": video_id}, {"_id": 0})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if isinstance(video.get('created_at'), datetime):
        video['created_at'] = video['created_at'].isoformat()
    
    return video

# Admin Routes
@api_router.post("/admin/login", response_model=AdminLoginResponse)
async def admin_login(login: AdminLogin):
    """Verify admin password"""
    if secrets.compare_digest(login.password, ADMIN_PASSWORD):
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid password")

@api_router.post("/admin/videos", response_model=VideoResponse)
async def create_video(video: VideoCreate, auth: bool = Depends(verify_admin)):
    """Create a new video (admin only)"""
    video_dict = video.model_dump()
    video_obj = Video(**video_dict)
    
    # Auto-generate thumbnail if not provided
    if not video_obj.thumbnail:
        video_obj.thumbnail = extract_youtube_thumbnail(video_obj.youtube_url)
    
    doc = video_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.videos.insert_one(doc)
    return doc

@api_router.put("/admin/videos/{video_id}", response_model=VideoResponse)
async def update_video(video_id: str, video: VideoUpdate, auth: bool = Depends(verify_admin)):
    """Update a video (admin only)"""
    update_data = {k: v for k, v in video.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Update thumbnail if URL changed
    if 'youtube_url' in update_data and 'thumbnail' not in update_data:
        update_data['thumbnail'] = extract_youtube_thumbnail(update_data['youtube_url'])
    
    result = await db.videos.update_one(
        {"id": video_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    updated_video = await db.videos.find_one({"id": video_id}, {"_id": 0})
    if isinstance(updated_video.get('created_at'), datetime):
        updated_video['created_at'] = updated_video['created_at'].isoformat()
    
    return updated_video

@api_router.delete("/admin/videos/{video_id}")
async def delete_video(video_id: str, auth: bool = Depends(verify_admin)):
    """Delete a video (admin only)"""
    result = await db.videos.delete_one({"id": video_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"message": "Video deleted successfully"}

@api_router.post("/admin/videos/bulk")
async def bulk_import_videos(file: UploadFile = File(...), auth: bool = Depends(verify_admin)):
    """Bulk import videos from CSV file (admin only)
    CSV format: song,artist,youtube_url
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    videos_added = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            if not all(k in row for k in ['song', 'artist', 'youtube_url']):
                errors.append(f"Row {row_num}: Missing required fields")
                continue
            
            video = Video(
                song=row['song'].strip(),
                artist=row['artist'].strip(),
                youtube_url=row['youtube_url'].strip(),
                thumbnail=extract_youtube_thumbnail(row['youtube_url'].strip())
            )
            
            doc = video.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            
            await db.videos.insert_one(doc)
            videos_added += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "message": f"Import completed. {videos_added} videos added.",
        "videos_added": videos_added,
        "errors": errors
    }

@api_router.get("/admin/stats")
async def get_stats(auth: bool = Depends(verify_admin)):
    """Get database statistics (admin only)"""
    total_videos = await db.videos.count_documents({})
    
    # Get unique artists
    artists = await db.videos.distinct("artist")
    
    return {
        "total_videos": total_videos,
        "total_artists": len(artists)
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
