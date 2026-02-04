"""
DadRock Tabs API Tests
Tests for video search, admin login, and CRUD operations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPublicEndpoints:
    """Public API endpoint tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "DadRock Tabs API"
        print(f"✓ API root: {data['message']}")
    
    def test_get_videos_no_search(self):
        """Test getting all videos without search"""
        response = requests.get(f"{BASE_URL}/api/videos")
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert "total" in data
        assert isinstance(data["videos"], list)
        assert data["total"] > 0
        print(f"✓ Total videos: {data['total']}")
    
    def test_search_videos_by_song(self):
        """Test searching videos by song name"""
        response = requests.get(f"{BASE_URL}/api/videos", params={
            "search": "stairway",
            "search_type": "song"
        })
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert "total" in data
        print(f"✓ Search by song 'stairway': {data['total']} results")
    
    def test_search_videos_by_artist(self):
        """Test searching videos by artist name"""
        response = requests.get(f"{BASE_URL}/api/videos", params={
            "search": "led zeppelin",
            "search_type": "artist"
        })
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert data["total"] > 0
        print(f"✓ Search by artist 'led zeppelin': {data['total']} results")
    
    def test_search_videos_all_type(self):
        """Test searching videos with 'all' search type"""
        response = requests.get(f"{BASE_URL}/api/videos", params={
            "search": "led",
            "search_type": "all"
        })
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert data["total"] > 0
        print(f"✓ Search all 'led': {data['total']} results")
    
    def test_get_single_video(self):
        """Test getting a single video by ID"""
        # First get a video ID from the list
        list_response = requests.get(f"{BASE_URL}/api/videos", params={"limit": 1})
        assert list_response.status_code == 200
        videos = list_response.json()["videos"]
        assert len(videos) > 0
        
        video_id = videos[0]["id"]
        response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == video_id
        assert "song" in data
        assert "artist" in data
        assert "youtube_url" in data
        print(f"✓ Get video by ID: {data['song']} by {data['artist']}")
    
    def test_get_nonexistent_video(self):
        """Test getting a video that doesn't exist"""
        response = requests.get(f"{BASE_URL}/api/videos/nonexistent-id-12345")
        assert response.status_code == 404
        print("✓ Nonexistent video returns 404")
    
    def test_video_response_structure(self):
        """Test that video response has correct structure"""
        response = requests.get(f"{BASE_URL}/api/videos", params={"limit": 1})
        assert response.status_code == 200
        videos = response.json()["videos"]
        assert len(videos) > 0
        
        video = videos[0]
        required_fields = ["id", "song", "artist", "youtube_url", "created_at"]
        for field in required_fields:
            assert field in video, f"Missing field: {field}"
        print(f"✓ Video structure valid: {list(video.keys())}")


