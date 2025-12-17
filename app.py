import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_youtube_service, get_channel_stats, POPULAR_NEWS_CHANNELS

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

# Channel Selection
st.header("Select Channels")

selected_channels = st.multiselect(
    "Select Channels to Compare",
    options=list(POPULAR_NEWS_CHANNELS.keys()),
    default=list(POPULAR_NEWS_CHANNELS.keys())[:2]
)

if selected_channels:
    selected_channel_ids = [POPULAR_NEWS_CHANNELS[name] for name in selected_channels]
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
