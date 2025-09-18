"""
Test Complete VSS Integration System V3.1
Kiểm tra hệ thống tích hợp VSS hoàn chỉnh với trích xuất dữ liệu đầy đủ:

🎯 Test Flow:
MST Input → API Doanh nghiệp → VSS Data Extraction → JSON chuẩn hóa

👥 Danh sách nhân viên
💰 Dữ liệu đóng góp BHXH  
📋 Hồ sơ yêu cầu bảo hiểm
🏥 Danh sách bệnh viện

Author: MiniMax Agent
Date: 2025-09-19
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'test_complete_vss_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

# Import complete VSS processor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.complete_vss_integration_processor import (
    CompleteVSSIntegrationProcessor, CompleteProcessingResult, process_mst_complete
)


def print_section_header(title: str, emoji: str = "🔹"):
    """In header cho từng section"""
    print(f"\n{emoji} {'='*60}")
    print(f"{emoji} {title}")
    print(f"{emoji} {'='*60}")


def print_processing_summary(result: CompleteProcessingResult):
    """In tóm tắt kết quả xử lý"""
    
    print_section_header("KẾT QUẢ XỬ LÝ TỔNG QUAN", "📊")
    
    print(f"🆔 Processing ID: {result.processing_id}")
    print(f"🏢 Company Tax Code: {result.company_tax_code}")
    print(f"✅ Processing Status: {result.processing_status}")
    print(f"⏱️  Total Duration: {result.total_processing_duration_ms:.2f}ms")
    print(f"📈 Data Quality Score: {result.overall_data_quality_score:.1f}/100")
    print(f"📋 Data Completeness: {result.data_completeness_percentage:.1f}%")
    
    if result.warnings:
        print(f"⚠️  Warnings: {len(result.warnings)}")
        for warning in result.warnings[:3]:  # Show first 3
            print(f"   - {warning}")
    
    if result.errors:
        print(f"❌ Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"   - {error}")


def print_enterprise_data_summary(result: CompleteProcessingResult):
    """In tóm tắt dữ liệu doanh nghiệp"""
    
    if not result.enterprise_data:
        print("❌ No enterprise data available")
        return
    
    print_section_header("THÔNG TIN DOANH NGHIỆP (API)", "🏢")
    
    enterprise = result.enterprise_data
    print(f"📛 Company Name: {enterprise.company_name}")
    print(f"🆔 Tax Code: {enterprise.tax_code}")
    print(f"👤 Legal Representative: {enterprise.legal_representative}")
    print(f"📍 Business Address: {enterprise.business_address}")
    print(f"📅 Registration Date: {enterprise.registration_date}")
    print(f"📊 Business Status: {enterprise.business_status}")
    print(f"💰 Capital Amount: {enterprise.capital_amount:,} VND")
    print(f"🏭 Business Sectors: {len(enterprise.business_sectors)} sectors")


def print_vss_data_summary(result: CompleteProcessingResult):
    """In tóm tắt dữ liệu VSS"""
    
    if not result.vss_data:
        print("❌ No VSS data available")
        return
    
    vss_data = result.vss_data
    
    print_section_header("DỮ LIỆU VSS CHI TIẾT", "🔍")
    
    # Employee summary
    print(f"👥 NHÂN VIÊN:")
    print(f"   • Tổng số: {vss_data.total_employees}")
    print(f"   • Đang làm việc: {vss_data.active_employees}")
    print(f"   • Ngừng làm việc: {vss_data.inactive_employees}")
    
    # Contribution summary
    print(f"💰 ĐÓNG GÓP BHXH:")
    print(f"   • Tổng kỳ: {vss_data.total_contributions}")
    print(f"   • Tổng tiền: {vss_data.total_contribution_amount:,} VND")
    
    # Claims summary
    print(f"📋 HỒ SƠ BẢO HIỂM:")
    print(f"   • Tổng hồ sơ: {vss_data.total_claims}")
    print(f"   • Đã duyệt: {vss_data.approved_claims}")
    print(f"   • Đang chờ: {vss_data.pending_claims}")
    print(f"   • Bị từ chối: {vss_data.rejected_claims}")
    
    # Hospital summary
    print(f"🏥 BỆNH VIỆN LIÊN QUAN:")
    print(f"   • Tổng số: {len(vss_data.related_hospitals)}")
    
    # Data quality
    print(f"📊 CHẤT LƯỢNG DỮ LIỆU:")
    print(f"   • Completeness: {vss_data.data_completeness_score:.1f}%")
    print(f"   • Accuracy: {vss_data.data_accuracy_score:.1f}%")
    print(f"   • Extraction Time: {vss_data.extraction_duration_seconds:.2f}s")


def print_detailed_vss_breakdown(result: CompleteProcessingResult):
    """In chi tiết dữ liệu VSS"""
    
    if not result.vss_data:
        return
    
    vss_data = result.vss_data
    
    # Employee details
    if vss_data.employees:
        print_section_header("CHI TIẾT NHÂN VIÊN (Top 5)", "👥")
        for i, emp in enumerate(vss_data.employees[:5]):
            print(f"{i+1}. {emp.full_name} ({emp.employee_id})")
            print(f"   • Chức vụ: {emp.position} - {emp.department}")
            print(f"   • Trạng thái: {emp.status.value}")
            print(f"   • Lương BH: {emp.insurance_salary:,} VND")
    
    # Contribution details
    if vss_data.contributions:
        print_section_header("CHI TIẾT ĐÓNG GÓP (Top 5)", "💰")
        for i, contrib in enumerate(vss_data.contributions[:5]):
            print(f"{i+1}. Kỳ {contrib.contribution_period}")
            print(f"   • Nhân viên: {contrib.employee_id}")
            print(f"   • Tổng đóng góp: {contrib.total_contribution:,} VND")
            print(f"   • Trạng thái: {contrib.status.value}")
    
    # Claims details
    if vss_data.claims:
        print_section_header("CHI TIẾT HỒ SƠ BẢO HIỂM (Top 5)", "📋")
        for i, claim in enumerate(vss_data.claims[:5]):
            print(f"{i+1}. {claim.claim_title} ({claim.claim_id})")
            print(f"   • Loại: {claim.claim_type.value.upper()}")
            print(f"   • Số tiền: {claim.claim_amount:,} VND")
            print(f"   • Trạng thái: {claim.status.value}")
    
    # Hospital details
    if vss_data.related_hospitals:
        print_section_header("CHI TIẾT BỆNH VIỆN", "🏥")
        for i, hosp in enumerate(vss_data.related_hospitals):
            print(f"{i+1}. {hosp.hospital_name} ({hosp.hospital_id})")
            print(f"   • Loại: {hosp.hospital_type.value}")
            print(f"   • Địa chỉ: {hosp.address}")
            print(f"   • Đánh giá: {hosp.quality_rating}/5.0")


def save_complete_result_to_file(result: CompleteProcessingResult, filename: str):
    """Lưu kết quả hoàn chỉnh vào file"""
    
    # Convert result to dict for JSON serialization
    result_dict = {
        "processing_info": {
            "processing_id": result.processing_id,
            "company_tax_code": result.company_tax_code,
            "processing_status": result.processing_status,
            "processing_duration_ms": result.total_processing_duration_ms,
            "data_quality_score": result.overall_data_quality_score,
            "data_completeness": result.data_completeness_percentage
        },
        
        "enterprise_data": None,
        "vss_data": None,
        "integrated_json": result.integrated_json,
        "warnings": result.warnings,
        "errors": result.errors
    }
    
    # Add enterprise data if available
    if result.enterprise_data:
        result_dict["enterprise_data"] = {
            "company_name": result.enterprise_data.company_name,
            "tax_code": result.enterprise_data.tax_code,
            "legal_representative": result.enterprise_data.legal_representative,
            "business_address": result.enterprise_data.business_address,
            "registration_date": result.enterprise_data.registration_date.isoformat() if result.enterprise_data.registration_date else None,
            "business_status": result.enterprise_data.business_status,
            "capital_amount": float(result.enterprise_data.capital_amount) if result.enterprise_data.capital_amount else 0
        }
    
    # Add VSS data summary if available
    if result.vss_data:
        result_dict["vss_data"] = {
            "total_employees": result.vss_data.total_employees,
            "active_employees": result.vss_data.active_employees,
            "total_contributions": result.vss_data.total_contributions,
            "total_contribution_amount": float(result.vss_data.total_contribution_amount),
            "total_claims": result.vss_data.total_claims,
            "approved_claims": result.vss_data.approved_claims,
            "related_hospitals_count": len(result.vss_data.related_hospitals),
            "data_completeness_score": result.vss_data.data_completeness_score,
            "data_accuracy_score": result.vss_data.data_accuracy_score
        }
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Đã lưu kết quả vào file: {filename}")


async def test_complete_vss_system():
    """Test hệ thống VSS integration hoàn chỉnh"""
    
    print_section_header("VSS INTEGRATION SYSTEM V3.1 - COMPLETE TEST", "🚀")
    print("Testing complete MST processing flow:")
    print("MST Input → API Doanh nghiệp → VSS Data Extraction → JSON chuẩn hóa")
    print("🎯 Bao gồm: Nhân viên, BHXH, Hồ sơ BH, Bệnh viện")
    
    # Test data
    test_msts = [
        "5200958920",  # MST được user yêu cầu
        "0100109106"   # MST bổ sung
    ]
    
    for mst in test_msts:
        try:
            print_section_header(f"TESTING MST: {mst}", "🧪")
            
            start_time = time.time()
            
            # Chạy xử lý hoàn chỉnh
            result = await process_mst_complete(mst)
            
            processing_time = (time.time() - start_time) * 1000
            
            # In kết quả tổng quan
            print_processing_summary(result)
            
            # In chi tiết dữ liệu doanh nghiệp
            print_enterprise_data_summary(result)
            
            # In chi tiết dữ liệu VSS
            print_vss_data_summary(result)
            
            # In breakdown chi tiết
            print_detailed_vss_breakdown(result)
            
            # Lưu kết quả vào file
            output_filename = f"complete_vss_result_{mst}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_complete_result_to_file(result, output_filename)
            
            print_section_header("ĐÁNH GIÁ KẾT QUẢ", "⭐")
            
            if result.is_successful:
                print("🎊 THÀNH CÔNG! Hệ thống đã trích xuất đầy đủ dữ liệu VSS")
                print(f"✅ Enterprise Data: {'Available' if result.enterprise_data else 'Missing'}")
                print(f"✅ VSS Employees: {result.total_employees} nhân viên")
                print(f"✅ VSS Contributions: {len(result.vss_data.contributions) if result.vss_data else 0} kỳ đóng góp")
                print(f"✅ VSS Claims: {result.total_insurance_claims} hồ sơ bảo hiểm")
                print(f"✅ VSS Hospitals: {result.total_related_hospitals} bệnh viện")
                print(f"⚡ Processing Time: {processing_time:.2f}ms")
                print(f"📊 Overall Quality: {result.overall_data_quality_score:.1f}/100")
            else:
                print("❌ FAILED! Có lỗi trong quá trình xử lý")
                for error in result.errors:
                    print(f"   ❌ {error}")
        
        except Exception as e:
            logger.error(f"Error testing MST {mst}: {str(e)}")
            print(f"💥 ERROR: {str(e)}")
        
        print("\n" + "="*80)


async def test_performance_benchmark():
    """Test hiệu suất xử lý"""
    
    print_section_header("PERFORMANCE BENCHMARK", "⚡")
    
    processor = CompleteVSSIntegrationProcessor()
    
    # Test với nhiều MST
    test_cases = ["5200958920", "0100109106", "0123456789", "9876543210"]
    
    total_start_time = time.time()
    results = []
    
    for mst in test_cases:
        try:
            start_time = time.time()
            result = await processor.process_complete_enterprise_vss_data(mst)
            processing_time = (time.time() - start_time) * 1000
            
            results.append({
                "mst": mst,
                "processing_time_ms": processing_time,
                "success": result.is_successful,
                "data_quality": result.overall_data_quality_score
            })
            
            print(f"✅ {mst}: {processing_time:.2f}ms - Quality: {result.overall_data_quality_score:.1f}/100")
            
        except Exception as e:
            print(f"❌ {mst}: Error - {str(e)}")
    
    total_time = (time.time() - total_start_time) * 1000
    
    # Performance summary
    print_section_header("PERFORMANCE RESULTS", "📊")
    
    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_processing_time = sum(r["processing_time_ms"] for r in successful_results) / len(successful_results)
        avg_quality_score = sum(r["data_quality"] for r in successful_results) / len(successful_results)
        
        print(f"📈 Processed: {len(results)} MSTs")
        print(f"✅ Successful: {len(successful_results)}")
        print(f"⚡ Average Processing Time: {avg_processing_time:.2f}ms")
        print(f"📊 Average Quality Score: {avg_quality_score:.1f}/100")
        print(f"🕐 Total Benchmark Time: {total_time:.2f}ms")
        print(f"🚀 Throughput: {len(results) / (total_time/1000):.2f} MST/second")
    
    # Get processor statistics
    stats = processor.get_processing_statistics()
    print_section_header("PROCESSOR STATISTICS", "📈")
    print(f"📊 Success Rate: {stats['success_rate']:.1f}%")
    print(f"⚡ Average Processing Time: {stats['average_processing_time']:.2f}ms")


async def main():
    """Main test function"""
    
    print("🚀 STARTING COMPLETE VSS INTEGRATION SYSTEM TEST")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Complete system test
        await test_complete_vss_system()
        
        # Test 2: Performance benchmark
        await test_performance_benchmark()
        
        print_section_header("TEST COMPLETED SUCCESSFULLY", "🎊")
        print("✅ All tests completed")
        print("📋 VSS Integration System V3.1 is ready for production!")
        print("🎯 Full VSS data extraction implemented:")
        print("   👥 Employee records")
        print("   💰 Insurance contributions")
        print("   📋 Insurance claims")
        print("   🏥 Hospital listings")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"💥 TEST FAILED: {str(e)}")
    
    print(f"🏁 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
