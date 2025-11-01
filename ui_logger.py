import threading
import time
from typing import List, Dict, Any
# Import the thread-safe function from your Asset_Manager
from Asset_Manager import get_sorted_portfolio

def display_portfolio(stop_event: threading.Event) -> None:
    """
    UI THREAD: Periodically gets the sorted portfolio and prints it.
    """
    while not stop_event.is_set():
        
        # --- NO LOCK NEEDED ---
        # We just call the simple, thread-safe function.
        # It handles the lock and returns a sorted copy.
        sorted_portfolio: List[Dict[str, Any]] = get_sorted_portfolio()
        # --- END ---

        # --- Printing (Done safely, with no lock held) ---
        print("\n" + "="*40)
        print(f" PORTFOLIO DASHBOARD (Time: {time.strftime('%H:%M:%S')} )")
        print("="*40)
        
        for i, asset in enumerate(sorted_portfolio):
            # Format the value to be readable (e.g., 1,50,00,000)
            value_str = f"₹{asset['current_value']:,}"
            
            print(f"{i+1}. {asset['name']} ({asset['type']})")
            print(f"   Value: {value_str: <18} | Priority: {asset['priority_score']}")
            
            # Only show the suggestion if there is one
            if asset['suggestion'] != "None":
                print(f"   -> Suggestion: {asset['suggestion']}")
        
        print("="*40 + "\n")
        
        # Wait 2 seconds before the next refresh
        time.sleep(2)