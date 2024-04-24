import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from requests.auth import HTTPBasicAuth
import numpy as np
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
    all_data = []
    while endpoint_url:
        response = requests.get(endpoint_url, auth=auth)
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data['results'])
            endpoint_url = data['next']  # Update the URL to the next page URL
        else:
            st.error(f"Failed to fetch data from {endpoint_url}: Status {response.status_code}")
            break
    return all_data

# Load data from APIs
df_documents = pd.DataFrame(fetch_data(urls['documents']))
df_cabinets = pd.DataFrame(fetch_data(urls['cabinets']))


# Helper function to fetch document count for each cabinet
# Extract document type and labels for visualization
if not df_documents.empty:
    st.header('Document Types') 
    df_documents['type_label'] = df_documents['document_type'].apply(lambda x: x.get('label') if isinstance(x, dict) else None)
    type_counts = df_documents['type_label'].value_counts().reset_index()
    type_counts.columns = ['type_label', 'count']
    total_documents = type_counts['count'].sum()
    type_counts['percentage'] = (type_counts['count'] / total_documents) * 100

    # Layout with two columns
    col1, col2 = st.columns([3, 7])

    with col1:
        st.markdown("**Select Document Types Percentage Range**")
        min_percentage = st.number_input('Enter minimum percentage', min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        max_percentage = st.number_input('Enter maximum percentage', min_value=0.0, max_value=100.0, value=100.0, step=0.1)
    
    with col2:
        # Validate the range and plot the pie chart if valid
        if min_percentage < max_percentage:
            filtered_data = type_counts[(type_counts['percentage'] >= min_percentage) & (type_counts['percentage'] <= max_percentage)]
            fig_pie = px.pie(filtered_data, names='type_label', values='count',width=450,
                             title=f'Pie Chart of Document Types from {min_percentage}% to {max_percentage}%')
            st.plotly_chart(fig_pie)
        else:
            st.error('Minimum percentage must be less than maximum percentage.')

    # Additional charts
    
    fig_bubble = px.scatter(type_counts, x='type_label', y='count',
                            size='count', color='type_label',
                            hover_name='type_label', size_max=60,
                            title='Popularity of Document Types by Label')
    st.plotly_chart(fig_bubble)
    
    fig_bar = px.bar(type_counts, x='type_label', y='count', color='type_label',
                     labels={'type_label': 'Document Type', 'count': 'Count'},
                     title='Bar Chart of Document Types', text='count')
    fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig_bar)

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


    #Document Growth Over Time:
    st.header('Document Growth Over Time')
    # Convert datetime_created to datetime and extract date part
    df_documents['date'] = pd.to_datetime(df_documents['datetime_created']).dt.date
    df_documents['document_type'] = df_documents['document_type'].apply(lambda x: x['label'])
    df_documents['file_extension'] = df_documents['file_latest'].apply(lambda x: x['mimetype'].split('/')[-1].upper())

    # Group by date and count by document type or file extension
    def prepare_data(group_field):
        df_grouped = df_documents.groupby(['date', group_field]).size().reset_index(name='count')
        return df_grouped.pivot(index='date', columns=group_field, values='count').fillna(0).cumsum().reset_index()

    # User selection for data view
    option = st.selectbox('Choose Data View', ['Document Types Growth Over Time', 'File Extension Growth Over Time'])

    if option == 'Document Types Growth Over Time':
        df_plot = prepare_data('document_type')
        title = "Document Type Growth Over Time"
    else:
        df_plot = prepare_data('file_extension')
        title = "File Extension Growth Over Time"

    # Plotting the data
    fig = px.line(df_plot, x='date', y=[col for col in df_plot.columns if col != 'date'],
                labels={'value': 'Number of Documents', 'date': 'Date'},
                title=title)
    fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Document Count', legend_title=option[:-16])
    st.plotly_chart(fig)



# Function to fetch data from an API
def fetch_data(endpoint_url):
    all_data = []
    while endpoint_url:
        response = requests.get(endpoint_url, auth=auth)
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data['results'])
            endpoint_url = data['next']  # Update the URL to the next page URL
        else:
            st.error(f"Failed to fetch data from {endpoint_url}: Status {response.status_code}")
            break
    return all_data

# Recursive function to fetch document count for each cabinet and its children
def fetch_cabinet_documents_recursive(cabinet):
    document_count = 0
    # Fetch documents for the current cabinet
    if cabinet['documents_url']:
        documents_data = requests.get(cabinet['documents_url'], auth=auth)
        if documents_data.status_code == 200:
            documents = documents_data.json()
            document_count += documents['count']
    
    # Recursively fetch documents for children
    for child in cabinet.get('children', []):
        document_count += fetch_cabinet_documents_recursive(child)
    
    return document_count

# Load data from APIs
df_cabinets = pd.DataFrame(fetch_data(urls['cabinets']))

# Prepare cabinet data with document counts
if not df_cabinets.empty:
    st.header('Cabinets')
    cabinet_data = []
    for index, row in df_cabinets.iterrows():
        document_count = fetch_cabinet_documents_recursive(row)
        cabinet_data.append({
            'full_path': row['full_path'],
            'document_count': document_count
        })

    df_cabinet_documents = pd.DataFrame(cabinet_data)

    # Treemap with document counts
    fig_cabinets = px.treemap(df_cabinet_documents, path=[px.Constant("All Cabinets"), 'full_path'], values='document_count', title="Cabinet Document Distribution")
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


#Build chart for Document by indexes

index_url = "https://edms-demo.epik.live/api/v4/index_instances/"
auth = HTTPBasicAuth('admin', '1234@BCD')

# Function to fetch all data from an API
def fetch_all_data(endpoint_url):
    all_data = []
    while endpoint_url:
        response = requests.get(endpoint_url, auth=auth)
        if response.status_code == 200:
            data = response.json()
            all_data.extend(data['results'])
            endpoint_url = data['next']
        else:
            st.error(f"Failed to fetch data from {endpoint_url}: Status {response.status_code}")
            break
    return all_data

# Recursive function to fetch documents for nodes and sub-nodes
def fetch_documents(node_url):
    nodes = fetch_all_data(node_url)
    node_documents = []
    for node in nodes:
        documents = fetch_all_data(node['documents_url'])
        document_count = len(documents)
        node_documents.append({
            'Node Value': node['value'],
            'Document Count': document_count
        })
        # Recursively fetch for child nodes
        if node.get('children_url'):
            node_documents.extend(fetch_documents(node['children_url']))
    return node_documents

# Fetch index data and process each index
node_counts = []
for index in fetch_all_data(index_url):
    node_documents = fetch_documents(index['nodes_url'])
    for node_doc in node_documents:
        node_counts.append({
            'Index Label': index['label'],
            'Node Value': node_doc['Node Value'],
            'Document Count': node_doc['Document Count']
        })

# Convert to DataFrame
df_node_counts = pd.DataFrame(node_counts)

# Create a stacked bar chart
st.header('Document Count by Index and Node Value')
fig = px.bar(df_node_counts, x='Index Label', y='Document Count', color='Node Value', text='Document Count', barmode='stack')
fig.update_traces(texttemplate='%{text}', textposition='outside')
st.plotly_chart(fig)

#Document Growth Over Time:


