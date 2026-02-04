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

class YouTubeSyncRequest(BaseModel):
    api_key: Optional[str] = None  # Will use env var if not provided
    channel_id: str = "UCLN8LV-ojTQP2wPtDg1kvGQ"  # DadRock Tabs channel ID

# YouTube API key from env
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

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

@api_router.get("/sitemap.xml")
async def sitemap():
    from fastapi.responses import Response
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://dadrocktabs.com/</loc>
    <lastmod>2026-02-04</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://dadrocktabs.com/search</loc>
    <lastmod>2026-02-04</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
    return Response(content=sitemap_xml, media_type="application/xml")

@api_router.get("/robots.txt")
async def robots():
    from fastapi.responses import PlainTextResponse
    robots_txt = """User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/

Sitemap: https://dadrocktabs.com/api/sitemap.xml"""
    return PlainTextResponse(content=robots_txt)

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

def parse_video_title(title: str) -> tuple:
    """Parse video title to extract song and artist
    Expected formats: 
    - "Song Name - Artist Name Guitar TAB"
    - "Artist - Song Name (Guitar + Bass TABS)"
    """
    # Remove common suffixes
    clean_title = re.sub(r'\s*(Guitar|Bass|TAB|TABS|Lesson|Tutorial|\+|\(|\)|\[|\]|HD|Official).*', '', title, flags=re.IGNORECASE)
    clean_title = clean_title.strip()
    
    # Try to split by " - "
    if " - " in clean_title:
        parts = clean_title.split(" - ", 1)
        # Heuristic: usually format is "Song - Artist" or "Artist - Song"
        # For DadRock Tabs, it's typically "Song Name - Artist Name"
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else "Unknown Artist"
    
    # Try to split by " by "
    if " by " in clean_title.lower():
        parts = re.split(r'\s+by\s+', clean_title, flags=re.IGNORECASE)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else "Unknown Artist"
    
    return clean_title, "DadRock Tabs"

@api_router.post("/admin/youtube/sync")
async def sync_youtube_channel(request: YouTubeSyncRequest, auth: bool = Depends(verify_admin)):
    """Sync videos from YouTube channel using API"""
    # Use provided API key or fall back to env variable
    api_key = request.api_key or YOUTUBE_API_KEY
    if not api_key:
        raise HTTPException(status_code=400, detail="YouTube API key not configured")
    
    try:
        youtube = build("youtube", "v3", developerKey=api_key, cache_discovery=False)
        
        videos_added = 0
        videos_skipped = 0
        errors = []
        next_page_token = None
        
        # Get channel's uploads playlist
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=request.channel_id
        ).execute()
        
        if not channel_response.get("items"):
            raise HTTPException(status_code=404, detail="Channel not found")
        
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Fetch all videos from uploads playlist
        while True:
            playlist_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for item in playlist_response.get("items", []):
                snippet = item["snippet"]
                video_id = snippet["resourceId"]["videoId"]
                title = snippet["title"]
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                thumbnail = snippet["thumbnails"].get("high", snippet["thumbnails"].get("default", {})).get("url", "")
                
                # Check if video already exists
                existing = await db.videos.find_one({"youtube_url": youtube_url})
                if existing:
                    videos_skipped += 1
                    continue
                
                # Parse title to get song and artist
                song, artist = parse_video_title(title)
                
                # Create video entry
                video = Video(
                    song=song,
                    artist=artist,
                    youtube_url=youtube_url,
                    thumbnail=thumbnail
                )
                
                doc = video.model_dump()
                doc['created_at'] = doc['created_at'].isoformat()
                
                try:
                    await db.videos.insert_one(doc)
                    videos_added += 1
                except Exception as e:
                    errors.append(f"Failed to add '{title}': {str(e)}")
            
            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break
        
        return {
            "success": True,
            "message": f"Sync completed! {videos_added} videos added, {videos_skipped} already existed.",
            "videos_added": videos_added,
            "videos_skipped": videos_skipped,
            "errors": errors
        }
        
    except HttpError as e:
        error_reason = str(e)
        if "quotaExceeded" in error_reason:
            raise HTTPException(status_code=429, detail="YouTube API quota exceeded. Try again tomorrow.")
        elif "keyInvalid" in error_reason or "API key not valid" in error_reason:
            raise HTTPException(status_code=401, detail="Invalid YouTube API key")
        else:
            raise HTTPException(status_code=400, detail=f"YouTube API error: {error_reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# SEO Routes (on main app, not api_router)
from fastapi.responses import Response, PlainTextResponse

@app.get("/sitemap.xml")
async def sitemap_root():
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://dadrocktabs.com/</loc>
    <lastmod>2026-02-04</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://dadrocktabs.com/search</loc>
    <lastmod>2026-02-04</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
    return Response(content=sitemap_xml, media_type="application/xml")

@app.get("/robots.txt")
async def robots_root():
    robots_txt = """User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/

Sitemap: https://dadrocktabs.com/sitemap.xml"""
    return PlainTextResponse(content=robots_txt)

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
