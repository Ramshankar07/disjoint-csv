import streamlit as st
import pandas as pd
import re
import io
import zipfile
import openpyxl

def filter_alphanumeric(df, column_name):
    # Keep only rows where the column's value contains only alphanumeric characters
    df = df[df[column_name].apply(lambda x: bool(re.match('^[a-zA-Z0-9]+$', str(x))))]
    return df

def safe_read_csv(file):
    try:
        # Reset the file pointer to the beginning
        file.seek(0)
        return pd.read_csv(file)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

def validate_column_name(file1, file2, column_name):
    df1 = safe_read_csv(file1)
    df2 = safe_read_csv(file2)
    
    if df1.empty and df2.empty:
        return False, "Both uploaded files are empty or couldn't be read. Please upload valid CSV files."
    elif df1.empty:
        return False, "The first uploaded file is empty or couldn't be read. Please upload a valid CSV file."
    elif df2.empty:
        return False, "The second uploaded file is empty or couldn't be read. Please upload a valid CSV file."
    
    if column_name not in df1.columns and column_name not in df2.columns:
        return False, f"The specified column name '{column_name}' is not present in either file. Available columns in first file: {', '.join(df1.columns)}\nAvailable columns in second file: {', '.join(df2.columns)}"
    elif column_name not in df1.columns:
        return False, f"The specified column name '{column_name}' is not present in the first file. Available columns: {', '.join(df1.columns)}"
    elif column_name not in df2.columns:
        return False, f"The specified column name '{column_name}' is not present in the second file. Available columns: {', '.join(df2.columns)}"
    return True, ""

def process_csv_files(file1, file2, column_name):
    # Load the two CSV files
    sheet1 = safe_read_csv(file1)
    sheet2 = safe_read_csv(file2)

    if sheet1.empty or sheet2.empty:
        st.error("One or both of the uploaded files are empty or couldn't be read. Please upload valid CSV files.")
        return None, None, None

    # Filter out rows that do not have alphanumeric values
    sheet1 = filter_alphanumeric(sheet1, column_name)
    sheet2 = filter_alphanumeric(sheet2, column_name)

    # Find unique values in each sheet
    unique_sheet1 = sheet1[~sheet1[column_name].isin(sheet2[column_name])]
    unique_sheet2 = sheet2[~sheet2[column_name].isin(sheet1[column_name])]

    # Find common values between both sheets
    common = pd.merge(sheet1, sheet2, on=column_name)

    return unique_sheet1, unique_sheet2, common

def create_excel_file(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def create_zip_file(unique_sheet1, unique_sheet2, common):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("unique_sheet1.xlsx", create_excel_file(unique_sheet1))
        zip_file.writestr("unique_sheet2.xlsx", create_excel_file(unique_sheet2))
        zip_file.writestr("common.xlsx", create_excel_file(common))
    return zip_buffer.getvalue()

def main():
    st.title("CSV Comparison App")

    st.write("Upload two CSV files and specify the column name to compare.")

    file1 = st.file_uploader("Upload first CSV file", type="csv")
    file2 = st.file_uploader("Upload second CSV file", type="csv")
    column_name = st.text_input("Enter the column name to compare")

    if file1 is not None and file2 is not None and column_name:
        is_valid, message = validate_column_name(file1, file2, column_name)
        if not is_valid:
            st.error(message)
        else:
            if st.button("Process Files and Download Results"):
                unique_sheet1, unique_sheet2, common = process_csv_files(file1, file2, column_name)

                if unique_sheet1 is not None and unique_sheet2 is not None and common is not None:
                    st.success("Files processed successfully!")

                    zip_file = create_zip_file(unique_sheet1, unique_sheet2, common)

                    st.download_button(
                        label="Download All Results (ZIP)",
                        data=zip_file,
                        file_name="excel_comparison_results.zip",
                        mime="application/zip"
                    )

if __name__ == "__main__":
    main()
