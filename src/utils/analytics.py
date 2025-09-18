"""
Advanced analytics and reporting utilities
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
from ..utils.logger import setup_module_logger


class AnalyticsEngine:
    """Advanced analytics engine for VSS data"""

    def __init__(self):
        self.logger = setup_module_logger("analytics")
        self.data_cache = {}
        self.report_cache = {}

    def analyze_processing_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze processing results for insights"""

        if not results:
            return self._empty_analysis()

        df = pd.DataFrame(results)

        analysis = {
            'summary': self._generate_summary_stats(df),
            'performance': self._analyze_performance(df),
            'quality': self._analyze_data_quality(df),
            'compliance': self._analyze_compliance(df),
            'trends': self._analyze_trends(df),
            'recommendations': self._generate_recommendations(df),
            'timestamp': datetime.now().isoformat()
        }

        return analysis

    def _generate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        total = len(df)
        successful = len(df[df['success'] == True])
        failed = total - successful

        return {
            'total_processed': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'avg_processing_time': df['processing_time'].mean(),
            'median_processing_time': df['processing_time'].median(),
            'min_processing_time': df['processing_time'].min(),
            'max_processing_time': df['processing_time'].max(),
            'total_processing_time': df['processing_time'].sum()
        }

    def _analyze_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance metrics"""
        successful_df = df[df['success'] == True]

        performance = {
            'throughput': len(successful_df) / successful_df['processing_time'].sum() if len(successful_df) > 0 else 0,
            'efficiency_score': self._calculate_efficiency_score(successful_df),
            'bottlenecks': self._identify_bottlenecks(df),
            'optimization_opportunities': self._find_optimization_opportunities(df)
        }

        return performance

    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality metrics"""
        quality_counts = df['data_quality'].value_counts().to_dict()

        quality_scores = {
            'HIGH': 1.0,
            'MEDIUM': 0.7,
            'LOW': 0.4,
            'UNKNOWN': 0.0
        }

        avg_quality_score = sum(
            quality_scores.get(quality, 0) * count
            for quality, count in quality_counts.items()
        ) / len(df) if len(df) > 0 else 0

        return {
            'quality_distribution': quality_counts,
            'average_quality_score': avg_quality_score,
            'quality_trend': self._calculate_quality_trend(df),
            'data_completeness': self._assess_data_completeness(df)
        }

    def _analyze_compliance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze compliance metrics"""
        successful_df = df[df['success'] == True]

        if len(successful_df) == 0:
            return {'compliance_score': 0, 'risk_assessment': 'UNKNOWN'}

        avg_confidence = successful_df['confidence_score'].mean()

        # Compliance score based on confidence and success rate
        compliance_score = (avg_confidence * 0.7) + ((len(successful_df) / len(df)) * 0.3)

        # Risk assessment
        if compliance_score >= 0.8:
            risk_level = 'LOW'
        elif compliance_score >= 0.6:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'

        return {
            'compliance_score': compliance_score,
            'average_confidence': avg_confidence,
            'risk_level': risk_level,
            'compliance_trend': self._calculate_compliance_trend(successful_df)
        }

    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends over time"""
        if 'timestamp' not in df.columns or len(df) < 2:
            return {'trend_available': False}

        # Convert timestamps and sort
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Calculate rolling averages
        window_size = min(10, len(df))
        df['rolling_success_rate'] = df['success'].rolling(window=window_size).mean()
        df['rolling_processing_time'] = df['processing_time'].rolling(window=window_size).mean()

        trends = {
            'trend_available': True,
            'processing_time_trend': 'improving' if df['rolling_processing_time'].iloc[-1] < df['rolling_processing_time'].iloc[0] else 'degrading',
            'success_rate_trend': 'improving' if df['rolling_success_rate'].iloc[-1] > df['rolling_success_rate'].iloc[0] else 'stable',
            'volatility': df['processing_time'].std() / df['processing_time'].mean() if df['processing_time'].mean() > 0 else 0
        }

        return trends

    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Performance recommendations
        avg_time = df['processing_time'].mean()
        if avg_time > 5.0:
            recommendations.append("Consider increasing worker threads for better parallel processing")
        elif avg_time > 2.0:
            recommendations.append("Optimize API calls with better connection pooling")

        # Success rate recommendations
        success_rate = len(df[df['success'] == True]) / len(df) if len(df) > 0 else 0
        if success_rate < 0.8:
            recommendations.append("Investigate API reliability issues and implement better error handling")
        elif success_rate < 0.95:
            recommendations.append("Monitor API endpoints for intermittent failures")

        # Quality recommendations
        quality_counts = df['data_quality'].value_counts()
        if quality_counts.get('LOW', 0) > quality_counts.get('HIGH', 0):
            recommendations.append("Improve data validation and fallback mechanisms")

        # Resource recommendations
        if len(df) > 1000:
            recommendations.append("Consider implementing result caching for frequently accessed MSTs")

        return recommendations

    def _calculate_efficiency_score(self, df: pd.DataFrame) -> float:
        """Calculate processing efficiency score"""
        if len(df) == 0:
            return 0.0

        # Efficiency based on processing time distribution
        mean_time = df['processing_time'].mean()
        std_time = df['processing_time'].std()

        # Lower variance and reasonable mean time = higher efficiency
        efficiency = 1.0 / (1.0 + (std_time / mean_time)) if mean_time > 0 else 0.0

        # Penalize very slow processing
        if mean_time > 10.0:
            efficiency *= 0.5

        return max(0.0, min(1.0, efficiency))

    def _identify_bottlenecks(self, df: pd.DataFrame) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Check for slow processing times
        slow_threshold = df['processing_time'].quantile(0.95)
        slow_count = len(df[df['processing_time'] > slow_threshold])

        if slow_count > len(df) * 0.1:  # More than 10% are slow
            bottlenecks.append(f"High number of slow requests ({slow_count} > 95th percentile)")

        # Check for API errors
        error_count = len(df[df['success'] == False])
        if error_count > len(df) * 0.05:  # More than 5% errors
            bottlenecks.append(f"High error rate ({error_count}/{len(df)} requests)")

        return bottlenecks

    def _find_optimization_opportunities(self, df: pd.DataFrame) -> List[str]:
        """Find optimization opportunities"""
        opportunities = []

        # Check processing time variance
        if len(df) > 10:
            cv = df['processing_time'].std() / df['processing_time'].mean()  # Coefficient of variation
            if cv > 0.5:
                opportunities.append("High processing time variance suggests inconsistent performance")

        # Check for repeated MSTs (potential for caching)
        if 'mst' in df.columns:
            mst_counts = df['mst'].value_counts()
            repeated_msts = len(mst_counts[mst_counts > 1])
            if repeated_msts > len(mst_counts) * 0.1:
                opportunities.append(f"Consider caching results for {repeated_msts} frequently requested MSTs")

        return opportunities

    def _calculate_quality_trend(self, df: pd.DataFrame) -> str:
        """Calculate data quality trend"""
        if len(df) < 2:
            return 'stable'

        # Simple trend analysis
        quality_scores = df['data_quality'].map({'HIGH': 1, 'MEDIUM': 0.5, 'LOW': 0, 'UNKNOWN': 0})
        first_half = quality_scores.iloc[:len(quality_scores)//2].mean()
        second_half = quality_scores.iloc[len(quality_scores)//2:].mean()

        if second_half > first_half + 0.1:
            return 'improving'
        elif second_half < first_half - 0.1:
            return 'degrading'
        else:
            return 'stable'

    def _assess_data_completeness(self, df: pd.DataFrame) -> float:
        """Assess data completeness"""
        required_fields = ['mst', 'success', 'processing_time', 'confidence_score', 'data_quality']
        completeness_scores = []

        for field in required_fields:
            if field in df.columns:
                non_null_ratio = df[field].notna().mean()
                completeness_scores.append(non_null_ratio)

        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0

    def _calculate_compliance_trend(self, df: pd.DataFrame) -> str:
        """Calculate compliance trend"""
        if len(df) < 2:
            return 'stable'

        first_half = df['confidence_score'].iloc[:len(df)//2].mean()
        second_half = df['confidence_score'].iloc[len(df)//2:].mean()

        if second_half > first_half + 0.05:
            return 'improving'
        elif second_half < first_half - 0.05:
            return 'degrading'
        else:
            return 'stable'

    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'summary': {'total_processed': 0, 'successful': 0, 'failed': 0, 'success_rate': 0},
            'performance': {'throughput': 0, 'efficiency_score': 0},
            'quality': {'average_quality_score': 0},
            'compliance': {'compliance_score': 0, 'risk_level': 'UNKNOWN'},
            'trends': {'trend_available': False},
            'recommendations': ['No data available for analysis'],
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self, results: List[Dict[str, Any]], format: str = 'json') -> str:
        """Generate comprehensive analytics report"""
        analysis = self.analyze_processing_results(results)

        if format == 'json':
            return json.dumps(analysis, indent=2, ensure_ascii=False)
        elif format == 'html':
            return self._generate_html_report(analysis)
        else:
            return str(analysis)

    def _generate_html_report(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML analytics report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VSS Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .good {{ color: green; }}
                .warning {{ color: orange; }}
                .bad {{ color: red; }}
                h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h1>VSS Integration Analytics Report</h1>
            <p><strong>Generated:</strong> {analysis['timestamp']}</p>

            <h2>Summary</h2>
            <div class="metric">
                <strong>Total Processed:</strong> {analysis['summary']['total_processed']}<br>
                <strong>Success Rate:</strong> <span class="{self._get_rate_class(analysis['summary']['success_rate'])}">{analysis['summary']['success_rate']:.1f}%</span><br>
                <strong>Average Processing Time:</strong> {analysis['summary']['avg_processing_time']:.2f}s
            </div>

            <h2>Performance</h2>
            <div class="metric">
                <strong>Throughput:</strong> {analysis['performance']['throughput']:.2f} req/s<br>
                <strong>Efficiency Score:</strong> <span class="{self._get_score_class(analysis['performance']['efficiency_score'])}">{analysis['performance']['efficiency_score']:.2f}</span>
            </div>

            <h2>Data Quality</h2>
            <div class="metric">
                <strong>Average Quality Score:</strong> <span class="{self._get_score_class(analysis['quality']['average_quality_score'])}">{analysis['quality']['average_quality_score']:.2f}</span>
            </div>

            <h2>Compliance</h2>
            <div class="metric">
                <strong>Compliance Score:</strong> <span class="{self._get_compliance_class(analysis['compliance']['compliance_score'])}">{analysis['compliance']['compliance_score']:.2f}</span><br>
                <strong>Risk Level:</strong> <span class="{self._get_risk_class(analysis['compliance']['risk_level'])}">{analysis['compliance']['risk_level']}</span>
            </div>

            <h2>Recommendations</h2>
            <ul>
                {"".join(f"<li>{rec}</li>" for rec in analysis['recommendations'])}
            </ul>
        </body>
        </html>
        """
        return html

    def _get_rate_class(self, rate: float) -> str:
        """Get CSS class for success rate"""
        if rate >= 95: return 'good'
        if rate >= 80: return 'warning'
        return 'bad'

    def _get_score_class(self, score: float) -> str:
        """Get CSS class for scores"""
        if score >= 0.8: return 'good'
        if score >= 0.6: return 'warning'
        return 'bad'

    def _get_compliance_class(self, score: float) -> str:
        """Get CSS class for compliance score"""
        if score >= 0.8: return 'good'
        if score >= 0.6: return 'warning'
        return 'bad'

    def _get_risk_class(self, risk: str) -> str:
        """Get CSS class for risk level"""
        if risk == 'LOW': return 'good'
        if risk == 'MEDIUM': return 'warning'
        return 'bad'


# Global analytics engine instance
analytics_engine = AnalyticsEngine()


def get_analytics_engine() -> AnalyticsEngine:
    """Get global analytics engine instance"""
    return analytics_engine