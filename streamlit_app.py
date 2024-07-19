import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Global variables
DATE_COLUMNS = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']
NUMERIC_COLUMNS = ['Estimated Hours', 'Total Hours Estimate', 'Number of Delays', 'Harvest Hours']

@st.cache_data
def load_and_process_data(file):
    df = pd.read_csv(file)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df['Duration'] = (df['Due Date'] - df['Start Date']).dt.days
    df['Completion_Status'] = df.apply(lambda row: 'Completed' if pd.notnull(row['Completed At']) 
                                       else 'Overdue' if row.get('Overdue') == True 
                                       else 'In Progress', axis=1)
    
    # Ensure all necessary columns exist, if not, create with default values
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

@st.cache_data
def create_interactive_gantt(df, selected_assignees, selected_projects, selected_statuses):
    filtered_df = df[
        (df['Assignee'].isin(selected_assignees)) &
        (df['Projects'].isin(selected_projects)) &
        (df['Deliverable Status'].isin(selected_statuses))
    ]
    
    fig = px.timeline(filtered_df, x_start="Start Date", x_end="Due Date", y="Name", color="Assignee",
                      hover_data=["Task ID", "Projects", "Estimated Hours", "Deliverable Status"],
                      title="Interactive Project Timeline")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=600, xaxis_title="Date", yaxis_title="Task Name")
    
    # Add range slider
    fig.update_xaxes(rangeslider_visible=True)

    # Add buttons for time range selection
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=list([
                    dict(label="All",
                         method="relayout",
                         args=[{"xaxis.range": [filtered_df['Start Date'].min(), filtered_df['Due Date'].max()]}]),
                    dict(label="Next Month",
                         method="relayout",
                         args=[{"xaxis.range": [datetime.now(), datetime.now() + timedelta(days=30)]}]),
                    dict(label="Next Week",
                         method="relayout",
                         args=[{"xaxis.range": [datetime.now(), datetime.now() + timedelta(days=7)]}]),
                ]),
            )
        ]
    )

    return fig

@st.cache_data
def create_task_status_distribution(df):
    status_counts = df['Completion_Status'].value_counts()
    fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index, 
                 title="Task Status Distribution")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

@st.cache_data
def create_workload_by_assignee(df):
    workload = df.groupby('Assignee')['Estimated Hours'].sum().sort_values(ascending=False)
    fig = px.bar(workload, x=workload.index, y=workload.values, 
                 title="Workload by Assignee", labels={'y': 'Estimated Hours', 'x': 'Assignee'})
    fig.update_layout(height=500)
    return fig

@st.cache_data
def create_task_completion_trend(df):
    df['Completion_Week'] = df['Completed At'].dt.to_period('W').astype(str)
    completion_trend = df[df['Completion_Status'] == 'Completed'].groupby('Completion_Week').size().reset_index(name='Completed Tasks')
    fig = px.line(completion_trend, x='Completion_Week', y='Completed Tasks', title="Task Completion Trend")
    fig.update_layout(height=400)
    return fig

@st.cache_data
def create_delay_analysis(df):
    delay_by_project = df.groupby('Projects')['Number of Delays'].mean().sort_values(ascending=False)
    fig = px.bar(delay_by_project, x=delay_by_project.index, y=delay_by_project.values,
                 title="Average Number of Delays by Project", labels={'y': 'Average Delays', 'x': 'Project'})
    fig.update_layout(height=400)
    return fig

@st.cache_data
def create_estimated_vs_actual_hours(df):
    fig = px.scatter(df, x='Estimated Hours', y='Harvest Hours', color='Projects', 
                     hover_name='Name', title='Estimated vs Actual Hours')
    fig.add_trace(go.Scatter(x=[0, df['Estimated Hours'].max()], 
                             y=[0, df['Estimated Hours'].max()], 
                             mode='lines', name='Perfect Estimation'))
    fig.update_layout(height=500)
    return fig

@st.cache_data
def create_billable_hours_chart(df):
    billable_hours = df.groupby('Billable or Non-Billable')['Harvest Hours'].sum().reset_index()
    fig = px.pie(billable_hours, values='Harvest Hours', names='Billable or Non-Billable',
                 title='Billable vs Non-Billable Hours')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

@st.cache_data
def create_job_category_distribution(df):
    job_category_counts = df['Job Category'].value_counts()
    fig = px.bar(job_category_counts, x=job_category_counts.index, y=job_category_counts.values,
                 title="Distribution of Job Categories", labels={'y': 'Number of Tasks', 'x': 'Job Category'})
    fig.update_layout(height=500)
    return fig

