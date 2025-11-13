"""
Test Configuration Module
==========================
Tests for config/config.py to ensure paths and settings are properly configured.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    PROJECT_ROOT,
    DATA_DIR,
    OUTPUT_DIR,
    MODELS_DIR,
    DOCS_DIR,
    RAW_DATA,
    PROCESSED_DATA,
    OUTPUT_FILES,
    MODEL_FILES,
    get_path,
)


def test_project_root():
    """Test that PROJECT_ROOT is correctly set."""
    assert PROJECT_ROOT.exists(), "Project root should exist"
    assert PROJECT_ROOT.is_dir(), "Project root should be a directory"
    print(f"✓ PROJECT_ROOT exists: {PROJECT_ROOT}")


def test_directory_paths():
    """Test that all directory paths are Path objects."""
    directories = {
        "DATA_DIR": DATA_DIR,
        "OUTPUT_DIR": OUTPUT_DIR,
        "MODELS_DIR": MODELS_DIR,
        "DOCS_DIR": DOCS_DIR,
    }
    
    for name, path in directories.items():
        assert isinstance(path, Path), f"{name} should be a Path object"
        # Note: directories may not exist yet, but should be valid paths
        print(f"✓ {name}: {path}")


def test_raw_data_paths():
    """Test that all raw data paths are defined."""
    expected_sources = [
        "worldbank", "dpwh", "jica", "ltfrb", "psa", 
        "sws", "openaq", "tomtom", "overpass", "uitp", 
        "adb", "congestion"
    ]
    
    for source in expected_sources:
        assert source in RAW_DATA, f"Missing raw data path for {source}"
        assert isinstance(RAW_DATA[source], Path), f"{source} should be a Path"
        print(f"✓ RAW_DATA[{source}]: {RAW_DATA[source]}")


def test_processed_data_paths():
    """Test that processed data paths are defined."""
    expected_processed = ["clean_panel", "clean_panel_train", "clean_panel_test"]
    
    for name in expected_processed:
        assert name in PROCESSED_DATA, f"Missing processed data path for {name}"
        assert isinstance(PROCESSED_DATA[name], Path), f"{name} should be a Path"
        print(f"✓ PROCESSED_DATA[{name}]: {PROCESSED_DATA[name]}")


def test_get_path_function():
    """Test the get_path helper function."""
    # Test valid paths
    try:
        path = get_path("raw", "worldbank")
        assert isinstance(path, Path), "get_path should return Path object"
        print(f"✓ get_path('raw', 'worldbank'): {path}")
    except Exception as e:
        assert False, f"get_path failed: {e}"
    
    # Test invalid category
    try:
        get_path("invalid", "worldbank")
        assert False, "Should raise ValueError for invalid category"
    except ValueError:
        print("✓ get_path correctly raises ValueError for invalid category")
    
    # Test invalid key
    try:
        get_path("raw", "invalid_key")
        assert False, "Should raise ValueError for invalid key"
    except ValueError:
        print("✓ get_path correctly raises ValueError for invalid key")


def test_config_structure():
    """Test that config file structure is valid."""
    # Check that all path dictionaries exist
    assert isinstance(RAW_DATA, dict), "RAW_DATA should be a dictionary"
    assert isinstance(PROCESSED_DATA, dict), "PROCESSED_DATA should be a dictionary"
    assert isinstance(OUTPUT_FILES, dict), "OUTPUT_FILES should be a dictionary"
    assert isinstance(MODEL_FILES, dict), "MODEL_FILES should be a dictionary"
    print("✓ All configuration dictionaries are properly structured")


def run_all_tests():
    """Run all tests."""
    tests = [
        test_project_root,
        test_directory_paths,
        test_raw_data_paths,
        test_processed_data_paths,
        test_get_path_function,
        test_config_structure,
    ]
    
    print("=" * 80)
    print("Running Configuration Tests")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for test in tests:
        test_name = test.__name__
        try:
            print(f"\n{test_name}:")
            test()
            passed += 1
            print(f"✅ {test_name} PASSED\n")
        except AssertionError as e:
            failed += 1
            print(f"❌ {test_name} FAILED: {e}\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}\n")
    
    print("=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

