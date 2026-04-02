#!/usr/bin/env python3
"""
Backend Test Suite for DadRock Tabs Website Health Check API
Tests the /api/admin/health endpoint with various modes and authentication scenarios.
"""

import requests
import json
import base64
import time
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Babyty99"

def create_auth_header(username, password):
    """Create Basic Auth header"""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}

def test_health_check_api():
    """Test the Website Health Check API at /api/admin/health"""
    print("=" * 80)
    print("TESTING: Website Health Check API (/api/admin/health)")
    print("=" * 80)
    
    results = []
    
    # Test 1: GET /api/admin/health without auth → expect 401
    print("\n1. Testing GET /api/admin/health without auth (expect 401)")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/health", timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 401:
            print("   ✅ PASS: Correctly returned 401 for unauthorized access")
            results.append(("Auth check (no auth)", True))
        else:
            print(f"   ❌ FAIL: Expected 401, got {response.status_code}")
            results.append(("Auth check (no auth)", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Auth check (no auth)", False))
    
    # Test 2: GET /api/admin/health with wrong password → expect 401
    print("\n2. Testing GET /api/admin/health with wrong password (expect 401)")
    try:
        wrong_auth = create_auth_header(ADMIN_USERNAME, "wrongpassword")
        response = requests.get(f"{BASE_URL}/api/admin/health", headers=wrong_auth, timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 401:
            print("   ✅ PASS: Correctly returned 401 for wrong password")
            results.append(("Auth check (wrong password)", True))
        else:
            print(f"   ❌ FAIL: Expected 401, got {response.status_code}")
            results.append(("Auth check (wrong password)", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Auth check (wrong password)", False))
    
    # Test 3: GET /api/admin/health?mode=quick with auth → expect 200
    print("\n3. Testing GET /api/admin/health?mode=quick with auth (expect 200)")
    try:
        auth_header = create_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
        response = requests.get(f"{BASE_URL}/api/admin/health?mode=quick", headers=auth_header, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for expected checks
            expected_checks = ['database', 'api_endpoints', 'sitemap', 'robots']
            checks = data.get('checks', {})
            print(f"   Available checks: {list(checks.keys())}")
            
            all_checks_present = all(check in checks for check in expected_checks)
            if all_checks_present:
                print("   ✅ PASS: All expected checks present (database, api_endpoints, sitemap, robots)")
                results.append(("Quick mode", True))
            else:
                missing = [c for c in expected_checks if c not in checks]
                print(f"   ❌ FAIL: Missing checks: {missing}")
                results.append(("Quick mode", False))
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            results.append(("Quick mode", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Quick mode", False))
    
    # Test 4: GET /api/admin/health?mode=videos_only with auth → expect 200 (10-30s timeout)
    print("\n4. Testing GET /api/admin/health?mode=videos_only with auth (expect 200, 60s timeout)")
    try:
        auth_header = create_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/admin/health?mode=videos_only", headers=auth_header, timeout=60)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Duration: {duration:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            checks = data.get('checks', {})
            print(f"   Available checks: {list(checks.keys())}")
            
            # Should have database and dead_videos checks
            expected_checks = ['database', 'dead_videos']
            all_checks_present = all(check in checks for check in expected_checks)
            
            if all_checks_present:
                print("   ✅ PASS: Videos only mode working with database and dead_videos checks")
                results.append(("Videos only mode", True))
            else:
                missing = [c for c in expected_checks if c not in checks]
                print(f"   ❌ FAIL: Missing checks: {missing}")
                results.append(("Videos only mode", False))
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            results.append(("Videos only mode", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("Videos only mode", False))
    
    # Test 5: GET /api/admin/health?mode=urls_only with auth → expect 200 (30-120s timeout)
    print("\n5. Testing GET /api/admin/health?mode=urls_only with auth (expect 200, 180s timeout)")
    try:
        auth_header = create_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/admin/health?mode=urls_only", headers=auth_header, timeout=180)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   Status: {response.status_code}")
        print(f"   Duration: {duration:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            checks = data.get('checks', {})
            print(f"   Available checks: {list(checks.keys())}")
            
            # Should have database and internal_urls checks
            expected_checks = ['database', 'internal_urls']
            all_checks_present = all(check in checks for check in expected_checks)
            
            if all_checks_present:
                print("   ✅ PASS: URLs only mode working with database and internal_urls checks")
                results.append(("URLs only mode", True))
            else:
                missing = [c for c in expected_checks if c not in checks]
                print(f"   ❌ FAIL: Missing checks: {missing}")
                results.append(("URLs only mode", False))
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            results.append(("URLs only mode", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("URLs only mode", False))
    
    # Test 6: POST /api/admin/health with remove_dead_videos action → expect 200
    print("\n6. Testing POST /api/admin/health with remove_dead_videos action (expect 200)")
    try:
        auth_header = create_auth_header(ADMIN_USERNAME, ADMIN_PASSWORD)
        payload = {
            "action": "remove_dead_videos",
            "video_ids": ["nonexistent-id"]
        }
        response = requests.post(f"{BASE_URL}/api/admin/health", 
                               headers={**auth_header, "Content-Type": "application/json"}, 
                               json=payload, 
                               timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            
            # Should have removed_count of 0 since ID doesn't exist
            removed_count = data.get('removed_count', -1)
            if removed_count == 0:
                print("   ✅ PASS: Correctly returned removed_count=0 for nonexistent ID")
                results.append(("POST remove dead videos", True))
            else:
                print(f"   ❌ FAIL: Expected removed_count=0, got {removed_count}")
                results.append(("POST remove dead videos", False))
        else:
            print(f"   ❌ FAIL: Expected 200, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            results.append(("POST remove dead videos", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("POST remove dead videos", False))
    
    # Test 7: POST /api/admin/health without auth → expect 401
    print("\n7. Testing POST /api/admin/health without auth (expect 401)")
    try:
        payload = {
            "action": "remove_dead_videos",
            "video_ids": ["test-id"]
        }
        response = requests.post(f"{BASE_URL}/api/admin/health", 
                               headers={"Content-Type": "application/json"}, 
                               json=payload, 
                               timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code == 401:
            print("   ✅ PASS: Correctly returned 401 for unauthorized POST")
            results.append(("POST unauthorized", True))
        else:
            print(f"   ❌ FAIL: Expected 401, got {response.status_code}")
            results.append(("POST unauthorized", False))
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        results.append(("POST unauthorized", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("HEALTH CHECK API TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Website Health Check API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    print("Starting Website Health Check API Tests...")
    print(f"Base URL: {BASE_URL}")
    print(f"Testing endpoint: /api/admin/health")
    
    success = test_health_check_api()
    
    if success:
        exit(0)
    else:
        exit(1)