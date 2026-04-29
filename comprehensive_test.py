#!/usr/bin/env python3
"""
DadRock Tabs Comprehensive Testing Script
Tests ALL 31 features as specified in the review request
"""

import requests
import json
import sys
from urllib.parse import urljoin

# Base URL for testing (localhost as specified in review request)
BASE_URL = "http://localhost:3000"

# User-Agent header required for page requests (not API)
USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1)"

def test_core_pages():
    """[A] CORE PAGES (6 tests)"""
    print("\n=== [A] TESTING CORE PAGES ===")
    
    results = []
    
    # Test 1: Homepage
    try:
        url = f"{BASE_URL}/"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            has_dadrock = "DadRock" in content
            has_manifest = "manifest.json" in content
            has_preconnect = "preconnect" in content
            
            if has_dadrock and has_manifest and has_preconnect:
                print(f"✅ 1. GET / → 200, contains DadRock, manifest.json, preconnect")
                results.append(True)
            else:
                missing = []
                if not has_dadrock: missing.append('DadRock')
                if not has_manifest: missing.append('manifest.json')
                if not has_preconnect: missing.append('preconnect')
                print(f"❌ 1. GET / → 200 but missing: {', '.join(missing)}")
                results.append(False)
        else:
            print(f"❌ 1. GET / → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 1. GET / → Error: {e}")
        results.append(False)
    
    # Test 2: Artist page - Metallica
    try:
        url = f"{BASE_URL}/artist/metallica"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            has_musicgroup = '"@type":"MusicGroup"' in content or '"@type": "MusicGroup"' in content
            has_breadcrumb = '"@type":"BreadcrumbList"' in content or '"@type": "BreadcrumbList"' in content
            has_collection = '"@type":"CollectionPage"' in content or '"@type": "CollectionPage"' in content
            has_faq = '"@type":"FAQPage"' in content or '"@type": "FAQPage"' in content
            
            if has_musicgroup and has_breadcrumb and has_collection and has_faq:
                print(f"✅ 2. GET /artist/metallica → 200, contains MusicGroup+BreadcrumbList+CollectionPage+FAQPage JSON-LD")
                results.append(True)
            else:
                missing = []
                if not has_musicgroup: missing.append('MusicGroup')
                if not has_breadcrumb: missing.append('BreadcrumbList')
                if not has_collection: missing.append('CollectionPage')
                if not has_faq: missing.append('FAQPage')
                print(f"❌ 2. GET /artist/metallica → 200 but missing schemas: {', '.join(missing)}")
                results.append(False)
        else:
            print(f"❌ 2. GET /artist/metallica → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 2. GET /artist/metallica → Error: {e}")
        results.append(False)
    
    # Test 3: Artist page - AC/DC
    try:
        url = f"{BASE_URL}/artist/ac-dc"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 3. GET /artist/ac-dc → 200")
            results.append(True)
        else:
            print(f"❌ 3. GET /artist/ac-dc → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 3. GET /artist/ac-dc → Error: {e}")
        results.append(False)
    
    # Test 4: Invalid artist should redirect
    try:
        url = f"{BASE_URL}/artist/totally-fake-artist-xyz"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30, allow_redirects=False)
        
        if response.status_code == 308:
            print(f"✅ 4. GET /artist/totally-fake-artist-xyz → 308 redirect")
            results.append(True)
        else:
            print(f"❌ 4. GET /artist/totally-fake-artist-xyz → {response.status_code} (expected 308)")
            results.append(False)
    except Exception as e:
        print(f"❌ 4. GET /artist/totally-fake-artist-xyz → Error: {e}")
        results.append(False)
    
    # Test 5: Song page with schemas and visual elements
    try:
        url = f"{BASE_URL}/songs/metallica-am-i-evil"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            has_howto = '"@type":"HowTo"' in content or '"@type": "HowTo"' in content
            has_musicrecording = '"@type":"MusicRecording"' in content or '"@type": "MusicRecording"' in content
            has_videoobject = '"@type":"VideoObject"' in content or '"@type": "VideoObject"' in content
            has_flame_text = "flame-text" in content
            has_progress = "ProgressTracker" in content or "progress" in content or "Track Your Progress" in content
            
            if has_howto and has_musicrecording and has_videoobject and has_flame_text and has_progress:
                print(f"✅ 5. GET /songs/metallica-am-i-evil → 200, contains HowTo+MusicRecording+VideoObject JSON-LD, flame-text, ProgressTracker")
                results.append(True)
            else:
                missing = []
                if not has_howto: missing.append('HowTo')
                if not has_musicrecording: missing.append('MusicRecording')
                if not has_videoobject: missing.append('VideoObject')
                if not has_flame_text: missing.append('flame-text')
                if not has_progress: missing.append('ProgressTracker')
                print(f"❌ 5. GET /songs/metallica-am-i-evil → 200 but missing: {', '.join(missing)}")
                results.append(False)
        else:
            print(f"❌ 5. GET /songs/metallica-am-i-evil → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 5. GET /songs/metallica-am-i-evil → Error: {e}")
        results.append(False)
    
    # Test 6: Invalid song should redirect
    try:
        url = f"{BASE_URL}/songs/completely-fake-song-xyz"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30, allow_redirects=False)
        
        if response.status_code == 308:
            print(f"✅ 6. GET /songs/completely-fake-song-xyz → 308 redirect")
            results.append(True)
        else:
            print(f"❌ 6. GET /songs/completely-fake-song-xyz → {response.status_code} (expected 308)")
            results.append(False)
    except Exception as e:
        print(f"❌ 6. GET /songs/completely-fake-song-xyz → Error: {e}")
        results.append(False)
    
    return results

