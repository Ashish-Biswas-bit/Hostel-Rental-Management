import webview
import threading
import web_server  # Flask server

# Flask server run in a separate thread
def start_flask():
    web_server.app.run(port=5000)

t = threading.Thread(target=start_flask)
t.daemon = True
t.start()

# Open WebView window
webview.create_window("All Rent Ads", "http://127.0.0.1:5000")
webview.start()
