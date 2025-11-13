#!/usr/bin/env python3
"""
Run Project Improvements
=========================
Executes all newly created improvement scripts:
1. Transit investment validation
2. Philippines deep dive analysis
3. Model comparison framework

This script should be run after the main pipeline (run_all.py) has completed.
"""

import os
import sys
import subprocess
import time
from datetime import datetime

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_step(step_num, total_steps, message):
    print(f"{Colors.OKCYAN}{Colors.BOLD}[Step {step_num}/{total_steps}]{Colors.ENDC} {message}")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    if os.path.exists(script_name):
        script_path = script_name
    elif os.path.exists(os.path.join('scripts', script_name)):
        script_path = os.path.join('scripts', script_name)
    else:
        print_error(f"Script not found: {script_name}")
        return False
    
    print(f"  Running: {script_name}")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=False,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print_success(f"{description} (completed in {elapsed:.1f}s)")
            return True
        else:
            print_error(f"{description} (failed after {elapsed:.1f}s)")
            return False
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} (timeout after 600s)")
        return False
    except Exception as e:
        print_error(f"{description} (exception: {e})")
        return False

def check_prerequisites():
    """Check if main pipeline has been run"""
    data_dir = '../data' if os.path.exists('../data') else 'data'
    
    required_files = [
        'clean_panel.csv',
        'jica_mrt_lrt.csv',
        'ltfrb_data.csv',
        'adb_projects.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(data_dir, file)):
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

def main():
    """Main execution function"""
    start_time = datetime.now()
    
    print_header("TransPort-PH Project Improvements")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check prerequisites
    print("\nChecking prerequisites...")
    prereqs_ok, missing_files = check_prerequisites()
    
    if not prereqs_ok:
        print_error("Main pipeline must be run first!")
        print_warning(f"Missing files: {', '.join(missing_files)}")
        print_warning("Please run: python run_all.py")
        return False
    
    print_success("Prerequisites satisfied")
    
    # Define improvement scripts
    steps = [
        ('validate_transit_investment.py', 'Validate transit investment variable'),
        ('philippines_deep_dive.py', 'Philippines deep dive analysis'),
        ('model_comparison.py', 'Model comparison framework'),
    ]
    
    total_steps = len(steps)
    successful_steps = 0
    failed_steps = []
    
    # Execute all steps
    for i, (script, description) in enumerate(steps, 1):
        print_step(i, total_steps, description)
        
        if run_script(script, description):
            successful_steps += 1
        else:
            failed_steps.append((script, description))
            response = input(f"\n{Colors.WARNING}Continue despite error? (y/n): {Colors.ENDC}")
            if response.lower() != 'y':
                print_error("Execution aborted by user")
                break
    
    # Final report
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    print_header("Execution Summary")
    print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {elapsed}")
    print(f"\nTotal steps: {total_steps}")
    print(f"{Colors.OKGREEN}Successful: {successful_steps}{Colors.ENDC}")
    
    if failed_steps:
        print(f"{Colors.FAIL}Failed: {len(failed_steps)}{Colors.ENDC}")
        print(f"\nFailed steps:")
        for script, description in failed_steps:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} {description} ({script})")
    else:
        print_success("All improvement scripts completed successfully!")
    
    # List new outputs
    output_dir = '../output' if os.path.exists('../output') else 'output'
    data_dir = '../data' if os.path.exists('../data') else 'data'
    
    print("\n" + "=" * 80)
    print("NEW OUTPUTS GENERATED:")
    print("=" * 80)
    
    new_files = [
        ('Visualizations', output_dir, [
            'transit_investment_validation.png',
            'philippines/philippines_comprehensive_analysis.png',
            'model_comparison/model_comparison_results.png'
        ]),
        ('Reports', data_dir, [
            'transit_investment_validation_report.txt',
            'philippines_deep_dive_report.txt',
            'model_comparison_report.txt'
        ])
    ]
    
    for category, directory, files in new_files:
        print(f"\n{category}:")
        for file in files:
            filepath = os.path.join(directory, file)
            if os.path.exists(filepath):
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} (not found)")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Review the assessment document:")
    print("   docs/PROJECT_ASSESSMENT_AND_IMPROVEMENTS.md")
    print("\n2. Review the new reports in data/:")
    print("   - transit_investment_validation_report.txt")
    print("   - philippines_deep_dive_report.txt")
    print("   - model_comparison_report.txt")
    print("\n3. Examine the new visualizations in output/")
    print("\n4. Consider running the dashboard:")
    print("   streamlit run scripts/dashboard_app.py")
    print("\n5. Decide on strategic direction based on assessment")
    
    print(f"\n{Colors.BOLD}Improvement scripts execution complete!{Colors.ENDC}\n")
    
    return len(failed_steps) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

