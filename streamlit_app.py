import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Global variables
DATE_COLUMNS = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']
NUMERIC_COLUMNS = ['Estimated Hours', 'Total Hours Estimate', 'Number of Delays']

def load_data(file):
    df = pd.read_csv(file)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    df['Duration'] = (df['Due Date'] - df['Start Date']).dt.days
    df['Completion_Status'] = df.apply(lambda row: 'Completed' if pd.notnull(row['Completed At']) else 'In Progress' if row['Overdue'] != True else 'Overdue', axis=1)
    return df

def filter_data(df):
    st.sidebar.header("Filters")
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['Start Date'].min().date(), df['Due Date'].max().date()),
        min_value=df['Start Date'].min().date(),
        max_value=df['Due Date'].max().date()
    )

    assignees = df['Assignee'].dropna().unique().tolist()
    selected_assignees = st.sidebar.multiselect("Select Assignees", options=assignees, default=assignees)

    projects = df['Projects'].dropna().unique().tolist()
    selected_projects = st.sidebar.multiselect("Select Projects", options=projects, default=projects)

    statuses = df['Deliverable Status'].dropna().unique().tolist()
    selected_statuses = st.sidebar.multiselect("Select Deliverable Statuses", options=statuses, default=statuses)

    filtered_df = df[
        (df['Start Date'].dt.date >= date_range[0]) &
        (df['Due Date'].dt.date <= date_range[1]) &
        (df['Assignee'].isin(selected_assignees)) &
        (df['Projects'].isin(selected_projects)) &
        (df['Deliverable Status'].isin(selected_statuses))
    ]

    return filtered_df

def project_overview(df):
    st.title("Project Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", len(df))
    col2.metric("Completed Tasks", len(df[df['Completion_Status'] == 'Completed']))
    col3.metric("Overdue Tasks", len(df[df['Completion_Status'] == 'Overdue']))
    col4.metric("Total Estimated Hours", f"{df['Estimated Hours'].sum():.2f}")

    # Project Timeline
    fig = px.timeline(df, x_start="Start Date", x_end="Due Date", y="Projects", color="Completion_Status",
                      hover_name="Name", title="Project Timeline")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    # Task Status Distribution
    status_counts = df['Completion_Status'].value_counts()
    fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title="Task Status Distribution")
    st.plotly_chart(fig, use_container_width=True)

def resource_allocation(df):
    st.title("Resource Allocation")

    # Workload by Assignee
    fig = px.bar(df.groupby('Assignee')['Estimated Hours'].sum().reset_index(), 
                 x='Assignee', y='Estimated Hours', title="Workload by Assignee")
    st.plotly_chart(fig, use_container_width=True)

    # Task Distribution by Assignee
    fig = px.bar(df.groupby(['Assignee', 'Completion_Status']).size().unstack(fill_value=0), 
                 title="Task Distribution by Assignee", barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

def task_analysis(df):
    st.title("Task Analysis")

    # Task Duration vs Estimated Hours
    fig = px.scatter(df, x="Duration", y="Estimated Hours", color="Completion_Status", 
                     hover_name="Name", title="Task Duration vs Estimated Hours")
    st.plotly_chart(fig, use_container_width=True)

    # Top 10 Time-Consuming Tasks
    top_tasks = df.nlargest(10, 'Estimated Hours')
    fig = px.bar(top_tasks, x='Name', y='Estimated Hours', title="Top 10 Time-Consuming Tasks")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

def delay_analysis(df):
    st.title("Delay Analysis")

    # Number of Delays by Project
    fig = px.bar(df.groupby('Projects')['Number of Delays'].mean().reset_index(), 
                 x='Projects', y='Number of Delays', title="Average Number of Delays by Project")
    st.plotly_chart(fig, use_container_width=True)

    # Delay Rationale Distribution
    delay_rationale = df['Delay Rationale'].value_counts()
    fig = px.pie(delay_rationale, values=delay_rationale.values, names=delay_rationale.index, 
                 title="Delay Rationale Distribution")
    st.plotly_chart(fig, use_container_width=True)

def custom_view(df):
    st.title("Custom View")

    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Scatter Plot", "Line Chart"])
    x_axis = st.selectbox("Select X-axis", df.columns)
    y_axis = st.selectbox("Select Y-axis", NUMERIC_COLUMNS)
    color_by = st.selectbox("Color by", ['None'] + df.columns.tolist())

    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x_axis, y=y_axis, color=color_by if color_by != 'None' else None)
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_axis, y=y_axis, color=color_by if color_by != 'None' else None)
    else:  # Line Chart
        fig = px.line(df, x=x_axis, y=y_axis, color=color_by if color_by != 'None' else None)

    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(layout="wide", page_title="Comprehensive PM Dashboard")
    
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        filtered_df = filter_data(df)
        
        page = st.sidebar.selectbox("Select a View", ["Project Overview", "Resource Allocation", "Task Analysis", "Delay Analysis", "Custom View"])
        
        if page == "Project Overview":
            project_overview(filtered_df)
        elif page == "Resource Allocation":
            resource_allocation(filtered_df)
        elif page == "Task Analysis":
            task_analysis(filtered_df)
        elif page == "Delay Analysis":
            delay_analysis(filtered_df)
        elif page == "Custom View":
            custom_view(filtered_df)

if __name__ == "__main__":
    main()
