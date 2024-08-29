import streamlit as st
import csv
import re
import io

def filter_alphanumeric(value):
    return bool(re.match('^[a-zA-Z0-9]+$', str(value)))

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

def main():
    st.title("CSV Comparison App")

    st.write("Upload two CSV files and specify the column name to compare.")

    file1 = st.file_uploader("Upload first CSV file", type="csv")
    file2 = st.file_uploader("Upload second CSV file", type="csv")
    column_name = st.text_input("Enter the column name to compare")

    if file1 and file2 and column_name:
        if st.button("Process Files"):
            unique_sheet1, unique_sheet2, common = process_csv_files(file1, file2, column_name)

            st.write("Files processed successfully!")

            st.download_button(
                label="Download Unique Sheet 1",
                data=write_csv(unique_sheet1),
                file_name="unique_sheet1.csv",
                mime="text/csv"
            )

            st.download_button(
                label="Download Unique Sheet 2",
                data=write_csv(unique_sheet2),
                file_name="unique_sheet2.csv",
                mime="text/csv"
            )

            st.download_button(
                label="Download Common Values",
                data=write_csv(common),
                file_name="common.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()