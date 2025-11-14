"""
API Routes for AI Agents

Endpoints for interacting with specialized AI agents.
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from database.database_manager import DatabaseManager
from agents_framework.agents.email_analyst_agent import create_email_analyst_agent
from agents_framework.agents.followup_agent import create_followup_agent
from agents_framework.agents.job_hunter_agent import create_job_hunter_agent

logger = logging.getLogger(__name__)

router = APIRouter()


# Dependency to get database manager
def get_db():
    """Dependency to get database manager"""
    return DatabaseManager()


# Request/Response Models
class EmailAnalysisRequest(BaseModel):
    """Request model for email analysis"""
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    sender: Optional[str] = Field(None, description="Email sender address")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Interview Invitation - Software Engineer at Google",
                "body": "We are pleased to invite you for an interview...",
                "sender": "recruiting@google.com",
                "metadata": {"email_id": "123", "received_at": "2025-01-15T10:00:00Z"}
            }
        }


class EmailThreadAnalysisRequest(BaseModel):
    """Request model for email thread analysis"""
    emails: List[Dict[str, Any]] = Field(..., description="List of emails in the thread")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Thread metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "emails": [
                    {
                        "subject": "Re: Software Engineer Position",
                        "body": "Thank you for your interest...",
                        "sender": "hr@company.com",
                        "date": "2025-01-10"
                    },
                    {
                        "subject": "Re: Software Engineer Position",
                        "body": "I'm very interested in this role...",
                        "sender": "me@email.com",
                        "date": "2025-01-11"
                    }
                ]
            }
        }


class EmailAnalysisResponse(BaseModel):
    """Response model for email analysis"""
    success: bool
    analysis: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class EmailThreadAnalysisResponse(BaseModel):
    """Response model for email thread analysis"""
    success: bool
    analysis: str
    email_count: int
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentStatsResponse(BaseModel):
    """Response model for agent statistics"""
    name: str
    execution_count: int
    tools_count: int
    memory_size: int
    uptime: Optional[str] = None


# Follow-up Agent Request/Response Models
class FollowUpTimingRequest(BaseModel):
    """Request model for follow-up timing optimization"""
    job_id: int = Field(..., description="Job application ID")
    status: str = Field(..., description="Current application status")
    days_since_contact: int = Field(..., description="Days since last contact")
    application_date: str = Field(..., description="Application submission date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": 123,
                "status": "applied",
                "days_since_contact": 8,
                "application_date": "2025-11-01",
                "metadata": {}
            }
        }


class FollowUpDraftRequest(BaseModel):
    """Request model for drafting follow-up messages"""
    followup_type: str = Field(..., description="Type of follow-up")
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job position")
    tone: str = Field("professional", description="Message tone")
    context_notes: str = Field("", description="Additional context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "followup_type": "initial_application",
                "company": "Google",
                "position": "Software Engineer",
                "tone": "professional",
                "context_notes": "Applied via LinkedIn",
                "metadata": {}
            }
        }


class FollowUpStrategyRequest(BaseModel):
    """Request model for follow-up strategy analysis"""
    status: str = Field(..., description="Application status")
    days_since_application: int = Field(..., description="Days since application")
    response_history: str = Field(..., description="History of responses")
    priority: str = Field("medium", description="Priority level")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "interview",
                "days_since_application": 15,
                "response_history": "positive",
                "priority": "high",
                "metadata": {}
            }
        }


class FollowUpResponse(BaseModel):
    """Response model for follow-up operations"""
    success: bool
    output: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Job Hunter Agent Models
class JobSearchRequest(BaseModel):
    """Request model for job search"""
    keywords: str = Field(..., description="Job search keywords (e.g., 'Software Engineer', 'Data Scientist')")
    location: str = Field("", description="Location filter (e.g., 'San Francisco, CA', 'Remote')")
    platforms: Optional[List[str]] = Field(None, description="Platforms to search (LinkedIn, Indeed, Glassdoor)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")

    class Config:
        json_schema_extra = {
            "example": {
                "keywords": "Software Engineer",
                "location": "San Francisco, CA",
                "platforms": ["LinkedIn", "Indeed"],
                "filters": {
                    "experience_level": "Mid-Senior level",
                    "job_type": "Full-time",
                    "salary_min": 120
                }
            }
        }


class JobRecommendationsRequest(BaseModel):
    """Request model for job recommendations"""
    user_id: int = Field(1, description="User ID to get recommendations for")
    limit: int = Field(10, description="Maximum number of recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "limit": 10
            }
        }


class JobSearchResponse(BaseModel):
    """Response model for job search"""
    success: bool
    analysis: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JobRecommendationsResponse(BaseModel):
    """Response model for job recommendations"""
    success: bool
    analysis: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Email Analyst Agent Endpoints
@router.post("/email-analyst/analyze", response_model=EmailAnalysisResponse)
async def analyze_email(
    request: EmailAnalysisRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze a single job-related email using the Email Analyst Agent.

    This endpoint uses AI to:
    - Detect sentiment and urgency
    - Categorize the email type (interview, rejection, offer, etc.)
    - Extract company and position information
    - Find matching job applications
    - Extract action items and deadlines
    - Recommend appropriate follow-up actions

    Returns comprehensive analysis with actionable insights.
    """
    try:
        logger.info(f"📧 Email Analyst: Analyzing email from {request.sender}")

        # Create agent
        agent = create_email_analyst_agent(db)

        # Analyze email
        result = await agent.analyze_email(
            subject=request.subject,
            body=request.body,
            sender=request.sender or "",
            metadata=request.metadata
        )

        logger.info(f"✅ Email analysis {'successful' if result['success'] else 'failed'}")

        return EmailAnalysisResponse(**result)

    except Exception as e:
        logger.error(f"❌ Error in email analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing email: {str(e)}"
        )


