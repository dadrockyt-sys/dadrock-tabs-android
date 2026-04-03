#!/usr/bin/env python3
"""
Backend API Testing for DadRock Tabs - AI SEO Content APIs
Tests the AI SEO Content Generation and Retrieval endpoints
"""

import requests
import json
import base64
import os
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "Babyty99"

# Required User-Agent header (middleware blocks requests without proper UA)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json"
}

def get_auth_headers():
    """Get headers with Basic Auth for admin endpoints"""
    auth_string = f"{ADMIN_USER}:{ADMIN_PASSWORD}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Basic {auth_b64}"
    return headers

def test_seo_content_retrieval():
    """Test GET /api/seo-content endpoint (public)"""
    print("\n" + "="*60)
    print("TESTING: SEO Content Retrieval API (GET /api/seo-content)")
    print("="*60)
    
    test_cases = [
        {
            "name": "Get AC/DC content by slug",
            "params": {"type": "artist", "slug": "acdc"},
            "expected_found": True
        },
        {
            "name": "Get Pantera content by slug", 
            "params": {"type": "artist", "slug": "pantera"},
            "expected_found": True
        },
        {
            "name": "Get nonexistent artist content",
            "params": {"type": "artist", "slug": "nonexistent-artist"},
            "expected_found": False
        },
        {
            "name": "Get AC/DC content by name",
            "params": {"type": "artist", "name": "AC/DC"},
            "expected_found": True
        },
        {
            "name": "Get song content (should not exist yet)",
            "params": {"type": "song", "slug": "some-song"},
            "expected_found": False
        },
        {
            "name": "Missing parameters (should return 400)",
            "params": {},
            "expected_status": 400
        },
        {
            "name": "Invalid type parameter",
            "params": {"type": "invalid", "slug": "test"},
            "expected_status": 400
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n{i}. {test_case['name']}")
            
            url = f"{BASE_URL}/api/seo-content"
            response = requests.get(url, params=test_case['params'], headers=HEADERS, timeout=10)
            
            print(f"   Request: GET {url}?{requests.compat.urlencode(test_case['params'])}")
            print(f"   Status: {response.status_code}")
            
            # Check expected status code
            expected_status = test_case.get('expected_status', 200)
            if response.status_code != expected_status:
                print(f"   ❌ FAIL: Expected status {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                continue
            
            if response.status_code == 400:
                print(f"   ✅ PASS: Correctly returned 400 error")
                passed += 1
                continue
                
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            # Check found status
            if 'expected_found' in test_case:
                expected_found = test_case['expected_found']
                actual_found = data.get('found', False)
                
                if actual_found == expected_found:
                    if expected_found:
                        # Verify content structure for found items
                        required_fields = ['found', 'type', 'content']
                        if test_case['params'].get('type') == 'artist':
                            required_fields.extend(['name', 'slug'])
                        
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            print(f"   ❌ FAIL: Missing required fields: {missing_fields}")
                            continue
                        
                        # Check content structure
                        content = data.get('content', {})
                        if isinstance(content, dict) and content:
                            print(f"   Content sections: {list(content.keys())}")
                            print(f"   ✅ PASS: Found content with proper structure")
                        else:
                            print(f"   ❌ FAIL: Content is not a valid object")
                            continue
                    else:
                        print(f"   ✅ PASS: Correctly returned found=false")
                    passed += 1
                else:
                    print(f"   ❌ FAIL: Expected found={expected_found}, got found={actual_found}")
            else:
                print(f"   ✅ PASS: Request completed successfully")
                passed += 1
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAIL: Request error - {e}")
        except json.JSONDecodeError as e:
            print(f"   ❌ FAIL: JSON decode error - {e}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ FAIL: Unexpected error - {e}")
    
    print(f"\n📊 SEO Content Retrieval Results: {passed}/{total} tests passed")
    return passed == total

def test_admin_generate_seo_get():
    """Test GET /api/admin/generate-seo endpoint (admin stats)"""
    print("\n" + "="*60)
    print("TESTING: Admin SEO Generation Stats (GET /api/admin/generate-seo)")
    print("="*60)
    
    test_cases = [
        {
            "name": "Unauthorized access (no auth)",
            "headers": HEADERS,
            "expected_status": 401
        },
        {
            "name": "Wrong credentials",
            "headers": {**HEADERS, "Authorization": "Basic " + base64.b64encode(b"admin:wrongpass").decode()},
            "expected_status": 401
        },
        {
            "name": "Valid admin access",
            "headers": get_auth_headers(),
            "expected_status": 200
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n{i}. {test_case['name']}")
            
            url = f"{BASE_URL}/api/admin/generate-seo"
            response = requests.get(url, headers=test_case['headers'], timeout=10)
            
            print(f"   Request: GET {url}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code != test_case['expected_status']:
                print(f"   ❌ FAIL: Expected status {test_case['expected_status']}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                continue
            
            if response.status_code == 401:
                print(f"   ✅ PASS: Correctly rejected unauthorized access")
                passed += 1
                continue
            
            # For successful response, check structure
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            required_fields = ['success', 'artists', 'songs', 'api_configured']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing required fields: {missing_fields}")
                continue
            
            # Check artists and songs structure
            artists = data.get('artists', {})
            songs = data.get('songs', {})
            
            artist_fields = ['total', 'with_ai_content', 'without_ai_content']
            song_fields = ['total', 'with_ai_content', 'without_ai_content']
            
            missing_artist_fields = [field for field in artist_fields if field not in artists]
            missing_song_fields = [field for field in song_fields if field not in songs]
            
            if missing_artist_fields or missing_song_fields:
                print(f"   ❌ FAIL: Missing artist fields: {missing_artist_fields}, song fields: {missing_song_fields}")
                continue
            
            print(f"   Artists: {artists['total']} total, {artists['with_ai_content']} with AI content")
            print(f"   Songs: {songs['total']} total, {songs['with_ai_content']} with AI content")
            print(f"   API configured: {data['api_configured']}")
            print(f"   ✅ PASS: Valid stats response structure")
            passed += 1
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAIL: Request error - {e}")
        except json.JSONDecodeError as e:
            print(f"   ❌ FAIL: JSON decode error - {e}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ FAIL: Unexpected error - {e}")
    
    print(f"\n📊 Admin SEO Stats Results: {passed}/{total} tests passed")
    return passed == total

def test_admin_generate_seo_post():
    """Test POST /api/admin/generate-seo endpoint (AI content generation)"""
    print("\n" + "="*60)
    print("TESTING: Admin SEO Content Generation (POST /api/admin/generate-seo)")
    print("="*60)
    
    test_cases = [
        {
            "name": "Unauthorized access (no auth)",
            "headers": HEADERS,
            "body": {"action": "generate_artist", "artist_name": "Test Artist"},
            "expected_status": 401
        },
        {
            "name": "Wrong credentials",
            "headers": {**HEADERS, "Authorization": "Basic " + base64.b64encode(b"admin:wrongpass").decode()},
            "body": {"action": "generate_artist", "artist_name": "Test Artist"},
            "expected_status": 401
        },
        {
            "name": "Missing action parameter",
            "headers": get_auth_headers(),
            "body": {"artist_name": "Test Artist"},
            "expected_status": 400
        },
        {
            "name": "Generate AC/DC content (should be cached)",
            "headers": get_auth_headers(),
            "body": {"action": "generate_artist", "artist_name": "AC/DC"},
            "expected_status": 200,
            "expected_cached": True
        },
        {
            "name": "Generate Pantera content (should be cached)",
            "headers": get_auth_headers(),
            "body": {"action": "generate_artist", "artist_name": "Pantera"},
            "expected_status": 200,
            "expected_cached": True
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n{i}. {test_case['name']}")
            
            url = f"{BASE_URL}/api/admin/generate-seo"
            response = requests.post(
                url, 
                headers=test_case['headers'], 
                json=test_case['body'],
                timeout=30  # Longer timeout for AI generation
            )
            
            print(f"   Request: POST {url}")
            print(f"   Body: {json.dumps(test_case['body'])}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code != test_case['expected_status']:
                print(f"   ❌ FAIL: Expected status {test_case['expected_status']}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                continue
            
            if response.status_code == 401:
                print(f"   ✅ PASS: Correctly rejected unauthorized access")
                passed += 1
                continue
            
            if response.status_code == 400:
                print(f"   ✅ PASS: Correctly returned 400 for invalid request")
                passed += 1
                continue
            
            # For successful response, check structure
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            required_fields = ['success']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"   ❌ FAIL: Missing required fields: {missing_fields}")
                continue
            
            if not data.get('success'):
                print(f"   ❌ FAIL: Success field is false")
                print(f"   Response: {json.dumps(data, indent=2)}")
                continue
            
            # Check if cached response is as expected
            if 'expected_cached' in test_case:
                expected_cached = test_case['expected_cached']
                actual_cached = data.get('cached', False)
                
                if actual_cached == expected_cached:
                    if expected_cached:
                        print(f"   ✅ PASS: Content already exists (cached=true)")
                    else:
                        print(f"   ✅ PASS: New content generated (cached=false)")
                    passed += 1
                else:
                    print(f"   ❌ FAIL: Expected cached={expected_cached}, got cached={actual_cached}")
            else:
                print(f"   ✅ PASS: Request completed successfully")
                passed += 1
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ FAIL: Request error - {e}")
        except json.JSONDecodeError as e:
            print(f"   ❌ FAIL: JSON decode error - {e}")
            print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ FAIL: Unexpected error - {e}")
    
    print(f"\n📊 Admin SEO Generation Results: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all AI SEO Content API tests"""
    print("🚀 Starting AI SEO Content API Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"Testing with User-Agent: {HEADERS['User-Agent']}")
    
    results = []
    
    # Test SEO Content Retrieval API
    results.append(test_seo_content_retrieval())
    
    # Test Admin SEO Generation Stats
    results.append(test_admin_generate_seo_get())
    
    # Test Admin SEO Content Generation
    results.append(test_admin_generate_seo_post())
    
    # Final summary
    print("\n" + "="*60)
    print("🏁 FINAL TEST SUMMARY")
    print("="*60)
    
    test_names = [
        "SEO Content Retrieval API",
        "Admin SEO Generation Stats", 
        "Admin SEO Content Generation"
    ]
    
    passed_count = sum(results)
    total_count = len(results)
    
    for i, (name, passed) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n📊 Overall Results: {passed_count}/{total_count} test suites passed")
    
    if passed_count == total_count:
        print("🎉 All AI SEO Content API tests PASSED!")
        return True
    else:
        print("⚠️  Some tests FAILED - check details above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)