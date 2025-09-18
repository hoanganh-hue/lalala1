#!/usr/bin/env python3
"""
Excel Processor CLI - Command Line Interface for VSS Integration System
"""
import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.processors.excel_integration_processor import ExcelIntegrationProcessor
from src.utils.logger import get_logger


def process_excel_file(input_file: str, output_dir: str = "data/output", 
                      max_workers: int = 4, use_real_apis: bool = True):
    """Process Excel file through VSS integration"""
    logger = get_logger("excel_cli")
    
    try:
        print(f"🚀 Processing Excel file: {input_file}")
        print(f"📁 Output directory: {output_dir}")
        print(f"👥 Workers: {max_workers}")
        print(f"🌐 Real APIs: {'Yes' if use_real_apis else 'No'}")
        print("-" * 50)
        
        # Initialize processor
        processor = ExcelIntegrationProcessor(max_workers=max_workers, use_real_apis=use_real_apis)
        
        # Process file
        start_time = datetime.now()
        summary = processor.process_excel_file(input_file, output_dir)
        end_time = datetime.now()
        
        # Display results
        results = summary['processing_results']
        print(f"\n📈 Processing Results:")
        print(f"   📋 Total processed: {results['total_processed']}")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📊 Success rate: {results['success_rate']:.1f}%")
        print(f"   💎 Average confidence: {results['average_confidence']:.3f}")
        print(f"   ⏱️ Processing time: {results['processing_time']:.2f}s")
        print(f"   ⚡ Processing rate: {results['processing_rate']:.2f} MST/s")
        
        # Output files
        output_files = summary['output_files']
        print(f"\n📁 Output Files:")
        print(f"   📊 Summary Report: {output_files['summary_report']}")
        print(f"   📋 Detailed Report: {output_files['detailed_report']}")
        
        # Save summary
        summary_file = os.path.join(output_dir, f"processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Summary JSON: {summary_file}")
        print(f"\n✅ Processing completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(f"\n❌ Processing failed: {str(e)}")
        return False


def validate_excel_file(input_file: str):
    """Validate Excel file"""
    try:
        print(f"🔍 Validating Excel file: {input_file}")
        
        processor = ExcelIntegrationProcessor()
        validation = processor.validate_input_file(input_file)
        
        print(f"\n📊 Validation Results:")
        print(f"   ✅ Valid: {validation['valid']}")
        print(f"   📋 Total rows: {validation['total_rows']}")
        print(f"   🏢 MST column: {validation['mst_column']}")
        print(f"   🔢 MST count: {validation['mst_count']}")
        
        if validation['columns']:
            print(f"   📝 Columns: {', '.join(validation['columns'])}")
        
        if validation['errors']:
            print(f"   ❌ Errors: {', '.join(validation['errors'])}")
        
        return validation['valid']
        
    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        return False


def create_template(template_path: str = "data/templates/mst_input_template.xlsx"):
    """Create input template"""
    try:
        print(f"📝 Creating input template: {template_path}")
        
        processor = ExcelIntegrationProcessor()
        result_path = processor.create_input_template(template_path)
        
        print(f"✅ Template created successfully: {result_path}")
        return True
        
    except Exception as e:
        print(f"❌ Template creation failed: {str(e)}")
        return False


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="VSS Integration System - Excel Processor CLI")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process Excel file')
    process_parser.add_argument('input_file', help='Input Excel file path')
    process_parser.add_argument('--output-dir', default='data/output', help='Output directory')
    process_parser.add_argument('--workers', type=int, default=4, help='Number of workers')
    process_parser.add_argument('--no-real-apis', action='store_true', help='Use generated data instead of real APIs')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate Excel file')
    validate_parser.add_argument('input_file', help='Input Excel file path')
    
    # Template command
    template_parser = subparsers.add_parser('template', help='Create input template')
    template_parser.add_argument('--output', default='data/templates/mst_input_template.xlsx', help='Template output path')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo workflow')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create necessary directories
    Path("data/input").mkdir(parents=True, exist_ok=True)
    Path("data/output").mkdir(parents=True, exist_ok=True)
    Path("data/templates").mkdir(parents=True, exist_ok=True)
    
    try:
        if args.command == 'process':
            success = process_excel_file(
                args.input_file, 
                args.output_dir, 
                args.workers, 
                not args.no_real_apis
            )
            return 0 if success else 1
            
        elif args.command == 'validate':
            success = validate_excel_file(args.input_file)
            return 0 if success else 1
            
        elif args.command == 'template':
            success = create_template(args.output)
            return 0 if success else 1
            
        elif args.command == 'demo':
            # Import and run demo
            from excel_workflow_demo import main as demo_main
            success = demo_main()
            return 0 if success else 1
            
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
