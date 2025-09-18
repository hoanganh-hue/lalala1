"""
API Documentation with OpenAPI/Swagger
"""
import sys
import os
from flask import Flask
from flask_restx import Api, Resource, fields
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.core.data_models import ProcessingResult
from src.config.settings import config
from src.utils.logger import get_logger

# Create Flask app for API documentation
app = Flask(__name__)
api = Api(app, version='2.0.0', title='VSS Integration System API',
          description='API for Vietnamese Social Security (VSS) data integration and processing',
          doc='/docs')

logger = get_logger("api_docs")

# Define API models
mst_input = api.model('MSTInput', {
    'mst': fields.String(required=True, description='Mã số thuế (10-13 chữ số)', example='110198560'),
    'format': fields.String(required=False, description='Định dạng kết quả', enum=['summary', 'detailed', 'full'], default='summary')
})

processing_result = api.model('ProcessingResult', {
    'mst': fields.String(description='Mã số thuế đã xử lý'),
    'success': fields.Boolean(description='Trạng thái xử lý'),
    'processing_time': fields.Float(description='Thời gian xử lý (giây)'),
    'confidence_score': fields.Float(description='Điểm tin cậy (0-1)'),
    'data_quality': fields.String(description='Chất lượng dữ liệu', enum=['HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']),
    'source': fields.String(description='Nguồn dữ liệu'),
    'timestamp': fields.String(description='Thời gian xử lý'),
    'error': fields.String(description='Thông báo lỗi (nếu có)')
})

stats_result = api.model('StatsResult', {
    'total': fields.Integer(description='Tổng số requests'),
    'successful': fields.Integer(description='Số requests thành công'),
    'totalTime': fields.Float(description='Tổng thời gian xử lý')
})

health_result = api.model('HealthResult', {
    'status': fields.String(description='Trạng thái hệ thống'),
    'timestamp': fields.String(description='Thời gian kiểm tra'),
    'version': fields.String(description='Phiên bản hệ thống')
})

# API namespace
ns = api.namespace('api/v1', description='VSS Integration API v1')

@ns.route('/process')
class ProcessMST(Resource):
    @ns.doc('process_mst')
    @ns.expect(mst_input)
    @ns.marshal_with(processing_result)
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input')
    @ns.response(500, 'Processing error')
    def post(self):
        """Xử lý thông tin doanh nghiệp từ mã số thuế (MST)

        API này sẽ truy xuất và xử lý thông tin doanh nghiệp từ các nguồn dữ liệu
        chính thức của Việt Nam, bao gồm thông tin từ Tổng cục Thuế và Bảo hiểm xã hội.
        """
        try:
            data = api.payload
            mst = data.get('mst', '').strip()
            format_type = data.get('format', 'summary')

            if not mst:
                api.abort(400, 'MST is required')

            # Validate MST format
            if not mst.isdigit() or len(mst) < 10 or len(mst) > 13:
                api.abort(400, 'Invalid MST format (must be 10-13 digits)')

            logger.info(f"Processing MST via API: {mst}")

            # Process MST
            processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=True)
            result = processor.process_single_mst(mst)

            # Prepare response
            response_data = {
                'mst': result.mst,
                'success': result.success,
                'processing_time': result.processing_time,
                'confidence_score': result.confidence_score,
                'data_quality': result.data_quality,
                'source': result.source,
                'timestamp': result.timestamp
            }

            if not result.success:
                response_data['error'] = result.error

            if format_type == 'detailed':
                response_data['retry_count'] = getattr(result, 'retry_count', 0)

            return response_data

        except Exception as e:
            logger.error(f"API processing error: {str(e)}")
            api.abort(500, str(e))


@ns.route('/stats')
class GetStats(Resource):
    @ns.doc('get_stats')
    @ns.marshal_with(stats_result)
    @ns.response(200, 'Success')
    def get(self):
        """Lấy thống kê hệ thống

        Trả về thống kê về số lượng requests, tỷ lệ thành công và hiệu suất xử lý.
        """
        try:
            # Load stats from file or return default
            stats_file = Path('data/stats.json')
            if stats_file.exists():
                import json
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            else:
                stats = {'total': 0, 'successful': 0, 'totalTime': 0}

            return stats

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {'total': 0, 'successful': 0, 'totalTime': 0}


@ns.route('/health')
class HealthCheck(Resource):
    @ns.doc('health_check')
    @ns.marshal_with(health_result)
    @ns.response(200, 'System is healthy')
    def get(self):
        """Kiểm tra tình trạng hệ thống

        Endpoint health check để monitor tình trạng hoạt động của hệ thống.
        """
        from datetime import datetime
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0'
        }


@ns.route('/batch')
class BatchProcess(Resource):
    @ns.doc('batch_process')
    @ns.expect(api.model('BatchInput', {
        'msts': fields.List(fields.String, required=True, description='Danh sách MST cần xử lý'),
        'format': fields.String(required=False, description='Định dạng kết quả', default='summary')
    }))
    @ns.marshal_with(api.model('BatchResult', {
        'total_processed': fields.Integer(description='Tổng số MST đã xử lý'),
        'successful': fields.Integer(description='Số MST xử lý thành công'),
        'failed': fields.Integer(description='Số MST xử lý thất bại'),
        'results': fields.List(fields.Nested(processing_result), description='Kết quả chi tiết'),
        'processing_time': fields.Float(description='Tổng thời gian xử lý')
    }))
    @ns.response(200, 'Success')
    @ns.response(400, 'Invalid input')
    def post(self):
        """Xử lý hàng loạt MST

        Xử lý nhiều MST cùng lúc với tối ưu hóa hiệu suất.
        """
        try:
            data = api.payload
            msts = data.get('msts', [])
            format_type = data.get('format', 'summary')

            if not msts or not isinstance(msts, list):
                api.abort(400, 'msts must be a non-empty list')

            if len(msts) > 100:  # Limit batch size
                api.abort(400, 'Maximum 100 MSTs per batch')

            logger.info(f"Batch processing {len(msts)} MSTs")

            # Process batch
            processor = VSSIntegrationProcessor(max_workers=min(len(msts), 4), use_real_apis=True)
            results = processor.process_batch(msts)

            # Prepare response
            successful = sum(1 for r in results if r.success)
            total_time = sum(r.processing_time for r in results)

            response_data = {
                'total_processed': len(results),
                'successful': successful,
                'failed': len(results) - successful,
                'results': [{
                    'mst': r.mst,
                    'success': r.success,
                    'processing_time': r.processing_time,
                    'confidence_score': r.confidence_score,
                    'data_quality': r.data_quality,
                    'source': r.source,
                    'timestamp': r.timestamp,
                    'error': r.error if not r.success else None
                } for r in results],
                'processing_time': total_time
            }

            return response_data

        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            api.abort(500, str(e))


if __name__ == '__main__':
    # Create necessary directories
    Path('data').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)

    # Get configuration
    port = config.get('web.port', 5001)  # Different port for API docs

    logger.info(f"Starting API documentation server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)