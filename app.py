import os

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO
import xlsxwriter

# Page configuration
st.set_page_config(
    page_title="Field Activity Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling with better colors
st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .metric-card,
        .metric-card-2,
        .metric-card-3,
        .metric-card-4 {
            padding: 18px;
            height: 170px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.14);
            border: 2px solid rgba(255,255,255,0.18);
            display: flex;
            flex-direction: column;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover,
        .metric-card-2:hover,
        .metric-card-3:hover,
        .metric-card-4:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        }
        
        .metric-card-2 {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
        }
        
        .metric-card-3 {
            background: linear-gradient(135deg, #EA580C 0%, #C2410C 100%);
        }
        
        .metric-card-4 {
            background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 12px 0;
            letter-spacing: 1px;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.95;
            font-weight: 600;
        }
        
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: 1px;
        }
        
        h2 {
            color: #667eea;
            font-size: 1.8rem;
            margin-top: 30px;
            margin-bottom: 20px;
            font-weight: 700;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .stMetric {
            background: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .header-info {
            background: white;
            padding: 15px 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .export-section {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-top: 3px solid #667eea;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
    </style>
""", unsafe_allow_html=True)

import glob


def read_excel_data(file_path):
    """Read an Excel file even when the sheet name is not exactly 'Call Data'."""
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names

    preferred_order = ["Call Data", "Data", "Sheet1", "Sheet"]
    for preferred in preferred_order:
        if preferred in sheet_names:
            return pd.read_excel(file_path, sheet_name=preferred)

    for sheet_name in sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if isinstance(df, pd.DataFrame) and not df.empty and len(df.columns) > 0:
            return df

    raise ValueError(
        "No valid worksheet found in this Excel file. "
        "Expected a sheet named 'Call Data' or any data sheet."
    )


files = glob.glob("Data/*.xlsx")

df_list = []

for file in files:
    temp_df = read_excel_data(file)
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

# Function to create Excel export
def create_excel_report(product_counts, division_filter, month_filter, product_filter, df):
    """Create an Excel file with dashboard insights"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'font_color': 'white',
        'bg_color': '#667eea',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 12
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'bg_color': '#f0f0f0',
        'border': 1
    })
    
    subtitle_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'bg_color': '#e8e8e8',
        'border': 1
    })
    
    data_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    progress_format = workbook.add_format({
        'border': 1,
        'num_format': '0'
    })
    
    # Create sheets
    ws_summary = workbook.add_worksheet('Summary')
    ws_products = workbook.add_worksheet('Product Details')
    ws_filters = workbook.add_worksheet('Filters Applied')
    
    # Summary Sheet
    ws_summary.set_column('A:A', 25)
    ws_summary.set_column('B:B', 20)
    
    ws_summary.merge_range('A1:B1', 'FIELD ACTIVITY DASHBOARD REPORT', title_format)
    
    row = 2
    ws_summary.write(row, 0, 'Report Generated:', subtitle_format)
    ws_summary.write(row, 1, pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'), data_format)
    
    row += 2
    ws_summary.write(row, 0, 'Metric', header_format)
    ws_summary.write(row, 1, 'Value', header_format)
    
    row += 1
    filtered_df = df.copy()
    if division_filter:
        filtered_df = filtered_df[filtered_df['Division'] == division_filter]
    if month_filter:
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]
    if owner_filter: 
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner_filter]
    
    metrics = [
        ('Total Visits', len(filtered_df)),
        ('Unique Products', len(product_counts)),
        ('Total Product Discussions', sum(product_counts.values())),
        ('Avg Products per Visit', round(sum(product_counts.values()) / len(filtered_df), 2) if len(filtered_df) > 0 else 0),
    ]
    
    for label, value in metrics:
        ws_summary.write(row, 0, label, data_format)
        ws_summary.write(row, 1, value, data_format)
        row += 1
    
    # Product Details Sheet
    ws_products.set_column('A:A', 30)
    ws_products.set_column('B:B', 20)
    ws_products.set_column('C:C', 20)
    
    ws_products.merge_range('A1:C1', 'PRODUCT DISCUSSION ANALYSIS', title_format)
    
    row = 2
    ws_products.write(row, 0, 'Product', header_format)
    ws_products.write(row, 1, 'Discussions', header_format)
    ws_products.write(row, 2, 'Rank', header_format)
    
    row += 1
    for idx, (product, count) in enumerate(product_counts.items(), 1):
        ws_products.write(row, 0, product, data_format)
        ws_products.write(row, 1, count, progress_format)
        ws_products.write(row, 2, idx, data_format)
        row += 1
    
    # Filters Applied Sheet
    ws_filters.set_column('A:A', 25)
    ws_filters.set_column('B:B', 30)
    
    ws_filters.merge_range('A1:B1', 'FILTERS APPLIED', title_format)
    
    row = 2
    ws_filters.write(row, 0, 'Filter Type', header_format)
    ws_filters.write(row, 1, 'Value', header_format)
    
    row += 1
    filters_applied = [
        ('Division', division_filter if division_filter else 'All'),
        ('Month', month_filter if month_filter else 'All'),
        ('Product', product_filter if product_filter else 'All'),
    ]
    
    for filter_type, filter_value in filters_applied:
        ws_filters.write(row, 0, filter_type, data_format)
        ws_filters.write(row, 1, filter_value, data_format)
        row += 1
    
    workbook.close()
    output.seek(0)
    return output



