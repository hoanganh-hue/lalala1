#!/usr/bin/env python3
"""
Batch processing script for 1000 MSTs with detailed company data export
"""
import sys
import os
import time
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.utils.analytics import get_analytics_engine
from src.utils.performance_monitor import get_performance_monitor
from src.utils.prometheus_metrics import get_metrics_collector
from src.utils.logger import setup_module_logger

# Try to import ML components
try:
    from src.utils.ml_predictions import get_risk_assessment_engine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML predictions not available (scikit-learn not installed)")

# Set up logging
logger = setup_module_logger("batch_processor_detailed")

def load_mst_from_excel(file_path: str, limit: int = 1000) -> list:
    """Load MSTs from Excel file"""
    logger.info(f"Loading MSTs from {file_path}")

    df = pd.read_excel(file_path)
    msts = df['Dãy số 10 chữ số'].astype(str).tolist()

    # Take first 'limit' MSTs
    selected_msts = msts[:limit]
    logger.info(f"Selected {len(selected_msts)} MSTs for processing")

    return selected_msts

def run_batch_processing_detailed(msts: list) -> dict:
    """Run batch processing with detailed company data"""
    logger.info("🚀 Starting detailed batch processing with 1000 MSTs")
    logger.info("📊 Configuration: max_workers=8, use_real_apis=False (mock data for demo)")

    # Initialize components
    processor = VSSIntegrationProcessor(max_workers=8, use_real_apis=False)
    analytics_engine = get_analytics_engine()
    performance_monitor = get_performance_monitor()
    metrics_collector = get_metrics_collector()

    if ML_AVAILABLE:
        risk_engine = get_risk_assessment_engine()
    else:
        risk_engine = None

    # Performance monitoring is already active
    logger.info("📈 Performance monitoring active...")

    # Record start metrics
    start_time = time.time()
    initial_memory = performance_monitor.get_memory_stats()

    logger.info("⚡ Starting batch processing...")

    try:
        # Process batch
        batch_start = time.time()
        results = processor.process_batch(msts)
        batch_time = time.time() - batch_start

        # Calculate metrics
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        success_rate = (successful / len(results)) * 100 if results else 0
        throughput = len(results) / batch_time if batch_time > 0 else 0
        avg_processing_time = sum(r.processing_time for r in results) / len(results) if results else 0

        # Performance metrics
        final_memory = performance_monitor.get_memory_stats()
        memory_increase = final_memory['current'] - initial_memory['current']

        # Analytics
        logger.info("📊 Running analytics...")
        analytics_results = [r.to_dict() for r in results]
        analysis = analytics_engine.analyze_processing_results(analytics_results)

        # Risk assessment for sample results
        if risk_engine:
            logger.info("🎯 Running risk assessment...")
            sample_results = results[:10]  # Assess first 10
            risk_assessments = []
            for result in sample_results:
                risk = risk_engine.assess_risk(result.to_dict())
                risk_assessments.append(risk)
        else:
            risk_assessments = []

        # Update Prometheus metrics
        for result in results:
            metrics_collector.record_request("POST", "/api/v1/process", "200", result.processing_time)
            if result.success:
                metrics_collector.record_compliance_score(result.confidence_score)

        # Create detailed company data
        logger.info("🏢 Creating detailed company data...")
        detailed_results = []
        for i, result in enumerate(results):
            result_dict = result.to_dict()

            # Add MST index for reference
            result_dict['mst_index'] = i + 1
            result_dict['batch_timestamp'] = datetime.now().isoformat()

            detailed_results.append(result_dict)

        # Compile final results with detailed data
        processing_results = {
            'summary': {
                'total_processed': len(results),
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'total_time': batch_time,
                'throughput': throughput,
                'avg_processing_time': avg_processing_time
            },
            'performance': {
                'initial_memory_mb': initial_memory['current'] / (1024*1024),
                'final_memory_mb': final_memory['current'] / (1024*1024),
                'memory_increase_mb': memory_increase / (1024*1024),
                'cpu_stats': performance_monitor.get_cpu_stats(),
                'gc_stats': performance_monitor.get_gc_stats()
            },
            'analytics': analysis,
            'risk_assessment': {
                'sample_size': len(risk_assessments),
                'assessments': risk_assessments,
                'ml_available': ML_AVAILABLE
            },
            'results': detailed_results,  # Add detailed results
            'system_info': {
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'platform': sys.platform
            }
        }

        # Log results
        logger.info("✅ Batch processing completed!")
        logger.info(f"📈 Results: {successful}/{len(results)} successful ({success_rate:.1f}%)")
        logger.info(f"⚡ Throughput: {throughput:.2f} req/s")
        logger.info(f"⏱️  Avg processing time: {avg_processing_time:.3f}s")
        logger.info(f"🧠 Memory increase: {memory_increase/(1024*1024):.1f} MB")
        logger.info(f"📋 Detailed results: {len(detailed_results)} company records")

        return processing_results

    except Exception as e:
        logger.error(f"❌ Batch processing failed: {e}")
        raise

def save_detailed_results(results: dict, output_file: str):
    """Save detailed results to JSON file"""
    logger.info(f"💾 Saving detailed results to {output_file}")

    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Detailed results saved to {output_file}")

