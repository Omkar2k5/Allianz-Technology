"""
Asynchronous telemetry sender for the Eco-Compute SDK.

This module handles sending telemetry data to a configurable backend
endpoint in a non-blocking manner. The SDK never crashes the host
application due to telemetry failures.

Features:
- Non-blocking async HTTP POST
- Bearer token authentication
- Graceful failure handling
- Batch-ready design for future optimization
"""

import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

import requests

from eco_compute.types import TelemetryRecord

# Module logger
logger = logging.getLogger("eco_compute.telemetry")


@dataclass
class TelemetrySenderConfig:
    """
    Configuration for the telemetry sender.
    
    Attributes:
        endpoint: URL to send telemetry data to
        token: Bearer token for authentication
        enabled: Whether telemetry is enabled
        fail_silently: Whether to suppress errors
        timeout_seconds: HTTP request timeout
        max_retries: Maximum number of retry attempts
        retry_delay_seconds: Delay between retries
        batch_size: Number of records to batch
        batch_timeout_seconds: Max time to wait before sending batch
        max_queue_size: Maximum queue size before dropping
    """
    
    endpoint: Optional[str] = None
    token: Optional[str] = None
    enabled: bool = True
    fail_silently: bool = True
    timeout_seconds: float = 10.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    batch_size: int = 10
    batch_timeout_seconds: float = 30.0
    max_queue_size: int = 1000


