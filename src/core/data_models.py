"""
Data models and structures for VSS Integration System
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class ProcessingResult:
    """Standard result structure for MST processing"""
    mst: str
    success: bool
    processing_time: float
    confidence_score: float
    data_quality: str
    error: Optional[str] = None
    retry_count: int = 0
    source: str = "unknown"
    timestamp: str = None
    api_errors: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class EnterpriseData:
    """Enterprise information structure"""
    mst: str
    company_name: str
    address: str
    phone: str
    email: str
    business_type: str
    website: Optional[str] = None
    business_category: Optional[str] = None  # Loại hình doanh nghiệp
    revenue: Optional[float] = None
    bank_account: Optional[str] = None
    registration_date: Optional[str] = None
    expiration_date: Optional[str] = None


@dataclass
class EmployeeData:
    """Employee information structure"""
    mst: str
    employee_id: str
    name: str
    position: str
    salary: float
    insurance_number: str
    start_date: str
    status: str = "active"


@dataclass
class ContributionData:
    """Social insurance contribution data"""
    mst: str
    employee_id: str
    contribution_amount: float
    contribution_date: str
    insurance_type: str
    status: str = "paid"


@dataclass
class InsuranceRequest:
    """Insurance request data structure"""
    mst: str
    employee_id: str
    request_id: str
    request_type: str  # "new", "change", "terminate"
    request_date: str
    status: str = "pending"  # "pending", "approved", "rejected"
    description: Optional[str] = None


@dataclass
class Hospital:
    """Hospital information structure"""
    hospital_id: str
    name: str
    address: str
    phone: str
    email: Optional[str] = None
    specialization: Optional[str] = None
    region: str = "unknown"


@dataclass
class ComplianceAnalysis:
    """Detailed compliance analysis"""
    mst: str
    overall_score: float
    contribution_compliance: float
    reporting_compliance: float
    deadline_compliance: float
    issues_found: List[str]
    recommendations: List[str]
    analysis_date: str = None

    def __post_init__(self):
        if self.analysis_date is None:
            self.analysis_date = datetime.now().isoformat()


@dataclass
class RiskAssessment:
    """Risk assessment structure"""
    mst: str
    risk_level: str  # "low", "medium", "high", "critical"
    risk_score: float
    risk_factors: List[str]
    mitigation_suggestions: List[str]
    assessment_date: str = None

    def __post_init__(self):
        if self.assessment_date is None:
            self.assessment_date = datetime.now().isoformat()


@dataclass
class Recommendation:
    """Improvement recommendation structure"""
    mst: str
    category: str  # "compliance", "risk", "efficiency", "cost"
    priority: str  # "low", "medium", "high", "critical"
    title: str
    description: str
    impact_score: float
    implementation_effort: str  # "low", "medium", "high"
    created_date: str = None

    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()


@dataclass
class VSSIntegrationData:
    """Complete VSS integration data structure"""
    enterprise: EnterpriseData
    employees: List[EmployeeData]
    contributions: List[ContributionData]
    insurance_requests: List[InsuranceRequest]
    hospitals: List[Hospital]
    compliance_analysis: ComplianceAnalysis
    risk_assessment: RiskAssessment
    recommendations: List[Recommendation]
    compliance_score: float
    risk_level: str
    extraction_time: float
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ProcessingMetrics:
    """Processing performance metrics"""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    cache_hits: int = 0
    avg_response_time: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_processed == 0:
            return 0.0
        return (self.successful / self.total_processed) * 100
    
    @property
    def processing_rate(self) -> float:
        """Calculate processing rate per second"""
        if not self.start_time or not self.end_time:
            return 0.0
        duration = self.end_time - self.start_time
        if duration == 0:
            return 0.0
        return self.total_processed / duration
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        if self.total_processed == 0:
            return 0.0
        return (self.cache_hits / self.total_processed) * 100


@dataclass
class SystemConfig:
    """System configuration structure"""
    # API Settings
    enterprise_api_url: str = "https://thongtindoanhnghiep.co/api/company"
    vss_api_url: str = "http://vssapp.teca.vn:8088"
    
    # Timeout Settings
    request_timeout: int = 30
    connection_timeout: int = 10
    
    # Retry Settings
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate Limiting
    max_requests_per_minute: int = 15
    rate_limit_window: int = 60
    
    # Processing Settings
    max_workers: int = 4
    batch_size: int = 50
    
    # Caching
    cache_ttl: int = 300  # 5 minutes
    
    # Circuit Breaker
    failure_threshold: int = 5
    recovery_timeout: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/vss_integration.log"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
