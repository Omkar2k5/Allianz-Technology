"""
Utility modules for the Eco-Compute SDK.

This package provides common utilities for hashing and system information.
"""

from eco_compute.utils.hash import generate_request_id, hash_request, short_hash
from eco_compute.utils.system import (
    get_computer_name,
    get_environment_variable,
    get_platform_info,
    get_process_id,
    get_process_name,
    get_user_name,
    get_working_directory,
)

__all__ = [
    "hash_request",
    "generate_request_id",
    "short_hash",
    "get_computer_name",
    "get_process_name",
    "get_platform_info",
    "get_process_id",
    "get_user_name",
    "get_working_directory",
    "get_environment_variable",
]
