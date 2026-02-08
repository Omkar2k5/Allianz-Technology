"""
System information utilities.

This module provides platform-safe methods to collect system
information for telemetry and tracking purposes.
"""

import os
import platform
import sys
from typing import Optional


def get_computer_name() -> str:
    """
    Get the computer/hostname in a platform-safe manner.
    
    Returns:
        Computer name string, or 'unknown' if unavailable
    
    Example:
        >>> get_computer_name()
        'DESKTOP-ABC123'
    """
    try:
        # Try multiple methods for robustness
        name = platform.node()
        if name:
            return name
        
        # Fallback to environment variables
        for env_var in ("COMPUTERNAME", "HOSTNAME", "HOST"):
            name = os.environ.get(env_var)
            if name:
                return name
        
        return "unknown"
    except Exception:
        return "unknown"


def get_process_name() -> str:
    """
    Get the current process name.
    
    Returns:
        Process name string, or 'unknown' if unavailable
    
    Example:
        >>> get_process_name()
        'python'
    """
    try:
        # Get the executable name
        executable = sys.executable
        if executable:
            return os.path.basename(executable)
        
        # Fallback to argv
        if sys.argv and sys.argv[0]:
            return os.path.basename(sys.argv[0])
        
        return "python"
    except Exception:
        return "unknown"


def get_platform_info() -> dict:
    """
    Get detailed platform information.
    
    Returns:
        Dictionary containing platform details
    
    Example:
        >>> get_platform_info()
        {
            'system': 'Windows',
            'release': '10',
            'version': '10.0.19041',
            'machine': 'AMD64',
            'processor': 'Intel64 Family 6...',
            'python_version': '3.11.0'
        }
    """
    try:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    except Exception:
        return {
            "system": "unknown",
            "release": "unknown",
            "version": "unknown",
            "machine": "unknown",
            "processor": "unknown",
            "python_version": sys.version.split()[0] if sys.version else "unknown"
        }


def get_process_id() -> int:
    """
    Get the current process ID.
    
    Returns:
        Process ID as integer
    """
    return os.getpid()


def get_user_name() -> Optional[str]:
    """
    Get the current user name in a platform-safe manner.
    
    Returns:
        User name string, or None if unavailable
    """
    try:
        # Try getpass first
        import getpass
        return getpass.getuser()
    except Exception:
        pass
    
    # Fallback to environment variables
    for env_var in ("USER", "USERNAME", "LOGNAME"):
        user = os.environ.get(env_var)
        if user:
            return user
    
    return None


def get_working_directory() -> str:
    """
    Get the current working directory.
    
    Returns:
        Current working directory path
    """
    try:
        return os.getcwd()
    except Exception:
        return "unknown"


def get_environment_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely get an environment variable.
    
    Args:
        name: Environment variable name
        default: Default value if not found
    
    Returns:
        Environment variable value or default
    """
    return os.environ.get(name, default)
