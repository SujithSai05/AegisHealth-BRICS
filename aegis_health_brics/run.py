"""
AegisHealth BRICS - One-Click Launcher.
Starts the FastAPI application server and opens the Command Dashboard.
"""
import sys
import os
import time
import webbrowser
import uvicorn

# Ensure the project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    url = f"http://{host}:{port}"

    print("=" * 75)
    print("🛡️  AegisHealth BRICS — Smart Health & Supply Chain Resilience Platform")
    print("   Track 3: Smart Health & Supply Chain Resilience (BRICS Theme: Resilience)")
    print("=" * 75)
    print(f"[*] Starting server on {url} ...")
    print(f"[*] Web Command Dashboard: {url}")
    print(f"[*] Interactive API Docs (Swagger): {url}/docs")
    print(f"[*] ReDoc Documentation: {url}/redoc")
    print("=" * 75)

    # Optional: open browser after brief delay
    if os.environ.get("NO_BROWSER") != "1":
        def open_browser():
            time.sleep(1.2)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("aegis.main:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
