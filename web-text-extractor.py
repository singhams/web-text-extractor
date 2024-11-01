import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to extract text from a URL
def extract_text(url, tags):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text based on specified tags
        extracted_text = []
        for tag in tags:
            elements = soup.find_all(tag)
            for element in elements:
                extracted_text.append(element.get_text().strip())

        return ' '.join(extracted_text)
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Display README file content
with open('README.md', 'r') as f:
    readme_content = f.read()
st.markdown(readme_content)

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
        # Read the file into a DataFrame
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, header=None, names=["URL"])

        urls = df['URL'].tolist()
        tags_list = [tag.strip() for tag in tags.split(',')]
        results = []

        # Progress bar
        progress_bar = st.progress(0)
        total_urls = len(urls)

        for i, url in enumerate(urls):
            text = extract_text(url, tags_list)
            results.append({'URL': url, 'Text': text})

            # Update progress bar
            progress_bar.progress((i + 1) / total_urls)

            # Allow stopping the app
            if st.button("Stop"):
                st.stop()

        # Convert results to DataFrame
        results_df = pd.DataFrame(results)

        # Display results
        st.write(results_df)

        # Provide download link
        if output_format == "CSV":
            results_df.to_csv('results.csv', index=False)
            st.download_button("Download CSV", data=open('results.csv', 'rb'), file_name='results.csv')
        else:
            results_df.to_json('results.json', orient='records')
            st.download_button("Download JSON", data=open('results.json', 'rb'), file_name='results.json')
    else:
        st.error("Please upload a file.")