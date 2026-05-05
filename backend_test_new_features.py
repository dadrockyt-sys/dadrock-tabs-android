#!/usr/bin/env python3
"""
DadRock Tabs Backend Testing Script - NEW FEATURES
Tests: RSS Feed, Comments API, Share Card Image, What's New API, and regression checks
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

# Base URL from environment
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"

# User-Agent header required for page requests (not API)
USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1)"

def test_rss_feed():
    """Test RSS Feed API - GET /api/rss"""
    print("\n=== TESTING RSS FEED API ===")
    
    results = []
    
    try:
        url = f"{BASE_URL}/api/rss"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ GET /api/rss → 200")
            
            # Check Content-Type
            content_type = response.headers.get('Content-Type', '')
            if 'application/rss+xml' in content_type:
                print(f"✅ Content-Type: {content_type}")
                results.append(True)
            else:
                print(f"❌ Content-Type: {content_type} (expected application/rss+xml)")
                results.append(False)
            
            # Check XML structure
            content = response.text
            required_elements = [
                '<rss',
                '<channel>',
                '<item>',
                '<title>',
                '<link>',
                '<guid',
                '<description>',
                '<pubDate>',
                'atom:link'
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                print(f"✅ RSS XML contains all required elements: {', '.join(required_elements)}")
                results.append(True)
            else:
                print(f"❌ RSS XML missing elements: {', '.join(missing_elements)}")
                results.append(False)
            
            # Check for atom:link self-reference
            if 'rel="self"' in content and '/api/rss' in content:
                print(f"✅ Contains atom:link self-reference")
                results.append(True)
            else:
                print(f"❌ Missing atom:link self-reference")
                results.append(False)
            
            # Count items
            item_count = content.count('<item>')
            print(f"✅ RSS feed contains {item_count} items")
            results.append(True)
            
        else:
            print(f"❌ GET /api/rss → {response.status_code}")
            results.append(False)
            
    except Exception as e:
        print(f"❌ GET /api/rss → Error: {e}")
        results.append(False)
    
    return all(results)

def test_comments_api():
    """Test Comments and Ratings API - POST and GET /api/comments"""
    print("\n=== TESTING COMMENTS API ===")
    
    results = []
    
    # Test 1: POST a new comment with valid data
    try:
        url = f"{BASE_URL}/api/comments"
        test_comment = {
            "songSlug": "metallica-seek-and-destroy",
            "name": "TestUser",
            "comment": "Great song!",
            "rating": 4
        }
        response = requests.post(url, json=test_comment, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") == True and "comment" in data:
                comment = data["comment"]
                if (comment.get("songSlug") == "metallica-seek-and-destroy" and 
                    comment.get("name") == "TestUser" and
                    comment.get("rating") == 4):
                    print(f"✅ POST /api/comments with valid data → 200, success=true, comment returned")
                    results.append(True)
                else:
                    print(f"❌ POST /api/comments → 200 but comment data incorrect: {comment}")
                    results.append(False)
            else:
                print(f"❌ POST /api/comments → 200 but unexpected response: {data}")
                results.append(False)
        else:
            print(f"❌ POST /api/comments with valid data → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/comments with valid data → Error: {e}")
        results.append(False)
    
    # Test 2: GET comments for a song
    try:
        url = f"{BASE_URL}/api/comments?slug=metallica-seek-and-destroy"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "comments" in data and isinstance(data["comments"], list):
                print(f"✅ GET /api/comments?slug=metallica-seek-and-destroy → 200, returns {len(data['comments'])} comments")
                results.append(True)
            else:
                print(f"❌ GET /api/comments → 200 but missing comments array: {data}")
                results.append(False)
        else:
            print(f"❌ GET /api/comments?slug=metallica-seek-and-destroy → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/comments → Error: {e}")
        results.append(False)
    
    # Test 3: POST without name (should return 400)
    try:
        url = f"{BASE_URL}/api/comments"
        invalid_comment = {
            "songSlug": "metallica-seek-and-destroy",
            "comment": "Great song!"
        }
        response = requests.post(url, json=invalid_comment, timeout=30)
        
        if response.status_code == 400:
            print(f"✅ POST /api/comments without name → 400 (correct validation)")
            results.append(True)
        else:
            print(f"❌ POST /api/comments without name → {response.status_code} (expected 400)")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/comments without name → Error: {e}")
        results.append(False)
    
    # Test 4: POST without songSlug (should return 400)
    try:
        url = f"{BASE_URL}/api/comments"
        invalid_comment = {
            "name": "TestUser",
            "comment": "Great song!"
        }
        response = requests.post(url, json=invalid_comment, timeout=30)
        
        if response.status_code == 400:
            print(f"✅ POST /api/comments without songSlug → 400 (correct validation)")
            results.append(True)
        else:
            print(f"❌ POST /api/comments without songSlug → {response.status_code} (expected 400)")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/comments without songSlug → Error: {e}")
        results.append(False)
    
    # Test 5: GET without slug parameter (should return 400)
    try:
        url = f"{BASE_URL}/api/comments"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 400:
            print(f"✅ GET /api/comments without slug → 400 (correct validation)")
            results.append(True)
        else:
            print(f"❌ GET /api/comments without slug → {response.status_code} (expected 400)")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/comments without slug → Error: {e}")
        results.append(False)
    
    return all(results)

def test_share_card_api():
    """Test Share Card Image API - GET /api/share-card"""
    print("\n=== TESTING SHARE CARD IMAGE API ===")
    
    results = []
    
    # Test 1: Learned type
    try:
        url = f"{BASE_URL}/api/share-card?song=Test&artist=Artist&type=learned"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                print(f"✅ GET /api/share-card?type=learned → 200 with content-type: image/png")
                results.append(True)
            else:
                print(f"❌ GET /api/share-card?type=learned → 200 but wrong content-type: {content_type}")
                results.append(False)
        else:
            print(f"❌ GET /api/share-card?type=learned → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/share-card?type=learned → Error: {e}")
        results.append(False)
    
    # Test 2: Streak type
    try:
        url = f"{BASE_URL}/api/share-card?type=streak&value=7"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                print(f"✅ GET /api/share-card?type=streak&value=7 → 200 with content-type: image/png")
                results.append(True)
            else:
                print(f"❌ GET /api/share-card?type=streak → 200 but wrong content-type: {content_type}")
                results.append(False)
        else:
            print(f"❌ GET /api/share-card?type=streak → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/share-card?type=streak → Error: {e}")
        results.append(False)
    
    # Test 3: Badge type
    try:
        url = f"{BASE_URL}/api/share-card?type=badge&value=Guitar+Hero"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                print(f"✅ GET /api/share-card?type=badge&value=Guitar+Hero → 200 with content-type: image/png")
                results.append(True)
            else:
                print(f"❌ GET /api/share-card?type=badge → 200 but wrong content-type: {content_type}")
                results.append(False)
        else:
            print(f"❌ GET /api/share-card?type=badge → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/share-card?type=badge → Error: {e}")
        results.append(False)
    
    return all(results)

def test_whats_new_api():
    """Test What's New API - GET /api/whats-new"""
    print("\n=== TESTING WHAT'S NEW API ===")
    
    results = []
    
    try:
        url = f"{BASE_URL}/api/whats-new"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ GET /api/whats-new → 200")
            
            try:
                data = response.json()
                
                # Check for recentSongs array
                if "recentSongs" in data and isinstance(data["recentSongs"], list):
                    recent_songs = data["recentSongs"]
                    print(f"✅ Response contains recentSongs array with {len(recent_songs)} songs")
                    
                    # Check if songs have required fields
                    if len(recent_songs) > 0:
                        first_song = recent_songs[0]
                        required_fields = ["title", "artist", "slug"]
                        missing_fields = [f for f in required_fields if f not in first_song]
                        
                        if not missing_fields:
                            print(f"✅ Songs have required fields: {', '.join(required_fields)}")
                            results.append(True)
                        else:
                            print(f"❌ Songs missing fields: {', '.join(missing_fields)}")
                            results.append(False)
                    else:
                        print(f"⚠️  No songs in recentSongs array (empty database?)")
                        results.append(True)  # Not a failure if DB is empty
                else:
                    print(f"❌ Response missing recentSongs array: {data}")
                    results.append(False)
                
                # Check for stats object
                if "stats" in data and isinstance(data["stats"], dict):
                    stats = data["stats"]
                    if "totalSongs" in stats and "totalComments" in stats:
                        print(f"✅ Response contains stats: totalSongs={stats['totalSongs']}, totalComments={stats['totalComments']}")
                        results.append(True)
                    else:
                        print(f"❌ Stats missing totalSongs or totalComments: {stats}")
                        results.append(False)
                else:
                    print(f"❌ Response missing stats object: {data}")
                    results.append(False)
                    
            except json.JSONDecodeError:
                print(f"❌ GET /api/whats-new → 200 but invalid JSON")
                results.append(False)
        else:
            print(f"❌ GET /api/whats-new → {response.status_code}")
            results.append(False)
            
    except Exception as e:
        print(f"❌ GET /api/whats-new → Error: {e}")
        results.append(False)
    
    return all(results)

