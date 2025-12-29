#!/usr/bin/env python3

import argparse
import datetime
import os
import subprocess
import json
import sys
import shutil
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotext as plt_text


def get_args():
    parser = argparse.ArgumentParser(description='Check internet speed')
    parser.add_argument('--serverid', type=int, help='Preferred server ID')
    parser.add_argument('--servername', type=str, help='Preferred server name (partial match)')
    parser.add_argument('--checkserver', type=str, help='Check server availability by name and return details')
    parser.add_argument('--logfile', type=str, default='speed_log.txt', help='Path to log file (default: speed_log.txt)')
    return parser.parse_args()

def log_results(download, upload, ping, server_id, server_name, log_file):
    parser.add_argument('--plot', nargs='?', const='gui', help='Plot internet speed history (last 30 days). Use "text" for terminal plot.')
    parser.add_argument('--stats', action='store_true', help='Show historical statistics (averages and count) without running a test.')
    return parser.parse_args()


def log_results(download, upload, ping, server_id, server_name):
    timestamp = datetime.datetime.now().isoformat()
    # Sanitize server name to remove commas if any, to avoid CSV issues
    server_name = str(server_name).replace(',', ' ')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp},{download},{upload},{ping},{server_id},{server_name}\n")

def calculate_averages(log_file):
    if not os.path.exists(log_file):
        return None, None, None
def get_plot_data(days=30):
    if not os.path.exists(LOG_FILE):
        return None

    dates = []
    downloads = []
    uploads = []
    avg_downloads = []
    avg_uploads = []

    # Variables for cumulative average calculation
    cum_total_dl = 0.0
    cum_total_ul = 0.0
    count = 0

    now = datetime.datetime.now()
    cutoff_date = now - datetime.timedelta(days=days)

    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                try:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        ts_str = parts[0]
                        dl = float(parts[1])
                        ul = float(parts[2])
                        
                        dt = datetime.datetime.fromisoformat(ts_str)
                        
                        # Calculate cumulative averages (history matters for this, so calculate before filtering)
                        cum_total_dl += dl
                        cum_total_ul += ul
                        count += 1
                        
                        current_avg_dl = cum_total_dl / count
                        current_avg_ul = cum_total_ul / count

                        # Filter for plotting
                        if dt >= cutoff_date:
                            dates.append(dt)
                            downloads.append(dl)
                            uploads.append(ul)
                            avg_downloads.append(current_avg_dl)
                            avg_uploads.append(current_avg_ul)

                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading log file for plotting: {e}")
        return None

    if not dates:
        return None
        
    return {
        'dates': dates,
        'downloads': downloads,
        'uploads': uploads,
        'avg_downloads': avg_downloads,
        'avg_uploads': avg_uploads
    }

def plot_results():
    data = get_plot_data()
    if not data:
        print("No log file found or no data from the last 30 days.")
        return

    dates = data['dates']
    downloads = data['downloads']
    uploads = data['uploads']
    avg_downloads = data['avg_downloads']
    avg_uploads = data['avg_uploads']

    # Plotting
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Left Y-axis: Measured speeds
    color_dl = 'tab:blue'
    color_ul = 'tab:orange'
    
    ax1.set_xlabel('Date and Time')
    ax1.set_ylabel('Measured Speed (Mbps)', color='black')
    
    l1, = ax1.plot(dates, downloads, color=color_dl, label='Measured Download', alpha=0.6)
    l2, = ax1.plot(dates, uploads, color=color_ul, label='Measured Upload', alpha=0.6)
    
    ax1.tick_params(axis='y', labelcolor='black')

    # Right Y-axis: Average speeds
    ax2 = ax1.twinx()
    ax2.set_ylabel('Historical Average Speed (Mbps)', color='black')
    
    l3, = ax2.plot(dates, avg_downloads, color=color_dl, linestyle='--', label='Avg Download (Cumulative)', linewidth=2)
    l4, = ax2.plot(dates, avg_uploads, color=color_ul, linestyle='--', label='Avg Upload (Cumulative)', linewidth=2)
    
    ax2.tick_params(axis='y', labelcolor='black')

    # Formatting
    plt.title('Internet Speed History (Last 30 Days)')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()
    
    # Legend
    lines = [l1, l2, l3, l4]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.grid(True)
    plt.tight_layout()
    print("Displaying plot...")
    plt.show()

