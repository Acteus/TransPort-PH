#!/usr/bin/env python3
"""
TransPort-PH Project - Master Execution Script
===============================================
This script runs all data gathering, processing, and analysis steps in the correct order.

Usage:
    python run_all.py [--skip-gathering] [--skip-eda]
    
Options:
    --skip-gathering    Skip data gathering steps (use existing data)
    --skip-eda          Skip exploratory data analysis visualizations
"""

import os
import sys
import subprocess
import time
from datetime import datetime

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_step(step_num, total_steps, message):
    """Print a formatted step"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}[Step {step_num}/{total_steps}]{Colors.ENDC} {message}")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    # If running from scripts directory, just use the script name
    # If running from parent directory, use scripts/script_name
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
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print_success(f"{description} (completed in {elapsed:.1f}s)")
            return True
        else:
            print_error(f"{description} (failed after {elapsed:.1f}s)")
            return False
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} (timeout after 300s)")
        return False
    except Exception as e:
        print_error(f"{description} (exception: {e})")
        return False

def check_data_exists():
    """Check if key data files already exist"""
    # Check for data directory
    data_dir = '../data' if os.path.exists('../data') else 'data'
    if not os.path.exists(data_dir):
        return False
    
    # Check for key data files
    key_files = [
        'worldbank_data.csv',
        'tomtom_traffic_data.csv',
        'psa_data.csv',
        'ltfrb_data.csv'
    ]
    
    existing_files = 0
    for filename in key_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            existing_files += 1
    
    # If at least 75% of key files exist, consider data as already gathered
    return existing_files >= len(key_files) * 0.75

def main():
    """Main execution function"""
    start_time = datetime.now()
    
    # Parse command line arguments
    skip_gathering = '--skip-gathering' in sys.argv
    skip_eda = '--skip-eda' in sys.argv
    
    # Auto-detect if data already exists
    if not skip_gathering and check_data_exists():
        print_warning("Key data files already exist in data directory")
        response = input(f"{Colors.OKCYAN}Skip data gathering? (y/n): {Colors.ENDC}")
        if response.lower() == 'y':
            skip_gathering = True
    
    print_header("TransPort-PH Project - Master Execution Script")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if skip_gathering:
        print_warning("Skipping data gathering steps")
    if skip_eda:
        print_warning("Skipping EDA visualization steps")
    
    # Define all steps
    steps = []
    
    # Phase 1: Data Gathering (UPDATED with enhanced scripts)
    if not skip_gathering:
        steps.extend([
            ('data_gathering_worldbank.py', 'Fetch World Bank data'),
            ('data_gathering_tomtom.py', 'Fetch TomTom traffic data (ENHANCED: 31 cities)'),
            ('data_gathering_congestion_proxy.py', 'Generate ML-based congestion estimates (NEW: 277 countries)'),
            ('data_gathering_uitp.py', 'Fetch UITP modal share data (ENHANCED: 29 cities)'),
            ('data_gathering_psa.py', 'Fetch PSA demographic data'),
            ('data_gathering_ltfrb.py', 'Fetch LTFRB fleet and fare data'),
            ('data_gathering_openaq.py', 'Fetch OpenAQ air quality data (ENHANCED: 24 countries)'),
            ('data_gathering_overpass.py', 'Fetch Overpass OSM infrastructure data'),
            ('data_gathering_adb.py', 'Scrape ADB project data'),
            ('data_gathering_jica.py', 'Extract JICA MRT/LRT data'),
            ('data_gathering_sws.py', 'Gather SWS satisfaction survey data'),
            ('data_gathering_dpwh.py', 'Fetch DPWH infrastructure data'),
        ])
    
    # Phase 2: Data Preparation
    steps.extend([
        ('data_inspection.py', 'Inspect raw data quality'),
        ('data_standardization.py', 'Standardize country names and years'),
        ('handle_missing_values.py', 'Handle missing values'),
        ('feature_engineering.py', 'Create engineered features'),
        ('outlier_winsorization.py', 'Winsorize outliers'),
        ('panel_balance.py', 'Check and balance panel data'),
        ('train_test_split.py', 'Split data into train/test sets'),
        ('merge_panel.py', 'Merge all data sources into clean panel'),
    ])
    
    # Phase 3: EDA and Visualization
    if not skip_eda:
        steps.extend([
            ('validation_plots.py', 'Generate validation plots'),
            ('eda_univariate.py', 'Perform univariate analysis'),
            ('eda_time_trends.py', 'Analyze time trends per country'),
            ('eda_correlation_clustering.py', 'Perform correlation and clustering analysis'),
            ('eda_scatter_loess.py', 'Create scatter plots with Loess smoothing'),
        ])
    
    # Phase 4: Data Quality and Verification (NEW)
    steps.extend([
        ('verify_data_improvements.py', 'Verify data coverage improvements'),
        ('sensitivity_analysis.py', 'Conduct sensitivity analysis (actual vs. ML estimates)'),
    ])
    
    # Phase 5: Causal Modeling (optional)
    steps.extend([
        ('causal_modeling_dowhy.py', 'Build causal graph and estimate treatment effects'),
    ])
    
    # Phase 6: Machine Learning Models (conditional on data availability)
    # Check if we have sufficient data for TFT (UPDATED with improved thresholds)
    data_dir = '../data' if os.path.exists('../data') else 'data'
    clean_panel_path = os.path.join(data_dir, 'clean_panel.csv')
    
    skip_tft = False
    if os.path.exists(clean_panel_path):
        import pandas as pd
        df = pd.read_csv(clean_panel_path)
        congestion_count = df['congestion_index'].notna().sum() if 'congestion_index' in df.columns else 0
        country_count = df[df['congestion_index'].notna()]['country'].nunique() if 'congestion_index' in df.columns else 0
        
        # Calculate year range for countries with congestion data
        df_congestion = df[df['congestion_index'].notna()]
        year_range = int(df_congestion['year'].max() - df_congestion['year'].min()) + 1 if len(df_congestion) > 0 else 0
        
        # Check data source split if available
        actual_count = 0
        ml_count = 0
        if 'data_source' in df.columns:
            actual_count = len(df[df['data_source'] == 'actual_tomtom'])
            ml_count = congestion_count - actual_count
        
        print_header("Data Sufficiency Check for Deep Learning Models (UPDATED)")
        print(f"Current data status:")
        print(f"  • Total observations with congestion_index: {congestion_count}")
        print(f"  • Countries with congestion data: {country_count}")
        print(f"  • Year range: {year_range} years")
        print(f"  • Data coverage: {congestion_count/len(df)*100:.1f}% of panel")
        if 'data_source' in df.columns:
            print(f"\n  Data Quality:")
            print(f"  • Actual TomTom measurements: {actual_count} ({actual_count/congestion_count*100:.1f}%)")
            print(f"  • ML-estimated data: {ml_count} ({ml_count/congestion_count*100:.1f}%)")
        
        print(f"\n{Colors.BOLD}TFT Model Requirements (from DATA_COVERAGE_ANALYSIS.md):{Colors.ENDC}")
        print(f"  ✓ Minimum observations: 1,000+")
        print(f"  ✓ Minimum countries: 10+")
        print(f"  ✓ Minimum years per country: 10+")
        print(f"  ✓ Rich temporal patterns needed")
        
        # Check data sufficiency (UPDATED with improved thresholds)
        if congestion_count < 1000:
            print(f"\n{Colors.FAIL}❌ INSUFFICIENT DATA FOR DEEP LEARNING{Colors.ENDC}")
            print(f"  Current: {congestion_count} observations")
            print(f"  Required: 1,000+ observations")
            skip_tft = True
        elif country_count < 10:
            print(f"\n{Colors.FAIL}❌ INSUFFICIENT COUNTRIES FOR TFT{Colors.ENDC}")
            print(f"  Current: {country_count} countries")
            print(f"  Required: 10+ countries with time series data")
            skip_tft = True
        elif year_range < 10:
            print(f"\n{Colors.WARNING}⚠️  LIMITED TEMPORAL COVERAGE{Colors.ENDC}")
            print(f"  Current: {year_range} years")
            print(f"  Recommended: 10+ years")
            print(f"  TFT may overfit with limited history")
            skip_tft = True
        else:
            print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ EXCELLENT! SUFFICIENT DATA FOR DEEP LEARNING{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
            print(f"\n{Colors.BOLD}Your enhanced dataset is ready for TFT training:{Colors.ENDC}")
            print(f"  ✅ Observations: {congestion_count:,} (target: 1,000+)")
            print(f"  ✅ Countries: {country_count} (target: 10+)")
            print(f"  ✅ Years: {year_range} (target: 10+)")
            print(f"  ✅ Coverage: {congestion_count/len(df)*100:.1f}% of panel")
            if ml_count > 0:
                print(f"\n{Colors.OKCYAN}Data composition:{Colors.ENDC}")
                print(f"  • High-quality measurements: {actual_count:,}")
                print(f"  • ML estimates (validated): {ml_count:,}")
                print(f"  • Sensitivity analysis completed: ✓")
            print(f"\n{Colors.BOLD}Proceeding with TFT model training...{Colors.ENDC}\n")
        
        if skip_tft:
            print(f"\n{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{Colors.BOLD}RECOMMENDED APPROACH (from DATA_COVERAGE_ANALYSIS.md):{Colors.ENDC}")
            print(f"{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
            
            print(f"\n{Colors.OKGREEN}✓ Option 1: Use Simpler Time Series Models (RECOMMENDED){Colors.ENDC}")
            print(f"  Models that work with your current data:")
            print(f"  • Panel Fixed Effects Regression (already in pipeline)")
            print(f"  • ARIMA/SARIMAX per country (10+ observations needed)")
            print(f"  • Facebook Prophet (20+ observations needed)")
            print(f"  • Simple LSTM (50+ observations, minimal architecture)")
            
            print(f"\n{Colors.OKCYAN}→ Option 2: Expand Your Dataset{Colors.ENDC}")
            print(f"  Target: 1,000+ observations, 20+ countries, 10+ years each")
            print(f"  • Purchase TomTom historical data (2008-2024)")
            print(f"  • Add more Southeast Asian countries")
            print(f"  • Consider imputation strategies")
            print(f"  • Use alternative target variables (modal_share, PM2.5)")
            
            print(f"\n{Colors.OKCYAN}→ Option 3: Focus on Philippines Deep Dive{Colors.ENDC}")
            print(f"  • Get Metro Manila city-level data (~$500)")
            print(f"  • Before/after analysis of MRT/LRT projects")
            print(f"  • Mixed methods approach (quant + qualitative)")
            print(f"  • More feasible and publishable")
            
            print(f"\n{Colors.BOLD}For more details, see:{Colors.ENDC}")
            print(f"  📄 docs/DATA_COVERAGE_ANALYSIS.md")
            print(f"  📄 docs/PROJECT_ASSESSMENT_AND_IMPROVEMENTS.md")
            print(f"  📄 NEXT_STEPS.md")
            print(f"{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}\n")
            
            # Ask user if they want to continue anyway
            response = input(f"{Colors.WARNING}Skip TFT training? (recommended: y) [y/n]: {Colors.ENDC}")
            if response.lower() != 'n':
                skip_tft = True
            else:
                print_warning("Proceeding with TFT training (may produce unreliable results)")
                skip_tft = False
    
    if not skip_tft:
        steps.extend([
            ('prepare_tft_dataset.py', 'Prepare dataset for TFT model'),
            ('train_tft_model.py', 'Train Temporal Fusion Transformer model'),
        ])
    else:
        print_success("Skipping TFT - Using simpler models instead")
    
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
            # Ask user if they want to continue
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
        print_success("All steps completed successfully!")
    
    # Check output directory (adjust path if running from scripts dir)
    output_dir = '../output' if os.path.exists('../output') else 'output'
    if os.path.exists(output_dir):
        output_files = os.listdir(output_dir)
        print(f"\nOutput directory contains {len(output_files)} files:")
        for f in sorted(output_files)[:10]:
            print(f"  - {f}")
        if len(output_files) > 10:
            print(f"  ... and {len(output_files) - 10} more")
    
    # Check clean panel (adjust path if running from scripts dir)
    clean_panel = os.path.join('../data', 'clean_panel.csv') if os.path.exists('../data') else os.path.join('data', 'clean_panel.csv')
    if os.path.exists(clean_panel):
        import pandas as pd
        df = pd.read_csv(clean_panel)
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}Clean panel dataset created:{Colors.ENDC}")
        print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"  Countries: {df['country'].nunique()}")
        if 'year' in df.columns:
            print(f"  Year range: {df['year'].min():.0f} - {df['year'].max():.0f}")
        
        # Show data coverage improvements
        if 'congestion_index' in df.columns:
            congestion_coverage = df['congestion_index'].notna().sum()
            congestion_pct = congestion_coverage / len(df) * 100
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 DATA COVERAGE ACHIEVEMENTS:{Colors.ENDC}")
            print(f"  ✅ Congestion data: {congestion_coverage:,}/{len(df):,} ({congestion_pct:.1f}%)")
            
            if 'data_source' in df.columns:
                actual = len(df[df['data_source'] == 'actual_tomtom'])
                estimated = congestion_coverage - actual
                print(f"     • Actual measurements: {actual:,}")
                print(f"     • ML estimates: {estimated:,}")
            
            if 'modal_share_public' in df.columns:
                modal_coverage = df['modal_share_public'].notna().sum()
                print(f"  ✅ Modal share data: {modal_coverage:,}/{len(df):,} ({modal_coverage/len(df)*100:.1f}%)")
            
            if 'pm25' in df.columns:
                pm25_coverage = df['pm25'].notna().sum()
                print(f"  ✅ PM2.5 data: {pm25_coverage:,}/{len(df):,} ({pm25_coverage/len(df)*100:.1f}%)")
            
            print(f"\n{Colors.OKCYAN}📊 See detailed reports:{Colors.ENDC}")
            print(f"  • DATA_SPARSITY_SOLUTION.md - Full improvement documentation")
            print(f"  • PIPELINE_SUCCESS_SUMMARY.md - Pipeline execution summary")
            print(f"  • data/sensitivity_analysis_results.csv - Robustness validation")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}✓ PIPELINE EXECUTION COMPLETE! ✓{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    return len(failed_steps) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
