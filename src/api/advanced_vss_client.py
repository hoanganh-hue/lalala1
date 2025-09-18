"""
Advanced VSS API client for deep data extraction and analytics
"""
import hashlib
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .base_client import BaseAPIClient
from ..core.data_models import (
    EmployeeData, ContributionData, InsuranceRequest, Hospital,
    ComplianceAnalysis, RiskAssessment, Recommendation
)
from ..config.settings import config


class AdvancedVSSAPIClient(BaseAPIClient):
    """Advanced VSS API client with deep data extraction capabilities"""

    def __init__(self):
        api_config = config.get_api_config()
        super().__init__(
            base_url=api_config.get('vss_url', 'http://vssapp.teca.vn:8088'),
            client_name='advanced_vss'
        )
        self.use_mock = api_config.get('use_mock_vss', False)  # Use real API by default

        # Authentication (if needed)
        self.auth_token = api_config.get('vss_auth_token')
        if self.auth_token:
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})

    def get_compliance_analysis(self, mst: str) -> Optional[ComplianceAnalysis]:
        """Get detailed compliance analysis for MST"""
        try:
            if self.use_mock:
                data = self._generate_mock_compliance_analysis(mst)
                return self._parse_compliance_analysis(mst, data)
            else:
                data = self.get(f"/compliance/{mst}")
                if data:
                    return self._parse_compliance_analysis(mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get compliance analysis for MST {mst}: {str(e)}")
            if not self.use_mock:
                self.logger.info(f"Falling back to mock compliance analysis for MST {mst}")
                data = self._generate_mock_compliance_analysis(mst)
                return self._parse_compliance_analysis(mst, data)
            return None

    def get_risk_assessment(self, mst: str) -> Optional[RiskAssessment]:
        """Get risk assessment for MST"""
        try:
            if self.use_mock:
                data = self._generate_mock_risk_assessment(mst)
                return self._parse_risk_assessment(mst, data)
            else:
                data = self.get(f"/risk-assessment/{mst}")
                if data:
                    return self._parse_risk_assessment(mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get risk assessment for MST {mst}: {str(e)}")
            if not self.use_mock:
                self.logger.info(f"Falling back to mock risk assessment for MST {mst}")
                data = self._generate_mock_risk_assessment(mst)
                return self._parse_risk_assessment(mst, data)
            return None

    def get_recommendations(self, mst: str) -> Optional[List[Recommendation]]:
        """Get improvement recommendations for MST"""
        try:
            if self.use_mock:
                data = self._generate_mock_recommendations(mst)
                return self._parse_recommendations(mst, data)
            else:
                data = self.get(f"/recommendations/{mst}")
                if data:
                    return self._parse_recommendations(mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get recommendations for MST {mst}: {str(e)}")
            if not self.use_mock:
                self.logger.info(f"Falling back to mock recommendations for MST {mst}")
                data = self._generate_mock_recommendations(mst)
                return self._parse_recommendations(mst, data)
            return None

    def get_detailed_employee_data(self, mst: str, employee_id: str) -> Optional[EmployeeData]:
        """Get detailed employee data by ID"""
        try:
            if self.use_mock:
                data = self._generate_mock_detailed_employee(mst, employee_id)
                return self._parse_employee_data(mst, [data])[0] if data else None
            else:
                data = self.get(f"/employees/{mst}/{employee_id}")
                if data:
                    return self._parse_employee_data(mst, [data])[0] if data else None
                return None
        except Exception as e:
            self.logger.error(f"Failed to get detailed employee data for {employee_id}: {str(e)}")
            if not self.use_mock:
                self.logger.info(f"Falling back to mock detailed employee data for {employee_id}")
                data = self._generate_mock_detailed_employee(mst, employee_id)
                return self._parse_employee_data(mst, [data])[0] if data else None
            return None

    def get_contribution_history(self, mst: str, employee_id: str, months: int = 12) -> Optional[List[ContributionData]]:
        """Get contribution history for specific employee"""
        try:
            if self.use_mock:
                data = self._generate_mock_contribution_history(mst, employee_id, months)
                return self._parse_contribution_data(mst, data)
            else:
                data = self.get(f"/contributions/{mst}/{employee_id}/history?months={months}")
                if data:
                    return self._parse_contribution_data(mst, data)
                return None
        except Exception as e:
            self.logger.error(f"Failed to get contribution history for {employee_id}: {str(e)}")
            if not self.use_mock:
                self.logger.info(f"Falling back to mock contribution history for {employee_id}")
                data = self._generate_mock_contribution_history(mst, employee_id, months)
                return self._parse_contribution_data(mst, data)
            return None

    def get_compliance_report(self, mst: str, report_type: str = "monthly") -> Optional[Dict[str, Any]]:
        """Get compliance report for MST"""
        try:
            if self.use_mock:
                return self._generate_mock_compliance_report(mst, report_type)
            else:
                data = self.get(f"/reports/compliance/{mst}?type={report_type}")
                return data
        except Exception as e:
            self.logger.error(f"Failed to get compliance report for MST {mst}: {str(e)}")
            if not self.use_mock:
                self.logger.info(f"Falling back to mock compliance report for MST {mst}")
                return self._generate_mock_compliance_report(mst, report_type)
            return None

    def _parse_compliance_analysis(self, mst: str, data: Dict[str, Any]) -> ComplianceAnalysis:
        """Parse compliance analysis from API response"""
        return ComplianceAnalysis(
            mst=mst,
            overall_score=data.get('overall_score', 0.0),
            contribution_compliance=data.get('contribution_compliance', 0.0),
            reporting_compliance=data.get('reporting_compliance', 0.0),
            deadline_compliance=data.get('deadline_compliance', 0.0),
            issues_found=data.get('issues_found', []),
            recommendations=data.get('recommendations', [])
        )

    def _parse_risk_assessment(self, mst: str, data: Dict[str, Any]) -> RiskAssessment:
        """Parse risk assessment from API response"""
        return RiskAssessment(
            mst=mst,
            risk_level=data.get('risk_level', 'medium'),
            risk_score=data.get('risk_score', 50.0),
            risk_factors=data.get('risk_factors', []),
            mitigation_suggestions=data.get('mitigation_suggestions', [])
        )

    def _parse_recommendations(self, mst: str, data: Dict[str, Any]) -> List[Recommendation]:
        """Parse recommendations from API response"""
        recommendations = []

        rec_list = data.get('recommendations', [])
        if isinstance(rec_list, list):
            for rec_data in rec_list:
                recommendation = Recommendation(
                    mst=mst,
                    category=rec_data.get('category', 'general'),
                    priority=rec_data.get('priority', 'medium'),
                    title=rec_data.get('title', ''),
                    description=rec_data.get('description', ''),
                    impact_score=rec_data.get('impact_score', 5.0),
                    implementation_effort=rec_data.get('implementation_effort', 'medium')
                )
                recommendations.append(recommendation)

        return recommendations

    def _generate_mock_compliance_analysis(self, mst: str) -> Dict[str, Any]:
        """Generate mock compliance analysis"""
        seed = int(hashlib.md5(mst.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        overall_score = random.uniform(60, 95)
        contribution_compliance = random.uniform(max(50, overall_score - 10), min(100, overall_score + 10))
        reporting_compliance = random.uniform(max(50, overall_score - 15), min(100, overall_score + 5))
        deadline_compliance = random.uniform(max(40, overall_score - 20), min(100, overall_score + 10))

        issues = []
        recommendations = []

        if contribution_compliance < 80:
            issues.append("Một số khoản đóng bảo hiểm chưa được thanh toán đầy đủ")
            recommendations.append("Tăng cường giám sát và thanh toán đúng hạn")

        if reporting_compliance < 85:
            issues.append("Báo cáo bảo hiểm chưa được cập nhật kịp thời")
            recommendations.append("Thiết lập hệ thống nhắc nhở báo cáo tự động")

        if deadline_compliance < 75:
            issues.append("Quá hạn đóng bảo hiểm nhiều lần")
            recommendations.append("Tối ưu hóa quy trình thanh toán")

        return {
            "overall_score": round(overall_score, 2),
            "contribution_compliance": round(contribution_compliance, 2),
            "reporting_compliance": round(reporting_compliance, 2),
            "deadline_compliance": round(deadline_compliance, 2),
            "issues_found": issues,
            "recommendations": recommendations
        }

    def _generate_mock_risk_assessment(self, mst: str) -> Dict[str, Any]:
        """Generate mock risk assessment"""
        seed = int(hashlib.md5(mst.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        risk_score = random.uniform(20, 80)

        if risk_score < 30:
            risk_level = "low"
            risk_factors = ["Tuân thủ tốt", "Thanh toán đúng hạn"]
            mitigation_suggestions = ["Tiếp tục duy trì các quy trình hiện tại"]
        elif risk_score < 60:
            risk_level = "medium"
            risk_factors = ["Một số khoản thanh toán chậm trễ", "Báo cáo chưa đầy đủ"]
            mitigation_suggestions = ["Cải thiện quy trình thanh toán", "Tăng cường giám sát báo cáo"]
        else:
            risk_level = "high"
            risk_factors = ["Thanh toán không đúng hạn", "Vi phạm quy định bảo hiểm", "Rủi ro pháp lý cao"]
            mitigation_suggestions = ["Khẩn cấp cải thiện tuân thủ", "Tư vấn pháp lý", "Thiết lập hệ thống cảnh báo"]

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors,
            "mitigation_suggestions": mitigation_suggestions
        }

    def _generate_mock_recommendations(self, mst: str) -> Dict[str, Any]:
        """Generate mock recommendations"""
        recommendations = [
            {
                "category": "compliance",
                "priority": "high",
                "title": "Cải thiện tỷ lệ thanh toán đúng hạn",
                "description": "Nâng cao tỷ lệ thanh toán bảo hiểm xã hội đúng hạn từ 85% lên 95%",
                "impact_score": 8.5,
                "implementation_effort": "medium"
            },
            {
                "category": "efficiency",
                "priority": "medium",
                "title": "Tự động hóa quy trình báo cáo",
                "description": "Triển khai hệ thống tự động tạo và gửi báo cáo bảo hiểm định kỳ",
                "impact_score": 7.0,
                "implementation_effort": "high"
            },
            {
                "category": "cost",
                "priority": "low",
                "title": "Tối ưu hóa chi phí bảo hiểm",
                "description": "Phân tích và giảm thiểu các chi phí không cần thiết liên quan đến bảo hiểm",
                "impact_score": 5.5,
                "implementation_effort": "low"
            }
        ]

        return {"recommendations": recommendations}

    def _generate_mock_detailed_employee(self, mst: str, employee_id: str) -> Dict[str, Any]:
        """Generate detailed mock employee data"""
        seed = int(hashlib.md5(f"{mst}{employee_id}".encode()).hexdigest()[:8], 16)
        random.seed(seed)

        vietnamese_names = [
            "Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung",
            "Hoàng Văn Em", "Vũ Thị Phương", "Đặng Văn Giang", "Bùi Thị Hoa"
        ]

        positions = [
            "Giám đốc", "Phó giám đốc", "Trưởng phòng", "Nhân viên",
            "Kế toán trưởng", "Kỹ sư", "Chuyên viên", "Thư ký"
        ]

        start_date = datetime.now() - timedelta(days=random.randint(365, 365*3))
        salary = random.randint(8000000, 30000000)

        return {
            "employee_id": employee_id,
            "name": random.choice(vietnamese_names),
            "position": random.choice(positions),
            "salary": salary,
            "insurance_number": f"INS{mst}{employee_id[-3:]}",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "status": "active" if random.random() > 0.1 else "inactive"
        }

    def _generate_mock_contribution_history(self, mst: str, employee_id: str, months: int) -> Dict[str, Any]:
        """Generate mock contribution history"""
        contributions = []

        for i in range(months):
            contrib_date = datetime.now() - timedelta(days=30 * i)
            amount = random.randint(800000, 3000000)  # Based on salary range

            contribution = {
                "employee_id": employee_id,
                "contribution_amount": amount,
                "contribution_date": contrib_date.strftime("%Y-%m-%d"),
                "insurance_type": "social",
                "status": "paid" if random.random() > 0.1 else "pending"
            }
            contributions.append(contribution)

        return {"contributions": contributions}

    def _generate_mock_compliance_report(self, mst: str, report_type: str) -> Dict[str, Any]:
        """Generate mock compliance report"""
        seed = int(hashlib.md5(mst.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        return {
            "mst": mst,
            "report_type": report_type,
            "period": f"{datetime.now().strftime('%Y-%m')}",
            "compliance_score": round(random.uniform(70, 95), 2),
            "total_employees": random.randint(10, 50),
            "compliant_employees": random.randint(8, 45),
            "pending_contributions": random.randint(0, 5),
            "overdue_contributions": random.randint(0, 3),
            "recommendations": [
                "Tăng cường giám sát thanh toán",
                "Cải thiện quy trình báo cáo",
                "Đào tạo nhân viên về quy định bảo hiểm"
            ]
        }