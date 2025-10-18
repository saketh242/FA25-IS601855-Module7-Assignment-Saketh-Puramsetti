#!/usr/bin/env python3
"""
Test runner script for the QR Code Generator application.
This script provides an easy way to run tests with different configurations.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """
    Run tests with the specified configuration.
    
    Args:
        test_type (str): Type of tests to run ('all', 'unit', 'integration')
        verbose (bool): Whether to run tests in verbose mode
        coverage (bool): Whether to generate coverage report
    """
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=main", "--cov-report=html", "--cov-report=term"])
    
    # Select test files based on type
    if test_type == "unit":
        cmd.append("test_qr_generator.py::TestQRCodeGenerator")
    elif test_type == "integration":
        cmd.append("test_qr_generator.py::TestQRCodeIntegration")
    else:  # all
        cmd.append("test_qr_generator.py")
    
    # Add additional pytest options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "-x",  # Stop on first failure
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install test dependencies:")
        print("pip install -r requirements.txt")
        return False


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run tests for QR Code Generator")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration"], 
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🧪 QR Code Generator Test Runner")
    print("=" * 50)
    print(f"Test type: {args.type}")
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    print()
    
    # Run the tests
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
