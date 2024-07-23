import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# Function to load data from Excel file
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

# Function to save modified data to Excel
def save_data(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Function to convert image to Base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Function to set background with custom image and styles
def set_background_and_styles(image_path):
    bin_str = get_base64_of_bin_file(image_path)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        color: white; /* Text color */
        font-family: 'Roboto', sans-serif; /* Stylish font */
    }}
    .title {{
        background-color: white; /* White background for titles */
        padding: 10px; /* Padding around titles */
        border-radius: 5px; /* Rounded corners */
        margin-bottom: 20px; /* Space below titles */
    }}
    .stButton button {{
        color: black; /* Text color for buttons */
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background and styles


# Rest of your Streamlit app code
# Load the uploaded file, sidebar, modify rows, save changes, etc.

# Example usage of the updated styles
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

if uploaded_file is not None:
    if "df" not in st.session_state:
        st.session_state.df = load_data(uploaded_file)

    df = st.session_state.df

    # Centered title with white background
    st.markdown("<h2 class='title' style='text-align: center;'>Choose an Excel file</h2>", unsafe_allow_html=True)

    # Display the dataframe
    st.dataframe(df)

    # Sidebar for filtering data
    st.sidebar.markdown("<h2 class='title' style='text-align: center;'>Filter Data</h2>", unsafe_allow_html=True)
    column_to_filter = st.sidebar.selectbox("Select column to filter", df.columns)
    filter_value = st.sidebar.text_input(f"Enter value to filter {column_to_filter}")
    if filter_value:
        filtered_df = df[df[column_to_filter].astype(str).str.contains(filter_value, na=False)]
        st.dataframe(filtered_df)

    # Centered title for adding new row
    st.markdown("<h2 class='title' style='text-align: center;'>Add New Row</h2>", unsafe_allow_html=True)
    new_row = {col: st.text_input(f"Enter value for {col}") for col in df.columns}
    if st.button("Add Row"):
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Row added")
        st.experimental_rerun()

    # Centered title for deleting a row
    st.markdown("<h2 class='title' style='text-align: center;'>Delete Row</h2>", unsafe_allow_html=True)
    index_to_delete = st.number_input("Enter row index to delete", min_value=0, max_value=len(df) - 1, step=1)
    if st.button("Delete Row"):
        if not df.empty and index_to_delete < len(df):
            st.session_state.df = st.session_state.df.drop(index_to_delete).reset_index(drop=True)
            st.success("Row deleted")
            st.experimental_rerun()
        else:
            st.error("Invalid index. Please try again.")

    # Centered title for modifying a row
    st.markdown("<h2 class='title' style='text-align: center;'>Modify Row</h2>", unsafe_allow_html=True)
    index_to_modify = st.number_input("Enter row index to modify", min_value=0, max_value=len(df) - 1, step=1)

    if index_to_modify < len(df):
        modify_container = st.container()
        new_values = {}
        for col in df.columns:
            new_values[col] = modify_container.text_input(f"Enter new value for {col} at row {index_to_modify}", value=str(df.at[index_to_modify, col]))

        if modify_container.button("Modify Row"):
            for col in df.columns:
                st.session_state.df.at[index_to_modify, col] = new_values[col]
            st.success("Row modified")
            st.experimental_rerun()
    else:
        st.error("Invalid index. Please try again.")

    # Save changes and provide download link for the modified file
    if st.button("Save Changes"):
        modified_file = save_data(st.session_state.df)
        st.download_button(
            label="Download Modified File",
            data=modified_file,
            file_name="modified_dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("Changes saved and ready to download")
