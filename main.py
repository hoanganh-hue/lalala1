#!/usr/bin/env python3
"""
Main Entry Point for VSS Integration System V3.1
Hệ thống tích hợp VSS hoàn chỉnh với trích xuất dữ liệu đầy đủ

🎯 Features:
- Complete enterprise data extraction
- Full VSS data extraction (employees, contributions, claims, hospitals)
- Real-time processing with high accuracy
- World-class data validation
- Production-ready performance

Author: MiniMax Agent
Date: 2025-09-19
Version: 3.1.0
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import V3.1 Complete VSS Integration Processor
from src.processors.complete_vss_integration_processor import (
    CompleteVSSIntegrationProcessor, CompleteProcessingResult, process_mst_complete
)
from src.config.settings import config
from src.utils.logger import get_logger

# Version info
__version__ = "3.1.0"
__title__ = "VSS Integration System V3.1"
__description__ = "Complete VSS Integration with Full Data Extraction"


def print_banner():
    """Print application banner"""
    banner = f"""
🚀 {__title__}
{__description__}
Version: {__version__} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 Complete Data Flow:
MST Input → API Doanh nghiệp → VSS Data Extraction → JSON Standardization

📊 VSS Data Extraction:
👥 Employee Records | 💰 Insurance Contributions | 📋 Insurance Claims | 🏥 Hospital Network

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(banner)


async def process_single_mst(mst: str, save_result: bool = True) -> CompleteProcessingResult:
    """
    Process single MST with complete VSS data extraction
    
    Args:
        mst: Mã số thuế doanh nghiệp
        save_result: Save result to JSON file
        
    Returns:
        CompleteProcessingResult: Comprehensive processing result
    """
    logger = get_logger("main")
    logger.info(f"🏢 Processing single MST: {mst}")
    
    try:
        # Use V3.1 complete processor
        result = await process_mst_complete(mst)
        
        # Print summary
        print(f"\n📋 Processing Summary for MST: {mst}")
        print(f"{'='*60}")
        print(f"✅ Status: {result.processing_status.upper()}")
        print(f"⏱️  Duration: {result.total_processing_duration_ms:.2f}ms")
        print(f"📊 Quality Score: {result.overall_data_quality_score:.1f}/100")
        print(f"📈 Completeness: {result.data_completeness_percentage:.1f}%")
        
        if result.vss_data:
            print(f"\n🔍 VSS Data Summary:")
            print(f"👥 Employees: {result.total_employees}")
            print(f"💰 Contributions: {len(result.vss_data.contributions)}")
            print(f"📋 Insurance Claims: {result.total_insurance_claims}")
            print(f"🏥 Related Hospitals: {result.total_related_hospitals}")
        
        # Print warnings and errors
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings[:3]:
                print(f"   • {warning}")
        
        if result.errors:
            print(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"   • {error}")
        
        # Save result if requested
        if save_result:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"vss_result_{mst}_{timestamp}.json"
            save_processing_result(result, filename)
            print(f"\n💾 Result saved to: {filename}")
        
        logger.info(f"✅ MST {mst} processed successfully - Quality: {result.overall_data_quality_score:.1f}/100")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error processing MST {mst}: {str(e)}")
        print(f"💥 Error processing MST {mst}: {str(e)}")
        raise


async def process_batch(msts: List[str], max_workers: int = 4, save_results: bool = True) -> List[CompleteProcessingResult]:
    """
    Process batch of MSTs with complete VSS data extraction
    
    Args:
        msts: List of MST codes
        max_workers: Maximum concurrent workers
        save_results: Save results to files
        
    Returns:
        List[CompleteProcessingResult]: Batch processing results
    """
    logger = get_logger("main")
    logger.info(f"🚀 Processing batch of {len(msts)} MSTs with {max_workers} workers")
    
    print(f"\n🚀 Batch Processing Started")
    print(f"📊 MSTs to process: {len(msts)}")
    print(f"⚡ Max workers: {max_workers}")
    
    results = []
    start_time = datetime.now()
    
    try:
        # Create processor
        processor = CompleteVSSIntegrationProcessor()
        
        # Process MSTs concurrently (limited by max_workers)
        semaphore = asyncio.Semaphore(max_workers)
        
        async def process_with_semaphore(mst):
            async with semaphore:
                return await processor.process_complete_enterprise_vss_data(mst)
        
        # Execute batch processing
        tasks = [process_with_semaphore(mst) for mst in msts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ MST {msts[i]} failed: {str(result)}")
                print(f"❌ MST {msts[i]}: Error - {str(result)}")
            else:
                processed_results.append(result)
                status = "✅" if result.is_successful else "❌"
                print(f"{status} MST {msts[i]}: {result.processing_status} - Quality: {result.overall_data_quality_score:.1f}/100")
        
        # Summary statistics
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        successful = len([r for r in processed_results if r.is_successful])
        
        print(f"\n📊 Batch Processing Summary")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful}/{len(msts)}")
        print(f"❌ Failed: {len(msts) - successful}/{len(msts)}")
        print(f"⏱️  Total Time: {total_duration:.2f}s")
        print(f"🚀 Throughput: {len(msts)/total_duration:.2f} MST/second")
        
        if successful > 0:
            avg_quality = sum(r.overall_data_quality_score for r in processed_results if r.is_successful) / successful
            print(f"📈 Average Quality: {avg_quality:.1f}/100")
        
        # Save batch results if requested
        if save_results and processed_results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            batch_filename = f"vss_batch_results_{len(msts)}mst_{timestamp}.json"
            save_batch_results(processed_results, batch_filename)
            print(f"\n💾 Batch results saved to: {batch_filename}")
        
        logger.info(f"✅ Batch processing completed: {successful}/{len(msts)} successful")
        return processed_results
        
    except Exception as e:
        logger.error(f"💥 Batch processing failed: {str(e)}")
        print(f"💥 Batch processing error: {str(e)}")
        raise