def export_detailed_to_excel(data: Dict[str, Any], excel_file: str):
    """Export detailed results to Excel with company data"""
    logger.info(f"📊 Exporting detailed results to Excel: {excel_file}")

    # Create output directory if needed
    Path(excel_file).parent.mkdir(parents=True, exist_ok=True)

    # Create Excel writer
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:

        # Sheet 1: Summary
        summary_data = {
            'Metric': [
                'Tổng số MST đã xử lý',
                'Số MST thành công',
                'Số MST thất bại',
                'Tỷ lệ thành công (%)',
                'Tổng thời gian xử lý (giây)',
                'Thông lượng (MST/giây)',
                'Thời gian xử lý trung bình (giây)',
                'Trạng thái xử lý'
            ],
            'Value': [
                data['summary']['total_processed'],
                data['summary']['successful'],
                data['summary']['failed'],
                f"{data['summary']['success_rate']:.2f}",
                f"{data['summary']['total_time']:.3f}",
                f"{data['summary']['throughput']:.2f}",
                f"{data['summary']['avg_processing_time']:.4f}",
                'HOÀN THÀNH' if data['summary']['success_rate'] == 100.0 else 'CÓ LỖI'
            ],
            'Unit': [
                'MST', 'MST', 'MST', '%', 'giây', 'MST/s', 'giây', ''
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Tóm tắt', index=False)

        # Sheet 2: Detailed Company Data
        if 'results' in data and data['results']:
            logger.info(f"📋 Creating company data sheet with {len(data['results'])} records")

            # Flatten the results for Excel
            company_records = []
            for result in data['results']:
                record = {
                    'STT': result.get('mst_index', ''),
                    'MST': result.get('mst', ''),
                    'Thành công': 'Có' if result.get('success', False) else 'Không',
                    'Thời gian xử lý (giây)': f"{result.get('processing_time', 0):.4f}",
                    'Điểm tin cậy': f"{result.get('confidence_score', 0):.2f}",
                    'Chất lượng dữ liệu': result.get('data_quality', ''),
                    'Nguồn': result.get('source', ''),
                    'Timestamp': result.get('timestamp', ''),
                    'Lỗi': result.get('error', ''),
                    'Retry count': result.get('retry_count', 0)
                }
                company_records.append(record)

            company_df = pd.DataFrame(company_records)
            company_df.to_excel(writer, sheet_name='Dữ liệu công ty', index=False)

        # Sheet 3: Performance
        performance = data.get('performance', {})
        performance_data = {
            'Metric': [
                'Bộ nhớ ban đầu',
                'Bộ nhớ cuối cùng',
                'Tăng bộ nhớ',
                'CPU trung bình (%)'
            ],
            'Value': [
                f"{performance.get('initial_memory_mb', 0):.1f}",
                f"{performance.get('final_memory_mb', 0):.1f}",
                f"{performance.get('memory_increase_mb', 0):.1f}",
                f"{performance.get('cpu_stats', {}).get('avg', 0):.1f}"
            ],
            'Unit': [
                'MB', 'MB', 'MB', '%'
            ]
        }
        performance_df = pd.DataFrame(performance_data)
        performance_df.to_excel(writer, sheet_name='Hiệu suất', index=False)

        # Sheet 4: Analytics
        analytics = data.get('analytics', {})
        analytics_data = {
            'Category': ['TUÂN THỦ', 'CHẤT LƯỢNG', 'HIỆU SUẤT'],
            'Metric': [
                'Điểm tuân thủ tổng thể',
                'Điểm chất lượng trung bình',
                'Thời gian xử lý trung bình'
            ],
            'Value': [
                f"{analytics.get('compliance', {}).get('compliance_score', 0):.2f}",
                f"{analytics.get('quality', {}).get('avg_quality_score', 0):.2f}",
                f"{analytics.get('performance', {}).get('avg_response_time', 0):.4f}"
            ],
            'Status': [
                analytics.get('compliance', {}).get('risk_level', 'UNKNOWN'),
                'GOOD' if analytics.get('quality', {}).get('avg_quality_score', 0) > 0.8 else 'NEEDS_IMPROVEMENT',
                'FAST' if analytics.get('performance', {}).get('avg_response_time', 0) < 1.0 else 'NORMAL'
            ]
        }
        analytics_df = pd.DataFrame(analytics_data)
        analytics_df.to_excel(writer, sheet_name='Phân tích', index=False)

        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Max width 50
                worksheet.column_dimensions[column_letter].width = adjusted_width

    logger.info(f"✅ Detailed Excel export completed: {excel_file}")

def main():
    """Main execution function"""
    print("🚀 VSS Integration System - Detailed Batch Processing 1000 MSTs")
    print("📊 Including detailed company data export")

    # Configuration
    excel_file = "data/input/sample_mst_input.xlsx"
    json_output = f"reports/detailed_batch_results_1000_mst_{int(time.time())}.json"
    excel_output = "data/output/vss_detailed_batch_results_1000_mst.xlsx"
    mst_limit = 1000

    try:
        # Load MSTs from Excel
        msts = load_mst_from_excel(excel_file, mst_limit)

        # Run detailed batch processing
        results = run_batch_processing_detailed(msts)

        # Save detailed JSON results
        save_detailed_results(results, json_output)

        # Export detailed Excel
        export_detailed_to_excel(results, excel_output)

        print("✅ Detailed batch processing completed successfully!")
        print(f"📄 JSON results: {json_output}")
        print(f"📊 Excel export: {excel_output}")

        # Show summary
        summary = results.get('summary', {})
        print("\n📊 Batch Summary:")
        print(f"   Processed: {summary.get('total_processed', 0)} MSTs")
        print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"   Throughput: {summary.get('throughput', 0):.2f} MST/s")
        print(f"   Detailed Records: {len(results.get('results', []))} company entries")

    except Exception as e:
        logger.error(f"Detailed batch processing failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()