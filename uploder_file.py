# File uploader
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file, sheet_name='Call Data')
        return df

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