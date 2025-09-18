#!/usr/bin/env python3
"""
Migration script to move legacy data to new structure
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime


def migrate_legacy_data():
    """Migrate legacy data to new structure"""
    print("🔄 Migrating legacy data to new structure...")
    
    # Source and destination paths
    source_dir = Path("..")  # Parent directory (where old files are)
    dest_dir = Path(".")
    
    # Create necessary directories
    (dest_dir / "data" / "input").mkdir(parents=True, exist_ok=True)
    (dest_dir / "data" / "output").mkdir(parents=True, exist_ok=True)
    (dest_dir / "data" / "backup").mkdir(parents=True, exist_ok=True)
    (dest_dir / "reports").mkdir(exist_ok=True)
    (dest_dir / "logs").mkdir(exist_ok=True)
    
    # Migrate JSON result files
    json_files = list(source_dir.glob("*.json"))
    migrated_count = 0
    
    for json_file in json_files:
        if json_file.name.startswith(("optimized_results", "batch_test_results", "quick_test")):
            try:
                # Copy to data/output
                dest_file = dest_dir / "data" / "output" / json_file.name
                shutil.copy2(json_file, dest_file)
                migrated_count += 1
                print(f"✅ Migrated: {json_file.name}")
            except Exception as e:
                print(f"❌ Failed to migrate {json_file.name}: {e}")
    
    # Migrate Excel files
    excel_files = list(source_dir.glob("*.xlsx"))
    for excel_file in excel_files:
        try:
            dest_file = dest_dir / "data" / "input" / excel_file.name
            shutil.copy2(excel_file, dest_file)
            migrated_count += 1
            print(f"✅ Migrated: {excel_file.name}")
        except Exception as e:
            print(f"❌ Failed to migrate {excel_file.name}: {e}")
    
    # Migrate report files
    report_files = list(source_dir.glob("*.md")) + list(source_dir.glob("*.docx")) + list(source_dir.glob("*.pdf"))
    for report_file in report_files:
        if "report" in report_file.name.lower():
            try:
                dest_file = dest_dir / "reports" / report_file.name
                shutil.copy2(report_file, dest_file)
                migrated_count += 1
                print(f"✅ Migrated: {report_file.name}")
            except Exception as e:
                print(f"❌ Failed to migrate {report_file.name}: {e}")
    
    # Create migration summary
    migration_summary = {
        "migration_date": datetime.now().isoformat(),
        "files_migrated": migrated_count,
        "source_directory": str(source_dir.absolute()),
        "destination_directory": str(dest_dir.absolute()),
        "migrated_files": {
            "json_results": len(list((dest_dir / "data" / "output").glob("*.json"))),
            "excel_inputs": len(list((dest_dir / "data" / "input").glob("*.xlsx"))),
            "reports": len(list((dest_dir / "reports").glob("*")))
        }
    }
    
    with open(dest_dir / "migration_summary.json", "w") as f:
        json.dump(migration_summary, f, indent=2)
    
    print(f"\n🎉 Migration completed!")
    print(f"📊 Files migrated: {migrated_count}")
    print(f"📁 JSON results: {migration_summary['migrated_files']['json_results']}")
    print(f"📊 Excel inputs: {migration_summary['migrated_files']['excel_inputs']}")
    print(f"📄 Reports: {migration_summary['migrated_files']['reports']}")
    print(f"📋 Summary saved: migration_summary.json")


if __name__ == "__main__":
    migrate_legacy_data()
