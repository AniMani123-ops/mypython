import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_youtube_service, get_channel_stats, search_channels, POPULAR_NEWS_CHANNELS

st.set_page_config(page_title="YouTube News Channel Comparison", layout="wide")

st.title("YouTube News Channel Comparison")
st.markdown("Compare statistics of different YouTube news channels.")

# Load API Key from Secrets
if "YOUTUBE_API_KEY" in st.secrets:
    api_key = st.secrets["YOUTUBE_API_KEY"]
else:
    st.error("YOUTUBE_API_KEY not found in .streamlit/secrets.toml")
    st.stop()

# Initialize Service
service = get_youtube_service(api_key)

if not service:
    st.error("Failed to initialize YouTube service. Please check your API Key.")
    st.stop()

# Initialize session state for selected channels
if 'selected_channels' not in st.session_state:
    st.session_state['selected_channels'] = []

# Sidebar: Channel Search & Management
with st.sidebar:
    st.header("Manage Channels")
    
    # Search Section
    st.subheader("Add New Channel")
    search_query = st.text_input("Search for a channel")
    
    if st.button("Search"):
        if search_query:
            with st.spinner("Searching..."):
                results, error = search_channels(service, search_query)
                if results:
                    st.session_state['search_results'] = results
                elif error:
                    st.error(error)
                else:
                    st.warning("No channels found.")
    
    # Display Search Results
    if 'search_results' in st.session_state:
        options = {f"{ch['title']}": ch for ch in st.session_state['search_results']}
        selected_search_result = st.selectbox("Select channel to add", options=list(options.keys()))
        
        if st.button("Add Channel"):
            channel_to_add = options[selected_search_result]
            
            # Check if already added
            current_ids = [ch['id'] for ch in st.session_state['selected_channels']]
            if channel_to_add['id'] not in current_ids:
                st.session_state['selected_channels'].append({
                    'id': channel_to_add['id'],
                    'title': channel_to_add['title']
                })
                st.success(f"Added {channel_to_add['title']}")
                # Optional: Clear search results after adding
                # del st.session_state['search_results'] 
            else:
                st.warning("Channel already selected.")

    st.divider()

    # List of Selected Channels
    st.subheader("Selected Channels")
    
    # Create a copy to iterate while modifying
    for ch in st.session_state['selected_channels'][:]:
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"**{ch['title']}**")
        if col2.button("❌", key=ch['id']):
            st.session_state['selected_channels'].remove(ch)
            st.rerun()

    if st.button("Reset App"):
        st.session_state.clear()
        st.rerun()

# Main Content: Comparison Logic
if st.session_state['selected_channels']:
    selected_channel_ids = [ch['id'] for ch in st.session_state['selected_channels']]
    
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
else:
    st.info("👈 Please start by searching and adding channels from the sidebar!")
