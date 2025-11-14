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
from agents_framework.agents.resume_writer_agent import create_resume_writer_agent
from agents_framework.agents.analytics_agent import create_analytics_agent

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


# Resume Writer Agent Request/Response Models
class ResumeAnalysisRequest(BaseModel):
    """Request model for resume analysis"""
    resume_text: str = Field(..., description="Resume content to analyze")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "resume_text": "John Doe\\nSoftware Engineer\\n\\nExperience:\\n- Developed web applications...",
                "metadata": {}
            }
        }


class ResumeTailorRequest(BaseModel):
    """Request model for resume tailoring"""
    job_title: str = Field(..., description="Target job title")
    job_requirements: str = Field(..., description="Key requirements from job description")
    candidate_experience: str = Field(..., description="Candidate's relevant experience")
    keywords: str = Field("", description="Target keywords from job description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Senior Software Engineer",
                "job_requirements": "5+ years Python, React, AWS experience. Strong communication skills.",
                "candidate_experience": "6 years full-stack development with Python/React",
                "keywords": "Python, React, AWS, Agile, REST API",
                "metadata": {}
            }
        }


class CoverLetterRequest(BaseModel):
    """Request model for cover letter generation"""
    company: str = Field(..., description="Target company name")
    position: str = Field(..., description="Job position")
    motivation: str = Field(..., description="Key motivation for applying")
    achievement: str = Field("", description="Relevant achievement to highlight")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Google",
                "position": "Software Engineer",
                "motivation": "passion for scalable systems",
                "achievement": "led a team that reduced API latency by 60%",
                "metadata": {}
            }
        }


class ResumeWriterResponse(BaseModel):
    """Response model for resume writer operations"""
    success: bool
    output: str
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


