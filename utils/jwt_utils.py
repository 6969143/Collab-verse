from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from flask import current_app

def generate_token(identity):
    """Create a new JWT for the given identity."""
    expires = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
    return create_access_token(identity=identity, expires_delta=expires)

def get_current_user_id():
    """Extract user ID from a valid JWT cookie."""
    verify_jwt_in_request()
    return get_jwt_identity()