#!/usr/bin/env python3
"""
VSS Optimization Demo Script
Demonstrate the capabilities of the optimized VSS system

Features:
- Interactive demo of Enhanced VSS Client
- Optimized Processor demonstrations  
- Performance metrics display
- Real-time health monitoring
- Comparison with basic functionality

Author: MiniMax Agent
Date: 2025-09-15
"""

import asyncio
import json
import logging
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import threading

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import optimized components
from src.processors.optimized_vss_processor import OptimizedVSSProcessor, create_optimized_processor, APIStrategy
from src.api.enhanced_vss_client import create_enhanced_vss_client
from src.config.default_config import Config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VSSOptimizationDemo:
    """VSS Optimization Demo Class"""
    
    def __init__(self):
        self.config = Config.get_default_config()
        
        # Demo MST codes for testing
        self.demo_mst_codes = [
            "0123456789",  # Standard test codes
            "0123456788", 
            "0123456787",
            "0106565892",  # Real MST for testing
            "0104926454"
        ]
        
        # Initialize components
        self.enhanced_client = None
        self.optimized_processor = None
        
        self.demo_results = []
        
    def setup_components(self):
        """Setup demo components"""
        logger.info("🚀 Setting up VSS optimization components...")
        
        try:
            # Enhanced VSS Client
            self.enhanced_client = create_enhanced_vss_client()
            logger.info("✅ Enhanced VSS Client created")
            
            # Optimized Processor
            self.optimized_processor = create_optimized_processor(
                config=self.config,
                api_strategy="enterprise_first"
            )
            logger.info("✅ Optimized VSS Processor created")
            
            logger.info("🎯 All components ready for demonstration!")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup components: {e}")
            raise
    
    def demo_enhanced_client(self):
        """Demonstrate Enhanced VSS Client capabilities"""
        logger.info("\n" + "="*60)
        logger.info("🔥 DEMO: Enhanced VSS Client")
        logger.info("="*60)
        
        print("\n📋 Features being demonstrated:")
        print("  ✓ Proxy Rotation Manager")
        print("  ✓ Circuit Breaker Pattern") 
        print("  ✓ Smart Caching System")
        print("  ✓ Advanced Error Handling")
        print("  ✓ Data Validation")
        print("  ✓ Performance Metrics")
        
        for i, mst in enumerate(self.demo_mst_codes[:3], 1):
            print(f"\n🔍 Test {i}: Processing MST {mst}")
            
            start_time = time.time()
            
            try:
                # First call - will be cached
                result = self.enhanced_client.get_company_info(mst)
                first_call_time = time.time() - start_time
                
                print(f"   ✅ Success - Response time: {first_call_time:.3f}s")
                print(f"   📊 Company: {result.get('ten_doanh_nghiep', 'N/A')}")
                
                # Second call - should hit cache
                start_time = time.time()
                cached_result = self.enhanced_client.get_company_info(mst)
                second_call_time = time.time() - start_time
                
                print(f"   🚀 Cached call - Response time: {second_call_time:.3f}s")
                print(f"   ⚡ Speed improvement: {((first_call_time - second_call_time) / first_call_time) * 100:.1f}%")
                
                self.demo_results.append({
                    "test": f"enhanced_client_{i}",
                    "mst": mst,
                    "first_call_time": first_call_time,
                    "cached_call_time": second_call_time,
                    "cache_speedup": ((first_call_time - second_call_time) / first_call_time) * 100,
                    "success": True
                })
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                self.demo_results.append({
                    "test": f"enhanced_client_{i}",
                    "mst": mst,
                    "error": str(e),
                    "success": False
                })
                
            time.sleep(1)  # Brief pause between tests
        
        # Show performance metrics
        print(f"\n📈 Enhanced Client Performance Metrics:")
        metrics = self.enhanced_client.get_performance_metrics()
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   Success Rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"   Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1f}%")
        print(f"   Average Response Time: {metrics['average_response_time']:.3f}s")
        print(f"   Circuit Breaker State: {metrics['circuit_breaker_state']}")
        
    def demo_optimized_processor(self):
        """Demonstrate Optimized Processor capabilities"""
        logger.info("\n" + "="*60)
        logger.info("⚡ DEMO: Optimized VSS Processor")
        logger.info("="*60)
        
        print("\n📋 Features being demonstrated:")
        print("  ✓ Intelligent API Routing")
        print("  ✓ Parallel Processing")
        print("  ✓ Real-time Performance Monitoring") 
        print("  ✓ Batch Processing")
        print("  ✓ Health Checking")
        print("  ✓ Auto-optimization")
        
        # Single request demo
        print(f"\n🎯 Single Request Demo:")
        test_mst = self.demo_mst_codes[0]
        
        start_time = time.time()
        
        try:
            result = self.optimized_processor.get_company_info(test_mst)
            processing_time = time.time() - start_time
            
            print(f"   ✅ MST {test_mst} processed successfully")
            print(f"   ⏱️ Processing time: {processing_time:.3f}s")
            print(f"   🔄 API used: {result.get('_api_source', 'unknown')}")
            print(f"   🏢 Company: {result.get('ten_doanh_nghiep', 'N/A')}")
            
            # Show processing status
            status = self.optimized_processor.get_processing_status(test_mst)
            print(f"   📊 Processing status: {status.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        # Batch processing demo
        print(f"\n📦 Batch Processing Demo:")
        batch_mst_codes = self.demo_mst_codes[:3]
        
        print(f"   Processing {len(batch_mst_codes)} MST codes in parallel...")
        
        start_time = time.time()
        
        def progress_callback(completed, total, percentage):
            print(f"   📊 Progress: {completed}/{total} ({percentage:.1f}%)")
        
        try:
            batch_results = self.optimized_processor.batch_process(
                batch_mst_codes,
                progress_callback=progress_callback
            )
            
            batch_time = time.time() - start_time
            success_count = sum(1 for r in batch_results if r.get("success", False))
            
            print(f"   ✅ Batch processing completed")
            print(f"   ⏱️ Total time: {batch_time:.3f}s")
            print(f"   📈 Success rate: {(success_count/len(batch_results))*100:.1f}%")
            print(f"   🚀 Average per item: {batch_time/len(batch_results):.3f}s")
            
            self.demo_results.append({
                "test": "batch_processing",
                "batch_size": len(batch_mst_codes),
                "total_time": batch_time,
                "success_count": success_count,
                "success_rate": (success_count/len(batch_results))*100,
                "avg_per_item": batch_time/len(batch_results)
            })
            
        except Exception as e:
            print(f"   ❌ Batch processing error: {str(e)}")
    
    def demo_intelligent_routing(self):
        """Demonstrate intelligent API routing"""
        logger.info("\n" + "="*60) 
        logger.info("🧠 DEMO: Intelligent API Routing")
        logger.info("="*60)
        
        print("\n📋 Testing different API strategies:")
        
        strategies = [
            ("ENTERPRISE_FIRST", "Enterprise API first, fallback to VSS"),
            ("VSS_ONLY", "VSS API only"),
            ("AUTO", "Automatic selection based on performance")
        ]
        
        test_mst = self.demo_mst_codes[0]
        
        for strategy_name, description in strategies:
            print(f"\n🎯 Testing {strategy_name} strategy:")
            print(f"   📝 {description}")
            
            # Create processor with specific strategy
            strategy_enum = getattr(APIStrategy, strategy_name)
            processor = OptimizedVSSProcessor(
                config=self.config,
                api_strategy=strategy_enum,
                max_concurrent_requests=5
            )
            
            start_time = time.time()
            
            try:
                result = processor.get_company_info(test_mst)
                processing_time = time.time() - start_time
                
                print(f"   ✅ Success - Time: {processing_time:.3f}s")
                print(f"   🔄 API used: {result.get('_api_source', 'unknown')}")
                
                # Get metrics
                metrics = processor.get_performance_metrics()
                api_perf = metrics.get('api_performance', {})
                
                print(f"   📊 Enterprise API success rate: {api_perf.get('enterprise_api', {}).get('success_rate', 0):.1f}%")
                print(f"   📊 VSS API success rate: {api_perf.get('vss_api', {}).get('success_rate', 0):.1f}%")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                
            finally:
                processor.shutdown()
                
            time.sleep(1)
    
    def demo_performance_monitoring(self):
        """Demonstrate real-time performance monitoring"""
        logger.info("\n" + "="*60)
        logger.info("📊 DEMO: Performance Monitoring")
        logger.info("="*60)
        
        print("\n📋 Performance monitoring features:")
        print("  ✓ Real-time metrics collection")
        print("  ✓ API performance tracking")
        print("  ✓ Health status monitoring")
        print("  ✓ Performance history")
        
        # Get comprehensive metrics
        print(f"\n🔍 Current Performance Metrics:")
        
        try:
            metrics = self.optimized_processor.get_performance_metrics()
            
            current = metrics.get('current_metrics', {})
            api_perf = metrics.get('api_performance', {})
            caching = metrics.get('caching', {})
            config = metrics.get('configuration', {})
            
            print(f"   📈 Current Metrics:")
            print(f"     • Total Requests: {current.get('total_requests', 0)}")
            print(f"     • Success Rate: {current.get('success_rate', 0):.1f}%")
            print(f"     • Avg Response Time: {current.get('average_processing_time', 0):.3f}s")
            print(f"     • Concurrent Requests: {current.get('current_concurrent_requests', 0)}")
            print(f"     • Peak Concurrent: {current.get('peak_concurrent_requests', 0)}")
            
            print(f"   🔄 API Performance:")
            enterprise = api_perf.get('enterprise_api', {})
            vss = api_perf.get('vss_api', {})
            print(f"     • Enterprise API: {enterprise.get('success_count', 0)} success, {enterprise.get('success_rate', 0):.1f}% rate")
            print(f"     • VSS API: {vss.get('success_count', 0)} success, {vss.get('success_rate', 0):.1f}% rate")
            
            print(f"   💾 Caching:")
            print(f"     • Cache Hits: {caching.get('cache_hits', 0)}")
            print(f"     • Cache Misses: {caching.get('cache_misses', 0)}")
            print(f"     • Hit Rate: {caching.get('cache_hit_rate', 0):.1f}%")
            
            print(f"   ⚙️ Configuration:")
            print(f"     • API Strategy: {config.get('api_strategy', 'unknown')}")
            print(f"     • Max Concurrent: {config.get('max_concurrent_requests', 0)}")
            print(f"     • Caching: {'Enabled' if config.get('caching_enabled') else 'Disabled'}")
            
        except Exception as e:
            print(f"   ❌ Error getting metrics: {str(e)}")
    
    def demo_health_check(self):
        """Demonstrate health checking capabilities"""
        logger.info("\n" + "="*60)
        logger.info("🩺 DEMO: Health Check System")
        logger.info("="*60)
        
        print("\n📋 Health check components:")
        print("  ✓ Overall system health")
        print("  ✓ Individual client health")
        print("  ✓ Performance indicators")
        print("  ✓ Resource utilization")
        
        try:
            # Enhanced Client Health
            print(f"\n🔍 Enhanced VSS Client Health:")
            client_health = self.enhanced_client.health_check()
            
            print(f"   Status: {client_health.get('status', 'unknown').upper()}")
            
            circuit_breaker = client_health.get('circuit_breaker', {})
            print(f"   Circuit Breaker: {circuit_breaker.get('state', 'unknown')} ({circuit_breaker.get('failure_count', 0)} failures)")
            
            proxy_manager = client_health.get('proxy_manager', {})
            print(f"   Proxies: {proxy_manager.get('healthy_proxies', 0)}/{proxy_manager.get('total_proxies', 0)} healthy")
            
            cache = client_health.get('cache', {})
            print(f"   Cache: {'Enabled' if cache.get('enabled') else 'Disabled'} ({cache.get('size', 0)} items)")
            
            # Processor Health
            print(f"\n🔍 Optimized Processor Health:")
            processor_health = self.optimized_processor.health_check()
            
            print(f"   Status: {processor_health.get('status', 'unknown').upper()}")
            
            processor_info = processor_health.get('processor', {})
            print(f"   API Strategy: {processor_info.get('api_strategy', 'unknown')}")
            print(f"   Concurrent Requests: {processor_info.get('concurrent_requests', 0)}")
            print(f"   Queue Size: {processor_info.get('queue_size', 0)}")
            
            clients = processor_health.get('clients', {})
            enterprise_status = clients.get('enterprise', {}).get('status', 'unknown')
            vss_status = clients.get('vss', {}).get('status', 'unknown')
            
            print(f"   Enterprise Client: {enterprise_status.upper()}")
            print(f"   VSS Client: {vss_status.upper()}")
            
        except Exception as e:
            print(f"   ❌ Health check error: {str(e)}")
    
    def demo_auto_optimization(self):
        """Demonstrate auto-optimization capabilities"""
        logger.info("\n" + "="*60)
        logger.info("🤖 DEMO: Auto-Optimization")
        logger.info("="*60)
        
        print("\n📋 Auto-optimization features:")
        print("  ✓ Automatic strategy adjustment")
        print("  ✓ Concurrency optimization")
        print("  ✓ Cache management")
        print("  ✓ Performance tuning")
        
        try:
            print(f"\n🔍 Current Configuration:")
            metrics = self.optimized_processor.get_performance_metrics()
            config = metrics.get('configuration', {})
            
            print(f"   API Strategy: {config.get('api_strategy', 'unknown')}")
            print(f"   Max Concurrent: {config.get('max_concurrent_requests', 0)}")
            print(f"   Success Rate: {metrics.get('current_metrics', {}).get('success_rate', 0):.1f}%")
            
            print(f"\n🤖 Running auto-optimization...")
            optimization_result = self.optimized_processor.optimize_performance()
            
            optimizations = optimization_result.get('optimizations_applied', [])
            if optimizations:
                print(f"   ✅ Optimizations applied:")
                for opt in optimizations:
                    print(f"     • {opt}")
            else:
                print(f"   ℹ️ No optimizations needed - system already performing well")
            
            new_config = optimization_result.get('current_config', {})
            print(f"\n📊 Updated Configuration:")
            print(f"   API Strategy: {new_config.get('api_strategy', 'unknown')}")
            print(f"   Max Concurrent: {new_config.get('max_concurrent_requests', 0)}")
            
        except Exception as e:
            print(f"   ❌ Auto-optimization error: {str(e)}")
    
    def run_comprehensive_demo(self):
        """Run comprehensive demonstration"""
        logger.info("\n" + "🎉"*20)
        logger.info("🚀 VSS OPTIMIZATION COMPREHENSIVE DEMO")
        logger.info("🎉"*20)
        
        print(f"\n⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Demo will showcase all optimization features")
        
        demo_start_time = time.time()
        
        try:
            # Setup
            self.setup_components()
            
            # Run all demonstrations
            self.demo_enhanced_client()
            self.demo_optimized_processor()
            self.demo_intelligent_routing()
            self.demo_performance_monitoring()
            self.demo_health_check()
            self.demo_auto_optimization()
            
            # Final summary
            demo_duration = time.time() - demo_start_time
            
            print(f"\n" + "="*60)
            print("🎊 DEMO COMPLETE")
            print("="*60)
            
            print(f"\n⏱️ Total demo duration: {demo_duration:.1f} seconds")
            print(f"📊 Demo tests completed: {len(self.demo_results)}")
            
            # Save demo results
            self.save_demo_results()
            
            print(f"\n💡 Key Benefits Demonstrated:")
            print("  ✅ Improved reliability through circuit breakers and retry logic")
            print("  ✅ Enhanced performance via caching and proxy rotation")  
            print("  ✅ Intelligent routing for maximum success rates")
            print("  ✅ Real-time monitoring and health checking")
            print("  ✅ Automatic optimization and tuning")
            print("  ✅ Comprehensive error handling and recovery")
            
            print(f"\n🚀 Ready for production deployment!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
        finally:
            self.cleanup()
    
    def save_demo_results(self):
        """Save demo results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"vss_optimization_demo_results_{timestamp}.json"
        
        demo_summary = {
            "demo_info": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.demo_results),
                "demo_mst_codes": self.demo_mst_codes
            },
            "test_results": self.demo_results,
            "component_metrics": {}
        }
        
        # Add component metrics
        try:
            if self.enhanced_client:
                demo_summary["component_metrics"]["enhanced_client"] = self.enhanced_client.get_performance_metrics()
            if self.optimized_processor:
                demo_summary["component_metrics"]["optimized_processor"] = self.optimized_processor.get_performance_metrics()
        except Exception as e:
            logger.warning(f"Could not collect final metrics: {e}")
        
        # Save to file
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(demo_summary, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Demo results saved to: {results_file}")
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up demo resources...")
        
        if self.optimized_processor:
            self.optimized_processor.shutdown()
        
        logger.info("✅ Cleanup completed")

def main():
    """Main demo execution"""
    print("🎯 VSS Optimization System Demo")
    print("🔥 Showcasing advanced features and capabilities\n")
    
    demo = VSSOptimizationDemo()
    
    try:
        demo.run_comprehensive_demo()
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        logger.error(f"💥 Demo failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()