def test_existing_apis_regression():
    """Test existing APIs to ensure they still work"""
    print("\n=== TESTING EXISTING APIS (REGRESSION) ===")
    
    results = []
    
    # Test 1: GET /api/random-song
    try:
        url = f"{BASE_URL}/api/random-song"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "slug" in data:
                print(f"✅ GET /api/random-song → 200 with slug: {data['slug']}")
                results.append(True)
            else:
                print(f"❌ GET /api/random-song → 200 but missing slug: {data}")
                results.append(False)
        else:
            print(f"❌ GET /api/random-song → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/random-song → Error: {e}")
        results.append(False)
    
    # Test 2: GET /api/search?q=metallica
    try:
        url = f"{BASE_URL}/api/search?q=metallica"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "artists" in data and "songs" in data:
                print(f"✅ GET /api/search?q=metallica → 200 with {len(data['artists'])} artists, {len(data['songs'])} songs")
                results.append(True)
            else:
                print(f"❌ GET /api/search?q=metallica → 200 but missing artists/songs: {data}")
                results.append(False)
        else:
            print(f"❌ GET /api/search?q=metallica → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/search?q=metallica → Error: {e}")
        results.append(False)
    
    # Test 3: POST /api/newsletter
    try:
        url = f"{BASE_URL}/api/newsletter"
        test_email = f"test-regression-{int(time.time())}@test.com"
        response = requests.post(url, json={"email": test_email}, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ POST /api/newsletter → 200")
            results.append(True)
        else:
            print(f"❌ POST /api/newsletter → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/newsletter → Error: {e}")
        results.append(False)
    
    # Test 4: GET /api/song-of-the-day
    try:
        url = f"{BASE_URL}/api/song-of-the-day"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "song" in data and "slug" in data["song"]:
                print(f"✅ GET /api/song-of-the-day → 200 with song data")
                results.append(True)
            else:
                print(f"❌ GET /api/song-of-the-day → 200 but missing song data: {data}")
                results.append(False)
        else:
            print(f"❌ GET /api/song-of-the-day → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/song-of-the-day → Error: {e}")
        results.append(False)
    
    # Test 5: GET /api/og?title=Test&type=song
    try:
        url = f"{BASE_URL}/api/og?title=Test&type=song"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'image/png' in content_type:
                print(f"✅ GET /api/og?title=Test&type=song → 200 with image/png")
                results.append(True)
            else:
                print(f"❌ GET /api/og → 200 but wrong content-type: {content_type}")
                results.append(False)
        else:
            print(f"❌ GET /api/og?title=Test&type=song → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/og → Error: {e}")
        results.append(False)
    
    return all(results)

def main():
    """Run all tests and provide summary"""
    print(f"🎸 DadRock Tabs Backend Testing - NEW FEATURES")
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {USER_AGENT}")
    
    # Run all test suites
    rss_results = test_rss_feed()
    comments_results = test_comments_api()
    share_card_results = test_share_card_api()
    whats_new_results = test_whats_new_api()
    regression_results = test_existing_apis_regression()
    
    # Summary
    print(f"\n=== TEST SUMMARY ===")
    print(f"RSS Feed API: {'✅ PASS' if rss_results else '❌ FAIL'}")
    print(f"Comments API: {'✅ PASS' if comments_results else '❌ FAIL'}")
    print(f"Share Card Image API: {'✅ PASS' if share_card_results else '❌ FAIL'}")
    print(f"What's New API: {'✅ PASS' if whats_new_results else '❌ FAIL'}")
    print(f"Existing APIs (Regression): {'✅ PASS' if regression_results else '❌ FAIL'}")
    
    all_passed = all([rss_results, comments_results, share_card_results, whats_new_results, regression_results])
    print(f"\nOVERALL: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
