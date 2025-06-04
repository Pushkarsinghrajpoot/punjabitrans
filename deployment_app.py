import streamlit.web.bootstrap as bootstrap
import os
import sys
import socket

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = False
    try:
        sock.bind(("0.0.0.0", port))
        result = True
    except:
        pass
    finally:
        sock.close()
    return result

def main():
    """
    Custom entrypoint for deployment environments that expect port 8501
    """
    # Try ports in sequence until we find an available one
    available_port = None
    ports_to_try = [8501, 8502, 8503, 8504, 8505]
    
    for port in ports_to_try:
        if check_port(port):
            available_port = port
            print(f"Found available port: {port}")
            break
    
    if available_port is None:
        print("❌ No available ports found in range 8501-8505. Please free up a port and try again.")
        sys.exit(1)
    
    port = available_port
    
    # Set environment variables that Streamlit will use
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_SERVER_ENABLECORS"] = "true"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"  # Listen on all interfaces
    
    # Bootstrap the Streamlit application
    bootstrap.load_config_options(flag_options={
        "server.port": port,
        "server.address": "0.0.0.0",
        "browser.serverAddress": "localhost",
        "browser.serverPort": port
    })
    
    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # Path to the main application file
    main_script_path = os.path.join(dir_path, "app.py")
    
    # Run the Streamlit application
    bootstrap.run(main_script_path, "", [], [])

if __name__ == "__main__":
    main()
