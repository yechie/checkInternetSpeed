import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_plot_data(log_file, days=30):
    if not os.path.exists(log_file):
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
        with open(log_file, 'r') as f:
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

def calculate_stats(log_file):
    if not os.path.exists(log_file):
        return None

    total_download = 0.0
    total_upload = 0.0
    total_ping = 0.0
    count = 0
    
    min_download = float('inf')
    max_download = 0.0
    min_upload = float('inf')
    max_upload = 0.0

    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    parts = line.strip().split(',')
                    # Ensure we have at least the basic speed data (timestamp, dl, ul, ping)
                    if len(parts) >= 4:
                        download_speed = float(parts[1])
                        upload_speed = float(parts[2])
                        
                        total_download += download_speed
                        total_upload += upload_speed
                        total_ping += float(parts[3])
                        count += 1
                        
                        min_download = min(min_download, download_speed)
                        max_download = max(max_download, download_speed)
                        min_upload = min(min_upload, upload_speed)
                        max_upload = max(max_upload, upload_speed)
                        
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None

    if count == 0:
        return None

    return {
        'avg_dl': total_download / count,
        'avg_ul': total_upload / count,
        'avg_ping': total_ping / count,
        'count': count,
        'min_dl': min_download,
        'max_dl': max_download,
        'min_ul': min_upload,
        'max_ul': max_upload,
    }

def generate_plot_image(log_file, output_path, days=30):
    data = get_plot_data(log_file, days)
    if not data:
        print("No log file found or no data for plotting.")
        return False

    dates = data['dates']
    downloads = data['downloads']
    uploads = data['uploads']
    avg_downloads = data['avg_downloads']
    avg_uploads = data['avg_uploads']

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color_dl = 'tab:blue'
    color_ul = 'tab:orange'
    
    ax1.set_xlabel('Date and Time')
    ax1.set_ylabel('Measured Speed (Mbps)', color='black')
    
    l1, = ax1.plot(dates, downloads, color=color_dl, label='Measured Download', alpha=0.6)
    l2, = ax1.plot(dates, uploads, color=color_ul, label='Measured Upload', alpha=0.6)
    
    ax1.tick_params(axis='y', labelcolor='black')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Historical Average Speed (Mbps)', color='black')
    
    l3, = ax2.plot(dates, avg_downloads, color=color_dl, linestyle='--', label='Avg Download (Cumulative)', linewidth=2)
    l4, = ax2.plot(dates, avg_uploads, color=color_ul, linestyle='--', label='Avg Upload (Cumulative)', linewidth=2)
    
    ax2.tick_params(axis='y', labelcolor='black')

    plt.title('Internet Speed History (Last {} Days)'.format(days))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()
    
    lines = [l1, l2, l3, l4]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.grid(True)
    plt.tight_layout()
    
    try:
        plt.savefig(output_path)
        plt.close(fig) # Close the figure to free up memory
        return True
    except Exception as e:
        print(f"Error saving plot to {output_path}: {e}")
        return False

def get_latest_speedtest(log_file):
    if not os.path.exists(log_file):
        return None

    try:
        with open(log_file, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()

            parts = last_line.strip().split(',')
            
            if len(parts) >= 6:
                return {
                    'timestamp': parts[0],
                    'download': float(parts[1]),
                    'upload': float(parts[2]),
                    'ping': float(parts[3]),
                    'server_id': parts[4],
                    'server_name': parts[5]
                }
    except Exception as e:
        print(f"Error reading latest speedtest from log file: {e}")
        return None
    
    return None