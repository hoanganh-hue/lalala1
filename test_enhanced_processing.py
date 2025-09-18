#!/usr/bin/env python3
"""
Test script for enhanced processing with better error handling
"""
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.utils.logger import setup_module_logger

def test_enhanced_processing():
    """Test the enhanced processing with a small batch"""
    logger = setup_module_logger("test_enhanced")
    
    logger.info("🧪 Testing Enhanced VSS Processing")
    logger.info("=" * 50)
    
    # Test with a small batch of MSTs
    test_msts = [
        "0123456789",
        "0987654321", 
        "1122334455",
        "5566778899",
        "9988776655"
    ]
    
    logger.info(f"Testing with {len(test_msts)} MSTs: {test_msts}")
    
    # Initialize processor with real APIs
    processor = VSSIntegrationProcessor(
        max_workers=2,
        use_real_apis=True
    )
    
    start_time = time.time()
    
    try:
        # Process the batch
        results = processor.process_batch(test_msts)
        
        processing_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        logger.info(f"✅ Processing completed in {processing_time:.2f} seconds")
        logger.info(f"📊 Results: {successful} successful, {failed} failed")
        
        # Print detailed results
        for result in results:
            status = "✅" if result.success else "❌"
            logger.info(
                f"{status} MST {result.mst}: "
                f"Quality={result.data_quality}, "
                f"Confidence={result.confidence_score:.3f}, "
                f"Source={result.source}, "
                f"Time={result.processing_time:.3f}s"
            )
            
            if result.api_errors:
                logger.info(f"   API Errors: {', '.join(result.api_errors)}")
        
        # Save test results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"enhanced_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_info": {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "msts_tested": test_msts,
                    "processing_time": processing_time,
                    "successful": successful,
                    "failed": failed
                },
                "results": [result.__dict__ for result in results]
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Test results saved to: {results_file}")
        
        return successful == len(test_msts)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_enhanced_processing()
    sys.exit(0 if success else 1)

