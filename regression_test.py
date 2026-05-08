#!/usr/bin/env python3
"""
DadRock Tabs Quick Regression Test
Tests core APIs after FlameTransition.js update
"""

import requests
import json
import sys

# Base URL - localhost as specified in review request
BASE_URL = "http://localhost:3000"

# User-Agent header required for page requests (not API)
USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1)"

def test_health_api():
    """Test 1: GET /api/health → should return 200"""
    print("\n=== TEST 1: Health Check API ===")
    try:
        url = f"{BASE_URL}/api/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ GET /api/health → 200")
            return True
        else:
            print(f"❌ GET /api/health → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /api/health → Error: {e}")
        return False

def test_settings_api():
    """Test 2: GET /api/settings → should return 200 with JSON"""
    print("\n=== TEST 2: Settings API ===")
    try:
        url = f"{BASE_URL}/api/settings"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ GET /api/settings → 200 with JSON: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"❌ GET /api/settings → 200 but invalid JSON")
                return False
        else:
            print(f"❌ GET /api/settings → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /api/settings → Error: {e}")
        return False

def test_random_song_api():
    """Test 3: GET /api/random-song → should return 200 with {slug}"""
    print("\n=== TEST 3: Random Song API ===")
    try:
        url = f"{BASE_URL}/api/random-song"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "slug" in data:
                    print(f"✅ GET /api/random-song → 200 with slug='{data['slug']}'")
                    return True
                else:
                    print(f"❌ GET /api/random-song → 200 but missing slug field: {data}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ GET /api/random-song → 200 but invalid JSON")
                return False
        else:
            print(f"❌ GET /api/random-song → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /api/random-song → Error: {e}")
        return False

def test_song_of_the_day_api():
    """Test 4: GET /api/song-of-the-day → should return 200 with {song: {slug, title, artist}}"""
    print("\n=== TEST 4: Song of the Day API ===")
    try:
        url = f"{BASE_URL}/api/song-of-the-day"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "song" in data and "slug" in data["song"] and "title" in data["song"] and "artist" in data["song"]:
                    print(f"✅ GET /api/song-of-the-day → 200 with song={{slug='{data['song']['slug']}', title='{data['song']['title']}', artist='{data['song']['artist']}'}}")
                    return True
                else:
                    print(f"❌ GET /api/song-of-the-day → 200 but missing required fields: {data}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ GET /api/song-of-the-day → 200 but invalid JSON")
                return False
        else:
            print(f"❌ GET /api/song-of-the-day → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /api/song-of-the-day → Error: {e}")
        return False

def test_search_api():
    """Test 5: GET /api/search?q=metallica → should return 200 with {artists: [...], songs: [...]}"""
    print("\n=== TEST 5: Search API ===")
    try:
        url = f"{BASE_URL}/api/search?q=metallica"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "artists" in data and "songs" in data:
                    print(f"✅ GET /api/search?q=metallica → 200 with {len(data['artists'])} artists, {len(data['songs'])} songs")
                    return True
                else:
                    print(f"❌ GET /api/search?q=metallica → 200 but missing required fields: {data}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ GET /api/search?q=metallica → 200 but invalid JSON")
                return False
        else:
            print(f"❌ GET /api/search?q=metallica → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /api/search?q=metallica → Error: {e}")
        return False

def test_newsletter_api():
    """Test 6: POST /api/newsletter with {"email": "regression-test@example.com"} → should return 200"""
    print("\n=== TEST 6: Newsletter API ===")
    try:
        url = f"{BASE_URL}/api/newsletter"
        import time
        test_email = f"regression-test-{int(time.time())}@example.com"
        response = requests.post(url, json={"email": test_email}, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ POST /api/newsletter → 200 with response: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"❌ POST /api/newsletter → 200 but invalid JSON")
                return False
        else:
            print(f"❌ POST /api/newsletter → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ POST /api/newsletter → Error: {e}")
        return False

def test_og_image_api():
    """Test 7: GET /api/og?title=Test&type=song → should return 200 with content-type: image/png"""
    print("\n=== TEST 7: OG Image API ===")
    try:
        url = f"{BASE_URL}/api/og?title=Test&type=song"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image/png' in content_type:
                print(f"✅ GET /api/og?title=Test&type=song → 200 with content-type: {content_type}")
                return True
            else:
                print(f"❌ GET /api/og?title=Test&type=song → 200 but wrong content-type: {content_type} (expected image/png)")
                return False
        else:
            print(f"❌ GET /api/og?title=Test&type=song → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /api/og?title=Test&type=song → Error: {e}")
        return False

def test_homepage():
    """Test 8: GET / (with UA header) → should return 200 with HTML containing "DadRock" """
    print("\n=== TEST 8: Homepage ===")
    try:
        url = f"{BASE_URL}/"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if "DadRock" in content or "dadrock" in content.lower():
                print(f"✅ GET / → 200 with HTML containing 'DadRock'")
                return True
            else:
                print(f"❌ GET / → 200 but missing 'DadRock' in HTML")
                return False
        else:
            print(f"❌ GET / → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET / → Error: {e}")
        return False

def test_artist_page():
    """Test 9: GET /artist/metallica (with UA header) → should return 200"""
    print("\n=== TEST 9: Artist Page ===")
    try:
        url = f"{BASE_URL}/artist/metallica"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ GET /artist/metallica → 200")
            return True
        else:
            print(f"❌ GET /artist/metallica → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /artist/metallica → Error: {e}")
        return False

def test_song_page():
    """Test 10: GET /songs/metallica-am-i-evil (with UA header) → should return 200"""
    print("\n=== TEST 10: Song Page ===")
    try:
        url = f"{BASE_URL}/songs/metallica-am-i-evil"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ GET /songs/metallica-am-i-evil → 200")
            return True
        else:
            print(f"❌ GET /songs/metallica-am-i-evil → {response.status_code} (expected 200)")
            return False
    except Exception as e:
        print(f"❌ GET /songs/metallica-am-i-evil → Error: {e}")
        return False

def main():
    """Run all regression tests and provide summary"""
    print(f"🎸 DadRock Tabs Quick Regression Test")
    print(f"Base URL: {BASE_URL}")
    print(f"Testing core APIs after FlameTransition.js update")
    
    # Run all tests
    results = []
    results.append(("Health API", test_health_api()))
    results.append(("Settings API", test_settings_api()))
    results.append(("Random Song API", test_random_song_api()))
    results.append(("Song of the Day API", test_song_of_the_day_api()))
    results.append(("Search API", test_search_api()))
    results.append(("Newsletter API", test_newsletter_api()))
    results.append(("OG Image API", test_og_image_api()))
    results.append(("Homepage", test_homepage()))
    results.append(("Artist Page", test_artist_page()))
    results.append(("Song Page", test_song_page()))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"=== REGRESSION TEST SUMMARY ===")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Total: {passed}/{len(results)} tests passed")
    
    if failed == 0:
        print(f"✅ ALL REGRESSION TESTS PASSED - No backend impact from FlameTransition.js update")
        return 0
    else:
        print(f"❌ {failed} REGRESSION TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
