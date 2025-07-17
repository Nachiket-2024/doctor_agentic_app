# --- Import necessary libraries from Starlette ---
from starlette.middleware.base import BaseHTTPMiddleware  # Base class for creating custom middleware
from starlette.responses import StreamingResponse  # Used to return streaming responses
from starlette.types import ASGIApp, Scope, Receive, Send  # Type definitions for ASGI apps, required by middleware
from starlette.responses import JSONResponse  # To send JSON error response in case of an exception
from .logging_config import get_logger  # Import the custom logging setup from the logging_config file

# --- Get logger instance using custom logging setup ---
logger = get_logger()  # Create a logger instance for logging incoming requests and responses

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests and responses, including streaming responses.
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Initializes the middleware and calls the parent class constructor.
        :param app: The ASGI app that this middleware is wrapping
        """
        super().__init__(app)  # Call the parent constructor (BaseHTTPMiddleware) to initialize the app

    async def dispatch(self, request, call_next):
        """
        Handles the incoming request, logs the request details, processes the request, 
        and logs the response details (including streaming responses).
        
        :param request: The incoming HTTP request
        :param call_next: The function that will be called to get the response
        :return: The final response
        """
        # --- Log incoming request details with user info (if available) ---
        user_info = f"User: {getattr(request.state, 'user', 'Anonymous')}"  # Fetch user info from request state (or "Anonymous" if not found)
        logger.info(f"Incoming request: {request.method} {request.url} {user_info}")  # Log the method, URL, and user info for incoming requests

        try:
            # --- Process the request and get the response ---
            response = await call_next(request)  # Call the next handler (route) to process the request and return a response
        except Exception as e:
            # --- Log error and return a response ---
            logger.error(f"Error processing request: {request.method} {request.url} - {str(e)}")  # Log error details (method, URL, exception message)
            return JSONResponse(  # Return a JSON error response with a status code 500 (Internal Server Error)
                {"detail": "Internal Server Error"}, status_code=500
            )

        # --- Log the response details for non-streaming responses ---
        if not isinstance(response, StreamingResponse):  # Check if the response is NOT a StreamingResponse (i.e., normal response)
            # Log the response status, method, URL, and body size (if available)
            logger.info(f"Response: {response.status_code} for {request.method} {request.url}, Body size: {len(response.body) if hasattr(response, 'body') else 'N/A'} bytes")

        # --- Handle and log StreamingResponse ---
        if isinstance(response, StreamingResponse):  # Check if the response is a StreamingResponse
            # Define an async function to wrap the response body in order to handle streaming
            async def streaming_body():
                async for chunk in response.body_iterator:  # Iterate through each chunk of the streaming response
                    yield chunk  # Yield each chunk of the streaming response

            # Create a new StreamingResponse, wrapping the streaming body
            response = StreamingResponse(
                streaming_body(), status_code=response.status_code, headers=response.headers
            )

            # --- Log the streaming response status ---
            logger.info(f"Streaming response with status code: {response.status_code}")  # Log the status code of the streaming response

        # --- Return the (possibly wrapped) response ---
        return response  # Return the final response, which may be wrapped in a StreamingResponse
