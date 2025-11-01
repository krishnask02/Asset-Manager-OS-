import streamlit as st
import pandas as pd
import time
import threading
import queue
from typing import Any, List, Dict

# --- Import All Your Project Files ---
from Asset_Manager import (
    load_portfolio, 
    get_sorted_portfolio, 
    _g_portfolio_list,
    get_event_history  # NEW: Import the history function
)
from Event_Processor import event_producer, event_consumer # type: ignore

# --- Page Configuration ---
st.set_page_config(
    page_title="OS Project Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Singleton Function to Start Background Threads ---
@st.cache_resource
def init_backend():
    """
    Initializes the portfolio and starts the producer/consumer threads.
    """
    print("--- (Re)Starting Backend Threads ---")
    if not _g_portfolio_list:
        load_portfolio("portfolio.json")

    event_queue: queue.Queue[Any] = queue.Queue()
    t_producer = threading.Thread(
        target=event_producer, 
        args=(event_queue, "events.json"), 
        daemon=True
    )
    t_consumer = threading.Thread(
        target=event_consumer, 
        args=(event_queue,), 
        daemon=True
    )
    t_producer.start()
    t_consumer.start()
    print("--- Backend Threads are Live ---")
    return True

# --- The Main Application ---

# 1. Run the Backend
init_backend()

# 2. Main Page Title
st.title("📈 Real-Time Asset Priority Dashboard")
st.caption(f"Dashboard last updated: {time.strftime('%H:%M:%S')}")

# 3. Create a placeholder for the entire dashboard
placeholder = st.empty()

# 4. The Main Refresh Loop
while True:
    # --- GET ALL DATA ---
    portfolio_data: List[Dict[str, Any]] = get_sorted_portfolio()
    event_history: List[Dict[str, Any]] = get_event_history() # NEW: Get event history

    # If data isn't loaded yet, show a spinner
    if not portfolio_data:
        with placeholder.container():
            st.spinner("Waiting for portfolio data to load...")
        time.sleep(1)
        continue

    # --- Re-draw the entire dashboard inside the placeholder ---
    with placeholder.container():

        # --- NEW LAYOUT: 2 Columns (1/3 for events, 2/3 for main) ---
        col_events, col_main = st.columns([1, 2])

        # --- COLUMN 1: Event Feed (Your Request) ---
        with col_events:
            st.subheader("Live Event Feed")
            
            if not event_history:
                st.info("Waiting for first event...")
            
            # Display events (history is already reversed, newest first)
            for event in event_history:
                st.divider()
                st.caption(f"Time: {event['timestamp']}")
                
                # Find the asset name for a friendlier message
                asset_name = "Unknown"
                for asset in portfolio_data:
                    if asset['id'] == event['asset_id']:
                        asset_name = asset['name']
                        break
                
                st.text(f"Asset: {asset_name}")
                st.info(f"{event['suggestion']}")
                
                if event['bump'] > 0:
                    st.success(f"Priority Bump: +{event['bump']}")
                else:
                    st.error(f"Priority Bump: {event['bump']}")

        # --- COLUMN 2: Main Dashboard ---
        with col_main:
            # --- A: Top Priority Metrics ---
            st.subheader("Top Priority Assets")
            cols = st.columns(3)
            top_assets = portfolio_data[:3]
            
            for i, asset in enumerate(top_assets):
                if i < len(top_assets):
                    with cols[i]:
                        st.metric(
                            label=f"🥇 {i+1}st Priority: {asset['name']}",
                            value=f"Score: {asset['priority_score']}",
                            delta=f"{asset['suggestion']}",
                            delta_color="inverse" if asset['priority_score'] < 0 else "normal"
                        )

            st.divider()

            # --- B: Visualizations (Chart and Table) ---
            st.subheader("Asset Priority Monitor")
            
            tab1, tab2 = st.tabs(["Priority Chart (Live)", "Full Portfolio (Table)"])

            df = pd.DataFrame(portfolio_data)

            with tab1:
                chart_df = df.set_index("name")[['priority_score']]
                st.bar_chart(chart_df)
                st.caption("This chart visualizes the priority scores.")

            with tab2:
                st.caption("Complete view of all assets and their current status.")
                st.dataframe(
                    df,
                    column_config={
                        "name": "Asset Name",
                        "type": "Asset Class",
                        "current_value": st.column_config.NumberColumn(
                            "Current Value (₹)",
                            format="₹%,.0f"
                        ),
                        "priority_score": "Priority Score",
                        "suggestion": "Latest Suggestion"
                    },
                    column_order=("name", "type", "current_value", "priority_score", "suggestion"),
                    use_container_width=True
                )

    # Refresh every 1 second
    time.sleep(1)