def save_processing_result(result: CompleteProcessingResult, filename: str):
    """Save single processing result to JSON"""
    try:
        result_dict = {
            "processing_info": {
                "processing_id": result.processing_id,
                "company_tax_code": result.company_tax_code,
                "processing_status": result.processing_status,
                "processing_duration_ms": result.total_processing_duration_ms,
                "data_quality_score": result.overall_data_quality_score,
                "data_completeness": result.data_completeness_percentage,
                "timestamp": result.processing_start_time.isoformat()
            },
            "integrated_json": result.integrated_json,
            "summary_statistics": {
                "total_employees": result.total_employees,
                "total_contribution_amount": result.total_contribution_amount,
                "total_insurance_claims": result.total_insurance_claims,
                "total_related_hospitals": result.total_related_hospitals
            },
            "warnings": result.warnings,
            "errors": result.errors
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"❌ Error saving result: {str(e)}")


def save_batch_results(results: List[CompleteProcessingResult], filename: str):
    """Save batch results to JSON"""
    try:
        batch_data = {
            "batch_info": {
                "total_processed": len(results),
                "successful_count": len([r for r in results if r.is_successful]),
                "timestamp": datetime.now().isoformat(),
                "version": __version__
            },
            "results": []
        }
        
        for result in results:
            result_summary = {
                "company_tax_code": result.company_tax_code,
                "processing_status": result.processing_status,
                "data_quality_score": result.overall_data_quality_score,
                "processing_duration_ms": result.total_processing_duration_ms,
                "total_employees": result.total_employees,
                "total_contributions": len(result.vss_data.contributions) if result.vss_data else 0,
                "errors": result.errors,
                "warnings": result.warnings
            }
            batch_data["results"].append(result_summary)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"❌ Error saving batch results: {str(e)}")


def create_cli_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description=f"{__title__} - {__description__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single MST
  python main.py --mst 5200958920
  
  # Process multiple MSTs
  python main.py --mst 5200958920 0100109106 --batch
  
  # Process from file
  python main.py --file mst_list.txt --workers 8
  
  # Show version and help
  python main.py --version
        """
    )
    
    parser.add_argument('--version', action='version', version=f'{__title__} {__version__}')
    
    parser.add_argument('--mst', nargs='+', help='MST code(s) to process')
    parser.add_argument('--file', type=str, help='File containing MST codes (one per line)')
    parser.add_argument('--batch', action='store_true', help='Enable batch processing mode')
    parser.add_argument('--workers', type=int, default=4, help='Number of concurrent workers (default: 4)')
    parser.add_argument('--no-save', action='store_true', help='Do not save results to files')
    parser.add_argument('--quiet', action='store_true', help='Reduce output verbosity')
    
    return parser


async def main():
    """Main application entry point"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    # Determine MSTs to process
    msts = []
    if args.mst:
        msts.extend(args.mst)
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_msts = [line.strip() for line in f if line.strip()]
            msts.extend(file_msts)
            print(f"📄 Loaded {len(file_msts)} MSTs from file: {args.file}")
        except Exception as e:
            print(f"❌ Error reading file {args.file}: {str(e)}")
            return 1
    
    if not msts:
        print("❌ No MSTs provided. Use --mst or --file option.")
        parser.print_help()
        return 1
    
    # Remove duplicates while preserving order
    msts = list(dict.fromkeys(msts))
    save_results = not args.no_save
    
    try:
        if len(msts) == 1 and not args.batch:
            # Single MST processing
            await process_single_mst(msts[0], save_results)
        else:
            # Batch processing
            await process_batch(msts, args.workers, save_results)
        
        print(f"\n🎊 Processing completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Processing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Processing failed: {str(e)}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Application error: {str(e)}")
        sys.exit(1)
