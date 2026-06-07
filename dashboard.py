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
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
            border: 2px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.6);
        }
        
        .metric-card-2 {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(245, 87, 108, 0.4);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .metric-card-3 {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(79, 172, 254, 0.4);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .metric-card-4 {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 8px 16px rgba(67, 233, 123, 0.4);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .metric-value {
            font-size: 2.8rem;
            font-weight: 700;
            margin: 12px 0;
            letter-spacing: 1px;
        }
        
        .metric-label {
            font-size: 1.05rem;
            opacity: 0.95;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('Call data 2026.xlsx', sheet_name='Call Data')
    return df

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
    
    metrics = [
        ('Total Calls', len(filtered_df)),
        ('Unique Products', len(product_counts)),
        ('Total Product Discussions', sum(product_counts.values())),
        ('Avg Products per Call', round(sum(product_counts.values()) / len(filtered_df), 2) if len(filtered_df) > 0 else 0),
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

df = load_data()

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

selected_division = st.sidebar.selectbox("Division", all_divisions, index=0)
selected_month = st.sidebar.selectbox("Month", all_months, index=0)
selected_product = st.sidebar.selectbox("Product", all_products, index=0)

# Prepare filter values
division_filter = None if selected_division == 'All' else selected_division
month_filter = None if selected_month == 'All' else selected_month
product_filter = None if selected_product == 'All' else selected_product

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
    
    counts_by_col = {}
    for col in ['P1', 'P2', 'P3', 'P4']:
        count_col = (filtered_df[col] == product_filter).sum()
        counts_by_col[col] = count_col
    
    # KPI Cards for single product
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    total_calls = len(filtered_df)
    total_products = len(product_counts)
    total_discussions = sum(product_counts.values())
    avg_per_call = total_discussions / total_calls if total_calls > 0 else 0
    
    st.markdown("## 📊 Overall Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
            <div class="metric-label">📦 Unique Products</div>
            <div class="metric-value">{total_products:,}</div>
            <small>Different products</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-3">
            <div class="metric-label">💬 Total Discussions</div>
            <div class="metric-value">{total_discussions:,}</div>
            <small>All mentions</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-4">
            <div class="metric-label">📈 Avg Products/Call</div>
            <div class="metric-value">{avg_per_call:.2f}</div>
            <small>Per visit</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

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
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_n = min(15, len(product_counts))
        top_products = dict(list(product_counts.items())[:top_n])
        
        fig_top = go.Figure(data=[
            go.Bar(
                y=list(top_products.keys()),
                x=list(top_products.values()),
                orientation='h',
                marker=dict(
                    color=list(top_products.values()),
                    colorscale='Viridis',
                    line=dict(color='#333', width=1.5)
                ),
                text=list(top_products.values()),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Discussions: %{x}<extra></extra>'
            )
        ])
        fig_top.update_layout(
            title=f"Top {top_n} Products by Discussion Count",
            xaxis_title="Number of Discussions",
            yaxis_title="Product",
            height=500,
            showlegend=False,
            template='plotly_white',
            yaxis={'categoryorder': 'total ascending'}
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

st.markdown("---")

# Detailed table
st.markdown("## 📋 Detailed Product Breakdown")

product_counts = get_product_counts_by_column(df, division_filter, month_filter)
table_data = []
for product, count in product_counts.items():
    table_data.append({
        'Product': product,
        'Total Discussions': count
    })

table_df = pd.DataFrame(table_data)
st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        'Product': st.column_config.TextColumn('Product', width='medium'),
        'Total Discussions': st.column_config.ProgressColumn(
            'Total Discussions',
            min_value=0,
            max_value=max(table_df['Total Discussions']) if len(table_df) > 0 else 1
        )
    }
)

# Footer
st.markdown("---")

# Export section
st.markdown("## 📥 Export & Share Dashboard")

product_counts = get_product_counts_by_column(df, division_filter, month_filter)
filtered_df = df.copy()
if division_filter:
    filtered_df = filtered_df[filtered_df['Division'] == division_filter]
if month_filter:
    filtered_df = filtered_df[filtered_df['Month'] == month_filter]

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
### 📋 How to Share the Dashboard:

1. **Live Dashboard Link**: Share the local URL (http://localhost:8501) with your team
2. **Excel Report**: Download the comprehensive Excel report with multiple sheets
3. **CSV Export**: Export product data for further analysis
4. **Deployment Options**:
   - **Streamlit Cloud**: Deploy free at https://share.streamlit.io/
   - **Heroku**: Deploy with Heroku hosting
   - **Local Server**: Share via LAN for team access

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
