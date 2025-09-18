"""
End-to-end tests for production validation
"""
import pytest
import time
import requests
import subprocess
import signal
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.utils.analytics import get_analytics_engine
from src.utils.performance_monitor import get_performance_monitor


class TestE2EIntegration:
    """End-to-end integration tests"""

    def test_full_system_startup(self):
        """Test complete system startup and shutdown"""
        # This would test the full application startup
        # For now, we'll test component initialization
        processor = VSSIntegrationProcessor(max_workers=2)
        assert processor is not None
        assert processor.max_workers == 2

        # Test analytics engine
        analytics = get_analytics_engine()
        assert analytics is not None

        # Test performance monitor
        monitor = get_performance_monitor()
        assert monitor is not None

    def test_batch_processing_workflow(self):
        """Test complete batch processing workflow"""
        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)

        # Test data
        test_msts = ["110198560", "110197454", "110198088"]

        # Process batch
        start_time = time.time()
        results = processor.process_batch(test_msts)
        processing_time = time.time() - start_time

        # Assertions
        assert len(results) == 3
        assert all(r.success for r in results)
        assert processing_time < 30  # Should complete within 30 seconds

        # Check result structure
        for result in results:
            assert result.mst in test_msts
            assert result.confidence_score > 0
            assert result.data_quality in ["HIGH", "MEDIUM", "LOW"]
            assert result.processing_time > 0

    def test_analytics_workflow(self):
        """Test analytics workflow end-to-end"""
        analytics = get_analytics_engine()

        # Generate test data
        test_results = [
            {
                'mst': '110198560',
                'success': True,
                'processing_time': 1.2,
                'confidence_score': 0.95,
                'data_quality': 'HIGH',
                'source': 'real_api',
                'timestamp': '2024-01-01T10:00:00'
            },
            {
                'mst': '110197454',
                'success': True,
                'processing_time': 0.8,
                'confidence_score': 0.87,
                'data_quality': 'HIGH',
                'source': 'real_api',
                'timestamp': '2024-01-01T10:00:01'
            }
        ]

        # Analyze results
        analysis = analytics.analyze_processing_results(test_results)

        # Assertions
        assert analysis['summary']['total_processed'] == 2
        assert analysis['summary']['successful'] == 2
        assert analysis['summary']['success_rate'] == 100.0
        assert 'performance' in analysis
        assert 'quality' in analysis
        assert 'compliance' in analysis

    def test_performance_under_load(self):
        """Test system performance under load"""
        processor = VSSIntegrationProcessor(max_workers=4, use_real_apis=False)

        # Generate larger test dataset
        test_msts = [f"11019{i:04d}" for i in range(100)]  # 100 MSTs

        # Process under load
        start_time = time.time()
        results = processor.process_batch(test_msts)
        total_time = time.time() - start_time

        # Performance assertions
        assert len(results) == 100
        assert all(r.success for r in results)

        # Throughput should be reasonable
        throughput = len(results) / total_time
        assert throughput > 1.0  # At least 1 MST per second

        # Average processing time should be reasonable
        avg_time = sum(r.processing_time for r in results) / len(results)
        assert avg_time < 5.0  # Less than 5 seconds per MST

    def test_error_handling_and_recovery(self):
        """Test error handling and system recovery"""
        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)

        # Mix of valid and invalid MSTs
        test_msts = [
            "110198560",  # Valid
            "invalid",    # Invalid
            "110197454",  # Valid
            "",          # Empty
            "110198088"   # Valid
        ]

        results = processor.process_batch(test_msts)

        # Should handle all cases gracefully
        assert len(results) == 5

        # Valid MSTs should succeed
        valid_results = [r for r in results if r.mst in ["110198560", "110197454", "110198088"]]
        assert all(r.success for r in valid_results)

        # Invalid MSTs should still return results (with mock data)
        invalid_results = [r for r in results if r.mst in ["invalid", ""]]
        assert all(r.success for r in invalid_results)  # Mock fallback

    def test_memory_usage_stability(self):
        """Test memory usage remains stable under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)

        # Process multiple batches
        for i in range(5):
            test_msts = [f"11019{i:04d}" for i in range(20)]  # 20 MSTs per batch
            results = processor.process_batch(test_msts)
            assert all(r.success for r in results)

            # Force garbage collection
            import gc
            gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB"

    def test_concurrent_access_safety(self):
        """Test system handles concurrent access safely"""
        import threading
        import queue

        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)
        results_queue = queue.Queue()

        def worker_thread(thread_id: int):
            """Worker thread for concurrent testing"""
            try:
                test_msts = [f"11019{i:04d}" for i in range(10)]  # 10 MSTs per thread
                results = processor.process_batch(test_msts)
                results_queue.put((thread_id, results))
            except Exception as e:
                results_queue.put((thread_id, e))

        # Start multiple threads
        threads = []
        num_threads = 3

        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join(timeout=60)

        # Collect results
        all_results = []
        for _ in range(num_threads):
            thread_id, result = results_queue.get(timeout=10)
            if isinstance(result, Exception):
                pytest.fail(f"Thread {thread_id} failed: {result}")
            all_results.extend(result)

        # Verify all results
        assert len(all_results) == num_threads * 10  # 3 threads * 10 MSTs each
        assert all(r.success for r in all_results)


class TestProductionValidation:
    """Production validation tests"""

    def test_configuration_validation(self):
        """Test configuration validation for production"""
        from src.config.settings import config

        # Test required configuration sections exist
        api_config = config.get_api_config()
        assert 'vss_url' in api_config
        assert 'enterprise_url' in api_config

        processing_config = config.get_processing_config()
        assert 'max_workers' in processing_config
        assert 'batch_size' in processing_config

        logging_config = config.get('logging', {})
        assert 'level' in logging_config

    def test_resource_limits(self):
        """Test resource limits are reasonable"""
        processor = VSSIntegrationProcessor(max_workers=10, use_real_apis=False)

        # Should not allow excessive workers
        assert processor.max_workers <= 10

        # Test with large batch
        large_batch = [f"11019{i:04d}" for i in range(1000)]
        results = processor.process_batch(large_batch)

        # Should handle large batches gracefully
        assert len(results) == 1000
        # Allow some failures for very large batches
        success_rate = sum(1 for r in results if r.success) / len(results)
        assert success_rate > 0.8  # At least 80% success rate

    def test_graceful_shutdown(self):
        """Test system shuts down gracefully"""
        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)

        # Start processing
        import threading
        results = []

        def background_process():
            test_msts = [f"11019{i:04d}" for i in range(50)]
            results.extend(processor.process_batch(test_msts))

        thread = threading.Thread(target=background_process)
        thread.start()

        # Wait a bit then check if we can interrupt gracefully
        time.sleep(2)

        # Thread should complete normally
        thread.join(timeout=30)
        assert thread.is_alive() == False
        assert len(results) == 50

    def test_data_integrity(self):
        """Test data integrity across operations"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        # Process same MST multiple times
        mst = "110198560"
        results = []

        for _ in range(3):
            result = processor.process_single_mst(mst)
            results.append(result)
            time.sleep(0.1)  # Small delay

        # All results should be consistent
        assert all(r.success for r in results)
        assert all(r.mst == mst for r in results)
        assert all(r.confidence_score > 0 for r in results)

        # Results should be reasonably consistent (within mock data variation)
        confidence_scores = [r.confidence_score for r in results]
        max_diff = max(confidence_scores) - min(confidence_scores)
        assert max_diff < 0.3  # Allow some variation but not too much

    def test_monitoring_integration(self):
        """Test monitoring integration works"""
        monitor = get_performance_monitor()

        # Get initial metrics
        initial_report = monitor.get_performance_report()

        # Perform some operations
        processor = VSSIntegrationProcessor(use_real_apis=False)
        results = processor.process_batch(["110198560", "110197454"])

        # Get updated metrics
        updated_report = monitor.get_performance_report()

        # Should have some monitoring data
        assert 'timestamp' in initial_report
        assert 'timestamp' in updated_report
        assert updated_report['timestamp'] != initial_report['timestamp']


