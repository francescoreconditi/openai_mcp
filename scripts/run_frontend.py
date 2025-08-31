import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    frontend_path = Path(__file__).parent.parent / "src" / "frontend" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(frontend_path)])