#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import tempfile
import base64
from speed_utils import calculate_stats, generate_plot_image, get_latest_speedtest

# Configuration
HOST = '0.0.0.0'
PORT = 8000
LOG_FILE = 'speed_log.txt' # Make sure this matches the log file used by check_speed.py
TEMP_PLOT_FILE = os.path.join(tempfile.gettempdir(), 'speed_plot.png')

class SpeedHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='text/html', status=200):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.handle_main_page_request()
        else:
            self._set_headers(status=404)
            self.wfile.write(b"404 Not Found")

    def handle_main_page_request(self):
        stats = calculate_stats(LOG_FILE)
        latest_test = get_latest_speedtest(LOG_FILE)
        
        plot_base64 = None
        if generate_plot_image(LOG_FILE, TEMP_PLOT_FILE):
            if os.path.exists(TEMP_PLOT_FILE):
                with open(TEMP_PLOT_FILE, 'rb') as f:
                    plot_base64 = base64.b64encode(f.read()).decode('utf-8')

        html = self._generate_html(stats, latest_test, plot_base64)
        self._set_headers('text/html')
        self.wfile.write(html.encode('utf-8'))

    def _generate_html(self, stats, latest_test, plot_base64):
        css = """
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; background-color: #f0f2f5; color: #1c1e21; }
    .header { background-color: #fff; padding: 20px 40px; border-bottom: 1px solid #dddfe2; text-align: center; }
    .header h1 { color: #0056b3; margin: 0; font-size: 2rem; }
    .container { padding: 40px; }
    .stats-container { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-bottom: 40px; }
    .stat-tile { background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 25px; text-align: center; flex: 1 1 200px; min-width: 200px; transition: transform 0.2s; }
    .stat-tile:hover { transform: translateY(-5px); }
    .stat-tile h3 { margin: 0 0 15px; color: #606770; font-size: 1rem; font-weight: 600; }
    .stat-tile .value { font-size: 2.5rem; margin: 0; color: #0056b3; font-weight: 700; }
    .stat-tile .unit { font-size: 1rem; color: #606770; }
    .plot-container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
    .plot-container h2 { color: #0056b3; margin-top: 0; }
    h2 { text-align: center; color: #0056b3; margin-top: 40px; }
    img { max-width: 100%; height: auto; }
</style>
"""
        
        html_content = f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>Internet Speed Statistics</title>{css}</head><body>"
        html_content += "<div class='header'><h1>Internet Speed Statistics</h1></div>"
        html_content += "<div class='container'>"

        if stats:
            html_content += "<h2>Historical Averages</h2>"
            html_content += "<div class='stats-container'>"
            
            def tile(title, value, unit):
                return f'''
                <div class='stat-tile'>
                    <h3>{title}</h3>
                    <p class='value'>{value}</p>
                    <span class='unit'>{unit}</span>
                </div>
                '''
            
            html_content += tile("Avg Download", f"{stats.get('avg_dl', 0):.2f}", "Mbps")
            html_content += tile("Avg Upload", f"{stats.get('avg_ul', 0):.2f}", "Mbps")
            html_content += tile("Avg Ping", f"{stats.get('avg_ping', 0):.2f}", "ms")
            html_content += tile("Total Tests", stats.get('count', 0), "")
            html_content += tile("Highest Download", f"{stats.get('max_dl', 0):.2f}", "Mbps")
            html_content += tile("Highest Upload", f"{stats.get('max_ul', 0):.2f}", "Mbps")
            
            html_content += "</div>"
        else:
            html_content += "<p>No statistics available yet.</p>"
        
        if latest_test:
            html_content += "<h2>Latest Speed Test</h2>"
            html_content += "<div class='stats-container'>"
            html_content += tile("Download", f"{latest_test.get('download', 0):.2f}", "Mbps")
            html_content += tile("Upload", f"{latest_test.get('upload', 0):.2f}", "Mbps")
            html_content += tile("Ping", f"{latest_test.get('ping', 0):.2f}", "ms")
            html_content += f"<div class='stat-tile'><h3>Server</h3><p class='value' style='font-size: 1rem; white-space: normal; word-break: break-all;'>{latest_test.get('server_name', 'N/A')}</p></div>"
            html_content += "</div>"

        if plot_base64:
            html_content += "<div class='plot-container'>"
            html_content += "<h2>Speed History Plot</h2>"
            html_content += f"<img src='data:image/png;base64,{plot_base64}' alt='Internet speed history plot'>"
            html_content += "</div>"
        else:
            html_content += "<div class='plot-container'><p>Could not generate plot. Run a speed test to generate data.</p></div>"
        
        html_content += "</div></body></html>"
        return html_content

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, SpeedHTTPRequestHandler)
    print(f"Starting httpd server on {HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping httpd server.")
        httpd.shutdown()
        
if __name__ == '__main__':
    run_server()