# Process product data
def get_unique_products(df):
    """Extract all unique products from P1, P2, P3, P4 columns"""
    products = set()
    for col in ['P1', 'P2', 'P3', 'P4']:
        products.update(df[col].dropna().unique())
    return sorted(list(products))

def count_product_discussions(df, product, division=None, month=None):
    """Count how many times a product was discussed"""
    filtered_df = df.copy()
    
    if division:
        filtered_df = filtered_df[filtered_df['Division'] == division]
    if month:
        filtered_df = filtered_df[filtered_df['Month'] == month]
    if owner_filter: 
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner_filter]
    count = 0
    for col in ['P1', 'P2', 'P3', 'P4']:
        count += (filtered_df[col] == product).sum()
    
    return count

def get_product_counts_by_column(df, division=None, month=None):
    """Get counts for each product across all columns"""
    filtered_df = df.copy()
    
    if division:
        filtered_df = filtered_df[filtered_df['Division'] == division]
    if month:
        filtered_df = filtered_df[filtered_df['Month'] == month]
    if owner_filter: 
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner_filter]

    product_counts = {}
    for col in ['P1', 'P2', 'P3', 'P4']:
        value_counts = filtered_df[col].value_counts()
        for product, count in value_counts.items():
            if pd.notna(product):
                product_counts[product] = product_counts.get(product, 0) + count
    
    return dict(sorted(product_counts.items(), key=lambda x: x[1], reverse=True))

# Sidebar - Filters
st.sidebar.markdown("### 🔍 Dashboard Filters")
st.sidebar.markdown("---")

all_divisions = ['All'] + sorted(df['Division'].unique().tolist())
all_months = ['All'] + sorted(df['Month'].unique().tolist())
unique_products = get_unique_products(df)
all_products = ['All'] + unique_products
all_owners = ['All'] + sorted(df['In-Field Activity: Owner Name'].unique().tolist())

selected_division = st.sidebar.selectbox("Division", all_divisions, index=0)
selected_month = st.sidebar.selectbox("Month", all_months, index=0)
selected_product = st.sidebar.selectbox("Product", all_products, index=0)
selected_owner = st.sidebar.selectbox("Representative", all_owners, index=0) 

# Prepare filter values
division_filter = None if selected_division == 'All' else selected_division
month_filter = None if selected_month == 'All' else selected_month
product_filter = None if selected_product == 'All' else selected_product
owner_filter = None if selected_owner == 'All' else selected_owner

