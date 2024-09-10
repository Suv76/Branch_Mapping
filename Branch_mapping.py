import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Function to format employee IDs
def format_emp_id(emp_id):
    if pd.isna(emp_id) or emp_id == '-':
        return np.nan
    try:
        emp_id = int(emp_id)  # Convert to integer to remove decimal places
        return str(emp_id).zfill(4)  # Add leading zeros if necessary
    except ValueError:
        return np.nan  # Return NaN for any non-numeric values

# Function to process the file and generate the output
def process_file(uploaded_file):
    # Load the file
    df = pd.read_excel(uploaded_file)

    # Define columns to keep
    columns_to_keep = ['Branch', 'Branch ID', 'State', 'AM', 'AM Emp ID', 'DM', 'DM Emp ID',
                       'RM', 'RM Emp ID', 'SH', 'SH Emp ID', 'ZM', 'ZM Emp ID', 'Senior ZH', 'Senior ZH Emp ID']
    df = df[columns_to_keep]

    # Define common columns and role sets
    common_columns = ['Branch', 'Branch ID', 'State']
    role_columns = {
        'AM': ['AM', 'AM Emp ID'],
        'DM': ['DM', 'DM Emp ID'],
        'RM': ['RM', 'RM Emp ID'],
        'SH': ['SH', 'SH Emp ID'],
        'ZM': ['ZM', 'ZM Emp ID'],
        'ZM': ['Senior ZH', 'Senior ZH Emp ID']
    }

    # Create a list to hold the new DataFrame segments
    segments = []

    # Iterate over each role and its corresponding columns
    for role, cols in role_columns.items():
        # Create a new DataFrame segment with the common columns and the current set of columns
        segment = df[common_columns + cols].copy()
        # Rename columns to match expected format
        segment.columns = common_columns + ['Name', 'Emp ID']
        # Add an extra 'Role' column for the current set
        segment['Role'] = role
        # Format the 'Emp ID' column
        segment['Emp ID'] = segment['Emp ID'].apply(format_emp_id)
        # Append the segment to the list
        segments.append(segment)

    # Concatenate all the segments vertically
    new_df = pd.concat(segments, ignore_index=True)

    # Remove rows where 'Emp ID' is NaN or not numeric
    new_df = new_df[pd.notna(new_df['Emp ID']) & new_df['Emp ID'].str.isnumeric()]

    # Add new column by concatenating Role and Emp ID
    new_df['Role_Emp_ID'] = 'SM' + new_df['Emp ID']

    # Convert 'Branch ID' and 'Role_Emp_ID' to string
    new_df['Branch ID'] = new_df['Branch ID'].astype(str)
    new_df['Role_Emp_ID'] = new_df['Role_Emp_ID'].astype(str)

    # Add a unique code by concatenating Role_Emp_ID and Branch ID
    new_df['Unique code'] = new_df['Role_Emp_ID'] + new_df['Branch ID']

    return new_df

# Streamlit UI
st.title("Branch Mapping")

# File uploader
uploaded_file = st.file_uploader("Upload the Branch Team Contact Details file", type=['xlsx'])

if uploaded_file:
    # Process the file and generate the output
    if st.button('Generate Output'):
        result_df = process_file(uploaded_file)
        st.write("Processing Complete!")

        # Create an Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, index=False)
        output.seek(0)

        # Download button for the output
        st.download_button(
            label="Download Output",
            data=output,
            file_name="Mapping.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
