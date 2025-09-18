"""
Realistic data generator for VSS Integration System
"""
import random
import hashlib
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .data_models import (
    EnterpriseData, EmployeeData, ContributionData, InsuranceRequest, Hospital,
    ComplianceAnalysis, RiskAssessment, Recommendation, VSSIntegrationData
)
from ..utils.logger import setup_module_logger


class RealisticDataGenerator:
    """Generate realistic test data for VSS integration"""
    
    def __init__(self):
        self.logger = setup_module_logger("data_generator")
        
        # Vietnamese company names
        self.company_prefixes = [
            "Công ty TNHH", "Công ty Cổ phần", "Doanh nghiệp tư nhân",
            "Công ty", "Tập đoàn", "Tổng công ty", "Công ty liên doanh"
        ]
        
        self.company_suffixes = [
            "Thương mại", "Sản xuất", "Dịch vụ", "Xây dựng", "Bất động sản",
            "Công nghệ thông tin", "Tài chính", "Ngân hàng", "Bảo hiểm",
            "Vận tải", "Logistics", "Du lịch", "Khách sạn", "Nhà hàng"
        ]
        
        self.business_types = [
            "Thương mại điện tử", "Sản xuất công nghiệp", "Dịch vụ tài chính",
            "Xây dựng dân dụng", "Bất động sản", "Công nghệ thông tin",
            "Vận tải và logistics", "Du lịch và khách sạn", "Giáo dục",
            "Y tế", "Nông nghiệp", "Thủy sản"
        ]
        
        self.vietnamese_names = [
            "Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung",
            "Hoàng Văn Em", "Vũ Thị Phương", "Đặng Văn Giang", "Bùi Thị Hoa",
            "Phan Văn Inh", "Võ Thị Kim", "Đinh Văn Long", "Lý Thị Mai",
            "Tôn Văn Nam", "Đỗ Thị Oanh", "Hồ Văn Phúc", "Ngô Thị Quỳnh"
        ]
        
        self.positions = [
            "Giám đốc", "Phó giám đốc", "Trưởng phòng", "Nhân viên",
            "Kế toán trưởng", "Kỹ sư", "Chuyên viên", "Thư ký",
            "Bảo vệ", "Lao động phổ thông", "Tài xế", "Bán hàng"
        ]
    
    def generate_enterprise_data(self, mst: str) -> EnterpriseData:
        """Generate realistic enterprise data"""
        # Generate company name
        prefix = random.choice(self.company_prefixes)
        suffix = random.choice(self.company_suffixes)
        company_name = f"{prefix} {suffix} {mst}"
        
        # Generate address
        cities = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ"]
        districts = ["Quận 1", "Quận 2", "Quận 3", "Quận Ba Đình", "Quận Hoàn Kiếm"]
        address = f"{random.randint(1, 999)} {random.choice(['Đường', 'Phố'])} {random.choice(['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo', 'Hai Bà Trưng'])}, {random.choice(districts)}, {random.choice(cities)}"
        
        # Generate contact info
        phone = f"0{random.randint(100000000, 999999999)}"
        email = f"contact@{mst}.com"
        
        # Generate business type
        business_type = random.choice(self.business_types)
        
        # Generate financial data
        revenue = random.randint(1000000000, 10000000000)  # 1B to 10B VND
        bank_account = f"{random.randint(1000000000, 9999999999)}"
        
        # Generate registration date
        start_date = datetime.now() - timedelta(days=random.randint(30, 3650))  # 1 month to 10 years ago
        registration_date = start_date.strftime("%Y-%m-%d")
        
        # Generate website
        website = f"https://www.{mst}.com.vn"

        # Generate business category
        business_categories = [
            "Doanh nghiệp nhà nước", "Doanh nghiệp tư nhân", "Công ty cổ phần",
            "Công ty trách nhiệm hữu hạn", "Công ty liên doanh", "Doanh nghiệp FDI"
        ]
        business_category = random.choice(business_categories)

        # Generate expiration date (1-10 years from registration)
        expiration_date = (start_date + timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d")

        return EnterpriseData(
            mst=mst,
            company_name=company_name,
            address=address,
            phone=phone,
            email=email,
            website=website,
            business_type=business_type,
            business_category=business_category,
            revenue=revenue,
            bank_account=bank_account,
            registration_date=registration_date,
            expiration_date=expiration_date
        )
    
    def generate_employee_data(self, mst: str) -> List[EmployeeData]:
        """Generate realistic employee data"""
        employees = []
        num_employees = random.randint(1, 20)  # 1 to 20 employees
        
        for i in range(num_employees):
            employee_id = f"EMP{mst}{i+1:03d}"
            name = random.choice(self.vietnamese_names)
            position = random.choice(self.positions)
            salary = random.randint(5000000, 50000000)  # 5M to 50M VND
            insurance_number = f"BH{mst}{i+1:03d}"
            
            # Generate start date
            start_date = datetime.now() - timedelta(days=random.randint(30, 1095))  # 1 month to 3 years ago
            start_date_str = start_date.strftime("%Y-%m-%d")
            
            employee = EmployeeData(
                mst=mst,
                employee_id=employee_id,
                name=name,
                position=position,
                salary=salary,
                insurance_number=insurance_number,
                start_date=start_date_str,
                status="active" if random.random() > 0.1 else "inactive"
            )
            employees.append(employee)
        
        return employees
    
    def generate_contribution_data(self, mst: str, employees: List[EmployeeData] = None) -> List[ContributionData]:
        """Generate realistic contribution data"""
        contributions = []
        
        if not employees:
            employees = self.generate_employee_data(mst)
        
        for employee in employees:
            # Generate 1-12 contributions per employee (monthly)
            num_contributions = random.randint(1, 12)
            
            for month in range(num_contributions):
                contribution_date = datetime.now() - timedelta(days=30 * month)
                contribution_date_str = contribution_date.strftime("%Y-%m-%d")
                
                # Calculate contribution amount (typically 8% of salary for social insurance)
                contribution_amount = employee.salary * 0.08
                
                contribution = ContributionData(
                    mst=mst,
                    employee_id=employee.employee_id,
                    contribution_amount=contribution_amount,
                    contribution_date=contribution_date_str,
                    insurance_type="social",
                    status="paid" if random.random() > 0.05 else "pending"
                )
                contributions.append(contribution)
        
        return contributions

    def generate_insurance_requests(self, mst: str, employees: List[EmployeeData] = None) -> List[InsuranceRequest]:
        """Generate realistic insurance requests"""
        requests = []

        if not employees:
            employees = self.generate_employee_data(mst)

        request_types = ["new", "change", "terminate"]
        statuses = ["pending", "approved", "rejected"]
        descriptions = [
            "Đăng ký bảo hiểm xã hội lần đầu",
            "Thay đổi thông tin bảo hiểm",
            "Chấm dứt hợp đồng lao động",
            "Điều chỉnh mức đóng bảo hiểm",
            "Cập nhật thông tin cá nhân"
        ]

        for employee in employees:
            # 30% chance of having a request
            if random.random() < 0.3:
                request_date = datetime.now() - timedelta(days=random.randint(1, 365))
                request_date_str = request_date.strftime("%Y-%m-%d")

                request = InsuranceRequest(
                    mst=mst,
                    employee_id=employee.employee_id,
                    request_id=f"REQ{mst}{employee.employee_id[-3:]}{random.randint(1, 99):02d}",
                    request_type=random.choice(request_types),
                    request_date=request_date_str,
                    status=random.choice(statuses),
                    description=random.choice(descriptions)
                )
                requests.append(request)

        return requests

    def generate_hospitals(self, region: str = "all") -> List[Hospital]:
        """Generate hospital data"""
        hospitals = [
            Hospital(
                hospital_id="HOSP001",
                name="Bệnh viện Việt Đức",
                address="40 Tràng Thi, Hoàn Kiếm, Hà Nội",
                phone="024-3825-0536",
                email="info@vietduc.com.vn",
                specialization="Đa khoa",
                region="north"
            ),
            Hospital(
                hospital_id="HOSP002",
                name="Bệnh viện Chợ Rẫy",
                address="201B Nguyễn Chí Thanh, Quận 5, TP.HCM",
                phone="028-3855-4137",
                email="info@choray.com.vn",
                specialization="Đa khoa",
                region="south"
            ),
            Hospital(
                hospital_id="HOSP003",
                name="Bệnh viện Trung ương Huế",
                address="16 Lê Lợi, Vĩnh Ninh, Thành phố Huế",
                phone="0234-3822-376",
                email="info@huecentral.com.vn",
                specialization="Đa khoa",
                region="central"
            ),
            Hospital(
                hospital_id="HOSP004",
                name="Bệnh viện Nhi Đồng 1",
                address="341 Sư Vạn Hạnh, Quận 10, TP.HCM",
                phone="028-3929-0011",
                email="info@nhidong1.com.vn",
                specialization="Nhi khoa",
                region="south"
            ),
            Hospital(
                hospital_id="HOSP005",
                name="Bệnh viện Phụ sản Trung ương",
                address="43 Tràng Thi, Hoàn Kiếm, Hà Nội",
                phone="024-3825-3537",
                email="info@phusan.vn",
                specialization="Phụ sản",
                region="north"
            )
        ]

        if region == "all":
            return hospitals
        else:
            return [h for h in hospitals if h.region == region]

    def generate_compliance_analysis(self, mst: str, contributions: List[ContributionData] = None) -> ComplianceAnalysis:
        """Generate compliance analysis"""
        if not contributions:
            contributions = self.generate_contribution_data(mst)

        # Calculate compliance metrics
        total_contributions = len(contributions)
        paid_contributions = len([c for c in contributions if c.status == "paid"])
        contribution_compliance = (paid_contributions / total_contributions * 100) if total_contributions > 0 else 0

        # Simulate reporting compliance (80-100%)
        reporting_compliance = random.uniform(80, 100)

        # Simulate deadline compliance (70-100%)
        deadline_compliance = random.uniform(70, 100)

        # Overall score
        overall_score = (contribution_compliance + reporting_compliance + deadline_compliance) / 3

        # Generate issues
        issues = []
        if contribution_compliance < 90:
            issues.append("Một số khoản đóng bảo hiểm chưa được thanh toán")
        if reporting_compliance < 90:
            issues.append("Báo cáo bảo hiểm chưa đầy đủ")
        if deadline_compliance < 90:
            issues.append("Một số deadline đóng bảo hiểm đã quá hạn")

        # Generate recommendations
        recommendations = []
        if issues:
            recommendations.append("Nâng cao tỷ lệ thanh toán đúng hạn")
            recommendations.append("Đẩy mạnh công tác báo cáo và cập nhật dữ liệu")
            recommendations.append("Thiết lập hệ thống nhắc nhở tự động")

        return ComplianceAnalysis(
            mst=mst,
            overall_score=round(overall_score, 2),
            contribution_compliance=round(contribution_compliance, 2),
            reporting_compliance=round(reporting_compliance, 2),
            deadline_compliance=round(deadline_compliance, 2),
            issues_found=issues,
            recommendations=recommendations
        )

    def generate_risk_assessment(self, mst: str, compliance_score: float = None) -> RiskAssessment:
        """Generate risk assessment"""
        if compliance_score is None:
            compliance_score = random.uniform(0, 100)

        # Determine risk level based on compliance score
        if compliance_score >= 90:
            risk_level = "low"
            risk_score = random.uniform(0, 30)
        elif compliance_score >= 70:
            risk_level = "medium"
            risk_score = random.uniform(30, 70)
        else:
            risk_level = "high"
            risk_score = random.uniform(70, 100)

        # Generate risk factors
        risk_factors = []
        if risk_level == "high":
            risk_factors.extend([
                "Tỷ lệ tuân thủ thấp",
                "Thiếu dữ liệu báo cáo",
                "Quá hạn đóng bảo hiểm nhiều lần"
            ])
        elif risk_level == "medium":
            risk_factors.extend([
                "Tỷ lệ tuân thủ trung bình",
                "Một số khoản đóng bảo hiểm chậm trễ"
            ])
        else:
            risk_factors.append("Tuân thủ tốt, rủi ro thấp")

        # Generate mitigation suggestions
        mitigation_suggestions = []
        if risk_level != "low":
            mitigation_suggestions.extend([
                "Tăng cường giám sát quy trình đóng bảo hiểm",
                "Thiết lập hệ thống nhắc nhở tự động",
                "Đào tạo nhân viên về quy định bảo hiểm",
                "Kiểm tra định kỳ tình trạng tuân thủ"
            ])

        return RiskAssessment(
            mst=mst,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            risk_factors=risk_factors,
            mitigation_suggestions=mitigation_suggestions
        )

    def generate_recommendations(self, mst: str, compliance_analysis: ComplianceAnalysis = None,
                               risk_assessment: RiskAssessment = None) -> List[Recommendation]:
        """Generate improvement recommendations"""
        recommendations = []

        if not compliance_analysis:
            compliance_analysis = self.generate_compliance_analysis(mst)
        if not risk_assessment:
            risk_assessment = self.generate_risk_assessment(mst, compliance_analysis.overall_score)

        # Compliance-based recommendations
        if compliance_analysis.overall_score < 90:
            recommendations.append(Recommendation(
                mst=mst,
                category="compliance",
                priority="high" if compliance_analysis.overall_score < 70 else "medium",
                title="Cải thiện tỷ lệ tuân thủ đóng bảo hiểm",
                description="Nâng cao tỷ lệ thanh toán đúng hạn và đầy đủ các khoản đóng bảo hiểm xã hội",
                impact_score=8.5,
                implementation_effort="medium"
            ))

        # Risk-based recommendations
        if risk_assessment.risk_level == "high":
            recommendations.append(Recommendation(
                mst=mst,
                category="risk",
                priority="critical",
                title="Giảm thiểu rủi ro pháp lý",
                description="Thực hiện các biện pháp khẩn cấp để giảm rủi ro vi phạm quy định bảo hiểm",
                impact_score=9.0,
                implementation_effort="high"
            ))
        elif risk_assessment.risk_level == "medium":
            recommendations.append(Recommendation(
                mst=mst,
                category="risk",
                priority="medium",
                title="Giảm thiểu rủi ro vận hành",
                description="Cải thiện quy trình để giảm thiểu rủi ro trong hoạt động bảo hiểm",
                impact_score=7.0,
                implementation_effort="medium"
            ))

        # Efficiency recommendations
        recommendations.append(Recommendation(
            mst=mst,
            category="efficiency",
            priority="low",
            title="Tối ưu hóa quy trình quản lý bảo hiểm",
            description="Triển khai hệ thống tự động hóa để tăng hiệu quả quản lý dữ liệu bảo hiểm",
            impact_score=6.5,
            implementation_effort="medium"
        ))

        # Cost optimization
        recommendations.append(Recommendation(
            mst=mst,
            category="cost",
            priority="low",
            title="Tối ưu hóa chi phí bảo hiểm",
            description="Phân tích và tối ưu hóa các khoản chi phí liên quan đến bảo hiểm xã hội",
            impact_score=5.5,
            implementation_effort="low"
        ))

        return recommendations

    def generate_vss_integration_data(self, mst: str) -> VSSIntegrationData:
        """Generate complete VSS integration data"""
        enterprise = self.generate_enterprise_data(mst)
        employees = self.generate_employee_data(mst)
        contributions = self.generate_contribution_data(mst, employees)
        insurance_requests = self.generate_insurance_requests(mst, employees)
        hospitals = self.generate_hospitals()

        # Generate compliance analysis
        compliance_analysis = self.generate_compliance_analysis(mst, contributions)

        # Generate risk assessment
        risk_assessment = self.generate_risk_assessment(mst, compliance_analysis.overall_score)

        # Generate recommendations
        recommendations = self.generate_recommendations(mst, compliance_analysis, risk_assessment)

        return VSSIntegrationData(
            enterprise=enterprise,
            employees=employees,
            contributions=contributions,
            insurance_requests=insurance_requests,
            hospitals=hospitals,
            compliance_analysis=compliance_analysis,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            compliance_score=compliance_analysis.overall_score,
            risk_level=risk_assessment.risk_level,
            extraction_time=random.uniform(0.1, 2.0)
        )
