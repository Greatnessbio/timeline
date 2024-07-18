import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def main():
    st.set_page_config(layout="wide")
    st.title("Enhanced Project Dashboard")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Convert date columns to datetime
        date_columns = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Calculate task duration
        df['Duration'] = (df['Due Date'] - df['Start Date']).dt.days

        # Sidebar for filtering
        st.sidebar.header("Filters")
        
        # Filter by Date Range
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(df['Start Date'].min().date(), df['Due Date'].max().date()),
            min_value=df['Start Date'].min().date(),
            max_value=df['Due Date'].max().date()
        )

        # Filter by Assignee
        assignees = df['Assignee'].dropna().unique().tolist()
        selected_assignees = st.sidebar.multiselect("Select Assignees", options=assignees, default=assignees)

        # Filter by Project
        projects = df['Projects'].dropna().unique().tolist()
        selected_projects = st.sidebar.multiselect("Select Projects", options=projects, default=projects)

        # Filter by Deliverable Status
        statuses = df['Deliverable Status'].dropna().unique().tolist()
        selected_statuses = st.sidebar.multiselect("Select Deliverable Statuses", options=statuses, default=statuses)

        # Apply filters
        filtered_df = df[
            (df['Start Date'].dt.date >= date_range[0]) &
            (df['Due Date'].dt.date <= date_range[1]) &
            (df['Assignee'].isin(selected_assignees)) &
            (df['Projects'].isin(selected_projects)) &
            (df['Deliverable Status'].isin(selected_statuses))
        ]

        # Main content area
        col1, col2 = st.columns([2, 1])

        with col1:
            # Gantt Chart
            st.subheader("Project Timeline (Gantt Chart)")
            fig_gantt = px.timeline(
                filtered_df, 
                x_start="Start Date", 
                x_end="Due Date", 
                y="Name",
                color="Assignee",
                hover_name="Name",
                hover_data={
                    "Start Date": "|%B %d, %Y",
                    "Due Date": "|%B %d, %Y",
                    "Duration": True,
                    "Estimated Hours": True,
                    "Deliverable Status": True,
                    "Overdue": True
                },
                labels={
                    "Name": "Task",
                    "Assignee": "Assigned To",
                    "Duration": "Duration (days)"
                },
            )
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(height=600, title_x=0.5)
            st.plotly_chart(fig_gantt, use_container_width=True)

        with col2:
            # Task Status Breakdown
            st.subheader("Task Status Breakdown")
            status_counts = filtered_df['Deliverable Status'].value_counts()
            fig_status = px.pie(status_counts, values=status_counts.values, names=status_counts.index, hole=0.3)
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

            # Assignee Workload
            st.subheader("Assignee Workload")
            assignee_workload = filtered_df.groupby('Assignee')['Estimated Hours'].sum().sort_values(ascending=False)
            fig_workload = px.bar(assignee_workload, x=assignee_workload.index, y=assignee_workload.values)
            fig_workload.update_layout(xaxis_title="Assignee", yaxis_title="Total Estimated Hours")
            st.plotly_chart(fig_workload, use_container_width=True)

        # Project Progress
        st.subheader("Project Progress")
        total_tasks = len(filtered_df)
        completed_tasks = len(filtered_df[filtered_df['Completed At'].notna()])
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        fig_progress = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = progress * 100,
            title = {'text': "Project Completion"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'axis': {'range': [0, 100]},
                     'bar': {'color': "darkblue"},
                     'steps' : [
                         {'range': [0, 50], 'color': "lightgray"},
                         {'range': [50, 75], 'color': "gray"},
                         {'range': [75, 100], 'color': "darkgray"}],
                     'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}
        ))
        st.plotly_chart(fig_progress, use_container_width=True)

        # Task Table
        st.subheader("Task Details")
        st.dataframe(filtered_df[['Name', 'Assignee', 'Start Date', 'Due Date', 'Estimated Hours', 'Deliverable Status', 'Overdue']])

        # Summary statistics
        st.subheader("Project Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tasks", len(filtered_df))
        with col2:
            st.metric("Completed Tasks", completed_tasks)
        with col3:
            st.metric("Overdue Tasks", len(filtered_df[filtered_df['Overdue'] == True]))
        with col4:
            st.metric("Total Estimated Hours", f"{filtered_df['Estimated Hours'].sum():.2f}")

if __name__ == "__main__":
    main()