def plot_results_text():
    data = get_plot_data()
    if not data:
        print("No log file found or no data from the last 30 days.")
        return

    dates = data['dates']
    # Convert datetimes to string for plotext
    date_strs = [dt.strftime('%Y-%m-%d %H:%M') for dt in dates]
    
    downloads = data['downloads']
    uploads = data['uploads']
    avg_downloads = data['avg_downloads']
    avg_uploads = data['avg_uploads']

    plt_text.date_form('Y-m-d H:M')
    
    # Measured Speeds (Left Axis effectively)
    plt_text.plot(date_strs, downloads, label='Measured Download', color='blue')
    plt_text.plot(date_strs, uploads, label='Measured Upload', color='orange')
    
    # Averages
    # Plotext doesn't support dual-axis easily in same plot in simple mode,
    # but we can overlay them. Scales might be different but usually DL/UL are in similar ranges.
    # Note: If scales are vastly different, this might be messy in text mode.
    # However, existing GUI plot shares same scale concept (Mbps).
    plt_text.plot(date_strs, avg_downloads, label='Avg Download', color='blue+', marker='sd')
    plt_text.plot(date_strs, avg_uploads, label='Avg Upload', color='orange+', marker='sd')

    plt_text.title("Internet Speed History (Last 30 Days)")
    plt_text.xlabel("Date and Time")
    plt_text.ylabel("Speed (Mbps)")
    plt_text.show()



def calculate_averages():
    if not os.path.exists(LOG_FILE):
        return None, None, None, 0

    total_download = 0.0
    total_upload = 0.0
    total_ping = 0.0
    count = 0

    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    parts = line.strip().split(',')
                    # Ensure we have at least the basic speed data (timestamp, dl, ul, ping)
                    if len(parts) >= 4:
                        total_download += float(parts[1])
                        total_upload += float(parts[2])
                        total_ping += float(parts[3])
                        count += 1
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None, None, None, 0

    if count == 0:
        return None, None, None, 0

    return total_download / count, total_upload / count, total_ping / count, count

def get_official_speedtest_command():
    """Checks for official Ookla speedtest CLI in common paths and returns the executable path."""
    # Candidates to check: generic command, and explicit paths
    candidates = ['speedtest', '/usr/bin/speedtest', '/usr/local/bin/speedtest']
    
    for cmd in candidates:
        # Check if executable exists (shutil.which for commands, os.path.exists for paths)
        if not shutil.which(cmd) and not (os.path.isabs(cmd) and os.path.exists(cmd) and os.access(cmd, os.X_OK)):
            continue
            
        try:
            # Check version output for "Ookla"
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if 'Ookla' in result.stdout:
                return cmd
        except Exception:
            continue
            
    return None