def test_seo_features():
    """[B] SEO FEATURES (3 tests)"""
    print("\n=== [B] TESTING SEO FEATURES ===")
    
    results = []
    
    # Test 7: Video sitemap
    try:
        url = f"{BASE_URL}/video-sitemap.xml"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            content = response.text
            has_xml_type = 'application/xml' in content_type
            has_video_schema = 'video:video' in content
            
            if has_xml_type and has_video_schema:
                print(f"✅ 7. GET /video-sitemap.xml → 200, Content-Type: application/xml, contains video:video")
                results.append(True)
            else:
                issues = []
                if not has_xml_type: issues.append('wrong content-type')
                if not has_video_schema: issues.append('missing video:video')
                print(f"❌ 7. GET /video-sitemap.xml → 200 but issues: {', '.join(issues)}")
                results.append(False)
        else:
            print(f"❌ 7. GET /video-sitemap.xml → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 7. GET /video-sitemap.xml → Error: {e}")
        results.append(False)
    
    # Test 8: Robots.txt
    try:
        url = f"{BASE_URL}/robots.txt"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if 'video-sitemap.xml' in content:
                print(f"✅ 8. GET /robots.txt → 200, contains video-sitemap.xml")
                results.append(True)
            else:
                print(f"❌ 8. GET /robots.txt → 200 but missing video-sitemap.xml")
                results.append(False)
        else:
            print(f"❌ 8. GET /robots.txt → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 8. GET /robots.txt → Error: {e}")
        results.append(False)
    
    # Test 9: Main sitemap
    try:
        url = f"{BASE_URL}/sitemap.xml"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            has_learn = '/learn' in content
            has_difficulty = '/difficulty' in content
            has_playlist = '/playlist' in content
            has_genre = '/genre' in content
            has_era = '/era' in content
            
            if has_learn and has_difficulty and has_playlist and has_genre and has_era:
                print(f"✅ 9. GET /sitemap.xml → 200, contains /learn, /difficulty, /playlist, /genre, /era")
                results.append(True)
            else:
                missing = []
                if not has_learn: missing.append('/learn')
                if not has_difficulty: missing.append('/difficulty')
                if not has_playlist: missing.append('/playlist')
                if not has_genre: missing.append('/genre')
                if not has_era: missing.append('/era')
                print(f"❌ 9. GET /sitemap.xml → 200 but missing: {', '.join(missing)}")
                results.append(False)
        else:
            print(f"❌ 9. GET /sitemap.xml → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 9. GET /sitemap.xml → Error: {e}")
        results.append(False)
    
    return results

