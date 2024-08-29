import streamlit as st
import csv
import re
import io
import zipfile

def filter_alphanumeric(value):
    return bool(re.match('^[a-zA-Z0-9]+$', str(value)))

def get_csv_headers(file):
    content = io.StringIO(file.getvalue().decode("utf-8"))
    reader = csv.reader(content)
    return next(reader, [])

def validate_column_name(file1, file2, column_name):
    headers1 = get_csv_headers(file1)
    headers2 = get_csv_headers(file2)
    
    if column_name not in headers1 and column_name not in headers2:
        return False, "The specified column name is not present in either file."
    elif column_name not in headers1:
        return False, f"The specified column name is not present in the first file. Available columns: {', '.join(headers1)}"
    elif column_name not in headers2:
        return False, f"The specified column name is not present in the second file. Available columns: {', '.join(headers2)}"
    return True, ""

def process_csv_files(file1, file2, column_name):
    def read_csv(file):
        content = io.StringIO(file.getvalue().decode("utf-8"))
        reader = csv.DictReader(content)
        return [row for row in reader if filter_alphanumeric(row.get(column_name, ''))]

    sheet1 = read_csv(file1)
    sheet2 = read_csv(file2)

    values1 = set(row[column_name] for row in sheet1)
    values2 = set(row[column_name] for row in sheet2)

    unique_sheet1 = [row for row in sheet1 if row[column_name] not in values2]
    unique_sheet2 = [row for row in sheet2 if row[column_name] not in values1]
    common = [row for row in sheet1 if row[column_name] in values2]

    return unique_sheet1, unique_sheet2, common

def write_csv(data):
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return output.getvalue()

def create_zip_file(unique_sheet1, unique_sheet2, common):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("unique_sheet1.csv", write_csv(unique_sheet1))
        zip_file.writestr("unique_sheet2.csv", write_csv(unique_sheet2))
        zip_file.writestr("common.csv", write_csv(common))
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
