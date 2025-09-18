#!/usr/bin/env python3
"""
Test VSS API directly with MST 5200958920
"""

import requests
import time
import json

def test_vss_api_direct():
    """Test VSS API directly"""
    
    print("🔄 Testing VSS API directly with MST: 5200958920")
    
    # VSS API with proxy
    proxies = {
        'http': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301',
        'https': 'http://beba111:tDV5tkMchYUBMD@ip.mproxy.vn:12301'
    }
    
    url = "http://vssapp.teca.vn:8088/tcnnt/mstcn.jsp"
    params = {
        'mst': '5200958920',
        'tm': str(int(time.time() * 1000))
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json,text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8'
    }
    
    try:
        print("📡 Making request to VSS API...")
        response = requests.get(
            url,
            params=params,
            headers=headers,
            proxies=proxies,
            timeout=30,
            verify=False
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️ Response Time: {response.elapsed.total_seconds():.3f} seconds")
        print(f"📏 Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Try to parse as JSON
            try:
                data = response.json()
                print("✅ JSON Response received:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError:
                print("📄 HTML Response received (first 1000 characters):")
                print(response.text[:1000])
                print("...")
                
                # Try to extract company info from HTML
                import re
                
                # Search for common patterns
                patterns = {
                    'company_name': [
                        r'ten_doanh_nghiep["\s]*:["\s]*([^"<\n]+)',
                        r'Tên doanh nghiệp[:\s]*([^<\n]+)'
                    ],
                    'address': [
                        r'dia_chi["\s]*:["\s]*([^"<\n]+)',
                        r'Địa chỉ[:\s]*([^<\n]+)'
                    ],
                    'legal_rep': [
                        r'nguoi_dai_dien["\s]*:["\s]*([^"<\n]+)',
                        r'Người đại diện[:\s]*([^<\n]+)'
                    ]
                }
                
                extracted_data = {}
                for field, field_patterns in patterns.items():
                    for pattern in field_patterns:
                        match = re.search(pattern, response.text, re.IGNORECASE)
                        if match:
                            extracted_data[field] = match.group(1).strip()
                            break
                
                if extracted_data:
                    print("\n✅ Extracted Data:")
                    for field, value in extracted_data.items():
                        print(f"   {field}: {value}")
                else:
                    print("\n❌ No data patterns found in HTML response")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Request failed with error: {str(e)}")


def test_enterprise_api_direct():
    """Test Enterprise API directly"""
    
    print("\n🔄 Testing Enterprise API directly with MST: 5200958920")
    
    url = "https://thongtindoanhnghiep.co/api/company/5200958920"
    
    headers = {
        'User-Agent': 'VSS-Integration-System/3.0',
        'Accept': 'application/json'
    }
    
    try:
        print("📡 Making request to Enterprise API...")
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️ Response Time: {response.elapsed.total_seconds():.3f} seconds")
        print(f"📏 Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON Response received:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError:
                print("📄 Non-JSON Response:")
                print(response.text[:1000])
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Request failed with error: {str(e)}")


if __name__ == "__main__":
    print("🚀 Direct API Testing for MST: 5200958920")
    print("="*60)
    
    test_enterprise_api_direct()
    test_vss_api_direct()
    
    print("\n✅ Direct API testing completed")
