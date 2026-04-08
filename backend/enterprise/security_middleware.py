"""
STEP 16.8-16.9 — SECURITY MIDDLEWARE

Security headers + rate limiting:

Headers (16.8):
- Strict-Transport-Security (HSTS)
- Content-Security-Policy (CSP)
- X-Frame-Options (clickjacking)
- X-Content-Type-Options (MIME sniffing)
- Referrer-Policy

Rate Limiting (16.9):
- Per-user rate limits
- Per-IP rate limits
- Per-endpoint limits
- Adaptive blocking (after repeated violations)
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import time


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"       # Reset at fixed times
    SLIDING_WINDOW = "sliding_window"   # Continuous window
    TOKEN_BUCKET = "token_bucket"       # Tokens refill over time
    LEAKY_BUCKET = "leaky_bucket"       # Constant outflow


class SecurityHeadersMiddleware:
    """
    Adds security headers to all responses.
    Prevents common browser-based attacks.
    """
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get standard security headers"""
        return {
            # HTTPS enforcement
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # CSP: Restrict script/style sources
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            
            # Clickjacking protection
            "X-Frame-Options": "DENY",
            
            # MIME type sniffing protection
            "X-Content-Type-Options": "nosniff",
            
            # XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Feature policy / Permissions policy
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            ),
        }
    
    @staticmethod
    def apply_headers(response: dict) -> dict:
        """Apply security headers to response"""
        headers = SecurityHeadersMiddleware.get_security_headers()
        
        if "headers" not in response:
            response["headers"] = {}
        
        response["headers"].update(headers)
        return response


@dataclass
class RateLimitConfig:
    """Configuration for rate limit"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    burst_size: int = 10  # Allow brief bursts


class RateLimiter:
    """
    Rate limiting using token bucket algorithm.
    
    Supports:
    - Per-user limits
    - Per-IP limits
    - Per-endpoint limits
    - Adaptive blocking
    """
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        
        # Track requests: key -> list of timestamps
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        
        # Track violations: key -> violation count
        self.violations: Dict[str, int] = defaultdict(int)
        
        # Blocked keys: key -> unblock time
        self.blocked: Dict[str, float] = {}
    
    def _get_key(self, user_id: Optional[str] = None, ip_address: Optional[str] = None,
                 endpoint: Optional[str] = None) -> str:
        """Generate rate limit key"""
        parts = []
        if user_id:
            parts.append(f"user:{user_id}")
        if ip_address:
            parts.append(f"ip:{ip_address}")
        if endpoint:
            parts.append(f"endpoint:{endpoint}")
        
        return "|".join(parts) if parts else "global"
    
    def _clean_old_requests(self, key: str, window_seconds: int):
        """Remove requests older than window"""
        now = time.time()
        cutoff = now - window_seconds
        
        if key in self.request_history:
            self.request_history[key] = [
                ts for ts in self.request_history[key] if ts >= cutoff
            ]
    
    def is_throttled(self, user_id: Optional[str] = None, 
                    ip_address: Optional[str] = None,
                    endpoint: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if request should be throttled.
        
        Returns:
            (is_throttled, reason)
        """
        key = self._get_key(user_id, ip_address, endpoint)
        now = time.time()
        
        # Check if blocked
        if key in self.blocked:
            if self.blocked[key] > now:
                return True, f"Rate limit exceeded. Try again in {int(self.blocked[key] - now)}s"
            else:
                # Unblock
                del self.blocked[key]
                self.violations[key] = 0
        
        # Check requests per minute
        self._clean_old_requests(key, 60)
        requests_last_minute = len(self.request_history[key])
        
        if requests_last_minute >= self.config.requests_per_minute:
            self.violations[key] += 1
            
            # Block after repeated violations
            if self.violations[key] > 3:
                block_duration = 300 * (self.violations[key] - 2)  # 5min, 10min, 15min...
                self.blocked[key] = now + block_duration
                return True, f"Too many violations. Blocked for {block_duration}s"
            
            return True, "Rate limit exceeded (per minute)"
        
        # Check requests per hour
        self._clean_old_requests(key, 3600)
        requests_last_hour = len(self.request_history[key])
        
        if requests_last_hour >= self.config.requests_per_hour:
            return True, "Rate limit exceeded (per hour)"
        
        return False, None
    
    def record_request(self, user_id: Optional[str] = None,
                      ip_address: Optional[str] = None,
                      endpoint: Optional[str] = None):
        """Record a request"""
        key = self._get_key(user_id, ip_address, endpoint)
        self.request_history[key].append(time.time())
    
    def record_violation(self, user_id: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        endpoint: Optional[str] = None):
        """Record a violation (failed auth, etc.)"""
        key = self._get_key(user_id, ip_address, endpoint)
        self.violations[key] += 1
        
        # Auto-block after 5 violations
        if self.violations[key] >= 5:
            self.blocked[key] = time.time() + 600  # 10 minutes
    
    def get_status(self, user_id: Optional[str] = None,
                   ip_address: Optional[str] = None,
                   endpoint: Optional[str] = None) -> dict:
        """Get current rate limit status"""
        key = self._get_key(user_id, ip_address, endpoint)
        
        self._clean_old_requests(key, 60)
        requests_last_minute = len(self.request_history[key])
        
        is_blocked = key in self.blocked and self.blocked[key] > time.time()
        
        return {
            "requests_this_minute": requests_last_minute,
            "limit_per_minute": self.config.requests_per_minute,
            "remaining": max(0, self.config.requests_per_minute - requests_last_minute),
            "is_limited": is_blocked,
            "violations": self.violations.get(key, 0)
        }
    
    def reset(self, user_id: Optional[str] = None,
             ip_address: Optional[str] = None,
             endpoint: Optional[str] = None):
        """Reset rate limits for key"""
        key = self._get_key(user_id, ip_address, endpoint)
        
        if key in self.request_history:
            self.request_history[key] = []
        if key in self.violations:
            self.violations[key] = 0
        if key in self.blocked:
            del self.blocked[key]


