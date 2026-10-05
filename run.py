"""
Convenience launcher script to run the Streamlit app with standard Python.
Run:
    python run.py
"""

import sys
import subprocess
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    print(f"Launching Streamlit application from: {app_path}")
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    subprocess.run(cmd)
