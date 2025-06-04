import subprocess
import os
import sys
import time

def start_streamlit():
    """
    Start the Streamlit application on a specific port
    with proper retry mechanism if default port is busy.
    """
    print("Starting Punjabi Translator Streamlit App...")
    
    # List of ports to try
    ports = [8501, 8502, 8503, 8504, 8505]
    
    for port in ports:
        try:
            print(f"Attempting to start on port {port}...")
            
            # Build the command to execute streamlit
            cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port)]
            
            # Start the process
            process = subprocess.Popen(cmd, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if the process is still running
            if process.poll() is None:
                print(f"✅ Streamlit app successfully started on port {port}")
                print(f"Open your browser to: http://localhost:{port}")
                
                # Keep the script running while streamlit is running
                while process.poll() is None:
                    time.sleep(1)
                
                # If we get here, the process has ended
                return
            else:
                stdout, stderr = process.communicate()
                if "Address already in use" in stderr or "Port is already in use" in stderr:
                    print(f"Port {port} is already in use, trying next port...")
                else:
                    print(f"Error starting Streamlit: {stderr}")
                    return
        except Exception as e:
            print(f"Error: {e}")
    
    print("❌ Failed to start Streamlit app after trying all ports.")
    print("Please check if you have multiple instances already running.")

if __name__ == "__main__":
    start_streamlit()
