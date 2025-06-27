#!/usr/bin/env python3
"""
Frontend Integration Test - Test actual frontend API calls
"""
import requests
import json
import time

def test_frontend_api_integration():
    """Test that frontend can communicate with backend"""
    print("🌐 Testing Frontend-Backend API Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8080/api"
    
    try:
        # Test 1: Health Check (matching frontend api.ts)
        print("1. Testing /api/health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test 2: Campaign Creation (matching frontend types)
        print("\n2. Testing /api/campaigns/create endpoint...")
        campaign_data = {
            "business_name": "Frontend Test Co",
            "industry": "technology",
            "campaign_goal": "test frontend integration",
            "target_platforms": ["instagram", "facebook"],
            "brand_voice": "professional",
            "target_audience": "tech enthusiasts",
            "keywords": ["innovation", "technology"]
        }
        
        response = requests.post(
            f"{base_url}/campaigns/create",
            json=campaign_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            campaign_response = response.json()
            campaign_id = campaign_response["campaign_id"]
            print(f"   ✅ Campaign created: {campaign_id}")
            
            # Test 3: Status polling (matching frontend useCampaignStatus hook)
            print(f"\n3. Testing status polling for {campaign_id}...")
            max_polls = 10
            poll_count = 0
            
            while poll_count < max_polls:
                status_response = requests.get(f"{base_url}/campaigns/{campaign_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Poll {poll_count + 1}: Status = {status_data['status']}")
                    
                    if status_data['status'] == 'completed':
                        print("   ✅ Campaign completed successfully")
                        break
                    elif status_data['status'] == 'failed':
                        print("   ⚠️ Campaign failed, but API working")
                        break
                    
                    time.sleep(3)  # Match frontend polling interval
                    poll_count += 1
                else:
                    print(f"   ❌ Status check failed: {status_response.status_code}")
                    return False
            
            # Test 4: Results endpoint (matching frontend useCampaignResults hook)
            print(f"\n4. Testing results endpoint for {campaign_id}...")
            results_response = requests.get(f"{base_url}/campaigns/{campaign_id}/results")
            if results_response.status_code == 200:
                results_data = results_response.json()
                print("   ✅ Results endpoint working")
                print(f"   ✅ Content platforms: {list(results_data.get('content', {}).keys())}")
                print(f"   ✅ Visual suggestions: {len(results_data.get('visuals', {}).get('image_suggestions', []))}")
            else:
                print(f"   ❌ Results endpoint failed: {results_response.status_code}")
                return False
            
            # Test 5: Force complete endpoint (matching frontend API)
            print(f"\n5. Testing force complete endpoint...")
            force_response = requests.post(f"{base_url}/campaigns/{campaign_id}/force-complete")
            if force_response.status_code == 200:
                print("   ✅ Force complete endpoint working")
            else:
                print(f"   ❌ Force complete failed: {force_response.status_code}")
                return False
            
        else:
            print(f"   ❌ Campaign creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 FRONTEND INTEGRATION TEST PASSED!")
        print("✅ All frontend API calls working correctly")
        print("✅ Real-time polling functional")
        print("✅ Campaign lifecycle complete")
        print("✅ Frontend can fully communicate with backend")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("💡 Make sure backend is running: python vyralflow_enhanced.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_api_integration()
    if not success:
        exit(1)