import threading
import json
import time # Import the time module
from typing import List, Dict, Any, Optional

# --- SHARED RESOURCES ---
_g_portfolio_list: List[Dict[str, Any]] = []
_g_event_history: List[Dict[str, Any]] = [] # NEW: To store event history
_g_portfolio_lock: threading.Lock = threading.Lock()
# --- END SHARED RESOURCES ---

def load_portfolio(filepath: str = "portfolio.json") -> None:
    """
    Loads the initial portfolio from the JSON file.
    """
    global _g_portfolio_list
    try:
        with open(filepath, 'r') as f:
            _g_portfolio_list = json.load(f)
        print(f"--- Portfolio loaded from {filepath} successfully. ---")
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        _g_portfolio_list = []

# --- THREAD-SAFE FUNCTIONS ---

def update_asset_priority(asset_id: str, suggestion: str, bump: int) -> bool:
    """
    THREAD-SAFE function to update an asset's priority AND
    record the event in the history.
    """
    global _g_portfolio_list, _g_event_history
    
    _g_portfolio_lock.acquire()
    
    found = False
    try:
        # 1. Update the portfolio list
        for asset in _g_portfolio_list:
            if asset['id'] == asset_id:
                asset['priority_score'] += bump
                asset['suggestion'] = suggestion
                found = True
                break
        
        # 2. NEW: Record the event in the history
        event_record = {
            "timestamp": time.strftime('%H:%M:%S'), # Add the current time
            "asset_id": asset_id,
            "suggestion": suggestion,
            "bump": bump
        }
        _g_event_history.append(event_record)
        
    finally:
        _g_portfolio_lock.release()
        
    return found

def get_sorted_portfolio() -> List[Dict[str, Any]]:
    """
    THREAD-SAFE function to get a sorted copy of the portfolio.
    """
    _g_portfolio_lock.acquire()
    sorted_copy: List[Dict[str, Any]] = []
    try:
        sorted_copy = sorted(
            _g_portfolio_list, 
            key=lambda x: x['priority_score'], 
            reverse=True
        )
    finally:
        _g_portfolio_lock.release()
    return sorted_copy

def get_event_history() -> List[Dict[str, Any]]:
    """
    NEW THREAD-SAFE function to get a (reversed) copy
    of the event history.
    """
    _g_portfolio_lock.acquire()
    history_copy: List[Dict[str, Any]] = []
    try:
        # Return a reversed copy so newest events are first
        history_copy = list(reversed(_g_event_history))
    finally:
        _g_portfolio_lock.release()
    return history_copy

# --- PERSISTENCE FUNCTION ---

def save_portfolio(filepath: str = "portfolio_final_state.json") -> None:
    """
    Saves the final state of the portfolio to a new JSON file.
    """
    _g_portfolio_lock.acquire()
    try:
        with open(filepath, 'w') as f:
            json.dump(_g_portfolio_list, f, indent=2)
        print(f"--- Final portfolio state saved to {filepath} ---")
    except Exception as e:
        print(f"Error saving portfolio: {e}")
    finally:
        _g_portfolio_lock.release()