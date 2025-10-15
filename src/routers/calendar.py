from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import httpx
import os

from database import get_db
from models.user import User
from routers.auth import get_current_user

router = APIRouter()

# Google Calendar API Configuration
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"

async def get_google_calendar_events(
    access_token: str,
    time_min: str,
    time_max: str,
    calendar_id: str = "primary"
):
    """
    Fetch events from Google Calendar API
    """
    url = f"{GOOGLE_CALENDAR_API}/calendars/{calendar_id}/events"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    params = {
        "timeMin": time_min,
        "timeMax": time_max,
        "singleEvents": True,
        "orderBy": "startTime",
        "maxResults": 250  # Adjust as needed
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Google Calendar access token is invalid or expired"
                )
            elif e.response.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to access Google Calendar. Please reauthorize with calendar scopes."
                )
            else:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Google Calendar API error: {e.response.text}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch calendar events: {str(e)}"
            )


@router.get("/calendar")
async def get_calendar_events(
    timeMin: str,
    timeMax: str,
    calendar_id: Optional[str] = "primary",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get calendar events for the authenticated user
    
    Query Parameters:
    - timeMin: Start time in ISO format (e.g., 2025-10-12T04:00:00.000Z)
    - timeMax: End time in ISO format (e.g., 2025-10-20T03:59:59.999Z)
    - calendar_id: Calendar ID (default: "primary")
    
    Returns:
    - List of calendar events with details
    """
    
    # Check if user has Google access token
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated with Google. Please connect your Google account."
        )
    
    # Validate date formats
    try:
        datetime.fromisoformat(timeMin.replace('Z', '+00:00'))
        datetime.fromisoformat(timeMax.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (e.g., 2025-10-12T04:00:00.000Z)"
        )
    
    # Check if Google Calendar scope verification is pending
    if os.getenv("GOOGLE_CALENDAR_VERIFICATION_PENDING") == "true":
        # Return mock data while waiting for verification
        return {
            "status": "pending_verification",
            "message": "Google Calendar API verification is pending. Showing sample data.",
            "events": [
                {
                    "id": "sample_1",
                    "summary": "Sample Event - Verification Pending",
                    "description": "This is sample data. Full calendar sync will be available after Google verification.",
                    "start": {
                        "dateTime": timeMin,
                        "timeZone": "America/New_York"
                    },
                    "end": {
                        "dateTime": timeMin,
                        "timeZone": "America/New_York"
                    },
                    "status": "confirmed",
                    "htmlLink": "#"
                }
            ],
            "timeMin": timeMin,
            "timeMax": timeMax
        }
    
    # Fetch real events from Google Calendar
    try:
        calendar_data = await get_google_calendar_events(
            access_token=current_user.google_access_token,
            time_min=timeMin,
            time_max=timeMax,
            calendar_id=calendar_id
        )
        
        # Format and return events
        events = calendar_data.get("items", [])
        
        return {
            "status": "success",
            "events": events,
            "timeMin": timeMin,
            "timeMax": timeMax,
            "calendar_id": calendar_id,
            "total_events": len(events)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error fetching calendar events: {str(e)}"
        )


@router.get("/calendar/list")
async def list_calendars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all calendars available to the user
    """
    
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated with Google"
        )
    
    url = f"{GOOGLE_CALENDAR_API}/users/me/calendarList"
    
    headers = {
        "Authorization": f"Bearer {current_user.google_access_token}",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            return {
                "status": "success",
                "calendars": data.get("items", [])
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch calendar list: {str(e)}"
            )


@router.post("/calendar/sync")
async def sync_calendar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a manual sync of calendar events
    This can be used to refresh the user's calendar data
    """
    
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated with Google"
        )
    
    # TODO: Implement sync logic
    # This could involve:
    # 1. Fetching recent events
    # 2. Storing them in your database
    # 3. Setting up webhooks for real-time updates
    
    return {
        "status": "success",
        "message": "Calendar sync initiated",
        "user_id": current_user.id
    }


@router.get("/calendar/status")
async def calendar_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of Google Calendar integration
    """
    
    has_token = bool(current_user.google_access_token)
    verification_pending = os.getenv("GOOGLE_CALENDAR_VERIFICATION_PENDING") == "true"
    
    return {
        "connected": has_token,
        "verification_pending": verification_pending,
        "scopes_needed": [
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events"
        ],
        "message": "Google Calendar verification pending" if verification_pending else (
            "Calendar connected" if has_token else "Calendar not connected"
        )
    }