"""
World Bank Data Collection
============================
Fetches economic and infrastructure indicators from the World Bank API.
"""

import pandas as pd
import pandas_datareader.wb as wb
import sys
from pathlib import Path
import time

# Add project root to path for config import
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config import DATA_DIR, RAW_DATA

# Define indicators relevant to transport and urban development
indicators = {
    'NY.GDP.PCAP.CD': 'gdp_per_capita',
    'NY.GDP.MKTP.CD': 'gdp_current_usd',
    'SP.POP.TOTL': 'population',
    'SP.URB.TOTL.IN.ZS': 'urban_population_pct',
    'IS.ROD.TOTL.KM': 'road_length_km',
    'IS.ROD.PAVE.ZS': 'paved_roads_pct',
    'EN.ATM.PM25.MC.M3': 'pm25_annual_mean',
    'EN.CO2.TRAN.ZS': 'co2_from_transport_pct',
    'IS.RRS.TOTL.KM': 'rail_lines_km',
    'SL.UEM.TOTL.ZS': 'unemployment_rate'
}

print("Fetching World Bank data for all countries (2000-2024)...")
print(f"Indicators: {len(indicators)}")

try:
    # Fetch data for all countries from 2000 to 2024
    # Note: Some indicators may not be available for all years/countries
    data = wb.download(
        indicator=list(indicators.keys()), 
        country='all', 
        start=2000, 
        end=2024
    )
    
    # Rename columns to more readable names
    data = data.rename(columns=indicators)
    
    # Reset index to have country and year as columns
    data = data.reset_index()
    
    print(f"Successfully fetched data: {len(data)} records")
    print(f"Countries: {data['country'].nunique()}")
    print(f"Years: {sorted(data['year'].unique())}")
    
    # Save to CSV
    output_path = RAW_DATA["worldbank"]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    
    print(f"\nWorld Bank data saved to {output_path}")
    
    # Print some sample statistics
    print("\nSample statistics:")
    print(f"- Philippines records: {len(data[data['country'] == 'Philippines'])}")
    print(f"- Columns with data: {data.notna().sum().to_dict()}")
    
except Exception as e:
    print(f"Error fetching World Bank data: {e}")
    print("\nAttempting to fetch with fewer indicators...")
    
    # Fallback: try with core indicators only
    core_indicators = {
        'NY.GDP.PCAP.CD': 'gdp_per_capita',
        'SP.POP.TOTL': 'population',
        'SP.URB.TOTL.IN.ZS': 'urban_population_pct',
        'EN.ATM.PM25.MC.M3': 'pm25_annual_mean'
    }
    
    try:
        data = wb.download(
            indicator=list(core_indicators.keys()), 
            country='all', 
            start=2000, 
            end=2024
        )
        
        data = data.rename(columns=core_indicators)
        data = data.reset_index()
        
        output_path = RAW_DATA["worldbank"]
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data.to_csv(output_path, index=False)
        
        print(f"World Bank data saved with core indicators: {len(data)} records")
        
    except Exception as e2:
        print(f"Error with core indicators: {e2}")
        print("Unable to fetch World Bank data")