@router.post("/email-analyst/analyze-thread", response_model=EmailThreadAnalysisResponse)
async def analyze_email_thread(
    request: EmailThreadAnalysisRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze a conversation thread of multiple related emails.

    This endpoint uses AI to understand:
    - Conversation timeline and progression
    - Sentiment shifts across the thread
    - Key milestones and decisions
    - Overall action items from the thread
    - Current state and recommended next steps

    Useful for understanding the full context of job application communications.
    """
    try:
        logger.info(f"🧵 Email Analyst: Analyzing thread with {len(request.emails)} emails")

        if not request.emails:
            raise HTTPException(
                status_code=400,
                detail="Email thread must contain at least one email"
            )

        # Create agent
        agent = create_email_analyst_agent(db)

        # Analyze thread
        result = await agent.analyze_thread(
            emails=request.emails,
            metadata=request.metadata
        )

        logger.info(f"✅ Thread analysis {'successful' if result['success'] else 'failed'}")

        return EmailThreadAnalysisResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in thread analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing email thread: {str(e)}"
        )


@router.get("/email-analyst/stats", response_model=AgentStatsResponse)
async def get_email_analyst_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get statistics and status information for the Email Analyst Agent.

    Returns:
    - Agent name and configuration
    - Number of executions
    - Available tools count
    - Memory usage
    - Performance metrics
    """
    try:
        logger.info("📊 Email Analyst: Getting agent statistics")

        # Create agent
        agent = create_email_analyst_agent(db)

        # Get statistics
        stats = agent.get_stats()

        return AgentStatsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ Error getting agent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent statistics: {str(e)}"
        )


