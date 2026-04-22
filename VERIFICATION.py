"""
VERIFICATION CHECKLIST — Centro de Mando v2.0
Run this after setup to verify all components are ready
"""

import os
import sys

def check_file_exists(path):
    """Check if file exists."""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {path}")
    return exists

def check_directory_exists(path):
    """Check if directory exists."""
    exists = os.path.isdir(path)
    status = "✓" if exists else "✗"
    print(f"{status} {path}/")
    return exists

def main():
    print("=" * 60)
    print("CENTRO DE MANDO v2.0 — Verification Checklist")
    print("=" * 60)
    
    print("\n1. Directory Structure:")
    dirs_ok = all([
        check_directory_exists("utils"),
        check_directory_exists("components"),
        check_directory_exists("pages"),
        check_directory_exists(".streamlit"),
    ])
    
    print("\n2. Core Files:")
    files_ok = all([
        check_file_exists("app.py"),
        check_file_exists("requirements.txt"),
        check_file_exists("README.md"),
    ])
    
    print("\n3. Utils Module:")
    utils_ok = all([
        check_file_exists("utils/__init__.py"),
        check_file_exists("utils/constants.py"),
        check_file_exists("utils/database.py"),
        check_file_exists("utils/calculations.py"),
        check_file_exists("utils/excel_loader.py"),
    ])
    
    print("\n4. Components Module:")
    components_ok = all([
        check_file_exists("components/__init__.py"),
        check_file_exists("components/header.py"),
        check_file_exists("components/sidebar.py"),
    ])
    
    print("\n5. Pages Module:")
    pages_ok = all([
        check_file_exists("pages/__init__.py"),
        check_file_exists("pages/dashboard.py"),
        check_file_exists("pages/training.py"),
        check_file_exists("pages/nutrition.py"),
        check_file_exists("pages/biometrics.py"),
    ])
    
    print("\n6. Configuration:")
    config_ok = all([
        check_file_exists(".streamlit/secrets.toml"),
    ])
    
    print("\n7. Optional (Bootstrap):")
    optional_ok = check_file_exists("Mesociclo Neil.xlsx")
    
    print("\n" + "=" * 60)
    if all([dirs_ok, files_ok, utils_ok, components_ok, pages_ok, config_ok]):
        print("✓ ALL REQUIRED FILES PRESENT")
        print("\nNEXT STEPS:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run: streamlit run app.py")
        print("3. Open: http://localhost:8501")
        return 0
    else:
        print("✗ MISSING FILES — See above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