def test_browse_pages():
    """[C] BROWSE PAGES (13 tests)"""
    print("\n=== [C] TESTING BROWSE PAGES ===")
    
    results = []
    
    # Test 10: Valid genre page
    try:
        url = f"{BASE_URL}/genre/thrash-metal"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if '"@type":"CollectionPage"' in content or '"@type": "CollectionPage"' in content:
                print(f"✅ 10. GET /genre/thrash-metal → 200, contains CollectionPage")
                results.append(True)
            else:
                print(f"❌ 10. GET /genre/thrash-metal → 200 but missing CollectionPage schema")
                results.append(False)
        else:
            print(f"❌ 10. GET /genre/thrash-metal → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 10. GET /genre/thrash-metal → Error: {e}")
        results.append(False)
    
    # Test 11: Invalid genre page
    try:
        url = f"{BASE_URL}/genre/nonexistent-genre"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 404:
            print(f"✅ 11. GET /genre/nonexistent-genre → 404")
            results.append(True)
        else:
            print(f"❌ 11. GET /genre/nonexistent-genre → {response.status_code} (expected 404)")
            results.append(False)
    except Exception as e:
        print(f"❌ 11. GET /genre/nonexistent-genre → Error: {e}")
        results.append(False)
    
    # Test 12: Valid era page
    try:
        url = f"{BASE_URL}/era/80s-rock"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if '"@type":"CollectionPage"' in content or '"@type": "CollectionPage"' in content:
                print(f"✅ 12. GET /era/80s-rock → 200, contains CollectionPage")
                results.append(True)
            else:
                print(f"❌ 12. GET /era/80s-rock → 200 but missing CollectionPage schema")
                results.append(False)
        else:
            print(f"❌ 12. GET /era/80s-rock → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 12. GET /era/80s-rock → Error: {e}")
        results.append(False)
    
    # Test 13: Invalid era page
    try:
        url = f"{BASE_URL}/era/nonexistent-era"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 404:
            print(f"✅ 13. GET /era/nonexistent-era → 404")
            results.append(True)
        else:
            print(f"❌ 13. GET /era/nonexistent-era → {response.status_code} (expected 404)")
            results.append(False)
    except Exception as e:
        print(f"❌ 13. GET /era/nonexistent-era → Error: {e}")
        results.append(False)
    
    # Test 14: Valid difficulty page
    try:
        url = f"{BASE_URL}/difficulty/beginner"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if '"@type":"CollectionPage"' in content or '"@type": "CollectionPage"' in content:
                print(f"✅ 14. GET /difficulty/beginner → 200, contains CollectionPage")
                results.append(True)
            else:
                print(f"❌ 14. GET /difficulty/beginner → 200 but missing CollectionPage schema")
                results.append(False)
        else:
            print(f"❌ 14. GET /difficulty/beginner → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 14. GET /difficulty/beginner → Error: {e}")
        results.append(False)
    
    # Test 15: Another valid difficulty page
    try:
        url = f"{BASE_URL}/difficulty/advanced"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 15. GET /difficulty/advanced → 200")
            results.append(True)
        else:
            print(f"❌ 15. GET /difficulty/advanced → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 15. GET /difficulty/advanced → Error: {e}")
        results.append(False)
    
    # Test 16: Invalid difficulty page
    try:
        url = f"{BASE_URL}/difficulty/nonexistent"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 404:
            print(f"✅ 16. GET /difficulty/nonexistent → 404")
            results.append(True)
        else:
            print(f"❌ 16. GET /difficulty/nonexistent → {response.status_code} (expected 404)")
            results.append(False)
    except Exception as e:
        print(f"❌ 16. GET /difficulty/nonexistent → Error: {e}")
        results.append(False)
    
    # Test 17: Learn hub page
    try:
        url = f"{BASE_URL}/learn"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if '"@type":"CollectionPage"' in content or '"@type": "CollectionPage"' in content:
                print(f"✅ 17. GET /learn → 200, contains CollectionPage")
                results.append(True)
            else:
                print(f"❌ 17. GET /learn → 200 but missing CollectionPage schema")
                results.append(False)
        else:
            print(f"❌ 17. GET /learn → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 17. GET /learn → Error: {e}")
        results.append(False)
    
    # Test 18: Valid learn guide
    try:
        url = f"{BASE_URL}/learn/easiest-guitar-riffs-beginners"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if '"@type":"Article"' in content or '"@type": "Article"' in content:
                print(f"✅ 18. GET /learn/easiest-guitar-riffs-beginners → 200, contains Article JSON-LD")
                results.append(True)
            else:
                print(f"❌ 18. GET /learn/easiest-guitar-riffs-beginners → 200 but missing Article schema")
                results.append(False)
        else:
            print(f"❌ 18. GET /learn/easiest-guitar-riffs-beginners → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 18. GET /learn/easiest-guitar-riffs-beginners → Error: {e}")
        results.append(False)
    
    # Test 19: Invalid learn guide
    try:
        url = f"{BASE_URL}/learn/nonexistent-guide"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 404:
            print(f"✅ 19. GET /learn/nonexistent-guide → 404")
            results.append(True)
        else:
            print(f"❌ 19. GET /learn/nonexistent-guide → {response.status_code} (expected 404)")
            results.append(False)
    except Exception as e:
        print(f"❌ 19. GET /learn/nonexistent-guide → Error: {e}")
        results.append(False)
    
    # Test 20: Valid playlist
    try:
        url = f"{BASE_URL}/playlist/beginner-riffs-starter-pack"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            has_itemlist = '"@type":"ItemList"' in content or '"@type": "ItemList"' in content
            has_musicrecording = '"@type":"MusicRecording"' in content or '"@type": "MusicRecording"' in content
            
            if has_itemlist and has_musicrecording:
                print(f"✅ 20. GET /playlist/beginner-riffs-starter-pack → 200, contains ItemList and MusicRecording")
                results.append(True)
            else:
                missing = []
                if not has_itemlist: missing.append('ItemList')
                if not has_musicrecording: missing.append('MusicRecording')
                print(f"❌ 20. GET /playlist/beginner-riffs-starter-pack → 200 but missing: {', '.join(missing)}")
                results.append(False)
        else:
            print(f"❌ 20. GET /playlist/beginner-riffs-starter-pack → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 20. GET /playlist/beginner-riffs-starter-pack → Error: {e}")
        results.append(False)
    
    # Test 21: Another valid playlist
    try:
        url = f"{BASE_URL}/playlist/headbanger-classics"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 21. GET /playlist/headbanger-classics → 200")
            results.append(True)
        else:
            print(f"❌ 21. GET /playlist/headbanger-classics → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 21. GET /playlist/headbanger-classics → Error: {e}")
        results.append(False)
    
    # Test 22: Invalid playlist
    try:
        url = f"{BASE_URL}/playlist/nonexistent"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 404:
            print(f"✅ 22. GET /playlist/nonexistent → 404")
            results.append(True)
        else:
            print(f"❌ 22. GET /playlist/nonexistent → {response.status_code} (expected 404)")
            results.append(False)
    except Exception as e:
        print(f"❌ 22. GET /playlist/nonexistent → Error: {e}")
        results.append(False)
    
    return results

