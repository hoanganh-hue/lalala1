"""
Centralized logging system for VSS Integration System
"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from ..config.settings import config


class VSSLogger:
    """Centralized logger for VSS Integration System"""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def get_logger(cls, name: str = "vss_integration") -> logging.Logger:
        """Get or create logger instance"""
        if not cls._initialized:
            cls._setup_logging()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def _setup_logging(cls):
        """Setup logging configuration"""
        log_config = config.get_logging_config()
        
        # Create logs directory
        log_file = log_config.get('file', 'logs/vss_integration.log')
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_config.get('level', 'INFO')))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=log_config.get('backup_count', 5)
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
        
        # Error file handler
        error_file = log_path.parent / f"{log_path.stem}_error{log_path.suffix}"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=log_config.get('backup_count', 5)
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        root_logger.addHandler(error_handler)
        
        cls._initialized = True
    
    @classmethod
    def setup_module_logger(cls, module_name: str) -> logging.Logger:
        """Setup logger for specific module"""
        logger = cls.get_logger(f"vss_integration.{module_name}")
        return logger


def get_logger(name: str = "vss_integration") -> logging.Logger:
    """Convenience function to get logger"""
    return VSSLogger.get_logger(name)


def setup_module_logger(module_name: str) -> logging.Logger:
    """Convenience function to setup module logger"""
    return VSSLogger.setup_module_logger(module_name)
