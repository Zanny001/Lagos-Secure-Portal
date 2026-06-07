from functools import wraps
from flask import request, jsonify

# Pre-authorized structural API client access token matrix mapping keys
AUTHORIZED_API_TOKENS = {
    "dev_client_zannie_mobile_6619": "Zannie Frontend Mobile App",
    "lead_harvester_internal_3302": "Internal Lead Generation Scraper",
    "dashboard_panel_admin_5581": "Administrative Reporting CLI Console"
}

def require_api_token(f):
    """
    Custom decorator filter designed to protect microservice routing paths.
    Validates incoming request headers for a registered system verification token.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intercept and check the custom security header token array
        client_token = request.headers.get("X-Zannie-Auth-Token")
        
        if not client_token:
            return jsonify({
                "status": "unauthorized",
                "message": "Access Denied: Missing system identification token header token."
            }), 401
            
        if client_token not in AUTHORIZED_API_TOKENS:
            return jsonify({
                "status": "forbidden",
                "message": "Access Denied: Presented API key signature token is invalid or expired."
            }), 403
            
        # Log valid authentications silently to the server logs
        print(f"[SECURITY GUARD] Authenticated Client: {AUTHORIZED_API_TOKENS[client_token]}")
        return f(*args, **kwargs)
        
    return decorated_function