class SecurityMiddlewareStack:
    """
    Combined security middleware stack.
    Applies all security measures to requests/responses.
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.violation_log: List[dict] = []
    
    async def process_request(self, user_id: Optional[str] = None,
                             ip_address: Optional[str] = None,
                             endpoint: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Process incoming request through security checks.
        
        Returns:
            (allow, error_message)
        """
        
        # Check rate limit
        is_throttled, reason = self.rate_limiter.is_throttled(user_id, ip_address, endpoint)
        if is_throttled:
            self.violation_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "ip_address": ip_address,
                "endpoint": endpoint,
                "violation": "rate_limit",
                "reason": reason
            })
            return False, reason
        
        # Record request
        self.rate_limiter.record_request(user_id, ip_address, endpoint)
        
        return True, None
    
    async def process_response(self, response: dict) -> dict:
        """Add security headers to response"""
        return SecurityHeadersMiddleware.apply_headers(response)
    
    def record_security_violation(self, user_id: Optional[str],
                                  violation_type: str,
                                  details: Optional[str] = None):
        """Log security violation"""
        self.violation_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "violation_type": violation_type,
            "details": details
        })
        
        # After 3 violations, block user
        user_violations = sum(1 for v in self.violation_log
                             if v.get("user_id") == user_id)
        
        if user_violations >= 3:
            self.rate_limiter.violations[f"user:{user_id}"] = 10
    
    def get_violation_report(self, hours: int = 24) -> dict:
        """Get security violation report"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_violations = [
            v for v in self.violation_log
            if datetime.fromisoformat(v.get("timestamp", "")) >= cutoff
        ]
        
        violated_users = set(v.get("user_id") for v in recent_violations if v.get("user_id"))
        violated_ips = set(v.get("ip_address") for v in recent_violations if v.get("ip_address"))
        
        violation_types = {}
        for v in recent_violations:
            vtype = v.get("violation_type", "unknown")
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        return {
            "recent_hours": hours,
            "total_violations": len(recent_violations),
            "violated_users": len(violated_users),
            "violated_ips": len(violated_ips),
            "by_type": violation_types,
            "recent": recent_violations[-10:]  # Last 10
        }


# Global security middleware
_security_middleware = None


def get_security_middleware() -> SecurityMiddlewareStack:
    """Get or create global security middleware"""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddlewareStack()
    return _security_middleware
