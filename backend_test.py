#!/usr/bin/env python3
"""
Backend Testing Script for DadRock Tabs SEO Features
Tests the new Search API and FAQ Schema features
"""

import requests
import json
import re
from urllib.parse import quote_plus

# Base URL from environment
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"

# Required User-Agent header (middleware blocks requests without proper UA)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
}

def test_search_api():
    """Test the new Search API endpoint (/api/search)"""
    print("🔍 TESTING SEARCH API")
    print("=" * 50)
    
    test_cases = [
        # Test case 1: Search for "metal" - should return Metallica
        {
            "name": "Search for 'metal'",
            "query": "metal",
            "expected_artists": ["Metallica"],
            "should_have_songs": True
        },
        # Test case 2: Search for "van halen"
        {
            "name": "Search for 'van halen'",
            "query": "van+halen",
            "expected_artists": ["Van Halen"],
            "should_have_songs": True
        },
        # Test case 3: Query too short (< 2 chars)
        {
            "name": "Query too short 'a'",
            "query": "a",
            "expected_artists": [],
            "should_have_songs": False
        },
        # Test case 4: Empty query
        {
            "name": "Empty query",
            "query": "",
            "expected_artists": [],
            "should_have_songs": False
        },
        # Test case 5: Search for "zz top"
        {
            "name": "Search for 'zz top'",
            "query": "zz+top",
            "expected_artists": ["ZZ Top"],
            "should_have_songs": True
        },
        # Test case 6: Nonexistent band
        {
            "name": "Nonexistent band",
            "query": "nonexistentbandxyz123",
            "expected_artists": [],
            "should_have_songs": False
        },
        # Test case 7: Search for "sabbath"
        {
            "name": "Search for 'sabbath'",
            "query": "sabbath",
            "expected_artists": ["Black Sabbath"],
            "should_have_songs": True
        },
        # Test case 8: Search for song "am i evil"
        {
            "name": "Search for song 'am i evil'",
            "query": "am+i+evil",
            "expected_artists": [],
            "should_have_songs": True,
            "expected_songs": ["Am I Evil"]
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        try:
            print(f"\n{i}. {test['name']}")
            url = f"{BASE_URL}/api/search?q={test['query']}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ FAILED: Expected 200, got {response.status_code}")
                continue
            
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Check response structure
            if 'artists' not in data or 'songs' not in data:
                print(f"   ❌ FAILED: Missing 'artists' or 'songs' in response")
                continue
            
            # Check artists
            artists_found = [artist['name'] for artist in data['artists']]
            if test['expected_artists']:
                found_expected = any(expected in artists_found for expected in test['expected_artists'])
                if not found_expected:
                    print(f"   ❌ FAILED: Expected artists {test['expected_artists']}, got {artists_found}")
                    continue
            else:
                if len(artists_found) > 0:
                    print(f"   ❌ FAILED: Expected no artists, got {artists_found}")
                    continue
            
            # Check songs
            songs_found = [song['title'] for song in data['songs']]
            if test.get('expected_songs'):
                found_expected_song = any(expected in str(songs_found) for expected in test['expected_songs'])
                if not found_expected_song:
                    print(f"   ❌ FAILED: Expected songs containing {test['expected_songs']}, got {songs_found}")
                    continue
            
            if test['should_have_songs']:
                if len(songs_found) == 0 and len(artists_found) == 0:
                    print(f"   ❌ FAILED: Expected some results, got none")
                    continue
            else:
                if len(songs_found) > 0 or len(artists_found) > 0:
                    print(f"   ❌ FAILED: Expected no results, got artists: {artists_found}, songs: {songs_found}")
                    continue
            
            print(f"   ✅ PASSED")
            passed += 1
            
        except Exception as e:
            print(f"   ❌ FAILED: Exception - {str(e)}")
    
    print(f"\n🔍 SEARCH API RESULTS: {passed}/{total} tests passed")
    return passed == total

def test_faq_schema():
    """Test FAQ Schema on artist pages"""
    print("\n📋 TESTING FAQ SCHEMA")
    print("=" * 50)
    
    test_cases = [
        # Test case 9: Metallica artist page
        {
            "name": "Metallica artist page FAQ schema",
            "url": f"{BASE_URL}/artist/metallica",
            "artist": "Metallica"
        },
        # Test case 10: Check for Question type
        {
            "name": "Metallica page has Question types",
            "url": f"{BASE_URL}/artist/metallica",
            "artist": "Metallica"
        },
        # Test case 11: Check for at least 5 FAQ questions
        {
            "name": "Metallica page has at least 5 FAQ questions",
            "url": f"{BASE_URL}/artist/metallica",
            "artist": "Metallica"
        },
        # Test case 12: AC/DC artist page
        {
            "name": "AC/DC artist page FAQ schema",
            "url": f"{BASE_URL}/artist/acdc",
            "artist": "AC/DC"
        },
        # Test case 13: Van Halen artist page
        {
            "name": "Van Halen artist page FAQ schema",
            "url": f"{BASE_URL}/artist/van-halen",
            "artist": "Van Halen"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 9):  # Start from 9 to continue numbering
        try:
            print(f"\n{i}. {test['name']}")
            response = requests.get(test['url'], headers=HEADERS, timeout=10)
            
            print(f"   URL: {test['url']}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ FAILED: Expected 200, got {response.status_code}")
                continue
            
            html_content = response.text
            
            # Check for FAQPage schema
            if '"@type":"FAQPage"' not in html_content and '"@type": "FAQPage"' not in html_content:
                print(f"   ❌ FAILED: No FAQPage schema found in HTML")
                continue
            
            # Check for Question schema
            if '"@type":"Question"' not in html_content and '"@type": "Question"' not in html_content:
                print(f"   ❌ FAILED: No Question schema found in HTML")
                continue
            
            # Count FAQ questions
            question_count = html_content.count('"@type":"Question"') + html_content.count('"@type": "Question"')
            print(f"   Found {question_count} FAQ questions")
            
            if question_count < 5:
                print(f"   ❌ FAILED: Expected at least 5 FAQ questions, found {question_count}")
                continue
            
            # Check for artist name in FAQ content
            if test['artist'].lower() not in html_content.lower():
                print(f"   ❌ FAILED: Artist name '{test['artist']}' not found in FAQ content")
                continue
            
            print(f"   ✅ PASSED: Found FAQPage schema with {question_count} questions")
            passed += 1
            
        except Exception as e:
            print(f"   ❌ FAILED: Exception - {str(e)}")
    
    print(f"\n📋 FAQ SCHEMA RESULTS: {passed}/{total} tests passed")
    return passed == total

def test_previous_features():
    """Test that previous features still work"""
    print("\n🔄 TESTING PREVIOUS FEATURES")
    print("=" * 50)
    
    test_cases = [
        # Test case 14: Metallica page still has other schemas
        {
            "name": "Metallica page has BreadcrumbList, MusicGroup, CollectionPage schemas",
            "url": f"{BASE_URL}/artist/metallica",
            "expected_schemas": ["BreadcrumbList", "MusicGroup", "CollectionPage"]
        },
        # Test case 15: Song page still has MusicRecording schema
        {
            "name": "Song page has MusicRecording schema",
            "url": f"{BASE_URL}/songs/metallica-am-i-evil",
            "expected_schemas": ["MusicRecording"]
        },
        # Test case 16: Invalid artist redirects
        {
            "name": "Invalid artist redirects to homepage",
            "url": f"{BASE_URL}/artist/totally-nonexistent",
            "expected_status": 308
        },
        # Test case 17: Homepage works
        {
            "name": "Homepage works",
            "url": f"{BASE_URL}/",
            "expected_status": 200
        },
        # Test case 18: Sitemap works
        {
            "name": "Sitemap works",
            "url": f"{BASE_URL}/sitemap.xml",
            "expected_status": 200
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 14):  # Start from 14 to continue numbering
        try:
            print(f"\n{i}. {test['name']}")
            response = requests.get(test['url'], headers=HEADERS, timeout=10, allow_redirects=False)
            
            print(f"   URL: {test['url']}")
            print(f"   Status: {response.status_code}")
            
            expected_status = test.get('expected_status', 200)
            if response.status_code != expected_status:
                print(f"   ❌ FAILED: Expected {expected_status}, got {response.status_code}")
                continue
            
            if 'expected_schemas' in test:
                html_content = response.text
                missing_schemas = []
                for schema in test['expected_schemas']:
                    if f'"@type":"{schema}"' not in html_content and f'"@type": "{schema}"' not in html_content:
                        missing_schemas.append(schema)
                
                if missing_schemas:
                    print(f"   ❌ FAILED: Missing schemas: {missing_schemas}")
                    continue
                
                print(f"   ✅ PASSED: Found all expected schemas: {test['expected_schemas']}")
            else:
                print(f"   ✅ PASSED: Status code {response.status_code} as expected")
            
            passed += 1
            
        except Exception as e:
            print(f"   ❌ FAILED: Exception - {str(e)}")
    
    print(f"\n🔄 PREVIOUS FEATURES RESULTS: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all tests"""
    print("🎸 DADROCK TABS SEO FEATURES TESTING")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {HEADERS['User-Agent']}")
    print("=" * 60)
    
    # Run all test suites
    search_passed = test_search_api()
    faq_passed = test_faq_schema()
    previous_passed = test_previous_features()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎸 FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"🔍 Search API Tests: {'✅ PASSED' if search_passed else '❌ FAILED'}")
    print(f"📋 FAQ Schema Tests: {'✅ PASSED' if faq_passed else '❌ FAILED'}")
    print(f"🔄 Previous Features: {'✅ PASSED' if previous_passed else '❌ FAILED'}")
    
    all_passed = search_passed and faq_passed and previous_passed
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    main()