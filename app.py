import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_youtube_service, search_channels, get_channel_stats

st.set_page_config(page_title="YouTube News Channel Comparison", layout="wide")

st.title("YouTube News Channel Comparison")
st.markdown("Compare statistics of different YouTube news channels.")

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your YouTube Data API Key", type="password")
    if not api_key:
        st.warning("Please enter your API Key to proceed.")
        st.stop()

# Initialize Service
service = get_youtube_service(api_key)

if not service:
    st.error("Failed to initialize YouTube service. Please check your API Key.")
    st.stop()

# Search Interface
st.header("Search Channels")
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("Search for a channel (e.g., 'BBC News')")

with col2:
    search_button = st.button("Search")

# Session state for search results and selected channels
if "search_results" not in st.session_state:
    st.session_state.search_results = []

if search_button and search_query:
    with st.spinner("Searching..."):
        new_results = search_channels(service, search_query)
        # Avoid duplicates by checking channel IDs
        existing_ids = {item['id'] for item in st.session_state.search_results}
        for res in new_results:
            if res['id'] not in existing_ids:
                st.session_state.search_results.append(res)
        
        if not new_results:
            st.warning("No channels found.")

# Display Search Results and Selection
selected_channels_data = []
if st.session_state.search_results:
    st.subheader("Your Search History & Selection")
    
    # Create a dictionary for easier lookup and display in multiselect
    # Use title and ID in the label to handle channels with same name
    channel_options = {f"{item['title']} ({item['id']})": item['id'] for item in st.session_state.search_results}
    
    selected_channel_names = st.multiselect(
        "Select channels to compare:",
        options=list(channel_options.keys())
    )
    
    selected_channel_ids = [channel_options[name] for name in selected_channel_names]
    
    if selected_channel_ids:
        if st.button("Compare Selected Channels"):
            with st.spinner("Fetching statistics..."):
                stats_df = get_channel_stats(service, selected_channel_ids)
                
                if not stats_df.empty:
                    st.divider()
                    st.header("Comparison")

                    # Tabular View
                    st.subheader("Tabular View")
                    st.dataframe(stats_df, use_container_width=True)

                    # Graphical View
                    st.subheader("Graphical View")
                    
                    # Layout for charts
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        fig_subs = px.bar(stats_df, x='Channel Name', y='Subscribers', title='Subscribers Comparison', color='Channel Name')
                        st.plotly_chart(fig_subs, use_container_width=True)
                        
                    with chart_col2:
                         fig_views = px.bar(stats_df, x='Channel Name', y='Total Views', title='Total Views Comparison', color='Channel Name')
                         st.plotly_chart(fig_views, use_container_width=True)
                    
                    fig_videos = px.bar(stats_df, x='Channel Name', y='Video Count', title='Video Count Comparison', color='Channel Name')
                    st.plotly_chart(fig_videos, use_container_width=True)
                else:
                    st.error("Could not retrieve statistics for the selected channels.")
