#!/usr/bin/env python3
"""
Backend Testing for DadRock Tabs SEO Features
Tests the 3 newly implemented SEO features:
1. Video Sitemap XML (/video-sitemap.xml)
2. Genre Browse Pages (/genre/[slug])
3. Era Browse Pages (/era/[slug])
"""

import requests
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
import sys

# Base URL for testing
BASE_URL = "http://localhost:3000"

# Required User-Agent header (middleware blocks requests without proper UA)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
}

# Test data from genreData.js
GENRES = [
    'thrash-metal', 'hair-metal', 'classic-hard-rock', 'heavy-metal',
    'grunge-alternative', 'blues-rock', 'guitar-shred', 'southern-rock'
]

ERAS = ['70s-rock', '80s-rock', '90s-rock']

def test_video_sitemap():
    """Test Video Sitemap XML at /video-sitemap.xml"""
    print("\n🎸 TESTING VIDEO SITEMAP XML")
    print("=" * 50)
    
    try:
        # Test 1: GET /video-sitemap.xml should return 200 with proper Content-Type
        print("1. Testing GET /video-sitemap.xml...")
        response = requests.get(f"{BASE_URL}/video-sitemap.xml", headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
        
        # Check Content-Type
        content_type = response.headers.get('Content-Type', '')
        if 'application/xml' not in content_type:
            print(f"❌ FAILED: Expected Content-Type 'application/xml', got '{content_type}'")
            return False
        
        print(f"✅ Status: {response.status_code}, Content-Type: {content_type}")
        
        # Test 2: Parse XML and check structure
        print("2. Testing XML structure...")
        try:
            root = ET.fromstring(response.text)
            
            # Check namespace
            if root.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
                print(f"❌ FAILED: Expected urlset with sitemap namespace, got {root.tag}")
                return False
            
            # Check for video namespace
            video_ns = 'http://www.google.com/schemas/sitemap-video/1.1'
            if 'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"' not in response.text:
                print("❌ FAILED: Missing video namespace in XML")
                return False
            
            print("✅ XML has proper urlset and video namespaces")
            
            # Test 3: Check for video entries
            print("3. Testing video entries...")
            url_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            video_elements = root.findall(f'.//{{{video_ns}}}video')
            
            if len(url_elements) == 0:
                print("❌ FAILED: No URL entries found in sitemap")
                return False
            
            if len(video_elements) == 0:
                print("❌ FAILED: No video entries found in sitemap")
                return False
            
            print(f"✅ Found {len(url_elements)} URL entries with {len(video_elements)} video entries")
            
            # Test 4: Check required video elements in first video entry
            print("4. Testing required video elements...")
            first_video = video_elements[0]
            required_elements = [
                'thumbnail_loc', 'title', 'description', 
                'content_loc', 'player_loc', 'publication_date'
            ]
            
            missing_elements = []
            for element in required_elements:
                if first_video.find(f'{{{video_ns}}}{element}') is None:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"❌ FAILED: Missing required elements: {missing_elements}")
                return False
            
            print("✅ All required video elements present")
            
            # Test 5: Check XML escaping (no raw &, <, > in text)
            print("5. Testing XML escaping...")
            if '&' in response.text and '&amp;' not in response.text:
                # Check if there are unescaped ampersands
                unescaped_amps = [line for line in response.text.split('\n') 
                                if '&' in line and not any(esc in line for esc in ['&amp;', '&lt;', '&gt;', '&quot;', '&apos;'])]
                if unescaped_amps:
                    print("❌ FAILED: Found unescaped ampersands in XML")
                    return False
            
            print("✅ XML properly escaped")
            
            return True
            
        except ET.ParseError as e:
            print(f"❌ FAILED: XML parsing error: {e}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ FAILED: Request error: {e}")
        return False

