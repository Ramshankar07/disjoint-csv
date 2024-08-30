import streamlit as st
import pandas as pd
import re
import io
import zipfile

def filter_alphanumeric(df, column_name):
    # Keep only rows where the column's value contains only alphanumeric characters
    df = df[df[column_name].apply(lambda x: bool(re.match('^[a-zA-Z0-9]+$', str(x))))]
    return df

def validate_column_name(file1, file2, column_name):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    if column_name not in df1.columns and column_name not in df2.columns:
        return False, f"The specified column name '{column_name}' is not present in either file. Available columns in first file: {', '.join(df1.columns)}\nAvailable columns in second file: {', '.join(df2.columns)}"
    elif column_name not in df1.columns:
        return False, f"The specified column name '{column_name}' is not present in the first file. Available columns: {', '.join(df1.columns)}"
    elif column_name not in df2.columns:
        return False, f"The specified column name '{column_name}' is not present in the second file. Available columns: {', '.join(df2.columns)}"
    return True, ""

def process_csv_files(file1, file2, column_name):
    # Load the two CSV files
    sheet1 = pd.read_csv(file1)
    sheet2 = pd.read_csv(file2)

    # Filter out rows that do not have alphanumeric values
    sheet1 = filter_alphanumeric(sheet1, column_name)
    sheet2 = filter_alphanumeric(sheet2, column_name)

    # Find unique values in each sheet
    unique_sheet1 = sheet1[~sheet1[column_name].isin(sheet2[column_name])]
    unique_sheet2 = sheet2[~sheet2[column_name].isin(sheet1[column_name])]

    # Find common values between both sheets
    common = pd.merge(sheet1, sheet2, on=column_name)

    return unique_sheet1, unique_sheet2, common

def create_zip_file(unique_sheet1, unique_sheet2, common):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("unique_sheet1.csv", unique_sheet1.to_csv(index=False))
        zip_file.writestr("unique_sheet2.csv", unique_sheet2.to_csv(index=False))
        zip_file.writestr("common.csv", common.to_csv(index=False))
    return zip_buffer.getvalue()

def main():
    st.title("CSV Comparison App")

    st.write("Upload two CSV files and specify the column name to compare.")

    file1 = st.file_uploader("Upload first CSV file", type="csv")
    file2 = st.file_uploader("Upload second CSV file", type="csv")
    column_name = st.text_input("Enter the column name to compare")

    if file1 and file2 and column_name:
        is_valid, message = validate_column_name(file1, file2, column_name)
        if not is_valid:
            st.error(message)
        else:
            if st.button("Process Files and Download Results"):
                unique_sheet1, unique_sheet2, common = process_csv_files(file1, file2, column_name)

                st.success("Files processed successfully!")

                zip_file = create_zip_file(unique_sheet1, unique_sheet2, common)

                st.download_button(
                    label="Download All Results (ZIP)",
                    data=zip_file,
                    file_name="csv_comparison_results.zip",
                    mime="application/zip"
                )

if __name__ == "__main__":
    main()