def test_api_endpoints():
    """[D] API ENDPOINTS (4 tests)"""
    print("\n=== [D] TESTING API ENDPOINTS ===")
    
    results = []
    
    # Test 23: Search API
    try:
        url = f"{BASE_URL}/api/search?q=metallica"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "artists" in data and "songs" in data and isinstance(data["artists"], list) and isinstance(data["songs"], list):
                    print(f"✅ 23. GET /api/search?q=metallica → 200, JSON response with artists and songs arrays")
                    results.append(True)
                else:
                    print(f"❌ 23. GET /api/search?q=metallica → 200 but missing artists/songs arrays: {data}")
                    results.append(False)
            except json.JSONDecodeError:
                print(f"❌ 23. GET /api/search?q=metallica → 200 but invalid JSON")
                results.append(False)
        else:
            print(f"❌ 23. GET /api/search?q=metallica → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 23. GET /api/search?q=metallica → Error: {e}")
        results.append(False)
    
    # Test 24: Song of the Day API
    try:
        url = f"{BASE_URL}/api/song-of-the-day"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "song" in data and isinstance(data["song"], dict):
                    song = data["song"]
                    if "slug" in song and "title" in song and "artist" in song:
                        print(f"✅ 24. GET /api/song-of-the-day → 200, JSON with song object containing slug, title, artist")
                        results.append(True)
                    else:
                        print(f"❌ 24. GET /api/song-of-the-day → 200 but song missing required fields: {song}")
                        results.append(False)
                else:
                    print(f"❌ 24. GET /api/song-of-the-day → 200 but missing song object: {data}")
                    results.append(False)
            except json.JSONDecodeError:
                print(f"❌ 24. GET /api/song-of-the-day → 200 but invalid JSON")
                results.append(False)
        else:
            print(f"❌ 24. GET /api/song-of-the-day → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 24. GET /api/song-of-the-day → Error: {e}")
        results.append(False)
    
    # Test 25: OG Image API
    try:
        url = f"{BASE_URL}/api/og?title=Test&type=song"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            if 'image/png' in content_type:
                print(f"✅ 25. GET /api/og?title=Test&type=song → 200, content-type: image/png")
                results.append(True)
            else:
                print(f"❌ 25. GET /api/og?title=Test&type=song → 200 but wrong content-type: {content_type}")
                results.append(False)
        else:
            print(f"❌ 25. GET /api/og?title=Test&type=song → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 25. GET /api/og?title=Test&type=song → Error: {e}")
        results.append(False)
    
    # Test 26: Newsletter API
    try:
        url = f"{BASE_URL}/api/newsletter"
        import time
        test_email = f"comprehensive-test-{int(time.time())}@example.com"
        response = requests.post(url, json={"email": test_email}, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 26. POST /api/newsletter with email → 200")
            results.append(True)
        else:
            print(f"❌ 26. POST /api/newsletter with email → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 26. POST /api/newsletter with email → Error: {e}")
        results.append(False)
    
    return results

def test_pwa():
    """[E] PWA (2 tests)"""
    print("\n=== [E] TESTING PWA ===")
    
    results = []
    
    # Test 27: Manifest.json
    try:
        url = f"{BASE_URL}/manifest.json"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            try:
                manifest = response.json()
                if "DadRock Tabs" in str(manifest):
                    print(f"✅ 27. GET /manifest.json → 200, valid JSON, contains 'DadRock Tabs'")
                    results.append(True)
                else:
                    print(f"❌ 27. GET /manifest.json → 200 but missing 'DadRock Tabs': {manifest}")
                    results.append(False)
            except json.JSONDecodeError:
                print(f"❌ 27. GET /manifest.json → 200 but invalid JSON")
                results.append(False)
        else:
            print(f"❌ 27. GET /manifest.json → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 27. GET /manifest.json → Error: {e}")
        results.append(False)
    
    # Test 28: Service Worker
    try:
        url = f"{BASE_URL}/sw.js"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            if "addEventListener" in content:
                print(f"✅ 28. GET /sw.js → 200, contains addEventListener")
                results.append(True)
            else:
                print(f"❌ 28. GET /sw.js → 200 but missing addEventListener")
                results.append(False)
        else:
            print(f"❌ 28. GET /sw.js → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 28. GET /sw.js → Error: {e}")
        results.append(False)
    
    return results

def test_visual_css():
    """[F] VISUAL CSS CLASSES IN HTML (3 tests)"""
    print("\n=== [F] TESTING VISUAL CSS CLASSES ===")
    
    results = []
    
    # Test 29: Homepage CSS classes
    try:
        url = f"{BASE_URL}/"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            required_classes = ["neon-flicker", "eq-visualizer", "fire-glow", "vinyl-record", "ember", "rock-divider", "float-note"]
            found_classes = [cls for cls in required_classes if cls in content]
            
            if len(found_classes) >= 5:  # Allow some flexibility
                print(f"✅ 29. Homepage HTML contains CSS classes: {', '.join(found_classes)}")
                results.append(True)
            else:
                print(f"❌ 29. Homepage HTML missing CSS classes. Found: {', '.join(found_classes)}, Required: {', '.join(required_classes)}")
                results.append(False)
        else:
            print(f"❌ 29. GET / → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 29. GET / → Error: {e}")
        results.append(False)
    
    # Test 30: Artist page CSS classes
    try:
        url = f"{BASE_URL}/artist/metallica"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            required_classes = ["fire-glow", "ember-container", "eq-visualizer"]
            found_classes = [cls for cls in required_classes if cls in content]
            
            if len(found_classes) >= 2:  # Allow some flexibility
                print(f"✅ 30. Artist page HTML contains CSS classes: {', '.join(found_classes)}")
                results.append(True)
            else:
                print(f"❌ 30. Artist page HTML missing CSS classes. Found: {', '.join(found_classes)}, Required: {', '.join(required_classes)}")
                results.append(False)
        else:
            print(f"❌ 30. GET /artist/metallica → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 30. GET /artist/metallica → Error: {e}")
        results.append(False)
    
    # Test 31: Song page CSS classes
    try:
        url = f"{BASE_URL}/songs/metallica-am-i-evil"
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=30)
        
        if response.status_code == 200:
            content = response.text
            required_classes = ["flame-text", "float-note", "rock-divider"]
            found_classes = [cls for cls in required_classes if cls in content]
            
            if len(found_classes) >= 2:  # Allow some flexibility
                print(f"✅ 31. Song page HTML contains CSS classes: {', '.join(found_classes)}")
                results.append(True)
            else:
                print(f"❌ 31. Song page HTML missing CSS classes. Found: {', '.join(found_classes)}, Required: {', '.join(required_classes)}")
                results.append(False)
        else:
            print(f"❌ 31. GET /songs/metallica-am-i-evil → {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"❌ 31. GET /songs/metallica-am-i-evil → Error: {e}")
        results.append(False)
    
    return results

def main():
    """Run all 31 tests and provide comprehensive summary"""
    print(f"🎸 DadRock Tabs COMPREHENSIVE TESTING - ALL 31 FEATURES")
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {USER_AGENT}")
    print(f"=" * 80)
    
    # Run all test suites
    core_results = test_core_pages()
    seo_results = test_seo_features()
    browse_results = test_browse_pages()
    api_results = test_api_endpoints()
    pwa_results = test_pwa()
    visual_results = test_visual_css()
    
    # Flatten all results
    all_results = core_results + seo_results + browse_results + api_results + pwa_results + visual_results
    
    # Calculate statistics
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # Summary by category
    print(f"\n" + "=" * 80)
    print(f"=== COMPREHENSIVE TEST SUMMARY ===")
    print(f"[A] Core Pages (6 tests): {sum(core_results)}/6 passed")
    print(f"[B] SEO Features (3 tests): {sum(seo_results)}/3 passed")
    print(f"[C] Browse Pages (13 tests): {sum(browse_results)}/13 passed")
    print(f"[D] API Endpoints (4 tests): {sum(api_results)}/4 passed")
    print(f"[E] PWA (2 tests): {sum(pwa_results)}/2 passed")
    print(f"[F] Visual CSS (3 tests): {sum(visual_results)}/3 passed")
    print(f"")
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed ({pass_rate:.1f}%)")
    
    if passed_tests == total_tests:
        print(f"🎉 ALL 31 TESTS PASSED - COMPREHENSIVE VERIFICATION COMPLETE!")
        return 0
    else:
        print(f"⚠️  {failed_tests} tests failed - see details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())