"""
Machine Learning predictions for compliance scoring
"""
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os
from datetime import datetime, timedelta
from ..utils.logger import setup_module_logger


class CompliancePredictor:
    """Machine learning model for compliance score prediction"""

    def __init__(self):
        self.logger = setup_module_logger("ml_predictor")
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            'processing_time',
            'api_call_count',
            'data_quality_score',
            'employee_count',
            'contribution_count',
            'time_of_day',
            'day_of_week'
        ]

    def train_model(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train the compliance prediction model"""

        if len(historical_data) < 10:
            self.logger.warning("Insufficient data for training")
            return {'success': False, 'message': 'Insufficient training data'}

        # Prepare features and target
        X, y = self._prepare_training_data(historical_data)

        if len(X) == 0:
            return {'success': False, 'message': 'No valid training samples'}

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        self.is_trained = True

        # Save model
        self._save_model()

        result = {
            'success': True,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'mse': mse,
            'r2_score': r2,
            'feature_importance': self._get_feature_importance()
        }

        self.logger.info(f"Model trained successfully. R² = {r2:.3f}, MSE = {mse:.3f}")
        return result

    def predict_compliance(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict compliance score for new data"""

        if not self.is_trained:
            # Load existing model if available
            if not self._load_model():
                return {
                    'predicted_score': 0.5,  # Default fallback
                    'confidence': 0.0,
                    'method': 'fallback'
                }

        # Extract features
        feature_vector = self._extract_features(features)

        # Scale features
        feature_vector_scaled = self.scaler.transform([feature_vector])

        # Make prediction
        prediction = self.model.predict(feature_vector_scaled)[0]

        # Calculate confidence based on feature completeness
        confidence = self._calculate_prediction_confidence(features)

        # Ensure prediction is within bounds
        prediction = max(0.0, min(1.0, prediction))

        return {
            'predicted_score': float(prediction),
            'confidence': confidence,
            'method': 'ml_model',
            'feature_contribution': self._explain_prediction(feature_vector)
        }

    def _prepare_training_data(self, historical_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from historical results"""

        X = []
        y = []

        for record in historical_data:
            try:
                features = self._extract_features(record)
                target = record.get('confidence_score', 0.0)

                # Only include records with valid targets
                if 0.0 <= target <= 1.0:
                    X.append(features)
                    y.append(target)

            except (KeyError, ValueError, TypeError) as e:
                self.logger.debug(f"Skipping invalid training record: {e}")
                continue

        return np.array(X), np.array(y)

    def _extract_features(self, data: Dict[str, Any]) -> List[float]:
        """Extract feature vector from data"""

        features = []

        # Processing time
        processing_time = data.get('processing_time', 1.0)
        features.append(min(processing_time, 60.0))  # Cap at 60 seconds

        # API call count (estimated)
        api_errors = data.get('api_errors', [])
        api_call_count = 1 + len(api_errors)  # Base call + error retries
        features.append(min(api_call_count, 10))  # Cap at 10 calls

        # Data quality score
        quality_map = {'HIGH': 1.0, 'MEDIUM': 0.7, 'LOW': 0.3, 'UNKNOWN': 0.0}
        quality = data.get('data_quality', 'UNKNOWN')
        features.append(quality_map.get(quality, 0.0))

        # Employee count (estimated from mock data patterns)
        # This would be more accurate with real data
        employee_count = np.random.poisson(5)  # Placeholder
        features.append(min(employee_count, 50))

        # Contribution count (estimated)
        contribution_count = employee_count * 12  # 12 months
        features.append(min(contribution_count, 600))

        # Time-based features
        now = datetime.now()
        features.append(now.hour / 24.0)  # Time of day (0-1)
        features.append(now.weekday() / 6.0)  # Day of week (0-1)

        return features

    def _calculate_prediction_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in the prediction"""

        confidence = 1.0

        # Reduce confidence for missing or extreme values
        if features.get('processing_time', 0) > 30:  # Very slow
            confidence *= 0.8

        if len(features.get('api_errors', [])) > 2:  # Many API errors
            confidence *= 0.7

        if features.get('data_quality') in ['LOW', 'UNKNOWN']:
            confidence *= 0.9

        return confidence

    def _explain_prediction(self, feature_vector: List[float]) -> Dict[str, float]:
        """Explain feature contributions to prediction"""

        if not hasattr(self.model, 'feature_importances_'):
            return {}

        importance = self.model.feature_importances_
        explanation = {}

        for i, (feature_name, importance_score) in enumerate(zip(self.feature_names, importance)):
            if i < len(feature_vector):
                contribution = importance_score * feature_vector[i]
                explanation[feature_name] = contribution

        return explanation

    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""

        if not self.model or not hasattr(self.model, 'feature_importances_'):
            return {}

        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))

    def _save_model(self):
        """Save trained model to disk"""

        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'trained_at': datetime.now().isoformat()
            }

            os.makedirs('models', exist_ok=True)
            with open('models/compliance_predictor.pkl', 'wb') as f:
                pickle.dump(model_data, f)

            self.logger.info("Model saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")

    def _load_model(self) -> bool:
        """Load trained model from disk"""

        try:
            model_path = 'models/compliance_predictor.pkl'
            if not os.path.exists(model_path):
                return False

            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data.get('feature_names', self.feature_names)
            self.is_trained = True

            self.logger.info("Model loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics and metadata"""

        if not self.is_trained:
            return {'status': 'not_trained'}

        return {
            'status': 'trained',
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'feature_importance': self._get_feature_importance(),
            'scaler_mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else None,
            'scaler_scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else None
        }


class RiskAssessmentEngine:
    """Risk assessment engine using ML predictions"""

    def __init__(self):
        self.predictor = CompliancePredictor()
        self.logger = setup_module_logger("risk_assessment")

    def assess_risk(self, processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess compliance risk for a processing result"""

        # Get ML prediction
        prediction = self.predictor.predict_compliance(processing_result)

        predicted_score = prediction['predicted_score']
        confidence = prediction['confidence']

        # Determine risk level
        if predicted_score >= 0.8:
            risk_level = 'LOW'
            risk_score = 0.2
        elif predicted_score >= 0.6:
            risk_level = 'MEDIUM'
            risk_score = 0.5
        else:
            risk_level = 'HIGH'
            risk_score = 0.8

        # Adjust risk based on prediction confidence
        risk_score = risk_score * (2 - confidence)  # Lower confidence = higher risk

        # Consider additional factors
        risk_factors = self._identify_risk_factors(processing_result)

        return {
            'predicted_compliance_score': predicted_score,
            'risk_level': risk_level,
            'risk_score': min(1.0, risk_score),
            'prediction_confidence': confidence,
            'risk_factors': risk_factors,
            'recommendations': self._generate_risk_recommendations(risk_level, risk_factors)
        }

    def _identify_risk_factors(self, result: Dict[str, Any]) -> List[str]:
        """Identify risk factors from processing result"""

        factors = []

        # Processing time risk
        if result.get('processing_time', 0) > 10:
            factors.append('slow_processing')

        # API errors risk
        api_errors = result.get('api_errors', [])
        if len(api_errors) > 0:
            factors.append('api_errors')

        # Data quality risk
        if result.get('data_quality') in ['LOW', 'UNKNOWN']:
            factors.append('poor_data_quality')

        # Source risk
        if result.get('source') == 'generated':
            factors.append('generated_data_fallback')

        return factors

    def _generate_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation recommendations"""

        recommendations = []

        if risk_level == 'HIGH':
            recommendations.append("Immediate review required - high compliance risk detected")
        elif risk_level == 'MEDIUM':
            recommendations.append("Monitor closely - medium compliance risk")

        # Factor-specific recommendations
        if 'slow_processing' in risk_factors:
            recommendations.append("Investigate performance bottlenecks")

        if 'api_errors' in risk_factors:
            recommendations.append("Check API connectivity and implement retry logic")

        if 'poor_data_quality' in risk_factors:
            recommendations.append("Improve data validation and quality checks")

        if 'generated_data_fallback' in risk_factors:
            recommendations.append("Verify API endpoints and connectivity")

        return recommendations


# Global instances
compliance_predictor = CompliancePredictor()
risk_assessment_engine = RiskAssessmentEngine()


def get_compliance_predictor() -> CompliancePredictor:
    """Get global compliance predictor instance"""
    return compliance_predictor


def get_risk_assessment_engine() -> RiskAssessmentEngine:
    """Get global risk assessment engine instance"""
    return risk_assessment_engine