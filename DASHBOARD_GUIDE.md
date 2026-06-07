# 📊 Field Activity Dashboard - Complete Guide

## ✨ Dashboard Features Implemented

### 1. **Beautiful Color Design**
- **KPI Card 1 (Purple Gradient)**: 📞 Total Calls - Shows total field visits
- **KPI Card 2 (Pink Gradient)**: 🏆 Top Position - Displays highest metric value
- **KPI Card 3 (Cyan Gradient)**: 📈 P1 Priority - Shows P1 product count
- **KPI Card 4 (Green Gradient)**: 💡 P2 Support - Displays P2 product count

### 2. **Interactive Filters (Sidebar)**
- **Division Filter**: HOSPITAL CARE, NCD, VIROLOGY, or All
- **Month Filter**: Jan, Feb, Mar, Apr, or All
- **Product Filter**: All products mentioned in your data, or All

### 3. **Key Metrics Displayed**
- **Total Calls**: Number of field visits
- **Unique Products**: Count of different products discussed
- **Total Discussions**: Total product mentions across all visits
- **Avg Products/Call**: Average products discussed per field visit

### 4. **Advanced Visualizations**
- **Top Products Chart**: Horizontal bar chart showing top 15 products
- **Product Position Analysis**: Shows how many times a product appeared in P1, P2, P3, P4 columns
- **Division Breakdown**: Product discussions by division
- **Monthly Trends**: Product discussions by month
- **Detailed Table**: Sortable data table with progress bars

---

## 📥 Export & Sharing Options

### **1. Excel Report Export**
- **File**: `Field_Activity_Dashboard.xlsx`
- **Contents**:
  - **Summary Sheet**: Key metrics and report timestamp
  - **Product Details Sheet**: All products with discussion counts and rankings
  - **Filters Applied Sheet**: Shows which filters were active when report was generated
- **Usage**: Click "📊 Download Excel Report" button at the bottom of the dashboard

### **2. CSV Export**
- **File**: `Product_Discussions.csv`
- **Contents**: Product name, discussion count, and rank
- **Usage**: Click "📄 Download CSV" button
- **Use Cases**: Import into Excel, Tableau, Power BI, or Python

### **3. Dashboard URL Sharing**
- **Current**: http://localhost:8501
- **For Local Network**: http://192.168.1.2:8501
- Share the URL with your team members on the same network

---

## 🚀 How to Use the Dashboard

### **Step 1: Access the Dashboard**
```bash
# Dashboard is already running at:
http://localhost:8501
```

### **Step 2: Apply Filters**
1. Open the sidebar (← icon on the left)
2. Select filters:
   - Choose a **Division** or keep "All"
   - Choose a **Month** or keep "All"
   - Choose a **Product** or keep "All"
3. Dashboard updates automatically

### **Step 3: View Insights**
- See KPI cards with your selected data
- View interactive charts and visualizations
- Scroll down to see detailed product breakdown

### **Step 4: Export Data**
- **For Excel**: Click "📊 Download Excel Report"
- **For CSV**: Click "📄 Download CSV"
- **For Presentations**: Take screenshots of the charts

---

## 📈 Data Structure Explained

Your Excel file (`Call data 2026.xlsx`) contains:
- **Call Data Sheet**: 115,793 records with 28 columns
- **Product Columns**: P1, P2, P3, P4 (each can contain a product name or be empty)
- **Key Fields**:
  - Month (Jan, Feb, Mar, Apr)
  - Division (HOSPITAL CARE, NCD, VIROLOGY)
  - Date/Time information
  - Customer/Doctor information
  - Product data (P1, P2, P3, P4)

**Product Counts**:
- P1: 115,780 entries
- P2: 65,673 entries
- P3: 31,826 entries
- P4: 15,795 entries

---

## 🎨 Color Scheme

