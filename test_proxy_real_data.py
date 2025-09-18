#!/usr/bin/env python3
"""
Test script với proxy configuration và dữ liệu thực tế từ Excel
"""
import sys
import os
import pandas as pd
import json
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.config.settings import config
from src.utils.logger import get_logger

def load_msts_from_excel(file_path):
    """Load MSTs from Excel file"""
    try:
        df = pd.read_excel(file_path)
        # Assuming the column name is 'Dãy số 10 chữ số'
        mst_column = 'Dãy số 10 chữ số'
        if mst_column in df.columns:
            msts = df[mst_column].astype(str).tolist()
            return msts
        else:
            print(f"Available columns: {df.columns.tolist()}")
            return df.iloc[:, 0].astype(str).tolist()  # Use first column
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []

def test_proxy_connection():
    """Test proxy connection"""
    print("🔍 Testing proxy connection...")
    
    # Check proxy configuration
    security_config = config.get('security', {})
    enable_proxy = security_config.get('enable_proxy', False)
    proxy_config = security_config.get('proxy_config', {})
    
    print(f"   Proxy enabled: {enable_proxy}")
    print(f"   HTTP proxy: {proxy_config.get('http', 'None')}")
    print(f"   HTTPS proxy: {proxy_config.get('https', 'None')}")
    
    if enable_proxy:
        print("   ✅ Proxy configuration is enabled")
    else:
        print("   ❌ Proxy configuration is disabled")
    
    return enable_proxy

def run_test_with_proxy():
    """Run test with proxy configuration"""
    print("🚀 VSS Integration System - Test with Proxy")
    print("=" * 60)
    
    # Setup logging
    logger = get_logger("proxy_test")
    logger.info("Starting proxy test")
    
    # Test proxy connection
    proxy_enabled = test_proxy_connection()
    
    # Load MSTs from Excel
    excel_file = "../test_mst_50.xlsx"
    print(f"\n📊 Loading MSTs from {excel_file}...")
    
    msts = load_msts_from_excel(excel_file)
    if not msts:
        print("❌ No MSTs loaded from Excel file")
        return False
    
    print(f"   ✅ Loaded {len(msts)} MSTs")
    print(f"   📋 First 5 MSTs: {msts[:5]}")
    
    # Initialize processor with real APIs
    print(f"\n🔧 Initializing VSS Integration Processor...")
    processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=True)
    
    # Test with first 5 MSTs
    test_msts = msts[:5]
    print(f"\n🧪 Testing with first {len(test_msts)} MSTs...")
    print(f"   Test MSTs: {test_msts}")
    
    start_time = time.time()
    
    try:
        # Process test MSTs
        results = processor.process_batch(test_msts)
        
        processing_time = time.time() - start_time
        
        # Analyze results
        successful = len([r for r in results if r.success])
        failed = len([r for r in results if not r.success])
        avg_confidence = sum(r.confidence_score for r in results if r.success) / successful if successful > 0 else 0
        
        print(f"\n📈 Test Results:")
        print(f"   📋 Total processed: {len(results)}")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📊 Success rate: {successful/len(results)*100:.1f}%")
        print(f"   💎 Average confidence: {avg_confidence:.2f}")
        print(f"   ⏱️ Processing time: {processing_time:.2f}s")
        print(f"   ⚡ Rate: {len(results)/processing_time:.2f} MST/s")
        
        # Show detailed results
        print(f"\n📋 Detailed Results:")
        for i, result in enumerate(results):
            status = "✅" if result.success else "❌"
            print(f"   {i+1}. {result.mst}: {status} (Confidence: {result.confidence_score:.2f}, Source: {result.source})")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"proxy_test_results_{timestamp}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'proxy_enabled': proxy_enabled,
            'proxy_config': config.get('security.proxy_config', {}),
            'test_msts': test_msts,
            'total_processed': len(results),
            'successful': successful,
            'failed': failed,
            'success_rate': successful/len(results)*100,
            'average_confidence': avg_confidence,
            'processing_time': processing_time,
            'processing_rate': len(results)/processing_time,
            'results': [
                {
                    'mst': r.mst,
                    'success': r.success,
                    'confidence_score': r.confidence_score,
                    'data_quality': r.data_quality,
                    'source': r.source,
                    'processing_time': r.processing_time,
                    'error': r.error if hasattr(r, 'error') else None
                }
                for r in results
            ]
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_test_with_proxy()
    sys.exit(0 if success else 1)
