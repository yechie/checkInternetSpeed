# Internet Speed Test Logger

A Python script to track your internet connection speed over time using the **official Ookla Speedtest CLI**. It logs the results to a file and calculates historical averages.

## Features

- **Automated Speed Testing**: Measures Download, Upload, and Ping.
- **Official CLI Integration**: Strictly uses the official Ookla binary for accurate results.
- **Robust Logging**: Saves every test result to `speed_log.txt` with timestamp, server ID, and name.
- **Historical Averages**: Calculates and displays the average Download, Upload, and Ping from previous runs.
- **Server Selection**:
    - Select by **Server ID**.
    - Select by **Server Name** (partial match support).
    - Auto-selects the best server if none provided.
- **Smart Diagnostics**:
    - Search for servers by name to find their IDs using `--checkserver`.
    - Automatically accepts license/GDPR prompts to prevent hanging.

## Prerequisites

This script **requires** the official Ookla Speedtest CLI.
It is **not** compatible with the legacy `speedtest-cli` Python library.

### Installing Ookla Speedtest CLI
Follow the official instructions: [https://www.speedtest.net/apps/cli](https://www.speedtest.net/apps/cli)

**Ubuntu/Debian example:**
```bash
sudo apt-get install curl
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest
```

## Usage

Make the script executable:
```bash
chmod +x check_speed.py
```

### 1. Basic Test (Auto-select best server)
```bash
./check_speed.py
```

### 2. Select a Specific Server by ID
```bash
./check_speed.py --serverid 1234
```

### 3. Select a Server by Name
Search for a server with "Bezeq" in the name and use it. The script will try to resolve the name to a server ID.
```bash
./check_speed.py --servername "Bezeq"
```

### 4. Search for Server IDs
Just search for servers (does not run a speed test):
```bash
./check_speed.py --checkserver "Tel Aviv"
```
*Use this to find the ID to use with `--serverid` for reliable repetitive testing.*

### 5. Custom Log File
Specify a custom log file (default is `speed_log.txt`):
```bash
./check_speed.py --logfile "my_speed_log.txt"
```

### 5. Check Historical Stats
Display historical statistics without running a new test. This includes the total number of tests, average speeds, and the lowest and highest speeds recorded.
```bash
./check_speed.py --stats
```

### 6. Plot History
Visualize speed test results from the last 30 days.

**GUI Plot (Default):**
```bash
./check_speed.py --plot
```
Opens a window with a dual-axis graph:
- **Left Axis**: Measured speeds (solid lines).
- **Right Axis**: Cumulative average speeds (dashed lines).

**Terminal Plot (ASCII):**
```bash
./check_speed.py --plot text
```
Prints the graph directly to the terminal using `plotext`.


## Logs & Output

Results are appended to `speed_log.txt` (or specified log file) in CSV format:
```csv
timestamp,download_speed,upload_speed,ping,server_id,server_name
```
Example output:
```text
2025-12-25T14:30:00.123456,920.50,95.20,5.00,1234,Bezeq (Tel Aviv)
```

At the end of every run, the script reads this log to show you your historical averages.
