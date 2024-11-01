import streamlit as st

# Display README file content
try:
    with open('README.md', 'r') as f:
        readme_content = f.read()
    st.markdown(readme_content)
except FileNotFoundError:
    st.error("README.md file not found.")

# Subheader for the app functionality
st.subheader("Process File")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel or text file with URLs", type=["xlsx", "txt"])

# Input for HTML tags
tags = st.text_input("Enter HTML tags to extract (comma-separated)", "title,meta,header,p")

# Select output format
output_format = st.selectbox("Select output format", ["CSV", "JSON"])

# Button to start extraction
if st.button("Start Extraction"):
    if uploaded_file:
        st.success("File uploaded successfully.")
    else:
        st.error("Please upload a file.")
