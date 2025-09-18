"""
Integration tests for API clients
"""
import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api.vss_client import VSSAPIClient
from src.api.enterprise_client import EnterpriseAPIClient
from src.core.data_models import EmployeeData, ContributionData, EnterpriseData


class TestVSSAPIIntegration:
    """Integration tests for VSS API client"""

    def test_vss_client_initialization(self):
        """Test VSS client initializes correctly"""
        client = VSSAPIClient()
        assert client is not None
        assert client.use_mock == True  # Should use mock by default

    def test_get_employee_data_mock(self):
        """Test getting employee data with mock"""
        client = VSSAPIClient()
        employees = client.get_employee_data("110198560")

        assert employees is not None
        assert len(employees) > 0
        assert all(isinstance(emp, EmployeeData) for emp in employees)

        # Check data consistency
        for emp in employees:
            assert emp.mst == "110198560"
            assert emp.employee_id.startswith("EMP110198560")
            assert emp.name is not None
            assert emp.position is not None
            assert emp.salary > 0
            assert emp.insurance_number.startswith("INS110198560")

    def test_get_contribution_data_mock(self):
        """Test getting contribution data with mock"""
        client = VSSAPIClient()
        contributions = client.get_contribution_data("110198560")

        assert contributions is not None
        assert len(contributions) > 0
        assert all(isinstance(contrib, ContributionData) for contrib in contributions)

        # Check data consistency
        for contrib in contributions:
            assert contrib.mst == "110198560"
            assert contrib.employee_id.startswith("EMP110198560")
            assert contrib.contribution_amount > 0
            assert contrib.contribution_date is not None
            assert contrib.insurance_type == "social"
            assert contrib.status == "paid"

    def test_mock_data_consistency(self):
        """Test that mock data is consistent across calls"""
        client = VSSAPIClient()

        # Get data multiple times
        employees1 = client.get_employee_data("110198560")
        employees2 = client.get_employee_data("110198560")

        # Should be identical
        assert len(employees1) == len(employees2)
        for emp1, emp2 in zip(employees1, employees2):
            assert emp1.employee_id == emp2.employee_id
            assert emp1.name == emp2.name
            assert emp1.salary == emp2.salary

    def test_different_mst_different_data(self):
        """Test that different MSTs generate different data"""
        client = VSSAPIClient()

        employees1 = client.get_employee_data("110198560")
        employees2 = client.get_employee_data("110197454")

        # Should be different
        assert employees1[0].employee_id != employees2[0].employee_id
        # Should have same structure but different content
        assert len(employees1) >= 1  # At least one employee
        assert len(employees2) >= 1
        assert employees1[0].mst == "110198560"
        assert employees2[0].mst == "110197454"


class TestEnterpriseAPIIntegration:
    """Integration tests for Enterprise API client"""

    def test_enterprise_client_initialization(self):
        """Test Enterprise client initializes correctly"""
        client = EnterpriseAPIClient()
        assert client is not None

    def test_get_enterprise_data_structure(self):
        """Test enterprise data has correct structure"""
        client = EnterpriseAPIClient()
        data = client.get_company_info("110198560")

        if data:  # May be None if API is down
            assert isinstance(data, EnterpriseData)
            assert data.mst == "110198560"
            # Note: API may return empty data, just check structure
            assert hasattr(data, 'company_name')
            assert hasattr(data, 'address')


class TestAPIErrorHandling:
    """Test error handling in API clients"""

    def test_vss_client_handles_invalid_mst(self):
        """Test VSS client handles invalid MST gracefully"""
        client = VSSAPIClient()
        employees = client.get_employee_data("invalid_mst")

        # Should still return data (mock generates for any MST)
        assert employees is not None
        assert len(employees) > 0

    def test_vss_client_handles_empty_mst(self):
        """Test VSS client handles empty MST"""
        client = VSSAPIClient()
        employees = client.get_employee_data("")

        assert employees is not None
        assert len(employees) > 0


if __name__ == "__main__":
    pytest.main([__file__])