import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from requests.auth import HTTPBasicAuth

# URLs for the data
urls = {
    "documents": "http://edms-demo.epik.live/api/v4/documents/",
    "cabinets": "http://edms-demo.epik.live/api/v4/cabinets/",
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
df_groups = pd.DataFrame(fetch_data(urls['groups']))
df_metadata_types = pd.DataFrame(fetch_data(urls['metadata_types']))

# Extract document type and labels for visualization
if not df_documents.empty:
    df_documents['type_label'] = df_documents['document_type'].apply(lambda x: x.get('label') if isinstance(x, dict) else None)
    df_documents['type_id'] = df_documents['document_type'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)

    # Count the frequency of each document type label
    type_counts = df_documents['type_label'].value_counts().reset_index()
    type_counts.columns = ['type_label', 'count']

    # Create a bubble chart
    fig_bubble = px.scatter(type_counts, x='type_label', y='count',
                            size='count', color='type_label',
                            hover_name='type_label', size_max=60,
                            title='Popularity of Document Types by Label')
    st.plotly_chart(fig_bubble)

# Visualization: Tree Map for Cabinet Labels
fig_cabinets = px.treemap(df_cabinets, path=['label'], title="Cabinet Labels Distribution")
st.plotly_chart(fig_cabinets)

# Visualization: Bar Chart for Documents by Group
# Assuming we have the counts of documents per group available
# For demonstration, using dummy count of 1 for each group
fig_groups = px.bar(df_groups, x='name', y=[1]*len(df_groups), title="Documents by Group")
st.plotly_chart(fig_groups)

# Visualization: Bar Chart for Metadata Types Count
fig_metadata = px.bar(df_metadata_types, x='name', y=[1]*len(df_metadata_types), title="Metadata Types Count")
st.plotly_chart(fig_metadata)

# Display data tables
st.text('Documents Table')
st.dataframe(df_documents[['id', 'label', 'type_label', 'language']])
st.text('Cabinets Table')
st.dataframe(df_cabinets[['id', 'label']])
st.text('Groups Table')
st.dataframe(df_groups[['id', 'name']])
st.text('Metadata Types Table')
st.dataframe(df_metadata_types[['id', 'name']])