def main():
    st.set_page_config(layout="wide", page_title="Interactive PM Dashboard")
    
    st.title("Comprehensive Interactive Project Management Dashboard")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_and_process_data(uploaded_file)
        
        # Project Overview
        st.header("Project Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Tasks", len(df))
        col2.metric("Completed Tasks", len(df[df['Completion_Status'] == 'Completed']))
        col3.metric("Overdue Tasks", len(df[df['Completion_Status'] == 'Overdue']))
        col4.metric("Total Estimated Hours", f"{df['Estimated Hours'].sum():.2f}")
        col5.metric("Total Actual Hours", f"{df['Harvest Hours'].sum():.2f}")
        
        # Task filtering
        st.subheader("Task Filtering")
        
        # Filter by Assignee
        assignees = df['Assignee'].dropna().unique().tolist()
        selected_assignees = st.multiselect("Filter by Assignee", options=assignees, default=assignees)
        
        # Filter by Project
        projects = df['Projects'].dropna().unique().tolist()
        selected_projects = st.multiselect("Filter by Project", options=projects, default=projects)
        
        # Filter by Deliverable Status
        statuses = df['Deliverable Status'].dropna().unique().tolist()
        selected_statuses = st.multiselect("Filter by Deliverable Status", options=statuses, default=statuses)

        # Interactive Gantt Chart
        st.subheader("Interactive Project Timeline (Gantt Chart)")
        gantt_fig = create_interactive_gantt(df, selected_assignees, selected_projects, selected_statuses)
        st.plotly_chart(gantt_fig, use_container_width=True)
        
        # Apply filters for other visualizations
        filtered_df = df[
            (df['Assignee'].isin(selected_assignees)) &
            (df['Projects'].isin(selected_projects)) &
            (df['Deliverable Status'].isin(selected_statuses))
        ]
        
        # Task Status and Workload
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Task Status Distribution")
            status_fig = create_task_status_distribution(filtered_df)
            st.plotly_chart(status_fig, use_container_width=True)
        
        with col2:
            st.subheader("Workload by Assignee")
            workload_fig = create_workload_by_assignee(filtered_df)
            st.plotly_chart(workload_fig, use_container_width=True)
        
        # Task Completion and Delay Analysis
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Task Completion Trend")
            trend_fig = create_task_completion_trend(filtered_df)
            st.plotly_chart(trend_fig, use_container_width=True)
        
        with col2:
            st.subheader("Delay Analysis")
            delay_fig = create_delay_analysis(filtered_df)
            st.plotly_chart(delay_fig, use_container_width=True)
        
        # Estimated vs Actual Hours
        st.subheader("Estimated vs Actual Hours")
        hours_fig = create_estimated_vs_actual_hours(filtered_df)
        st.plotly_chart(hours_fig, use_container_width=True)
        
        # Billable Hours Chart
        st.subheader("Billable vs Non-Billable Hours")
        billable_fig = create_billable_hours_chart(filtered_df)
        st.plotly_chart(billable_fig, use_container_width=True)
        
        # Job Category Distribution
        st.subheader("Job Category Distribution")
        job_category_fig = create_job_category_distribution(filtered_df)
        st.plotly_chart(job_category_fig, use_container_width=True)
        
        # Summary statistics
        st.subheader("Project Summary")
        st.write(f"Total number of tasks: {len(filtered_df)}")
        st.write(f"Project start date: {filtered_df['Start Date'].min().date()}")
        st.write(f"Project end date: {filtered_df['Due Date'].max().date()}")
        st.write(f"Number of assignees: {filtered_df['Assignee'].nunique()}")
        st.write(f"Total estimated hours: {filtered_df['Estimated Hours'].sum():.2f}")
        
        # Overdue tasks
        overdue_tasks = filtered_df[filtered_df['Overdue'] == True]
        st.write(f"Number of overdue tasks: {len(overdue_tasks)}")

        # Task completion status
        completed_tasks = filtered_df[filtered_df['Completed At'].notna()]
        st.write(f"Completed tasks: {len(completed_tasks)} ({len(completed_tasks)/len(filtered_df)*100:.2f}%)")
        
        # Custom Analysis
        st.header("Custom Analysis")
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Scatter Plot", "Line Chart"])
        x_axis = st.selectbox("Select X-axis", filtered_df.columns)
        y_axis = st.selectbox("Select Y-axis", [col for col in filtered_df.columns if filtered_df[col].dtype in ['int64', 'float64']])
        color_by = st.selectbox("Color by", ['None'] + filtered_df.columns.tolist())
        
        if chart_type == "Bar Chart":
            custom_fig = px.bar(filtered_df, x=x_axis, y=y_axis, color=color_by if color_by != 'None' else None,
                                title=f"{y_axis} by {x_axis}")
        elif chart_type == "Scatter Plot":
            custom_fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color=color_by if color_by != 'None' else None,
                                    title=f"{y_axis} vs {x_axis}")
        else:  # Line Chart
            custom_fig = px.line(filtered_df, x=x_axis, y=y_axis, color=color_by if color_by != 'None' else None,
                                 title=f"{y_axis} over {x_axis}")
        
        custom_fig.update_layout(height=600)
        st.plotly_chart(custom_fig, use_container_width=True)

if __name__ == "__main__":
    main()
