import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
from streamlit_timeline import timeline

def plotly_timeline(df):
    fig = px.timeline(df, x_start="Start Date", x_end="Due Date", y="Name", color="Assignee",
                      hover_data=["Task ID", "Projects", "Estimated Hours", "Deliverable Status"],
                      title="Project Timeline")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(rangeslider_visible=True)
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
                         args=[{"xaxis.range": [df['Start Date'].min(), df['Due Date'].max()]}]),
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
    events = []
    for _, row in df.iterrows():
        event = {
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
        events.append(event)
    
    timeline_data = {
        "title": {
            "text": {
                "headline": "Project Timeline",
                "text": "<p>Overview of project tasks</p>"
            }
        },
        "events": events
    }
    return timeline_data

def main():
    st.title("Custom Project Timeline")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        st.subheader("Raw Data")
        st.write(df)

        required_columns = ['Name', 'Start Date', 'Due Date']
        if not all(col in df.columns for col in required_columns):
            st.error("The CSV file must contain 'Name', 'Start Date', and 'Due Date' columns.")
            return

        date_columns = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        st.subheader("Project Timeline")
        
        timeline_type = st.selectbox("Select Timeline Type", ["Plotly", "Altair", "TimelineJS"])
        
        if timeline_type == "Plotly":
            fig = plotly_timeline(df)
            st.plotly_chart(fig)
        elif timeline_type == "Altair":
            chart = altair_timeline(df)
            st.altair_chart(chart, use_container_width=True)
        elif timeline_type == "TimelineJS":
            timeline_data = streamlit_timeline_js(df)
            timeline(timeline_data)

        # Task filtering (same as before)
        st.subheader("Task Filtering")
        
        assignees = df['Assignee'].dropna().unique().tolist()
        selected_assignees = st.multiselect("Filter by Assignee", options=assignees, default=assignees)
        
        projects = df['Projects'].dropna().unique().tolist()
        selected_projects = st.multiselect("Filter by Project", options=projects, default=projects)
        
        statuses = df['Deliverable Status'].dropna().unique().tolist()
        selected_statuses = st.multiselect("Filter by Deliverable Status", options=statuses, default=statuses)

        filtered_df = df[
            (df['Assignee'].isin(selected_assignees)) &
            (df['Projects'].isin(selected_projects)) &
            (df['Deliverable Status'].isin(selected_statuses))
        ]

        st.subheader("Filtered Project Timeline")
        
        if timeline_type == "Plotly":
            fig_filtered = plotly_timeline(filtered_df)
            st.plotly_chart(fig_filtered)
        elif timeline_type == "Altair":
            chart_filtered = altair_timeline(filtered_df)
            st.altair_chart(chart_filtered, use_container_width=True)
        elif timeline_type == "TimelineJS":
            timeline_data_filtered = streamlit_timeline_js(filtered_df)
            timeline(timeline_data_filtered)

        # Summary statistics (same as before)
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
