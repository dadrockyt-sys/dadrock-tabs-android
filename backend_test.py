#!/usr/bin/env python3
"""
Backend API Tests for DadRock Tabs Next.js API
Tests all endpoints with authentication, CRUD operations, and search functionality
"""

import requests
import json
import base64
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://youtube-video-hub.preview.emergentagent.com/api"
ADMIN_PASSWORD = "dadrock2024"

def create_basic_auth_header():
    """Create Basic Auth header for admin endpoints"""
    credentials = f"admin:{ADMIN_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

def print_test_result(test_name, success, response_data=None, error=None):
    """Print formatted test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if error:
        print(f"   Error: {error}")
    if response_data and not success:
        print(f"   Response: {response_data}")
    print()

def test_health_endpoint():
    """Test GET /health endpoint"""
    print("Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('status') == 'healthy'
            print_test_result("GET /health", success, data)
            return success
        else:
            print_test_result("GET /health", False, response.text, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test_result("GET /health", False, error=str(e))
        return False

def test_settings_endpoint():
    """Test GET /settings endpoint"""
    print("Testing Settings Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/settings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['featured_video_url', 'featured_video_title', 'featured_video_artist']
            success = all(field in data for field in required_fields)
            print_test_result("GET /settings", success, data)
            return success, data
        else:
            print_test_result("GET /settings", False, response.text, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        print_test_result("GET /settings", False, error=str(e))
        return False, None

def test_videos_endpoint():
    """Test GET /videos endpoint with different search parameters"""
    print("Testing Videos Endpoint...")
    
    # Test basic videos list
    try:
        response = requests.get(f"{BASE_URL}/videos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = 'videos' in data and 'total' in data
            print_test_result("GET /videos (basic)", success, data)
        else:
            print_test_result("GET /videos (basic)", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("GET /videos (basic)", False, error=str(e))
        success = False
    
    # Test search functionality
    search_tests = [
        ("search=rock", "search by keyword"),
        ("search=queen&search_type=artist", "search by artist"),
        ("search=rock&search_type=song", "search by song"),
        ("search=test&search_type=all", "search all fields"),
        ("limit=10&skip=0", "pagination")
    ]
    
    for params, description in search_tests:
        try:
            response = requests.get(f"{BASE_URL}/videos?{params}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                test_success = 'videos' in data and 'total' in data
                print_test_result(f"GET /videos ({description})", test_success, {"count": len(data.get('videos', []))})
                success = success and test_success
            else:
                print_test_result(f"GET /videos ({description})", False, response.text, f"Status: {response.status_code}")
                success = False
        except Exception as e:
            print_test_result(f"GET /videos ({description})", False, error=str(e))
            success = False
    
    return success

def test_admin_login():
    """Test POST /admin/login endpoint"""
    print("Testing Admin Login...")
    
    # Test correct password
    try:
        payload = {"password": ADMIN_PASSWORD}
        response = requests.post(f"{BASE_URL}/admin/login", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('success') == True
            print_test_result("POST /admin/login (correct password)", success, data)
        else:
            print_test_result("POST /admin/login (correct password)", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("POST /admin/login (correct password)", False, error=str(e))
        success = False
    
    # Test wrong password
    try:
        payload = {"password": "wrongpassword"}
        response = requests.post(f"{BASE_URL}/admin/login", json=payload, timeout=10)
        wrong_pass_success = response.status_code == 401
        print_test_result("POST /admin/login (wrong password)", wrong_pass_success, {"status": response.status_code})
        success = success and wrong_pass_success
    except Exception as e:
        print_test_result("POST /admin/login (wrong password)", False, error=str(e))
        success = False
    
    return success

def test_admin_settings():
    """Test PUT /admin/settings endpoint"""
    print("Testing Admin Settings Update...")
    
    headers = create_basic_auth_header()
    headers['Content-Type'] = 'application/json'
    
    # Test settings update
    try:
        payload = {
            "featured_video_url": "https://www.youtube.com/watch?v=TEST123",
            "featured_video_title": "Test Song Title",
            "featured_video_artist": "Test Artist"
        }
        response = requests.put(f"{BASE_URL}/admin/settings", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            success = data.get('success') == True
            print_test_result("PUT /admin/settings", success, data)
        else:
            print_test_result("PUT /admin/settings", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("PUT /admin/settings", False, error=str(e))
        success = False
    
    # Test unauthorized access
    try:
        response = requests.put(f"{BASE_URL}/admin/settings", json=payload, timeout=10)
        unauth_success = response.status_code == 401
        print_test_result("PUT /admin/settings (unauthorized)", unauth_success, {"status": response.status_code})
        success = success and unauth_success
    except Exception as e:
        print_test_result("PUT /admin/settings (unauthorized)", False, error=str(e))
        success = False
    
    return success

def test_admin_stats():
    """Test GET /admin/stats endpoint"""
    print("Testing Admin Stats...")
    
    headers = create_basic_auth_header()
    
    try:
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['total_videos', 'total_artists']
            success = all(field in data for field in required_fields)
            print_test_result("GET /admin/stats", success, data)
        else:
            print_test_result("GET /admin/stats", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("GET /admin/stats", False, error=str(e))
        success = False
    
    # Test unauthorized access
    try:
        response = requests.get(f"{BASE_URL}/admin/stats", timeout=10)
        unauth_success = response.status_code == 401
        print_test_result("GET /admin/stats (unauthorized)", unauth_success, {"status": response.status_code})
        success = success and unauth_success
    except Exception as e:
        print_test_result("GET /admin/stats (unauthorized)", False, error=str(e))
        success = False
    
    return success

def test_video_crud():
    """Test full CRUD cycle for videos"""
    print("Testing Video CRUD Operations...")
    
    headers = create_basic_auth_header()
    headers['Content-Type'] = 'application/json'
    
    created_video_id = None
    
    # CREATE - Test POST /admin/videos
    try:
        payload = {
            "song": "Bohemian Rhapsody",
            "artist": "Queen",
            "youtube_url": "https://www.youtube.com/watch?v=fJ9rUzIMcZQ"
        }
        response = requests.post(f"{BASE_URL}/admin/videos", json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            data = response.json()
            created_video_id = data.get('id')
            required_fields = ['id', 'song', 'artist', 'youtube_url', 'thumbnail', 'created_at']
            success = all(field in data for field in required_fields) and created_video_id
            print_test_result("POST /admin/videos (create)", success, {"id": created_video_id, "song": data.get('song')})
        else:
            print_test_result("POST /admin/videos (create)", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("POST /admin/videos (create)", False, error=str(e))
        success = False
    
    if not created_video_id:
        print("❌ Cannot continue CRUD tests - video creation failed")
        return False
    
    # READ - Test GET /videos/:id
    try:
        response = requests.get(f"{BASE_URL}/videos/{created_video_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            read_success = data.get('id') == created_video_id and data.get('song') == "Bohemian Rhapsody"
            print_test_result("GET /videos/:id (read)", read_success, {"id": data.get('id'), "song": data.get('song')})
            success = success and read_success
        else:
            print_test_result("GET /videos/:id (read)", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("GET /videos/:id (read)", False, error=str(e))
        success = False
    
    # UPDATE - Test PUT /admin/videos/:id
    try:
        payload = {
            "song": "We Will Rock You",
            "artist": "Queen",
            "youtube_url": "https://www.youtube.com/watch?v=BT4AEyYXSKA"
        }
        response = requests.put(f"{BASE_URL}/admin/videos/{created_video_id}", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            update_success = data.get('id') == created_video_id and data.get('song') == "We Will Rock You"
            print_test_result("PUT /admin/videos/:id (update)", update_success, {"id": data.get('id'), "song": data.get('song')})
            success = success and update_success
        else:
            print_test_result("PUT /admin/videos/:id (update)", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("PUT /admin/videos/:id (update)", False, error=str(e))
        success = False
    
    # DELETE - Test DELETE /admin/videos/:id
    try:
        response = requests.delete(f"{BASE_URL}/admin/videos/{created_video_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            delete_success = 'message' in data
            print_test_result("DELETE /admin/videos/:id (delete)", delete_success, data)
            success = success and delete_success
        else:
            print_test_result("DELETE /admin/videos/:id (delete)", False, response.text, f"Status: {response.status_code}")
            success = False
    except Exception as e:
        print_test_result("DELETE /admin/videos/:id (delete)", False, error=str(e))
        success = False
    
    # Verify deletion - GET should return 404
    try:
        response = requests.get(f"{BASE_URL}/videos/{created_video_id}", timeout=10)
        verify_delete_success = response.status_code == 404
        print_test_result("GET /videos/:id (verify delete)", verify_delete_success, {"status": response.status_code})
        success = success and verify_delete_success
    except Exception as e:
        print_test_result("GET /videos/:id (verify delete)", False, error=str(e))
        success = False
    
    # Test unauthorized CRUD operations
    try:
        payload = {"song": "Test", "artist": "Test", "youtube_url": "https://www.youtube.com/watch?v=test"}
        response = requests.post(f"{BASE_URL}/admin/videos", json=payload, timeout=10)
        unauth_success = response.status_code == 401
        print_test_result("POST /admin/videos (unauthorized)", unauth_success, {"status": response.status_code})
        success = success and unauth_success
    except Exception as e:
        print_test_result("POST /admin/videos (unauthorized)", False, error=str(e))
        success = False
    
    return success

def main():
    """Run all backend tests"""
    print("=" * 60)
    print("DadRock Tabs Backend API Tests")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin Password: {ADMIN_PASSWORD}")
    print("=" * 60)
    print()
    
    # Track all test results
    test_results = {}
    
    # Run all tests
    test_results['health'] = test_health_endpoint()
    test_results['settings'], _ = test_settings_endpoint()
    test_results['videos'] = test_videos_endpoint()
    test_results['admin_login'] = test_admin_login()
    test_results['admin_settings'] = test_admin_settings()
    test_results['admin_stats'] = test_admin_stats()
    test_results['video_crud'] = test_video_crud()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print()
    print(f"Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All backend tests PASSED!")
        return True
    else:
        print("⚠️  Some backend tests FAILED!")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)