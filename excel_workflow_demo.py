#!/usr/bin/env python3
"""
Excel Workflow Demo - VSS Integration System
Demonstrates complete Excel input/output workflow
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.excel_integration_processor import ExcelIntegrationProcessor
from src.utils.excel_processor import ExcelProcessor
from src.utils.logger import get_logger


def demo_excel_workflow():
    """Demo complete Excel workflow"""
    print("🚀 VSS Integration System - Excel Workflow Demo")
    print("=" * 60)
    
    # Setup logging
    logger = get_logger("excel_demo")
    logger.info("Starting Excel workflow demo")
    
    try:
        # Initialize processor
        print("\n🔧 Initializing Excel Integration Processor...")
        processor = ExcelIntegrationProcessor(max_workers=2, use_real_apis=True)
        
        # Step 1: Create input template
        print("\n📝 Step 1: Creating input template...")
        template_path = processor.create_input_template()
        print(f"   ✅ Template created: {template_path}")
        
        # Step 2: Validate sample input file
        print("\n🔍 Step 2: Validating sample input file...")
        sample_file = "data/input/sample_mst_input.xlsx"
        
        if os.path.exists(sample_file):
            validation = processor.validate_input_file(sample_file)
            print(f"   📊 File validation:")
            print(f"      - Valid: {validation['valid']}")
            print(f"      - Total rows: {validation['total_rows']}")
            print(f"      - MST count: {validation['mst_count']}")
            print(f"      - MST column: {validation['mst_column']}")
            
            if validation['errors']:
                print(f"      - Errors: {validation['errors']}")
        else:
            print(f"   ⚠️ Sample file not found: {sample_file}")
            return False
        
        # Step 3: Process Excel file
        print("\n⚙️ Step 3: Processing Excel file...")
        print(f"   📁 Input file: {sample_file}")
        print(f"   📁 Output directory: data/output")
        
        start_time = time.time()
        summary = processor.process_excel_file(sample_file, "data/output")
        processing_time = time.time() - start_time
        
        # Step 4: Display results
        print("\n📈 Step 4: Processing Results")
        print("=" * 40)
        
        results = summary['processing_results']
        print(f"   📋 Total processed: {results['total_processed']}")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📊 Success rate: {results['success_rate']:.1f}%")
        print(f"   💎 Average confidence: {results['average_confidence']:.3f}")
        print(f"   ⏱️ Processing time: {results['processing_time']:.2f}s")
        print(f"   ⚡ Processing rate: {results['processing_rate']:.2f} MST/s")
        
        # Data quality distribution
        quality_dist = summary['data_quality_distribution']
        print(f"\n   📊 Data Quality Distribution:")
        print(f"      - HIGH: {quality_dist['high']}")
        print(f"      - MEDIUM: {quality_dist['medium']}")
        print(f"      - LOW: {quality_dist['low']}")
        
        # Source distribution
        source_dist = summary['source_distribution']
        print(f"\n   📡 Data Source Distribution:")
        print(f"      - Real API: {source_dist['real_api']}")
        print(f"      - Generated: {source_dist['generated']}")
        
        # Output files
        output_files = summary['output_files']
        print(f"\n   📁 Output Files Generated:")
        print(f"      - Summary Report: {output_files['summary_report']}")
        print(f"      - Detailed Report: {output_files['detailed_report']}")
        print(f"      - Output Directory: {output_files['output_directory']}")
        
        # Step 5: Verify output files
        print("\n🔍 Step 5: Verifying output files...")
        summary_file = output_files['summary_report']
        detailed_file = output_files['detailed_report']
        
        if os.path.exists(summary_file):
            file_size = os.path.getsize(summary_file)
            print(f"   ✅ Summary report: {summary_file} ({file_size:,} bytes)")
        else:
            print(f"   ❌ Summary report not found: {summary_file}")
        
        if os.path.exists(detailed_file):
            file_size = os.path.getsize(detailed_file)
            print(f"   ✅ Detailed report: {detailed_file} ({file_size:,} bytes)")
        else:
            print(f"   ⚠️ Detailed report not generated: {detailed_file}")
        
        # Step 6: Save summary to JSON
        print("\n💾 Step 6: Saving summary to JSON...")
        summary_file_json = f"data/output/excel_workflow_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(summary_file_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Summary saved: {summary_file_json}")
        
        print("\n🎉 Excel Workflow Demo Completed Successfully!")
        print("=" * 60)
        print("✅ Input template created")
        print("✅ Excel file validated")
        print("✅ MSTs processed through VSS system")
        print("✅ Excel reports generated")
        print("✅ Summary saved to JSON")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def demo_batch_processing():
    """Demo batch processing with different file sizes"""
    print("\n\n🔄 Batch Processing Demo")
    print("=" * 40)
    
    processor = ExcelIntegrationProcessor(max_workers=4, use_real_apis=False)
    
    # Test with different batch sizes
    batch_sizes = [5, 10, 20]
    
    for batch_size in batch_sizes:
        print(f"\n📊 Testing with {batch_size} MSTs...")
        
        # Create test data
        test_msts = [f"11019{i:06d}" for i in range(1000, 1000 + batch_size)]
        
        # Create temporary Excel file
        import pandas as pd
        temp_file = f"data/input/temp_batch_{batch_size}.xlsx"
        df = pd.DataFrame({'Dãy số 10 chữ số': test_msts})
        df.to_excel(temp_file, index=False)
        
        try:
            start_time = time.time()
            summary = processor.process_excel_file(temp_file, f"data/output/batch_{batch_size}")
            processing_time = time.time() - start_time
            
            results = summary['processing_results']
            print(f"   ✅ Processed {batch_size} MSTs in {processing_time:.2f}s")
            print(f"   📊 Success rate: {results['success_rate']:.1f}%")
            print(f"   ⚡ Rate: {results['processing_rate']:.2f} MST/s")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)


def main():
    """Main demo function"""
    print("🚀 VSS Integration System - Excel Workflow Demo")
    print("=" * 60)
    print("This demo showcases the complete Excel input/output workflow")
    print("=" * 60)
    
    # Create necessary directories
    Path("data/input").mkdir(parents=True, exist_ok=True)
    Path("data/output").mkdir(parents=True, exist_ok=True)
    Path("data/templates").mkdir(parents=True, exist_ok=True)
    
    try:
        # Run main demo
        success = demo_excel_workflow()
        
        if success:
            # Run batch processing demo
            demo_batch_processing()
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
