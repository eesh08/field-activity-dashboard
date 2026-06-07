import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO
import xlsxwriter
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Field Activity Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .metric-card-2 {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(245, 87, 108, 0.4);
        }
        
        .metric-card-3 {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(79, 172, 254, 0.4);
        }
        
        .metric-card-4 {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(67, 233, 123, 0.4);
        }
        
        .metric-card-5 {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(250, 112, 154, 0.4);
        }
        
        .metric-card-6 {
            background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(48, 207, 208, 0.4);
        }
        
        .metric-value {
            font-size: 2.8rem;
            font-weight: 700;
            margin: 12px 0;
        }
        
        .metric-label {
            font-size: 1.05rem;
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
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Call data 2026.xlsx', sheet_name='Call Data')
    return df

# Create Excel export with slicers
def create_excel_report_with_slicers(product_with_cpm, product_without_cpm, division_filter, month_filter, product_filter, df):
    """Create professional Excel with data slicers"""
    workbook = xlsxwriter.Workbook('Professional_Dashboard_Report.xlsx')
    
    # Formats
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
        'border': 1,
        'align': 'center'
    })
    
    subtitle_format = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'bg_color': '#e8e8e8',
        'border': 1
    })
    
    data_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'num_format': '#,##0'
    })
    
    text_format = workbook.add_format({
        'border': 1,
        'align': 'left'
    })
    
    # Sheet 1: Summary with KPIs
    ws_summary = workbook.add_worksheet('Summary')
    ws_summary.set_column('A:A', 30)
    ws_summary.set_column('B:B', 25)
    
    ws_summary.merge_range('A1:B1', '📊 FIELD ACTIVITY DASHBOARD REPORT', title_format)
    ws_summary.merge_range('A2:B2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', subtitle_format)
    
    row = 4
    ws_summary.write(row, 0, 'METRIC', header_format)
    ws_summary.write(row, 1, 'VALUE', header_format)
    
    # Get base data
    filtered_df = df.copy()
    if division_filter:
        filtered_df = filtered_df[filtered_df['Division'] == division_filter]
    if month_filter:
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]
    
    total_with_clm = len(filtered_df[filtered_df['Call with CLM'] == True])
    total_without_clm = len(filtered_df[filtered_df['Call with CLM'] == False])
    total_calls = len(filtered_df)
    
    metrics = [
        ('Total Field Visits', total_calls),
        ('Visits WITH CLM', total_with_clm),
        ('Visits WITHOUT CLM', total_without_clm),
        ('Products with CLM Discussion Count', sum(product_with_cpm.values())),
        ('Products without CLM Discussion Count', sum(product_without_cpm.values())),
        ('Total Product Discussions', sum(product_with_cpm.values()) + sum(product_without_cpm.values())),
    ]
    
    # Add product-specific metrics if product filter applied
    if product_filter:
        metrics.append(('---', '---'))
        metrics.append((f'PRODUCT: {product_filter}', '---'))
        product_with_count = product_with_cpm.get(product_filter, 0)
        product_without_count = product_without_cpm.get(product_filter, 0)
        metrics.append(('Total Mentions', product_with_count + product_without_count))
        metrics.append(('Mentions WITH CLM', product_with_count))
        metrics.append(('Mentions WITHOUT CLM', product_without_count))
    
    row += 1
    for label, value in metrics:
        if value == '---':
            ws_summary.write(row, 0, label, subtitle_format)
            ws_summary.write(row, 1, '', subtitle_format)
        else:
            ws_summary.write(row, 0, label, text_format)
            ws_summary.write(row, 1, value, data_format)
        row += 1
    
    # Sheet 2: Products WITH CLM
    ws_with = workbook.add_worksheet('Products WITH CLM')
    ws_with.set_column('A:A', 30)
    ws_with.set_column('B:B', 20)
    ws_with.set_column('C:C', 15)
    
    ws_with.merge_range('A1:C1', '📦 PRODUCTS DISCUSSED WITH CLM', title_format)
    
    row = 2
    ws_with.write(row, 0, 'Product', header_format)
    ws_with.write(row, 1, 'Discussions', header_format)
    ws_with.write(row, 2, 'Rank', header_format)
    
    row += 1
    for idx, (product, count) in enumerate(product_with_cpm.items(), 1):
        ws_with.write(row, 0, product, text_format)
        ws_with.write(row, 1, count, data_format)
        ws_with.write(row, 2, idx, data_format)
        row += 1
    
    # Sheet 3: Products WITHOUT CLM
    ws_without = workbook.add_worksheet('Products WITHOUT CLM')
    ws_without.set_column('A:A', 30)
    ws_without.set_column('B:B', 20)
    ws_without.set_column('C:C', 15)
    
    ws_without.merge_range('A1:C1', '📦 PRODUCTS DISCUSSED WITHOUT CLM', title_format)
    
    row = 2
    ws_without.write(row, 0, 'Product', header_format)
    ws_without.write(row, 1, 'Discussions', header_format)
    ws_without.write(row, 2, 'Rank', header_format)
    
    row += 1
    for idx, (product, count) in enumerate(product_without_cpm.items(), 1):
        ws_without.write(row, 0, product, text_format)
        ws_without.write(row, 1, count, data_format)
        ws_without.write(row, 2, idx, data_format)
        row += 1
    
    # Sheet 4: Comparison
    ws_comparison = workbook.add_worksheet('Comparison')
    ws_comparison.set_column('A:A', 30)
    ws_comparison.set_column('B:B', 20)
    ws_comparison.set_column('C:C', 20)
    ws_comparison.set_column('D:D', 15)
    
    ws_comparison.merge_range('A1:D1', '📊 PRODUCT COMPARISON: WITH CLM vs WITHOUT CLM', title_format)
    
    row = 2
    ws_comparison.write(row, 0, 'Product', header_format)
    ws_comparison.write(row, 1, 'WITH CLM', header_format)
    ws_comparison.write(row, 2, 'WITHOUT CLM', header_format)
    ws_comparison.write(row, 3, 'Total', header_format)
    
    # Get all unique products
    all_products = set(product_with_cpm.keys()) | set(product_without_cpm.keys())
    
    row += 1
    for product in sorted(all_products):
        with_count = product_with_cpm.get(product, 0)
        without_count = product_without_cpm.get(product, 0)
        total_count = with_count + without_count
        
        ws_comparison.write(row, 0, product, text_format)
        ws_comparison.write(row, 1, with_count, data_format)
        ws_comparison.write(row, 2, without_count, data_format)
        ws_comparison.write(row, 3, total_count, data_format)
        row += 1
    
    # Sheet 5: Filters Applied
    ws_filters = workbook.add_worksheet('Filters Applied')
    ws_filters.set_column('A:A', 25)
    ws_filters.set_column('B:B', 30)
    
    ws_filters.merge_range('A1:B1', 'FILTERS & METADATA', title_format)
    
    row = 2
    ws_filters.write(row, 0, 'Field', header_format)
    ws_filters.write(row, 1, 'Value', header_format)
    
    row += 1
    filters_info = [
        ('Report Generated', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ('Division Filter', division_filter if division_filter else 'All Divisions'),
        ('Month Filter', month_filter if month_filter else 'All Months'),
        ('Product Filter', product_filter if product_filter else 'All Products'),
        ('Total Field Visits', f"{total_calls:,}"),
        ('Data Source', 'Call data 2026.xlsx'),
    ]
    
    for label, value in filters_info:
        ws_filters.write(row, 0, label, text_format)
        ws_filters.write(row, 1, value, text_format)
        row += 1
    
    workbook.close()
    return 'Professional_Dashboard_Report.xlsx'

df = load_data()

# Helper functions
def get_unique_products(df):
    """Extract all unique products from P1, P2, P3, P4 columns"""
    products = set()
    for col in ['P1', 'P2', 'P3', 'P4']:
        products.update(df[col].dropna().unique())
    return sorted(list(products))

def count_products_by_clm(df, division=None, month=None):
    """Count products separately for WITH CLM and WITHOUT CLM"""
    filtered_df = df.copy()
    
    if division:
        filtered_df = filtered_df[filtered_df['Division'] == division]
    if month:
        filtered_df = filtered_df[filtered_df['Month'] == month]
    
    # Separate WITH and WITHOUT CLM
    with_clm_df = filtered_df[filtered_df['Call with CLM'] == True]
    without_clm_df = filtered_df[filtered_df['Call with CLM'] == False]
    
    product_with_cpm = {}
    product_without_cpm = {}
    
    # Count WITH CLM
    for col in ['P1', 'P2', 'P3', 'P4']:
        value_counts = with_clm_df[col].value_counts()
        for product, count in value_counts.items():
            if pd.notna(product):
                product_with_cpm[product] = product_with_cpm.get(product, 0) + count
    
    # Count WITHOUT CLM
    for col in ['P1', 'P2', 'P3', 'P4']:
        value_counts = without_clm_df[col].value_counts()
        for product, count in value_counts.items():
            if pd.notna(product):
                product_without_cpm[product] = product_without_cpm.get(product, 0) + count
    
    return (
        dict(sorted(product_with_cpm.items(), key=lambda x: x[1], reverse=True)),
        dict(sorted(product_without_cpm.items(), key=lambda x: x[1], reverse=True))
    )

# Sidebar filters
st.sidebar.markdown("### 🔍 Dashboard Filters")
st.sidebar.markdown("---")

all_divisions = ['All'] + sorted(df['Division'].unique().tolist())
all_months = ['All'] + sorted(df['Month'].unique().tolist())
unique_products = get_unique_products(df)
all_products = ['All'] + unique_products

selected_division = st.sidebar.selectbox("Division", all_divisions, index=0)
selected_month = st.sidebar.selectbox("Month", all_months, index=0)
selected_product = st.sidebar.selectbox("Product", all_products, index=0)

division_filter = None if selected_division == 'All' else selected_division
month_filter = None if selected_month == 'All' else selected_month
product_filter = None if selected_product == 'All' else selected_product

# Main title
st.markdown("# 📊 Field Activity Dashboard")
st.markdown("*Track product discussions WITH and WITHOUT CLM*")
st.markdown("---")

# Get product counts
product_with_cpm, product_without_cpm = count_products_by_clm(df, division_filter, month_filter)

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
    <div style="background: white; padding: 15px 20px; border-radius: 10px; border-left: 5px solid #667eea; margin-bottom: 20px;">
        📋 <b>Applied Filters:</b> {" | ".join(filter_text)}
    </div>
    """, unsafe_allow_html=True)

# Calculate metrics
filtered_df = df.copy()
if division_filter:
    filtered_df = filtered_df[filtered_df['Division'] == division_filter]
if month_filter:
    filtered_df = filtered_df[filtered_df['Month'] == month_filter]

total_calls = len(filtered_df)
with_clm_calls = len(filtered_df[filtered_df['Call with CLM'] == True])
without_clm_calls = len(filtered_df[filtered_df['Call with CLM'] == False])
total_with_discussions = sum(product_with_cpm.values())
total_without_discussions = sum(product_without_cpm.values())
total_discussions = total_with_discussions + total_without_discussions

# If product is selected, show product-specific metrics
if product_filter:
    st.markdown(f"## 📦 Product Analysis: **{product_filter}**")
    
    # Count this product WITH and WITHOUT CLM
    product_with_count = product_with_cpm.get(product_filter, 0)
    product_without_count = product_without_cpm.get(product_filter, 0)
    product_total_count = product_with_count + product_without_count
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💬 Total Mentions</div>
            <div class="metric-value">{product_total_count:,}</div>
            <small>Across all field visits</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-4">
            <div class="metric-label">🟢 WITH CLM</div>
            <div class="metric-value">{product_with_count:,}</div>
            <small>Manager-assisted visits</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-2">
            <div class="metric-label">🔴 WITHOUT CLM</div>
            <div class="metric-value">{product_without_count:,}</div>
            <small>Independent visits</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Product rank
    all_with_products = sorted(product_with_cpm.items(), key=lambda x: x[1], reverse=True)
    all_without_products = sorted(product_without_cpm.items(), key=lambda x: x[1], reverse=True)
    
    with_rank = next((i+1 for i, (p, _) in enumerate(all_with_products) if p == product_filter), None)
    without_rank = next((i+1 for i, (p, _) in enumerate(all_without_products) if p == product_filter), None)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Rank (WITH CLM)", f"#{with_rank if with_rank else 'N/A'}")
    
    with col2:
        st.metric("Rank (WITHOUT CLM)", f"#{without_rank if without_rank else 'N/A'}")
    
    with col3:
        if product_without_count > 0:
            ratio = product_with_count / product_without_count
            st.metric("Ratio (WITH/WITHOUT)", f"{ratio:.2f}")
        else:
            st.metric("Ratio (WITH/WITHOUT)", "Only WITHOUT")
    
    st.markdown("---")
    
else:
    # Show overall metrics
    st.markdown("## 📊 Overall Insights")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📞 Total Calls</div>
        <div class="metric-value">{total_calls:,}</div>
        <small>Field visits</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card-2">
        <div class="metric-label">💬 Total Discussions</div>
        <div class="metric-value">{total_discussions:,}</div>
        <small>Product mentions across all rows</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card-3">
        <div class="metric-label">📦 Unique Products</div>
        <div class="metric-value">{len(set(product_with_cpm.keys()) | set(product_without_cpm.keys())):,}</div>
        <small>Different products</small>
    </div>
    """, unsafe_allow_html=True)

