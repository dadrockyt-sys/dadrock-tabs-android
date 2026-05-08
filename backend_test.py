#!/usr/bin/env python3
"""
DadRock Tabs Backend Testing Script
Tests new features: Curated Playlists, Newsletter API, PWA Support, and regression tests
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Base URL from environment
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"

# User-Agent header required for page requests (not API)
USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1)"

def test_curated_playlists():
    """Test curated playlist pages with ItemList JSON-LD schema"""
    print("\n=== TESTING CURATED PLAYLISTS ===")
    
    playlist_slugs = [
        'beginner-riffs-starter-pack',
        'essential-80s-solos', 
        'headbanger-classics',
        'power-ballads',
        'riff-workout',
        'blues-rock-essentials',
        'nonexistent'  # Should return 404
    ]
    
    results = []
    
    for slug in playlist_slugs:
        try:
            url = f"{BASE_URL}/playlist/{slug}"
            response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
            
            if slug == 'nonexistent':
                if response.status_code == 404:
                    print(f"✅ GET /playlist/{slug} → 404 (correct)")
                    results.append(True)
                else:
                    print(f"❌ GET /playlist/{slug} → {response.status_code} (expected 404)")
                    results.append(False)
                continue
            
            if response.status_code == 200:
                # Check for ItemList JSON-LD schema
                html_content = response.text
                if '"@type":"ItemList"' in html_content or '"@type": "ItemList"' in html_content:
                    if '"@type":"MusicRecording"' in html_content or '"@type": "MusicRecording"' in html_content:
                        # Count MusicRecording entries
                        music_recording_count = html_content.count('"@type":"MusicRecording"') + html_content.count('"@type": "MusicRecording"')
                        print(f"✅ GET /playlist/{slug} → 200 with ItemList JSON-LD schema ({music_recording_count} MusicRecording entries)")
                        
                        # Check for /songs/ links
                        songs_links = html_content.count('/songs/')
                        if songs_links > 0:
                            print(f"   Contains {songs_links} /songs/ links (matched from DB)")
                        results.append(True)
                    else:
                        print(f"❌ GET /playlist/{slug} → 200 but missing MusicRecording schema")
                        results.append(False)
                else:
                    print(f"❌ GET /playlist/{slug} → 200 but missing ItemList schema")
                    results.append(False)
            else:
                print(f"❌ GET /playlist/{slug} → {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ GET /playlist/{slug} → Error: {e}")
            results.append(False)
    
    return all(results)

def test_newsletter_api():
    """Test Newsletter API with various email scenarios"""
    print("\n=== TESTING NEWSLETTER API ===")
    
    results = []
    
    # Test 1: Valid new email
    try:
        url = f"{BASE_URL}/api/newsletter"
        import time
        test_email = f"newtest{int(time.time())}@example.com"  # Use timestamp to ensure uniqueness
        response = requests.post(url, json={"email": test_email}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "Successfully subscribed!" in data.get("message", "") and data.get("already_subscribed") == False:
                print(f"✅ POST /api/newsletter with new email → 200, successfully subscribed")
                results.append(True)
            elif data.get("already_subscribed") == True:
                print(f"✅ POST /api/newsletter with new email → 200, already subscribed (acceptable)")
                results.append(True)
            else:
                print(f"❌ POST /api/newsletter → 200 but unexpected response: {data}")
                results.append(False)
        else:
            print(f"❌ POST /api/newsletter with new email → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/newsletter with new email → Error: {e}")
        results.append(False)
    
    # Test 2: Same email again (should show already subscribed)
    try:
        response = requests.post(url, json={"email": test_email}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("already_subscribed") == True:
                print(f"✅ POST /api/newsletter with existing email → 200, already_subscribed=true")
                results.append(True)
            else:
                print(f"❌ POST /api/newsletter → 200 but already_subscribed not true: {data}")
                results.append(False)
        else:
            print(f"❌ POST /api/newsletter with existing email → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/newsletter with existing email → Error: {e}")
        results.append(False)
    
    # Test 3: Invalid email
    try:
        response = requests.post(url, json={"email": "invalid"}, timeout=30)
        
        if response.status_code == 400:
            print(f"✅ POST /api/newsletter with invalid email → 400 (correct)")
            results.append(True)
        else:
            print(f"❌ POST /api/newsletter with invalid email → {response.status_code} (expected 400)")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/newsletter with invalid email → Error: {e}")
        results.append(False)
    
    # Test 4: Empty body
    try:
        response = requests.post(url, json={}, timeout=30)
        
        if response.status_code == 400:
            print(f"✅ POST /api/newsletter with empty body → 400 (correct)")
            results.append(True)
        else:
            print(f"❌ POST /api/newsletter with empty body → {response.status_code} (expected 400)")
            results.append(False)
    except Exception as e:
        print(f"❌ POST /api/newsletter with empty body → Error: {e}")
        results.append(False)
    
    return all(results)

def test_pwa_support():
    """Test PWA manifest.json and service worker"""
    print("\n=== TESTING PWA SUPPORT ===")
    
    results = []
    
    # Test 1: manifest.json
    try:
        url = f"{BASE_URL}/manifest.json"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            try:
                manifest = response.json()
                if (manifest.get("name") == "DadRock Tabs" and 
                    "theme_color" in manifest and 
                    "icons" in manifest):
                    print(f"✅ GET /manifest.json → 200, valid JSON with name='DadRock Tabs', theme_color, icons")
                    results.append(True)
                else:
                    print(f"❌ GET /manifest.json → 200 but missing required fields: {manifest}")
                    results.append(False)
            except json.JSONDecodeError:
                print(f"❌ GET /manifest.json → 200 but invalid JSON")
                results.append(False)
        else:
            print(f"❌ GET /manifest.json → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /manifest.json → Error: {e}")
        results.append(False)
    
    # Test 2: service worker
    try:
        url = f"{BASE_URL}/sw.js"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if "serviceWorker" in content or "addEventListener" in content:
                print(f"✅ GET /sw.js → 200, contains 'serviceWorker' or 'addEventListener'")
                results.append(True)
            else:
                print(f"❌ GET /sw.js → 200 but doesn't contain service worker code")
                results.append(False)
        else:
            print(f"❌ GET /sw.js → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /sw.js → Error: {e}")
        results.append(False)
    
    # Test 3: Homepage should link to manifest.json
    try:
        url = f"{BASE_URL}/"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if 'rel="manifest"' in content and 'manifest.json' in content:
                print(f"✅ GET / → 200, HTML contains link to manifest.json")
                results.append(True)
            else:
                print(f"❌ GET / → 200 but missing manifest.json link in HTML")
                results.append(False)
        else:
            print(f"❌ GET / → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET / → Error: {e}")
        results.append(False)
    
    return all(results)

def test_existing_features_regression():
    """Test existing features to ensure they still work"""
    print("\n=== TESTING EXISTING FEATURES (REGRESSION) ===")
    
    results = []
    
    # Test 1: Song page with HowTo schema
    try:
        url = f"{BASE_URL}/songs/metallica-am-i-evil"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if ('"@type":"HowTo"' in content or '"@type": "HowTo"' in content) and ('ProgressTracker' in content or 'Track Your Progress' in content):
                print(f"✅ GET /songs/metallica-am-i-evil → 200 (contains HowTo schema and ProgressTracker)")
                results.append(True)
            else:
                print(f"❌ GET /songs/metallica-am-i-evil → 200 but missing HowTo schema or ProgressTracker")
                results.append(False)
        else:
            print(f"❌ GET /songs/metallica-am-i-evil → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /songs/metallica-am-i-evil → Error: {e}")
        results.append(False)
    
    # Test 2: Song of the Day API
    try:
        url = f"{BASE_URL}/api/song-of-the-day"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "song" in data and "slug" in data["song"] and "title" in data["song"]:
                    print(f"✅ GET /api/song-of-the-day → 200, returns JSON with song data")
                    results.append(True)
                else:
                    print(f"❌ GET /api/song-of-the-day → 200 but missing song data: {data}")
                    results.append(False)
            except json.JSONDecodeError:
                print(f"❌ GET /api/song-of-the-day → 200 but invalid JSON")
                results.append(False)
        else:
            print(f"❌ GET /api/song-of-the-day → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /api/song-of-the-day → Error: {e}")
        results.append(False)
    
    # Test 3: Sitemap contains learn, difficulty, playlist URLs
    try:
        url = f"{BASE_URL}/sitemap.xml"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            has_learn = '/learn' in content
            has_difficulty = '/difficulty' in content
            has_playlist = '/playlist' in content
            
            if has_learn and has_difficulty and has_playlist:
                print(f"✅ GET /sitemap.xml → 200, contains learn, difficulty, playlist URLs")
                results.append(True)
            else:
                missing = []
                if not has_learn: missing.append('learn')
                if not has_difficulty: missing.append('difficulty')
                if not has_playlist: missing.append('playlist')
                print(f"❌ GET /sitemap.xml → 200 but missing URLs: {', '.join(missing)}")
                results.append(False)
        else:
            print(f"❌ GET /sitemap.xml → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ GET /sitemap.xml → Error: {e}")
        results.append(False)
    
    return all(results)

def main():
    """Run all tests and provide summary"""
    print(f"🎸 DadRock Tabs Backend Testing")
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {USER_AGENT}")
    
    # Run all test suites
    playlist_results = test_curated_playlists()
    newsletter_results = test_newsletter_api()
    pwa_results = test_pwa_support()
    regression_results = test_existing_features_regression()
    
    # Summary
    print(f"\n=== TEST SUMMARY ===")
    print(f"Curated Playlists: {'✅ PASS' if playlist_results else '❌ FAIL'}")
    print(f"Newsletter API: {'✅ PASS' if newsletter_results else '❌ FAIL'}")
    print(f"PWA Support: {'✅ PASS' if pwa_results else '❌ FAIL'}")
    print(f"Existing Features: {'✅ PASS' if regression_results else '❌ FAIL'}")
    
    all_passed = all([playlist_results, newsletter_results, pwa_results, regression_results])
    print(f"\nOVERALL: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())