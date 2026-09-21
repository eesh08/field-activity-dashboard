from io import BytesIO

import pandas as pd
import streamlit as st
import xlsxwriter

from datacode.transformer import normalize_planned_data

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]


def ordered_months(values):
    """Return months in calendar order, preserving unseen values after the standard list."""
    ordered = []
    seen = set()
    for month in MONTH_ORDER:
        if month in values and month not in seen:
            ordered.append(month)
            seen.add(month)
    for month in values:
        if month not in seen:
            ordered.append(month)
            seen.add(month)
    return ordered


def create_excel_report_two_sheets(report_title, kpi_rows, breakdown_df, monthly_kpi_matrix_df=None, product_position_df=None, employee_product_df=None):
    """Create an Excel report with KPI summary, detailed breakdown, and optional matrix sheets."""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

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

    data_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })

    text_format = workbook.add_format({
        'border': 1,
        'align': 'left',
        'valign': 'vcenter'
    })

    ws_kpis = workbook.add_worksheet('KPI Summary')
    ws_kpis.set_column('A:A', 35)
    ws_kpis.set_column('B:B', 20)

    ws_kpis.merge_range('A1:B1', report_title, title_format)
    ws_kpis.write(2, 0, 'Metric', header_format)
    ws_kpis.write(2, 1, 'Value', header_format)

    row = 3
    for label, value in kpi_rows:
        ws_kpis.write(row, 0, label, text_format)
        ws_kpis.write(row, 1, value, data_format)
        row += 1

    def write_dataframe_sheet(worksheet, dataframe):
        worksheet.freeze_panes(1, 0)

        for col_idx, column_name in enumerate(dataframe.columns):
            worksheet.write(0, col_idx, column_name, header_format)

        for row_idx, row_values in enumerate(dataframe.itertuples(index=False), start=1):
            for col_idx, value in enumerate(row_values):
                fmt = text_format if isinstance(value, str) else data_format
                worksheet.write(row_idx, col_idx, value, fmt)

        for col_idx, column_name in enumerate(dataframe.columns):
            width = max(len(str(column_name)) + 2, 14)
            worksheet.set_column(col_idx, col_idx, width)

    ws_breakdown = workbook.add_worksheet('Detailed Breakdown')
    write_dataframe_sheet(ws_breakdown, breakdown_df)

    if monthly_kpi_matrix_df is not None:
        ws_monthly_matrix = workbook.add_worksheet('Monthly KPI Matrix')
        write_dataframe_sheet(ws_monthly_matrix, monthly_kpi_matrix_df)

    if product_position_df is not None:
        ws_product_position = workbook.add_worksheet('Product Position Matrix')
        write_dataframe_sheet(ws_product_position, product_position_df)

    if employee_product_df is not None:
        ws_employee_product = workbook.add_worksheet('Emp Product Division')
        write_dataframe_sheet(ws_employee_product, employee_product_df)

    workbook.close()
    output.seek(0)
    return output


@st.cache_data(show_spinner=False, ttl=3600)
def get_unique_products(df):
    """Extract all unique products from P1, P2, P3, P4 columns."""
    products = set()
    for col in ['P1', 'P2', 'P3', 'P4']:
        products.update(df[col].dropna().unique())
    return sorted(list(products))


@st.cache_data(show_spinner=False, ttl=3600)
def count_product_discussions(df, product, division=None, month=None, owner=None):
    """Count how many times a product was discussed."""
    filtered_df = df.copy()

    if division:
        filtered_df = filtered_df[filtered_df['Division'] == division]
    if month:
        filtered_df = filtered_df[filtered_df['Month'] == month]
    if owner:
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner]
    count = 0
    for col in ['P1', 'P2', 'P3', 'P4']:
        count += (filtered_df[col] == product).sum()

    return count


@st.cache_data(show_spinner=False, ttl=3600)
def get_product_counts_by_column(df, division=None, month=None, owner=None):
    """Get counts for each product across all columns."""
    filtered_df = df.copy()

    if division:
        filtered_df = filtered_df[filtered_df['Division'] == division]
    if month:
        filtered_df = filtered_df[filtered_df['Month'] == month]
    if owner:
        filtered_df = filtered_df[filtered_df['In-Field Activity: Owner Name'] == owner]

    product_counts = {}
    for col in ['P1', 'P2', 'P3', 'P4']:
        value_counts = filtered_df[col].value_counts()
        for product, count in value_counts.items():
            if pd.notna(product):
                product_counts[product] = product_counts.get(product, 0) + count

    return dict(sorted(product_counts.items(), key=lambda x: x[1], reverse=True))


