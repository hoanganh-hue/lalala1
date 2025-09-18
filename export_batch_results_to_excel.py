#!/usr/bin/env python3
"""
Export batch processing results to standardized Excel format
"""
import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.logger import setup_module_logger

# Set up logging
logger = setup_module_logger("excel_exporter")

def load_batch_results(json_file: str) -> Dict[str, Any]:
    """Load batch processing results from JSON file"""
    logger.info(f"Loading results from {json_file}")

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logger.info("Results loaded successfully")
    return data

def create_summary_sheet(data: Dict[str, Any]) -> pd.DataFrame:
    """Create summary statistics sheet"""
    summary = data.get('summary', {})

    # Create summary DataFrame
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
            summary.get('total_processed', 0),
            summary.get('successful', 0),
            summary.get('failed', 0),
            f"{summary.get('success_rate', 0):.2f}",
            f"{summary.get('total_time', 0):.3f}",
            f"{summary.get('throughput', 0):.2f}",
            f"{summary.get('avg_processing_time', 0):.4f}",
            'HOÀN THÀNH' if summary.get('success_rate', 0) == 100.0 else 'CÓ LỖI'
        ],
        'Unit': [
            'MST', 'MST', 'MST', '%', 'giây', 'MST/s', 'giây', ''
        ]
    }

    return pd.DataFrame(summary_data)

def create_performance_sheet(data: Dict[str, Any]) -> pd.DataFrame:
    """Create performance metrics sheet"""
    performance = data.get('performance', {})

    performance_data = {
        'Metric': [
            'Bộ nhớ ban đầu',
            'Bộ nhớ cuối cùng',
            'Tăng bộ nhớ',
            'CPU trung bình (%)',
            'GC Collections',
            'GC Time (giây)',
            'Thread Count',
            'Process ID'
        ],
        'Value': [
            f"{performance.get('initial_memory_mb', 0):.1f}",
            f"{performance.get('final_memory_mb', 0):.1f}",
            f"{performance.get('memory_increase_mb', 0):.1f}",
            f"{performance.get('cpu_stats', {}).get('avg', 0):.1f}",
            performance.get('gc_stats', {}).get('collections', 0),
            f"{performance.get('gc_stats', {}).get('time', 0):.4f}",
            performance.get('cpu_stats', {}).get('threads', 0),
            performance.get('cpu_stats', {}).get('pid', 0)
        ],
        'Unit': [
            'MB', 'MB', 'MB', '%', 'lần', 'giây', 'threads', 'PID'
        ]
    }

    return pd.DataFrame(performance_data)

def create_analytics_sheet(data: Dict[str, Any]) -> pd.DataFrame:
    """Create analytics results sheet"""
    analytics = data.get('analytics', {})

    analytics_data = {
        'Category': [],
        'Metric': [],
        'Value': [],
        'Description': []
    }

    # Summary metrics
    summary = analytics.get('summary', {})
    analytics_data['Category'].extend(['TÓM TẮT'] * 4)
    analytics_data['Metric'].extend([
        'Tổng số yêu cầu',
        'Thành công',
        'Thất bại',
        'Tỷ lệ thành công'
    ])
    analytics_data['Value'].extend([
        summary.get('total_requests', 0),
        summary.get('successful_requests', 0),
        summary.get('failed_requests', 0),
        f"{summary.get('success_rate', 0):.2f}%"
    ])
    analytics_data['Description'].extend([
        'Tổng số API requests',
        'Số requests thành công',
        'Số requests thất bại',
        'Tỷ lệ thành công tổng thể'
    ])

    # Performance metrics
    performance = analytics.get('performance', {})
    analytics_data['Category'].extend(['HIỆU SUẤT'] * 3)
    analytics_data['Metric'].extend([
        'Thời gian xử lý trung bình',
        'Thời gian xử lý tối đa',
        'Thời gian xử lý tối thiểu'
    ])
    analytics_data['Value'].extend([
        f"{performance.get('avg_response_time', 0):.4f}s",
        f"{performance.get('max_response_time', 0):.4f}s",
        f"{performance.get('min_response_time', 0):.4f}s"
    ])
    analytics_data['Description'].extend([
        'Thời gian xử lý trung bình',
        'Thời gian xử lý chậm nhất',
        'Thời gian xử lý nhanh nhất'
    ])

    # Quality metrics
    quality = analytics.get('quality', {})
    analytics_data['Category'].extend(['CHẤT LƯỢNG'] * 3)
    analytics_data['Metric'].extend([
        'Điểm chất lượng trung bình',
        'Tỷ lệ dữ liệu cao',
        'Tỷ lệ dữ liệu trung bình'
    ])
    analytics_data['Value'].extend([
        f"{quality.get('avg_quality_score', 0):.2f}",
        f"{quality.get('high_quality_rate', 0):.1f}%",
        f"{quality.get('medium_quality_rate', 0):.1f}%"
    ])
    analytics_data['Description'].extend([
        'Điểm chất lượng dữ liệu (0-1)',
        'Tỷ lệ dữ liệu chất lượng cao',
        'Tỷ lệ dữ liệu chất lượng trung bình'
    ])

    # Compliance metrics
    compliance = analytics.get('compliance', {})
    analytics_data['Category'].extend(['TUÂN THỦ'] * 4)
    analytics_data['Metric'].extend([
        'Điểm tuân thủ',
        'Độ tin cậy trung bình',
        'Mức độ rủi ro',
        'Khuyến nghị'
    ])
    analytics_data['Value'].extend([
        f"{compliance.get('compliance_score', 0):.2f}",
        f"{compliance.get('average_confidence', 0):.2f}",
        compliance.get('risk_level', 'UNKNOWN'),
        f"{len(analytics.get('recommendations', []))} items"
    ])
    analytics_data['Description'].extend([
        'Điểm tuân thủ tổng thể (0-1)',
        'Độ tin cậy trung bình',
        'Mức độ rủi ro hiện tại',
        'Số khuyến nghị cải thiện'
    ])

    return pd.DataFrame(analytics_data)