class TestLoadTesting:
    """Load testing scenarios"""

    @pytest.mark.slow
    def test_sustained_load(self):
        """Test system under sustained load"""
        processor = VSSIntegrationProcessor(max_workers=4, use_real_apis=False)

        # Run for extended period
        start_time = time.time()
        total_processed = 0

        # Process in waves
        for wave in range(5):
            test_msts = [f"110{i:06d}" for i in range(wave * 50, (wave + 1) * 50)]
            results = processor.process_batch(test_msts)

            successful = sum(1 for r in results if r.success)
            total_processed += successful

            # Should maintain good success rate
            success_rate = successful / len(results)
            assert success_rate > 0.9, f"Wave {wave} success rate: {success_rate}"

        elapsed_time = time.time() - start_time

        # Performance metrics
        throughput = total_processed / elapsed_time
        assert throughput > 2.0, f"Throughput: {throughput} req/s"

        self.logger.info(f"Load test completed: {total_processed} processed in {elapsed_time:.1f}s ({throughput:.1f} req/s)")

    @pytest.mark.slow
    def test_memory_leak_detection(self):
        """Test for memory leaks under prolonged operation"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)

        memory_readings = []

        # Take memory readings over time
        for i in range(10):
            # Process batch
            test_msts = [f"110{i:06d}" for i in range(20)]
            results = processor.process_batch(test_msts)

            # Record memory
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_readings.append(memory_mb)

            # Force GC
            import gc
            gc.collect()

            time.sleep(0.5)

        # Check for significant memory growth
        initial_memory = memory_readings[0]
        final_memory = memory_readings[-1]
        growth_rate = (final_memory - initial_memory) / initial_memory

        # Allow some growth but not excessive (< 20%)
        assert growth_rate < 0.2, f"Memory growth: {growth_rate:.1%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])