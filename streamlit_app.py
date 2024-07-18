import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
from streamlit_timeline import timeline

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    date_columns = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

@st.cache_data
def filter_data(df, assignees, projects, statuses):
    return df[
        (df['Assignee'].isin(assignees)) &
        (df['Projects'].isin(projects)) &
        (df['Deliverable Status'].isin(statuses))
    ]

def plotly_timeline(df):
    fig = px.timeline(df, x_start="Start Date", x_end="Due Date", y="Name", color="Assignee",
                      hover_data=["Task ID", "Projects", "Estimated Hours", "Deliverable Status"],
                      title="Project Timeline")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(rangeslider_visible=True)
    return fig

def altair_timeline(df):
    chart = alt.Chart(df).mark_bar().encode(
        x='Start Date',
        x2='Due Date',
        y='Name',
        color='Assignee',
        tooltip=['Name', 'Assignee', 'Projects', 'Estimated Hours', 'Deliverable Status']
    ).interactive()
    return chart

def streamlit_timeline_js(df):
    events = [
        {
            "start_date": {
                "year": str(row['Start Date'].year),
                "month": str(row['Start Date'].month),
                "day": str(row['Start Date'].day)
            },
            "end_date": {
                "year": str(row['Due Date'].year),
                "month": str(row['Due Date'].month),
                "day": str(row['Due Date'].day)
            },
            "text": {
                "headline": row['Name'],
                "text": f"Assignee: {row['Assignee']}<br>Project: {row['Projects']}<br>Status: {row['Deliverable Status']}"
            }
        }
        for _, row in df.iterrows()
    ]
    
    return {
        "title": {
            "text": {
                "headline": "Project Timeline",
                "text": "<p>Overview of project tasks</p>"
            }
        },
        "events": events
    }

def main():
    st.title("Custom Project Timeline")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if st.checkbox("Show Raw Data"):
            st.subheader("Raw Data")
            st.write(df.head())

        required_columns = ['Name', 'Start Date', 'Due Date']
        if not all(col in df.columns for col in required_columns):
            st.error("The CSV file must contain 'Name', 'Start Date', and 'Due Date' columns.")
            return

        st.subheader("Project Timeline")
        
        timeline_type = st.selectbox("Select Timeline Type", ["Plotly", "Altair", "TimelineJS"])
        
        # Task filtering
        st.subheader("Task Filtering")
        
        assignees = df['Assignee'].dropna().unique().tolist()
        selected_assignees = st.multiselect("Filter by Assignee", options=assignees, default=assignees)
        
        projects = df['Projects'].dropna().unique().tolist()
        selected_projects = st.multiselect("Filter by Project", options=projects, default=projects)
        
        statuses = df['Deliverable Status'].dropna().unique().tolist()
        selected_statuses = st.multiselect("Filter by Deliverable Status", options=statuses, default=statuses)

        filtered_df = filter_data(df, selected_assignees, selected_projects, selected_statuses)

        # Sampling for large datasets
        if len(filtered_df) > 1000:
            st.warning(f"Large dataset detected. Sampling {1000} rows for visualization.")
            filtered_df = filtered_df.sample(n=1000, random_state=42)

        if st.button("Generate Timeline"):
            if timeline_type == "Plotly":
                fig = plotly_timeline(filtered_df)
                st.plotly_chart(fig, use_container_width=True)
            elif timeline_type == "Altair":
                chart = altair_timeline(filtered_df)
                st.altair_chart(chart, use_container_width=True)
            elif timeline_type == "TimelineJS":
                timeline_data = streamlit_timeline_js(filtered_df)
                timeline(timeline_data)

        # Summary statistics
        st.subheader("Project Summary")
        st.write(f"Total number of tasks: {len(filtered_df)}")
        st.write(f"Project start date: {filtered_df['Start Date'].min().date()}")
        st.write(f"Project end date: {filtered_df['Due Date'].max().date()}")
        st.write(f"Number of assignees: {filtered_df['Assignee'].nunique()}")
        st.write(f"Total estimated hours: {filtered_df['Estimated Hours'].sum():.2f}")
        
        overdue_tasks = filtered_df[filtered_df['Overdue'] == True]
        st.write(f"Number of overdue tasks: {len(overdue_tasks)}")

        completed_tasks = filtered_df[filtered_df['Completed At'].notna()]
        st.write(f"Completed tasks: {len(completed_tasks)} ({len(completed_tasks)/len(filtered_df)*100:.2f}%)")

if __name__ == "__main__":
    main()