class TelemetrySender:
    """
    Non-blocking telemetry sender with async execution.
    
    Sends telemetry records to a configured endpoint using background
    threads. All operations are designed to never crash the host app.
    
    Example:
        >>> sender = TelemetrySender(TelemetrySenderConfig(
        ...     endpoint="https://telemetry.example.com/v1/records",
        ...     token="your-api-token"
        ... ))
        >>> sender.send(telemetry_record)
        >>> sender.shutdown()
    """
    
    def __init__(
        self,
        config: TelemetrySenderConfig,
        on_success: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        Initialize the telemetry sender.
        
        Args:
            config: Sender configuration
            on_success: Optional callback on successful send
            on_error: Optional callback on send error
        """
        self._config = config
        self._on_success = on_success
        self._on_error = on_error
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="eco_telemetry")
        self._queue: Queue[TelemetryRecord] = Queue(maxsize=config.max_queue_size)
        self._shutdown = False
        self._batch_thread: Optional[threading.Thread] = None
        
        # Start batch processing if batching is enabled
        if config.batch_size > 1 and config.endpoint:
            self._start_batch_processor()
    
    def _start_batch_processor(self) -> None:
        """Start the background batch processing thread."""
        self._batch_thread = threading.Thread(
            target=self._batch_processor_loop,
            name="eco_telemetry_batch",
            daemon=True
        )
        self._batch_thread.start()
    
    def _batch_processor_loop(self) -> None:
        """Background loop for batch processing telemetry records."""
        batch: List[TelemetryRecord] = []
        last_send_time = time.time()
        
        while not self._shutdown:
            try:
                # Try to get a record with timeout
                try:
                    record = self._queue.get(timeout=1.0)
                    batch.append(record)
                except Empty:
                    pass
                
                # Check if we should send the batch
                should_send = (
                    len(batch) >= self._config.batch_size or
                    (len(batch) > 0 and time.time() - last_send_time >= self._config.batch_timeout_seconds)
                )
                
                if should_send and batch:
                    self._send_batch(batch)
                    batch = []
                    last_send_time = time.time()
                    
            except Exception as e:
                if not self._config.fail_silently:
                    logger.error(f"Batch processor error: {e}")
        
        # Send remaining batch on shutdown
        if batch:
            self._send_batch(batch)
    
    def send(self, record: TelemetryRecord) -> None:
        """
        Send a telemetry record asynchronously.
        
        This method returns immediately. The actual sending happens
        in a background thread.
        
        Args:
            record: Telemetry record to send
        """
        if not self._config.enabled or not self._config.endpoint:
            return
        
        if self._shutdown:
            return
        
        try:
            if self._config.batch_size > 1:
                # Add to queue for batch processing
                try:
                    self._queue.put_nowait(record)
                except Exception:
                    # Queue full, drop the record
                    if not self._config.fail_silently:
                        logger.warning("Telemetry queue full, dropping record")
            else:
                # Send immediately in background
                self._executor.submit(self._send_single, record)
        except Exception as e:
            self._handle_error(e)
    
    def _send_single(self, record: TelemetryRecord) -> None:
        """
        Send a single telemetry record.
        
        Args:
            record: Telemetry record to send
        """
        if not self._config.endpoint:
            return
        
        for attempt in range(self._config.max_retries):
            try:
                response = self._make_request([record])
                
                if response.status_code >= 200 and response.status_code < 300:
                    if self._on_success:
                        self._on_success(record.get("id", "unknown"))
                    return
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if attempt == self._config.max_retries - 1:
                        self._handle_error(Exception(error_msg))
                    else:
                        time.sleep(self._config.retry_delay_seconds)
                        
            except requests.exceptions.Timeout:
                if attempt == self._config.max_retries - 1:
                    self._handle_error(Exception("Telemetry request timed out"))
                else:
                    time.sleep(self._config.retry_delay_seconds)
                    
            except Exception as e:
                if attempt == self._config.max_retries - 1:
                    self._handle_error(e)
                else:
                    time.sleep(self._config.retry_delay_seconds)
    
    def _send_batch(self, records: List[TelemetryRecord]) -> None:
        """
        Send a batch of telemetry records.
        
        Args:
            records: List of telemetry records to send
        """
        if not records or not self._config.endpoint:
            return
        
        for attempt in range(self._config.max_retries):
            try:
                response = self._make_request(records)
                
                if response.status_code >= 200 and response.status_code < 300:
                    if self._on_success:
                        for record in records:
                            self._on_success(record.get("id", "unknown"))
                    return
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if attempt == self._config.max_retries - 1:
                        self._handle_error(Exception(error_msg))
                    else:
                        time.sleep(self._config.retry_delay_seconds)
                        
            except Exception as e:
                if attempt == self._config.max_retries - 1:
                    self._handle_error(e)
                else:
                    time.sleep(self._config.retry_delay_seconds)
    
    def _make_request(self, records: List[TelemetryRecord]) -> requests.Response:
        """
        Make HTTP request to telemetry endpoint.
        
        Args:
            records: Records to send
        
        Returns:
            HTTP response
        """
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "eco-compute-sdk/0.1.0"
        }
        
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"
        
        payload = {
            "records": records,
            "sdk_version": "0.1.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        return requests.post(
            self._config.endpoint,  # type: ignore
            headers=headers,
            json=payload,
            timeout=self._config.timeout_seconds
        )
    
    def _handle_error(self, error: Exception) -> None:
        """
        Handle telemetry errors gracefully.
        
        Args:
            error: The exception that occurred
        """
        if self._on_error:
            try:
                self._on_error(error)
            except Exception:
                pass
        
        if not self._config.fail_silently:
            logger.error(f"Telemetry error: {error}")
    
    def flush(self, timeout_seconds: float = 10.0) -> None:
        """
        Flush any pending telemetry records.
        
        Blocks until all queued records are sent or timeout expires.
        
        Args:
            timeout_seconds: Maximum time to wait
        """
        start_time = time.time()
        
        while not self._queue.empty():
            if time.time() - start_time > timeout_seconds:
                break
            time.sleep(0.1)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the telemetry sender.
        
        Args:
            wait: Whether to wait for pending records
        """
        self._shutdown = True
        
        if wait:
            self.flush()
        
        self._executor.shutdown(wait=wait)
        
        if self._batch_thread and self._batch_thread.is_alive():
            self._batch_thread.join(timeout=5.0)
    
    @property
    def is_enabled(self) -> bool:
        """Check if telemetry is enabled and configured."""
        return self._config.enabled and self._config.endpoint is not None
    
    @property
    def queue_size(self) -> int:
        """Get the current queue size."""
        return self._queue.qsize()
    
    def set_token(self, token: str) -> None:
        """
        Update the telemetry authentication token.
        
        Args:
            token: New bearer token
        """
        self._config.token = token
        
    def set_endpoint(self, endpoint: str) -> None:
        """
        Update the telemetry endpoint.
        
        Args:
            endpoint: New telemetry endpoint URL
        """
        self._config.endpoint = endpoint
        # Start batch processor if not already running and batching is enabled
        if self._config.batch_size > 1 and not self._batch_thread and self._config.endpoint:
            self._start_batch_processor()


# Convenience function for simple usage
def create_sender(
    endpoint: Optional[str] = None,
    token: Optional[str] = None,
    enabled: bool = True,
    fail_silently: bool = True
) -> TelemetrySender:
    """
    Create a telemetry sender with simple configuration.
    
    Args:
        endpoint: Telemetry endpoint URL
        token: Bearer token for authentication
        enabled: Whether telemetry is enabled
        fail_silently: Whether to suppress errors
    
    Returns:
        Configured TelemetrySender instance
    
    Example:
        >>> sender = create_sender(
        ...     endpoint="https://api.example.com/telemetry",
        ...     token="your-token"
        ... )
    """
    config = TelemetrySenderConfig(
        endpoint=endpoint,
        token=token,
        enabled=enabled,
        fail_silently=fail_silently,
        batch_size=1  # Immediate sending for simple usage
    )
    return TelemetrySender(config)