| Card | Color | Purpose |
|------|-------|---------|
| **KPI 1** | Purple Gradient (#667eea → #764ba2) | Total Calls |
| **KPI 2** | Pink Gradient (#f093fb → #f5576c) | Top Position |
| **KPI 3** | Cyan Gradient (#4facfe → #00f2fe) | P1 Priority |
| **KPI 4** | Green Gradient (#43e97b → #38f9d7) | P2 Support |
| **Charts** | Viridis + Custom Palettes | Data Visualization |

---

## 🌐 Deployment Options

### **Option 1: Local Network Sharing (Current)**
- ✅ Already running on your machine
- ✅ Share URL with team on same network
- ✅ No setup required

### **Option 2: Streamlit Cloud (Free)**
1. Go to https://share.streamlit.io/
2. Connect your GitHub account
3. Deploy the dashboard.py file
4. Get a public URL to share with anyone

### **Option 3: Heroku Hosting**
1. Create a Heroku account
2. Deploy the app (requires some configuration)
3. Get a public URL

### **Option 4: Self-Hosted Server**
1. Run on a company server
2. Access via internal URL
3. More control and security

---

## 📊 Sample Insights Your Dashboard Shows

### **Overall Metrics** (All Divisions, All Months)
- Total Calls: 115,793
- Unique Products: 100+
- Total Discussions: 228,000+
- Avg Products/Call: ~2.0

### **Top Products Discussed**
The dashboard automatically ranks and displays the top 15 products by discussion frequency

### **Product Position Analysis**
- Shows which product position (P1, P2, P3, P4) is most common for each product
- Helps understand product hierarchy

---

## 🔧 Technical Details

**Built with**:
- **Streamlit**: Interactive web framework
- **Pandas**: Data processing
- **Plotly**: Interactive visualizations
- **XlsxWriter**: Excel file generation
- **Python 3.13.2**

**Performance**:
- Dashboard loads data once and caches it
- Filters apply instantly
- Exports generate on-demand

---

## 💡 Tips for Best Results

1. **For Presentations**: 
   - Filter to specific division/month for focused insights
   - Screenshot charts with white background
   - Download Excel report for detailed backup

2. **For Analysis**:
   - Export CSV for further analysis in Python/R
   - Use Excel export for multi-sheet reports
   - Filter by product to deep-dive into specific items

3. **For Sharing**:
   - Use Excel export for distribution to non-technical users
   - Share dashboard URL for real-time access
   - Generate reports at different time periods for comparison

---

## 📁 Files in Your Workspace

```
/Users/eeshwar/Desktop/ProductInsights/
├── Call data 2026.xlsx          # Your source data
├── dashboard.py                 # Main dashboard application
├── DASHBOARD_GUIDE.md           # This file
├── requirements.txt             # Python dependencies (optional)
└── .venv/                       # Virtual environment
```

---

## ❓ FAQ

**Q: How do I stop the dashboard?**
A: Press Ctrl+C in the terminal where it's running

**Q: How do I restart the dashboard?**
A: Kill the process and run: `streamlit run dashboard.py`

**Q: Can I add more products to the data?**
A: Yes! Just add columns P5, P6, etc. to your Excel file and update the dashboard code

**Q: How often is data updated?**
A: The dashboard reads from the Excel file each time you refresh. Just update your Excel file and refresh the browser

**Q: Can I customize the colors?**
A: Yes! Modify the gradient colors in the CSS section of dashboard.py

**Q: How do I export to PowerPoint?**
A: Use the Excel export, or take screenshots of the charts and insert into PowerPoint

---

## 🎯 Next Steps

1. **Test the Dashboard**: 
   - Click through different filters
   - Verify all products appear
   - Test both export buttons

2. **Share with Team**:
   - Send the URL to colleagues
   - They can view live on your network
   - Everyone can download reports

3. **Customize (Optional)**:
   - Change colors
   - Add more visualizations
   - Add new metrics

---

**Dashboard Status**: ✅ **LIVE AND RUNNING**
- Access at: http://localhost:8501
- Last Updated: Today
- Data Source: Call data 2026.xlsx
