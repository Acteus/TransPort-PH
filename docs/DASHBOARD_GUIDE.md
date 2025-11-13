# TransPort-PH Dashboard Guide

## 🚀 Quick Start

### Launch the Dashboard

```bash
cd /Users/gdullas/Desktop/Projects/Neural-Network-Projects/TransPort-PH/scripts
streamlit run dashboard_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📊 Dashboard Pages

### 1. 🏠 Overview
**Status**: ✅ Working
- Shows key metrics and scenario summaries
- Displays impact comparison across all scenarios
- Quick visual overview of baseline vs counterfactual results

### 2. ✨ Data Quality ⭐ NEW
**Status**: ✅ Working
- **Showcases your data improvements!**
- Before/After comparison (1.6% → 100% coverage)
- Data source breakdown (Actual vs ML estimates)
- Geographic coverage visualization
- Sensitivity analysis results
- Validation metrics

**This page demonstrates your solution to the data sparsity problem!**

### 3. 📊 Scenario Comparison
**Status**: ✅ Working (if simulation data exists)
- Compare multiple policy scenarios side-by-side
- Bar charts showing baseline vs counterfactual
- Relative impact visualization
- Detailed comparison table

### 4. 🌍 Country Analysis
**Status**: ✅ Working
- Select any country to explore
- Time series of congestion and investment
- Country-specific scenario impacts
- Historical trends

### 5. 📈 Time Series
**Status**: ⚠️ Requires simulation data
- Compare trajectories across scenarios
- Select multiple countries
- Baseline vs counterfactual projections

**If graphs aren't showing:**
1. Click "🔄 Clear Cache & Reload Data" in sidebar
2. Check debug information displayed on the page
3. Verify `output/simulation_results.pkl` exists

### 6. 🎲 Uncertainty Analysis
**Status**: ⚠️ Requires simulation data
- Bootstrap confidence intervals
- Sensitivity analysis
- Distribution visualization

**If graphs aren't showing:**
1. Click "🔄 Clear Cache & Reload Data" in sidebar
2. Check debug information displayed on the page
3. Verify `output/uncertainty_quantification.pkl` exists

### 7. ⚙️ Custom Simulator
**Status**: ✅ Working
- Design your own policy scenario
- Adjust investment parameters
- See expected impacts in real-time
- No external data required

### 8. 🔍 Deep Dive
**Status**: ⚠️ Requires simulation data
- Detailed country-level heterogeneous effects
- Distribution of impacts across countries
- Top/bottom performers
- Interactive exploration

**If graphs aren't showing:**
1. Click "🔄 Clear Cache & Reload Data" in sidebar
2. Check debug information displayed on the page
3. Verify `output/country_effects_*.csv` files exist

### 9. 📄 Reports
**Status**: ✅ Working
- Download analysis reports
- View report contents
- Export data

---

## 🔧 Troubleshooting

### Graphs Not Showing?

**Solution 1: Clear Cache**
1. Look for "🔄 Clear Cache & Reload Data" button in the sidebar
2. Click it to refresh all data
3. Navigate back to the page with missing graphs

**Solution 2: Check Debug Information**
- Pages now show debug info when data is missing
- Look for "Available data keys" message
- This tells you what data is loaded

**Solution 3: Verify Simulation Data Exists**
Check if these files exist:
```bash
ls -lh output/simulation_results.pkl
ls -lh output/uncertainty_quantification.pkl
ls -lh output/country_effects_*.csv
```

If missing, you need to run the counterfactual simulation:
```bash
python scripts/deep_counterfactual_simulation.py
```

---

## 📦 What's New in This Update

### ✅ Added Features

1. **New "Data Quality" Page**
   - Showcases the 58x improvement in data coverage
   - Before/After visualizations
   - Data source composition (Actual vs ML)
   - Geographic coverage maps
   - Sensitivity analysis results

2. **Cache Control Button**
   - "🔄 Clear Cache & Reload Data" in sidebar
   - Forces dashboard to reload all data
   - Fixes stuck cache issues

3. **Better Error Messages**
   - Debug information when graphs don't load
   - Shows which data files are missing
   - Helpful hints for fixing issues

4. **Improved Data Loading**
   - Compatible with enhanced dataset
   - Handles 7,430 observations smoothly
   - Works with 275 countries

---

## 📊 Data Requirements

### Always Available (No Simulation Required)
- ✅ Overview
- ✅ Data Quality ⭐ NEW
- ✅ Country Analysis
- ✅ Custom Simulator
- ✅ Reports (partial)

### Requires Counterfactual Simulation
To use these pages, run: `python scripts/deep_counterfactual_simulation.py`
- ⚠️ Scenario Comparison (full)
- ⚠️ Time Series
- ⚠️ Uncertainty Analysis
- ⚠️ Deep Dive

---

## 🎯 Recommended Workflow

### For Showcasing Data Improvements
1. Launch dashboard: `streamlit run dashboard_app.py`
2. Go to "✨ Data Quality" page
3. Show before/after comparison
4. Highlight 58x improvement (117 → 7,430 observations)
5. Explain data source breakdown
6. Show sensitivity analysis validation

### For Policy Analysis
1. Ensure simulation data exists (run `deep_counterfactual_simulation.py` if needed)
2. Launch dashboard
3. Start with "🏠 Overview" for big picture
4. Use "📊 Scenario Comparison" to compare policies
5. Dive into "🌍 Country Analysis" for specifics
6. Use "🎲 Uncertainty Analysis" to assess robustness
7. Try "⚙️ Custom Simulator" for what-if scenarios

---

## 🐛 Known Issues & Solutions

### Issue: Graphs not appearing after data update

**Solution:**
1. Click "🔄 Clear Cache & Reload Data" button
2. Refresh browser (Ctrl+R or Cmd+R)
3. If still not working, stop Streamlit (Ctrl+C) and restart

### Issue: "No simulation results available"

**Solution:**
Run the counterfactual simulation script:
```bash
cd scripts
python deep_counterfactual_simulation.py
```

Wait for completion, then click "🔄 Clear Cache & Reload Data"

### Issue: Dashboard is slow

**Solution:**
- This is normal with 7,430 observations
- First load caches data (will be faster after)
- Consider filtering to specific countries if needed

---

## 📁 File Structure

```
TransPort-PH/
├── data/
│   ├── clean_panel.csv                    ← Main dataset (7,430 rows)
│   ├── sensitivity_analysis_results.csv   ← Validation data
│   └── [other data files]
│
├── output/
│   ├── simulation_results.pkl             ← Required for scenarios
│   ├── uncertainty_quantification.pkl     ← Required for uncertainty
│   ├── country_effects_*.csv              ← Required for deep dive
│   └── counterfactual_summary.csv         ← Summary stats
│
└── scripts/
    ├── dashboard_app.py                   ← The dashboard (UPDATED)
    ├── deep_counterfactual_simulation.py  ← Generates simulation data
    └── [other scripts]
