"""
VSS Data Models V3.0 - Comprehensive Social Security Data Structure
Định nghĩa toàn diện cấu trúc dữ liệu Bảo hiểm Xã hội Việt Nam

🎯 Bao gồm 4 loại dữ liệu chính:
👥 Danh sách nhân viên
💰 Dữ liệu đóng góp BHXH
📋 Hồ sơ yêu cầu bảo hiểm
🏥 Danh sách bệnh viện

Author: MiniMax Agent
Date: 2025-09-19
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from decimal import Decimal


class EmployeeStatus(str, Enum):
    """Trạng thái nhân viên"""
    ACTIVE = "active"                    # Đang làm việc
    INACTIVE = "inactive"                # Ngừng làm việc
    SUSPENDED = "suspended"              # Tạm ngừng
    TERMINATED = "terminated"            # Chấm dứt hợp đồng
    MATERNITY_LEAVE = "maternity_leave"  # Nghỉ thai sản
    SICK_LEAVE = "sick_leave"           # Nghỉ ốm dài hạn


class InsuranceType(str, Enum):
    """Loại bảo hiểm"""
    BHXH = "bhxh"                       # Bảo hiểm xã hội
    BHYT = "bhyt"                       # Bảo hiểm y tế
    BHTN = "bhtn"                       # Bảo hiểm thất nghiệp
    BHTNNLĐ = "bhtnnld"                 # Bảo hiểm tai nạn nghề nghiệp


class ContributionStatus(str, Enum):
    """Trạng thái đóng góp"""
    PAID = "paid"                       # Đã đóng
    PENDING = "pending"                 # Đang chờ
    OVERDUE = "overdue"                 # Quá hạn
    EXEMPTED = "exempted"               # Được miễn
    DISPUTED = "disputed"               # Đang tranh chấp


class ClaimStatus(str, Enum):
    """Trạng thái hồ sơ yêu cầu"""
    SUBMITTED = "submitted"             # Đã nộp
    UNDER_REVIEW = "under_review"       # Đang xem xét
    APPROVED = "approved"               # Đã duyệt
    REJECTED = "rejected"               # Bị từ chối
    REQUIRES_ADDITIONAL_INFO = "requires_additional_info"  # Cần bổ sung


class HospitalType(str, Enum):
    """Loại bệnh viện"""
    PUBLIC = "public"                   # Công lập
    PRIVATE = "private"                 # Tư nhân
    SPECIALIST = "specialist"           # Chuyên khoa
    GENERAL = "general"                 # Đa khoa
    TRADITIONAL = "traditional"         # Y học cổ truyền


class EmployeeRecord(BaseModel):
    """Thông tin chi tiết nhân viên trong hệ thống VSS"""
    
    # Thông tin cơ bản
    employee_id: str = Field(..., description="Mã nhân viên")
    full_name: str = Field(..., description="Họ và tên")
    citizen_id: str = Field(..., description="Số CMND/CCCD")
    date_of_birth: date = Field(..., description="Ngày sinh")
    gender: str = Field(..., description="Giới tính")
    
    # Thông tin liên hệ
    address: str = Field(..., description="Địa chỉ thường trú")
    phone_number: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    
    # Thông tin công việc
    position: str = Field(..., description="Chức vụ")
    department: str = Field(..., description="Phòng ban")
    hire_date: date = Field(..., description="Ngày bắt đầu làm việc")
    termination_date: Optional[date] = Field(None, description="Ngày nghỉ việc")
    status: EmployeeStatus = Field(..., description="Trạng thái hiện tại")
    
    # Thông tin lương và bảo hiểm
    base_salary: Decimal = Field(..., description="Lương cơ bản")
    insurance_salary: Decimal = Field(..., description="Lương đóng bảo hiểm")
    insurance_start_date: date = Field(..., description="Ngày bắt đầu đóng BHXH")
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('citizen_id')
    def validate_citizen_id(cls, v):
        """Validate Vietnamese Citizen ID format"""
        if len(v) not in [9, 12]:
            raise ValueError('Citizen ID must be 9 or 12 digits')
        if not v.isdigit():
            raise ValueError('Citizen ID must contain only digits')
        return v


class InsuranceContribution(BaseModel):
    """Thông tin đóng góp bảo hiểm xã hội"""
    
    # Thông tin cơ bản
    contribution_id: str = Field(..., description="Mã đóng góp")
    employee_id: str = Field(..., description="Mã nhân viên")
    contribution_period: str = Field(..., description="Kỳ đóng (MM/YYYY)")
    
    # Chi tiết đóng góp
    bhxh_employee_amount: Decimal = Field(..., description="BHXH - Người lao động")
    bhxh_employer_amount: Decimal = Field(..., description="BHXH - Người sử dụng lao động")
    bhyt_employee_amount: Decimal = Field(..., description="BHYT - Người lao động")
    bhyt_employer_amount: Decimal = Field(..., description="BHYT - Người sử dụng lao động")
    bhtn_employee_amount: Decimal = Field(..., description="BHTN - Người lao động")
    bhtn_employer_amount: Decimal = Field(..., description="BHTN - Người sử dụng lao động")
    
    # Tổng cộng
    total_employee_contribution: Decimal = Field(..., description="Tổng đóng góp người lao động")
    total_employer_contribution: Decimal = Field(..., description="Tổng đóng góp người sử dụng lao động")
    total_contribution: Decimal = Field(..., description="Tổng đóng góp")
    
    # Trạng thái
    status: ContributionStatus = Field(..., description="Trạng thái đóng góp")
    payment_date: Optional[date] = Field(None, description="Ngày thanh toán")
    due_date: date = Field(..., description="Hạn cuối thanh toán")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class InsuranceClaim(BaseModel):
    """Hồ sơ yêu cầu bảo hiểm"""
    
    # Thông tin cơ bản
    claim_id: str = Field(..., description="Mã hồ sơ")
    employee_id: str = Field(..., description="Mã nhân viên")
    claim_type: InsuranceType = Field(..., description="Loại bảo hiểm")
    
    # Chi tiết yêu cầu
    claim_title: str = Field(..., description="Tiêu đề yêu cầu")
    claim_description: str = Field(..., description="Mô tả chi tiết")
    claim_amount: Decimal = Field(..., description="Số tiền yêu cầu")
    
    # Ngày tháng
    incident_date: date = Field(..., description="Ngày xảy ra sự việc")
    submission_date: date = Field(..., description="Ngày nộp hồ sơ")
    expected_processing_date: Optional[date] = Field(None, description="Ngày dự kiến xử lý")
    completion_date: Optional[date] = Field(None, description="Ngày hoàn thành")
    
    # Trạng thái và kết quả
    status: ClaimStatus = Field(..., description="Trạng thái hồ sơ")
    approved_amount: Optional[Decimal] = Field(None, description="Số tiền được duyệt")
    rejection_reason: Optional[str] = Field(None, description="Lý do từ chối")
    
    # Tài liệu đính kèm
    required_documents: List[str] = Field(default_factory=list, description="Tài liệu yêu cầu")
    submitted_documents: List[str] = Field(default_factory=list, description="Tài liệu đã nộp")
    missing_documents: List[str] = Field(default_factory=list, description="Tài liệu còn thiếu")
    
    # Thông tin xử lý
    assigned_officer: Optional[str] = Field(None, description="Cán bộ phụ trách")
    processing_notes: List[str] = Field(default_factory=list, description="Ghi chú xử lý")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)


class Hospital(BaseModel):
    """Thông tin bệnh viện trong hệ thống BHYT"""
    
    # Thông tin cơ bản
    hospital_id: str = Field(..., description="Mã bệnh viện")
    hospital_name: str = Field(..., description="Tên bệnh viện")
    hospital_code: str = Field(..., description="Mã đăng ký khám chữa bệnh BHYT")
    
    # Phân loại
    hospital_type: HospitalType = Field(..., description="Loại hình bệnh viện")
    hospital_level: str = Field(..., description="Hạng bệnh viện (Tuyến T1, T2, T3...)")
    specialties: List[str] = Field(default_factory=list, description="Các chuyên khoa")
    
    # Thông tin địa chỉ
    address: str = Field(..., description="Địa chỉ")
    province: str = Field(..., description="Tỉnh/Thành phố")
    district: str = Field(..., description="Quận/Huyện")
    ward: str = Field(..., description="Phường/Xã")
    
    # Thông tin liên hệ
    phone_number: Optional[str] = Field(None, description="Số điện thoại")
    email: Optional[str] = Field(None, description="Email")
    website: Optional[str] = Field(None, description="Website")
    
    # Thông tin BHYT
    accepts_bhyt: bool = Field(True, description="Có nhận BHYT không")
    bhyt_contract_start: Optional[date] = Field(None, description="Ngày bắt đầu hợp đồng BHYT")
    bhyt_contract_end: Optional[date] = Field(None, description="Ngày kết thúc hợp đồng BHYT")
    
    # Chất lượng dịch vụ
    bed_count: Optional[int] = Field(None, description="Số giường bệnh")
    doctor_count: Optional[int] = Field(None, description="Số bác sĩ")
    quality_rating: Optional[float] = Field(None, description="Đánh giá chất lượng", ge=0, le=5)
    
    # Metadata
    is_active: bool = Field(True, description="Còn hoạt động không")
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)


class VSSDataSummary(BaseModel):
    """Tổng hợp dữ liệu VSS cho một doanh nghiệp"""
    
    # Thông tin doanh nghiệp
    company_tax_code: str = Field(..., description="Mã số thuế")
    company_name: str = Field(..., description="Tên doanh nghiệp")
    
    # Tổng quan nhân viên
    total_employees: int = Field(0, description="Tổng số nhân viên")
    active_employees: int = Field(0, description="Số nhân viên đang làm việc")
    inactive_employees: int = Field(0, description="Số nhân viên ngừng làm việc")
    
    # Danh sách nhân viên chi tiết
    employees: List[EmployeeRecord] = Field(default_factory=list)
    
    # Tổng quan đóng góp BHXH
    total_contributions: int = Field(0, description="Tổng số kỳ đóng góp")
    total_contribution_amount: Decimal = Field(Decimal('0'), description="Tổng số tiền đóng góp")
    
    # Danh sách đóng góp chi tiết
    contributions: List[InsuranceContribution] = Field(default_factory=list)
    
    # Tổng quan hồ sơ bảo hiểm
    total_claims: int = Field(0, description="Tổng số hồ sơ")
    approved_claims: int = Field(0, description="Số hồ sơ được duyệt")
    pending_claims: int = Field(0, description="Số hồ sơ đang chờ")
    rejected_claims: int = Field(0, description="Số hồ sơ bị từ chối")
    
    # Danh sách hồ sơ chi tiết
    claims: List[InsuranceClaim] = Field(default_factory=list)
    
    # Danh sách bệnh viện liên quan
    related_hospitals: List[Hospital] = Field(default_factory=list)
    
    # Thời gian truy xuất
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    data_source: str = Field("VSS_SYSTEM", description="Nguồn dữ liệu")
    
    # Metadata chất lượng dữ liệu
    data_completeness_score: float = Field(0.0, description="Điểm hoàn thiện dữ liệu", ge=0, le=100)
    data_accuracy_score: float = Field(0.0, description="Điểm chính xác dữ liệu", ge=0, le=100)
    extraction_duration_seconds: float = Field(0.0, description="Thời gian trích xuất (giây)")


class VSSExtractionResult(BaseModel):
    """Kết quả trích xuất dữ liệu VSS hoàn chỉnh"""
    
    # Thông tin truy xuất
    extraction_id: str = Field(default_factory=lambda: f"VSS_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    company_tax_code: str = Field(..., description="Mã số thuế")
    extraction_status: str = Field("success", description="Trạng thái trích xuất")
    
    # Dữ liệu VSS đầy đủ
    vss_data: VSSDataSummary = Field(..., description="Dữ liệu VSS tổng hợp")
    
    # Thống kê tổng quan
    extraction_summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Cảnh báo và lỗi
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time_ms: float = Field(0.0, description="Thời gian xử lý (milliseconds)")
    
    def add_summary_stats(self):
        """Tự động tính toán thống kê tổng quan"""
        self.extraction_summary = {
            "employees": {
                "total": len(self.vss_data.employees),
                "active": len([e for e in self.vss_data.employees if e.status == EmployeeStatus.ACTIVE]),
                "inactive": len([e for e in self.vss_data.employees if e.status != EmployeeStatus.ACTIVE])
            },
            "contributions": {
                "total_periods": len(self.vss_data.contributions),
                "total_amount": float(sum(c.total_contribution for c in self.vss_data.contributions)),
                "paid": len([c for c in self.vss_data.contributions if c.status == ContributionStatus.PAID]),
                "pending": len([c for c in self.vss_data.contributions if c.status == ContributionStatus.PENDING])
            },
            "claims": {
                "total": len(self.vss_data.claims),
                "approved": len([c for c in self.vss_data.claims if c.status == ClaimStatus.APPROVED]),
                "pending": len([c for c in self.vss_data.claims if c.status == ClaimStatus.UNDER_REVIEW]),
                "rejected": len([c for c in self.vss_data.claims if c.status == ClaimStatus.REJECTED])
            },
            "hospitals": {
                "total": len(self.vss_data.related_hospitals),
                "public": len([h for h in self.vss_data.related_hospitals if h.hospital_type == HospitalType.PUBLIC]),
                "private": len([h for h in self.vss_data.related_hospitals if h.hospital_type == HospitalType.PRIVATE])
            }
        }
