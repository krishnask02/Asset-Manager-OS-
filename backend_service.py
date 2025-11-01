import threading
import queue
import time
from typing import Any

# Import your custom modules
from Asset_Manager import load_portfolio
from Event_Processor import event_producer, event_consumer # type: ignore

# We are NOT importing the ui_logger or save_portfolio
# This service's only job is to run the background tasks

if __name__ == "__main__":
    print("--- Starting Backend Service ---")

    load_portfolio("portfolio.json")
    event_queue: queue.Queue[Any] = queue.Queue()

    # Create the background threads
    t_producer = threading.Thread(target=event_producer, args=(event_queue, "events.json"))
    t_consumer = threading.Thread(target=event_consumer, args=(event_queue,))

    # Set them as daemon threads
    # This means they will stop automatically if the main script stops
    t_producer.daemon = True
    t_consumer.daemon = True

    print("--- Starting producer and consumer threads ---")
    t_producer.start()
    t_consumer.start()

    # This loop keeps the main script alive
    # so the daemon threads can keep running
    print("--- Backend service is now running. Press CTRL+C to stop. ---")
    try:
        while True:
            time.sleep(1)
            # You can add a check here to restart threads if they fail
            if not t_producer.is_alive() or not t_consumer.is_alive():
                print("A backend thread has stopped. (In a real app, you'd restart it)")
                break
    except KeyboardInterrupt:
        print("\n--- Backend service shutting down. ---")