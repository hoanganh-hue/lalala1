"""
Unit tests for VSS processor
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.core.data_models import ProcessingResult, ProcessingMetrics


class TestVSSProcessorInitialization:
    """Test VSS processor initialization"""

    def test_processor_initialization_default(self):
        """Test processor initialization with defaults"""
        processor = VSSIntegrationProcessor()

        assert processor.max_workers == 2  # Default from config
        assert processor.use_real_apis == True
        assert processor.data_generator is not None
        assert processor.metrics is not None

    def test_processor_initialization_custom(self):
        """Test processor initialization with custom parameters"""
        processor = VSSIntegrationProcessor(max_workers=4, use_real_apis=False)

        assert processor.max_workers == 4
        assert processor.use_real_apis == False

    def test_processor_metrics_initialization(self):
        """Test that processor initializes metrics"""
        processor = VSSIntegrationProcessor()

        metrics = processor.get_metrics()
        assert isinstance(metrics, ProcessingMetrics)
        assert metrics.total_processed == 0
        assert metrics.successful == 0
        assert metrics.failed == 0


class TestSingleMSTProcessing:
    """Test single MST processing"""

    def test_process_single_mst_success_mock(self):
        """Test successful single MST processing with mock data"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        result = processor.process_single_mst("110198560")

        assert isinstance(result, ProcessingResult)
        assert result.mst == "110198560"
        assert result.success == True
        assert result.confidence_score > 0
        assert result.data_quality in ["HIGH", "MEDIUM", "LOW"]
        assert result.processing_time > 0

    def test_process_single_mst_invalid(self):
        """Test processing invalid MST"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        result = processor.process_single_mst("invalid_mst")

        assert isinstance(result, ProcessingResult)
        assert result.mst == "invalid_mst"
        # Should still succeed with generated data
        assert result.success == True

    def test_process_single_mst_empty(self):
        """Test processing empty MST"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        result = processor.process_single_mst("")

        assert isinstance(result, ProcessingResult)
        assert result.mst == ""
        assert result.success == True


class TestBatchProcessing:
    """Test batch processing functionality"""

    def test_process_batch_empty(self):
        """Test processing empty batch"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        results = processor.process_batch([])

        assert isinstance(results, list)
        assert len(results) == 0

    def test_process_batch_single(self):
        """Test processing batch with single MST"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        results = processor.process_batch(["110198560"])

        assert isinstance(results, list)
        assert len(results) == 1
        assert isinstance(results[0], ProcessingResult)
        assert results[0].mst == "110198560"

    def test_process_batch_multiple(self):
        """Test processing batch with multiple MSTs"""
        processor = VSSIntegrationProcessor(use_real_apis=False, max_workers=2)

        msts = ["110198560", "110197454", "110198088"]
        results = processor.process_batch(msts)

        assert isinstance(results, list)
        assert len(results) == 3

        for result in results:
            assert isinstance(result, ProcessingResult)
            assert result.success == True
            assert result.mst in msts

    def test_batch_processing_metrics(self):
        """Test that batch processing updates metrics"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        initial_metrics = processor.get_metrics()

        msts = ["110198560", "110197454"]
        results = processor.process_batch(msts)

        final_metrics = processor.get_metrics()

        assert final_metrics.total_processed == initial_metrics.total_processed + 2
        assert final_metrics.successful == initial_metrics.successful + 2
        assert final_metrics.failed == initial_metrics.failed


class TestProcessorMetrics:
    """Test processor metrics functionality"""

    def test_get_metrics(self):
        """Test getting processor metrics"""
        processor = VSSIntegrationProcessor()

        metrics = processor.get_metrics()

        assert isinstance(metrics, ProcessingMetrics)
        assert hasattr(metrics, 'total_processed')
        assert hasattr(metrics, 'successful')
        assert hasattr(metrics, 'failed')
        assert hasattr(metrics, 'success_rate')

    def test_reset_metrics(self):
        """Test resetting processor metrics"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        # Process some MSTs
        processor.process_single_mst("110198560")

        # Check metrics were updated
        metrics_before = processor.get_metrics()
        assert metrics_before.total_processed > 0

        # Reset metrics
        processor.reset_metrics()

        # Check metrics were reset
        metrics_after = processor.get_metrics()
        assert metrics_after.total_processed == 0
        assert metrics_after.successful == 0
        assert metrics_after.failed == 0

    def test_metrics_calculation(self):
        """Test metrics calculation"""
        processor = VSSIntegrationProcessor()

        # Manually set metrics for testing
        processor.metrics.total_processed = 10
        processor.metrics.successful = 8
        processor.metrics.failed = 2

        metrics = processor.get_metrics()
        assert metrics.success_rate == 80.0


class TestProcessorErrorHandling:
    """Test processor error handling"""

    def test_process_single_mst_exception_handling(self):
        """Test exception handling in single MST processing"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        # Mock data generator to raise exception
        processor.data_generator.generate_enterprise_data = MagicMock(side_effect=Exception("Test error"))

        result = processor.process_single_mst("110198560")

        # Should still return a result, but with error
        assert isinstance(result, ProcessingResult)
        assert result.success == False
        assert result.error_message is not None

    def test_batch_processing_partial_failures(self):
        """Test batch processing with partial failures"""
        processor = VSSIntegrationProcessor(use_real_apis=False, max_workers=1)

        # Mock to fail on second MST
        original_method = processor._process_single_mst_internal

        def mock_process(mst):
            if mst == "110197454":
                raise Exception("Mock failure")
            return original_method(mst)

        processor._process_single_mst_internal = mock_process

        msts = ["110198560", "110197454", "110198088"]
        results = processor.process_batch(msts)

        assert len(results) == 3
        # First and third should succeed, second should fail
        assert results[0].success == True
        assert results[1].success == False
        assert results[2].success == True


class TestProcessorConcurrency:
    """Test processor concurrency features"""

    def test_thread_pool_executor_usage(self):
        """Test that processor uses ThreadPoolExecutor for batch processing"""
        processor = VSSIntegrationProcessor(max_workers=4, use_real_apis=False)

        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_future = MagicMock()
            mock_future.result.return_value = ProcessingResult(mst="110198560", success=True)
            mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

            results = processor.process_batch(["110198560"])

            # Verify ThreadPoolExecutor was used
            mock_executor.assert_called_once_with(max_workers=4)

    def test_max_workers_configuration(self):
        """Test max_workers configuration"""
        processor = VSSIntegrationProcessor(max_workers=8, use_real_apis=False)

        assert processor.max_workers == 8

        # Test with batch processing
        with patch('concurrent.futures.ThreadPoolExecutor') as mock_executor:
            mock_future = MagicMock()
            mock_future.result.return_value = ProcessingResult(mst="110198560", success=True)
            mock_executor.return_value.__enter__.return_value.submit.return_value = mock_future

            processor.process_batch(["110198560"])

            # Verify correct max_workers was used
            mock_executor.assert_called_once_with(max_workers=8)


class TestProcessorDataQuality:
    """Test processor data quality features"""

    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        result = processor.process_single_mst("110198560")

        # Confidence score should be reasonable
        assert 0 <= result.confidence_score <= 1.0

    def test_data_quality_assessment(self):
        """Test data quality assessment"""
        processor = VSSIntegrationProcessor(use_real_apis=False)

        result = processor.process_single_mst("110198560")

        # Data quality should be one of the expected values
        assert result.data_quality in ["HIGH", "MEDIUM", "LOW", "UNKNOWN"]


if __name__ == "__main__":
    pytest.main([__file__])