"""
MCP Server Manager
Manages the lifecycle of the MCP server process
"""
import subprocess
import time
import logging
import signal
import os
from pathlib import Path
from typing import Optional
import psutil

logger = logging.getLogger(__name__)


class MCPServerManager:
    """
    Manages MCP server process lifecycle.
    Handles starting, stopping, health checks, and recovery.
    """
    
    def __init__(self, server_path: Path, python_executable: str = "python"):
        """
        Initialize server manager.
        
        Args:
            server_path: Path to server.py
            python_executable: Python executable to use
        """
        self.server_path = server_path
        self.python_executable = python_executable
        self.process: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None
    
    def start(self, timeout: int = 10) -> bool:
        """
        Start the MCP server process.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            True if started successfully
        """
        if self.is_running():
            logger.info("MCP server is already running")
            return True
        
        try:
            logger.info(f"Starting MCP server: {self.server_path}")
            
            # Start server process with stdio transport
            self.process = subprocess.Popen(
                [self.python_executable, str(self.server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,  # Binary mode for MCP protocol
                bufsize=0    # Unbuffered
            )
            
            self._start_time = time.time()
            
            # Wait a moment for server to initialize
            time.sleep(2)
            
            if self.is_running():
                logger.info(f"MCP server started successfully (PID: {self.process.pid})")
                return True
            else:
                # Read stderr to see what went wrong
                if self.process and self.process.stderr:
                    try:
                        error_output = self.process.stderr.read().decode('utf-8', errors='ignore')
                        if error_output:
                            logger.error(f"MCP server stderr: {error_output}")
                    except:
                        pass
                logger.error("MCP server process died immediately after start")
                return False
        
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def stop(self, timeout: int = 5) -> bool:
        """
        Stop the MCP server process gracefully.
        
        Args:
            timeout: Timeout for graceful shutdown
            
        Returns:
            True if stopped successfully
        """
        if not self.process:
            logger.info("No MCP server process to stop")
            return True
        
        try:
            logger.info(f"Stopping MCP server (PID: {self.process.pid})")
            
            # Try graceful shutdown first
            self.process.terminate()
            
            try:
                self.process.wait(timeout=timeout)
                logger.info("MCP server stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                logger.warning("MCP server not responding, forcing kill")
                self.process.kill()
                self.process.wait()
            
            self.process = None
            self._start_time = None
            return True
        
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}")
            return False
    
    def restart(self, timeout: int = 10) -> bool:
        """
        Restart the MCP server.
        
        Args:
            timeout: Timeout for start/stop operations
            
        Returns:
            True if restarted successfully
        """
        logger.info("Restarting MCP server")
        self.stop(timeout=timeout)
        time.sleep(1)
        return self.start(timeout=timeout)
    
    def is_running(self) -> bool:
        """
        Check if server process is running.
        
        Returns:
            True if running
        """
        if not self.process:
            return False
        
        # Check if process is still alive
        poll_result = self.process.poll()
        if poll_result is not None:
            # Process has terminated
            logger.warning(f"MCP server process terminated with code {poll_result}")
            return False
        
        return True
    
    def get_health_status(self) -> dict:
        """
        Get server health status.
        
        Returns:
            Dict with status information
        """
        if not self.is_running():
            return {
                'running': False,
                'uptime': 0,
                'pid': None
            }
        
        uptime = time.time() - self._start_time if self._start_time else 0
        
        # Try to get process info
        try:
            process = psutil.Process(self.process.pid)
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent(interval=0.1)
            
            return {
                'running': True,
                'uptime': uptime,
                'pid': self.process.pid,
                'memory_mb': memory_info.rss / 1024 / 1024,
                'cpu_percent': cpu_percent
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {
                'running': True,
                'uptime': uptime,
                'pid': self.process.pid
            }
    
    def __del__(self):
        """Cleanup: stop server when manager is destroyed"""
        if self.process:
            try:
                self.stop()
            except:
                pass
