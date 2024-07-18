import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Global variables
DATE_COLUMNS = ['Start Date', 'Due Date', 'Created At', 'Completed At', 'Last Modified']

def load_data(file):
    df = pd.read_csv(file)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    df['Duration'] = (df['Due Date'] - df['Start Date']).dt.days
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

def gantt_chart(df):
    st.title("Project Timeline (Gantt Chart)")
    
    y_axis = st.selectbox("Select Y-axis", options=['Name', 'Assignee', 'Projects', 'Deliverable Status'])
    color_by = st.selectbox("Color by", options=['Assignee', 'Projects', 'Deliverable Status', 'Overdue'])

    fig = px.timeline(
        df, 
        x_start="Start Date", 
        x_end="Due Date", 
        y=y_axis,
        color=color_by,
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
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

def pie_chart(df):
    st.title("Task Distribution")
    
    attribute = st.selectbox("Select attribute to analyze", options=['Deliverable Status', 'Assignee', 'Projects', 'Overdue'])
    
    value_counts = df[attribute].value_counts()
    fig = px.pie(value_counts, values=value_counts.values, names=value_counts.index, hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

def bar_chart(df):
    st.title("Task Analysis")
    
    x_axis = st.selectbox("Select X-axis", options=['Assignee', 'Projects', 'Deliverable Status'])
    y_axis = st.selectbox("Select Y-axis", options=['Estimated Hours', 'Duration', 'count'])
    color_by = st.selectbox("Color by", options=['None', 'Assignee', 'Projects', 'Deliverable Status', 'Overdue'])

    if y_axis == 'count':
        df_grouped = df.groupby(x_axis).size().reset_index(name='count')
    else:
        df_grouped = df.groupby(x_axis)[y_axis].sum().reset_index()

    fig = px.bar(
        df_grouped, 
        x=x_axis, 
        y=y_axis if y_axis != 'count' else 'count', 
        color=None if color_by == 'None' else df[color_by],
        labels={x_axis: x_axis, y_axis: y_axis if y_axis != 'count' else 'Count'}
    )
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

def scatter_plot(df):
    st.title("Task Scatter Plot")
    
    x_axis = st.selectbox("Select X-axis", options=['Estimated Hours', 'Duration', 'Start Date', 'Due Date'])
    y_axis = st.selectbox("Select Y-axis", options=['Duration', 'Estimated Hours', 'Start Date', 'Due Date'])
    color_by = st.selectbox("Color by", options=['Assignee', 'Projects', 'Deliverable Status', 'Overdue'])
    
    fig = px.scatter(
        df, 
        x=x_axis, 
        y=y_axis, 
        color=color_by,
        hover_name="Name",
        labels={
            "Estimated Hours": "Estimated Hours",
            "Duration": "Duration (days)",
            "Start Date": "Start Date",
            "Due Date": "Due Date"
        }
    )
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

def main():
    st.set_page_config(layout="wide", page_title="Dynamic Project Dashboard")
    
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        filtered_df = filter_data(df)
        
        page = st.sidebar.selectbox("Select a chart", ["Gantt Chart", "Pie Chart", "Bar Chart", "Scatter Plot"])
        
        if page == "Gantt Chart":
            gantt_chart(filtered_df)
        elif page == "Pie Chart":
            pie_chart(filtered_df)
        elif page == "Bar Chart":
            bar_chart(filtered_df)
        elif page == "Scatter Plot":
            scatter_plot(filtered_df)

if __name__ == "__main__":
    main()
