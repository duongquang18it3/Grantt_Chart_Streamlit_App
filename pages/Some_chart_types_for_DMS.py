import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Create mock data and save to CSV
data = {
    'Document_ID': [1, 2, 3, 4, 5],
    'Type': ['PDF', 'DOCX', 'Image', 'PDF', 'DOCX'],
    'Cabinet': ['Finance', 'Legal', 'Marketing', 'Finance', 'Legal'],
    'Tag': ['Confidential', 'Public', 'Internal', 'Confidential', 'Public'],
    'Workflow_State': ['Draft', 'Review', 'Approved', 'Review', 'Draft'],
    'Creation_Date': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05']
}

df = pd.DataFrame(data)
df['Creation_Date'] = pd.to_datetime(df['Creation_Date'])
df.to_csv('dms_data.csv', index=False)

# Load data
df = pd.read_csv('dms_data.csv')
df['Creation_Date'] = pd.to_datetime(df['Creation_Date'])

# Display the dataset
st.write("Document Management System Data Overview", df)

# Prepare data for the "Number of Documents by Type" chart
type_counts = df['Type'].value_counts().reset_index()
type_counts.columns = ['Type', 'Count']

# Chart 1: Number of Documents by Type
fig1 = px.bar(type_counts, x='Type', y='Count', title="Number of Documents by Type")
st.plotly_chart(fig1)

# Chart 2: Documents in Different Cabinets
fig2 = px.treemap(df, path=['Cabinet', 'Type'], title="Documents in Different Cabinets")
st.plotly_chart(fig2)

# Chart 3: Documents by Workflow States
state_counts = df['Workflow_State'].value_counts().reset_index()
state_counts.columns = ['Workflow_State', 'Count']
fig3 = px.funnel(state_counts, x='Count', y='Workflow_State', title="Documents by Workflow States")
st.plotly_chart(fig3)

# Chart 4: Documents by Index (Here using Tag as a proxy for index)
fig4 = px.histogram(df, x='Tag', title="Documents by Tag")
st.plotly_chart(fig4)

df['Month'] = df['Creation_Date'].dt.strftime('%Y-%m')

# Group data by 'Month' and count the number of documents per month
monthly_counts = df.groupby('Month').size().reset_index(name='Counts')

# Create a line chart to display document growth over time
fig = px.line(monthly_counts, x='Month', y='Counts', title='Document Growth Over Time', markers=True)

# Adjust marker size: 'marker=dict(size=15)' changes the marker size to 15
fig.update_traces(marker=dict(size=50))

# Display the chart
st.plotly_chart(fig)


