#!/usr/bin/env python3
"""
Backend API Test Suite for DadRock Tabs App
Focus: Interstitial Ad Duration Control Feature
"""

import requests
import json
import base64
import sys

# Configuration
BASE_URL = "https://rock-timer-panel.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Babyty99"

# Create Basic Auth header
auth_string = f"{ADMIN_USERNAME}:{ADMIN_PASSWORD}"
auth_bytes = auth_string.encode('utf-8')
auth_header = base64.b64encode(auth_bytes).decode('utf-8')
HEADERS = {
    'Authorization': f'Basic {auth_header}',
    'Content-Type': 'application/json'
}

def test_get_settings_default_ad_duration():
    """Test 1: GET /api/settings should return ad_duration field (default value is 5)"""
    print("\n=== Test 1: GET /api/settings - Check default ad_duration ===")
    
    try:
        response = requests.get(f"{BASE_URL}/settings", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if ad_duration exists and has default value
            if 'ad_duration' in data:
                ad_duration = data['ad_duration']
                print(f"✅ ad_duration found: {ad_duration}")
                
                if ad_duration == 5:
                    print("✅ Default ad_duration is correctly set to 5")
                    return True
                else:
                    print(f"❌ Expected default ad_duration=5, but got {ad_duration}")
                    return False
            else:
                print("❌ ad_duration field missing from response")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_put_admin_settings_valid_duration():
    """Test 2: PUT /api/admin/settings with valid ad_duration should save successfully"""
    print("\n=== Test 2: PUT /api/admin/settings - Save valid ad_duration=15 ===")
    
    try:
        payload = {"ad_duration": 15}
        response = requests.put(f"{BASE_URL}/admin/settings", 
                               headers=HEADERS, 
                               json=payload, 
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'updated successfully' in data.get('message', ''):
                print("✅ ad_duration=15 saved successfully")
                return True
            else:
                print(f"❌ Unexpected response format: {data}")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_settings_updated_duration():
    """Test 3: GET /api/settings should now return ad_duration: 15"""
    print("\n=== Test 3: GET /api/settings - Verify ad_duration=15 is saved ===")
    
    try:
        response = requests.get(f"{BASE_URL}/settings", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if 'ad_duration' in data:
                ad_duration = data['ad_duration']
                print(f"✅ ad_duration found: {ad_duration}")
                
                if ad_duration == 15:
                    print("✅ ad_duration correctly updated to 15")
                    return True
                else:
                    print(f"❌ Expected ad_duration=15, but got {ad_duration}")
                    return False
            else:
                print("❌ ad_duration field missing from response")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_validation_minimum_clamping():
    """Test 4: PUT with ad_duration: 2 should be clamped to 5 (minimum)"""
    print("\n=== Test 4: PUT /api/admin/settings - Test minimum validation (2 -> 5) ===")
    
    try:
        payload = {"ad_duration": 2}
        response = requests.put(f"{BASE_URL}/admin/settings", 
                               headers=HEADERS, 
                               json=payload, 
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            # Now check if it was clamped to 5
            get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
            if get_response.status_code == 200:
                data = get_response.json()
                ad_duration = data.get('ad_duration')
                print(f"Actual saved ad_duration: {ad_duration}")
                
                if ad_duration == 5:
                    print("✅ ad_duration correctly clamped from 2 to minimum 5")
                    return True
                else:
                    print(f"❌ Expected clamped value 5, but got {ad_duration}")
                    return False
            else:
                print("❌ Failed to retrieve updated settings")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_validation_maximum_clamping():
    """Test 5: PUT with ad_duration: 60 should be clamped to 30 (maximum)"""
    print("\n=== Test 5: PUT /api/admin/settings - Test maximum validation (60 -> 30) ===")
    
    try:
        payload = {"ad_duration": 60}
        response = requests.put(f"{BASE_URL}/admin/settings", 
                               headers=HEADERS, 
                               json=payload, 
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            # Now check if it was clamped to 30
            get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
            if get_response.status_code == 200:
                data = get_response.json()
                ad_duration = data.get('ad_duration')
                print(f"Actual saved ad_duration: {ad_duration}")
                
                if ad_duration == 30:
                    print("✅ ad_duration correctly clamped from 60 to maximum 30")
                    return True
                else:
                    print(f"❌ Expected clamped value 30, but got {ad_duration}")
                    return False
            else:
                print("❌ Failed to retrieve updated settings")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ad_duration_with_other_settings():
    """Test 6: Test that ad_duration is saved alongside other ad settings"""
    print("\n=== Test 6: PUT /api/admin/settings - Save ad_duration with other settings ===")
    
    try:
        payload = {
            "ad_duration": 20,
            "ad_headline": "Test Headline",
            "ad_description": "Test Description",
            "ad_button_text": "Test Button",
            "ad_link": "https://test.com"
        }
        
        response = requests.put(f"{BASE_URL}/admin/settings", 
                               headers=HEADERS, 
                               json=payload, 
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            # Verify all settings were saved correctly
            get_response = requests.get(f"{BASE_URL}/settings", timeout=10)
            if get_response.status_code == 200:
                data = get_response.json()
                print(f"Retrieved settings: {json.dumps(data, indent=2)}")
                
                success = True
                
                # Check ad_duration
                if data.get('ad_duration') == 20:
                    print("✅ ad_duration=20 saved correctly")
                else:
                    print(f"❌ ad_duration expected 20, got {data.get('ad_duration')}")
                    success = False
                
                # Check other ad settings
                if data.get('ad_headline') == "Test Headline":
                    print("✅ ad_headline saved correctly")
                else:
                    print(f"❌ ad_headline expected 'Test Headline', got '{data.get('ad_headline')}'")
                    success = False
                
                if data.get('ad_description') == "Test Description":
                    print("✅ ad_description saved correctly")
                else:
                    print(f"❌ ad_description expected 'Test Description', got '{data.get('ad_description')}'")
                    success = False
                    
                if data.get('ad_button_text') == "Test Button":
                    print("✅ ad_button_text saved correctly")
                else:
                    print(f"❌ ad_button_text expected 'Test Button', got '{data.get('ad_button_text')}'")
                    success = False
                    
                if data.get('ad_link') == "https://test.com":
                    print("✅ ad_link saved correctly")
                else:
                    print(f"❌ ad_link expected 'https://test.com', got '{data.get('ad_link')}'")
                    success = False
                
                return success
            else:
                print("❌ Failed to retrieve updated settings")
                return False
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_unauthorized_access():
    """Test 7: Verify unauthorized access is properly rejected"""
    print("\n=== Test 7: PUT /api/admin/settings - Test unauthorized access ===")
    
    try:
        payload = {"ad_duration": 25}
        # Use wrong credentials
        wrong_headers = {
            'Authorization': 'Basic d3JvbmdfdXNlcjp3cm9uZ19wYXNz',  # wrong_user:wrong_pass
            'Content-Type': 'application/json'
        }
        
        response = requests.put(f"{BASE_URL}/admin/settings", 
                               headers=wrong_headers, 
                               json=payload, 
                               timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Unauthorized access correctly rejected with 401")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all ad duration control tests"""
    print("=" * 80)
    print("BACKEND TESTING: Interstitial Ad Duration Control Feature")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin Credentials: {ADMIN_USERNAME}:{ADMIN_PASSWORD}")
    print("=" * 80)
    
    tests = [
        ("Default ad_duration value", test_get_settings_default_ad_duration),
        ("Save valid ad_duration", test_put_admin_settings_valid_duration),
        ("Verify saved ad_duration", test_get_settings_updated_duration),
        ("Minimum validation (clamping)", test_validation_minimum_clamping),
        ("Maximum validation (clamping)", test_validation_maximum_clamping),
        ("Save with other ad settings", test_ad_duration_with_other_settings),
        ("Unauthorized access rejection", test_unauthorized_access)
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                results.append(f"✅ {test_name}")
            else:
                failed += 1
                results.append(f"❌ {test_name}")
        except Exception as e:
            failed += 1
            results.append(f"❌ {test_name} - Exception: {e}")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for result in results:
        print(result)
    
    print(f"\nTotal Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Interstitial Ad Duration Control feature is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)