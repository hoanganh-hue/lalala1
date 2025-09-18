#!/usr/bin/env python3
"""
Enhanced Excel Processor CLI with robust error handling
"""
import argparse
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.processors.excel_integration_processor import ExcelIntegrationProcessor
from src.utils.logger import setup_module_logger
from src.config.settings import config

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Enhanced Excel Processor for VSS Integration")
    parser.add_argument("command", choices=["process", "test"], help="Command to execute")
    parser.add_argument("input_file", help="Input Excel file path")
    parser.add_argument("--output", "-o", help="Output directory", default="data/output")
    parser.add_argument("--workers", "-w", type=int, help="Number of workers", default=2)
    parser.add_argument("--real-apis", action="store_true", help="Use real APIs (default: False)")
    parser.add_argument("--batch-size", type=int, help="Batch size for processing", default=25)
    parser.add_argument("--max-retries", type=int, help="Maximum retries per request", default=5)
    parser.add_argument("--timeout", type=int, help="Request timeout in seconds", default=45)
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_module_logger("enhanced_cli", level=log_level)
    
    # Update configuration based on arguments
    config.set("api.timeout", args.timeout)
    config.set("api.max_retries", args.max_retries)
    config.set("processing.max_workers", args.workers)
    config.set("processing.batch_size", args.batch_size)
    
    logger.info("🚀 Enhanced Excel Processor CLI")
    logger.info(f"📁 Input file: {args.input_file}")
    logger.info(f"📁 Output directory: {args.output}")
    logger.info(f"👥 Workers: {args.workers}")
    logger.info(f"🌐 Real APIs: {args.real_apis}")
    logger.info(f"📦 Batch size: {args.batch_size}")
    logger.info(f"🔄 Max retries: {args.max_retries}")
    logger.info(f"⏱️ Timeout: {args.timeout}s")
    logger.info("=" * 50)
    
    try:
        if args.command == "process":
            process_excel_file(args, logger)
        elif args.command == "test":
            test_connection(args, logger)
    except KeyboardInterrupt:
        logger.info("⏹️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

def process_excel_file(args, logger):
    """Process Excel file with enhanced error handling"""
    input_path = Path(args.input_file)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"❌ Input file not found: {input_path}")
        sys.exit(1)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = ExcelIntegrationProcessor(
        max_workers=args.workers,
        use_real_apis=args.real_apis
    )
    
    start_time = time.time()
    
    try:
        # Process the Excel file
        results = processor.process_excel_file(
            str(input_path),
            str(output_path)
        )
        
        processing_time = time.time() - start_time
        
        # Generate summary
        summary = generate_processing_summary(results, processing_time)
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = output_path / f"enhanced_processing_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "results": [result.__dict__ for result in results]
            }, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary_file = output_path / f"enhanced_processing_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print_processing_summary(summary)
        
        logger.info(f"✅ Processing completed successfully!")
        logger.info(f"📊 Results saved to: {results_file}")
        logger.info(f"📋 Summary saved to: {summary_file}")
        
    except Exception as e:
        logger.error(f"❌ Processing failed: {str(e)}")
        raise

def test_connection(args, logger):
    """Test API connections"""
    logger.info("🔍 Testing API connections...")
    
    from src.api.enterprise_client import EnterpriseAPIClient
    from src.api.vss_client import VSSAPIClient
    
    # Test enterprise API
    logger.info("Testing Enterprise API...")
    try:
        enterprise_client = EnterpriseAPIClient()
        test_result = enterprise_client.get_company_info("0123456789")
        if test_result:
            logger.info("✅ Enterprise API: Connected successfully")
        else:
            logger.warning("⚠️ Enterprise API: Connected but no data returned")
    except Exception as e:
        logger.error(f"❌ Enterprise API: Connection failed - {str(e)}")
    
    # Test VSS API
    logger.info("Testing VSS API...")
    try:
        vss_client = VSSAPIClient()
        test_result = vss_client.get_employee_data("0123456789")
        if test_result:
            logger.info("✅ VSS API: Connected successfully")
        else:
            logger.warning("⚠️ VSS API: Connected but no data returned")
    except Exception as e:
        logger.error(f"❌ VSS API: Connection failed - {str(e)}")
    
    logger.info("🔍 Connection test completed")

def generate_processing_summary(results: List, processing_time: float) -> Dict[str, Any]:
    """Generate processing summary"""
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful
    
    # Count by source
    sources = {}
    for result in results:
        source = result.source
        sources[source] = sources.get(source, 0) + 1
    
    # Count by data quality
    quality_counts = {}
    for result in results:
        quality = result.data_quality
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    # Calculate average confidence
    avg_confidence = sum(r.confidence_score for r in results if r.success) / successful if successful > 0 else 0
    
    # Calculate average processing time
    avg_processing_time = sum(r.processing_time for r in results) / total if total > 0 else 0
    
    return {
        "processing_time": processing_time,
        "total_processed": total,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "average_confidence": avg_confidence,
        "average_processing_time": avg_processing_time,
        "processing_rate": total / processing_time if processing_time > 0 else 0,
        "sources": sources,
        "data_quality": quality_counts,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def print_processing_summary(summary: Dict[str, Any]):
    """Print processing summary to console"""
    print("\n" + "=" * 60)
    print("📊 PROCESSING SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total time: {summary['processing_time']:.2f} seconds")
    print(f"📈 Total processed: {summary['total_processed']:,}")
    print(f"✅ Successful: {summary['successful']:,}")
    print(f"❌ Failed: {summary['failed']:,}")
    print(f"📊 Success rate: {summary['success_rate']:.1f}%")
    print(f"🎯 Average confidence: {summary['average_confidence']:.3f}")
    print(f"⚡ Processing rate: {summary['processing_rate']:.2f} MSTs/second")
    print(f"🕐 Average time per MST: {summary['average_processing_time']:.3f}s")
    
    print("\n📋 Data Sources:")
    for source, count in summary['sources'].items():
        percentage = (count / summary['total_processed'] * 100) if summary['total_processed'] > 0 else 0
        print(f"   {source}: {count:,} ({percentage:.1f}%)")
    
    print("\n📊 Data Quality:")
    for quality, count in summary['data_quality'].items():
        percentage = (count / summary['total_processed'] * 100) if summary['total_processed'] > 0 else 0
        print(f"   {quality}: {count:,} ({percentage:.1f}%)")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