def test_genre_pages():
    """Test Genre Browse Pages at /genre/[slug]"""
    print("\n🎸 TESTING GENRE BROWSE PAGES")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test valid genres
    for genre_slug in GENRES[:3]:  # Test first 3 genres
        total_tests += 1
        print(f"\n{total_tests}. Testing /genre/{genre_slug}...")
        
        try:
            response = requests.get(f"{BASE_URL}/genre/{genre_slug}", headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ FAILED: Expected 200, got {response.status_code}")
                continue
            
            # Check for CollectionPage JSON-LD schema
            if '"@type":"CollectionPage"' not in response.text and '"@type": "CollectionPage"' not in response.text:
                print("❌ FAILED: Missing CollectionPage JSON-LD schema")
                continue
            
            # Check for ItemList schema
            if '"@type":"ItemList"' not in response.text and '"@type": "ItemList"' not in response.text:
                print("❌ FAILED: Missing ItemList JSON-LD schema")
                continue
            
            # Check for artist links
            artist_links = response.text.count('/artist/')
            if artist_links < 1:
                print("❌ FAILED: No artist links found")
                continue
            
            print(f"✅ Status: 200, has CollectionPage+ItemList schema, {artist_links} artist links")
            success_count += 1
            
        except requests.RequestException as e:
            print(f"❌ FAILED: Request error: {e}")
    
    # Test nonexistent genre (should return 404)
    total_tests += 1
    print(f"\n{total_tests}. Testing /genre/nonexistent-genre...")
    
    try:
        response = requests.get(f"{BASE_URL}/genre/nonexistent-genre", headers=HEADERS, timeout=30)
        
        if response.status_code == 404:
            print("✅ Status: 404 (correct for nonexistent genre)")
            success_count += 1
        else:
            print(f"❌ FAILED: Expected 404, got {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ FAILED: Request error: {e}")
    
    print(f"\nGenre Pages: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_era_pages():
    """Test Era Browse Pages at /era/[slug]"""
    print("\n🎸 TESTING ERA BROWSE PAGES")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test all valid eras
    for era_slug in ERAS:
        total_tests += 1
        print(f"\n{total_tests}. Testing /era/{era_slug}...")
        
        try:
            response = requests.get(f"{BASE_URL}/era/{era_slug}", headers=HEADERS, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ FAILED: Expected 200, got {response.status_code}")
                continue
            
            # Check for CollectionPage JSON-LD schema
            if '"@type":"CollectionPage"' not in response.text and '"@type": "CollectionPage"' not in response.text:
                print("❌ FAILED: Missing CollectionPage JSON-LD schema")
                continue
            
            # Check for ItemList schema
            if '"@type":"ItemList"' not in response.text and '"@type": "ItemList"' not in response.text:
                print("❌ FAILED: Missing ItemList JSON-LD schema")
                continue
            
            print(f"✅ Status: 200, has CollectionPage+ItemList schema")
            success_count += 1
            
        except requests.RequestException as e:
            print(f"❌ FAILED: Request error: {e}")
    
    # Test nonexistent era (should return 404)
    total_tests += 1
    print(f"\n{total_tests}. Testing /era/nonexistent-era...")
    
    try:
        response = requests.get(f"{BASE_URL}/era/nonexistent-era", headers=HEADERS, timeout=30)
        
        if response.status_code == 404:
            print("✅ Status: 404 (correct for nonexistent era)")
            success_count += 1
        else:
            print(f"❌ FAILED: Expected 404, got {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ FAILED: Request error: {e}")
    
    print(f"\nEra Pages: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def test_integration():
    """Test integration with robots.txt and sitemap.xml"""
    print("\n🎸 TESTING INTEGRATION")
    print("=" * 50)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: robots.txt should contain video-sitemap.xml
    total_tests += 1
    print("1. Testing robots.txt contains video-sitemap.xml...")
    
    try:
        response = requests.get(f"{BASE_URL}/robots.txt", headers=HEADERS, timeout=30)
        
        if response.status_code == 200 and 'video-sitemap.xml' in response.text:
            print("✅ robots.txt contains video-sitemap.xml reference")
            success_count += 1
        else:
            print(f"❌ FAILED: robots.txt missing video-sitemap.xml (status: {response.status_code})")
            
    except requests.RequestException as e:
        print(f"❌ FAILED: Request error: {e}")
    
    # Test 2: sitemap.xml should contain genre and era URLs
    total_tests += 1
    print("2. Testing sitemap.xml contains genre and era URLs...")
    
    try:
        response = requests.get(f"{BASE_URL}/sitemap.xml", headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ FAILED: sitemap.xml returned {response.status_code}")
        else:
            genre_found = any(f'/genre/{genre}' in response.text for genre in GENRES[:2])
            era_found = any(f'/era/{era}' in response.text for era in ERAS[:2])
            
            if genre_found and era_found:
                print("✅ sitemap.xml contains genre and era URLs")
                success_count += 1
            else:
                print(f"❌ FAILED: sitemap.xml missing genre ({genre_found}) or era ({era_found}) URLs")
                
    except requests.RequestException as e:
        print(f"❌ FAILED: Request error: {e}")
    
    print(f"\nIntegration: {success_count}/{total_tests} tests passed")
    return success_count == total_tests

def main():
    """Run all SEO feature tests"""
    print("🎸 DADROCK TABS SEO FEATURES TESTING")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {HEADERS['User-Agent']}")
    
    # Run all test suites
    results = []
    
    try:
        results.append(("Video Sitemap XML", test_video_sitemap()))
        results.append(("Genre Browse Pages", test_genre_pages()))
        results.append(("Era Browse Pages", test_era_pages()))
        results.append(("Integration Tests", test_integration()))
        
        # Summary
        print("\n🎸 FINAL TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} test suites passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL SEO FEATURES WORKING CORRECTLY!")
            return True
        else:
            print(f"\n⚠️  {total-passed} test suite(s) failed - see details above")
            return False
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)