#!/usr/bin/env python3
"""
Backend Testing for DadRock Tabs - 6 New Features
Testing the newly implemented SEO and UX features as specified in the review request.
"""

import requests
import json
import sys
from urllib.parse import quote

# Base URL for testing
BASE_URL = "http://localhost:3000"

# User-Agent header required for page requests (not API routes)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
}

def test_howto_schema_on_song_pages():
    """Test 1: HowTo Schema on Song Pages"""
    print("\n=== TEST 1: HowTo Schema on Song Pages ===")
    
    try:
        # Test the specific song page mentioned in the review
        url = f"{BASE_URL}/songs/metallica-am-i-evil"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        print(f"GET {url} → {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for HowTo schema
            if '"@type":"HowTo"' in html_content:
                print("✅ HowTo JSON-LD schema found")
                
                # Check for HowToStep entries (should have 5 steps)
                step_count = html_content.count('"@type":"HowToStep"')
                print(f"✅ Found {step_count} HowToStep entries")
                
                # Check for HowToSupply and HowToTool
                if '"@type":"HowToSupply"' in html_content:
                    print("✅ HowToSupply found")
                else:
                    print("❌ HowToSupply not found")
                    
                if '"@type":"HowToTool"' in html_content:
                    print("✅ HowToTool found")
                else:
                    print("❌ HowToTool not found")
                    
                return step_count >= 5 and '"@type":"HowToSupply"' in html_content and '"@type":"HowToTool"' in html_content
            else:
                print("❌ HowTo JSON-LD schema not found")
                return False
        else:
            print(f"❌ Failed to load song page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing HowTo schema: {e}")
        return False

def test_dynamic_og_image_api():
    """Test 2: Dynamic OG Image API (/api/og)"""
    print("\n=== TEST 2: Dynamic OG Image API (/api/og) ===")
    
    test_cases = [
        {"title": "Test", "type": "song"},
        {"title": "Metallica", "artist": "", "type": "artist"},
        {"title": "Thrash Metal", "type": "genre"}
    ]
    
    all_passed = True
    
    for i, params in enumerate(test_cases, 1):
        try:
            # Build query string
            query_params = "&".join([f"{k}={quote(str(v))}" for k, v in params.items() if v is not None])
            url = f"{BASE_URL}/api/og?{query_params}"
            
            # API routes don't need User-Agent header
            response = requests.get(url, timeout=10)
            
            print(f"Test {i}: GET {url} → {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image/png' in content_type:
                    print(f"✅ Test {i}: Correct content-type: {content_type}")
                else:
                    print(f"❌ Test {i}: Wrong content-type: {content_type}")
                    all_passed = False
            else:
                print(f"❌ Test {i}: Failed with status {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Test {i}: Error - {e}")
            all_passed = False
    
    return all_passed

def test_learn_guides_content_hub():
    """Test 3: Learn/Guides Content Hub (/learn)"""
    print("\n=== TEST 3: Learn/Guides Content Hub (/learn) ===")
    
    test_cases = [
        "/learn",
        "/learn/easiest-guitar-riffs-beginners",
        "/learn/palm-muting-technique-guide", 
        "/learn/how-to-read-guitar-tabs",
        "/learn/nonexistent-guide"
    ]
    
    all_passed = True
    
    for url_path in test_cases:
        try:
            url = f"{BASE_URL}{url_path}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            print(f"GET {url} → {response.status_code}")
            
            if url_path == "/learn/nonexistent-guide":
                # Should return 404
                if response.status_code == 404:
                    print("✅ Nonexistent guide correctly returns 404")
                else:
                    print(f"❌ Nonexistent guide should return 404, got {response.status_code}")
                    all_passed = False
            else:
                # Should return 200
                if response.status_code == 200:
                    html_content = response.text
                    
                    if url_path == "/learn":
                        # Check for CollectionPage schema
                        if '"@type":"CollectionPage"' in html_content:
                            print("✅ CollectionPage JSON-LD schema found")
                        else:
                            print("❌ CollectionPage JSON-LD schema not found")
                            all_passed = False
                    else:
                        # Check for Article schema on guide pages
                        if '"@type":"Article"' in html_content:
                            print("✅ Article JSON-LD schema found")
                        else:
                            print("❌ Article JSON-LD schema not found")
                            all_passed = False
                else:
                    print(f"❌ Failed to load page: {response.status_code}")
                    all_passed = False
                    
        except Exception as e:
            print(f"❌ Error testing {url_path}: {e}")
            all_passed = False
    
    return all_passed

def test_difficulty_browse_pages():
    """Test 4: Difficulty Browse Pages (/difficulty/[level])"""
    print("\n=== TEST 4: Difficulty Browse Pages (/difficulty/[level]) ===")
    
    test_cases = [
        "/difficulty/beginner",
        "/difficulty/intermediate", 
        "/difficulty/advanced",
        "/difficulty/nonexistent"
    ]
    
    all_passed = True
    
    for url_path in test_cases:
        try:
            url = f"{BASE_URL}{url_path}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            print(f"GET {url} → {response.status_code}")
            
            if url_path == "/difficulty/nonexistent":
                # Should return 404
                if response.status_code == 404:
                    print("✅ Nonexistent difficulty correctly returns 404")
                else:
                    print(f"❌ Nonexistent difficulty should return 404, got {response.status_code}")
                    all_passed = False
            else:
                # Should return 200
                if response.status_code == 200:
                    html_content = response.text
                    
                    # Check for CollectionPage+ItemList schema
                    if '"@type":"CollectionPage"' in html_content and '"@type":"ItemList"' in html_content:
                        print("✅ CollectionPage+ItemList JSON-LD schema found")
                        
                        # Check for artist links
                        artist_links = html_content.count('/artist/')
                        if artist_links > 0:
                            print(f"✅ Found {artist_links} artist links")
                        else:
                            print("❌ No artist links found")
                            all_passed = False
                    else:
                        print("❌ CollectionPage+ItemList JSON-LD schema not found")
                        all_passed = False
                else:
                    print(f"❌ Failed to load page: {response.status_code}")
                    all_passed = False
                    
        except Exception as e:
            print(f"❌ Error testing {url_path}: {e}")
            all_passed = False
    
    return all_passed

def test_song_of_the_day_api():
    """Test 5: Song of the Day API (/api/song-of-the-day)"""
    print("\n=== TEST 5: Song of the Day API (/api/song-of-the-day) ===")
    
    try:
        url = f"{BASE_URL}/api/song-of-the-day"
        # API routes don't need User-Agent header
        response = requests.get(url, timeout=10)
        
        print(f"GET {url} → {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Check response structure
                if 'song' in data and 'date' in data:
                    print("✅ Response has correct structure (song, date)")
                    
                    song = data['song']
                    if song and 'slug' in song and 'title' in song and 'artist' in song:
                        print("✅ Song object has required fields (slug, title, artist)")
                        print(f"   Song: {song['title']} by {song['artist']}")
                        return True
                    else:
                        print("❌ Song object missing required fields")
                        return False
                else:
                    print("❌ Response missing required fields")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
                return False
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Song of the Day API: {e}")
        return False

def test_performance_preconnect():
    """Test 6: Performance & Integration (Preconnect links)"""
    print("\n=== TEST 6: Performance & Integration ===")
    
    try:
        # Test homepage for preconnect links
        url = f"{BASE_URL}/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        print(f"GET {url} → {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check for preconnect links to YouTube domains
            youtube_preconnects = [
                'rel="preconnect" href="https://www.youtube.com"',
                'rel="preconnect" href="https://i.ytimg.com"',
                'rel="preconnect" href="https://img.youtube.com"'
            ]
            
            found_preconnects = []
            for preconnect in youtube_preconnects:
                if preconnect in html_content:
                    found_preconnects.append(preconnect)
            
            if len(found_preconnects) >= 2:  # At least 2 YouTube preconnects
                print(f"✅ Found {len(found_preconnects)} YouTube preconnect links")
                
                # Test sitemap for /learn and /difficulty URLs
                sitemap_url = f"{BASE_URL}/sitemap.xml"
                sitemap_response = requests.get(sitemap_url, headers=HEADERS, timeout=10)
                
                print(f"GET {sitemap_url} → {sitemap_response.status_code}")
                
                if sitemap_response.status_code == 200:
                    sitemap_content = sitemap_response.text
                    
                    has_learn = '/learn' in sitemap_content
                    has_difficulty = '/difficulty' in sitemap_content
                    
                    if has_learn and has_difficulty:
                        print("✅ Sitemap includes /learn and /difficulty URLs")
                        return True
                    else:
                        print(f"❌ Sitemap missing URLs - learn: {has_learn}, difficulty: {has_difficulty}")
                        return False
                else:
                    print(f"❌ Failed to load sitemap: {sitemap_response.status_code}")
                    return False
            else:
                print(f"❌ Only found {len(found_preconnects)} YouTube preconnect links")
                return False
        else:
            print(f"❌ Failed to load homepage: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing performance features: {e}")
        return False

def main():
    """Run all tests and report results"""
    print("🎸 DadRock Tabs - Testing 6 New Features")
    print("=" * 50)
    
    tests = [
        ("HowTo Schema on Song Pages", test_howto_schema_on_song_pages),
        ("Dynamic OG Image API", test_dynamic_og_image_api),
        ("Learn/Guides Content Hub", test_learn_guides_content_hub),
        ("Difficulty Browse Pages", test_difficulty_browse_pages),
        ("Song of the Day API", test_song_of_the_day_api),
        ("Performance & Integration", test_performance_preconnect)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎸 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! All 6 new features are working correctly.")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())