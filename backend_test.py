#!/usr/bin/env python3

import requests
import json
import re
from urllib.parse import urljoin

# Base URL from environment
BASE_URL = "https://admin-sync-hub-1.preview.emergentagent.com"

# Required User-Agent header to bypass middleware blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"
}

def test_structured_data():
    """Test JSON-LD structured data implementation"""
    print("=== STRUCTURED DATA TESTS ===")
    
    # Test 1: Homepage - WebSite + Organization schema
    print("\n1. Testing homepage structured data...")
    try:
        response = requests.get(f"{BASE_URL}/", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Check for WebSite schema
            if '"@type":"WebSite"' in html or '"@type": "WebSite"' in html:
                print("   ✅ WebSite schema found")
            else:
                print("   ❌ WebSite schema NOT found")
            
            # Check for Organization schema
            if '"@type":"Organization"' in html or '"@type": "Organization"' in html:
                print("   ✅ Organization schema found")
            else:
                print("   ❌ Organization schema NOT found")
        else:
            print(f"   ❌ Failed to load homepage: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing homepage: {e}")
    
    # Test 2: Artist page - BreadcrumbList + MusicGroup + CollectionPage
    print("\n2. Testing artist page structured data (metallica)...")
    try:
        response = requests.get(f"{BASE_URL}/artist/metallica", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Check for BreadcrumbList schema
            if '"@type":"BreadcrumbList"' in html or '"@type": "BreadcrumbList"' in html:
                print("   ✅ BreadcrumbList schema found")
            else:
                print("   ❌ BreadcrumbList schema NOT found")
            
            # Check for MusicGroup schema
            if '"@type":"MusicGroup"' in html or '"@type": "MusicGroup"' in html:
                print("   ✅ MusicGroup schema found")
            else:
                print("   ❌ MusicGroup schema NOT found")
            
            # Check for CollectionPage schema
            if '"@type":"CollectionPage"' in html or '"@type": "CollectionPage"' in html:
                print("   ✅ CollectionPage schema found")
            else:
                print("   ❌ CollectionPage schema NOT found")
        else:
            print(f"   ❌ Failed to load artist page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing artist page: {e}")
    
    # Test 3: Song page - BreadcrumbList + MusicRecording + VideoObject
    print("\n3. Testing song page structured data (metallica-am-i-evil)...")
    try:
        response = requests.get(f"{BASE_URL}/songs/metallica-am-i-evil", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Check for BreadcrumbList schema
            if '"@type":"BreadcrumbList"' in html or '"@type": "BreadcrumbList"' in html:
                print("   ✅ BreadcrumbList schema found")
            else:
                print("   ❌ BreadcrumbList schema NOT found")
            
            # Check for MusicRecording schema
            if '"@type":"MusicRecording"' in html or '"@type": "MusicRecording"' in html:
                print("   ✅ MusicRecording schema found")
            else:
                print("   ❌ MusicRecording schema NOT found")
            
            # Check for VideoObject schema
            if '"@type":"VideoObject"' in html or '"@type": "VideoObject"' in html:
                print("   ✅ VideoObject schema found")
            else:
                print("   ❌ VideoObject schema NOT found")
        else:
            print(f"   ❌ Failed to load song page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing song page: {e}")
    
    # Test 4: AC/DC artist page - structured data with special characters
    print("\n4. Testing AC/DC artist page structured data...")
    try:
        response = requests.get(f"{BASE_URL}/artist/acdc", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Check for AC/DC name in structured data
            if "AC/DC" in html:
                print("   ✅ AC/DC name found in content")
            else:
                print("   ❌ AC/DC name NOT found in content")
            
            # Check for structured data presence
            if '"@type":"MusicGroup"' in html or '"@type": "MusicGroup"' in html:
                print("   ✅ MusicGroup schema found")
            else:
                print("   ❌ MusicGroup schema NOT found")
        else:
            print(f"   ❌ Failed to load AC/DC page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing AC/DC page: {e}")

def test_internal_linking():
    """Test internal linking improvements"""
    print("\n=== INTERNAL LINKING TESTS ===")
    
    # Test 5: Song page should contain links to other metallica songs
    print("\n5. Testing song page internal links (metallica-am-i-evil)...")
    try:
        response = requests.get(f"{BASE_URL}/songs/metallica-am-i-evil", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Look for links to other metallica songs
            metallica_song_links = re.findall(r'href="[^"]*songs/metallica-[^"]*"', html)
            if metallica_song_links:
                print(f"   ✅ Found {len(metallica_song_links)} links to other Metallica songs")
                # Show first few examples
                for i, link in enumerate(metallica_song_links[:3]):
                    print(f"      Example {i+1}: {link}")
            else:
                print("   ❌ No links to other Metallica songs found")
        else:
            print(f"   ❌ Failed to load song page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing song internal links: {e}")
    
    # Test 6: Song page should contain link to artist page
    print("\n6. Testing song page artist link (metallica-am-i-evil)...")
    try:
        response = requests.get(f"{BASE_URL}/songs/metallica-am-i-evil", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Look for link to artist page
            if 'href="/artist/metallica"' in html or "href='/artist/metallica'" in html:
                print("   ✅ Link to /artist/metallica found")
            else:
                print("   ❌ Link to /artist/metallica NOT found")
        else:
            print(f"   ❌ Failed to load song page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing song artist link: {e}")
    
    # Test 7: Artist page should contain related artist links
    print("\n7. Testing artist page related links (metallica)...")
    try:
        response = requests.get(f"{BASE_URL}/artist/metallica", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Look for related artist links (common metal bands)
            related_artists = ["megadeth", "slayer", "anthrax", "iron-maiden", "black-sabbath"]
            found_related = []
            
            for artist in related_artists:
                if f'href="/artist/{artist}"' in html or f"href='/artist/{artist}'" in html:
                    found_related.append(artist)
            
            if found_related:
                print(f"   ✅ Found {len(found_related)} related artist links: {', '.join(found_related)}")
            else:
                print("   ❌ No related artist links found")
        else:
            print(f"   ❌ Failed to load artist page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing artist related links: {e}")

def test_breadcrumbs():
    """Test breadcrumb implementation"""
    print("\n=== BREADCRUMB TESTS ===")
    
    # Test 8: Artist page breadcrumbs
    print("\n8. Testing artist page breadcrumbs...")
    try:
        response = requests.get(f"{BASE_URL}/artist/metallica", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Look for breadcrumb structure in JSON-LD
            breadcrumb_match = re.search(r'"@type":"BreadcrumbList"[^}]*"itemListElement":\s*\[(.*?)\]', html, re.DOTALL)
            if breadcrumb_match:
                breadcrumb_content = breadcrumb_match.group(1)
                # Count items (should be 3: Home → Artists → Artist Name Tabs)
                item_count = breadcrumb_content.count('"@type":"ListItem"')
                print(f"   ✅ BreadcrumbList found with {item_count} items")
                if item_count == 3:
                    print("   ✅ Correct breadcrumb structure (3 items)")
                else:
                    print(f"   ⚠️  Expected 3 breadcrumb items, found {item_count}")
            else:
                print("   ❌ BreadcrumbList structure NOT found")
        else:
            print(f"   ❌ Failed to load artist page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing artist breadcrumbs: {e}")
    
    # Test 9: Song page breadcrumbs
    print("\n9. Testing song page breadcrumbs...")
    try:
        response = requests.get(f"{BASE_URL}/songs/metallica-am-i-evil", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Look for breadcrumb structure in JSON-LD
            breadcrumb_match = re.search(r'"@type":"BreadcrumbList"[^}]*"itemListElement":\s*\[(.*?)\]', html, re.DOTALL)
            if breadcrumb_match:
                breadcrumb_content = breadcrumb_match.group(1)
                # Count items (should be 3: Home → Artist Tabs → Song Title)
                item_count = breadcrumb_content.count('"@type":"ListItem"')
                print(f"   ✅ BreadcrumbList found with {item_count} items")
                if item_count == 3:
                    print("   ✅ Correct breadcrumb structure (3 items)")
                else:
                    print(f"   ⚠️  Expected 3 breadcrumb items, found {item_count}")
            else:
                print("   ❌ BreadcrumbList structure NOT found")
        else:
            print(f"   ❌ Failed to load song page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing song breadcrumbs: {e}")

def test_previous_fixes():
    """Test that previous fixes still work"""
    print("\n=== PREVIOUS FIXES TESTS ===")
    
    # Test 10: Invalid artist should redirect to homepage
    print("\n10. Testing invalid artist redirect...")
    try:
        response = requests.get(f"{BASE_URL}/artist/totally-nonexistent-artist", headers=HEADERS, timeout=30, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 308:
            location = response.headers.get('Location', '')
            if location == '/' or location.endswith('/'):
                print("   ✅ 308 permanent redirect to homepage")
            else:
                print(f"   ❌ Redirects to wrong location: {location}")
        else:
            print(f"   ❌ Expected 308 redirect, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid artist redirect: {e}")
    
    # Test 11: Invalid song should redirect to artist page
    print("\n11. Testing invalid song redirect...")
    try:
        response = requests.get(f"{BASE_URL}/songs/van-halen-best-of-both-worlds", headers=HEADERS, timeout=30, allow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 308:
            location = response.headers.get('Location', '')
            if '/artist/van-halen' in location:
                print("   ✅ 308 permanent redirect to /artist/van-halen")
            else:
                print(f"   ❌ Redirects to wrong location: {location}")
        else:
            print(f"   ❌ Expected 308 redirect, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid song redirect: {e}")
    
    # Test 12: Valid artist should still work
    print("\n12. Testing valid artist still works...")
    try:
        response = requests.get(f"{BASE_URL}/artist/tesla", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Valid artist page loads correctly")
        else:
            print(f"   ❌ Valid artist page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing valid artist: {e}")
    
    # Test 13: Locale + artist should still work
    print("\n13. Testing locale + artist still works...")
    try:
        response = requests.get(f"{BASE_URL}/ja/artist/black-sabbath", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Locale + artist page loads correctly")
        else:
            print(f"   ❌ Locale + artist page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing locale + artist: {e}")

def test_sitemap():
    """Test sitemap improvements"""
    print("\n=== SITEMAP TESTS ===")
    
    # Test 14: Sitemap should not contain duplicate artist slugs
    print("\n14. Testing sitemap for duplicate artist slugs...")
    try:
        response = requests.get(f"{BASE_URL}/sitemap.xml", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            xml_content = response.text
            # Extract all artist URLs
            artist_urls = re.findall(r'<loc>[^<]*\/artist\/([^<\/]+)<\/loc>', xml_content)
            
            # Check for duplicates
            unique_artists = set(artist_urls)
            if len(artist_urls) == len(unique_artists):
                print(f"   ✅ No duplicate artist slugs found ({len(artist_urls)} unique artists)")
            else:
                duplicates = len(artist_urls) - len(unique_artists)
                print(f"   ❌ Found {duplicates} duplicate artist slugs")
        else:
            print(f"   ❌ Failed to load sitemap: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing sitemap duplicates: {e}")
    
    # Test 15: Sitemap should not contain junk entries
    print("\n15. Testing sitemap for junk entries...")
    try:
        response = requests.get(f"{BASE_URL}/sitemap.xml", headers=HEADERS, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            xml_content = response.text
            # Check for known junk entries
            junk_entries = ["fretmaster", "coming-soon"]
            found_junk = []
            
            for junk in junk_entries:
                if f"/artist/{junk}" in xml_content:
                    found_junk.append(junk)
            
            if not found_junk:
                print("   ✅ No junk entries found in sitemap")
            else:
                print(f"   ❌ Found junk entries: {', '.join(found_junk)}")
        else:
            print(f"   ❌ Failed to load sitemap: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing sitemap junk entries: {e}")

def main():
    """Run all SEO improvement tests"""
    print("🎸 DADROCK TABS SEO IMPROVEMENTS TESTING")
    print(f"Base URL: {BASE_URL}")
    print(f"User-Agent: {HEADERS['User-Agent']}")
    print("=" * 60)
    
    try:
        # Run all test suites
        test_structured_data()
        test_internal_linking()
        test_breadcrumbs()
        test_previous_fixes()
        test_sitemap()
        
        print("\n" + "=" * 60)
        print("🎸 SEO IMPROVEMENTS TESTING COMPLETE")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {e}")

if __name__ == "__main__":
    main()