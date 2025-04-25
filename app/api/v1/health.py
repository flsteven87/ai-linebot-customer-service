"""
Health check API endpoints.
"""
from fastapi import APIRouter, Response, status

router = APIRouter(tags=["Health"])

@router.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status of the API.
    """
    return {"status": "healthy"}


@router.get("/echo/{message}")
async def echo(message: str, response: Response):
    """
    Echo endpoint for testing.
    
    Args:
        message (str): Message to echo back.
        response (Response): FastAPI response object.
        
    Returns:
        dict: Echoed message.
    """
    if not message:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "No message provided"}
        
    return {"message": message} 