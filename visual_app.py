import streamlit as st
import time
from Asset_Manager import get_sorted_portfolio
from typing import List, Dict, Any

# --- Page Configuration (Do this once at the top) ---
st.set_page_config(
    page_title="OS Project Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- The App ---
st.title("📈 Real-Time Asset Priority Dashboard")
st.caption("Visualizing OS concepts (multithreading & priority scheduling)")

# Create a placeholder element for the "last updated" time
time_placeholder = st.empty()

# Create a placeholder for the main dashboard
dashboard_placeholder = st.empty()

# --- Main App Loop ---
while True:
    # Get the latest data from our thread-safe function
    sorted_portfolio: List[Dict[str, Any]] = get_sorted_portfolio()
    
    # Update the "last updated" time
    time_placeholder.text(f"Last updated: {time.strftime('%H:%M:%S')}")

    # Use the 'with' syntax to write into our placeholder
    with dashboard_placeholder.container():
        
        # Create 3 columns for a "metric" style layout
        col1, col2, col3 = st.columns(3)
        
        # Display the Top 3 assets as metrics
        # We check if the list has assets to prevent errors
        if len(sorted_portfolio) > 0:
            with col1:
                st.metric(
                    label=f"🥇 1st Priority: {sorted_portfolio[0]['name']}", 
                    value=f"Score: {sorted_portfolio[0]['priority_score']}",
                    delta=f"{sorted_portfolio[0]['suggestion']}"
                )
        
        if len(sorted_portfolio) > 1:
            with col2:
                st.metric(
                    label=f"🥈 2nd Priority: {sorted_portfolio[1]['name']}", 
                    value=f"Score: {sorted_portfolio[1]['priority_score']}",
                    delta=f"{sorted_portfolio[1]['suggestion']}"
                )
        
        if len(sorted_portfolio) > 2:
            with col3:
                st.metric(
                    label=f"🥉 3rd Priority: {sorted_portfolio[2]['name']}", 
                    value=f"Score: {sorted_portfolio[2]['priority_score']}",
                    delta=f"{sorted_portfolio[2]['suggestion']}"
                )

        # --- Full Portfolio List ---
        st.subheader("Full Portfolio View")

        for asset in sorted_portfolio:
            value_str = f"₹{asset['current_value']:,}"
            
            # Use an expander to show details
            with st.expander(f"**{asset['name']}** (Priority: {asset['priority_score']})"):
                st.text(f"ID:         {asset['id']}")
                st.text(f"Type:       {asset['type']}")
                st.text(f"Value:      {value_str}")
                if asset['suggestion'] != "None":
                    st.success(f"Suggestion: {asset['suggestion']}")
    
    # Wait 2 seconds before refreshing the app
    time.sleep(2)
    