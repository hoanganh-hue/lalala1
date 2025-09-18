"""
Unit tests for data generator
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.data_generator import RealisticDataGenerator
from src.core.data_models import EnterpriseData, EmployeeData, ContributionData


class TestDataGenerator:
    """Test RealisticDataGenerator class"""

    def test_data_generator_initialization(self):
        """Test DataGenerator initialization"""
        generator = RealisticDataGenerator()
        assert generator is not None

    def test_generate_enterprise_data(self):
        """Test generating enterprise data"""
        generator = RealisticDataGenerator()
        data = generator.generate_enterprise_data("110198560")

        assert isinstance(data, EnterpriseData)
        assert data.mst == "110198560"
        assert data.company_name is not None
        assert len(data.company_name) > 0
        assert data.address is not None
        assert len(data.address) > 0

    def test_generate_employee_data(self):
        """Test generating employee data"""
        generator = RealisticDataGenerator()
        employees = generator.generate_employee_data("110198560")

        assert isinstance(employees, list)
        assert len(employees) >= 1  # At least one employee
        for emp in employees:
            assert isinstance(emp, EmployeeData)
            assert emp.mst == "110198560"
            assert emp.employee_id.startswith("EMP")
            assert emp.name is not None
            assert len(emp.name) > 0
            assert emp.position is not None
            assert emp.salary > 0
            assert emp.insurance_number.startswith("BH")

    def test_generate_contribution_data(self):
        """Test generating contribution data"""
        generator = RealisticDataGenerator()

        # Create mock employee
        employee = EmployeeData(
            mst="110198560",
            employee_id="EMP001",
            name="Test Employee",
            position="Test Position",
            salary=10000000,  # 10M VND
            insurance_number="BH001"
        )

        contributions = generator.generate_contribution_data("110198560", [employee])

        assert isinstance(contributions, list)
        assert len(contributions) >= 1
        for contrib in contributions:
            assert isinstance(contrib, ContributionData)
            assert contrib.mst == "110198560"
            assert contrib.employee_id == "EMP001"
            assert contrib.contribution_amount > 0
            assert contrib.contribution_date is not None
            assert contrib.insurance_type == "social"
            assert contrib.status in ["paid", "pending"]

    def test_generate_vss_integration_data(self):
        """Test generating complete VSS integration data"""
        generator = RealisticDataGenerator()
        data = generator.generate_vss_integration_data("110198560")

        assert isinstance(data, dict)
        assert "enterprise" in data
        assert "employees" in data
        assert "contributions" in data
        assert "compliance_score" in data
        assert "risk_level" in data
        assert "extraction_time" in data
        assert "timestamp" in data

        assert isinstance(data["enterprise"], EnterpriseData)
        assert isinstance(data["employees"], list)
        assert isinstance(data["contributions"], list)
        assert isinstance(data["compliance_score"], (int, float))
        assert data["risk_level"] in ["low", "medium", "high"]

    def test_data_consistency_with_seed(self):
        """Test data consistency when using seed"""
        generator = RealisticDataGenerator()

        # Generate data twice with same MST (should be deterministic)
        data1 = generator.generate_enterprise_data("110198560")
        data2 = generator.generate_enterprise_data("110198560")

        # Should be identical due to deterministic generation
        assert data1.company_name == data2.company_name
        assert data1.address == data2.address

    def test_different_mst_different_data(self):
        """Test that different MSTs generate different data"""
        generator = RealisticDataGenerator()

        data1 = generator.generate_enterprise_data("110198560")
        data2 = generator.generate_enterprise_data("110197454")

        # Should be different
        assert data1.company_name != data2.company_name
        assert data1.address != data2.address


if __name__ == "__main__":
    pytest.main([__file__])