# WebSocket endpoint for real-time email analysis
@router.websocket("/email-analyst/ws")
async def email_analyst_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time email analysis.

    Allows streaming analysis results as the agent processes the email.

    Message format:
    - Client sends: {"type": "analyze", "data": {"subject": "...", "body": "...", "sender": "..."}}
    - Server sends: {"type": "analysis_progress", "data": {...}} (during processing)
    - Server sends: {"type": "analysis_complete", "data": {...}} (when done)
    """
    await websocket.accept()
    logger.info("🔌 Email Analyst WebSocket connection established")

    try:
        db = DatabaseManager()
        agent = create_email_analyst_agent(db)

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "analyze":
                email_data = data.get("data", {})

                # Send acknowledgment
                await websocket.send_json({
                    "type": "analysis_started",
                    "data": {"timestamp": datetime.now().isoformat()}
                })

                try:
                    # Perform analysis
                    result = await agent.analyze_email(
                        subject=email_data.get("subject", ""),
                        body=email_data.get("body", ""),
                        sender=email_data.get("sender", ""),
                        metadata=email_data.get("metadata")
                    )

                    # Send complete result
                    await websocket.send_json({
                        "type": "analysis_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket analysis: {e}")
                    await websocket.send_json({
                        "type": "analysis_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "analyze_thread":
                thread_data = data.get("data", {})
                emails = thread_data.get("emails", [])

                if not emails:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"error": "No emails provided in thread"}
                    })
                    continue

                # Send acknowledgment
                await websocket.send_json({
                    "type": "thread_analysis_started",
                    "data": {"email_count": len(emails), "timestamp": datetime.now().isoformat()}
                })

                try:
                    # Perform thread analysis
                    result = await agent.analyze_thread(
                        emails=emails,
                        metadata=thread_data.get("metadata")
                    )

                    # Send complete result
                    await websocket.send_json({
                        "type": "thread_analysis_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket thread analysis: {e}")
                    await websocket.send_json({
                        "type": "analysis_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"error": f"Unknown message type: {message_type}"}
                })

    except WebSocketDisconnect:
        logger.info("🔌 Email Analyst WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# Follow-up Agent Endpoints
@router.post("/followup-agent/optimize-timing", response_model=FollowUpResponse)
async def optimize_followup_timing(
    request: FollowUpTimingRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Optimize the timing for sending a follow-up email.

    This endpoint uses AI to:
    - Analyze current application stage
    - Calculate optimal send time based on best practices
    - Consider response patterns and timing rules
    - Recommend specific dates and times
    - Provide reasoning for recommendations

    Returns timing recommendations with confidence scores.
    """
    try:
        logger.info(f"⏰ Follow-up Agent: Optimizing timing for job #{request.job_id}")

        # Create agent
        agent = create_followup_agent(db)

        # Optimize timing
        result = await agent.optimize_followup_timing(
            job_id=request.job_id,
            status=request.status,
            days_since_contact=request.days_since_contact,
            application_date=request.application_date,
            metadata=request.metadata
        )

        logger.info(f"✅ Timing optimization {'successful' if result['success'] else 'failed'}")

        return FollowUpResponse(
            success=result['success'],
            output=result.get('recommendations', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in timing optimization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing follow-up timing: {str(e)}"
        )


@router.post("/followup-agent/draft-message", response_model=FollowUpResponse)
async def draft_followup_message(
    request: FollowUpDraftRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Draft a personalized follow-up message.

    This endpoint uses AI to:
    - Create personalized message content
    - Match tone to company culture and situation
    - Include relevant context and details
    - Provide subject line suggestions
    - Offer customization tips

    Returns a complete, ready-to-send follow-up email.
    """
    try:
        logger.info(f"✉️ Follow-up Agent: Drafting {request.followup_type} message for {request.company}")

        # Create agent
        agent = create_followup_agent(db)

        # Draft message
        result = await agent.draft_followup(
            followup_type=request.followup_type,
            company=request.company,
            position=request.position,
            tone=request.tone,
            context_notes=request.context_notes,
            metadata=request.metadata
        )

        logger.info(f"✅ Message drafting {'successful' if result['success'] else 'failed'}")

        return FollowUpResponse(
            success=result['success'],
            output=result.get('message', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in message drafting: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error drafting follow-up message: {str(e)}"
        )


@router.post("/followup-agent/analyze-strategy", response_model=FollowUpResponse)
async def analyze_followup_strategy(
    request: FollowUpStrategyRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze and suggest a comprehensive follow-up strategy.

    This endpoint uses AI to:
    - Analyze response history and patterns
    - Recommend a complete follow-up sequence
    - Optimize timing for each follow-up
    - Provide message guidelines
    - Set realistic success metrics

    Returns a data-driven, multi-step follow-up plan.
    """
    try:
        logger.info(f"🎯 Follow-up Agent: Analyzing strategy for {request.status} application")

        # Create agent
        agent = create_followup_agent(db)

        # Analyze strategy
        result = await agent.analyze_strategy(
            status=request.status,
            days_since_application=request.days_since_application,
            response_history=request.response_history,
            priority=request.priority,
            metadata=request.metadata
        )

        logger.info(f"✅ Strategy analysis {'successful' if result['success'] else 'failed'}")

        return FollowUpResponse(
            success=result['success'],
            output=result.get('strategy', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in strategy analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing follow-up strategy: {str(e)}"
        )


@router.get("/followup-agent/stats", response_model=AgentStatsResponse)
async def get_followup_agent_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get statistics and status information for the Follow-up Agent.

    Returns:
    - Agent name and configuration
    - Number of executions
    - Available tools count
    - Memory usage
    - Performance metrics
    """
    try:
        logger.info("📊 Follow-up Agent: Getting agent statistics")

        # Create agent
        agent = create_followup_agent(db)

        # Get statistics
        stats = agent.get_stats()

        return AgentStatsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ Error getting agent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent statistics: {str(e)}"
        )


# WebSocket endpoint for real-time follow-up operations
@router.websocket("/followup-agent/ws")
async def followup_agent_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time follow-up operations.

    Allows streaming results as the agent processes requests.

    Message format:
    - Client sends: {"type": "optimize_timing", "data": {...}}
    - Client sends: {"type": "draft_message", "data": {...}}
    - Client sends: {"type": "analyze_strategy", "data": {...}}
    - Server sends: {"type": "operation_complete", "data": {...}}
    """
    await websocket.accept()
    logger.info("🔌 Follow-up Agent WebSocket connection established")

    try:
        db = DatabaseManager()
        agent = create_followup_agent(db)

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")
            request_data = data.get("data", {})

            if message_type == "optimize_timing":
                # Send acknowledgment
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "timing_optimization", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.optimize_followup_timing(
                        job_id=request_data.get("job_id"),
                        status=request_data.get("status"),
                        days_since_contact=request_data.get("days_since_contact"),
                        application_date=request_data.get("application_date"),
                        metadata=request_data.get("metadata")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket timing optimization: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "draft_message":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "message_drafting", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.draft_followup(
                        followup_type=request_data.get("followup_type"),
                        company=request_data.get("company"),
                        position=request_data.get("position"),
                        tone=request_data.get("tone", "professional"),
                        context_notes=request_data.get("context_notes", ""),
                        metadata=request_data.get("metadata")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket message drafting: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "analyze_strategy":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "strategy_analysis", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.analyze_strategy(
                        status=request_data.get("status"),
                        days_since_application=request_data.get("days_since_application"),
                        response_history=request_data.get("response_history"),
                        priority=request_data.get("priority", "medium"),
                        metadata=request_data.get("metadata")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket strategy analysis: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"error": f"Unknown message type: {message_type}"}
                })

    except WebSocketDisconnect:
        logger.info("🔌 Follow-up Agent WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# Job Hunter Agent Endpoints
@router.post("/job-hunter/search", response_model=JobSearchResponse)
async def search_jobs(
    request: JobSearchRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Search for jobs across multiple platforms using the Job Hunter Agent.

    This endpoint uses AI to:
    - Search LinkedIn, Indeed, and Glassdoor for job listings
    - Extract job details and requirements
    - Match jobs to user preferences
    - Calculate match scores
    - Research companies
    - Save high-quality recommendations

    Returns comprehensive job search results with rankings.
    """
    try:
        logger.info(f"🔍 Job Hunter: Searching for '{request.keywords}' jobs in '{request.location or 'any location'}'")

        # Create agent
        agent = create_job_hunter_agent(db)

        # Search for jobs
        result = await agent.search_jobs(
            keywords=request.keywords,
            location=request.location,
            platforms=request.platforms,
            filters=request.filters
        )

        logger.info(f"✅ Job search {'successful' if result['success'] else 'failed'}")

        return JobSearchResponse(**result)

    except Exception as e:
        logger.error(f"❌ Error in job search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for jobs: {str(e)}"
        )


@router.post("/job-hunter/recommendations", response_model=JobRecommendationsResponse)
async def get_job_recommendations(
    request: JobRecommendationsRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get personalized job recommendations using the Job Hunter Agent.

    This endpoint uses AI to:
    - Analyze user preferences and profile
    - Search multiple job boards
    - Calculate match scores for all jobs
    - Research companies
    - Rank and filter recommendations

    Returns top job recommendations tailored to the user's preferences.
    """
    try:
        logger.info(f"💼 Job Hunter: Getting recommendations for user {request.user_id}")

        # Create agent
        agent = create_job_hunter_agent(db)

        # Get recommendations
        result = await agent.get_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )

        logger.info(f"✅ Job recommendations {'successful' if result['success'] else 'failed'}")

        return JobRecommendationsResponse(**result)

    except Exception as e:
        logger.error(f"❌ Error getting job recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting job recommendations: {str(e)}"
        )


@router.get("/job-hunter/stats", response_model=AgentStatsResponse)
async def get_job_hunter_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get statistics and status information for the Job Hunter Agent.

    Returns:
    - Agent name and configuration
    - Number of executions
    - Available tools count
    - Memory usage
    - Performance metrics
    """
    try:
        logger.info("📊 Job Hunter: Getting agent statistics")

        # Create agent
        agent = create_job_hunter_agent(db)

        # Get statistics
        stats = agent.get_stats()

        return AgentStatsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ Error getting agent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent statistics: {str(e)}"
        )


# WebSocket endpoint for real-time job search
@router.websocket("/job-hunter/ws")
async def job_hunter_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time job search and recommendations.

    Allows streaming job search results as the agent processes them.

    Message format:
    - Client sends: {"type": "search", "data": {"keywords": "...", "location": "...", ...}}
    - Client sends: {"type": "recommendations", "data": {"user_id": 1, "limit": 10}}
    - Server sends: {"type": "search_progress", "data": {...}} (during processing)
    - Server sends: {"type": "search_complete", "data": {...}} (when done)
    """
    await websocket.accept()
    logger.info("🔌 Job Hunter WebSocket connection established")

    try:
        db = DatabaseManager()
        agent = create_job_hunter_agent(db)

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "search":
                search_data = data.get("data", {})

                # Send acknowledgment
                await websocket.send_json({
                    "type": "search_started",
                    "data": {"timestamp": datetime.now().isoformat()}
                })

                try:
                    # Perform job search
                    result = await agent.search_jobs(
                        keywords=search_data.get("keywords", ""),
                        location=search_data.get("location", ""),
                        platforms=search_data.get("platforms"),
                        filters=search_data.get("filters")
                    )

                    # Send complete result
                    await websocket.send_json({
                        "type": "search_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket search: {e}")
                    await websocket.send_json({
                        "type": "search_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "recommendations":
                rec_data = data.get("data", {})

                # Send acknowledgment
                await websocket.send_json({
                    "type": "recommendations_started",
                    "data": {"timestamp": datetime.now().isoformat()}
                })

                try:
                    # Get recommendations
                    result = await agent.get_recommendations(
                        user_id=rec_data.get("user_id", 1),
                        limit=rec_data.get("limit", 10)
                    )

                    # Send complete result
                    await websocket.send_json({
                        "type": "recommendations_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket recommendations: {e}")
                    await websocket.send_json({
                        "type": "recommendations_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"error": f"Unknown message type: {message_type}"}
                })

    except WebSocketDisconnect:
        logger.info("🔌 Job Hunter WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# Future agent endpoints can be added here
# Example structure for other agents:

# @router.post("/application-manager/analyze")
# async def analyze_application(...)
