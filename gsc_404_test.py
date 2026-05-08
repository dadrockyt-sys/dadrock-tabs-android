#!/usr/bin/env python3
"""
Backend Testing for GSC 404 Fix Changes
Tests artist and song page redirects to verify 308 permanent redirects work correctly.
"""

import requests
import sys
import os
from urllib.parse import urljoin

# Base URL from environment
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"

# Required User-Agent header (middleware blocks requests without proper UA)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def test_url(path, expected_status, expected_redirect_to=None, description=""):
    """Test a URL and verify response status and redirect behavior"""
    url = urljoin(BASE_URL, path)
    print(f"\n🔍 Testing: {path}")
    print(f"   Description: {description}")
    print(f"   Full URL: {url}")
    
    try:
        # Don't follow redirects automatically so we can check the initial response
        response = requests.get(url, headers=HEADERS, allow_redirects=False, timeout=30)
        
        print(f"   ✅ Initial Response: {response.status_code}")
        
        if expected_redirect_to:
            if response.status_code in [301, 302, 307, 308]:
                location = response.headers.get('Location', '')
                print(f"   ✅ Redirect Location: {location}")
                
                # Follow the redirect to check final status
                if location:
                    if location.startswith('/'):
                        final_url = urljoin(BASE_URL, location)
                    else:
                        final_url = location
                    
                    final_response = requests.get(final_url, headers=HEADERS, timeout=30)
                    print(f"   ✅ Final Response: {final_response.status_code}")
                    
                    # Check if redirect target matches expected
                    if expected_redirect_to in location or location.endswith(expected_redirect_to):
                        print(f"   ✅ PASS: Redirected to expected location")
                        return True
                    else:
                        print(f"   ❌ FAIL: Expected redirect to '{expected_redirect_to}', got '{location}'")
                        return False
                else:
                    print(f"   ❌ FAIL: No Location header in redirect response")
                    return False
            else:
                print(f"   ❌ FAIL: Expected redirect status, got {response.status_code}")
                return False
        else:
            # No redirect expected, check status directly
            if response.status_code == expected_status:
                print(f"   ✅ PASS: Got expected status {expected_status}")
                return True
            else:
                print(f"   ❌ FAIL: Expected {expected_status}, got {response.status_code}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERROR: Request failed - {e}")
        return False

def main():
    """Run all GSC 404 fix tests"""
    print("=" * 80)
    print("🚀 TESTING GSC 404 FIX CHANGES")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {HEADERS['User-Agent']}")
    
    test_results = []
    
    # ===== ARTIST PAGE TESTS =====
    print("\n" + "=" * 50)
    print("🎸 ARTIST PAGE TESTS")
    print("=" * 50)
    
    # Valid artists should return 200
    test_results.append(test_url(
        "/artist/tesla", 200, None,
        "Valid artist - should return 200"
    ))
    
    test_results.append(test_url(
        "/artist/metallica", 200, None,
        "Valid artist - should return 200"
    ))
    
    test_results.append(test_url(
        "/artist/acdc", 200, None,
        "Valid artist with special slug - should return 200"
    ))
    
    test_results.append(test_url(
        "/artist/george-lynch-electric", 200, None,
        "Valid artist via fallback matching - should return 200"
    ))
    
    test_results.append(test_url(
        "/artist/reb-beach", 200, None,
        "Valid artist via fallback matching - should return 200"
    ))
    
    # Invalid artists should return 308 redirect to homepage
    test_results.append(test_url(
        "/artist/the-great-80s", 308, "/",
        "Slug doesn't match DB entry 'The Great 80's' - should 308 redirect to /"
    ))
    
    test_results.append(test_url(
        "/artist/totally-nonexistent-artist", 308, "/",
        "Artist not in DB - should 308 redirect to /"
    ))
    
    # ===== SONG PAGE TESTS =====
    print("\n" + "=" * 50)
    print("🎵 SONG PAGE TESTS")
    print("=" * 50)
    
    # Valid songs should return 200
    test_results.append(test_url(
        "/songs/metallica-am-i-evil", 200, None,
        "Valid song in song_pages - should return 200"
    ))
    
    test_results.append(test_url(
        "/songs/metallica-ride-the-lightning", 200, None,
        "Valid song - should return 200"
    ))
    
    # Missing songs with artist match should redirect to artist page
    test_results.append(test_url(
        "/songs/van-halen-best-of-both-worlds", 308, "/artist/van-halen",
        "Missing song but artist found - should 308 redirect to /artist/van-halen"
    ))
    
    # Songs handled by middleware redirect
    test_results.append(test_url(
        "/songs/pantera-walk", 301, "/artist/pantera",
        "Middleware redirect - should 301 redirect to /artist/pantera"
    ))
    
    # Completely nonexistent songs should redirect to homepage
    test_results.append(test_url(
        "/songs/totally-nonexistent-song", 308, "/",
        "No artist match - should 308 redirect to /"
    ))
    
    # ===== LOCALIZED URL TESTS =====
    print("\n" + "=" * 50)
    print("🌍 LOCALIZED URL TESTS")
    print("=" * 50)
    
    test_results.append(test_url(
        "/ja/artist/black-sabbath", 200, None,
        "Locale + valid artist - should return 200"
    ))
    
    test_results.append(test_url(
        "/ko/quickies", 200, None,
        "Locale + valid page - should return 200"
    ))
    
    test_results.append(test_url(
        "/zh/coming-soon", 200, None,
        "Locale + valid page - should return 200"
    ))
    
    # Trailing dash handling
    test_results.append(test_url(
        "/ja/artist/reb-beach-", 301, "/ja/artist/reb-beach",
        "Trailing dash strip - should 301 redirect to clean URL"
    ))
    
    # ===== EXISTING FUNCTIONALITY VERIFICATION =====
    print("\n" + "=" * 50)
    print("🔧 EXISTING FUNCTIONALITY VERIFICATION")
    print("=" * 50)
    
    test_results.append(test_url(
        "/", 200, None,
        "Homepage - should return 200"
    ))
    
    test_results.append(test_url(
        "/artist/acdc-", 301, "/artist/acdc",
        "Trailing dash - should 301 redirect to clean URL"
    ))
    
    test_results.append(test_url(
        "/favicon.ico", 200, None,
        "Favicon - should return 200"
    ))
    
    # ===== RESULTS SUMMARY =====
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(test_results)
    total = len(test_results)
    failed = total - passed
    
    print(f"✅ PASSED: {passed}/{total}")
    print(f"❌ FAILED: {failed}/{total}")
    print(f"📈 SUCCESS RATE: {(passed/total)*100:.1f}%")
    
    if failed > 0:
        print(f"\n⚠️  {failed} test(s) failed. Check output above for details.")
        return False
    else:
        print(f"\n🎉 All tests passed! GSC 404 fix is working correctly.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)