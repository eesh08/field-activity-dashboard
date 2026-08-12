

def read_excel_data(file):
    """Load a workbook and select the first valid sheet if the sheet name differs."""
    try:
        excel_file = pd.ExcelFile(file)
        sheet_names = excel_file.sheet_names

        preferred_order = ["Call Data", "Data", "Sheet1", "Sheet"]
        for preferred in preferred_order:
            if preferred in sheet_names:
                return pd.read_excel(file, sheet_name=preferred)

        for sheet_name in sheet_names:
            df = pd.read_excel(file, sheet_name=sheet_name)
            if isinstance(df, pd.DataFrame) and not df.empty and len(df.columns) > 0:
                return df

        raise ValueError("No valid worksheet found in the Excel file.")
    except Exception:
        raise


# File uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

@st.cache_data
def load_data(file):
    try:
        return read_excel_data(file)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None
    
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is None:
        st.stop()

else:
    st.warning("👈 Please upload an Excel file to continue.")
    st.stop()