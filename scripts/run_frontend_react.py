#!/usr/bin/env python3
"""
Run the React frontend for the chatbot application.

This script manages the React development server, handling
npm dependencies installation and starting the development server.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_node_npm():
    """Check if Node.js and npm are installed."""
    try:
        node_version = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Node.js found: {node_version.stdout.strip()}")
        
        npm_version = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ npm found: {npm_version.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js and npm are required to run the React frontend.")
        print("Please install Node.js from: https://nodejs.org/")
        return False

def install_dependencies(frontend_dir):
    """Install npm dependencies if needed."""
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print("📦 Installing npm dependencies...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                check=True
            )
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("✓ Dependencies already installed")
        return True

def start_react_server(frontend_dir):
    """Start the React development server."""
    print("\n" + "="*60)
    print("Starting React Frontend")
    print("="*60)
    print(f"Directory: {frontend_dir}")
    print("URL: http://localhost:3000")
    print("="*60)
    print()
    
    env = os.environ.copy()
    env["BROWSER"] = "none"  # Don't auto-open browser
    env["PORT"] = "3000"  # Ensure port 3000
    
    try:
        # Run npm start
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            env=env
        )
        
        print("🚀 React frontend is starting on http://localhost:3000")
        print("Press Ctrl+C to stop\n")
        
        process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down React frontend...")
        process.terminate()
        process.wait(timeout=5)
    except Exception as e:
        print(f"❌ Error running React frontend: {e}")
        return 1
    
    return 0

def main():
    """Main entry point."""
    # Get the frontend directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "src" / "frontend_react"
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        print("Please ensure the React frontend code is in src/frontend_react/")
        return 1
    
    # Check Node.js and npm
    if not check_node_npm():
        return 1
    
    # Install dependencies if needed
    if not install_dependencies(frontend_dir):
        return 1
    
    # Start the React server
    return start_react_server(frontend_dir)

if __name__ == "__main__":
    sys.exit(main())