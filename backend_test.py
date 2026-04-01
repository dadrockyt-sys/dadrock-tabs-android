#!/usr/bin/env python3
"""
Backend Test Suite for DadRock Tabs i18n Locale URL Routing Middleware
Tests the middleware at /app/middleware.js for localized URL rewrites
"""

import asyncio
import aiohttp
import os
import sys
from typing import Dict, List, Tuple

# Get base URL from environment
BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://admin-sync-hub-1.preview.emergentagent.com')

# Test configuration
LOCALES = ['es', 'pt', 'ko', 'de', 'fr', 'ja', 'pt-br', 'zh', 'ru', 'hi', 'sv', 'fi']
SUBPAGES = ['quickies', 'coming-soon', 'top-lessons', 'artist/acdc']

class I18nMiddlewareTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
        self.results = []
        
    async def setup(self):
        """Setup HTTP session"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    async def test_url(self, url: str, expected_status: int = 200, description: str = "") -> Tuple[bool, str]:
        """Test a single URL and return (success, message)"""
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                status = response.status
                success = status == expected_status
                
                if success:
                    message = f"✅ {description}: {url} → {status}"
                else:
                    message = f"❌ {description}: {url} → {status} (expected {expected_status})"
                    
                return success, message
                
        except Exception as e:
            message = f"❌ {description}: {url} → ERROR: {str(e)}"
            return False, message
            
    async def test_localized_subpages(self) -> List[Tuple[bool, str]]:
        """Test 1: Localized subpages return 200"""
        print("\n=== TEST 1: Localized subpages return 200 ===")
        results = []
        
        test_urls = [
            f"{self.base_url}/es/quickies",
            f"{self.base_url}/pt/coming-soon", 
            f"{self.base_url}/ko/top-lessons",
            f"{self.base_url}/de/quickies",
            f"{self.base_url}/fr/artist/acdc",
            f"{self.base_url}/ja/coming-soon",
            f"{self.base_url}/pt-br/top-lessons",
            f"{self.base_url}/zh/quickies",
            f"{self.base_url}/ru/quickies",
            f"{self.base_url}/hi/top-lessons",
            f"{self.base_url}/sv/coming-soon",
            f"{self.base_url}/fi/quickies"
        ]
        
        for url in test_urls:
            success, message = await self.test_url(url, 200, "Localized subpage")
            results.append((success, message))
            print(message)
            
        return results
        
    async def test_non_localized_pages(self) -> List[Tuple[bool, str]]:
        """Test 2: Non-localized English pages still work (200)"""
        print("\n=== TEST 2: Non-localized English pages still work ===")
        results = []
        
        test_urls = [
            f"{self.base_url}/",
            f"{self.base_url}/quickies",
            f"{self.base_url}/coming-soon", 
            f"{self.base_url}/top-lessons"
        ]
        
        for url in test_urls:
            success, message = await self.test_url(url, 200, "Non-localized page")
            results.append((success, message))
            print(message)
            
        return results
        
    async def test_api_routes(self) -> List[Tuple[bool, str]]:
        """Test 3: API routes still work (not intercepted by middleware)"""
        print("\n=== TEST 3: API routes still work ===")
        results = []
        
        test_urls = [
            f"{self.base_url}/api/settings",
            f"{self.base_url}/api/health"
        ]
        
        for url in test_urls:
            success, message = await self.test_url(url, 200, "API route")
            results.append((success, message))
            print(message)
            
        return results
        
    async def test_localized_homepage_paths(self) -> List[Tuple[bool, str]]:
        """Test 4: Localized homepage paths still work (200)"""
        print("\n=== TEST 4: Localized homepage paths still work ===")
        results = []
        
        test_urls = [
            f"{self.base_url}/es",
            f"{self.base_url}/fr",
            f"{self.base_url}/pt-br"
        ]
        
        for url in test_urls:
            success, message = await self.test_url(url, 200, "Localized homepage")
            results.append((success, message))
            print(message)
            
        return results
        
    async def test_sitemap_generation(self) -> List[Tuple[bool, str]]:
        """Test 5: Sitemap still generates correctly"""
        print("\n=== TEST 5: Sitemap generation ===")
        results = []
        
        url = f"{self.base_url}/sitemap.xml"
        
        try:
            async with self.session.get(url) as response:
                status = response.status
                content = await response.text()
                
                if status == 200:
                    # Check if it's valid XML and contains hreflang alternates
                    if 'xml' in content and 'hreflang' in content:
                        success = True
                        message = f"✅ Sitemap: {url} → {status} (contains XML with hreflang alternates)"
                    else:
                        success = False
                        message = f"❌ Sitemap: {url} → {status} (missing XML or hreflang content)"
                else:
                    success = False
                    message = f"❌ Sitemap: {url} → {status} (expected 200)"
                    
                results.append((success, message))
                print(message)
                
        except Exception as e:
            message = f"❌ Sitemap: {url} → ERROR: {str(e)}"
            results.append((False, message))
            print(message)
            
        return results
        
    async def run_all_tests(self):
        """Run all middleware tests"""
        print(f"🧪 Testing i18n Locale URL Routing Middleware")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Run all test suites
            test_1_results = await self.test_localized_subpages()
            test_2_results = await self.test_non_localized_pages()
            test_3_results = await self.test_api_routes()
            test_4_results = await self.test_localized_homepage_paths()
            test_5_results = await self.test_sitemap_generation()
            
            # Combine all results
            all_results = test_1_results + test_2_results + test_3_results + test_4_results + test_5_results
            
            # Calculate summary
            total_tests = len(all_results)
            passed_tests = sum(1 for success, _ in all_results if success)
            failed_tests = total_tests - passed_tests
            
            print("\n" + "=" * 80)
            print("📊 TEST SUMMARY")
            print("=" * 80)
            print(f"Total Tests: {total_tests}")
            print(f"✅ Passed: {passed_tests}")
            print(f"❌ Failed: {failed_tests}")
            print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
            
            if failed_tests > 0:
                print("\n🚨 FAILED TESTS:")
                for success, message in all_results:
                    if not success:
                        print(f"  {message}")
                        
            print("\n" + "=" * 80)
            
            # Return overall success
            return failed_tests == 0
            
        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    try:
        tester = I18nMiddlewareTest()
        success = await tester.run_all_tests()
        
        if success:
            print("🎉 ALL TESTS PASSED - i18n middleware is working correctly!")
            sys.exit(0)
        else:
            print("💥 SOME TESTS FAILED - i18n middleware needs attention!")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 TEST RUNNER ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())