```

---

## 💡 Tips & Tricks

1. **Use the sidebar** for quick navigation between pages

2. **Clear cache regularly** if you update underlying data files

3. **Check debug messages** - they tell you exactly what's missing

4. **Start with Data Quality page** - great for presentations!

5. **Custom Simulator** works without any simulation data - perfect for quick demos

6. **Download reports** from the Reports page for offline analysis

---

## 🎉 Highlights

### Your Data Improvement Story
The **"✨ Data Quality"** page tells the complete story of how you:
1. Identified critical data sparsity (98.4% missing)
2. Implemented multi-pronged solution
3. Achieved 58x improvement in coverage
4. Validated with sensitivity analysis
5. Created publication-ready dataset

**This is your showcase feature!** Perfect for:
- Thesis presentations
- Research talks
- Code reviews
- Demonstrating problem-solving skills

---

## 📞 Support

If you encounter issues:
1. Check debug information displayed on problematic pages
2. Verify data files exist (see File Structure section)
3. Try clearing cache
4. Restart Streamlit

---

**Dashboard Version**: 2.0 (Updated November 2024)  
**Compatible with**: Enhanced dataset (7,430 observations, 275 countries)  
**New Feature**: Data Quality showcase page ✨

---

*Ready to impress with your data improvements? Launch the dashboard and head to the "✨ Data Quality" page!* 🚀

