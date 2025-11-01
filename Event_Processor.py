import threading
import queue
import time
import json
from typing import Dict, Any
# We NO LONGER import the lock! We import the safe function.
from Asset_Manager import update_asset_priority

def event_producer(event_queue: queue.Queue, filepath: str = "events.json") -> None:
    """
    PRODUCER THREAD: Reads from the JSON event file and puts events into the queue.
    """
    print("[Producer]: Starting... reading events from JSON.")
    try:
        with open(filepath, 'r') as f:
            events: List[Dict[str, Any]] = json.load(f) # Loads the entire list of events
    except Exception as e:
        print(f"[Producer]: ERROR, could not read {filepath}: {e}")
        event_queue.put(None) # Tell consumer to stop
        return

    for event in events:
        event_queue.put(event) # The event is a dictionary
        print(f"[Producer]: New event for {event['id']}. Queue size is {event_queue.qsize()}")
        time.sleep(3) # Simulate time between events
    
    event_queue.put(None) # "Poison pill" to tell the consumer to stop
    print("[Producer]: Finished all events. Sent stop signal.")

def event_consumer(event_queue: queue.Queue) -> None:
    """
    CONSUMER THREAD: Reads event dictionaries from the queue and updates the portfolio
    using the thread-safe function.
    """
    while True:
        event: Optional[Dict[str, Any]] = event_queue.get() # Waits for an item
        if event is None: 
            print("[Consumer]: Stop signal received. Shutting down.")
            event_queue.task_done()
            break # End the thread
        
        asset_id = event['id']
        suggestion = event['suggestion']
        bump = event['priority_bump']
        
        print(f"[Consumer]: Processing event for {asset_id}...")
        
        # CRITICAL SECTION REMOVED :
        # The complex lock/try/finally logic is GONE.
        # We just call the simple, thread-safe function.
        found = update_asset_priority(asset_id, suggestion, bump)
        # --- END ---
        
        if not found:
             print(f"[Consumer]: Warning - Asset ID '{asset_id}' from event not in portfolio.")
        else:
            print(f"[Consumer]: Updated {asset_id}.")
            
        event_queue.task_done()