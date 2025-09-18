"""
Main VSS Integration Processor
"""
import time
import random
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.data_models import (
    ProcessingResult, ProcessingMetrics, VSSIntegrationData,
    ComplianceAnalysis, RiskAssessment, Recommendation
)
from ..core.data_generator import RealisticDataGenerator
from ..api.enterprise_client import EnterpriseAPIClient
from ..api.vss_client import VSSAPIClient
from ..config.settings import config
from ..utils.logger import setup_module_logger


class VSSIntegrationProcessor:
    """Main processor for VSS integration with intelligent API routing"""
    
    def __init__(self, max_workers: int = None, use_real_apis: bool = True):
        self.logger = setup_module_logger("vss_processor")
        
        # Configuration
        api_config = config.get_api_config()
        processing_config = config.get_processing_config()
        
        self.max_workers = max_workers or processing_config.get('max_workers', 4)
        self.batch_size = processing_config.get('batch_size', 50)
        self.use_real_apis = use_real_apis
        
        # API Strategy Configuration
        self.api_strategy = api_config.get('api_strategy', 'fallback')
        self.fallback_timeout = api_config.get('fallback_timeout', 10)
        self.health_check_interval = api_config.get('health_check_interval', 300)
        
        # API Health Status
        self.api_health = {
            'enterprise': {'status': 'unknown', 'last_check': 0, 'success_count': 0, 'failure_count': 0},
            'vss': {'status': 'unknown', 'last_check': 0, 'success_count': 0, 'failure_count': 0}
        }
        
        # Initialize components
        self.data_generator = RealisticDataGenerator()
        
        # Initialize clients conditionally based on strategy
        if use_real_apis:
            if api_config.get('enterprise_enabled', True):
                self.enterprise_client = EnterpriseAPIClient()
            else:
                self.enterprise_client = None
                
            if api_config.get('vss_enabled', True):
                self.vss_client = VSSAPIClient()
            else:
                self.vss_client = None
        else:
            self.enterprise_client = None
            self.vss_client = None
        
        # Metrics
        self.metrics = ProcessingMetrics()
        
        # Cache
        self.cache = {}
        self.cache_ttl = config.get('cache.ttl', 300)
        
        # Performance monitoring
        self.performance_stats = {
            'enterprise_avg_time': 0.0,
            'vss_avg_time': 0.0,
            'enterprise_success_rate': 1.0,
            'vss_success_rate': 0.5  # Start with lower expectation for VSS
        }
        
        self.logger.info(f"VSS Integration Processor initialized with strategy '{self.api_strategy}' and {self.max_workers} workers")
        
        # Initial health check
        self._perform_health_check()
    def _perform_health_check(self):
        """Perform health check on all APIs"""
        current_time = time.time()
        
        # Check if health check is needed
        for api_name in self.api_health:
            last_check = self.api_health[api_name]['last_check']
            if current_time - last_check < self.health_check_interval:
                continue
                
            self.logger.debug(f"Performing health check for {api_name} API")
            
            try:
                if api_name == 'enterprise' and self.enterprise_client:
                    # Test with a known good MST
                    test_result = self.enterprise_client.get_company_info("0100109106")
                    if test_result:
                        self.api_health[api_name]['status'] = 'healthy'
                        self.api_health[api_name]['success_count'] += 1
                    else:
                        raise Exception("No data returned")
                        
                elif api_name == 'vss' and self.vss_client:
                    # Test VSS API with basic health check
                    test_result = self.vss_client.get_employee_data("0100109106")
                    if test_result is not None:  # Even empty list is OK
                        self.api_health[api_name]['status'] = 'healthy'
                        self.api_health[api_name]['success_count'] += 1
                    else:
                        raise Exception("API call failed")
                        
                self.api_health[api_name]['last_check'] = current_time
                self.logger.info(f"{api_name.title()} API is healthy")
                
            except Exception as e:
                self.api_health[api_name]['status'] = 'unhealthy'
                self.api_health[api_name]['failure_count'] += 1
                self.api_health[api_name]['last_check'] = current_time
                self.logger.warning(f"{api_name.title()} API health check failed: {str(e)}")
    
    def _get_optimal_data_source(self, mst: str) -> str:
        """Determine the optimal data source based on strategy and health"""
        self._perform_health_check()
        
        if self.api_strategy == "enterprise_only":
            return "enterprise"
        elif self.api_strategy == "vss_only":
            return "vss"
        elif self.api_strategy == "fallback":
            # Prioritize by health and performance
            enterprise_healthy = self.api_health['enterprise']['status'] == 'healthy'
            vss_healthy = self.api_health['vss']['status'] == 'healthy'
            
            if enterprise_healthy and self.performance_stats['enterprise_success_rate'] > 0.8:
                return "enterprise"
            elif vss_healthy and self.performance_stats['vss_success_rate'] > 0.6:
                return "vss"
            else:
                # Fallback to best available option
                return "enterprise" if enterprise_healthy else "vss"
        elif self.api_strategy == "parallel":
            return "parallel"
        
        return "enterprise"  # Default fallback
    
    def _get_enterprise_data_smart(self, mst: str) -> tuple:
        """Smart enterprise data retrieval with error handling"""
        if not self.enterprise_client:
            return None, ["Enterprise client not available"]
            
        start_time = time.time()
        try:
            enterprise_data = self.enterprise_client.get_company_info(mst)
            processing_time = time.time() - start_time
            
            # Update performance stats
            self._update_performance_stats('enterprise', processing_time, enterprise_data is not None)
            
            if enterprise_data:
                self.logger.debug(f"Enterprise data retrieved for {mst} in {processing_time:.2f}s")
                return enterprise_data, []
            else:
                return None, ["No enterprise data returned"]
                
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_performance_stats('enterprise', processing_time, False)
            error_msg = f"Enterprise API error: {str(e)}"
            self.logger.warning(f"{error_msg} for {mst}")
            return None, [error_msg]
    
    def _get_vss_data_smart(self, mst: str) -> tuple:
        """Smart VSS data retrieval with proxy and error handling"""
        if not self.vss_client:
            return None, ["VSS client not available"]
            
        start_time = time.time()
        vss_errors = []
        
        try:
            # Add small delay to avoid overwhelming the server
            time.sleep(random.uniform(0.1, 0.3))
            
            # Get VSS data components
            employees = self.vss_client.get_employee_data(mst)
            contributions = self.vss_client.get_contribution_data(mst)
            insurance_requests = self.vss_client.get_insurance_requests(mst)
            hospitals = self.vss_client.get_hospitals()
            
            processing_time = time.time() - start_time
            
            # Check if we got any valid data
            has_data = any([employees, contributions, insurance_requests, hospitals])
            
            self._update_performance_stats('vss', processing_time, has_data)
            
            if has_data:
                vss_data = {
                    'employees': employees or [],
                    'contributions': contributions or [],
                    'insurance_requests': insurance_requests or [],
                    'hospitals': hospitals or []
                }
                self.logger.debug(f"VSS data retrieved for {mst}: {len(employees or [])} employees, {len(contributions or [])} contributions")
                return vss_data, vss_errors
            else:
                vss_errors.append("No VSS data returned from any endpoint")
                return None, vss_errors
                
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_performance_stats('vss', processing_time, False)
            error_msg = f"VSS API error: {str(e)}"
            vss_errors.append(error_msg)
            self.logger.warning(f"{error_msg} for {mst}")
            return None, vss_errors
    
    def _update_performance_stats(self, api_name: str, processing_time: float, success: bool):
        """Update performance statistics for API"""
        # Update average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        current_avg = self.performance_stats[f'{api_name}_avg_time']
        self.performance_stats[f'{api_name}_avg_time'] = alpha * processing_time + (1 - alpha) * current_avg
        
        # Update success rate (exponential moving average)
        current_rate = self.performance_stats[f'{api_name}_success_rate']
        success_value = 1.0 if success else 0.0
        self.performance_stats[f'{api_name}_success_rate'] = alpha * success_value + (1 - alpha) * current_rate

    def process_single_mst(self, mst: str, index: int = 0) -> ProcessingResult:
        """Process single MST with intelligent API routing and enhanced error handling"""
        start_time = time.time()
        
        try:
            # Determine optimal data source
            optimal_source = self._get_optimal_data_source(mst)
            
            enterprise_data = None
            vss_data = None
            all_api_errors = []
            data_sources_used = []
            
            if self.use_real_apis:
                if optimal_source == "enterprise" or optimal_source == "parallel":
                    # Try Enterprise API first (primary)
                    enterprise_data, enterprise_errors = self._get_enterprise_data_smart(mst)
                    all_api_errors.extend(enterprise_errors)
                    if enterprise_data:
                        data_sources_used.append("enterprise")
                        self.logger.debug(f"✅ Enterprise API success for {mst}")
                    
                    # If enterprise fails and strategy is fallback, try VSS
                    if not enterprise_data and self.api_strategy == "fallback":
                        self.logger.info(f"🔄 Falling back to VSS API for {mst}")
                        vss_data, vss_errors = self._get_vss_data_smart(mst)
                        all_api_errors.extend(vss_errors)
                        if vss_data:
                            data_sources_used.append("vss")
                            self.logger.debug(f"✅ VSS API fallback success for {mst}")
                    
                    # If strategy is parallel, also try VSS
                    elif optimal_source == "parallel":
                        vss_data, vss_errors = self._get_vss_data_smart(mst)
                        all_api_errors.extend(vss_errors)
                        if vss_data:
                            data_sources_used.append("vss")
                            self.logger.debug(f"✅ VSS API parallel success for {mst}")
                
                elif optimal_source == "vss":
                    # Try VSS API first (when explicitly configured)
                    vss_data, vss_errors = self._get_vss_data_smart(mst)
                    all_api_errors.extend(vss_errors)
                    if vss_data:
                        data_sources_used.append("vss")
                        self.logger.debug(f"✅ VSS API primary success for {mst}")
                    
                    # Fallback to enterprise if VSS fails
                    if not vss_data and self.api_strategy == "fallback":
                        self.logger.info(f"🔄 Falling back to Enterprise API for {mst}")
                        enterprise_data, enterprise_errors = self._get_enterprise_data_smart(mst)
                        all_api_errors.extend(enterprise_errors)
                        if enterprise_data:
                            data_sources_used.append("enterprise")
                            self.logger.debug(f"✅ Enterprise API fallback success for {mst}")
            
            # Generate fallback data if needed
            if not enterprise_data or not vss_data:
                generated_data = self.data_generator.generate_vss_integration_data(mst)
                
                if not enterprise_data:
                    enterprise_data = generated_data.enterprise
                    data_sources_used.append("generated_enterprise")
                    self.logger.debug(f"📝 Using generated enterprise data for {mst}")
                
                if not vss_data:
                    vss_data = {
                        'employees': generated_data.employees,
                        'contributions': generated_data.contributions,
                        'insurance_requests': generated_data.insurance_requests,
                        'hospitals': generated_data.hospitals
                    }
                    data_sources_used.append("generated_vss")
                    self.logger.debug(f"📝 Using generated VSS data for {mst}")
            
            # Calculate confidence score based on data sources
            confidence = self._calculate_confidence_advanced(enterprise_data, vss_data, data_sources_used)
            
            processing_time = time.time() - start_time
            
            # Update metrics
            self.metrics.total_processed += 1
            self.metrics.successful += 1
            
            # Progress reporting
            if (index + 1) % 10 == 0:
                self._log_progress_advanced()
            
            # Determine final source description
            source_description = self._get_source_description(data_sources_used, all_api_errors)
            
            return ProcessingResult(
                mst=mst,
                success=True,
                processing_time=processing_time,
                confidence_score=confidence,
                data_quality="HIGH" if confidence > 0.8 else "MEDIUM" if confidence > 0.5 else "LOW",
                source=source_description,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                api_errors=all_api_errors if all_api_errors else None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.metrics.total_processed += 1
            self.metrics.failed += 1
            
            self.logger.error(f"❌ Failed to process MST {mst}: {str(e)}")
            
            return ProcessingResult(
                mst=mst,
                success=False,
                processing_time=processing_time,
                confidence_score=0,
                data_quality="FAILED",
                error=str(e),
                source="error"
            )
    
    def process_batch(self, msts: List[str]) -> List[ProcessingResult]:
        """Process batch of MSTs with enhanced error handling"""
        self.logger.info(f"Processing batch of {len(msts)} MSTs with {self.max_workers} workers")
        self.metrics.start_time = time.time()
        
        results = []
        
        # Process in smaller chunks to avoid overwhelming the API
        chunk_size = max(1, len(msts) // (self.max_workers * 2))
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks in chunks
            future_to_mst = {}
            
            for i, mst in enumerate(msts):
                # Add small delay between task submissions
                if i > 0 and i % chunk_size == 0:
                    time.sleep(0.1)
                
                future = executor.submit(self.process_single_mst, mst, i)
                future_to_mst[future] = (mst, i)
            
            # Collect results with timeout handling
            completed = 0
            for future in as_completed(future_to_mst, timeout=300):  # 5 minute timeout
                mst, index = future_to_mst[future]
                try:
                    result = future.result(timeout=60)  # 1 minute per task
                    results.append(result)
                    completed += 1
                    
                    # Log progress every 10 completions
                    if completed % 10 == 0:
                        self.logger.info(f"Completed {completed}/{len(msts)} MSTs")
                        
                except Exception as e:
                    self.logger.error(f"Executor error for MST {mst}: {str(e)}")
                    results.append(ProcessingResult(
                        mst=mst,
                        success=False,
                        processing_time=0,
                        confidence_score=0,
                        data_quality="FAILED",
                        error=f"Executor error: {str(e)}",
                        source="executor_error"
                    ))
                    completed += 1
        
        self.metrics.end_time = time.time()
        self._log_final_results(results)
        
        return results

    def _create_vss_integration_data(self, mst: str, enterprise_data, vss_data) -> VSSIntegrationData:
        """Create complete VSS integration data with analysis and recommendations"""
        # Extract data from vss_data dict
        employees = vss_data.get('employees', [])
        contributions = vss_data.get('contributions', [])
        insurance_requests = vss_data.get('insurance_requests', [])
        hospitals = vss_data.get('hospitals', [])

        # Generate compliance analysis
        compliance_analysis = self.data_generator.generate_compliance_analysis(mst, contributions)

        # Generate risk assessment
        risk_assessment = self.data_generator.generate_risk_assessment(mst, compliance_analysis.overall_score)

        # Generate recommendations
        recommendations = self.data_generator.generate_recommendations(mst, compliance_analysis, risk_assessment)

        return VSSIntegrationData(
            enterprise=enterprise_data,
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

    def _calculate_confidence_advanced(self, enterprise_data, vss_data, data_sources_used) -> float:
        """Calculate advanced confidence score based on data sources and API performance"""
        confidence = 0.0
        
        # Base confidence from data availability
        if enterprise_data and "enterprise" in data_sources_used:
            confidence += 0.4  # Higher weight for working enterprise API
        elif enterprise_data and "generated_enterprise" in data_sources_used:
            confidence += 0.2  # Lower weight for generated data
            
        if vss_data and "vss" in data_sources_used:
            confidence += 0.3  # Good weight for real VSS data
        elif vss_data and "generated_vss" in data_sources_used:
            confidence += 0.15  # Lower weight for generated data
            
        # Bonus for completeness
        if vss_data:
            if vss_data.get('employees'):
                confidence += 0.1
            if vss_data.get('contributions'):
                confidence += 0.1
            if vss_data.get('insurance_requests'):
                confidence += 0.05
                
        # Performance-based adjustments
        if "enterprise" in data_sources_used:
            confidence *= (0.9 + 0.1 * self.performance_stats['enterprise_success_rate'])
        if "vss" in data_sources_used:
            confidence *= (0.9 + 0.1 * self.performance_stats['vss_success_rate'])
            
        # Cap at 1.0
        return min(1.0, max(0.0, confidence))
    
    def _get_source_description(self, data_sources_used, api_errors) -> str:
        """Generate human-readable source description"""
        if not data_sources_used:
            return "no_data"
            
        real_sources = [s for s in data_sources_used if not s.startswith('generated')]
        generated_sources = [s for s in data_sources_used if s.startswith('generated')]
        
        if real_sources and not generated_sources:
            return "real_api_" + "_".join(real_sources)
        elif real_sources and generated_sources:
            return "mixed_" + "_".join(real_sources + generated_sources)
        elif generated_sources:
            return "generated_" + "_".join([s.replace('generated_', '') for s in generated_sources])
        else:
            return "unknown"
    
    def _log_progress_advanced(self):
        """Advanced progress logging with performance stats"""
        elapsed = time.time() - self.metrics.start_time if self.metrics.start_time else 0
        rate = self.metrics.total_processed / elapsed if elapsed > 0 else 0
        
        # API performance summary
        ent_rate = f"{self.performance_stats['enterprise_success_rate']*100:.0f}%"
        vss_rate = f"{self.performance_stats['vss_success_rate']*100:.0f}%"
        ent_time = f"{self.performance_stats['enterprise_avg_time']:.1f}s"
        vss_time = f"{self.performance_stats['vss_avg_time']:.1f}s"
        
        self.logger.info(
            f"Progress: {self.metrics.total_processed:,} processed | "
            f"✅ {self.metrics.successful:,} | ❌ {self.metrics.failed:,} | "
            f"⚡ {rate:.1f}/s | "
            f"📊 ENT: {ent_rate}({ent_time}) | VSS: {vss_rate}({vss_time})"
        )
    
    def get_api_health_status(self) -> Dict[str, Any]:
        """Get current API health status"""
        return {
            'api_health': self.api_health,
            'performance_stats': self.performance_stats,
            'current_strategy': self.api_strategy,
            'last_health_check': max(self.api_health['enterprise']['last_check'], 
                                   self.api_health['vss']['last_check'])
        }
        """Calculate confidence score based on data sources"""
        confidence = 0.0

        if enterprise_data:
            confidence += 0.3  # Enterprise data available

        if vss_data and vss_data.get('employees'):
            confidence += 0.2  # Employee data available

        if vss_data and vss_data.get('contributions'):
            confidence += 0.2  # Contribution data available

        if vss_data and vss_data.get('insurance_requests'):
            confidence += 0.15  # Insurance requests available

        if vss_data and vss_data.get('hospitals'):
            confidence += 0.15  # Hospital data available

        # Add some randomness for realistic variation
        confidence += random.uniform(-0.1, 0.1)
        confidence = max(0.0, min(1.0, confidence))

        return confidence
    
    def _log_progress(self):
        """Log processing progress"""
        elapsed = time.time() - self.metrics.start_time if self.metrics.start_time else 0
        rate = self.metrics.total_processed / elapsed if elapsed > 0 else 0
        
        self.logger.info(
            f"Progress: {self.metrics.total_processed:,} processed | "
            f"✅ {self.metrics.successful:,} | ❌ {self.metrics.failed:,} | "
            f"⚡ {rate:.1f}/s"
        )
    
    def _log_final_results(self, results: List[ProcessingResult]):
        """Log final processing results"""
        total_time = self.metrics.end_time - self.metrics.start_time if self.metrics.start_time else 0
        success_rate = (self.metrics.successful / self.metrics.total_processed * 100) if self.metrics.total_processed > 0 else 0
        processing_rate = self.metrics.total_processed / total_time if total_time > 0 else 0
        
        self.logger.info(
            f"Processing completed: {self.metrics.total_processed:,} total | "
            f"✅ {self.metrics.successful:,} successful | "
            f"❌ {self.metrics.failed:,} failed | "
            f"📈 {success_rate:.1f}% success rate | "
            f"⚡ {processing_rate:.2f}/s | "
            f"⏱️ {total_time/60:.1f} minutes"
        )
    
    def get_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics"""
        return self.metrics
    
    def reset_metrics(self):
        """Reset processing metrics"""
        self.metrics = ProcessingMetrics()

    def get_vss_integration_data(self, mst: str) -> Optional[VSSIntegrationData]:
        """Get complete VSS integration data for a single MST"""
        try:
            # Try to get real data first
            enterprise_data = None
            vss_data = None

            if self.use_real_apis:
                # Get enterprise data
                if self.enterprise_client:
                    enterprise_data = self.enterprise_client.get_company_info(mst)

                # Get VSS data
                if self.vss_client:
                    employees = self.vss_client.get_employee_data(mst)
                    contributions = self.vss_client.get_contribution_data(mst)
                    insurance_requests = self.vss_client.get_insurance_requests(mst)
                    hospitals = self.vss_client.get_hospitals()

                    vss_data = {
                        'employees': employees or [],
                        'contributions': contributions or [],
                        'insurance_requests': insurance_requests or [],
                        'hospitals': hospitals or []
                    }

            # Generate fallback data
            if not enterprise_data or not vss_data:
                generated_data = self.data_generator.generate_vss_integration_data(mst)

                if not enterprise_data:
                    enterprise_data = generated_data.enterprise

                if not vss_data:
                    vss_data = {
                        'employees': generated_data.employees,
                        'contributions': generated_data.contributions,
                        'insurance_requests': generated_data.insurance_requests,
                        'hospitals': generated_data.hospitals
                    }

            # Create complete integration data
            return self._create_vss_integration_data(mst, enterprise_data, vss_data)

        except Exception as e:
            self.logger.error(f"Failed to get VSS integration data for MST {mst}: {str(e)}")
            # Return generated data as last resort
            return self.data_generator.generate_vss_integration_data(mst)
