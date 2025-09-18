"""
Internationalization (i18n) support for multi-language interface
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.logger import setup_module_logger


class I18nManager:
    """Internationalization manager for multi-language support"""

    def __init__(self, default_locale: str = 'vi'):
        self.logger = setup_module_logger("i18n")
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations = {}
        self.supported_locales = ['vi', 'en']

        self._load_translations()

    def _load_translations(self):
        """Load translation files"""

        locales_dir = Path(__file__).parent.parent.parent / 'locales'
        locales_dir.mkdir(exist_ok=True)

        for locale in self.supported_locales:
            translation_file = locales_dir / f'{locale}.json'
            if translation_file.exists():
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[locale] = json.load(f)
                    self.logger.info(f"Loaded translations for {locale}")
                except Exception as e:
                    self.logger.error(f"Failed to load {locale} translations: {e}")
                    self.translations[locale] = {}
            else:
                # Create default translation file
                self._create_default_translations(locale)
                self.translations[locale] = {}

    def _create_default_translations(self, locale: str):
        """Create default translation files"""

        locales_dir = Path(__file__).parent.parent.parent / 'locales'
        locales_dir.mkdir(exist_ok=True)

        if locale == 'vi':
            translations = {
                # UI Elements
                "app_title": "Hệ thống Tích hợp VSS",
                "mst_input_label": "Mã số thuế (MST):",
                "mst_placeholder": "Nhập MST (10-13 chữ số)",
                "format_label": "Định dạng kết quả:",
                "format_summary": "Tóm tắt",
                "format_detailed": "Chi tiết",
                "format_full": "Đầy đủ",
                "process_button": "Xử lý MST",
                "processing": "Đang xử lý...",
                "stats_title": "Thống kê",
                "total_requests": "Tổng requests",
                "successful_requests": "Thành công",
                "avg_response_time": "Thời gian TB",

                # Messages
                "success_title": "✅ Kết quả xử lý",
                "error_title": "❌ Lỗi xử lý",
                "mst_label": "MST:",
                "status_label": "Trạng thái:",
                "confidence_label": "Điểm tin cậy:",
                "quality_label": "Chất lượng dữ liệu:",
                "time_label": "Thời gian xử lý:",
                "source_label": "Nguồn dữ liệu:",
                "error_label": "Lỗi:",
                "success_status": "Thành công",
                "api_source": "API thực",
                "mixed_source": "Kết hợp",
                "generated_source": "Dữ liệu giả lập",

                # Quality levels
                "quality_high": "CAO",
                "quality_medium": "TRUNG BÌNH",
                "quality_low": "THẤP",
                "quality_unknown": "KHÔNG XÁC ĐỊNH",

                # Errors
                "mst_required": "MST là bắt buộc",
                "invalid_mst": "Định dạng MST không hợp lệ (phải có 10-13 chữ số)",
                "connection_error": "Lỗi kết nối",
                "timeout_error": "Quá thời gian chờ",
                "api_error": "Lỗi API",

                # Analytics
                "analytics_title": "Phân tích nâng cao",
                "performance_tab": "Hiệu suất",
                "quality_tab": "Chất lượng",
                "compliance_tab": "Tuân thủ",
                "trends_tab": "Xu hướng",
                "throughput_label": "Thông lượng:",
                "efficiency_label": "Hiệu quả:",
                "compliance_score": "Điểm tuân thủ:",
                "risk_level": "Mức độ rủi ro:",
                "recommendations": "Khuyến nghị",

                # Risk levels
                "risk_low": "THẤP",
                "risk_medium": "TRUNG BÌNH",
                "risk_high": "CAO",

                # Navigation
                "home": "Trang chủ",
                "analytics": "Phân tích",
                "settings": "Cài đặt",
                "help": "Trợ giúp",
                "about": "Giới thiệu"
            }
        elif locale == 'en':
            translations = {
                # UI Elements
                "app_title": "VSS Integration System",
                "mst_input_label": "Tax Code (MST):",
                "mst_placeholder": "Enter MST (10-13 digits)",
                "format_label": "Result format:",
                "format_summary": "Summary",
                "format_detailed": "Detailed",
                "format_full": "Full",
                "process_button": "Process MST",
                "processing": "Processing...",
                "stats_title": "Statistics",
                "total_requests": "Total requests",
                "successful_requests": "Successful",
                "avg_response_time": "Avg response time",

                # Messages
                "success_title": "✅ Processing Result",
                "error_title": "❌ Processing Error",
                "mst_label": "MST:",
                "status_label": "Status:",
                "confidence_label": "Confidence score:",
                "quality_label": "Data quality:",
                "time_label": "Processing time:",
                "source_label": "Data source:",
                "error_label": "Error:",
                "success_status": "Success",
                "api_source": "Real API",
                "mixed_source": "Mixed",
                "generated_source": "Generated data",

                # Quality levels
                "quality_high": "HIGH",
                "quality_medium": "MEDIUM",
                "quality_low": "LOW",
                "quality_unknown": "UNKNOWN",

                # Errors
                "mst_required": "MST is required",
                "invalid_mst": "Invalid MST format (must be 10-13 digits)",
                "connection_error": "Connection error",
                "timeout_error": "Timeout error",
                "api_error": "API error",

                # Analytics
                "analytics_title": "Advanced Analytics",
                "performance_tab": "Performance",
                "quality_tab": "Quality",
                "compliance_tab": "Compliance",
                "trends_tab": "Trends",
                "throughput_label": "Throughput:",
                "efficiency_label": "Efficiency:",
                "compliance_score": "Compliance score:",
                "risk_level": "Risk level:",
                "recommendations": "Recommendations",

                # Risk levels
                "risk_low": "LOW",
                "risk_medium": "MEDIUM",
                "risk_high": "HIGH",

                # Navigation
                "home": "Home",
                "analytics": "Analytics",
                "settings": "Settings",
                "help": "Help",
                "about": "About"
            }

        # Save to file
        translation_file = locales_dir / f'{locale}.json'
        try:
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Created default translations for {locale}")
        except Exception as e:
            self.logger.error(f"Failed to create {locale} translations: {e}")

    def set_locale(self, locale: str) -> bool:
        """Set current locale"""

        if locale not in self.supported_locales:
            self.logger.warning(f"Unsupported locale: {locale}")
            return False

        if locale not in self.translations:
            self.logger.warning(f"Translations not loaded for: {locale}")
            return False

        self.current_locale = locale
        self.logger.info(f"Locale changed to: {locale}")
        return True

    def get_locale(self) -> str:
        """Get current locale"""
        return self.current_locale

    def translate(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """Translate a key to current locale"""

        target_locale = locale or self.current_locale

        # Get translation
        translation = self._get_translation(key, target_locale)

        # Apply formatting if kwargs provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Translation formatting failed for key '{key}': {e}")

        return translation

    def _get_translation(self, key: str, locale: str) -> str:
        """Get translation for a key"""

        # Try current locale first
        if locale in self.translations and key in self.translations[locale]:
            return self.translations[locale][key]

        # Try default locale
        if self.default_locale in self.translations and key in self.translations[self.default_locale]:
            return self.translations[self.default_locale][key]

        # Return key if no translation found
        self.logger.debug(f"Translation not found for key: {key}")
        return key

    def get_available_locales(self) -> list:
        """Get list of available locales"""
        return self.supported_locales.copy()

    def add_translation(self, locale: str, key: str, value: str):
        """Add or update a translation"""

        if locale not in self.translations:
            self.translations[locale] = {}

        self.translations[locale][key] = value

        # Save to file
        locales_dir = Path(__file__).parent.parent.parent / 'locales'
        translation_file = locales_dir / f'{locale}.json'

        try:
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[locale], f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save translation: {e}")

    def get_all_translations(self, locale: Optional[str] = None) -> Dict[str, str]:
        """Get all translations for a locale"""

        target_locale = locale or self.current_locale

        if target_locale in self.translations:
            return self.translations[target_locale].copy()

        return {}

    def detect_locale_from_request(self, accept_language: str) -> str:
        """Detect locale from HTTP Accept-Language header"""

        if not accept_language:
            return self.default_locale

        # Parse Accept-Language header
        languages = [lang.split(';')[0].strip().lower() for lang in accept_language.split(',')]

        # Find best match
        for lang in languages:
            # Exact match
            if lang in self.supported_locales:
                return lang

            # Language prefix match (e.g., 'en-US' -> 'en')
            lang_prefix = lang.split('-')[0]
            if lang_prefix in self.supported_locales:
                return lang_prefix

        return self.default_locale


# Global i18n manager instance
i18n_manager = I18nManager()


def get_i18n_manager() -> I18nManager:
    """Get global i18n manager instance"""
    return i18n_manager


def _(key: str, **kwargs) -> str:
    """Convenience function for translation"""
    return i18n_manager.translate(key, **kwargs)


# Initialize default translations
if __name__ != '__main__':
    # This will create default translation files when module is first imported
    pass