def create_risk_assessment_sheet(data: Dict[str, Any]) -> pd.DataFrame:
    """Create risk assessment sheet"""
    risk = data.get('risk_assessment', {})

    if risk.get('sample_size', 0) == 0:
        # No risk assessment data
        risk_data = {
            'MST': ['N/A'],
            'Predicted_Compliance_Score': [0.0],
            'Risk_Level': ['UNKNOWN'],
            'Prediction_Confidence': [0.0],
            'Risk_Factors': ['ML_NOT_AVAILABLE'],
            'Recommendations': ['Cài đặt scikit-learn để có đánh giá rủi ro']
        }
    else:
        # Risk assessment data available
        assessments = risk.get('assessments', [])
        risk_data = {
            'MST': [f"MST_{i+1}" for i in range(len(assessments))],
            'Predicted_Compliance_Score': [a.get('predicted_compliance_score', 0) for a in assessments],
            'Risk_Level': [a.get('risk_level', 'UNKNOWN') for a in assessments],
            'Prediction_Confidence': [a.get('prediction_confidence', 0) for a in assessments],
            'Risk_Factors': [', '.join(a.get('risk_factors', [])) for a in assessments],
            'Recommendations': [', '.join(a.get('recommendations', [])) for a in assessments]
        }

    return pd.DataFrame(risk_data)

def create_system_info_sheet(data: Dict[str, Any]) -> pd.DataFrame:
    """Create system information sheet"""
    system = data.get('system_info', {})

    system_data = {
        'Property': [
            'Timestamp',
            'Python Version',
            'Platform',
            'Architecture',
            'Machine',
            'Processor',
            'Batch Size',
            'Workers Used',
            'ML Available'
        ],
        'Value': [
            system.get('timestamp', 'N/A'),
            system.get('python_version', 'N/A'),
            system.get('platform', 'N/A'),
            '64-bit' if sys.maxsize > 2**32 else '32-bit',
            'Unknown',  # Would need platform module
            'Unknown',  # Would need platform module
            data.get('summary', {}).get('total_processed', 0),
            8,  # From batch script configuration
            data.get('risk_assessment', {}).get('ml_available', False)
        ]
    }

    return pd.DataFrame(system_data)

def export_to_excel(data: Dict[str, Any], output_file: str):
    """Export all data to Excel with multiple sheets"""
    logger.info(f"Exporting results to Excel: {output_file}")

    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

        # Sheet 1: Summary
        summary_df = create_summary_sheet(data)
        summary_df.to_excel(writer, sheet_name='Tóm tắt', index=False)

        # Sheet 2: Performance
        performance_df = create_performance_sheet(data)
        performance_df.to_excel(writer, sheet_name='Hiệu suất', index=False)

        # Sheet 3: Analytics
        analytics_df = create_analytics_sheet(data)
        analytics_df.to_excel(writer, sheet_name='Phân tích', index=False)

        # Sheet 4: Risk Assessment
        risk_df = create_risk_assessment_sheet(data)
        risk_df.to_excel(writer, sheet_name='Đánh giá rủi ro', index=False)

        # Sheet 5: System Info
        system_df = create_system_info_sheet(data)
        system_df.to_excel(writer, sheet_name='Thông tin hệ thống', index=False)

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

    logger.info(f"✅ Excel export completed: {output_file}")

def main():
    """Main execution function"""
    print("📊 Exporting VSS Integration Batch Results to Excel")

    # Configuration
    json_file = "reports/batch_results_1000_mst_1757917325.json"
    excel_file = "data/output/vss_batch_results_1000_mst.xlsx"

    try:
        # Load data
        data = load_batch_results(json_file)

        # Export to Excel
        export_to_excel(data, excel_file)

        print("✅ Export completed successfully!")
        print(f"📄 Excel file saved to: {excel_file}")

        # Show summary
        summary = data.get('summary', {})
        print("\n📊 Batch Summary:")
        print(f"   Processed: {summary.get('total_processed', 0)} MSTs")
        print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"   Throughput: {summary.get('throughput', 0):.2f} MST/s")
        print(f"   Total Time: {summary.get('total_time', 0):.2f}s")

    except Exception as e:
        logger.error(f"Export failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()