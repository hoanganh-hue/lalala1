"""
Complete VSS Integration Processor V3.1 - With Full VSS Data Extraction
Hệ thống tích hợp VSS hoàn chỉnh với trích xuất dữ liệu đầy đủ

🎯 Luồng xử lý hoàn chỉnh:
1. MST Input → Validate MST format
2. API Doanh nghiệp → Get basic company info  
3. VSS Data Extraction → Extract detailed VSS data:
   👥 Danh sách nhân viên
   💰 Dữ liệu đóng góp BHXH  
   📋 Hồ sơ yêu cầu bảo hiểm
   🏥 Danh sách bệnh viện
4. Data Processing → Standardize and validate
5. JSON chuẩn hóa → Final structured output

Author: MiniMax Agent  
Date: 2025-09-19
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

# Import existing enhanced modules
from ..core.enhanced_data_models import (
    ComprehensiveEnterpriseData, ProcessingResultV3, DataQuality
)
from ..core.enhanced_data_validator import EnhancedDataValidator, ValidationResult
from ..api.enhanced_realtime_client import (
    EnhancedRealTimeAPIClient, ProcessingPriority, create_enhanced_realtime_client
)

# Import new VSS modules
from ..core.vss_data_models import (
    VSSDataSummary, VSSExtractionResult, EmployeeRecord, 
    InsuranceContribution, InsuranceClaim, Hospital
)
from ..api.vss_data_extractor import (
    VSSDataExtractor, ExtractionConfig, create_vss_extractor
)


@dataclass
class CompleteProcessingResult:
    """Kết quả xử lý hoàn chỉnh bao gồm cả dữ liệu doanh nghiệp và VSS"""
    
    # Thông tin cơ bản
    processing_id: str
    company_tax_code: str
    processing_status: str = "success"
    
    # Dữ liệu doanh nghiệp (từ API Doanh nghiệp)
    enterprise_data: Optional[ComprehensiveEnterpriseData] = None
    enterprise_processing_result: Optional[ProcessingResultV3] = None
    
    # Dữ liệu VSS (từ hệ thống VSS)
    vss_data: Optional[VSSDataSummary] = None
    vss_extraction_result: Optional[VSSExtractionResult] = None
    
    # Dữ liệu tích hợp
    integrated_json: Dict[str, Any] = field(default_factory=dict)
    
    # Thống kê tổng hợp
    total_employees: int = 0
    total_contribution_amount: float = 0.0
    total_insurance_claims: int = 0
    total_related_hospitals: int = 0
    
    # Chất lượng dữ liệu
    overall_data_quality_score: float = 0.0
    data_completeness_percentage: float = 0.0
    
    # Metadata
    processing_start_time: datetime = field(default_factory=datetime.now)
    processing_end_time: Optional[datetime] = None
    total_processing_duration_ms: float = 0.0
    
    # Warnings và Errors
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def is_successful(self) -> bool:
        """Kiểm tra xử lý có thành công không"""
        return self.processing_status == "success" and len(self.errors) == 0


class CompleteVSSIntegrationProcessor:
    """
    Bộ xử lý tích hợp VSS hoàn chỉnh 
    Kết hợp dữ liệu từ API Doanh nghiệp và hệ thống VSS
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhanced components
        self.data_validator = EnhancedDataValidator()
        self.api_client = create_enhanced_realtime_client()
        
        # Initialize VSS components  
        self.vss_extractor = create_vss_extractor()
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'average_processing_time': 0.0
        }
    
    async def process_complete_enterprise_vss_data(self, company_tax_code: str) -> CompleteProcessingResult:
        """
        Xử lý hoàn chỉnh dữ liệu doanh nghiệp + VSS
        
        Flow: MST → API Doanh nghiệp → VSS Processing → JSON chuẩn hóa
        
        Args:
            company_tax_code: Mã số thuế doanh nghiệp
            
        Returns:
            CompleteProcessingResult: Kết quả xử lý hoàn chỉnh
        """
        start_time = time.time()
        processing_id = f"COMPLETE_{company_tax_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"🚀 BẮT ĐẦU XỬ LÝ HOÀN CHỈNH CHO MST: {company_tax_code}")
        
        result = CompleteProcessingResult(
            processing_id=processing_id,
            company_tax_code=company_tax_code,
            processing_start_time=datetime.now()
        )
        
        try:
            # BƯỚC 1: Validate MST format
            self.logger.info("📋 BƯỚC 1: Validating MST format...")
            if not self._validate_mst_format(company_tax_code):
                result.processing_status = "failed"
                result.errors.append("Invalid MST format")
                return result
            
            # BƯỚC 2: Parallel processing - API Doanh nghiệp và VSS
            self.logger.info("⚡ BƯỚC 2: Parallel data extraction...")
            
            # Tạo tasks cho xử lý song song
            enterprise_task = self._process_enterprise_data(company_tax_code)
            vss_task = self._process_vss_data(company_tax_code)
            
            # Chạy song song
            enterprise_result, vss_result = await asyncio.gather(
                enterprise_task, vss_task, return_exceptions=True
            )
            
            # Xử lý kết quả enterprise
            if isinstance(enterprise_result, Exception):
                result.errors.append(f"Enterprise processing failed: {str(enterprise_result)}")
                self.logger.error(f"❌ Enterprise processing error: {str(enterprise_result)}")
            else:
                result.enterprise_data = enterprise_result.get('enterprise_data')
                result.enterprise_processing_result = enterprise_result.get('processing_result')
                self.logger.info("✅ Enterprise data processed successfully")
            
            # Xử lý kết quả VSS
            if isinstance(vss_result, Exception):
                result.errors.append(f"VSS processing failed: {str(vss_result)}")
                self.logger.error(f"❌ VSS processing error: {str(vss_result)}")
            else:
                result.vss_data = vss_result.vss_data
                result.vss_extraction_result = vss_result
                self.logger.info("✅ VSS data extracted successfully")
            
            # BƯỚC 3: Data Integration và Standardization
            self.logger.info("🔄 BƯỚC 3: Data integration and standardization...")
            result.integrated_json = self._create_integrated_json(result)
            
            # BƯỚC 4: Quality Assessment
            self.logger.info("📊 BƯỚC 4: Data quality assessment...")
            self._calculate_quality_metrics(result)
            
            # BƯỚC 5: Finalization
            self.logger.info("🎯 BƯỚC 5: Process finalization...")
            result.processing_end_time = datetime.now()
            result.total_processing_duration_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self._update_processing_stats(result)
            
            self.logger.info(f"🎊 HOÀN THÀNH XỬ LÝ TOÀN DIỆN CHO MST: {company_tax_code} "
                           f"trong {result.total_processing_duration_ms:.2f}ms")
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 CRITICAL ERROR cho MST {company_tax_code}: {str(e)}")
            result.processing_status = "failed"
            result.errors.append(f"Critical processing error: {str(e)}")
            result.processing_end_time = datetime.now()
            result.total_processing_duration_ms = (time.time() - start_time) * 1000
            return result
    
    async def _process_enterprise_data(self, tax_code: str) -> Dict[str, Any]:
        """Xử lý dữ liệu từ API Doanh nghiệp"""
        self.logger.info(f"🏢 Processing enterprise data for MST: {tax_code}")
        
        try:
            # Sử dụng enhanced real-time client
            enterprise_data = await self.api_client.get_comprehensive_enterprise_data(
                tax_code, priority=ProcessingPriority.HIGH
            )
            
            # Validate dữ liệu
            validation_result = self.data_validator.validate_comprehensive_data(enterprise_data)
            
            # Tạo processing result
            processing_result = ProcessingResultV3(
                company_tax_code=tax_code,
                enterprise_data=enterprise_data,
                validation_result=validation_result,
                processing_status="completed"
            )
            
            return {
                'enterprise_data': enterprise_data,
                'processing_result': processing_result
            }
            
        except Exception as e:
            self.logger.error(f"Enterprise processing error for {tax_code}: {str(e)}")
            raise e
    
    async def _process_vss_data(self, tax_code: str) -> VSSExtractionResult:
        """Xử lý dữ liệu từ hệ thống VSS"""
        self.logger.info(f"🔍 Processing VSS data for MST: {tax_code}")
        
        try:
            # Trích xuất dữ liệu VSS hoàn chỉnh
            vss_result = await self.vss_extractor.extract_complete_vss_data(tax_code)
            
            return vss_result
            
        except Exception as e:
            self.logger.error(f"VSS processing error for {tax_code}: {str(e)}")
            raise e
    
    def _create_integrated_json(self, result: CompleteProcessingResult) -> Dict[str, Any]:
        """Tạo JSON tích hợp từ dữ liệu doanh nghiệp và VSS"""
        
        integrated_data = {
            "processing_info": {
                "processing_id": result.processing_id,
                "company_tax_code": result.company_tax_code,
                "processing_timestamp": result.processing_start_time.isoformat(),
                "data_sources": ["enterprise_api", "vss_system"]
            },
            
            "enterprise_basic_info": {},
            "vss_detailed_data": {},
            "summary_statistics": {},
            "data_quality_metrics": {}
        }
        
        # Tích hợp dữ liệu doanh nghiệp
        if result.enterprise_data:
            integrated_data["enterprise_basic_info"] = {
                "company_name": result.enterprise_data.company_name,
                "tax_code": result.enterprise_data.tax_code,
                "legal_representative": result.enterprise_data.legal_representative,
                "business_address": result.enterprise_data.business_address,
                "business_sectors": result.enterprise_data.business_sectors,
                "registration_date": result.enterprise_data.registration_date.isoformat() if result.enterprise_data.registration_date else None,
                "business_status": result.enterprise_data.business_status,
                "capital_amount": float(result.enterprise_data.capital_amount) if result.enterprise_data.capital_amount else 0
            }
        
        # Tích hợp dữ liệu VSS chi tiết
        if result.vss_data:
            # Employees section
            integrated_data["vss_detailed_data"]["employees"] = {
                "total_count": len(result.vss_data.employees),
                "active_count": result.vss_data.active_employees,
                "inactive_count": result.vss_data.inactive_employees,
                "employee_list": [
                    {
                        "employee_id": emp.employee_id,
                        "full_name": emp.full_name,
                        "citizen_id": emp.citizen_id,
                        "position": emp.position,
                        "department": emp.department,
                        "status": emp.status.value,
                        "hire_date": emp.hire_date.isoformat(),
                        "insurance_salary": float(emp.insurance_salary)
                    } for emp in result.vss_data.employees
                ]
            }
            
            # Contributions section  
            integrated_data["vss_detailed_data"]["insurance_contributions"] = {
                "total_periods": len(result.vss_data.contributions),
                "total_amount": float(result.vss_data.total_contribution_amount),
                "contribution_list": [
                    {
                        "period": contrib.contribution_period,
                        "employee_id": contrib.employee_id,
                        "total_contribution": float(contrib.total_contribution),
                        "employee_amount": float(contrib.total_employee_contribution),
                        "employer_amount": float(contrib.total_employer_contribution),
                        "status": contrib.status.value,
                        "payment_date": contrib.payment_date.isoformat() if contrib.payment_date else None
                    } for contrib in result.vss_data.contributions
                ]
            }
            
            # Claims section
            integrated_data["vss_detailed_data"]["insurance_claims"] = {
                "total_claims": len(result.vss_data.claims),
                "approved_claims": result.vss_data.approved_claims,
                "pending_claims": result.vss_data.pending_claims,
                "rejected_claims": result.vss_data.rejected_claims,
                "claims_list": [
                    {
                        "claim_id": claim.claim_id,
                        "employee_id": claim.employee_id,
                        "claim_type": claim.claim_type.value,
                        "claim_title": claim.claim_title,
                        "claim_amount": float(claim.claim_amount),
                        "status": claim.status.value,
                        "submission_date": claim.submission_date.isoformat(),
                        "approved_amount": float(claim.approved_amount) if claim.approved_amount else None
                    } for claim in result.vss_data.claims
                ]
            }
            
            # Hospitals section
            integrated_data["vss_detailed_data"]["related_hospitals"] = {
                "total_hospitals": len(result.vss_data.related_hospitals),
                "hospital_list": [
                    {
                        "hospital_id": hosp.hospital_id,
                        "hospital_name": hosp.hospital_name,
                        "hospital_type": hosp.hospital_type.value,
                        "address": hosp.address,
                        "specialties": hosp.specialties,
                        "accepts_bhyt": hosp.accepts_bhyt,
                        "quality_rating": hosp.quality_rating
                    } for hosp in result.vss_data.related_hospitals
                ]
            }
        
        return integrated_data
    
    def _calculate_quality_metrics(self, result: CompleteProcessingResult):
        """Tính toán các metrics chất lượng dữ liệu"""
        
        completeness_score = 0.0
        quality_score = 0.0
        
        # Tính điểm hoàn thiện dữ liệu
        total_sections = 4  # enterprise, employees, contributions, claims, hospitals
        completed_sections = 0
        
        if result.enterprise_data:
            completed_sections += 1
        if result.vss_data:
            if result.vss_data.employees:
                completed_sections += 1
            if result.vss_data.contributions:
                completed_sections += 1
            if result.vss_data.claims:
                completed_sections += 1
            # Hospital section is optional, không tính vào required
        
        result.data_completeness_percentage = (completed_sections / total_sections) * 100
        
        # Tính điểm chất lượng tổng thể
        quality_scores = []
        
        if result.enterprise_processing_result and result.enterprise_processing_result.validation_result:
            quality_scores.append(result.enterprise_processing_result.validation_result.overall_score)
        
        if result.vss_data:
            quality_scores.append(result.vss_data.data_accuracy_score)
            quality_scores.append(result.vss_data.data_completeness_score)
        
        result.overall_data_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Tính thống kê tổng hợp
        if result.vss_data:
            result.total_employees = len(result.vss_data.employees)
            result.total_contribution_amount = float(result.vss_data.total_contribution_amount)
            result.total_insurance_claims = len(result.vss_data.claims)
            result.total_related_hospitals = len(result.vss_data.related_hospitals)
    
    def _validate_mst_format(self, mst: str) -> bool:
        """Validate định dạng MST Việt Nam"""
        if not mst or len(mst) != 10:
            return False
        if not mst.isdigit():
            return False
        return True
    
    def _update_processing_stats(self, result: CompleteProcessingResult):
        """Cập nhật thống kê xử lý"""
        self.processing_stats['total_processed'] += 1
        
        if result.is_successful:
            self.processing_stats['successful_processed'] += 1
        else:
            self.processing_stats['failed_processed'] += 1
        
        # Cập nhật thời gian xử lý trung bình
        current_avg = self.processing_stats['average_processing_time']
        new_time = result.total_processing_duration_ms
        total_count = self.processing_stats['total_processed']
        
        self.processing_stats['average_processing_time'] = (
            (current_avg * (total_count - 1) + new_time) / total_count
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê xử lý"""
        return {
            **self.processing_stats,
            "success_rate": (
                self.processing_stats['successful_processed'] / 
                self.processing_stats['total_processed'] * 100
            ) if self.processing_stats['total_processed'] > 0 else 0
        }


# Factory function
def create_complete_vss_processor() -> CompleteVSSIntegrationProcessor:
    """Tạo Complete VSS Integration Processor"""
    return CompleteVSSIntegrationProcessor()


# Quick processing function  
async def process_mst_complete(company_tax_code: str) -> CompleteProcessingResult:
    """
    Hàm xử lý nhanh MST với dữ liệu hoàn chỉnh
    
    Args:
        company_tax_code: Mã số thuế
        
    Returns:
        CompleteProcessingResult: Kết quả xử lý hoàn chỉnh
    """
    processor = create_complete_vss_processor()
    return await processor.process_complete_enterprise_vss_data(company_tax_code)
