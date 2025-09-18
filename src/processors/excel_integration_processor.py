"""
Excel Integration Processor - Main processor for Excel-based VSS integration
"""
import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from ..core.data_models import ProcessingResult, VSSIntegrationData
from ..processors.vss_processor import VSSIntegrationProcessor
from ..utils.excel_processor import ExcelProcessor
from ..utils.logger import setup_module_logger


class ExcelIntegrationProcessor:
    """Main processor for Excel-based VSS integration workflow"""
    
    def __init__(self, max_workers: int = 4, use_real_apis: bool = True):
        self.logger = setup_module_logger("excel_integration_processor")
        
        # Initialize components
        self.vss_processor = VSSIntegrationProcessor(max_workers=max_workers, use_real_apis=use_real_apis)
        self.excel_processor = ExcelProcessor()
        
        # Configuration
        self.max_workers = max_workers
        self.use_real_apis = use_real_apis
        
        self.logger.info(f"Excel Integration Processor initialized with {max_workers} workers")
    
    def process_excel_file(self, input_file: str, output_dir: str = "data/output") -> Dict[str, Any]:
        """Process complete Excel file workflow"""
        try:
            start_time = time.time()
            self.logger.info(f"Starting Excel processing workflow for: {input_file}")
            
            # Step 1: Validate and load Excel file
            self.logger.info("Step 1: Validating and loading Excel file...")
            workflow_info = self.excel_processor.process_excel_workflow(input_file, output_dir)
            
            msts = workflow_info['msts']
            self.logger.info(f"Loaded {len(msts)} MSTs from Excel file")
            
            # Step 2: Process MSTs through VSS system
            self.logger.info("Step 2: Processing MSTs through VSS system...")
            results = self.vss_processor.process_batch(msts)
            
            # Step 3: Generate Excel reports
            self.logger.info("Step 3: Generating Excel reports...")
            self._generate_excel_reports(results, workflow_info)
            
            # Step 4: Create summary
            processing_time = time.time() - start_time
            summary = self._create_processing_summary(workflow_info, results, processing_time)
            
            self.logger.info(f"Excel processing workflow completed in {processing_time:.2f}s")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in Excel processing workflow: {str(e)}")
            raise
    
    def _generate_excel_reports(self, results: List[ProcessingResult], workflow_info: Dict[str, Any]):
        """Generate Excel reports from processing results"""
        try:
            # Generate summary report
            self.excel_processor.output_generator.generate_summary_report(
                results, 
                workflow_info['summary_file']
            )
            
            # Generate detailed report if we have integration data
            if self.use_real_apis:
                # Try to get detailed integration data
                integration_data = self._extract_integration_data(results)
                if integration_data:
                    self.excel_processor.output_generator.generate_detailed_report(
                        integration_data,
                        workflow_info['detailed_file']
                    )
            
            self.logger.info("Excel reports generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating Excel reports: {str(e)}")
            raise
    
    def _extract_integration_data(self, results: List[ProcessingResult]) -> List[VSSIntegrationData]:
        """Extract integration data from results (placeholder for now)"""
        # This would need to be implemented based on how VSSIntegrationData
        # is stored in ProcessingResult or retrieved separately
        return []
    
    def _create_processing_summary(self, workflow_info: Dict[str, Any], 
                                 results: List[ProcessingResult], 
                                 processing_time: float) -> Dict[str, Any]:
        """Create processing summary"""
        successful = len([r for r in results if r.success])
        failed = len([r for r in results if not r.success])
        avg_confidence = sum(r.confidence_score for r in results if r.success) / successful if successful > 0 else 0
        
        return {
            'workflow_info': workflow_info,
            'processing_results': {
                'total_processed': len(results),
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / len(results) * 100) if results else 0,
                'average_confidence': round(avg_confidence, 3),
                'processing_time': round(processing_time, 2),
                'processing_rate': round(len(results) / processing_time, 2) if processing_time > 0 else 0
            },
            'data_quality_distribution': {
                'high': len([r for r in results if r.data_quality == 'HIGH']),
                'medium': len([r for r in results if r.data_quality == 'MEDIUM']),
                'low': len([r for r in results if r.data_quality == 'LOW'])
            },
            'source_distribution': {
                'real_api': len([r for r in results if r.source == 'real_api']),
                'generated': len([r for r in results if r.source == 'generated'])
            },
            'output_files': {
                'summary_report': workflow_info['summary_file'],
                'detailed_report': workflow_info.get('detailed_file', 'Not generated'),
                'output_directory': workflow_info['output_dir']
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def create_input_template(self, template_path: str = "data/templates/mst_input_template.xlsx"):
        """Create input template file"""
        try:
            # Ensure template directory exists
            Path(template_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create template
            self.excel_processor.output_generator.create_template_file(template_path)
            
            self.logger.info(f"Input template created: {template_path}")
            return template_path
            
        except Exception as e:
            self.logger.error(f"Error creating input template: {str(e)}")
            raise
    
    def validate_input_file(self, file_path: str) -> Dict[str, Any]:
        """Validate input Excel file"""
        return self.excel_processor.input_processor.validate_excel_file(file_path)
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get current processing metrics"""
        return self.vss_processor.get_metrics().__dict__
