"""
Enterprise API client for retrieving company information
"""
from typing import Dict, Any, Optional
from .base_client import BaseAPIClient
from ..core.data_models import EnterpriseData
from ..config.settings import config
from ..utils.mst import normalize_mst


class EnterpriseAPIClient(BaseAPIClient):
    """Client for Enterprise API"""
    
    def __init__(self):
        api_config = config.get_api_config()
        super().__init__(
            base_url=api_config.get('enterprise_url', 'https://thongtindoanhnghiep.co/api/company'),
            client_name='enterprise'
        )
    
    def get_company_info(self, mst: str) -> Optional[EnterpriseData]:
        """Get company information by MST"""
        try:
            norm_mst = normalize_mst(mst)
            if not norm_mst:
                self.logger.warning(f"Invalid MST provided: {mst}")
                return None
            data = self.get(f"/{norm_mst}")
            if data:
                return self._parse_enterprise_data(norm_mst, data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get company info for MST {mst}: {str(e)}")
            return None
    
    def _parse_enterprise_data(self, mst: str, data: Dict[str, Any]) -> EnterpriseData:
        """Parse enterprise data from API response"""
        return EnterpriseData(
            mst=mst,
            company_name=data.get('Title', ''),
            address=data.get('Address', ''),
            phone=data.get('Phone', ''),
            email=data.get('Email', ''),
            website=data.get('Website'),
            business_type=data.get('BusinessType', ''),
            business_category=data.get('BusinessCategory'),
            revenue=data.get('Revenue'),
            bank_account=data.get('BankAccount'),
            registration_date=data.get('RegistrationDate'),
            expiration_date=data.get('ExpirationDate')
        )
