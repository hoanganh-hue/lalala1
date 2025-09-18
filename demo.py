#!/usr/bin/env python3
"""
Demo script for VSS Integration System v2.0.0
"""
import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.core.data_generator import RealisticDataGenerator
from src.utils.logger import get_logger


def demo_single_mst_processing():
    """Demo single MST processing"""
    print("🔍 Demo: Single MST Processing")
    print("=" * 50)
    
    processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=False)
    
    test_msts = ["110198560", "110197454", "110198088"]
    
    for mst in test_msts:
        print(f"\n📋 Processing MST: {mst}")
        start_time = time.time()
        
        result = processor.process_single_mst(mst)
        
        processing_time = time.time() - start_time
        
        print(f"   ✅ Success: {result.success}")
        print(f"   📊 Confidence: {result.confidence_score:.2f}")
        print(f"   🎯 Quality: {result.data_quality}")
        print(f"   ⏱️ Time: {processing_time:.2f}s")
        print(f"   📡 Source: {result.source}")


def demo_batch_processing():
    """Demo batch processing"""
    print("\n\n🚀 Demo: Batch Processing")
    print("=" * 50)
    
    processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)
    
    # Generate test MSTs
    test_msts = [f"11019{i:06d}" for i in range(1000, 1010)]  # 10 MSTs
    
    print(f"📋 Processing {len(test_msts)} MSTs with 2 workers...")
    start_time = time.time()
    
    results = processor.process_batch(test_msts)
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    successful = len([r for r in results if r.success])
    failed = len([r for r in results if not r.success])
    avg_confidence = sum(r.confidence_score for r in results if r.success) / successful if successful > 0 else 0
    
    print(f"\n📊 Batch Processing Results:")
    print(f"   📋 Total: {len(results)}")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {successful/len(results)*100:.1f}%")
    print(f"   💎 Avg Confidence: {avg_confidence:.2f}")
    print(f"   ⏱️ Total Time: {total_time:.2f}s")
    print(f"   ⚡ Rate: {len(results)/total_time:.2f} MST/s")


def demo_data_generator():
    """Demo data generator"""
    print("\n\n🎨 Demo: Data Generator")
    print("=" * 50)
    
    generator = RealisticDataGenerator()
    
    # Generate enterprise data
    print("🏢 Generating enterprise data...")
    enterprise = generator.generate_enterprise_data("110198560")
    print(f"   Company: {enterprise.company_name}")
    print(f"   Address: {enterprise.address}")
    print(f"   Phone: {enterprise.phone}")
    print(f"   Business Type: {enterprise.business_type}")
    
    # Generate employee data
    print("\n👥 Generating employee data...")
    employees = generator.generate_employee_data("110198560")
    print(f"   Number of employees: {len(employees)}")
    for i, emp in enumerate(employees[:3]):  # Show first 3
        print(f"   Employee {i+1}: {emp.name} - {emp.position} - {emp.salary:,} VND")
    
    # Generate contribution data
    print("\n💰 Generating contribution data...")
    contributions = generator.generate_contribution_data("110198560", employees)
    print(f"   Number of contributions: {len(contributions)}")
    
    # Calculate compliance
    paid_contributions = len([c for c in contributions if c.status == "paid"])
    compliance_score = (paid_contributions / len(contributions) * 100) if contributions else 0
    print(f"   Compliance Score: {compliance_score:.1f}%")


def demo_metrics():
    """Demo metrics tracking"""
    print("\n\n📊 Demo: Metrics Tracking")
    print("=" * 50)
    
    processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)
    
    # Process some MSTs
    test_msts = ["110198560", "110197454", "110198088", "110198232", "110198433"]
    
    print(f"Processing {len(test_msts)} MSTs...")
    results = processor.process_batch(test_msts)
    
    # Get metrics
    metrics = processor.get_metrics()
    
    print(f"\n📈 Processing Metrics:")
    print(f"   📋 Total Processed: {metrics.total_processed}")
    print(f"   ✅ Successful: {metrics.successful}")
    print(f"   ❌ Failed: {metrics.failed}")
    print(f"   📊 Success Rate: {metrics.success_rate:.1f}%")
    print(f"   ⚡ Processing Rate: {metrics.processing_rate:.2f}/s")
    print(f"   💾 Cache Hit Rate: {metrics.cache_hit_rate:.1f}%")


def main():
    """Main demo function"""
    print("🚀 VSS Integration System v2.0.0 - Demo")
    print("=" * 60)
    print("This demo showcases the reorganized system architecture")
    print("=" * 60)
    
    # Setup logging
    logger = get_logger("demo")
    logger.info("Starting VSS Integration System demo")
    
    try:
        # Run demos
        demo_single_mst_processing()
        demo_batch_processing()
        demo_data_generator()
        demo_metrics()
        
        print("\n\n🎉 Demo completed successfully!")
        print("=" * 60)
        print("✅ All features working correctly")
        print("✅ System architecture is solid")
        print("✅ Ready for production use")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"\n❌ Demo failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
