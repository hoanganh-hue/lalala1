"""
Tests for VSS Integration Processor
"""
import pytest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.core.data_models import ProcessingResult


class TestVSSIntegrationProcessor:
    """Test cases for VSS Integration Processor"""
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)
        assert processor.max_workers == 2
        assert processor.use_real_apis == False
        assert processor.data_generator is not None
    
    def test_process_single_mst_success(self):
        """Test processing single MST successfully"""
        processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=False)
        result = processor.process_single_mst("110198560")
        
        assert isinstance(result, ProcessingResult)
        assert result.mst == "110198560"
        assert result.success == True
        assert result.confidence_score > 0
        assert result.data_quality in ["HIGH", "MEDIUM"]
        assert result.processing_time > 0
    
    def test_process_single_mst_invalid(self):
        """Test processing invalid MST"""
        processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=False)
        result = processor.process_single_mst("invalid_mst")
        
        assert isinstance(result, ProcessingResult)
        assert result.mst == "invalid_mst"
        # Should still succeed with generated data
        assert result.success == True
    
    def test_process_batch(self):
        """Test batch processing"""
        processor = VSSIntegrationProcessor(max_workers=2, use_real_apis=False)
        msts = ["110198560", "110197454", "110198088"]
        
        results = processor.process_batch(msts)
        
        assert len(results) == 3
        assert all(isinstance(r, ProcessingResult) for r in results)
        assert all(r.success for r in results)
    
    def test_metrics_tracking(self):
        """Test metrics tracking"""
        processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=False)
        
        # Process some MSTs
        processor.process_single_mst("110198560")
        processor.process_single_mst("110197454")
        
        metrics = processor.get_metrics()
        assert metrics.total_processed == 2
        assert metrics.successful == 2
        assert metrics.failed == 0
        assert metrics.success_rate == 100.0
    
    def test_reset_metrics(self):
        """Test metrics reset"""
        processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=False)
        
        # Process some MSTs
        processor.process_single_mst("110198560")
        
        # Reset metrics
        processor.reset_metrics()
        
        metrics = processor.get_metrics()
        assert metrics.total_processed == 0
        assert metrics.successful == 0
        assert metrics.failed == 0


if __name__ == "__main__":
    pytest.main([__file__])
