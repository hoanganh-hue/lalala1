#!/usr/bin/env python3
"""
VSS Performance Benchmark Script
Comprehensive performance testing and evaluation tool

Features:
- Concurrent load testing
- Response time analysis  
- Success rate measurement
- Throughput benchmarking
- Resource usage monitoring
- Comparative analysis (Before vs After optimization)

Author: MiniMax Agent
Date: 2025-09-15
"""

import asyncio
import concurrent.futures
import time
import statistics
import json
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import threading
import psutil
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import optimized components
from src.processors.optimized_vss_processor import OptimizedVSSProcessor, create_optimized_processor
from src.api.enhanced_vss_client import create_enhanced_vss_client
from src.config.default_config import Config

# Configure matplotlib for Vietnamese text
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial Unicode MS", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vss_benchmark.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Single benchmark test result"""
    mst: str
    success: bool
    response_time: float
    error: str = None
    api_used: str = "unknown"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass 
class LoadTestResult:
    """Load test results for specific concurrency level"""
    concurrent_users: int
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    total_response_time: float
    average_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_rps: float
    errors: Dict[str, int]
    api_usage: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.monitoring = False
        self.samples = []
        self._thread = None
        
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.samples = []
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("System monitoring started")
        
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("System monitoring stopped")
        
    def _monitor_loop(self):
        """Monitoring loop"""
        while self.monitoring:
            try:
                sample = {
                    "timestamp": datetime.now(),
                    "cpu_percent": psutil.cpu_percent(interval=None),
                    "memory_percent": psutil.virtual_memory().percent,
                    "memory_used_mb": psutil.virtual_memory().used / (1024*1024),
                    "disk_io_read": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                    "disk_io_write": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
                    "network_sent": psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
                    "network_recv": psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0,
                }
                self.samples.append(sample)
                time.sleep(1)  # Sample every second
            except Exception as e:
                logger.warning(f"Monitoring error: {e}")
                time.sleep(1)
                
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary"""
        if not self.samples:
            return {}
            
        cpu_values = [s["cpu_percent"] for s in self.samples]
        memory_values = [s["memory_percent"] for s in self.samples]
        memory_mb_values = [s["memory_used_mb"] for s in self.samples]
        
        return {
            "duration_seconds": len(self.samples),
            "cpu": {
                "average": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
                "median": statistics.median(cpu_values)
            },
            "memory": {
                "average_percent": statistics.mean(memory_values),
                "max_percent": max(memory_values),
                "average_mb": statistics.mean(memory_mb_values),
                "max_mb": max(memory_mb_values)
            },
            "samples_count": len(self.samples)
        }

class VSSBenchmark:
    """Main benchmark class"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or Config.get_default_config()
        self.test_mst_codes = self.config.get("benchmarking", {}).get("test_mst_codes", [
            "0123456789", "0123456788", "0123456787", "0123456786", "0123456785"
        ])
        self.results_dir = Path("benchmark_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize processors
        self.optimized_processor = None
        self.basic_client = None
        
        self.system_monitor = SystemMonitor()
        
    def setup_processors(self):
        """Setup test processors"""
        logger.info("Setting up processors for benchmark...")
        
        try:
            # Optimized processor
            self.optimized_processor = create_optimized_processor(
                config=self.config,
                api_strategy="enterprise_first"
            )
            logger.info("Optimized processor created successfully")
            
            # Basic client for comparison
            self.basic_client = create_enhanced_vss_client()
            logger.info("Basic client created successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup processors: {e}")
            raise
            
    def run_single_request(self, processor, mst: str, test_name: str = "") -> BenchmarkResult:
        """Run single request and measure performance"""
        start_time = time.time()
        
        try:
            if hasattr(processor, 'get_company_info'):
                result = processor.get_company_info(mst)
                response_time = time.time() - start_time
                
                api_used = result.get("_api_source", "unknown")
                
                return BenchmarkResult(
                    mst=mst,
                    success=True,
                    response_time=response_time,
                    api_used=api_used,
                    timestamp=datetime.now()
                )
            else:
                raise Exception("Processor doesn't have get_company_info method")
                
        except Exception as e:
            response_time = time.time() - start_time
            return BenchmarkResult(
                mst=mst,
                success=False,
                response_time=response_time,
                error=str(e),
                timestamp=datetime.now()
            )
    
    def run_load_test(self, processor, concurrent_users: int, duration: int = 60) -> LoadTestResult:
        """Run load test with specified concurrency"""
        logger.info(f"Starting load test: {concurrent_users} users, {duration}s duration")
        
        results = []
        start_time = time.time()
        end_time = start_time + duration
        
        self.system_monitor.start_monitoring()
        
        def worker():
            """Worker function for concurrent requests"""
            while time.time() < end_time:
                mst = np.random.choice(self.test_mst_codes)
                result = self.run_single_request(processor, mst)
                results.append(result)
                
                # Small delay to prevent overwhelming
                time.sleep(0.1)
        
        # Start concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            
            # Wait for completion or timeout
            try:
                concurrent.futures.wait(futures, timeout=duration + 10)
            except Exception as e:
                logger.warning(f"Load test execution error: {e}")
        
        self.system_monitor.stop_monitoring()
        
        # Analyze results
        actual_duration = time.time() - start_time
        return self._analyze_load_test_results(results, concurrent_users, actual_duration)
    
    def _analyze_load_test_results(self, results: List[BenchmarkResult], 
                                 concurrent_users: int, duration: float) -> LoadTestResult:
        """Analyze load test results"""
        
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.success)
        failed_requests = total_requests - successful_requests
        
        if total_requests == 0:
            return LoadTestResult(
                concurrent_users=concurrent_users,
                duration=duration,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                success_rate=0.0,
                total_response_time=0.0,
                average_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                median_response_time=0.0,
                p95_response_time=0.0,
                p99_response_time=0.0,
                throughput_rps=0.0,
                errors={},
                api_usage={}
            )
        
        # Response time analysis
        response_times = [r.response_time for r in results]
        success_rate = (successful_requests / total_requests) * 100
        
        # Error analysis
        errors = {}
        for r in results:
            if not r.success and r.error:
                error_type = type(Exception(r.error)).__name__
                errors[error_type] = errors.get(error_type, 0) + 1
        
        # API usage analysis
        api_usage = {}
        for r in results:
            if r.success:
                api = r.api_used
                api_usage[api] = api_usage.get(api, 0) + 1
        
        return LoadTestResult(
            concurrent_users=concurrent_users,
            duration=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            success_rate=success_rate,
            total_response_time=sum(response_times),
            average_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=np.percentile(response_times, 95),
            p99_response_time=np.percentile(response_times, 99),
            throughput_rps=total_requests / duration,
            errors=errors,
            api_usage=api_usage
        )
    
    def run_comprehensive_benchmark(self, test_duration: int = 120) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        logger.info("🚀 Starting comprehensive VSS performance benchmark")
        
        benchmark_start = datetime.now()
        benchmark_results = {
            "benchmark_info": {
                "start_time": benchmark_start.isoformat(),
                "test_duration": test_duration,
                "test_mst_codes": self.test_mst_codes,
                "system_info": self._get_system_info()
            },
            "optimized_processor": {},
            "basic_client": {},
            "comparison": {},
            "recommendations": []
        }
        
        # Test concurrency levels
        concurrency_levels = [1, 2, 5, 10]
        
        try:
            # Test Optimized Processor
            logger.info("📊 Testing Optimized Processor...")
            optimized_results = []
            
            for concurrent_users in concurrency_levels:
                logger.info(f"Testing with {concurrent_users} concurrent users...")
                result = self.run_load_test(
                    self.optimized_processor, 
                    concurrent_users, 
                    test_duration // len(concurrency_levels)
                )
                optimized_results.append(result)
                
                # Get processor metrics
                processor_metrics = self.optimized_processor.get_performance_metrics()
                result_dict = result.to_dict()
                result_dict["processor_metrics"] = processor_metrics
                result_dict["system_resources"] = self.system_monitor.get_summary()
                
                benchmark_results["optimized_processor"][f"{concurrent_users}_users"] = result_dict
                
                # Short break between tests
                time.sleep(5)
            
            # Test Basic Client
            logger.info("📊 Testing Basic Client...")
            basic_results = []
            
            for concurrent_users in concurrency_levels:
                logger.info(f"Testing basic client with {concurrent_users} concurrent users...")
                result = self.run_load_test(
                    self.basic_client, 
                    concurrent_users, 
                    test_duration // len(concurrency_levels)
                )
                basic_results.append(result)
                
                result_dict = result.to_dict()
                result_dict["system_resources"] = self.system_monitor.get_summary()
                
                benchmark_results["basic_client"][f"{concurrent_users}_users"] = result_dict
                
                # Short break between tests
                time.sleep(5)
            
            # Comparative Analysis
            logger.info("📈 Performing comparative analysis...")
            comparison = self._compare_results(optimized_results, basic_results)
            benchmark_results["comparison"] = comparison
            
            # Generate recommendations
            recommendations = self._generate_recommendations(comparison)
            benchmark_results["recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"Benchmark execution error: {e}")
            benchmark_results["error"] = str(e)
        
        # Finalize results
        benchmark_end = datetime.now()
        benchmark_results["benchmark_info"]["end_time"] = benchmark_end.isoformat()
        benchmark_results["benchmark_info"]["total_duration"] = (benchmark_end - benchmark_start).total_seconds()
        
        # Save results
        self._save_results(benchmark_results)
        
        # Generate visualizations
        self._generate_visualizations(benchmark_results)
        
        logger.info("✅ Comprehensive benchmark completed!")
        return benchmark_results
    
    def _compare_results(self, optimized_results: List[LoadTestResult], 
                        basic_results: List[LoadTestResult]) -> Dict[str, Any]:
        """Compare optimized vs basic results"""
        
        comparison = {
            "performance_improvements": {},
            "summary": {}
        }
        
        for i, (opt_result, basic_result) in enumerate(zip(optimized_results, basic_results)):
            users = opt_result.concurrent_users
            
            # Calculate improvements
            success_rate_improvement = opt_result.success_rate - basic_result.success_rate
            response_time_improvement = ((basic_result.average_response_time - opt_result.average_response_time) 
                                       / basic_result.average_response_time) * 100
            throughput_improvement = ((opt_result.throughput_rps - basic_result.throughput_rps) 
                                    / basic_result.throughput_rps) * 100
            
            comparison["performance_improvements"][f"{users}_users"] = {
                "success_rate_improvement_percent": success_rate_improvement,
                "response_time_improvement_percent": response_time_improvement,
                "throughput_improvement_percent": throughput_improvement,
                "optimized": {
                    "success_rate": opt_result.success_rate,
                    "avg_response_time": opt_result.average_response_time,
                    "throughput_rps": opt_result.throughput_rps
                },
                "basic": {
                    "success_rate": basic_result.success_rate,
                    "avg_response_time": basic_result.average_response_time,
                    "throughput_rps": basic_result.throughput_rps
                }
            }
        
        # Overall summary
        avg_success_improvement = statistics.mean([
            comp["success_rate_improvement_percent"] 
            for comp in comparison["performance_improvements"].values()
        ])
        avg_response_improvement = statistics.mean([
            comp["response_time_improvement_percent"] 
            for comp in comparison["performance_improvements"].values()
        ])
        avg_throughput_improvement = statistics.mean([
            comp["throughput_improvement_percent"] 
            for comp in comparison["performance_improvements"].values()
        ])
        
        comparison["summary"] = {
            "average_success_rate_improvement": avg_success_improvement,
            "average_response_time_improvement": avg_response_improvement,
            "average_throughput_improvement": avg_throughput_improvement,
            "overall_rating": self._calculate_overall_rating(
                avg_success_improvement, avg_response_improvement, avg_throughput_improvement
            )
        }
        
        return comparison
    
    def _calculate_overall_rating(self, success_improvement: float, 
                                response_improvement: float, throughput_improvement: float) -> str:
        """Calculate overall performance rating"""
        
        score = 0
        
        # Success rate improvement (40% weight)
        if success_improvement >= 20:
            score += 4 * 0.4
        elif success_improvement >= 10:
            score += 3 * 0.4
        elif success_improvement >= 5:
            score += 2 * 0.4
        elif success_improvement >= 0:
            score += 1 * 0.4
        
        # Response time improvement (35% weight)
        if response_improvement >= 50:
            score += 4 * 0.35
        elif response_improvement >= 30:
            score += 3 * 0.35
        elif response_improvement >= 15:
            score += 2 * 0.35
        elif response_improvement >= 0:
            score += 1 * 0.35
        
        # Throughput improvement (25% weight)
        if throughput_improvement >= 50:
            score += 4 * 0.25
        elif throughput_improvement >= 25:
            score += 3 * 0.25
        elif throughput_improvement >= 10:
            score += 2 * 0.25
        elif throughput_improvement >= 0:
            score += 1 * 0.25
        
        if score >= 3.5:
            return "EXCELLENT"
        elif score >= 2.5:
            return "GOOD"
        elif score >= 1.5:
            return "FAIR"
        else:
            return "POOR"
    
    def _generate_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        summary = comparison["summary"]
        success_improvement = summary["average_success_rate_improvement"]
        response_improvement = summary["average_response_time_improvement"]
        throughput_improvement = summary["average_throughput_improvement"]
        
        if success_improvement >= 15:
            recommendations.append("✅ Optimized system significantly improves success rate - recommend production deployment")
        elif success_improvement >= 5:
            recommendations.append("⚠️  Moderate success rate improvement - consider further optimization")
        else:
            recommendations.append("❌ Limited success rate improvement - investigate configuration")
        
        if response_improvement >= 30:
            recommendations.append("🚀 Excellent response time improvement - users will notice faster performance")
        elif response_improvement >= 10:
            recommendations.append("📈 Good response time improvement - noticeable performance boost")
        else:
            recommendations.append("⏱️ Limited response time improvement - consider caching optimization")
        
        if throughput_improvement >= 25:
            recommendations.append("💪 Outstanding throughput improvement - system can handle much higher load")
        elif throughput_improvement >= 10:
            recommendations.append("📊 Good throughput improvement - better resource utilization")
        else:
            recommendations.append("🔄 Consider increasing concurrent request limits for better throughput")
        
        # Overall recommendation
        overall_rating = summary["overall_rating"]
        if overall_rating == "EXCELLENT":
            recommendations.append("🎉 RECOMMENDATION: Deploy optimized system immediately - all metrics show significant improvement")
        elif overall_rating == "GOOD":
            recommendations.append("👍 RECOMMENDATION: Deploy optimized system - most metrics show good improvement")
        elif overall_rating == "FAIR":
            recommendations.append("⚖️ RECOMMENDATION: Consider deployment after further testing and optimization")
        else:
            recommendations.append("🔍 RECOMMENDATION: Investigate issues before deployment - performance gains are minimal")
        
        return recommendations
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "disk_total_gb": psutil.disk_usage('/').total / (1024**3),
            "python_version": sys.version,
            "platform": sys.platform
        }
    
    def _save_results(self, results: Dict[str, Any]):
        """Save benchmark results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON results
        json_file = self.results_dir / f"vss_benchmark_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results saved to: {json_file}")
        
        # Save summary report
        summary_file = self.results_dir / f"vss_benchmark_summary_{timestamp}.md"
        self._generate_markdown_report(results, summary_file)
        
        return json_file
    
    def _generate_markdown_report(self, results: Dict[str, Any], output_file: Path):
        """Generate markdown summary report"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# VSS Performance Benchmark Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Benchmark Info
            f.write("## Benchmark Information\n\n")
            info = results["benchmark_info"]
            f.write(f"- **Duration:** {info.get('total_duration', 0):.1f} seconds\n")
            f.write(f"- **Test MST Codes:** {', '.join(info['test_mst_codes'])}\n")
            f.write(f"- **System:** {info['system_info']['cpu_count']} CPUs, {info['system_info']['memory_total_gb']:.1f}GB RAM\n\n")
            
            # Performance Summary
            if "comparison" in results and "summary" in results["comparison"]:
                f.write("## Performance Summary\n\n")
                summary = results["comparison"]["summary"]
                f.write(f"- **Overall Rating:** {summary['overall_rating']}\n")
                f.write(f"- **Success Rate Improvement:** {summary['average_success_rate_improvement']:.1f}%\n")
                f.write(f"- **Response Time Improvement:** {summary['average_response_time_improvement']:.1f}%\n")
                f.write(f"- **Throughput Improvement:** {summary['average_throughput_improvement']:.1f}%\n\n")
            
            # Recommendations
            if "recommendations" in results:
                f.write("## Recommendations\n\n")
                for rec in results["recommendations"]:
                    f.write(f"- {rec}\n")
                f.write("\n")
            
            # Detailed Results
            f.write("## Detailed Results\n\n")
            f.write("### Optimized Processor Results\n\n")
            
            for users, result in results.get("optimized_processor", {}).items():
                f.write(f"**{users.replace('_', ' ').title()}:**\n")
                f.write(f"- Success Rate: {result['success_rate']:.1f}%\n")
                f.write(f"- Avg Response Time: {result['average_response_time']:.3f}s\n") 
                f.write(f"- Throughput: {result['throughput_rps']:.1f} RPS\n")
                f.write(f"- Total Requests: {result['total_requests']}\n\n")
        
        logger.info(f"Summary report saved to: {output_file}")
    
    def _generate_visualizations(self, results: Dict[str, Any]):
        """Generate performance visualizations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Performance comparison chart
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('VSS Performance Benchmark Results', fontsize=16, fontweight='bold')
            
            # Extract data for plotting
            concurrency_levels = []
            opt_success_rates = []
            basic_success_rates = []
            opt_response_times = []
            basic_response_times = []
            opt_throughputs = []
            basic_throughputs = []
            
            for users in ['1_users', '2_users', '5_users', '10_users']:
                if users in results.get('optimized_processor', {}) and users in results.get('basic_client', {}):
                    concurrency_levels.append(int(users.split('_')[0]))
                    
                    opt_data = results['optimized_processor'][users]
                    basic_data = results['basic_client'][users]
                    
                    opt_success_rates.append(opt_data['success_rate'])
                    basic_success_rates.append(basic_data['success_rate'])
                    opt_response_times.append(opt_data['average_response_time'])
                    basic_response_times.append(basic_data['average_response_time'])
                    opt_throughputs.append(opt_data['throughput_rps'])
                    basic_throughputs.append(basic_data['throughput_rps'])
            
            if concurrency_levels:
                # Success Rate Comparison
                axes[0, 0].plot(concurrency_levels, opt_success_rates, 'o-', label='Optimized', linewidth=2, markersize=8)
                axes[0, 0].plot(concurrency_levels, basic_success_rates, 's--', label='Basic', linewidth=2, markersize=8)
                axes[0, 0].set_title('Success Rate Comparison')
                axes[0, 0].set_xlabel('Concurrent Users')
                axes[0, 0].set_ylabel('Success Rate (%)')
                axes[0, 0].legend()
                axes[0, 0].grid(True, alpha=0.3)
                
                # Response Time Comparison
                axes[0, 1].plot(concurrency_levels, opt_response_times, 'o-', label='Optimized', linewidth=2, markersize=8)
                axes[0, 1].plot(concurrency_levels, basic_response_times, 's--', label='Basic', linewidth=2, markersize=8)
                axes[0, 1].set_title('Response Time Comparison')
                axes[0, 1].set_xlabel('Concurrent Users')
                axes[0, 1].set_ylabel('Avg Response Time (s)')
                axes[0, 1].legend()
                axes[0, 1].grid(True, alpha=0.3)
                
                # Throughput Comparison
                axes[1, 0].plot(concurrency_levels, opt_throughputs, 'o-', label='Optimized', linewidth=2, markersize=8)
                axes[1, 0].plot(concurrency_levels, basic_throughputs, 's--', label='Basic', linewidth=2, markersize=8)
                axes[1, 0].set_title('Throughput Comparison')
                axes[1, 0].set_xlabel('Concurrent Users')
                axes[1, 0].set_ylabel('Throughput (RPS)')
                axes[1, 0].legend()
                axes[1, 0].grid(True, alpha=0.3)
                
                # Performance Improvement
                if len(concurrency_levels) > 0:
                    success_improvements = [(opt - basic) for opt, basic in zip(opt_success_rates, basic_success_rates)]
                    response_improvements = [((basic - opt) / basic) * 100 for opt, basic in zip(opt_response_times, basic_response_times)]
                    throughput_improvements = [((opt - basic) / basic) * 100 for opt, basic in zip(opt_throughputs, basic_throughputs)]
                    
                    x = np.arange(len(concurrency_levels))
                    width = 0.25
                    
                    axes[1, 1].bar(x - width, success_improvements, width, label='Success Rate (%)', alpha=0.8)
                    axes[1, 1].bar(x, response_improvements, width, label='Response Time (%)', alpha=0.8)
                    axes[1, 1].bar(x + width, throughput_improvements, width, label='Throughput (%)', alpha=0.8)
                    
                    axes[1, 1].set_title('Performance Improvements')
                    axes[1, 1].set_xlabel('Concurrent Users')
                    axes[1, 1].set_ylabel('Improvement (%)')
                    axes[1, 1].set_xticks(x)
                    axes[1, 1].set_xticklabels(concurrency_levels)
                    axes[1, 1].legend()
                    axes[1, 1].grid(True, alpha=0.3)
                    axes[1, 1].axhline(y=0, color='k', linestyle='-', alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_file = self.results_dir / f"vss_benchmark_chart_{timestamp}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Performance chart saved to: {chart_file}")
            
        except Exception as e:
            logger.warning(f"Failed to generate visualizations: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.optimized_processor:
            self.optimized_processor.shutdown()
        self.system_monitor.stop_monitoring()

def main():
    """Main benchmark execution"""
    logger.info("🔥 Starting VSS Performance Benchmark")
    
    benchmark = VSSBenchmark()
    
    try:
        # Setup
        benchmark.setup_processors()
        
        # Run comprehensive benchmark
        results = benchmark.run_comprehensive_benchmark(test_duration=240)  # 4 minutes
        
        # Print summary
        if "comparison" in results and "summary" in results["comparison"]:
            summary = results["comparison"]["summary"]
            logger.info("📊 BENCHMARK SUMMARY:")
            logger.info(f"   Overall Rating: {summary['overall_rating']}")
            logger.info(f"   Success Rate Improvement: {summary['average_success_rate_improvement']:.1f}%")
            logger.info(f"   Response Time Improvement: {summary['average_response_time_improvement']:.1f}%")
            logger.info(f"   Throughput Improvement: {summary['average_throughput_improvement']:.1f}%")
            
        if "recommendations" in results:
            logger.info("💡 RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                logger.info(f"   {rec}")
        
        logger.info("✅ Benchmark completed successfully!")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        raise
    finally:
        benchmark.cleanup()

if __name__ == "__main__":
    main()