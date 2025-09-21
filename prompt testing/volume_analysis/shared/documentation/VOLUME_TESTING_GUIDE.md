# Volume Analysis Testing Framework - Complete Guide

## 📁 Organized File Structure

The volume analysis testing framework now creates organized directories for easy inspection of all generated files:

```
volume_analysis_test_results_YYYYMMDD_HHMMSS/
├── charts/         📊 Volume analysis chart images (PNG files)
├── prompts/        📝 Formatted prompts sent to LLM
├── responses/      💬 LLM analysis responses  
└── reports/        📋 Summary reports (Excel/CSV)
```

## 🖼️ Viewing Generated Images

### For Each Stock Tested:

**Chart Files**: `charts/volume_chart_[SYMBOL]_[TIMESTAMP].png`
- Multi-panel volume analysis charts
- Price action with volume bars
- Volume moving averages and anomalies
- Technical indicators and analysis summary
- File sizes typically 400-600KB (high-resolution PNG)

### How to View Charts:

#### macOS:
```bash
# Open charts folder in Finder
open volume_analysis_test_results_*/charts/

# View specific chart
open 'charts/volume_chart_RELIANCE_20250920_203015.png'

# View all charts in Preview
open charts/*.png
```

#### Windows:
```cmd
# Open charts folder in Explorer  
explorer volume_analysis_test_results_*\charts

# View specific chart
start charts\volume_chart_RELIANCE_20250920_203015.png
```

#### Linux:
```bash
# Open charts folder in file manager
xdg-open volume_analysis_test_results_*/charts/

# View specific chart with default image viewer
xdg-open charts/volume_chart_RELIANCE_20250920_203015.png
```

## 📝 Generated Files for Each Stock

### 1. Volume Analysis Chart (`charts/`)
- **File**: `volume_chart_[SYMBOL]_[TIMESTAMP].png`
- **Content**: 
  - Price and volume candlestick/bar chart
  - Volume moving averages (20-day)
  - Volume anomaly detection (spikes in red)
  - Price-volume correlation analysis
  - Recent 30-day volume activity
  - Technical analysis summary

### 2. Formatted Prompt (`prompts/`)
- **File**: `volume_prompt_[SYMBOL]_[TIMESTAMP].txt`
- **Content**:
  - Stock information (symbol, company, sector)
  - Volume characteristics profile
  - Key volume analysis indicators summary
  - Complete formatted prompt text sent to LLM
  - Context length and prompt statistics

### 3. LLM Response (`responses/`)
- **File**: `volume_response_[SYMBOL]_[TIMESTAMP].txt`
- **Content**:
  - Complete LLM analysis response
  - Response metadata (length, timing)
  - Parsed JSON structure (if valid JSON)
  - Code execution results (if any)

### 4. Summary Reports (`reports/`)
- **File**: `volume_analysis_summary.xlsx` (or `.csv`)
- **Content**: Tabulated results for all stocks
- **File**: `volume_analysis_comprehensive_report.txt`
- **Content**: Detailed analysis report with statistics

## 🔍 Testing Workflow

### 1. Run Volume Analysis Tests
```bash
# Full test (all 8 stocks)
python multi_stock_test.py

# Demo test (3 stocks for faster testing)
python demo_organized_volume_testing.py
```

### 2. Inspect Generated Charts
```bash
# Open charts directory to view all images
open volume_analysis_test_results_*/charts/

# Each chart shows:
# - Multi-panel volume analysis visualization
# - Price action with volume confirmation/divergence
# - Anomaly detection and institutional activity
# - Technical analysis summary
```

### 3. Review Prompts and Context
```bash
# Check prompt formatting and context quality
open volume_analysis_test_results_*/prompts/volume_prompt_*.txt

# Verify:
# - Complete volume metrics included
# - Proper context formatting
# - All analysis components present
```

### 4. Validate LLM Responses  
```bash
# Review LLM analysis quality
open volume_analysis_test_results_*/responses/volume_response_*.txt

# Check for:
# - Comprehensive volume analysis
# - Proper JSON structure
# - Volume-specific insights
# - Chart interpretation accuracy
```

### 5. Review Test Performance
```bash
# Open summary report
open volume_analysis_test_results_*/reports/volume_analysis_summary.xlsx

# Check:
# - Success rates across stocks
# - Quality scores and metrics
# - Volume characteristics analysis
# - Execution performance
```

## 🎯 Key Features

### Chart Image Generation
- **High-resolution PNG images** (300 DPI)
- **Multi-panel layout** showing different volume aspects
- **Anomaly highlighting** with color coding
- **Technical indicators** overlaid on charts
- **Automatic saving** to organized charts directory

### Multimodal LLM Integration
- **Chart + context** sent together to LLM
- **Visual analysis** combined with numerical data
- **Comprehensive prompts** with formatted context
- **Structured JSON responses** for consistent analysis

### Quality Evaluation
- **Volume data completeness** scoring
- **Analysis depth** evaluation
- **Response quality** metrics
- **Volume insight quality** assessment
- **Overall performance** scoring

## 🚀 Quick Start Commands

```bash
# 1. Run demo test (3 stocks, faster)
python demo_organized_volume_testing.py

# 2. View generated charts
open volume_analysis_test_results_*/charts/

# 3. Review all files
find volume_analysis_test_results_* -type f

# 4. Open summary report
open volume_analysis_test_results_*/reports/volume_analysis_summary.xlsx
```

## 📊 Chart Interpretation Guide

Each generated chart contains 4-5 panels:

1. **Price & Volume**: Candlestick price with volume bars
2. **Volume Analysis**: Volume with moving averages and anomalies  
3. **Technical Indicators**: VWAP, correlations, trends
4. **Analysis Summary**: Key metrics and findings text
5. **Recent Activity**: Last 30 days detailed volume activity

### Visual Elements:
- **Red volume bars**: Detected anomalies/spikes
- **Blue line**: Volume moving average (20-day)
- **Green/red price bars**: Price movement direction
- **Text annotations**: Key analysis findings
- **Date ranges**: X-axis showing analysis period

## 🔧 Troubleshooting

### If Charts Don't Generate:
- Check matplotlib backend: `export MPLBACKEND=Agg`
- Verify write permissions to output directory
- Check for missing dependencies (matplotlib, seaborn)

### If No Images Show:
- Ensure PNG files exist: `ls -la charts/*.png`
- Check file sizes (should be 400-600KB each)
- Verify your system's default image viewer

### For Faster Testing:
- Use `demo_organized_volume_testing.py` for 3-stock test
- Limit to specific stocks in `multi_stock_test.py`
- Disable LLM calls for chart-only testing

## 🎉 Success Indicators

✅ **Complete Test Run**:
- All directories created (charts, prompts, responses, reports)
- PNG files generated for each stock (400-600KB each)  
- Text files contain formatted prompts and responses
- Excel/CSV report with summary statistics

✅ **Quality Charts**:
- Multi-panel layout visible
- Price and volume data properly plotted
- Anomalies highlighted in red
- Clear date axis and labeling
- Analysis summary text readable

✅ **Comprehensive Context**:
- Prompts contain detailed volume metrics
- All analysis components included
- Proper formatting and structure
- Context length appropriate (1500-3000 chars)

The framework is now ready for comprehensive volume analysis testing with easy visual inspection of all generated charts and analysis files!