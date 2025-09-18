#!/usr/bin/env python3
"""
Web server for VSS Integration System
"""
import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import csv
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.vss_processor import VSSIntegrationProcessor
from src.core.data_models import ProcessingResult
from src.config.settings import config
from src.utils.logger import get_logger
from src.utils.mst import normalize_mst, is_valid_mst

app = Flask(__name__)
logger = get_logger("web_server")

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VSS Integration System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background-color: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #2980b9; }
        .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .info { background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .stat-label { color: #7f8c8d; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 VSS Integration System</h1>
        
        <form id="mstForm">
            <div class="form-group">
                <label for="mst">Mã số thuế (MST):</label>
                <input type="text" id="mst" name="mst" placeholder="Nhập MST (10-13 chữ số)" required>
            </div>
            
            <div class="form-group">
                <label for="format">Định dạng kết quả:</label>
                <select id="format" name="format">
                    <option value="summary">Tóm tắt</option>
                    <option value="detailed">Chi tiết</option>
                    <option value="full">Đầy đủ</option>
                </select>
            </div>
            
            <button type="submit">Xử lý MST</button>
        </form>
        
        <div id="result"></div>
        
        <div class="stats" id="stats" style="display: none;">
            <div class="stat-card">
                <div class="stat-number" id="totalRequests">0</div>
                <div class="stat-label">Tổng requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="successfulRequests">0</div>
                <div class="stat-label">Thành công</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avgResponseTime">0s</div>
                <div class="stat-label">Thời gian TB</div>
            </div>
        </div>
    </div>

    <script>
        let stats = { total: 0, successful: 0, totalTime: 0 };
        
        document.getElementById('mstForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const mst = document.getElementById('mst').value;
            const format = document.getElementById('format').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '<div class="info">Đang xử lý...</div>';
            
            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mst: mst, format: format })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <div class="success">
                            <h3>✅ Kết quả xử lý</h3>
                            <p><strong>MST:</strong> ${data.mst}</p>
                            <p><strong>Trạng thái:</strong> Thành công</p>
                            <p><strong>Điểm tin cậy:</strong> ${(data.confidence_score * 100).toFixed(1)}%</p>
                            <p><strong>Chất lượng dữ liệu:</strong> ${data.data_quality}</p>
                            <p><strong>Thời gian xử lý:</strong> ${data.processing_time.toFixed(2)}s</p>
                            <p><strong>Nguồn dữ liệu:</strong> ${data.source}</p>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="error">
                            <h3>❌ Lỗi xử lý</h3>
                            <p><strong>MST:</strong> ${data.mst}</p>
                            <p><strong>Lỗi:</strong> ${data.error}</p>
                        </div>
                    `;
                }
                
                // Update stats
                stats.total++;
                if (data.success) stats.successful++;
                stats.totalTime += data.processing_time || 0;
                updateStats();
                
            } catch (error) {
                resultDiv.innerHTML = `<div class="error">Lỗi kết nối: ${error.message}</div>`;
            }
        });
        
        function updateStats() {
            document.getElementById('stats').style.display = 'grid';
            document.getElementById('totalRequests').textContent = stats.total;
            document.getElementById('successfulRequests').textContent = stats.successful;
            document.getElementById('avgResponseTime').textContent = 
                stats.total > 0 ? (stats.totalTime / stats.total).toFixed(2) + 's' : '0s';
        }
        
        // Load initial stats
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                stats = data;
                updateStats();
            })
            .catch(error => console.log('Could not load stats:', error));
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/process', methods=['POST'])
def process_mst():
    """Process MST endpoint"""
    try:
        data = request.get_json()
        mst = data.get('mst', '').strip()
        format_type = data.get('format', 'summary')
        
        if not mst:
            return jsonify({'success': False, 'error': 'MST is required'}), 400
        
        # Normalize & validate MST format (9–13 digits, pad 9 to 10)
        norm = normalize_mst(mst)
        if not norm:
            return jsonify({'success': False, 'error': 'Invalid MST format'}), 400
        
        logger.info(f"Processing MST: {norm}")
        
        # Process MST
        processor = VSSIntegrationProcessor(max_workers=1, use_real_apis=True)
        result = processor.process_single_mst(norm)
        
        # Update stats
        update_stats(result)
        
        # Prepare response based on format
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
            response_data['retry_count'] = result.retry_count
        
        # Persist daily CSV/JSON completeness logs
        persist_daily_reports(result)

        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error processing MST: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/stats')
def get_stats():
    """Get system statistics"""
    try:
        # Load stats from file or return default
        stats_file = Path('data/stats.json')
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'total': 0, 'successful': 0, 'totalTime': 0, 'source': {'real_api': 0, 'mixed': 0, 'generated': 0}}
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'total': 0, 'successful': 0, 'totalTime': 0})


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })


def update_stats(result: ProcessingResult):
    """Update system statistics"""
    try:
        stats_file = Path('data/stats.json')
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {'total': 0, 'successful': 0, 'totalTime': 0, 'source': {'real_api': 0, 'mixed': 0, 'generated': 0}}
        
        stats['total'] += 1
        if result.success:
            stats['successful'] += 1
        stats['totalTime'] += result.processing_time

        # Track data source distribution
        source_key = result.source or 'unknown'
        if 'source' not in stats:
            stats['source'] = {'real_api': 0, 'mixed': 0, 'generated': 0}
        if source_key not in stats['source']:
            stats['source'][source_key] = 0
        stats['source'][source_key] += 1
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error updating stats: {str(e)}")


def persist_daily_reports(result: ProcessingResult):
    """Persist daily JSON and append to CSV for completeness tracking"""
    try:
        reports_dir = Path('reports')
        reports_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime('%Y-%m-%d')
        json_path = reports_dir / f'completeness_summary_{date_str}.json'
        csv_path = reports_dir / f'completeness_summary_{date_str}.csv'

        # Load or init JSON summary
        if json_path.exists():
            with open(json_path, 'r') as f:
                summary = json.load(f)
        else:
            summary = {
                'date': date_str,
                'total': 0,
                'real_api': 0,
                'mixed': 0,
                'generated': 0,
                'failed': 0,
                'avg_processing_time': 0.0,
                'avg_confidence': 0.0
            }

        # Update summary
        prev_total = summary['total']
        prev_avg_time = summary['avg_processing_time']
        prev_avg_conf = summary['avg_confidence']
        new_total = prev_total + 1

        summary['total'] = new_total
        summary['failed'] += 0 if result.success else 1
        summary[result.source or 'generated'] = summary.get(result.source or 'generated', 0) + 1
        summary['avg_processing_time'] = ((prev_avg_time * prev_total) + (result.processing_time or 0.0)) / new_total
        summary['avg_confidence'] = ((prev_avg_conf * prev_total) + (result.confidence_score or 0.0)) / new_total

        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        # Append CSV row
        write_header = not csv_path.exists()
        with open(csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'mst', 'success', 'source', 'processing_time', 'confidence_score', 'data_quality'])
            if write_header:
                writer.writeheader()
            writer.writerow({
                'timestamp': result.timestamp,
                'mst': result.mst,
                'success': result.success,
                'source': result.source,
                'processing_time': round(result.processing_time or 0.0, 3),
                'confidence_score': round(result.confidence_score or 0.0, 3),
                'data_quality': result.data_quality
            })
    except Exception as e:
        logger.error(f"Error persisting daily reports: {str(e)}")


if __name__ == '__main__':
    # Create necessary directories
    Path('data').mkdir(exist_ok=True)
    Path('logs').mkdir(exist_ok=True)
    
    # Get configuration
    port = config.get('web.port', 5000)
    debug = config.get('web.debug', False)
    
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
