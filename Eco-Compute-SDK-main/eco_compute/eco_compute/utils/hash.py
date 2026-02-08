"""
Request hashing utilities for audit trails.

This module provides deterministic hashing of LLM requests
for tracking, deduplication, and audit purposes.
"""

import hashlib
import json
from typing import Any, Dict, Optional


def hash_request(
    prompt: str,
    config: Optional[Dict[str, Any]] = None,
    algorithm: str = "sha256"
) -> str:
    """
    Generate a deterministic hash of an LLM request.
    
    Creates a consistent hash from the prompt and configuration
    for audit trails, deduplication detection, and tracking.
    
    Args:
        prompt: The input prompt to the LLM
        config: Optional configuration dictionary
        algorithm: Hash algorithm to use (default: sha256)
    
    Returns:
        Hexadecimal hash string
    
    Example:
        >>> hash_request("Hello, world!")
        'a591a6d40b...'
        
        >>> hash_request("Hello", {"model": "gpt-4"})
        'f8b3c7e2...'
    """
    # Build canonical representation
    canonical_data: Dict[str, Any] = {
        "prompt": prompt,
        "config": _normalize_config(config) if config else {}
    }
    
    # Convert to deterministic JSON string
    # sort_keys ensures consistent ordering
    json_str = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
    
    # Hash the string
    hasher = hashlib.new(algorithm)
    hasher.update(json_str.encode("utf-8"))
    
    return hasher.hexdigest()


def _normalize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize configuration for consistent hashing.
    
    Removes non-deterministic fields and normalizes values
    to ensure consistent hashing across requests.
    
    Args:
        config: Raw configuration dictionary
    
    Returns:
        Normalized configuration dictionary
    """
    # Fields to exclude from hashing (non-deterministic or sensitive)
    excluded_fields = {
        "api_key",
        "telemetry_token",
        "timestamp",
        "request_id",
        "_internal"
    }
    
    normalized: Dict[str, Any] = {}
    
    for key, value in sorted(config.items()):
        # Skip excluded fields
        if key.lower() in excluded_fields:
            continue
        
        # Normalize the value
        if isinstance(value, dict):
            normalized[key] = _normalize_config(value)
        elif isinstance(value, (list, tuple)):
            normalized[key] = _normalize_list(list(value))
        elif isinstance(value, float):
            # Round floats to avoid precision issues
            normalized[key] = round(value, 10)
        else:
            normalized[key] = value
    
    return normalized


def _normalize_list(items: list) -> list:
    """
    Normalize a list for consistent hashing.
    
    Args:
        items: List of items to normalize
    
    Returns:
        Normalized list
    """
    normalized = []
    for item in items:
        if isinstance(item, dict):
            normalized.append(_normalize_config(item))
        elif isinstance(item, (list, tuple)):
            normalized.append(_normalize_list(list(item)))
        elif isinstance(item, float):
            normalized.append(round(item, 10))
        else:
            normalized.append(item)
    return normalized


def generate_request_id() -> str:
    """
    Generate a unique request ID.
    
    Creates a UUID-based identifier for tracking individual requests.
    
    Returns:
        Unique request ID string
    """
    import uuid
    return str(uuid.uuid4())


def short_hash(data: str, length: int = 8) -> str:
    """
    Generate a short hash for display purposes.
    
    Args:
        data: String to hash
        length: Length of the short hash (default: 8)
    
    Returns:
        Short hash string
    """
    full_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
    return full_hash[:length]
