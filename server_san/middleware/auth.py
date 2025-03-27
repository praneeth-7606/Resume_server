# Update middleware/auth.py

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from services import auth_service
import jwt
import config
from pymongo import MongoClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection for token blacklist
client = MongoClient(config.MONGODB_URL)
db = client[config.DATABASE_NAME]
blacklist_collection = db["token_blacklist"]

async def auth_middleware(request: Request, call_next):
    # Log the request path for debugging
    logger.info(f"Processing request: {request.method} {request.url.path}")
    
    # Paths that don't require authentication
    public_paths = [
        "/",
        "/auth/signup",
        "/auth/token",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static"
    ]
    
    # Skip auth check for public paths and OPTIONS requests (CORS preflight)
    if any(request.url.path.startswith(path) for path in public_paths) or request.method == "OPTIONS":
        logger.info(f"Skipping auth for public path or OPTIONS: {request.url.path}")
        response = await call_next(request)
        return response
    
    # Check for authorization header
    authorization = request.headers.get("Authorization")
    if not authorization:
        logger.warning("No Authorization header found")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Extract token
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            logger.warning(f"Invalid auth scheme: {scheme}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check if token is blacklisted
        if blacklist_collection.find_one({"token": token}):
            logger.warning(f"Blacklisted token detected")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has been revoked"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verify token
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning("Token missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except (jwt.JWTError, jwt.ExpiredSignatureError) as e:
        logger.error(f"JWT validation error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token or expired token"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Auth middleware error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication failed"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Proceed with request if token is valid
    logger.info(f"Authentication successful for user: {username}")
    response = await call_next(request)
    return response