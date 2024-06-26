import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
# Define paths to datasets
current_dir = os.getcwd()
dataset_dir = os.path.join(current_dir, "dataset")
supermarket_sales_path = os.path.join(dataset_dir, "supermarket_sales.csv")
ai_keywords_path = os.path.join(dataset_dir, "AI_Invoice_Keywords_Occurrences.csv")

# Sidebar to select the dataset
dataset_options = {
    'Supermarket Sales': supermarket_sales_path,
    'AI Invoice Keywords': ai_keywords_path
}
selected_dataset = st.sidebar.selectbox('Select Dataset:', list(dataset_options.keys()))

# Load the selected dataset
df = pd.read_csv(dataset_options[selected_dataset])
def calculate_sizeref(data_size, desired_max_bubble_area=60**2, max_data_points=100):
    """
    Adjust the bubble sizes based on the count of displayed data points to ensure
    the bubbles grow larger as fewer points are displayed.
    """
    base_sizeref = 3 * max(data_size) / (desired_max_bubble_area)  # Base reference for max bubble size
    
    current_data_points = len(data_size)
    scaling_factor = max_data_points / max(current_data_points, 1)  # Prevent division by zero
    adjusted_sizeref = base_sizeref / scaling_factor  # Inverse relationship
    
    return adjusted_sizeref

# Configure options and process data based on the selected dataset
if selected_dataset == 'Supermarket Sales':
    analysis_options = (
        'View Data Table',
        'Total Revenue by Product Line', 
        'Product Consumption by Gender', 
        'Customers per City', 
        'Gross Income per Product Line', 
        'Total Bill per Product Line'
    )

    total_sales = df.groupby('Product line')['Total'].sum().reset_index()
    sales_by_gender = df.groupby(['Product line', 'Gender'])['Quantity'].sum().reset_index()
    customers_per_city = df.groupby('City')['Customer type'].count().reset_index().rename(columns={'Customer type': 'Number of Customers'})
    gross_income_by_product = df.groupby('Product line')['gross income'].sum().reset_index()

elif selected_dataset == 'AI Invoice Keywords':
    analysis_options = (
        'View Data Table',
        'Occurrences Bubble Chart',
        'Top 10 Keywords by Occurrence'  # New option added
    )
    # No extra processing needed for this simple dataset

# Sidebar to choose the analysis type
analysis_type = st.sidebar.selectbox('Choose the Chart Type:', analysis_options)

# Conditional rendering based on selected analysis type
if analysis_type == 'View Data Table':
    st.subheader(f'{selected_dataset} Data Table')

    # Column selection and filtering
    columns = df.columns.tolist()
    column_to_filter = st.sidebar.selectbox('Select Column to Filter', ['None'] + columns)

    if column_to_filter != 'None':
        unique_values = df[column_to_filter].dropna().unique()
        selected_value = st.sidebar.selectbox(f'Select Value for {column_to_filter}', unique_values)
        df = df[df[column_to_filter] == selected_value]

    # Sorting
    sort_by = st.sidebar.selectbox('Sort by', ['None'] + columns)
    if sort_by != 'None':
        sort_order = st.sidebar.radio('Sort Order', ['Ascending', 'Descending'])
        df = df.sort_values(by=sort_by, ascending=(sort_order == 'Ascending'))

    st.write(df)

elif analysis_type == 'Occurrences Bubble Chart':
    # Get the global minimum and maximum occurrences to set the bounds for input fields
    global_min_occurrences, global_max_occurrences = df['Occurrences'].min(), df['Occurrences'].max()

    # Create two numeric input boxes for minimum and maximum occurrences
    min_occurrences = st.sidebar.number_input('Minimum Occurrences', min_value=int(global_min_occurrences), 
                                              max_value=int(global_max_occurrences), value=int(global_min_occurrences))
    max_occurrences = st.sidebar.number_input('Maximum Occurrences', min_value=int(global_min_occurrences), 
                                              max_value=int(global_max_occurrences), value=int(global_max_occurrences))

    # Filter the DataFrame based on the input range
    filtered_df = df[(df['Occurrences'] >= min_occurrences) & (df['Occurrences'] <= max_occurrences)]
    if not filtered_df.empty:
        sizeref = calculate_sizeref(filtered_df['Occurrences'].tolist(), desired_max_bubble_area=60**2, max_data_points=len(df))
        
        fig = go.Figure(data=[go.Scatter(
            x=filtered_df['Keyword'],
            y=filtered_df['Occurrences'],
            mode='markers',
            marker=dict(
                size=filtered_df['Occurrences'],
                color=filtered_df['Occurrences'],  # Apply color scale based on occurrences
                sizemode='area',
                sizeref=sizeref,
                sizemin=4,
                showscale=True
            ),
            text=filtered_df['Keyword']
        )])
        fig.update_layout(title='Occurrences of AI Keywords by Input Range',
                          xaxis_title='Keyword',
                          yaxis_title='Occurrences',
                          coloraxis=dict(colorscale='Viridis'),
                          hovermode='closest')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No data falls within the selected range. Please adjust the input values.")


elif analysis_type == 'Top 10 Keywords by Occurrence':
    top_keywords = df.nlargest(10, 'Occurrences')
    sizeref = calculate_sizeref(top_keywords['Occurrences'].tolist(), desired_max_bubble_area=60**2, max_data_points=10)

    fig = go.Figure(data=[go.Scatter(
        x=top_keywords['Keyword'],
        y=top_keywords['Occurrences'],
        mode='markers',
        marker=dict(
            size=top_keywords['Occurrences'],
            color=top_keywords['Occurrences'],
            sizemode='area',
            sizeref=sizeref,
            sizemin=4,
            showscale=True
        ),
        text=top_keywords['Keyword']  # Display keyword on hover
    )])
    fig.update_layout(
        title='Top 10 AI Keywords by Occurrence',
        xaxis_title='Keyword',
        yaxis_title='Occurrences',
        coloraxis=dict(colorscale='Viridis'),
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == 'Total Revenue by Product Line':
    fig = px.scatter(total_sales, x='Product line', y='Total', size='Total', color='Product line', hover_name='Product line', size_max=60, title="Total Revenue by Product Line")
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == 'Product Consumption by Gender':
    fig = px.scatter(sales_by_gender, x='Product line', y='Quantity', size='Quantity', color='Gender', facet_col='Gender', hover_name='Product line', size_max=60, title="Product Consumption by Gender")
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == 'Customers per City':
    fig = px.scatter(customers_per_city, x='City', y='Number of Customers', size='Number of Customers', color='City', hover_name='City', size_max=60, title="Customers per City")
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == 'Gross Income per Product Line':
    fig = px.scatter(gross_income_by_product, x='Product line', y='gross income', size='gross income', color='Product line', hover_name='Product line', size_max=60, title="Gross Income per Product Line")
    st.plotly_chart(fig, use_container_width=True)

elif analysis_type == 'Total Bill per Product Line':
    fig = px.scatter(total_sales, x='Product line', y='Total', size='Total', color='Product line', hover_name='Product line', size_max=60, title="Total Bill in Each Product Line")
    st.plotly_chart(fig, use_container_width=True)