def get_server_id_by_name(cmd_exec, search_term):
    """Finds server ID by partial name match."""
    try:
        # Add license flags to prevent hanging on fresh installs
        result = subprocess.run([cmd_exec, '--accept-license', '--accept-gdpr', '-L', '-f', 'json'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error listing servers: {result.stderr}")
            return None

        data = json.loads(result.stdout)
        servers = data.get('servers', [])

        for server in servers:
            if search_term.lower() in server['name'].lower() or \
               search_term.lower() in server['location'].lower() or \
               search_term.lower() in server['host'].lower():
                return server['id']
    except Exception as e:
        print(f"Error finding server by name: {e}")
    return None

def run_official_check_server(cmd_exec, search_term):
    """Uses official CLI to check for server availability."""
    print(f"[Official CLI] Searching for server containing '{search_term}'...")
    try:
        # Official CLI doesn't have a simple search-by-name flag easily accessible without running
        # But we can list servers (usually lists closest) and filter.
        # speedtest -L -f json
        # Add license flags to prevent hanging on fresh installs
        result = subprocess.run([cmd_exec, '--accept-license', '--accept-gdpr', '-L', '-f', 'json'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error listing servers: {result.stderr}")
            return

        try:
            # Output might be multiple JSON objects or a list depending on version
            # Usually 'servers' key contains list in JSON output
            data = json.loads(result.stdout)
            servers = data.get('servers', [])
            
            found = False
            for server in servers:
                if search_term.lower() in server['name'].lower() or \
                   search_term.lower() in server['location'].lower() or \
                   search_term.lower() in server['host'].lower():
                     print(f"Server Name: {server['name']} ({server['location']})")
                     print(f"Server URL:  {server['host']}")
                     print(f"Server ID:   {server['id']}")
                     found = True
            
            if not found:
                 print(f"Server '{search_term}' not found in official CLI local server list.")
                 print("Note: Official CLI also mainly lists geographically close servers.")

        except json.JSONDecodeError:
            print("Error parsing JSON output from speedtest CLI.")

    except Exception as e:
        print(f"An error occurred with official CLI: {e}")

def run_official_speedtest(cmd_exec, args):
    """Runs speedtest using official Ookla CLI."""
    print(f"Using Official Ookla speedtest CLI at: {cmd_exec}")
    # Add license acceptance flags to avoid interactive prompts
    cmd = [cmd_exec, '--accept-license', '--accept-gdpr', '-f', 'json']
    
    server_id = args.serverid
    if args.servername and not server_id:
        print(f"Resolving server ID for name '{args.servername}'...")
        server_id = get_server_id_by_name(cmd_exec, args.servername)
        if not server_id:
            print(f"Could not find server matching '{args.servername}'. Proceeding with auto-selection.")
        else:
            print(f"Found Server ID: {server_id}")

    if server_id:
        cmd.extend(['-s', str(server_id)])
        print(f"Using Server ID: {server_id}")

    print("Running speedtest...")
    try:
        # This can take a while
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Speedtest failed: {stderr}")
            return False

        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            print("Error: Invalid JSON output from speedtest CLI.")
            print(f"Output: {stdout}")
            return False
        
        # Extract data
        # Note: Official CLI JSON keys might differ slightly, usually:
        # download (bytes), upload (bytes), ping (latency), server{id, name, ...}
        
        download_mbps = data['download']['bandwidth'] * 8 / 1000000 
        upload_mbps = data['upload']['bandwidth'] * 8 / 1000000
        ping = data['ping']['latency']
        
        server_info = data.get('server', {})
        s_id = server_info.get('id', 'N/A')
        s_name = f"{server_info.get('name', 'Unknown')} ({server_info.get('location', '')})"

        print("\nResults:")
        print(f"Download Speed: {download_mbps:.2f} Mbps")
        print(f"Upload Speed: {upload_mbps:.2f} Mbps")
        print(f"Ping: {ping:.2f} ms")
        print(f"Server: {s_name} (ID: {s_id})")
        print(f"Result URL: {data.get('result', {}).get('url', 'N/A')}")

        log_results(download_mbps, upload_mbps, ping, s_id, s_name, args.logfile)
        return True

    except Exception as e:
        print(f"Error running official CLI: {e}")
        return False



def check_speed():
    args = get_args()
    
    # Try to find official CLI
    official_cmd = get_official_speedtest_command()

    if args.stats:
        avg_dl, avg_ul, avg_ping, count = calculate_averages()
        if avg_dl is not None:
             print("\nHistorical Statistics:")
             print(f"Total Tests Run: {count}")
             print(f"Avg Download:    {avg_dl:.2f} Mbps")
             print(f"Avg Upload:      {avg_ul:.2f} Mbps")
             print(f"Avg Ping:        {avg_ping:.2f} ms")
        else:
             print("No logs found or empty log file.")
        sys.exit(0)
    
    if official_cmd:
        if args.plot:
             if args.plot == 'text':
                 plot_results_text()
             else:
                 plot_results()
             sys.exit(0)
             
        if args.checkserver:

            search_term = args.checkserver.strip("'").strip('"')
            run_official_check_server(official_cmd, search_term)
        else:
            run_official_speedtest(official_cmd, args)
    else:
        print("Error: Official Ookla Speedtest CLI not found.")
        print("Please install it from: https://www.speedtest.net/apps/cli")
        sys.exit(1)
        
    # Always print averages at the end if log exists
    avg_dl, avg_ul, avg_ping = calculate_averages(args.logfile)
    avg_dl, avg_ul, avg_ping, count = calculate_averages()
    if avg_dl is not None:
        print("\nHistorical Averages (All Servers, {} tests):".format(count))
        print(f"Avg Download: {avg_dl:.2f} Mbps")
        print(f"Avg Upload: {avg_ul:.2f} Mbps")
        print(f"Avg Ping: {avg_ping:.2f} ms")

if __name__ == "__main__":
    check_speed()