# Resume Writer Agent Endpoints
@router.post("/resume-writer/analyze", response_model=ResumeWriterResponse)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze a resume and provide comprehensive feedback.

    This endpoint uses AI to:
    - Parse resume sections and structure
    - Check ATS (Applicant Tracking System) compatibility
    - Identify strengths and weaknesses
    - Provide specific improvement recommendations
    - Analyze content metrics and formatting

    Returns detailed analysis with actionable insights.
    """
    try:
        logger.info(f"📄 Resume Writer: Analyzing resume ({len(request.resume_text)} chars)")

        # Create agent
        agent = create_resume_writer_agent(db)

        # Analyze resume
        result = await agent.analyze_resume(
            resume_text=request.resume_text,
            metadata=request.metadata
        )

        logger.info(f"✅ Resume analysis {'successful' if result['success'] else 'failed'}")

        return ResumeWriterResponse(
            success=result['success'],
            output=result.get('analysis', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in resume analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )


@router.post("/resume-writer/tailor", response_model=ResumeWriterResponse)
async def tailor_resume(
    request: ResumeTailorRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Tailor a resume for a specific job posting.

    This endpoint uses AI to:
    - Match resume keywords to job requirements
    - Optimize content for target role
    - Suggest specific phrasing and content changes
    - Recommend experience highlighting
    - Provide keyword placement strategies

    Returns comprehensive tailoring recommendations.
    """
    try:
        logger.info(f"🎯 Resume Writer: Tailoring resume for {request.job_title}")

        # Create agent
        agent = create_resume_writer_agent(db)

        # Tailor resume
        result = await agent.tailor_for_job(
            job_title=request.job_title,
            job_requirements=request.job_requirements,
            candidate_experience=request.candidate_experience,
            keywords=request.keywords,
            metadata=request.metadata
        )

        logger.info(f"✅ Resume tailoring {'successful' if result['success'] else 'failed'}")

        return ResumeWriterResponse(
            success=result['success'],
            output=result.get('recommendations', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in resume tailoring: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error tailoring resume: {str(e)}"
        )


@router.post("/resume-writer/cover-letter", response_model=ResumeWriterResponse)
async def generate_cover_letter(
    request: CoverLetterRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Generate a compelling cover letter.

    This endpoint uses AI to:
    - Create personalized opening paragraphs
    - Provide multiple style options (achievement, passion, value-focused)
    - Include company-specific customization tips
    - Offer subject line suggestions
    - Provide personalization checklists

    Returns complete cover letter content and guidance.
    """
    try:
        logger.info(f"✉️ Resume Writer: Generating cover letter for {request.company}")

        # Create agent
        agent = create_resume_writer_agent(db)

        # Generate cover letter
        result = await agent.generate_cover_letter(
            company=request.company,
            position=request.position,
            motivation=request.motivation,
            achievement=request.achievement,
            metadata=request.metadata
        )

        logger.info(f"✅ Cover letter generation {'successful' if result['success'] else 'failed'}")

        return ResumeWriterResponse(
            success=result['success'],
            output=result.get('cover_letter', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in cover letter generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover letter: {str(e)}"
        )


@router.get("/resume-writer/stats", response_model=AgentStatsResponse)
async def get_resume_writer_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get statistics and status information for the Resume Writer Agent.

    Returns:
    - Agent name and configuration
    - Number of executions
    - Available tools count
    - Memory usage
    - Performance metrics
    """
    try:
        logger.info("📊 Resume Writer: Getting agent statistics")

        # Create agent
        agent = create_resume_writer_agent(db)

        # Get statistics
        stats = agent.get_stats()

        return AgentStatsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ Error getting agent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent statistics: {str(e)}"
        )


# WebSocket endpoint for real-time resume writing operations
@router.websocket("/resume-writer/ws")
async def resume_writer_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time resume writing operations.

    Allows streaming results as the agent processes requests.

    Message format:
    - Client sends: {"type": "analyze", "data": {"resume_text": "..."}}
    - Client sends: {"type": "tailor", "data": {...}}
    - Client sends: {"type": "cover_letter", "data": {...}}
    - Server sends: {"type": "operation_complete", "data": {...}}
    """
    await websocket.accept()
    logger.info("🔌 Resume Writer WebSocket connection established")

    try:
        db = DatabaseManager()
        agent = create_resume_writer_agent(db)

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")
            request_data = data.get("data", {})

            if message_type == "analyze":
                # Send acknowledgment
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "resume_analysis", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.analyze_resume(
                        resume_text=request_data.get("resume_text", ""),
                        metadata=request_data.get("metadata")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket resume analysis: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "tailor":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "resume_tailoring", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.tailor_for_job(
                        job_title=request_data.get("job_title", ""),
                        job_requirements=request_data.get("job_requirements", ""),
                        candidate_experience=request_data.get("candidate_experience", ""),
                        keywords=request_data.get("keywords", ""),
                        metadata=request_data.get("metadata")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket resume tailoring: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "cover_letter":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "cover_letter_generation", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.generate_cover_letter(
                        company=request_data.get("company", ""),
                        position=request_data.get("position", ""),
                        motivation=request_data.get("motivation", ""),
                        achievement=request_data.get("achievement", ""),
                        metadata=request_data.get("metadata")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket cover letter generation: {e}")
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
        logger.info("🔌 Resume Writer WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# Analytics Agent Request/Response Models
class AnalyticsDataRequest(BaseModel):
    """Request model for analytics data analysis"""
    user_id: int = Field(1, description="User ID to analyze")
    time_period_days: int = Field(90, description="Number of days to analyze")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "time_period_days": 90
            }
        }


class SuccessPatternsRequest(BaseModel):
    """Request model for success pattern analysis"""
    user_id: int = Field(1, description="User ID to analyze")
    min_confidence: float = Field(0.7, description="Minimum confidence threshold (0.0-1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "min_confidence": 0.7
            }
        }


class OfferPredictionRequest(BaseModel):
    """Request model for offer likelihood prediction"""
    job_details: Dict[str, Any] = Field(..., description="Job information")
    user_profile: Dict[str, Any] = Field(..., description="User profile information")

    class Config:
        json_schema_extra = {
            "example": {
                "job_details": {
                    "title": "Software Engineer",
                    "company_size": "Medium",
                    "industry": "Technology"
                },
                "user_profile": {
                    "skills_match_percent": 75,
                    "has_referral": False,
                    "has_cover_letter": True,
                    "years_experience": 5,
                    "application_quality_score": 8.0
                }
            }
        }


class StrategyRequest(BaseModel):
    """Request model for optimization strategy"""
    current_stats: Dict[str, Any] = Field(..., description="Current performance statistics")
    target_role: str = Field(..., description="Target job role")

    class Config:
        json_schema_extra = {
            "example": {
                "current_stats": {
                    "success_rate": 0.067,
                    "applications_per_week": 10
                },
                "target_role": "Software Engineer"
            }
        }


class SalaryAnalysisRequest(BaseModel):
    """Request model for salary analysis"""
    job_title: str = Field(..., description="Job title/role")
    location: str = Field(..., description="Geographic location")
    years_experience: int = Field(..., description="Years of experience")
    industry: str = Field("Technology", description="Industry sector")
    company_size: str = Field("Medium", description="Company size category")

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Software Engineer",
                "location": "San Francisco, CA",
                "years_experience": 5,
                "industry": "Technology",
                "company_size": "Medium"
            }
        }


class AnalyticsResponse(BaseModel):
    """Response model for analytics operations"""
    success: bool
    analysis: Optional[str] = None
    patterns: Optional[str] = None
    prediction: Optional[str] = None
    strategy: Optional[str] = None
    salary_analysis: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Analytics Agent Endpoints
@router.post("/analytics/analyze-data", response_model=AnalyticsResponse)
async def analyze_application_data(
    request: AnalyticsDataRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze job application data and provide comprehensive insights.

    This endpoint uses AI to:
    - Calculate overall statistics and trends
    - Analyze conversion rates at each application stage
    - Compute response time metrics
    - Break down applications by industry and company size
    - Generate actionable insights and recommendations

    Returns detailed data analysis with key metrics and trends.
    """
    try:
        logger.info(f"📊 Analytics: Analyzing data for user {request.user_id} over {request.time_period_days} days")

        # Create agent
        agent = create_analytics_agent(db)

        # Analyze application data
        result = await agent.analyze_application_data(
            user_id=request.user_id,
            time_period_days=request.time_period_days
        )

        logger.info(f"✅ Data analysis {'successful' if result['success'] else 'failed'}")

        return AnalyticsResponse(
            success=result['success'],
            analysis=result.get('analysis'),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in data analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing application data: {str(e)}"
        )


@router.post("/analytics/success-patterns", response_model=AnalyticsResponse)
async def identify_success_patterns(
    request: SuccessPatternsRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Identify patterns that correlate with successful job application outcomes.

    This endpoint uses AI to:
    - Analyze application timing patterns
    - Evaluate application quality factors
    - Identify successful company characteristics
    - Study effective follow-up strategies
    - Assess skills alignment impact

    Returns identified patterns with confidence scores and recommendations.
    """
    try:
        logger.info(f"🔍 Analytics: Identifying success patterns for user {request.user_id}")

        # Create agent
        agent = create_analytics_agent(db)

        # Get success patterns
        result = await agent.get_success_patterns(
            user_id=request.user_id,
            min_confidence=request.min_confidence
        )

        logger.info(f"✅ Pattern analysis {'successful' if result['success'] else 'failed'}")

        return AnalyticsResponse(
            success=result['success'],
            patterns=result.get('patterns'),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in pattern analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error identifying success patterns: {str(e)}"
        )


@router.post("/analytics/predict-offer", response_model=AnalyticsResponse)
async def predict_offer_likelihood(
    request: OfferPredictionRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Predict the likelihood of receiving a job offer.

    This endpoint uses AI to:
    - Calculate offer probability based on multiple factors
    - Analyze contributing strengths and weaknesses
    - Identify areas for improvement
    - Provide specific recommendations to increase success chances
    - Estimate probabilities for each stage (screening, interview, offer)

    Returns prediction with confidence level and actionable recommendations.
    """
    try:
        job_title = request.job_details.get("title", "Unknown")
        logger.info(f"🎯 Analytics: Predicting offer likelihood for {job_title}")

        # Create agent
        agent = create_analytics_agent(db)

        # Predict offer likelihood
        result = await agent.predict_offer_success(
            job_details=request.job_details,
            user_profile=request.user_profile
        )

        logger.info(f"✅ Offer prediction {'successful' if result['success'] else 'failed'}")

        return AnalyticsResponse(
            success=result['success'],
            prediction=result.get('prediction'),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in offer prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting offer likelihood: {str(e)}"
        )


@router.post("/analytics/strategy", response_model=AnalyticsResponse)
async def get_optimization_strategy(
    request: StrategyRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Generate personalized job search optimization strategy.

    This endpoint uses AI to:
    - Analyze current performance metrics
    - Identify strategic priorities based on data
    - Provide tactical actions with timelines
    - Recommend resource allocation
    - Set realistic expected outcomes

    Returns comprehensive strategy with prioritized recommendations.
    """
    try:
        logger.info(f"🎯 Analytics: Generating optimization strategy for {request.target_role}")

        # Create agent
        agent = create_analytics_agent(db)

        # Get optimization strategy
        result = await agent.get_optimization_strategy(
            current_stats=request.current_stats,
            target_role=request.target_role
        )

        logger.info(f"✅ Strategy generation {'successful' if result['success'] else 'failed'}")

        return AnalyticsResponse(
            success=result['success'],
            strategy=result.get('strategy'),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in strategy generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating optimization strategy: {str(e)}"
        )


@router.post("/analytics/salary", response_model=AnalyticsResponse)
async def analyze_market_salary(
    request: SalaryAnalysisRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze market salary data for a given role and location.

    This endpoint uses AI to:
    - Provide salary ranges by percentile (p10, p25, median, p75, p90)
    - Break down total compensation (base, bonus, equity)
    - Share market insights and trends
    - Offer negotiation strategies
    - List benefits to consider

    Returns comprehensive salary analysis with negotiation guidance.
    """
    try:
        logger.info(f"💰 Analytics: Analyzing salary for {request.job_title} in {request.location}")

        # Create agent
        agent = create_analytics_agent(db)

        # Get salary insights
        result = await agent.get_salary_insights(
            job_title=request.job_title,
            location=request.location,
            years_experience=request.years_experience,
            industry=request.industry,
            company_size=request.company_size
        )

        logger.info(f"✅ Salary analysis {'successful' if result['success'] else 'failed'}")

        return AnalyticsResponse(
            success=result['success'],
            salary_analysis=result.get('salary_analysis'),
            metadata=result.get('metadata'),
            error=result.get('error')
        )

    except Exception as e:
        logger.error(f"❌ Error in salary analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing market salary: {str(e)}"
        )


@router.get("/analytics/stats", response_model=AgentStatsResponse)
async def get_analytics_agent_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get statistics and status information for the Analytics Agent.

    Returns:
    - Agent name and configuration
    - Number of executions
    - Available tools count
    - Memory usage
    - Performance metrics
    """
    try:
        logger.info("📊 Analytics: Getting agent statistics")

        # Create agent
        agent = create_analytics_agent(db)

        # Get statistics
        stats = agent.get_stats()

        return AgentStatsResponse(**stats)

    except Exception as e:
        logger.error(f"❌ Error getting agent stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent statistics: {str(e)}"
        )


# WebSocket endpoint for real-time analytics operations
@router.websocket("/analytics/ws")
async def analytics_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analytics operations.

    Allows streaming analytics results as the agent processes them.

    Message format:
    - Client sends: {"type": "analyze_data", "data": {...}}
    - Client sends: {"type": "success_patterns", "data": {...}}
    - Client sends: {"type": "predict_offer", "data": {...}}
    - Client sends: {"type": "strategy", "data": {...}}
    - Client sends: {"type": "salary", "data": {...}}
    - Server sends: {"type": "operation_complete", "data": {...}}
    """
    await websocket.accept()
    logger.info("🔌 Analytics WebSocket connection established")

    try:
        db = DatabaseManager()
        agent = create_analytics_agent(db)

        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message_type = data.get("type")
            request_data = data.get("data", {})

            if message_type == "analyze_data":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "data_analysis", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.analyze_application_data(
                        user_id=request_data.get("user_id", 1),
                        time_period_days=request_data.get("time_period_days", 90)
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket data analysis: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "success_patterns":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "pattern_analysis", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.get_success_patterns(
                        user_id=request_data.get("user_id", 1),
                        min_confidence=request_data.get("min_confidence", 0.7)
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket pattern analysis: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "predict_offer":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "offer_prediction", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.predict_offer_success(
                        job_details=request_data.get("job_details", {}),
                        user_profile=request_data.get("user_profile", {})
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket offer prediction: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "strategy":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "strategy_generation", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.get_optimization_strategy(
                        current_stats=request_data.get("current_stats", {}),
                        target_role=request_data.get("target_role", "Software Engineer")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket strategy generation: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "salary":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"operation": "salary_analysis", "timestamp": datetime.now().isoformat()}
                })

                try:
                    result = await agent.get_salary_insights(
                        job_title=request_data.get("job_title", "Software Engineer"),
                        location=request_data.get("location", "San Francisco, CA"),
                        years_experience=request_data.get("years_experience", 5),
                        industry=request_data.get("industry", "Technology"),
                        company_size=request_data.get("company_size", "Medium")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket salary analysis: {e}")
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
        logger.info("🔌 Analytics WebSocket connection closed")
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
