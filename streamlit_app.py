import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def main():
    st.title("Updated Project Timeline")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Display raw data
        st.subheader("Raw Data")
        st.write(df)

        # Check if required columns exist
        required_columns = ['Name', 'Start Date', 'Due Date']
        if not all(col in df.columns for col in required_columns):
            st.error("The CSV file must contain 'Name', 'Start Date', and 'Due Date' columns.")
            return

        # Convert date columns to datetime
        date_columns = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Calculate task duration
        df['Duration'] = (df['Due Date'] - df['Start Date']).dt.days

        # Create Gantt chart
        st.subheader("Project Timeline (Gantt Chart)")

        fig = px.timeline(
            df, 
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
            title="Project Timeline"
        )

        # Customize the layout
        fig.update_yaxes(autorange="reversed")  # Reverse the order of tasks
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
            ),
            xaxis_title="Date",
            yaxis_title="Task",
            height=600,
            title_x=0.5,
            xaxis_range=[df['Start Date'].min() - timedelta(days=5), df['Due Date'].max() + timedelta(days=5)]
        )

        # Add range slider and buttons
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Task filtering
        st.subheader("Task Filtering")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            # Filter by Assignee
            assignees = df['Assignee'].dropna().unique().tolist()
            selected_assignees = st.multiselect("Filter by Assignee", options=assignees, default=assignees)

        with col2:
            # Filter by Project
            projects = df['Projects'].dropna().unique().tolist()
            selected_projects = st.multiselect("Filter by Project", options=projects, default=projects)

        with col3:
            # Filter by Deliverable Status
            statuses = df['Deliverable Status'].dropna().unique().tolist()
            selected_statuses = st.multiselect("Filter by Deliverable Status", options=statuses, default=statuses)

        # Apply filters
        filtered_df = df[
            (df['Assignee'].isin(selected_assignees)) &
            (df['Projects'].isin(selected_projects)) &
            (df['Deliverable Status'].isin(selected_statuses))
        ]

        # Create filtered Gantt chart
        st.subheader("Filtered Project Timeline")

        fig_filtered = px.timeline(
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
            title="Filtered Project Timeline"
        )

        fig_filtered.update_yaxes(autorange="reversed")
        fig_filtered.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
            ),
            xaxis_title="Date",
            yaxis_title="Task",
            height=600,
            title_x=0.5,
            xaxis_range=[filtered_df['Start Date'].min() - timedelta(days=5), filtered_df['Due Date'].max() + timedelta(days=5)]
        )

        fig_filtered.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        st.plotly_chart(fig_filtered, use_container_width=True)

        # Summary statistics
        st.subheader("Project Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Total number of tasks: {len(filtered_df)}")
            st.write(f"Project start date: {filtered_df['Start Date'].min().date()}")
            st.write(f"Project end date: {filtered_df['Due Date'].max().date()}")
            st.write(f"Number of assignees: {filtered_df['Assignee'].nunique()}")
        with col2:
            st.write(f"Total estimated hours: {filtered_df['Estimated Hours'].sum():.2f}")
            overdue_tasks = filtered_df[filtered_df['Overdue'] == True]
            st.write(f"Number of overdue tasks: {len(overdue_tasks)}")
            completed_tasks = filtered_df[filtered_df['Completed At'].notna()]
            st.write(f"Completed tasks: {len(completed_tasks)} ({len(completed_tasks)/len(filtered_df)*100:.2f}%)")

if __name__ == "__main__":
    main()
