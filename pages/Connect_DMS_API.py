import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from requests.auth import HTTPBasicAuth

# URLs for the data
urls = {
    "documents": "http://edms-demo.epik.live/api/v4/documents/",
    "cabinets": "http://edms-demo.epik.live/api/v4/cabinets/",
    "tags": "http://edms-demo.epik.live/api/v4/tags/",  # URL for tags
    "groups": "http://edms-demo.epik.live/api/v4/groups/",
    "metadata_types": "http://edms-demo.epik.live/api/v4/metadata_types/"
}

# Basic Authentication
auth = HTTPBasicAuth('admin', '1234@BCD')

# Function to fetch data from an API
def fetch_data(endpoint_url):
    response = requests.get(endpoint_url, auth=auth)
    if response.status_code == 200:
        return response.json()['results']
    else:
        st.error(f"Failed to fetch data from {endpoint_url}: Status {response.status_code}")
        return []

# Load data from APIs
df_documents = pd.DataFrame(fetch_data(urls['documents']))
df_cabinets = pd.DataFrame(fetch_data(urls['cabinets']))


# Helper function to fetch document count for each cabinet
# Extract document type and labels for visualization
if not df_documents.empty:
    df_documents['type_label'] = df_documents['document_type'].apply(lambda x: x.get('label') if isinstance(x, dict) else None)
    df_documents['type_id'] = df_documents['document_type'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)

    # Count the frequency of each document type label
    type_counts = df_documents['type_label'].value_counts().reset_index()
    type_counts.columns = ['type_label', 'count']

    st.header('Document Types')

    # Create a bubble chart
    fig_bubble = px.scatter(type_counts, x='type_label', y='count',
                            size='count', color='type_label',
                            hover_name='type_label', size_max=60,
                            title='Popularity of Document Types by Label')
    st.plotly_chart(fig_bubble)

    # Tạo DataFrame từ value_counts và reset index với tên cột cụ thể
    type_counts = df_documents['type_label'].value_counts().reset_index(name='count')
    type_counts.rename(columns={'index': 'type_label'}, inplace=True)

    
    fig_bar = px.bar(type_counts, x='type_label', y='count', color='type_label',
                 labels={'type_label': 'Document Type', 'count': 'Count'},
                 title='Bar Chart of Document Types', text='count')
    fig_bar.update_traces(texttemplate='%{text}', textposition='outside')  # Ajust text position if necessary
    st.plotly_chart(fig_bar)


    # Create a pie chart for document types based on 'label'
    fig_pie = px.pie(df_documents, names='type_label', 
                    title='Pie Chart of Document Types')
    st.plotly_chart(fig_pie)

    # Bar chart for file extention
    # Extracting file extension from mimetype
    df_documents['file_extension'] = df_documents['file_latest'].apply(lambda x: x['mimetype'].split('/')[-1].upper() if isinstance(x, dict) else None)

    # Count the frequency of each file extension
    extension_counts = df_documents['file_extension'].value_counts().reset_index()
    extension_counts.columns = ['File Extension', 'Count']

    # Create a Bar Chart
    fig_file_extension = px.bar(extension_counts, x='File Extension', y='Count', color='File Extension',
                            title='Document File Extensions', text='Count')
    fig_file_extension.update_traces(texttemplate='%{text}', textposition='outside')
    fig_file_extension.update_layout(bargap=0.5)
    st.plotly_chart(fig_file_extension)

def fetch_cabinet_documents(url):
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        data = response.json()
        return data['count']
    else:
        return 0  # Or handle error appropriately

# Prepare cabinet data with document counts
if not df_cabinets.empty:
    st.header('Cabinets')
    df_cabinets['documents_url'] = df_cabinets.apply(lambda x: x['documents_url'], axis=1)
    df_cabinets['document_count'] = df_cabinets['documents_url'].apply(fetch_cabinet_documents)

    # Configure columns
    
    df_cabinets['label_with_count'] = df_cabinets['label'] + ': ' + df_cabinets['document_count'].astype(str)
    

    
        # Treemap with document counts
    fig_cabinets = px.treemap(df_cabinets, path=['label_with_count'], values='document_count', title="Cabinet Document Distribution")
    
    st.plotly_chart(fig_cabinets)
        
# Function to fetch document count for each tag
def fetch_tag_documents(url):
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        data = response.json()
        return data['count']
    else:
        return 0  # Or handle errors appropriately

# Load data from APIs
df_tags = pd.DataFrame(fetch_data(urls['tags']))

if not df_tags.empty:
    st.header('Document Tags')
    # Add document count to each tag
    df_tags['document_count'] = df_tags['documents_url'].apply(fetch_tag_documents)
    df_tags['color'] = df_tags.apply(lambda x: x['color'], axis=1)

    # Bar Chart for Tags
    fig_tags = px.bar(df_tags, x='label', y='document_count', title="Documents by Tag",
                      color='color', text='document_count')
    fig_tags.update_layout(showlegend=False)  # Optional: Turn off the legend if color coding is sufficient
    st.plotly_chart(fig_tags)
