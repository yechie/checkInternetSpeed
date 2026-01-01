#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import tempfile
from speed_utils import calculate_stats, generate_plot_image

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
        if self.path == '/stats':
            self.handle_stats_request()
        elif self.path == '/plot.png':
            self.handle_plot_request()
        elif self.path == '/':
            self._set_headers('text/html')
            self.wfile.write(b"""
                <html>
                <head><title>Speedtest Server</title></head>
                <body>
                    <h1>Welcome to the Speedtest Server!</h1>
                    <p>Check out your internet speed statistics:</p>
                    <ul>
                        <li><a href="/stats">Raw Statistics (JSON)</a></li>
                        <li><a href="/plot.png">Speed History Plot (PNG)</a></li>
                    </ul>
                </body>
                </html>
            """)

    def handle_stats_request(self):
        stats = calculate_stats(LOG_FILE)
        if stats:
            self._set_headers('application/json')
            self.wfile.write(json.dumps(stats, indent=4).encode('utf-8'))
        else:
            self._set_headers('application/json', status=404)
            self.wfile.write(json.dumps({"error": "No stats found or log file is empty/missing."} ).encode('utf-8'))

    def handle_plot_request(self):
        if generate_plot_image(LOG_FILE, TEMP_PLOT_FILE):
            if os.path.exists(TEMP_PLOT_FILE):
                self._set_headers('image/png')
                with open(TEMP_PLOT_FILE, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self._set_headers(status=500)
                self.wfile.write(b"Error generating plot image.")
        else:
            self._set_headers(status=500)
            self.wfile.write(b"Error generating plot or no data available.")

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
