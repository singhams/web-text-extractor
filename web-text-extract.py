import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# Display the contents of the README.md file
def display_readme():
    try:
        with open("README.md", "r") as f:
            readme_content = f.read()
        st.markdown(readme_content)
    except FileNotFoundError:
        st.error("README.md file not found.")

display_readme()

# Function to extract text from a URL
def extract_text(url, tags, meta_tags):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text based on specified tags
        extracted_text = {}
        for tag in tags:
            if tag == 'title':
                # Extract title from meta tags if not found in HTML
                title = soup.title.string.strip() if soup.title else ''
                if not title:
                    title_meta = soup.find('meta', attrs={'name': 'title'})
                    title = title_meta['content'].strip() if title_meta else ''
                extracted_text['title'] = title
            else:
                elements = soup.select(f"main {tag}, article {tag}, section {tag}")
                text = ' '.join(element.get_text().strip() for element in elements)
                text = ' '.join(text.split())  # Remove extra whitespace and line breaks
                extracted_text[tag] = text

        # Extract specific meta tags
        for meta_tag in meta_tags:
            name, attr = meta_tag.split('=')
            element = soup.find('meta', attrs={name: attr.strip('"')})
            text = element['content'].strip() if element else ''
            text = ' '.join(text.split())  # Remove extra whitespace and line breaks
            extracted_text[meta_tag] = text

        return extracted_text
    except requests.exceptions.RequestException as e:
        return {tag: f"Error: {str(e)}" for tag in tags + meta_tags}

# Subheader for the app functionality
st.subheader("Process File")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel or text file with URLs", type=["xlsx", "txt"])

# Input for column name containing URLs
url_column = st.text_input("Enter the column name containing URLs", "URL")

# Input for HTML tags
tags = st.text_input("Enter HTML tags to extract (comma-separated)", "title,h1,h2,h3,p")

# Input for specific meta tags
meta_tags = st.text_input('Enter specific meta tags to extract (e.g., name="description", name="keywords")', 'name="description"')

# Select output format
output_format = st.selectbox("Select output format", ["CSV", "Excel", "JSON"])

# Placeholder for status messages
status_placeholder = st.empty()

# Button to start extraction
if st.button("Start Extraction", key="start_extraction"):
    if uploaded_file:
        # Read the file into a DataFrame
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file, header=None, names=[url_column])

        if url_column not in df.columns:
            st.error(f"Column '{url_column}' not found in the uploaded file.")
        else:
            urls = df[url_column].tolist()
            tags_list = [tag.strip() for tag in tags.split(',')]
            meta_tags_list = [meta_tag.strip() for meta_tag in meta_tags.split(',')]
            results = []

            # Progress bar
            progress_bar = st.progress(0)
            total_urls = len(urls)

            # Stop button
            stop_button = st.button("Stop", key="stop_button")

            for i, url in enumerate(urls):
                if stop_button:
                    status_placeholder.warning("Batch processing stopped.")
                    st.stop()

                status_placeholder.info(f"Processing batch {i + 1} of {total_urls}...")
                extracted_text = extract_text(url, tags_list, meta_tags_list)
                result = {'URL': url}
                result.update(extracted_text)
                results.append(result)

                # Update progress bar
                progress_bar.progress((i + 1) / total_urls)

            status_placeholder.success("Batch processing complete.")

            # Convert results to DataFrame
            results_df = pd.DataFrame(results)

            # Display results
            st.write(results_df)

            # Provide download link
            if output_format == "CSV":
                results_df.to_csv('results.csv', index=False)
                st.download_button("Download CSV", data=open('results.csv', 'rb'), file_name='results.csv', key="download_csv")
            elif output_format == "Excel":
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    results_df.to_excel(writer, index=False, sheet_name='Sheet1')
                st.download_button("Download Excel", data=output.getvalue(), file_name='results.xlsx', key="download_excel")
            else:
                results_df.to_json('results.json', orient='records')
                st.download_button("Download JSON", data=open('results.json', 'rb'), file_name='results.json', key="download_json")
    else:
        st.error("Please upload a file.")
