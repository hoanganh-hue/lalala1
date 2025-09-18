"""
Excel input/output processor for VSS Integration System
"""
import pandas as pd
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from ..core.data_models import ProcessingResult, EnterpriseData, EmployeeData, ContributionData, VSSIntegrationData
from ..utils.logger import setup_module_logger
from ..utils.mst import normalize_mst


class ExcelInputProcessor:
    """Process Excel input files containing MST data"""
    
    def __init__(self):
        self.logger = setup_module_logger("excel_input_processor")
        
        # Supported column names for MST
        self.mst_column_names = [
            'Dãy số 10 chữ số',
            'MST',
            'Mã số thuế',
            'Tax Code',
            'Tax ID',
            'Mã thuế',
            'Số thuế'
        ]
    
    def load_mst_from_excel(self, file_path: str) -> List[str]:
        """Load MST list from Excel file"""
        try:
            self.logger.info(f"Loading MST from Excel file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Find MST column
            mst_column = self._find_mst_column(df)
            if not mst_column:
                raise ValueError(f"No MST column found. Supported columns: {self.mst_column_names}")
            
            # Extract MSTs and normalize (support 9–13 digits, pad 9 to 10)
            msts = df[mst_column].astype(str).tolist()
            cleaned_msts = []
            for mst in msts:
                normalized = normalize_mst(str(mst).strip())
                if normalized:
                    cleaned_msts.append(normalized)
                else:
                    self.logger.warning(f"Invalid MST format: {mst}")
            
            self.logger.info(f"Successfully loaded {len(cleaned_msts)} MSTs from {file_path}")
            return cleaned_msts
            
        except Exception as e:
            self.logger.error(f"Error loading MST from Excel: {str(e)}")
            raise
    
    def _find_mst_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find MST column in DataFrame"""
        for col in df.columns:
            if any(name.lower() in col.lower() for name in self.mst_column_names):
                return col
        
        # If no exact match, try first column
        if len(df.columns) > 0:
            self.logger.warning(f"No MST column found, using first column: {df.columns[0]}")
            return df.columns[0]
        
        return None
    
    def validate_excel_file(self, file_path: str) -> Dict[str, Any]:
        """Validate Excel file structure and content"""
        try:
            df = pd.read_excel(file_path)
            
            validation_result = {
                'valid': True,
                'total_rows': len(df),
                'columns': df.columns.tolist(),
                'mst_column': None,
                'mst_count': 0,
                'errors': []
            }
            
            # Find MST column
            mst_column = self._find_mst_column(df)
            if mst_column:
                validation_result['mst_column'] = mst_column
                
                # Count valid MSTs using normalization
                msts = df[mst_column].astype(str).tolist()
                valid_msts = [normalize_mst(m) for m in msts]
                validation_result['mst_count'] = len([v for v in valid_msts if v])
                
                if len(valid_msts) == 0:
                    validation_result['valid'] = False
                    validation_result['errors'].append("No valid MSTs found")
            else:
                validation_result['valid'] = False
                validation_result['errors'].append("No MST column found")
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'total_rows': 0,
                'columns': [],
                'mst_column': None,
                'mst_count': 0,
                'errors': [str(e)]
            }


class ExcelOutputGenerator:
    """Generate Excel output files with processed results"""
    
    def __init__(self):
        self.logger = setup_module_logger("excel_output_generator")
    
    def generate_summary_report(self, results: List[ProcessingResult], output_path: str):
        """Generate summary report Excel file"""
        try:
            self.logger.info(f"Generating summary report: {output_path}")
            
            # Create summary data
            summary_data = self._create_summary_data(results)
            
            # Create detailed results data
            detailed_data = self._create_detailed_data(results)
            
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Summary sheet
                summary_df = pd.DataFrame([summary_data])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Detailed results sheet
                detailed_df = pd.DataFrame(detailed_data)
                detailed_df.to_excel(writer, sheet_name='Detailed Results', index=False)
                
                # Statistics sheet
                stats_df = self._create_statistics_data(results)
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            self.logger.info(f"Summary report generated successfully: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {str(e)}")
            raise
    
    def generate_detailed_report(self, integration_data: List[VSSIntegrationData], output_path: str):
        """Generate detailed report with all data"""
        try:
            self.logger.info(f"Generating detailed report: {output_path}")
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Enterprise data sheet
                enterprise_data = []
                for data in integration_data:
                    enterprise_data.append({
                        'MST': data.enterprise.mst,
                        'Company Name': data.enterprise.company_name,
                        'Address': data.enterprise.address,
                        'Phone': data.enterprise.phone,
                        'Email': data.enterprise.email,
                        'Business Type': data.enterprise.business_type,
                        'Revenue': data.enterprise.revenue,
                        'Bank Account': data.enterprise.bank_account,
                        'Registration Date': data.enterprise.registration_date,
                        'Compliance Score': data.compliance_score,
                        'Risk Level': data.risk_level
                    })
                
                enterprise_df = pd.DataFrame(enterprise_data)
                enterprise_df.to_excel(writer, sheet_name='Enterprise Data', index=False)
                
                # Employee data sheet
                employee_data = []
                for data in integration_data:
                    for emp in data.employees:
                        employee_data.append({
                            'MST': emp.mst,
                            'Employee ID': emp.employee_id,
                            'Name': emp.name,
                            'Position': emp.position,
                            'Salary': emp.salary,
                            'Insurance Number': emp.insurance_number,
                            'Start Date': emp.start_date,
                            'Status': emp.status
                        })
                
                employee_df = pd.DataFrame(employee_data)
                employee_df.to_excel(writer, sheet_name='Employee Data', index=False)
                
                # Contribution data sheet
                contribution_data = []
                for data in integration_data:
                    for contrib in data.contributions:
                        contribution_data.append({
                            'MST': contrib.mst,
                            'Employee ID': contrib.employee_id,
                            'Contribution Amount': contrib.contribution_amount,
                            'Contribution Date': contrib.contribution_date,
                            'Insurance Type': contrib.insurance_type,
                            'Status': contrib.status
                        })
                
                contribution_df = pd.DataFrame(contribution_data)
                contribution_df.to_excel(writer, sheet_name='Contribution Data', index=False)
            
            self.logger.info(f"Detailed report generated successfully: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating detailed report: {str(e)}")
            raise
    
    def _create_summary_data(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Create summary data for Excel"""
        total = len(results)
        successful = len([r for r in results if r.success])
        failed = total - successful
        avg_confidence = sum(r.confidence_score for r in results if r.success) / successful if successful > 0 else 0
        avg_processing_time = sum(r.processing_time for r in results) / total if total > 0 else 0
        
        return {
            'Total MSTs': total,
            'Successful': successful,
            'Failed': failed,
            'Success Rate (%)': (successful / total * 100) if total > 0 else 0,
            'Average Confidence': round(avg_confidence, 3),
            'Average Processing Time (s)': round(avg_processing_time, 2),
            'High Quality Data': len([r for r in results if r.data_quality == 'HIGH']),
            'Medium Quality Data': len([r for r in results if r.data_quality == 'MEDIUM']),
            'Low Quality Data': len([r for r in results if r.data_quality == 'LOW']),
            'Real API Data': len([r for r in results if r.source == 'real_api']),
            'Generated Data': len([r for r in results if r.source == 'generated']),
            'Report Generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _create_detailed_data(self, results: List[ProcessingResult]) -> List[Dict[str, Any]]:
        """Create detailed results data for Excel"""
        detailed_data = []
        for i, result in enumerate(results, 1):
            detailed_data.append({
                'No': i,
                'MST': result.mst,
                'Success': 'Yes' if result.success else 'No',
                'Confidence Score': round(result.confidence_score, 3),
                'Data Quality': result.data_quality,
                'Source': result.source,
                'Processing Time (s)': round(result.processing_time, 2),
                'Error': result.error if result.error else '',
                'Retry Count': result.retry_count,
                'Timestamp': result.timestamp
            })
        return detailed_data
    
    def _create_statistics_data(self, results: List[ProcessingResult]) -> pd.DataFrame:
        """Create statistics data for Excel"""
        stats_data = []
        
        # Data quality distribution
        quality_counts = {}
        for result in results:
            quality = result.data_quality
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        for quality, count in quality_counts.items():
            stats_data.append({
                'Metric': f'Data Quality - {quality}',
                'Count': count,
                'Percentage': round(count / len(results) * 100, 2)
            })
        
        # Source distribution
        source_counts = {}
        for result in results:
            source = result.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in source_counts.items():
            stats_data.append({
                'Metric': f'Data Source - {source}',
                'Count': count,
                'Percentage': round(count / len(results) * 100, 2)
            })
        
        # Processing time statistics
        processing_times = [r.processing_time for r in results if r.success]
        if processing_times:
            stats_data.extend([
                {
                    'Metric': 'Min Processing Time (s)',
                    'Count': round(min(processing_times), 2),
                    'Percentage': 0
                },
                {
                    'Metric': 'Max Processing Time (s)',
                    'Count': round(max(processing_times), 2),
                    'Percentage': 0
                },
                {
                    'Metric': 'Avg Processing Time (s)',
                    'Count': round(sum(processing_times) / len(processing_times), 2),
                    'Percentage': 0
                }
            ])
        
        return pd.DataFrame(stats_data)
    
    def create_template_file(self, template_path: str):
        """Create Excel template file for input"""
        try:
            self.logger.info(f"Creating template file: {template_path}")
            
            # Create sample data
            sample_data = {
                'Dãy số 10 chữ số': [
                    '110198560',
                    '110197454', 
                    '110198088',
                    '110198232',
                    '110198433'
                ],
                'Ghi chú': [
                    'MST mẫu 1',
                    'MST mẫu 2',
                    'MST mẫu 3',
                    'MST mẫu 4',
                    'MST mẫu 5'
                ]
            }
            
            df = pd.DataFrame(sample_data)
            df.to_excel(template_path, index=False, sheet_name='MST List')
            
            self.logger.info(f"Template file created successfully: {template_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating template file: {str(e)}")
            raise


class ExcelProcessor:
    """Main Excel processor combining input and output functionality"""
    
    def __init__(self):
        self.input_processor = ExcelInputProcessor()
        self.output_generator = ExcelOutputGenerator()
        self.logger = setup_module_logger("excel_processor")
    
    def process_excel_workflow(self, input_file: str, output_dir: str = "data/output") -> Dict[str, str]:
        """Complete Excel processing workflow"""
        try:
            # Validate input file
            validation = self.input_processor.validate_excel_file(input_file)
            if not validation['valid']:
                raise ValueError(f"Invalid Excel file: {validation['errors']}")
            
            # Load MSTs
            msts = self.input_processor.load_mst_from_excel(input_file)
            if not msts:
                raise ValueError("No valid MSTs found in input file")
            
            self.logger.info(f"Processing {len(msts)} MSTs from Excel file")
            
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate output file paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = os.path.join(output_dir, f"vss_summary_report_{timestamp}.xlsx")
            detailed_file = os.path.join(output_dir, f"vss_detailed_report_{timestamp}.xlsx")
            
            return {
                'input_file': input_file,
                'mst_count': len(msts),
                'msts': msts,
                'summary_file': summary_file,
                'detailed_file': detailed_file,
                'output_dir': output_dir
            }
            
        except Exception as e:
            self.logger.error(f"Error in Excel workflow: {str(e)}")
            raise
