import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from requests.auth import HTTPBasicAuth
import numpy as np
st.set_page_config(layout="wide")
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def add_custom_css():
    # Đoạn CSS để tùy chỉnh màu nền của các cột
    st.markdown("""
        <style>
        .st-cj {
            background-color: #f0f2f6;
        }
        </style>
        """, unsafe_allow_html=True)

# Gọi hàm để thêm CSS
add_custom_css()

# URLs for the data
urls = {
    "documents": "http://edms-demo.epik.live/api/v4/documents/",
    "cabinets": "http://edms-demo.epik.live/api/v4/cabinets/",
    "tags": "http://edms-demo.epik.live/api/v4/tags/",
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
            endpoint_url = data['next']
        else:
            st.error(f"Failed to fetch data from {endpoint_url}: Status {response.status_code}")
            break
    return all_data

# Sidebar for selecting the view
option = st.sidebar.selectbox(
    "Select Dashboard View",
    ("Document Type", "Document Growth Over Time", "Cabinet Document Distribution", "Document Tags", "Document Count by Index and Node Value")
)

# Main dashboard layout based on sidebar selection
# Depending on the option, display appropriate visuals
if option == "Document Type":
    st.header('Document Types')
    df_documents = pd.DataFrame(fetch_data(urls['documents']))
    if not df_documents.empty:
        # Document Type Charts
        # [Include your visualization code for Document Types here]
        col1, col2 = st.columns([6.5, 3.5])
        with col1:
            df_documents['type_label'] = df_documents['document_type'].apply(lambda x: x.get('label') if isinstance(x, dict) else None)
            type_counts = df_documents['type_label'].value_counts().reset_index()
            type_counts.columns = ['type_label', 'count']
            total_documents = type_counts['count'].sum()
            type_counts['percentage'] = (type_counts['count'] / total_documents) * 100

            # Layout with two columns
            col11, col22 = st.columns([3, 7])

            with col11:
               
                st.markdown("**Select Document Types Percentage Range**")
                min_percentage = st.number_input('Enter minimum percentage', min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                max_percentage = st.number_input('Enter maximum percentage', min_value=0.0, max_value=100.0, value=100.0, step=0.1)
            
            with col22:
                # Validate the range and plot the pie chart if valid
                if min_percentage < max_percentage:
                    filtered_data = type_counts[(type_counts['percentage'] >= min_percentage) & (type_counts['percentage'] <= max_percentage)]
                    fig_pie = px.pie(filtered_data, names='type_label', values='count',width=450,
                                    title=f'Pie Chart of Document Types from {min_percentage}% to {max_percentage}%')
                    st.plotly_chart(fig_pie)
                else:
                    st.error('Minimum percentage must be less than maximum percentage.')
        with col2:
            fig_bubble = px.scatter(type_counts, x='type_label', y='count',
                            size='count', color='type_label',
                            hover_name='type_label', size_max=60,width=400,
                            title='Popularity of Document Types by Label')
            st.plotly_chart(fig_bubble)

        col1, col2 = st.columns([6.5, 3.5])
        with col1:
            fig_bar = px.bar(type_counts, x='count', y='type_label', color='type_label',
                     labels={'type_label': 'Document Type', 'count': 'Count'},
                     title='Bar Chart of Document Types', text='count')
            fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_bar)
        with col2:
            df_documents['file_extension'] = df_documents['file_latest'].apply(lambda x: x['mimetype'].split('/')[-1].upper() if isinstance(x, dict) else None)

            # Count the frequency of each file extension
            extension_counts = df_documents['file_extension'].value_counts().reset_index()
            extension_counts.columns = ['File Extension', 'Count']

            # Create a Bar Chart
            fig_file_extension = px.bar(extension_counts, x='File Extension', y='Count', color='File Extension',
                                    title='Document File Extensions', width=400,text='Count')
            fig_file_extension.update_traces(texttemplate='%{text}', textposition='outside')
            fig_file_extension.update_layout(bargap=0.5)
            st.plotly_chart(fig_file_extension)

elif option == "Document Growth Over Time":
    st.header('Document Growth Over Time')
    df_documents = pd.DataFrame(fetch_data(urls['documents']))
    if not df_documents.empty:
            #Document Growth Over Time:
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
            # Document Growth Charts
            # [Include your visualization code for Document Growth Over Time here]

elif option == "Cabinet Document Distribution":
    st.header('Cabinets')
    df_cabinets = pd.DataFrame(fetch_data(urls['cabinets']))
    if not df_cabinets.empty:
        def fetch_data(endpoint_url):
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

        # Function to fetch direct document count for a cabinet
        def fetch_direct_document_count(documents_url):
            response = requests.get(documents_url, auth=auth)
            if response.status_code == 200:
                documents = response.json()
                return documents['count']
            else:
                st.error(f"Failed to fetch documents from {documents_url}: Status {response.status_code}")
                return 0

        # Load data from APIs
        df_cabinets = pd.DataFrame(fetch_data(urls['cabinets']))

        # Prepare cabinet data with direct document counts
        if not df_cabinets.empty:
            
            cabinet_data = []
            for index, row in df_cabinets.iterrows():
                document_count = fetch_direct_document_count(row['documents_url'])  # Fetch direct documents only
                full_path = row['full_path'].split(' / ')
                if len(full_path) > 1:
                    parent_name = full_path[-2]  # Gets the second last element as parent for children
                else:
                    parent_name = "All Cabinets"  # Default parent for top-level cabinets

                cabinet_data.append({
                    'parent': parent_name,
                    'label': row['label'],
                    'document_count': document_count
                })

            df_cabinet_documents = pd.DataFrame(cabinet_data)

            # Treemap with document counts
            fig_cabinets = px.treemap(df_cabinet_documents, path=[px.Constant("All Cabinets"), 'parent', 'label'], values='document_count',
                                    title="Cabinet Document Distribution", hover_data={'label': True, 'document_count': True})
            st.plotly_chart(fig_cabinets)
        # Cabinet Document Distribution Charts
        # [Include your Treemap visualization here]

elif option == "Document Tags":
    st.header('Document Tags')
    df_tags = pd.DataFrame(fetch_data(urls['tags']))
    if not df_tags.empty:
        # Document Tags Charts
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
            
            # Add document count to each tag
            df_tags['document_count'] = df_tags['documents_url'].apply(fetch_tag_documents)
            df_tags['color'] = df_tags.apply(lambda x: x['color'], axis=1)

            # Bar Chart for Tags
            fig_tags = px.bar(df_tags, x='label', y='document_count', title="Documents by Tag",
                            color='color', text='document_count')
            fig_tags.update_layout(showlegend=False)  # Optional: Turn off the legend if color coding is sufficient
            st.plotly_chart(fig_tags)
        # [Include your Tags Bar Chart visualization here]
        

elif option == "Document Count by Index and Node Value":
    st.header('Document Count by Index and Node Value')
    # Fetch index data and process each index
    # [Include your Stacked Bar Chart visualization here]
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
    
    fig = px.bar(df_node_counts, x='Index Label', y='Document Count', color='Node Value', text='Document Count', barmode='stack')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig)
