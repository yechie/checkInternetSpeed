#!/usr/bin/env python3

import argparse
import datetime
import os
import subprocess
import json
import sys
import shutil

LOG_FILE = 'speed_log.txt'

def get_args():
    parser = argparse.ArgumentParser(description='Check internet speed')
    parser.add_argument('--serverid', type=int, help='Preferred server ID')
    parser.add_argument('--servername', type=str, help='Preferred server name (partial match)')
    parser.add_argument('--checkserver', type=str, help='Check server availability by name and return details')
    return parser.parse_args()

def log_results(download, upload, ping, server_id, server_name):
    timestamp = datetime.datetime.now().isoformat()
    # Sanitize server name to remove commas if any, to avoid CSV issues
    server_name = str(server_name).replace(',', ' ')
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp},{download},{upload},{ping},{server_id},{server_name}\n")

def calculate_averages():
    if not os.path.exists(LOG_FILE):
        return None, None, None

    total_download = 0.0
    total_upload = 0.0
    total_ping = 0.0
    count = 0

    try:
        with open(LOG_FILE, 'r') as f:
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
        return None, None, None

    if count == 0:
        return None, None, None

    return total_download / count, total_upload / count, total_ping / count

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

def run_official_check_server(cmd_exec, search_term):
    """Uses official CLI to check for server availability."""
    print(f"[Official CLI] Searching for server containing '{search_term}'...")
    try:
        # Official CLI doesn't have a simple search-by-name flag easily accessible without running
        # But we can list servers (usually lists closest) and filter.
        # speedtest -L -f json
        result = subprocess.run([cmd_exec, '-L', '-f', 'json'], capture_output=True, text=True)
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
    
    if args.serverid:
        cmd.extend(['-s', str(args.serverid)])
        print(f"Using Server ID: {args.serverid}")
    
    # Selecting by name is tricky in CLI directly without pre-resolving ID
    # We will skip direct name selection in CLI execution for now, or warn user.
    if args.servername:
        print("Warning: --servername is not directly supported in CLI mode execution (requires ID).")
        print("Please use --checkserver to find the ID first, or use --serverid.")
        # Proceeding with auto-server selection if ID not provided

    print("Running speedtest...")
    try:
        # This can take a while
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Speedtest failed: {stderr}")
            return

        data = json.loads(stdout)
        
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

        log_results(download_mbps, upload_mbps, ping, s_id, s_name)
        return True

    except Exception as e:
        print(f"Error running official CLI: {e}")
        return False



def check_speed():
    args = get_args()
    
    # Try to find official CLI
    official_cmd = get_official_speedtest_command()
    
    if official_cmd:
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
    avg_dl, avg_ul, avg_ping = calculate_averages()
    if avg_dl is not None:
        print("\nHistorical Averages (All Servers):")
        print(f"Avg Download: {avg_dl:.2f} Mbps")
        print(f"Avg Upload: {avg_ul:.2f} Mbps")
        print(f"Avg Ping: {avg_ping:.2f} ms")

if __name__ == "__main__":
    check_speed()