class TestAdminLogin:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test admin login with correct password"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "password": "Babyty99"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "message" in data
        print("✓ Admin login successful with correct password")
    
    def test_admin_login_wrong_password(self):
        """Test admin login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Admin login rejected with wrong password")
    
    def test_admin_login_empty_password(self):
        """Test admin login with empty password"""
        response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "password": ""
        })
        assert response.status_code == 401
        print("✓ Admin login rejected with empty password")


class TestAdminProtectedEndpoints:
    """Admin protected endpoint tests"""
    
    @pytest.fixture
    def admin_auth(self):
        """Get admin authentication"""
        return ("admin", "Babyty99")
    
    def test_admin_stats(self, admin_auth):
        """Test getting admin stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", auth=admin_auth)
        assert response.status_code == 200
        data = response.json()
        assert "total_videos" in data
        assert "total_artists" in data
        assert data["total_videos"] > 0
        print(f"✓ Admin stats: {data['total_videos']} videos, {data['total_artists']} artists")
    
    def test_admin_stats_unauthorized(self):
        """Test admin stats without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401
        print("✓ Admin stats rejected without auth")
    
    def test_admin_create_video(self, admin_auth):
        """Test creating a video via admin API"""
        video_data = {
            "song": "TEST_Highway to Hell",
            "artist": "AC/DC",
            "youtube_url": "https://www.youtube.com/watch?v=l482T0yNkeo"
        }
        response = requests.post(f"{BASE_URL}/api/admin/videos", json=video_data, auth=admin_auth)
        assert response.status_code == 200
        data = response.json()
        assert data["song"] == video_data["song"]
        assert data["artist"] == video_data["artist"]
        assert "id" in data
        assert "thumbnail" in data  # Auto-generated
        print(f"✓ Created video: {data['song']} (ID: {data['id']})")
        
        # Cleanup - delete the test video
        delete_response = requests.delete(f"{BASE_URL}/api/admin/videos/{data['id']}", auth=admin_auth)
        assert delete_response.status_code == 200
        print(f"✓ Cleaned up test video")
    
    def test_admin_update_video(self, admin_auth):
        """Test updating a video via admin API"""
        # First create a test video
        create_data = {
            "song": "TEST_Update Test",
            "artist": "Test Artist",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        create_response = requests.post(f"{BASE_URL}/api/admin/videos", json=create_data, auth=admin_auth)
        assert create_response.status_code == 200
        video_id = create_response.json()["id"]
        
        # Update the video
        update_data = {"song": "TEST_Updated Song Name"}
        update_response = requests.put(f"{BASE_URL}/api/admin/videos/{video_id}", json=update_data, auth=admin_auth)
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["song"] == "TEST_Updated Song Name"
        print(f"✓ Updated video song name")
        
        # Verify update persisted
        get_response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        assert get_response.status_code == 200
        assert get_response.json()["song"] == "TEST_Updated Song Name"
        print(f"✓ Update verified via GET")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/admin/videos/{video_id}", auth=admin_auth)
    
    def test_admin_delete_video(self, admin_auth):
        """Test deleting a video via admin API"""
        # First create a test video
        create_data = {
            "song": "TEST_Delete Test",
            "artist": "Test Artist",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        create_response = requests.post(f"{BASE_URL}/api/admin/videos", json=create_data, auth=admin_auth)
        assert create_response.status_code == 200
        video_id = create_response.json()["id"]
        
        # Delete the video
        delete_response = requests.delete(f"{BASE_URL}/api/admin/videos/{video_id}", auth=admin_auth)
        assert delete_response.status_code == 200
        print(f"✓ Deleted video")
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        assert get_response.status_code == 404
        print(f"✓ Deletion verified - video returns 404")


class TestSEOEndpoints:
    """SEO-related endpoint tests"""
    
    def test_sitemap(self):
        """Test sitemap.xml endpoint"""
        response = requests.get(f"{BASE_URL}/sitemap.xml")
        assert response.status_code == 200
        assert "xml" in response.headers.get("content-type", "")
        assert "urlset" in response.text
        print("✓ Sitemap.xml accessible")
    
    def test_robots_txt(self):
        """Test robots.txt endpoint"""
        response = requests.get(f"{BASE_URL}/robots.txt")
        assert response.status_code == 200
        assert "User-agent" in response.text
        assert "Disallow: /admin" in response.text
        print("✓ Robots.txt accessible and contains admin disallow")


class TestPagination:
    """Pagination tests"""
    
    def test_pagination_limit(self):
        """Test pagination with limit parameter"""
        response = requests.get(f"{BASE_URL}/api/videos", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert len(data["videos"]) <= 5
        print(f"✓ Pagination limit: returned {len(data['videos'])} videos")
    
    def test_pagination_skip(self):
        """Test pagination with skip parameter"""
        # Get first page
        first_response = requests.get(f"{BASE_URL}/api/videos", params={"limit": 5, "skip": 0})
        first_videos = first_response.json()["videos"]
        
        # Get second page
        second_response = requests.get(f"{BASE_URL}/api/videos", params={"limit": 5, "skip": 5})
        second_videos = second_response.json()["videos"]
        
        # Verify different videos
        first_ids = {v["id"] for v in first_videos}
        second_ids = {v["id"] for v in second_videos}
        assert first_ids.isdisjoint(second_ids), "Pagination returned duplicate videos"
        print("✓ Pagination skip works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