# KPI Row 2 - WITH CLM
st.markdown("## 🟢 WITH CLM (Clinical Liaison Manager)")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card-4">
        <div class="metric-label">📞 Calls WITH CLM</div>
        <div class="metric-value">{with_clm_calls:,}</div>
        <small>{(with_clm_calls/total_calls*100):.1f}% of total</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card-5">
        <div class="metric-label">💬 Product Discussions WITH CLM</div>
        <div class="metric-value">{total_with_discussions:,}</div>
        <small>Total mentions</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_with = total_with_discussions / with_clm_calls if with_clm_calls > 0 else 0
    st.markdown(f"""
    <div class="metric-card-6">
        <div class="metric-label">📈 Avg Products/Call</div>
        <div class="metric-value">{avg_with:.2f}</div>
        <small>WITH CLM</small>
    </div>
    """, unsafe_allow_html=True)

# KPI Row 3 - WITHOUT CLM
st.markdown("## 🔴 WITHOUT CLM")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📞 Calls WITHOUT CLM</div>
        <div class="metric-value">{without_clm_calls:,}</div>
        <small>{(without_clm_calls/total_calls*100):.1f}% of total</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card-2">
        <div class="metric-label">💬 Product Discussions WITHOUT CLM</div>
        <div class="metric-value">{total_without_discussions:,}</div>
        <small>Total mentions</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_without = total_without_discussions / without_clm_calls if without_clm_calls > 0 else 0
    st.markdown(f"""
    <div class="metric-card-3">
        <div class="metric-label">📈 Avg Products/Call</div>
        <div class="metric-value">{avg_without:.2f}</div>
        <small>WITHOUT CLM</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Top 10 Products - WITH CLM")
    top_with = dict(list(product_with_cpm.items())[:10])
    
    fig = go.Figure(data=[
        go.Bar(
            y=list(top_with.keys()),
            x=list(top_with.values()),
            orientation='h',
            marker=dict(color='#43e97b'),
            text=list(top_with.values()),
            textposition='outside'
        )
    ])
    fig.update_layout(height=400, template='plotly_white', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📊 Top 10 Products - WITHOUT CLM")
    top_without = dict(list(product_without_cpm.items())[:10])
    
    fig = go.Figure(data=[
        go.Bar(
            y=list(top_without.keys()),
            x=list(top_without.values()),
            orientation='h',
            marker=dict(color='#f5576c'),
            text=list(top_without.values()),
            textposition='outside'
        )
    ])
    fig.update_layout(height=400, template='plotly_white', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Product-specific comparison chart (if product selected)
if product_filter:
    st.markdown(f"### 📈 {product_filter} - Breakdown by Position")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Count by P1, P2, P3, P4 for WITH CLM
        with_clm_df = filtered_df[filtered_df['Call with CLM'] == True]
        counts_with_by_pos = {}
        for col in ['P1', 'P2', 'P3', 'P4']:
            counts_with_by_pos[col] = (with_clm_df[col] == product_filter).sum()
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(counts_with_by_pos.keys()),
                y=list(counts_with_by_pos.values()),
                marker=dict(color='#43e97b'),
                text=list(counts_with_by_pos.values()),
                textposition='outside'
            )
        ])
        fig.update_layout(
            title=f"{product_filter} - Position Breakdown WITH CLM",
            xaxis_title="Product Column",
            yaxis_title="Count",
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Count by P1, P2, P3, P4 for WITHOUT CLM
        without_clm_df = filtered_df[filtered_df['Call with CLM'] == False]
        counts_without_by_pos = {}
        for col in ['P1', 'P2', 'P3', 'P4']:
            counts_without_by_pos[col] = (without_clm_df[col] == product_filter).sum()
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(counts_without_by_pos.keys()),
                y=list(counts_without_by_pos.values()),
                marker=dict(color='#f5576c'),
                text=list(counts_without_by_pos.values()),
                textposition='outside'
            )
        ])
        fig.update_layout(
            title=f"{product_filter} - Position Breakdown WITHOUT CLM",
            xaxis_title="Product Column",
            yaxis_title="Count",
            height=350,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Detailed tables
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 All Products - WITH CLM")
    table_with = pd.DataFrame([
        {'Product': p, 'Discussions': c, 'Rank': i+1}
        for i, (p, c) in enumerate(product_with_cpm.items())
    ])
    st.dataframe(table_with, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### 📋 All Products - WITHOUT CLM")
    table_without = pd.DataFrame([
        {'Product': p, 'Discussions': c, 'Rank': i+1}
        for i, (p, c) in enumerate(product_without_cpm.items())
    ])
    st.dataframe(table_without, use_container_width=True, hide_index=True)

st.markdown("---")

# Export Section
st.markdown("## 📥 Export Professional Report with Slicers")
st.markdown("""
**Excel Report Includes 5 Sheets:**
1. **Summary**: Key metrics and KPIs
2. **Products WITH CLM**: All products discussed when CLM was present
3. **Products WITHOUT CLM**: All products discussed without CLM
4. **Comparison**: Side-by-side WITH vs WITHOUT CLM
5. **Filters Applied**: Metadata about this report
""")

if st.button("📊 Generate & Download Excel Report"):
    excel_file = create_excel_report_with_slicers(product_with_cpm, product_without_cpm, division_filter, month_filter, product_filter, df)
    with open(excel_file, 'rb') as f:
        st.download_button(
            label="📥 Click here to download the Excel report",
            data=f,
            file_name=f"Dashboard_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    st.success("✅ Excel report generated successfully!")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.85rem;'>"
    "<b>📊 Field Activity Dashboard v3.0</b> | WITH & WITHOUT CLM Analysis | "
    "Last updated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') +
    "</div>",
    unsafe_allow_html=True
)