@st.cache_data(show_spinner=False, ttl=3600)
def build_detailed_breakdown_table(filtered_df, month_order):
    """Create the detailed product breakdown table used in UI and exports."""
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
    table_df = table_df[["Division", "Product"] + existing_months]
    table_df["Total"] = table_df.iloc[:, 2:].sum(axis=1)
    table_df["Average"] = table_df.iloc[:, 2:-1].mean(axis=1)
    return table_df


@st.cache_data(show_spinner=False, ttl=3600)
def build_product_position_matrix(filtered_df, month_order):
    """Return product counts by P1/P2/P3/P4, division and month for dashboard and export."""
    if filtered_df.empty:
        return pd.DataFrame(columns=['Division', 'Month', 'Product', 'P1', 'P2', 'P3', 'P4', 'Total Discussions'])

    melted_df = filtered_df[['Division', 'Month', 'P1', 'P2', 'P3', 'P4']].copy()
    melted_df = melted_df.melt(
        id_vars=['Division', 'Month'],
        value_vars=['P1', 'P2', 'P3', 'P4'],
        var_name='Position',
        value_name='Product'
    )
    melted_df = melted_df.dropna(subset=['Product'])
    if melted_df.empty:
        return pd.DataFrame(columns=['Division', 'Month', 'Product', 'P1', 'P2', 'P3', 'P4', 'Total Discussions'])

    pivot_df = (
        melted_df.groupby(['Division', 'Month', 'Product', 'Position'], dropna=False, observed=False)
        .size()
        .reset_index(name='Count')
    )

    position_matrix = pivot_df.pivot_table(
        index=['Division', 'Month', 'Product'],
        columns='Position',
        values='Count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    for pos in ['P1', 'P2', 'P3', 'P4']:
        if pos not in position_matrix.columns:
            position_matrix[pos] = 0

    position_matrix = position_matrix[['Division', 'Month', 'Product', 'P1', 'P2', 'P3', 'P4']].copy()
    position_matrix['Total Discussions'] = position_matrix[['P1', 'P2', 'P3', 'P4']].sum(axis=1)
    position_matrix['Month'] = pd.Categorical(position_matrix['Month'], categories=month_order, ordered=True)
    position_matrix = position_matrix.sort_values(['Division', 'Month', 'Total Discussions', 'Product'], ascending=[True, True, False, True]).reset_index(drop=True)
    position_matrix['Month'] = position_matrix['Month'].astype(str)
    return position_matrix


@st.cache_data(show_spinner=False, ttl=3600)
def build_employee_product_matrix(filtered_df):
    """Return counts for each employee/product across P1-P4 with division and employee code."""
    if filtered_df.empty:
        return pd.DataFrame(columns=['Division', 'Employee Name', 'Employee Code', 'Product', 'P1', 'P2', 'P3', 'P4', 'Total Discussions'])

    employee_name_col = 'In-Field Activity: Owner Name' if 'In-Field Activity: Owner Name' in filtered_df.columns else None
    employee_code_col = 'Employee Code' if 'Employee Code' in filtered_df.columns else None

    working_df = filtered_df.copy()
    if employee_name_col is None:
        working_df['Employee Name'] = 'Unknown'
        employee_name_col = 'Employee Name'
    if employee_code_col is None:
        working_df['Employee Code'] = ''
        employee_code_col = 'Employee Code'

    melted_df = working_df[['Division', employee_name_col, employee_code_col, 'P1', 'P2', 'P3', 'P4']].copy()
    melted_df = melted_df.rename(columns={employee_name_col: 'Employee Name', employee_code_col: 'Employee Code'})
    melted_df = melted_df.melt(
        id_vars=['Division', 'Employee Name', 'Employee Code'],
        value_vars=['P1', 'P2', 'P3', 'P4'],
        var_name='Position',
        value_name='Product'
    )
    melted_df = melted_df.dropna(subset=['Product'])
    if melted_df.empty:
        return pd.DataFrame(columns=['Division', 'Employee Name', 'Employee Code', 'Product', 'P1', 'P2', 'P3', 'P4', 'Total Discussions'])

    pivot_df = (
        melted_df.groupby(['Division', 'Employee Name', 'Employee Code', 'Product', 'Position'], dropna=False, observed=False)
        .size()
        .reset_index(name='Count')
    )

    employee_matrix = pivot_df.pivot_table(
        index=['Division', 'Employee Name', 'Employee Code', 'Product'],
        columns='Position',
        values='Count',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    for pos in ['P1', 'P2', 'P3', 'P4']:
        if pos not in employee_matrix.columns:
            employee_matrix[pos] = 0

    employee_matrix = employee_matrix[['Division', 'Employee Name', 'Employee Code', 'Product', 'P1', 'P2', 'P3', 'P4']].copy()
    employee_matrix['Total Discussions'] = employee_matrix[['P1', 'P2', 'P3', 'P4']].sum(axis=1)
    employee_matrix = employee_matrix.sort_values(['Division', 'Employee Name', 'Employee Code', 'Total Discussions', 'Product'], ascending=[True, True, True, False, True]).reset_index(drop=True)
    return employee_matrix


@st.cache_data(show_spinner=False, ttl=3600)
def build_monthly_kpi_breakdown_table(
    filtered_df,
    month_order,
    include_clm=False,
    date_column='CallDate',
    fallback_date_column=None
):
    """Create a month-columns KPI matrix with rows per division and KPI."""
    kpi_names = [
        'Total Visits',
        'Unique Products',
        'Total Discussions',
        'Unique Doctors',
        'Avg Products / Visit',
        'Visits / Rep / Month',
        'Visits / Rep / Day',
    ]
    if include_clm:
        kpi_names.insert(6, 'Visits with CLM')

    if filtered_df.empty:
        return pd.DataFrame(columns=['Division', 'KPI'] + month_order)

    working_df = filtered_df.copy()
    if 'Month' in working_df.columns:
        working_df['Month'] = pd.Categorical(working_df['Month'], categories=month_order, ordered=True)

    monthly_rows = []
    grouped = working_df.groupby(['Month', 'Division'], dropna=False, observed=False)

    for (month, division), group_df in grouped:
        if group_df.empty:
            continue

        month_value = str(month)
        if month_value not in month_order:
            continue

        total_visits = len(group_df)
        total_reps = group_df['In-Field Activity: Owner Name'].nunique()
        unique_doctors = group_df['Customer ID'].nunique()

        total_discussions = 0
        unique_products = set()
        for col in ['P1', 'P2', 'P3', 'P4']:
            non_null_products = group_df[col].dropna()
            total_discussions += non_null_products.shape[0]
            unique_products.update(non_null_products.unique().tolist())

        avg_products_per_visit = total_discussions / total_visits if total_visits > 0 else 0
        visits_per_rep_month = total_visits / total_reps if total_reps > 0 else 0

        date_series = group_df[date_column] if date_column in group_df.columns else pd.Series(dtype='datetime64[ns]')
        if fallback_date_column and fallback_date_column in group_df.columns:
            date_series = date_series.fillna(group_df[fallback_date_column])
        unique_days = date_series.nunique()
        visits_per_rep_day = total_visits / (total_reps * unique_days) if total_reps > 0 and unique_days > 0 else 0

        row = {
            'Month': month,
            'Division': division,
            'Total Visits': total_visits,
            'Unique Products': len(unique_products),
            'Total Discussions': total_discussions,
            'Unique Doctors': unique_doctors,
            'Avg Products / Visit': round(avg_products_per_visit, 2),
            'Visits / Rep / Month': round(visits_per_rep_month, 2),
            'Visits / Rep / Day': round(visits_per_rep_day, 2),
        }

        if include_clm and 'Call with CLM' in group_df.columns:
            row['Visits with CLM'] = int((group_df['Call with CLM'] == True).sum())

        monthly_rows.append(row)

    monthly_df = pd.DataFrame(monthly_rows)
    if monthly_df.empty:
        return pd.DataFrame(columns=['Division', 'KPI'] + month_order)

    divisions = sorted([str(d) for d in monthly_df['Division'].dropna().unique().tolist()])
    matrix_rows = []

    for division in divisions:
        division_df = monthly_df[monthly_df['Division'].astype(str) == division]
        for kpi_name in kpi_names:
            matrix_row = {'Division': division, 'KPI': kpi_name}
            for month in month_order:
                value_row = division_df[division_df['Month'].astype(str) == month]
                if value_row.empty:
                    matrix_row[month] = 0
                else:
                    matrix_row[month] = value_row.iloc[0][kpi_name]
            matrix_rows.append(matrix_row)

    matrix_df = pd.DataFrame(matrix_rows)
    return matrix_df[['Division', 'KPI'] + month_order]