month_order = [
    "Jan", "Feb", "Mar", "Apr", "May",
    "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

# Main title
st.markdown("# 📊 Field Activity Dashboard")
st.markdown("*Track product discussions across field visits*")
st.markdown("---")

# Filter summary
filter_text = []
if division_filter:
    filter_text.append(f"**Division:** {division_filter}")
if month_filter:
    filter_text.append(f"**Month:** {month_filter}")
if product_filter:
    filter_text.append(f"**Product:** {product_filter}")

if filter_text:
    st.markdown(f"""
    <div class="header-info">
        📋 <b>Applied Filters:</b> {" | ".join(filter_text)}
    </div>
    """, unsafe_allow_html=True)

# Get product counts based on filters
if product_filter:
    # Show detailed metrics for selected product
    count = count_product_discussions(df, product_filter, division_filter, month_filter)
    
    st.markdown(f"## 📦 Insights for **{product_filter}**")
    
    # Calculate counts by column
    filtered_df = df.copy()
    if division_filter:
        filtered_df = filtered_df[filtered_df['Division'] == division_filter]
    if month_filter:
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]
    if owner_filter:
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner_filter]
    
    counts_by_col = {}
    for col in ['P1', 'P2', 'P3', 'P4']:
        count_col = (filtered_df[col] == product_filter).sum()
        counts_by_col[col] = count_col
    
    # KPI Cards for single product
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Total Discussions</div>
            <div class="metric-value">{count:,}</div>
            <small>All field visits</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-2">
            <div class="metric-label">🏆 Top Position</div>
            <div class="metric-value">{max([v for v in counts_by_col.values()]) if counts_by_col else 0:,}</div>
            <small>Highest column count</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-3">
            <div class="metric-label">📈 P1 Priority</div>
            <div class="metric-value">{counts_by_col['P1']:,}</div>
            <small>Primary product</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-4">
            <div class="metric-label">💡 P2 Support</div>
            <div class="metric-value">{counts_by_col['P2']:,}</div>
            <small>Secondary product</small>
        </div>
        """, unsafe_allow_html=True)

else:
    # Show overall metrics
    product_counts = get_product_counts_by_column(df, division_filter, month_filter)
    
# Calculate metrics
filtered_df = df.copy()

if division_filter:
    filtered_df = filtered_df[filtered_df['Division'] == division_filter]

if month_filter:
    filtered_df = filtered_df[filtered_df['Month'] == month_filter]

if owner_filter:
    filtered_df = filtered_df[
        filtered_df['In-Field Activity: Owner Name'] == owner_filter
    ]

# KPI Calculations
total_calls = len(filtered_df)
total_products = len(product_counts)
total_discussions = sum(product_counts.values())
avg_per_call = total_discussions / total_calls if total_calls > 0 else 0
total_doctors = filtered_df['Customer ID'].nunique()

# Visit Average Calculation
total_visits = len(filtered_df)   # 1 row = 1 visit
total_reps = filtered_df['In-Field Activity: Owner Name'].nunique()
total_months = filtered_df['Month'].nunique()

if total_reps > 0 and total_months > 0:
    visit_average = total_visits / (total_reps * total_months)
else:
    visit_average = 0
# Total Visits with CLM
total_clm_visits = filtered_df[
    filtered_df['Call with CLM'] == True
].shape[0]

# Call Average Calculation
total_calls = len(filtered_df)
total_reps = filtered_df['In-Field Activity: Owner Name'].nunique()
total_call_dates = filtered_df['CallDate'].nunique()

if total_reps > 0 and total_call_dates > 0:
    visits_per_rep_day = total_calls / (total_reps * total_call_dates)
else:
    visits_per_rep_day = 0

st.markdown("## 📊 Overall Insights")

row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)

row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)


with row1_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📞 Total Visits</div>
        <div class="metric-value">{total_visits:,}</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
    <div class="metric-card-2">
        <div class="metric-label">📦 Unique Products</div>
        <div class="metric-value">{total_products:,}</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col3:
    st.markdown(f"""
    <div class="metric-card-3">
        <div class="metric-label">💬 Total Discussions</div>
        <div class="metric-value">{total_discussions:,}</div>
    </div>
    """, unsafe_allow_html=True)

with row1_col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">👨‍⚕️ Unique Doctors</div>
        <div class="metric-value">{total_doctors:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

with row2_col1:
    st.markdown(f"""
    <div class="metric-card-2">
        <div class="metric-label">📈 Avg Products / Visit</div>
        <div class="metric-value">{avg_per_call:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown(f"""
    <div class="metric-card-3">
        <div class="metric-label">🚗 Visits / Rep / Month</div>
        <div class="metric-value">{visit_average:.2f}</div>
    </div>
    """, unsafe_allow_html=True)   

with row2_col3:
    st.markdown(f"""
    <div class="metric-card-4">
        <div class="metric-label">📱 Visits with CLM</div>
        <div class="metric-value">{total_clm_visits:,}</div>
    </div>
    """, unsafe_allow_html=True)

with row2_col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📅 Visits / Rep / Day</div>
        <div class="metric-value">{visits_per_rep_day:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Charts section
if product_filter:
    # Single product analysis
    st.markdown(f"## 📊 Analysis for {product_filter}")
    
    # Breakdown by column
    col1, col2 = st.columns(2)
    
    with col1:
        # Count by product column
        filtered_df = df.copy()
        if division_filter:
            filtered_df = filtered_df[filtered_df['Division'] == division_filter]
        if month_filter:
            filtered_df = filtered_df[filtered_df['Month'] == month_filter]
        if owner_filter: 
            filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner_filter]

        counts_by_col = {}
        for col in ['P1', 'P2', 'P3', 'P4']:
            count = (filtered_df[col] == product_filter).sum()
            counts_by_col[col] = count
        
        fig_col = go.Figure(data=[
            go.Bar(
                x=list(counts_by_col.keys()),
                y=list(counts_by_col.values()),
                marker=dict(
                    color=['#667eea', '#764ba2', '#f093fb', '#4facfe'],
                    line=dict(color='#333', width=2)
                ),
                text=list(counts_by_col.values()),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        fig_col.update_layout(
            title=f"{product_filter} - Discussions by Position",
            xaxis_title="Product Column",
            yaxis_title="Count",
            height=400,
            showlegend=False,
            template='plotly_white'
        )
        st.plotly_chart(fig_col, use_container_width=True)
    
    with col2:
        # Count by division
        if not division_filter:
            count_by_div = {}
            for div in df['Division'].unique():
                count_by_div[div] = count_product_discussions(df, product_filter, div, month_filter)
            
            fig_div = go.Figure(data=[
                go.Bar(
                    x=list(count_by_div.keys()),
                    y=list(count_by_div.values()),
                    marker=dict(
                        color=['#667eea', '#764ba2', '#f093fb'],
                        line=dict(color='#333', width=2)
                    ),
                    text=list(count_by_div.values()),
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                )
            ])
            fig_div.update_layout(
                title=f"{product_filter} - Discussions by Division",
                xaxis_title="Division",
                yaxis_title="Count",
                height=400,
                showlegend=False,
                template='plotly_white'
            )
            st.plotly_chart(fig_div, use_container_width=True)
        else:
            # Count by month
            if not month_filter:
                count_by_month = {}
                for mon in sorted(df['Month'].unique()):
                    count_by_month[mon] = count_product_discussions(df, product_filter, division_filter, mon)
                
                fig_month = go.Figure(data=[
                    go.Bar(
                        x=list(count_by_month.keys()),
                        y=list(count_by_month.values()),
                        marker=dict(
                            color=['#667eea', '#764ba2', '#f093fb', '#4facfe'],
                            line=dict(color='#333', width=2)
                        ),
                        text=list(count_by_month.values()),
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                    )
                ])
                fig_month.update_layout(
                    title=f"{product_filter} - Discussions by Month",
                    xaxis_title="Month",
                    yaxis_title="Count",
                    height=400,
                    showlegend=False,
                    template='plotly_white'
                )
                st.plotly_chart(fig_month, use_container_width=True)

else:
    # Overall product analysis
    st.markdown("## 📊 Product Discussion Analysis")
    
    product_counts = get_product_counts_by_column(df, division_filter, month_filter)
    
    # Top products chart
    col1, col2 = st.columns([3, 1])
    
    with col1:
        top_n = min(5, len(product_counts))

        top_products = dict(list(product_counts.items())[:top_n])  

        others_count = sum(list(product_counts.values())[top_n:])

        if others_count > 0:
             top_products["Others"] = others_count
        
        fig_top = go.Figure(data=[
            go.Pie(
                labels=list(top_products.keys()),
                values=list(top_products.values()),
                textinfo="label+percent",
                 hoverinfo="label+value+percent",
                marker=dict(
                colors=[
                    "#2563EB",   # Blue
                    "#10B981",   # Green
                    "#F59E0B",   # Amber
                    "#8B5CF6",   # Purple
                    "#EF4444",   # Red
                    "#9CA3AF"    # Grey (Others)
        ]
    )
)
        ])
        fig_top.update_layout(
            title=f"Top {top_n} Products by Discussion",
            height=500,
            showlegend=False,
            template='plotly_white',
            
        )
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Product Statistics")
        st.markdown(f"- **Total Products:** {len(product_counts)}")
        st.markdown(f"- **Total Discussions:** {sum(product_counts.values()):,}")
        
        if product_counts:
            top_product = list(product_counts.keys())[0]
            top_count = list(product_counts.values())[0]
            st.markdown(f"- **Top Product:** {top_product}")
            st.markdown(f"- **Top Product Count:** {top_count}")
        
        # Average discussions
        avg_discussions = sum(product_counts.values()) / len(product_counts) if product_counts else 0
        st.markdown(f"- **Avg Discussions/Product:** {avg_discussions:.0f}")

# ==========================================================
# MONTHLY PERFORMANCE TRENDS
# ==========================================================

st.markdown("## 📈 Monthly Performance Trends")

# -----------------------------------------
# Total Visits by Month
# -----------------------------------------

visits_month = (
    filtered_df
    .groupby("Month")
    .size()
    .reindex(month_order, fill_value=0)
)

fig_visits = px.bar(
    x=visits_month.index,
    y=visits_month.values,
    title="Total Visits by Month",
    text=visits_month.values,
    labels={
        "x": "Month",
        "y": "Visits"
    }
)

fig_visits.update_traces(
    marker_color="#2563EB",
    textposition="outside"
)

fig_visits.update_layout(
    template="plotly_white",
    height=380,
    title_x=0.5
)

st.plotly_chart(fig_visits, use_container_width=True)

# -----------------------------------------
# Unique Doctors by Month
# -----------------------------------------

doctor_month = (
    filtered_df
    .groupby("Month")["Customer ID"]
    .nunique()
    .reindex(month_order, fill_value=0)
)

fig_doctors = px.bar(
    x=doctor_month.index,
    y=doctor_month.values,
    title="Unique Doctors Visited by Month",
    text=doctor_month.values,
    labels={
        "x": "Month",
        "y": "Doctors"
    }
)

fig_doctors.update_traces(
    marker_color="#059669",
    textposition="outside"
)

fig_doctors.update_layout(
    template="plotly_white",
    height=380,
    title_x=0.5
)

st.plotly_chart(fig_doctors, use_container_width=True)

# -----------------------------------------
# Average Products Discussed per Visit
# -----------------------------------------

monthly_visits = (
    filtered_df
    .groupby("Month")
    .size()
)

monthly_discussions = {}

for month in month_order:

    if month in filtered_df["Month"].values:

        temp = filtered_df[
            filtered_df["Month"] == month
        ]

        discussions = 0

        for col in ["P1", "P2", "P3", "P4"]:
            discussions += temp[col].count()

        monthly_discussions[month] = discussions

avg_products = {}

for month in month_order:

    visits = monthly_visits.get(month, 0)

    discussions = monthly_discussions.get(month, 0)

    avg_products[month] = (
        discussions / visits if visits > 0 else 0
    )

fig_avg = px.line(
    x=list(avg_products.keys()),
    y=list(avg_products.values()),
    title="Average Products Discussed per Visit",
    markers=True,
    labels={
        "x": "Month",
        "y": "Products / Visit"
    }
)

fig_avg.update_traces(
    line=dict(color="#EA580C", width=4),
    marker=dict(size=9)
)

fig_avg.update_layout(
    template="plotly_white",
    height=380,
    title_x=0.5
)

st.plotly_chart(fig_avg, use_container_width=True)

st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Detailed table
st.markdown("## 📋 Detailed Product Breakdown")


product_counts =  get_product_counts_by_column(df, division_filter, month_filter)
filtered_df = df.copy()

if division_filter:
    filtered_df = filtered_df[
        filtered_df['Division'] == division_filter
    ]

if month_filter:
    filtered_df = filtered_df[
        filtered_df['Month'] == month_filter
    ]

if owner_filter:
    filtered_df = filtered_df[
        filtered_df['In-Field Activity: Owner Name'] == owner_filter
    ]

melted_df = filtered_df.melt(
    id_vars=['Division', 'Month'],
    value_vars=['P1', 'P2', 'P3', 'P4'],
    var_name='Position',
    value_name='Product'
)

melted_df = melted_df.dropna(subset=['Product'])

table_df = pd.pivot_table(
    melted_df,
    index=['Division', 'Product'],
    columns='Month',
    aggfunc='size',
    fill_value=0
).reset_index()


existing_months = [month for month in month_order if month in table_df.columns]

table_df = table_df[
    ["Division", "Product"] + existing_months
]

table_df["Total"] = table_df.iloc[:, 2:].sum(axis=1)
table_df["Average"] = table_df.iloc[:, 2:-1].mean(axis=1)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

# Export section
st.markdown("## 📥 Export & Share Dashboard")

product_counts = get_product_counts_by_column(df, division_filter, month_filter)
filtered_df = df.copy()
if division_filter:
    filtered_df = filtered_df[filtered_df['Division'] == division_filter]
if month_filter:
    filtered_df = filtered_df[filtered_df['Month'] == month_filter]
if owner_filter: 
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner_filter]    

# Create export data
export_data = pd.DataFrame([
    {
        'Product': product,
        'Discussions': count,
        'Rank': idx + 1
    }
    for idx, (product, count) in enumerate(product_counts.items())
])

col1, col2, col3 = st.columns(3)

with col1:
    # Excel Export
    excel_file = create_excel_report(product_counts, division_filter, month_filter, product_filter, df)
    st.download_button(
        label="📊 Download Excel Report",
        data=excel_file,
        file_name="Field_Activity_Dashboard.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    # CSV Export
    csv = export_data.to_csv(index=False)
    st.download_button(
        label="📄 Download CSV",
        data=csv,
        file_name="Product_Discussions.csv",
        mime="text/csv"
    )

with col3:
    st.markdown("**Share:** You can share this URL or download reports →")

st.markdown("""
---
            
### 📊 Dashboard Features:
- ✅ Interactive filters (Division, Month, Product)
- ✅ Real-time KPI calculations
- ✅ Multi-sheet Excel export with insights
- ✅ Responsive design optimized for all devices
- ✅ Color-coded visualizations
- ✅ Professional formatting

---
""")

st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "<b>📊 Field Activity Dashboard v2.0</b> | Powered by Streamlit & Plotly | "
    "Data last updated: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') +
    "</div>",
    unsafe_allow_html=True
)
