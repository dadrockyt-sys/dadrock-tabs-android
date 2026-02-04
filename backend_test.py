import requests
import sys
import json
import base64
from datetime import datetime

class DadRockTabsAPITester:
    def __init__(self, base_url="https://tabfinder-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_password = "dadrock2024"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_video_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def get_admin_headers(self):
        """Get admin authentication headers"""
        auth_string = f"admin:{self.admin_password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_get_all_videos(self):
        """Test getting all videos"""
        return self.run_test("Get All Videos", "GET", "videos", 200)

    def test_search_videos_by_song(self):
        """Test searching videos by song"""
        return self.run_test(
            "Search Videos by Song", 
            "GET", 
            "videos", 
            200, 
            data={"search": "test", "search_type": "song"}
        )

    def test_search_videos_by_artist(self):
        """Test searching videos by artist"""
        return self.run_test(
            "Search Videos by Artist", 
            "GET", 
            "videos", 
            200, 
            data={"search": "test", "search_type": "artist"}
        )

    def test_search_videos_all(self):
        """Test searching videos (all types)"""
        return self.run_test(
            "Search Videos (All)", 
            "GET", 
            "videos", 
            200, 
            data={"search": "test", "search_type": "all"}
        )

    def test_admin_login_valid(self):
        """Test admin login with valid password"""
        return self.run_test(
            "Admin Login (Valid)", 
            "POST", 
            "admin/login", 
            200, 
            data={"password": self.admin_password}
        )

    def test_admin_login_invalid(self):
        """Test admin login with invalid password"""
        return self.run_test(
            "Admin Login (Invalid)", 
            "POST", 
            "admin/login", 
            401, 
            data={"password": "wrongpassword"}
        )

    def test_admin_stats(self):
        """Test admin stats endpoint"""
        return self.run_test(
            "Admin Stats", 
            "GET", 
            "admin/stats", 
            200, 
            headers=self.get_admin_headers()
        )

    def test_create_video(self):
        """Test creating a new video"""
        video_data = {
            "song": "Test Song",
            "artist": "Test Artist", 
            "youtube_url": "https://youtube.com/watch?v=test123"
        }
        success, response = self.run_test(
            "Create Video", 
            "POST", 
            "admin/videos", 
            200, 
            data=video_data,
            headers=self.get_admin_headers()
        )
        if success and response.get('id'):
            self.test_video_id = response['id']
            print(f"   Created video with ID: {self.test_video_id}")
        return success, response

    def test_get_video_by_id(self):
        """Test getting a video by ID"""
        if not self.test_video_id:
            print("❌ Skipped - No test video ID available")
            return False, {}
        
        return self.run_test(
            "Get Video by ID", 
            "GET", 
            f"videos/{self.test_video_id}", 
            200
        )

    def test_update_video(self):
        """Test updating a video"""
        if not self.test_video_id:
            print("❌ Skipped - No test video ID available")
            return False, {}
        
        update_data = {
            "song": "Updated Test Song",
            "artist": "Updated Test Artist"
        }
        return self.run_test(
            "Update Video", 
            "PUT", 
            f"admin/videos/{self.test_video_id}", 
            200, 
            data=update_data,
            headers=self.get_admin_headers()
        )

    def test_delete_video(self):
        """Test deleting a video"""
        if not self.test_video_id:
            print("❌ Skipped - No test video ID available")
            return False, {}
        
        return self.run_test(
            "Delete Video", 
            "DELETE", 
            f"admin/videos/{self.test_video_id}", 
            200, 
            headers=self.get_admin_headers()
        )

    def test_unauthorized_admin_access(self):
        """Test admin endpoints without authentication"""
        return self.run_test(
            "Unauthorized Admin Access", 
            "GET", 
            "admin/stats", 
            401
        )

def main():
    print("🎸 DadRock Tabs API Testing Suite")
    print("=" * 50)
    
    tester = DadRockTabsAPITester()
    
    # Test public endpoints
    print("\n📋 Testing Public Endpoints...")
    tester.test_root_endpoint()
    tester.test_get_all_videos()
    tester.test_search_videos_by_song()
    tester.test_search_videos_by_artist()
    tester.test_search_videos_all()
    
    # Test admin authentication
    print("\n🔐 Testing Admin Authentication...")
    tester.test_admin_login_valid()
    tester.test_admin_login_invalid()
    tester.test_unauthorized_admin_access()
    
    # Test admin endpoints
    print("\n⚙️ Testing Admin CRUD Operations...")
    tester.test_admin_stats()
    tester.test_create_video()
    tester.test_get_video_by_id()
    tester.test_update_video()
    tester.test_delete_video()
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())