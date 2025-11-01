🤖 OS Simulator: Real-Time Asset Task Manager
A university project for OPERATING SYSTEM 20IC301P that simulates an advanced operating system kernel. It demonstrates core OS concepts (MLFQ scheduling, paging, synchronization, and interrupts) by managing a portfolio of financial assets as if they were running processes.

This project is not just a simulation; it's an interactive "Task Manager" GUI built with Streamlit that runs a real-time WebSocket producer, multiple producer threads, and a preemptive scheduler to manage a "Process Table" of assets.

🚀 Core Concepts Demonstrated
1. Process & Thread Management
Assets as Processes: Each asset (stock, crypto, etc.) is treated as a "process" with its own PID (Process ID) and State.
Multithreading: The system runs 5+ concurrent threads:
3 Producer Threads:
websocket_price_producer (Live Binance data for Q0)
news_event_producer (Mock news from events.json for Q1)
batch_recheck_producer (Routine re-analysis for Q2)
1 Consumer Thread: The mlfq_scheduler_consumer acts as the CPU, processing tasks from the queues.
1 UI Thread: The streamlit app acts as the main thread.
2. CPU Scheduling (Multi-Level Feedback Queue)
This project implements a full 4-Level MLFQ to ensure high-priority tasks are preemptive:
Q-1 (Interrupt): Highest priority. Fed by user interaction (e.g., "Force Refresh" button).
Q0 (Critical): Fed by the real-time WebSocket producer (e.g., a sudden price crash).
Q1 (Interactive): Fed by the mock news producer (e.g., standard news).
Q2 (Batch): Lowest priority. Fed by the batch producer for routine checks. The Scheduler (consumer) always checks Q-1 first, then Q0, then Q1, and finally Q2, ensuring critical tasks are never blocked.
3. Memory Management (Paging)
Paging: The portfolio is split into two "memory" pools to simulate virtual memory:
Active Set ("RAM"): A fixed-size pool (e.g., 10 assets) that is actively monitored.
Inactive Set ("Disk"): All other assets that are "paged out."
Page Faults: When an event (Q-1, Q0, Q1) arrives for an asset in the "Inactive Set," a page fault is triggered.
Page Swap: The "kernel" (Asset_Manager.py) swaps the asset into the "Active Set" and "pages out" the lowest-priority asset from RAM to make room.
4. Synchronization (Mutex)
Critical Section: The shared memory (_g_active_set, _g_inactive_set) is a critical section.
Mutex: A threading.Lock (_g_portfolio_lock) is used to protect the shared memory. Any thread (producers, consumer, or UI) must acquire this lock before reading or writing, preventing race conditions.
Visualization: All lock/release actions are logged in the "System Log" in the UI.
5. Process States
Assets move between states just like real OS processes:
Swapped (on Disk): Inactive, in the "virtual memory" pool.
Active (in RAM): Idle, but in the "physical memory" pool.
Ready (in Q): An event has arrived. The asset is in one of the MLFQ ready queues, waiting for the "CPU."
Processing (CPU): The asset is currently being worked on by the scheduler thread.
✨ Features
Real-Time Data: Connects to a live Binance WebSocket to generate real Q0 (Critical) events based on BTCUSDT price action.
Interactive UI: Built with Streamlit, the "Task Manager" GUI updates every second.
Live Controls:
Trigger an Interrupt: A "Force Refresh" button lets the user manually trigger a Q-1 interrupt for any asset.
Update Asset Value: The user can change the value of any asset in real-time, which recalculates its Base Priority and can cause the process table to re-sort.
Deep Visualization:
Process Table: The main view shows all assets, their PID, State, and priority scores.
Live Queues: A side panel shows the number of "processes" waiting in each of the 4 MLFQ queues.
System Logs: Separate live-updating logs show the Scheduler (CPU) Log and the Mutex (Lock) Log.
🔧 How to Run
Install dependencies:
Bash
pip install streamlit pandas websocket-client
Clone the repository:
Bash
git clone [your-repo-url]
Navigate to the project directory:
Bash
cd OS_Project
Run the Streamlit app:
Bash
streamlit run app.py
A browser window will open automatically, displaying your "Asset Task Manager" dashboard.
📽️ Demo
Here is a demo of the program running. You can see the "Live Event Feed" logging new tasks, the "Process Table" states changing from Active to Ready to Processing, and the "Priority Chart" re-sorting in real-time.

📂 Project Structure
app.py: The "Task Manager" GUI. This is the only file you run. It starts the threads and renders the Streamlit dashboard.
Asset_Manager.py: The "Kernel." Manages all shared memory (Active/Inactive sets), states, PIDs, and the Mutex. All "system calls" (thread-safe functions) are here.
Event_Processor.py: The "CPU & Producers." Contains the logic for all 3 producer threads and the 1 MLFQ scheduler (consumer) thread.
portfolio.json: The "database" of assets, loaded at the start.
events.json: The "mock API" of news events for the Q1 producer.
