# app.py
import http.server
import socketserver
import json
import threading
import time
import webbrowser
from urllib.parse import parse_qs
import requests

from database import DatabaseManager
from api_client import fetch_rank_data

# --- Configuration ---
PORT = 8000
DB_FILE = 'valorant_accounts.db'
REFRESH_INTERVAL_SECONDS = 60

# --- Background Task for Refreshing Ranks ---
def refresh_all_accounts(db: DatabaseManager, stop_event: threading.Event):
    """Fetches the latest rank for all saved accounts."""
    print(f"\n[{time.strftime('%H:%M:%S')}] Starting background refresh of all saved accounts...")
    accounts = db.get_all_accounts()

    if not accounts:
        print(f"[{time.strftime('%H:%M:%S')}] No saved accounts to refresh.")
        return

    for account in accounts:
        if stop_event.is_set():
            break
        try:
            rank, rr = fetch_rank_data(account['username'], account['hashtag'], account['region'])
            if rank is not None:
                db.update_account_rank(account['username'], account['hashtag'], account['region'], rank, rr)
                print(f"  - Refreshed: {account['username']}#{account['hashtag']} -> {rank} {rr}RR")
        except requests.exceptions.RequestException as e:
            print(f"  - Could not refresh {account['username']}#{account['hashtag']}: {e}")
        time.sleep(1)  # Small delay to avoid overwhelming the API
    
    print(f"[{time.strftime('%H:%M:%S')}] Background refresh complete.")

def schedule_periodic_refresh(db: DatabaseManager, stop_event: threading.Event):
    """Runs the refresh function periodically."""
    while not stop_event.is_set():
        refresh_all_accounts(db, stop_event)
        stop_event.wait(REFRESH_INTERVAL_SECONDS)

# --- HTTP Request Handler ---
class ValorantRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler to serve API endpoints and static files."""

    def __init__(self, *args, **kwargs):
        self.db = DatabaseManager(DB_FILE)
        super().__init__(*args, directory='static', **kwargs)

    def do_GET(self):
        """Handle GET requests for API endpoints or static files."""
        if self.path == '/get_accounts':
            self.handle_get_accounts()
        elif self.path == '/get_sections':
            self.handle_get_sections()
        else:
            # Serve '/' as index.html, otherwise serve files from the 'static' directory
            self.path = '/index.html' if self.path == '/' else self.path
            super().do_GET()

    def do_POST(self):
        """Handle POST requests for actions like check, save, delete, etc."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            action = params.get('action', [''])[0]

            action_map = {
                'check': self.handle_check_rank,
                'save': self.handle_save_account,
                'delete': self.handle_delete_account,
                'create_section': self.handle_create_section,
                'delete_section': self.handle_delete_section,
            }

            handler_func = action_map.get(action)
            if handler_func:
                handler_func(params)
            else:
                self.send_json_response({"error": "Unknown action"}, status_code=400)
        except Exception as e:
            self.send_json_response({"error": f"Server error: {e}"}, status_code=500)

    # --- GET Handlers ---
    def handle_get_accounts(self):
        accounts = self.db.get_all_accounts()
        accounts_by_section = {}
        for acc in accounts:
            section = acc.get('section', 'Default')
            if section not in accounts_by_section:
                accounts_by_section[section] = []
            accounts_by_section[section].append(acc)
        self.send_json_response(accounts_by_section)

    def handle_get_sections(self):
        sections = self.db.get_sections()
        self.send_json_response(sections)

    # --- POST Handlers ---
    def handle_check_rank(self, params):
        username = params.get('username', [''])[0]
        hashtag = params.get('hashtag', [''])[0]
        region = params.get('region', ['na'])[0]
        try:
            rank, rr = fetch_rank_data(username, hashtag, region)
            if rank is not None:
                result = {"playerName": f"{username}#{hashtag}", "rank": rank, "rr": rr}
                self.send_json_response(result)
            else:
                self.send_json_response({"error": "Could not parse rank data."}, status_code=500)
        except requests.exceptions.HTTPError as e:
            self.send_json_response({"error": f"API Error (Status: {e.response.status_code}). Player may not exist."}, status_code=404)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status_code=500)

    def handle_save_account(self, params):
        try:
            account_data = {
                'username': params.get('username', [''])[0],
                'hashtag': params.get('hashtag', [''])[0],
                'region': params.get('region', ['na'])[0],
                'account_username': params.get('account_username', [''])[0],
                'password': params.get('password', [''])[0],
                'section': params.get('section', ['Default'])[0]
            }
            if not account_data['username'] or not account_data['hashtag']:
                self.send_json_response({"success": False, "error": "In-game Name and Hashtag are required."}, status_code=400)
                return
            
            # Fetch current rank before saving
            rank, rr = fetch_rank_data(account_data['username'], account_data['hashtag'], account_data['region'])
            account_data['rank'] = rank
            account_data['rr'] = rr

            self.db.save_account(account_data)
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"success": False, "error": str(e)}, status_code=500)
            
    def handle_delete_account(self, params):
        username = params.get('username', [''])[0]
        hashtag = params.get('hashtag', [''])[0]
        region = params.get('region', ['na'])[0]
        self.db.delete_account(username, hashtag, region)
        self.send_json_response({"success": True})
        
    def handle_create_section(self, params):
        section_name = params.get('section_name', [''])[0]
        if not section_name:
            self.send_json_response({"success": False, "error": "Section name cannot be empty."}, status_code=400)
            return
        self.db.create_section(section_name)
        self.send_json_response({"success": True})

    def handle_delete_section(self, params):
        section_name = params.get('section_name', [''])[0]
        if not section_name or section_name == 'Default':
            self.send_json_response({"success": False, "error": "Cannot delete the Default section."}, status_code=400)
            return
        self.db.delete_section(section_name)
        self.send_json_response({"success": True})
        
    # --- Utility ---
    def send_json_response(self, data, status_code=200):
        """Sends a JSON response."""
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


# --- Main Server Execution ---
def run_server(port: int):
    """Sets up the database, starts the background refresh thread, and runs the web server."""
    db_manager = DatabaseManager(DB_FILE)
    db_manager.setup()
    
    stop_event = threading.Event()
    refresh_thread = threading.Thread(
        target=schedule_periodic_refresh, 
        args=(db_manager, stop_event), 
        daemon=True
    )
    refresh_thread.start()
    
    server_address = ("", port)
    with socketserver.TCPServer(server_address, ValorantRequestHandler) as httpd:
        print("--- Valorant Rank Checker is Running ---")
        print(f"Access it on this computer: http://localhost:{port}")
        print(f"Ranks will be refreshed automatically every {REFRESH_INTERVAL_SECONDS} seconds.")
        print("----------------------------------------")
        print("Press Ctrl+C to stop the server.")
        
        webbrowser.open(f"http://localhost:{port}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            print("\nServer is shutting down...")
            stop_event.set()
            refresh_thread.join() # Wait for the refresh thread to finish
            httpd.server_close()
            print("Server stopped.")

if __name__ == "__main__":
    run_server(PORT)