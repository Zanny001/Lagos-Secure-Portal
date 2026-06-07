import time
from collections import defaultdict
from flask import jsonify, request

class SlidingWindowLimiter:
    def __init__(self, window_seconds=10, max_requests=5):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        # Store request timestamps mapped to client IP strings
        self.ip_track_registry = defaultdict(list)

    def is_rate_limited(self, ip_address):
        """Evaluates timestamps and cleans up windows to determine if traffic should be choked."""
        current_time = time.time()
        timestamps = self.ip_track_registry[ip_address]

        # Evict historical timestamps outside the active observation window
        while timestamps and timestamps[0] < current_time - self.window_seconds:
            timestamps.pop(0)

        # Evaluate if the client has exhausted their current window quota
        if len(timestamps) >= self.max_requests:
            return True

        # Log the current valid access timestamp
        timestamps.append(current_time)
        return False

def limit_requests(limiter_instance):
    """Decorator middleware designed to seamlessly interleave with Flask routing hooks."""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Isolate the caller's IP address
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            
            if limiter_instance.is_rate_limited(client_ip):
                print(f"⚠️  [SECURITY BLOCK] Rate limit hit by unauthorized burst from IP: {client_ip}")
                return jsonify({
                    "status": "error",
                    "message": "Too Many Requests. Rate limit exceeded for this window. Please back off.",
                    "window_limit": limiter_instance.max_requests,
                    "window_seconds": limiter_instance.window_seconds
                }), 429
                
            return f(*args, **kwargs)
        return wrapper
    return decorator
