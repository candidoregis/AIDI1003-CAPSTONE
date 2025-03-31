#!/usr/bin/env python
"""
HR Recruitment Services Launcher

This script starts all backend services needed for the HR Recruitment Frontend:
1. Main API service (for resume generation, analysis, etc.)
2. Voice search service

Both services run concurrently in separate processes, allowing all features
to be available simultaneously without delay.
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("HR-Services")

# Global variables
processes = []
running = True

def signal_handler(sig, frame):
    """Handle termination signals to gracefully shut down all services."""
    global running
    logger.info("Shutting down all services...")
    running = False
    stop_all_services()
    sys.exit(0)

def start_main_api(port=5003):
    """Start the main API service for resume generation and analysis."""
    try:
        logger.info(f"Starting main API service on port {port}...")
        
        # Get the absolute path to the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set environment variables for the main API
        env = os.environ.copy()
        env["FLASK_APP"] = "api/app.py"
        env["FLASK_ENV"] = "development"
        env["PORT"] = str(port)
        
        # Start the Flask app
        cmd = [sys.executable, "api/app.py"]
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        logger.info(f"Main API service started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start main API service: {e}")
        return None

def start_voice_search_api(port=5004):
    """Start the voice search API service."""
    try:
        logger.info(f"Starting voice search API service on port {port}...")
        
        # Get the absolute path to the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create a modified version of app.py for the voice search service
        voice_app_path = os.path.join(backend_dir, "api/voice_app.py")
        with open(os.path.join(backend_dir, "api/app.py"), "r") as f:
            app_content = f.read()
        
        # Modify the port in the app content
        app_content = app_content.replace(
            "app.run(debug=True, host='0.0.0.0', port=5001)",
            f"app.run(debug=True, host='0.0.0.0', port={port})"
        )
        
        # Write the modified content to voice_app.py
        with open(voice_app_path, "w") as f:
            f.write(app_content)
        
        # Set environment variables for the voice search API
        env = os.environ.copy()
        env["FLASK_APP"] = "api/voice_app.py"
        env["FLASK_ENV"] = "development"
        env["PORT"] = str(port)
        
        # Start the Flask app
        cmd = [sys.executable, "api/voice_app.py"]
        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        logger.info(f"Voice search API service started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start voice search API service: {e}")
        return None

def monitor_process_output(process, service_name):
    """Monitor and log the output of a process."""
    while running and process.poll() is None:
        try:
            # Read stdout
            stdout_line = process.stdout.readline()
            if stdout_line:
                logger.info(f"[{service_name}] {stdout_line.strip()}")
            
            # Read stderr
            stderr_line = process.stderr.readline()
            if stderr_line:
                logger.error(f"[{service_name}] {stderr_line.strip()}")
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error monitoring {service_name}: {e}")
            break

def stop_all_services():
    """Stop all running services."""
    global processes
    for process in processes:
        if process and process.poll() is None:
            logger.info(f"Terminating process with PID {process.pid}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {process.pid} did not terminate gracefully, killing...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping process {process.pid}: {e}")

def main():
    """Main function to start all services."""
    parser = argparse.ArgumentParser(description="Start HR Recruitment Backend Services")
    parser.add_argument("--main-port", type=int, default=5003, help="Port for the main API service")
    parser.add_argument("--voice-port", type=int, default=5004, help="Port for the voice search API service")
    args = parser.parse_args()
    
    global processes, running
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the main API service
        main_api_process = start_main_api(port=args.main_port)
        if main_api_process:
            processes.append(main_api_process)
            
            # Start monitoring the main API output in a separate thread
            main_monitor = threading.Thread(target=monitor_process_output, args=(main_api_process, "Main API"))
            main_monitor.daemon = True
            main_monitor.start()
        
        # Start the voice search API service
        voice_api_process = start_voice_search_api(port=args.voice_port)
        if voice_api_process:
            processes.append(voice_api_process)
            
            # Start monitoring the voice API output in a separate thread
            voice_monitor = threading.Thread(target=monitor_process_output, args=(voice_api_process, "Voice API"))
            voice_monitor.daemon = True
            voice_monitor.start()
        
        # Print service information
        if main_api_process and voice_api_process:
            logger.info("=" * 50)
            logger.info("HR Recruitment Services started successfully!")
            logger.info(f"Main API running at: http://localhost:{args.main_port}")
            logger.info(f"Voice Search API running at: http://localhost:{args.voice_port}")
            logger.info("Press Ctrl+C to stop all services")
            logger.info("=" * 50)
        
        # Keep the main process running
        while running:
            # Check if any process has terminated
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    exit_code = process.poll()
                    service_name = "Main API" if i == 0 else "Voice API"
                    logger.error(f"{service_name} process terminated with exit code {exit_code}")
                    running = False
                    break
            
            # Sleep to prevent high CPU usage
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        stop_all_services()

if __name__ == "__main__":
    main()
