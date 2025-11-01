import threading
import queue
import time
from typing import Any

# Import your custom modules
from Asset_Manager import load_portfolio, save_portfolio
from Event_Processor import event_producer, event_consumer # type: ignore
from ui_logger import display_portfolio # type: ignore

if __name__ == "__main__":
    print("--- Starting Asset Management System ---")

    # 1. Initialize shared data by loading the portfolio
    load_portfolio("portfolio.json")

    # 2. Initialize communication channel (the thread-safe queue)
    event_queue: queue.Queue[Any] = queue.Queue()
    
    # 3. Create a stop event for the UI thread
    # This is a thread-safe way to tell the UI thread to stop
    stop_ui_event: threading.Event = threading.Event()

    # 4. Create all the threads
    # We pass the queue and file paths as arguments
    t_producer = threading.Thread(target=event_producer, args=(event_queue, "events.json"))
    t_consumer = threading.Thread(target=event_consumer, args=(event_queue,))
    
    # The UI thread is set as a "daemon" so it stops when the main program stops
    t_logger = threading.Thread(target=display_portfolio, args=(stop_ui_event,), daemon=True)

    print("--- Starting all threads ---")
    
    # 5. Start all the threads
    t_logger.start()
    t_producer.start()
    t_consumer.start()
    
    # This diagram shows how the threads are now running
    # 

    # 6. Wait for the work to be done
    # The main thread will pause here
    t_producer.join() # Wait for producer to finish reading the file
    print("--- Producer has finished. ---")
    
    t_consumer.join() # Wait for consumer to process all items
    print("--- Consumer has finished. ---")
    
    # 7. Save the final state of the portfolio
    save_portfolio("portfolio_final_state.json")

    # 8. Signal the UI thread to stop
    print("--- Work finished. Stopping UI thread. ---")
    stop_ui_event.set()
    
    # A small delay to let the UI thread exit gracefully
    time.sleep(1) 
    
    print("--- System shutdown complete. ---")