"""
VSS API client for retrieving social insurance data
"""
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .base_client import BaseAPIClient
from ..core.data_models import EmployeeData, ContributionData, InsuranceRequest, Hospital
from ..config.settings import config
from ..utils.mst import normalize_mst


class VSSAPIClient(BaseAPIClient):
    """Client for VSS API with mock fallback"""

    def __init__(self):
        api_config = config.get_api_config()
        super().__init__(
            base_url=api_config.get('vss_url', 'http://vssapp.teca.vn:8088'),
            client_name='vss'
        )
        self.use_mock = api_config.get('use_mock_vss', False)  # Use real API by default, fallback to mock
    
    def get_employee_data(self, mst: str) -> Optional[List[EmployeeData]]:
        """Get employee data by MST"""
        try:
            norm_mst = normalize_mst(mst)
            if not norm_mst:
                self.logger.warning(f"Invalid MST provided: {mst}")
                return None
            if self.use_mock:
                # Use mock data for stable testing
                data = self._generate_mock_employee_data(mst)
                return self._parse_employee_data(mst, data)
            else:
                # Try real API
                data = self.get(f"/employees/{norm_mst}")
                if data:
                    return self._parse_employee_data(norm_mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get employee data for MST {mst}: {str(e)}")
            # Fallback to mock data if real API fails
            if not self.use_mock:
                self.logger.info(f"Falling back to mock data for MST {mst}")
                data = self._generate_mock_employee_data(mst)
                return self._parse_employee_data(mst, data)
            return None
    
    def get_contribution_data(self, mst: str) -> Optional[List[ContributionData]]:
        """Get contribution data by MST"""
        try:
            norm_mst = normalize_mst(mst)
            if not norm_mst:
                self.logger.warning(f"Invalid MST provided: {mst}")
                return None
            if self.use_mock:
                # Use mock data for stable testing
                data = self._generate_mock_contribution_data(mst)
                return self._parse_contribution_data(mst, data)
            else:
                # Try real API
                data = self.get(f"/contributions/{norm_mst}")
                if data:
                    return self._parse_contribution_data(norm_mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get contribution data for MST {mst}: {str(e)}")
            # Fallback to mock data if real API fails
            if not self.use_mock:
                self.logger.info(f"Falling back to mock data for MST {mst}")
                data = self._generate_mock_contribution_data(mst)
                return self._parse_contribution_data(mst, data)
            return None

    def get_insurance_requests(self, mst: str) -> Optional[List[InsuranceRequest]]:
        """Get insurance requests by MST"""
        try:
            norm_mst = normalize_mst(mst)
            if not norm_mst:
                self.logger.warning(f"Invalid MST provided: {mst}")
                return None
            if self.use_mock:
                # Use mock data for stable testing
                data = self._generate_mock_insurance_requests(mst)
                return self._parse_insurance_requests(mst, data)
            else:
                # Try real API
                data = self.get(f"/insurance-requests/{norm_mst}")
                if data:
                    return self._parse_insurance_requests(norm_mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get insurance requests for MST {mst}: {str(e)}")
            # Fallback to mock data if real API fails
            if not self.use_mock:
                self.logger.info(f"Falling back to mock data for MST {mst}")
                data = self._generate_mock_insurance_requests(mst)
                return self._parse_insurance_requests(mst, data)
            return None

    def get_hospitals(self, region: str = "all") -> Optional[List[Hospital]]:
        """Get hospitals list, optionally filtered by region"""
        try:
            if self.use_mock:
                # Use mock data for stable testing
                data = self._generate_mock_hospitals(region)
                return self._parse_hospitals(data)
            else:
                # Try real API
                endpoint = f"/hospitals" if region == "all" else f"/hospitals/region/{region}"
                data = self.get(endpoint)
                if data:
                    return self._parse_hospitals(data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get hospitals: {str(e)}")
            # Fallback to mock data if real API fails
            if not self.use_mock:
                self.logger.info("Falling back to mock hospitals data")
                data = self._generate_mock_hospitals(region)
                return self._parse_hospitals(data)
            return None
    
    def _parse_employee_data(self, mst: str, data: Dict[str, Any]) -> List[EmployeeData]:
        """Parse employee data from API response"""
        employees = []
        
        # Handle different response formats
        if isinstance(data, list):
            employee_list = data
        elif isinstance(data, dict) and 'employees' in data:
            employee_list = data['employees']
        else:
            employee_list = [data]
        
        for emp_data in employee_list:
            employee = EmployeeData(
                mst=mst,
                employee_id=emp_data.get('employee_id', ''),
                name=emp_data.get('name', ''),
                position=emp_data.get('position', ''),
                salary=emp_data.get('salary', 0.0),
                insurance_number=emp_data.get('insurance_number', ''),
                start_date=emp_data.get('start_date', ''),
                status=emp_data.get('status', 'active')
            )
            employees.append(employee)
        
        return employees
    
    def _parse_contribution_data(self, mst: str, data: Dict[str, Any]) -> List[ContributionData]:
        """Parse contribution data from API response"""
        contributions = []
        
        # Handle different response formats
        if isinstance(data, list):
            contribution_list = data
        elif isinstance(data, dict) and 'contributions' in data:
            contribution_list = data['contributions']
        else:
            contribution_list = [data]
        
        for contrib_data in contribution_list:
            contribution = ContributionData(
                mst=mst,
                employee_id=contrib_data.get('employee_id', ''),
                contribution_amount=contrib_data.get('contribution_amount', 0.0),
                contribution_date=contrib_data.get('contribution_date', ''),
                insurance_type=contrib_data.get('insurance_type', 'social'),
                status=contrib_data.get('status', 'paid')
            )
            contributions.append(contribution)
        
        return contributions

    def _parse_insurance_requests(self, mst: str, data: Dict[str, Any]) -> List[InsuranceRequest]:
        """Parse insurance requests from API response"""
        requests = []

        # Handle different response formats
        if isinstance(data, list):
            request_list = data
        elif isinstance(data, dict) and 'requests' in data:
            request_list = data['requests']
        else:
            request_list = [data]

        for req_data in request_list:
            request = InsuranceRequest(
                mst=mst,
                employee_id=req_data.get('employee_id', ''),
                request_id=req_data.get('request_id', ''),
                request_type=req_data.get('request_type', 'new'),
                request_date=req_data.get('request_date', ''),
                status=req_data.get('status', 'pending'),
                description=req_data.get('description')
            )
            requests.append(request)

        return requests

    def _parse_hospitals(self, data: Dict[str, Any]) -> List[Hospital]:
        """Parse hospitals from API response"""
        hospitals = []

        # Handle different response formats
        if isinstance(data, list):
            hospital_list = data
        elif isinstance(data, dict) and 'hospitals' in data:
            hospital_list = data['hospitals']
        else:
            hospital_list = [data]

        for hosp_data in hospital_list:
            hospital = Hospital(
                hospital_id=hosp_data.get('hospital_id', ''),
                name=hosp_data.get('name', ''),
                address=hosp_data.get('address', ''),
                phone=hosp_data.get('phone', ''),
                email=hosp_data.get('email'),
                specialization=hosp_data.get('specialization'),
                region=hosp_data.get('region', 'unknown')
            )
            hospitals.append(hospital)

        return hospitals

    def _generate_mock_employee_data(self, mst: str) -> Dict[str, Any]:
        """Generate consistent mock employee data based on MST"""
        # Use MST as seed for consistent data generation
        seed = int(hashlib.md5(mst.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # Generate 1-10 employees
        num_employees = random.randint(1, 10)

        employees = []
        vietnamese_names = [
            "Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D", "Hoàng Văn E",
            "Vũ Thị F", "Đặng Văn G", "Bùi Thị H", "Đỗ Văn I", "Hồ Thị K"
        ]

        positions = ["Nhân viên", "Kế toán", "Kỹ sư", "Quản lý", "Giám đốc", "Marketing"]
        statuses = ["active", "inactive", "terminated"]

        for i in range(num_employees):
            employee_seed = seed + i
            random.seed(employee_seed)

            start_date = datetime.now() - timedelta(days=random.randint(30, 365*5))
            salary = random.randint(5000000, 50000000)  # 5M - 50M VND

            employee = {
                "employee_id": f"EMP{mst}{i+1:03d}",
                "name": random.choice(vietnamese_names),
                "position": random.choice(positions),
                "salary": salary,
                "insurance_number": f"INS{mst}{i+1:03d}",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "status": random.choice(statuses)
            }
            employees.append(employee)

        return {"employees": employees}

    def _generate_mock_contribution_data(self, mst: str) -> Dict[str, Any]:
        """Generate consistent mock contribution data based on MST"""
        # Get employee data first to ensure consistency
        employee_data = self._generate_mock_employee_data(mst)
        employees = employee_data.get("employees", [])

        contributions = []
        for emp in employees:
            emp_id = emp["employee_id"]

            # Generate contributions for last 12 months
            for months_back in range(12):
                contrib_date = datetime.now() - timedelta(days=30 * months_back)
                amount = int(emp["salary"] * 0.105)  # 10.5% contribution

                contribution = {
                    "employee_id": emp_id,
                    "contribution_amount": amount,
                    "contribution_date": contrib_date.strftime("%Y-%m-%d"),
                    "insurance_type": "social",
                    "status": "paid"
                }
                contributions.append(contribution)

        return {"contributions": contributions}

    def _generate_mock_insurance_requests(self, mst: str) -> Dict[str, Any]:
        """Generate consistent mock insurance requests based on MST"""
        # Get employee data first to ensure consistency
        employee_data = self._generate_mock_employee_data(mst)
        employees = employee_data.get("employees", [])

        requests = []
        request_types = ["new", "change", "terminate"]
        statuses = ["pending", "approved", "rejected"]

        for emp in employees:
            emp_id = emp["employee_id"]

            # Generate 0-2 requests per employee
            num_requests = random.randint(0, 2)
            for i in range(num_requests):
                request_date = datetime.now() - timedelta(days=random.randint(1, 365))

                request = {
                    "employee_id": emp_id,
                    "request_id": f"REQ{mst}{emp_id[-3:]}{i+1:02d}",
                    "request_type": random.choice(request_types),
                    "request_date": request_date.strftime("%Y-%m-%d"),
                    "status": random.choice(statuses),
                    "description": f"Insurance request for employee {emp['name']}"
                }
                requests.append(request)

        return {"requests": requests}

    def _generate_mock_hospitals(self, region: str = "all") -> Dict[str, Any]:
        """Generate mock hospitals data"""
        hospitals_data = [
            {
                "hospital_id": "HOSP001",
                "name": "Bệnh viện Việt Đức",
                "address": "40 Tràng Thi, Hoàn Kiếm, Hà Nội",
                "phone": "024-3825-0536",
                "email": "info@vietduc.com.vn",
                "specialization": "Đa khoa",
                "region": "north"
            },
            {
                "hospital_id": "HOSP002",
                "name": "Bệnh viện Chợ Rẫy",
                "address": "201B Nguyễn Chí Thanh, Quận 5, TP.HCM",
                "phone": "028-3855-4137",
                "email": "info@choray.com.vn",
                "specialization": "Đa khoa",
                "region": "south"
            },
            {
                "hospital_id": "HOSP003",
                "name": "Bệnh viện Trung ương Huế",
                "address": "16 Lê Lợi, Vĩnh Ninh, Thành phố Huế",
                "phone": "0234-3822-376",
                "email": "info@huecentral.com.vn",
                "specialization": "Đa khoa",
                "region": "central"
            },
            {
                "hospital_id": "HOSP004",
                "name": "Bệnh viện Nhi Đồng 1",
                "address": "341 Sư Vạn Hạnh, Quận 10, TP.HCM",
                "phone": "028-3929-0011",
                "email": "info@nhidong1.com.vn",
                "specialization": "Nhi khoa",
                "region": "south"
            },
            {
                "hospital_id": "HOSP005",
                "name": "Bệnh viện Phụ sản Trung ương",
                "address": "43 Tràng Thi, Hoàn Kiếm, Hà Nội",
                "phone": "024-3825-3537",
                "email": "info@phusan.vn",
                "specialization": "Phụ sản",
                "region": "north"
            }
        ]

        if region == "all":
            return {"hospitals": hospitals_data}
        else:
            filtered = [h for h in hospitals_data if h["region"] == region]
            return {"hospitals": filtered}