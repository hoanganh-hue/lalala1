"""
Unit tests for data models
"""
import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.data_models import (
    ProcessingResult, EnterpriseData, EmployeeData, ContributionData,
    ProcessingMetrics
)


class TestProcessingResult:
    """Test ProcessingResult data model"""

    def test_processing_result_creation(self):
        """Test creating ProcessingResult"""
        result = ProcessingResult(
            mst="110198560",
            success=True,
            confidence_score=0.95,
            data_quality="HIGH",
            processing_time=1.5,
            error_message=None
        )

        assert result.mst == "110198560"
        assert result.success == True
        assert result.confidence_score == 0.95
        assert result.data_quality == "HIGH"
        assert result.processing_time == 1.5
        assert result.error_message is None

    def test_processing_result_defaults(self):
        """Test ProcessingResult default values"""
        result = ProcessingResult(mst="110198560")

        assert result.mst == "110198560"
        assert result.success == False
        assert result.confidence_score == 0.0
        assert result.data_quality == "UNKNOWN"
        assert result.processing_time == 0.0
        assert result.error_message is None


class TestEnterpriseData:
    """Test EnterpriseData data model"""

    def test_enterprise_data_creation(self):
        """Test creating EnterpriseData"""
        data = EnterpriseData(
            mst="110198560",
            company_name="Công ty TNHH ABC",
            address="123 Đường ABC, Quận 1, TP.HCM",
            phone="0123456789",
            email="contact@abc.com",
            business_type="Công nghệ thông tin",
            revenue=1000000000,
            bank_account="123456789",
            registration_date="2020-01-01"
        )

        assert data.mst == "110198560"
        assert data.company_name == "Công ty TNHH ABC"
        assert data.address == "123 Đường ABC, Quận 1, TP.HCM"
        assert data.phone == "0123456789"
        assert data.email == "contact@abc.com"
        assert data.business_type == "Công nghệ thông tin"
        assert data.revenue == 1000000000
        assert data.bank_account == "123456789"
        assert data.registration_date == "2020-01-01"

    def test_enterprise_data_defaults(self):
        """Test EnterpriseData default values"""
        data = EnterpriseData(mst="110198560")

        assert data.mst == "110198560"
        assert data.company_name == ""
        assert data.address == ""
        assert data.phone == ""
        assert data.email == ""
        assert data.business_type == ""
        assert data.revenue is None
        assert data.bank_account is None
        assert data.registration_date is None


class TestEmployeeData:
    """Test EmployeeData data model"""

    def test_employee_data_creation(self):
        """Test creating EmployeeData"""
        data = EmployeeData(
            mst="110198560",
            employee_id="EMP001",
            name="Nguyễn Văn A",
            position="Kỹ sư",
            salary=15000000,
            insurance_number="INS001",
            start_date="2020-01-01",
            status="active"
        )

        assert data.mst == "110198560"
        assert data.employee_id == "EMP001"
        assert data.name == "Nguyễn Văn A"
        assert data.position == "Kỹ sư"
        assert data.salary == 15000000
        assert data.insurance_number == "INS001"
        assert data.start_date == "2020-01-01"
        assert data.status == "active"

    def test_employee_data_defaults(self):
        """Test EmployeeData default values"""
        data = EmployeeData(mst="110198560", employee_id="EMP001")

        assert data.mst == "110198560"
        assert data.employee_id == "EMP001"
        assert data.name == ""
        assert data.position == ""
        assert data.salary == 0.0
        assert data.insurance_number == ""
        assert data.start_date == ""
        assert data.status == "active"


class TestContributionData:
    """Test ContributionData data model"""

    def test_contribution_data_creation(self):
        """Test creating ContributionData"""
        data = ContributionData(
            mst="110198560",
            employee_id="EMP001",
            contribution_amount=157500,  # 10.5% of 1.5M
            contribution_date="2024-01-01",
            insurance_type="social",
            status="paid"
        )

        assert data.mst == "110198560"
        assert data.employee_id == "EMP001"
        assert data.contribution_amount == 157500
        assert data.contribution_date == "2024-01-01"
        assert data.insurance_type == "social"
        assert data.status == "paid"

    def test_contribution_data_defaults(self):
        """Test ContributionData default values"""
        data = ContributionData(mst="110198560", employee_id="EMP001")

        assert data.mst == "110198560"
        assert data.employee_id == "EMP001"
        assert data.contribution_amount == 0.0
        assert data.contribution_date == ""
        assert data.insurance_type == "social"
        assert data.status == "paid"


class TestProcessingMetrics:
    """Test ProcessingMetrics data model"""

    def test_processing_metrics_creation(self):
        """Test creating ProcessingMetrics"""
        metrics = ProcessingMetrics(
            total_processed=100,
            successful=95,
            failed=5,
            success_rate=95.0,
            average_processing_time=1.2,
            total_api_calls=150,
            cache_hits=50,
            cache_misses=100
        )

        assert metrics.total_processed == 100
        assert metrics.successful == 95
        assert metrics.failed == 5
        assert metrics.success_rate == 95.0
        assert metrics.average_processing_time == 1.2
        assert metrics.total_api_calls == 150
        assert metrics.cache_hits == 50
        assert metrics.cache_misses == 100

    def test_processing_metrics_defaults(self):
        """Test ProcessingMetrics default values"""
        metrics = ProcessingMetrics()

        assert metrics.total_processed == 0
        assert metrics.successful == 0
        assert metrics.failed == 0
        assert metrics.success_rate == 0.0
        assert metrics.average_processing_time == 0.0
        assert metrics.total_api_calls == 0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0

    def test_processing_metrics_calculations(self):
        """Test ProcessingMetrics calculations"""
        metrics = ProcessingMetrics()
        metrics.total_processed = 10
        metrics.successful = 8
        metrics.failed = 2

        # Success rate should be calculated as (successful / total_processed) * 100
        assert metrics.success_rate == 80.0


if __name__ == "__main__":
    pytest.main([__file__])