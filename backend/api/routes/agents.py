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
from agents_framework.agents.interview_prep_agent import create_interview_prep_agent
from agents_framework.agents.orchestrator_agent import create_orchestrator_agent

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


# ============================================================================
# INTERVIEW PREP AGENT ENDPOINTS
# ============================================================================

# Interview Prep Agent Request/Response Models

class InterviewPrepRequest(BaseModel):
    """Request model for comprehensive interview preparation"""
    job_id: Optional[int] = Field(None, description="Job application ID")
    company_name: str = Field(..., description="Company name")
    job_title: str = Field(..., description="Job title/position")
    job_description: str = Field("", description="Full job description")
    interview_date: Optional[str] = Field(None, description="Interview date (YYYY-MM-DD)")
    interview_type: str = Field("general", description="Interview type: phone, video, in-person, technical, behavioral, panel, final")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": 123,
                "company_name": "Google",
                "job_title": "Senior Software Engineer",
                "job_description": "We are looking for a senior software engineer...",
                "interview_date": "2025-12-01",
                "interview_type": "technical",
                "metadata": {}
            }
        }


class QuestionGenerationRequest(BaseModel):
    """Request model for generating interview questions"""
    job_title: str = Field(..., description="Job title/position")
    job_description: str = Field("", description="Job description")
    company_name: str = Field("", description="Company name")
    question_type: str = Field("mixed", description="Type: behavioral, technical, situational, or mixed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Product Manager",
                "job_description": "Lead product strategy and development...",
                "company_name": "Microsoft",
                "question_type": "mixed",
                "metadata": {}
            }
        }


class STARAnswerRequest(BaseModel):
    """Request model for STAR format answer preparation"""
    question: str = Field(..., description="The interview question to answer")
    experience_context: str = Field("", description="Optional context about relevant experience")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Tell me about a time when you faced a significant challenge at work",
                "experience_context": "I worked on a complex microservices migration project",
                "metadata": {}
            }
        }


class MockInterviewRequest(BaseModel):
    """Request model for starting a mock interview"""
    job_title: str = Field(..., description="Job title/position")
    focus_area: str = Field("general", description="Focus area: behavioral, technical, company-fit, or general")
    difficulty: str = Field("medium", description="Difficulty: entry, medium, or senior")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "job_title": "Data Scientist",
                "focus_area": "technical",
                "difficulty": "senior",
                "metadata": {}
            }
        }


class InterviewTipsRequest(BaseModel):
    """Request model for getting interview tips"""
    interview_stage: str = Field("general", description="Interview stage: phone-screen, technical, behavioral, panel, final, or general")
    role_level: str = Field("mid", description="Role level: entry, mid, senior, or executive")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "interview_stage": "technical",
                "role_level": "senior",
                "metadata": {}
            }
        }


class InterviewChecklistRequest(BaseModel):
    """Request model for getting interview checklist"""
    interview_date: str = Field("", description="Interview date (YYYY-MM-DD)")
    interview_type: str = Field("general", description="Interview type: phone, video, in-person, technical, or general")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "interview_date": "2025-12-15",
                "interview_type": "video",
                "metadata": {}
            }
        }


class InterviewPrepResponse(BaseModel):
    """Response model for interview prep operations"""
    success: bool
    preparation_plan: Optional[str] = None
    questions: Optional[str] = None
    star_framework: Optional[str] = None
    mock_interview: Optional[str] = None
    tips: Optional[str] = None
    checklist: Optional[str] = None
    output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Interview Prep Agent Endpoints

@router.post("/interview-prep/prepare", response_model=InterviewPrepResponse)
async def prepare_for_interview(
    request: InterviewPrepRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Comprehensive interview preparation for a job application.

    This endpoint provides:
    - Company research and insights
    - Job description analysis
    - Relevant interview questions
    - Preparation timeline and checklist
    """
    try:
        logger.info(f"🎯 Interview Prep: Preparing for {request.job_title} at {request.company_name}")

        agent = create_interview_prep_agent(db)

        result = await agent.prepare_for_interview(
            job_id=request.job_id,
            company_name=request.company_name,
            job_title=request.job_title,
            job_description=request.job_description,
            interview_date=request.interview_date or "",
            interview_type=request.interview_type
        )

        logger.info(f"✅ Interview preparation {'successful' if result['success'] else 'failed'}")

        return InterviewPrepResponse(
            success=result["success"],
            preparation_plan=result.get("preparation_plan"),
            output=result.get("preparation_plan"),
            metadata=result.get("metadata"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"❌ Error in interview preparation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep/generate-questions", response_model=InterviewPrepResponse)
async def generate_interview_questions(
    request: QuestionGenerationRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Generate relevant interview questions for a specific role.

    Provides:
    - Behavioral questions (STAR format)
    - Technical questions (role-specific)
    - Situational questions
    - Company-fit questions
    """
    try:
        logger.info(f"❓ Interview Prep: Generating {request.question_type} questions for {request.job_title}")

        agent = create_interview_prep_agent(db)

        result = await agent.generate_practice_questions(
            job_title=request.job_title,
            company_name=request.company_name,
            job_description=request.job_description,
            question_type=request.question_type,
            difficulty="medium"
        )

        logger.info(f"✅ Question generation {'successful' if result['success'] else 'failed'}")

        return InterviewPrepResponse(
            success=result["success"],
            questions=result.get("questions"),
            output=result.get("questions"),
            metadata=result.get("metadata"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"❌ Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep/star-answer", response_model=InterviewPrepResponse)
async def prepare_star_answer(
    request: STARAnswerRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Help prepare a STAR format answer for a specific interview question.

    STAR = Situation, Task, Action, Result

    Provides:
    - STAR format framework
    - Tips for answering effectively
    - Example structure
    """
    try:
        logger.info(f"⭐ Interview Prep: Preparing STAR answer for question")

        agent = create_interview_prep_agent(db)

        result = await agent.practice_star_answer(
            question=request.question,
            experience_context=request.experience_context
        )

        logger.info(f"✅ STAR answer preparation {'successful' if result['success'] else 'failed'}")

        return InterviewPrepResponse(
            success=result["success"],
            star_framework=result.get("star_framework"),
            output=result.get("star_framework"),
            metadata=result.get("metadata"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"❌ Error preparing STAR answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep/mock-interview", response_model=InterviewPrepResponse)
async def start_mock_interview(
    request: MockInterviewRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Start a mock interview practice session.

    Provides:
    - Practice questions based on role and difficulty
    - Self-evaluation framework
    - Performance tracking
    """
    try:
        logger.info(f"🎭 Interview Prep: Starting mock interview for {request.job_title}")

        agent = create_interview_prep_agent(db)

        result = await agent.start_mock_interview(
            job_title=request.job_title,
            focus_area=request.focus_area,
            difficulty=request.difficulty
        )

        logger.info(f"✅ Mock interview {'started' if result['success'] else 'failed'}")

        return InterviewPrepResponse(
            success=result["success"],
            mock_interview=result.get("mock_interview"),
            output=result.get("mock_interview"),
            metadata=result.get("metadata"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"❌ Error starting mock interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep/tips", response_model=InterviewPrepResponse)
async def get_interview_tips(
    request: InterviewTipsRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get interview tips and strategies based on interview stage and role level.

    Provides:
    - Stage-specific tips
    - Role-level guidance
    - Best practices
    - Common mistakes to avoid
    """
    try:
        logger.info(f"💡 Interview Prep: Getting tips for {request.interview_stage} interview ({request.role_level} level)")

        agent = create_interview_prep_agent(db)

        # Use the agent to get tips
        query = f"Provide interview tips for a {request.interview_stage} interview at {request.role_level} level"
        response = await agent.run(query, context={
            "interview_stage": request.interview_stage,
            "role_level": request.role_level
        })

        logger.info(f"✅ Tips retrieval {'successful' if response.success else 'failed'}")

        return InterviewPrepResponse(
            success=response.success,
            tips=response.output,
            output=response.output,
            metadata=response.metadata,
            error=response.error
        )

    except Exception as e:
        logger.error(f"❌ Error getting interview tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interview-prep/checklist", response_model=InterviewPrepResponse)
async def get_interview_checklist(
    request: InterviewChecklistRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get a comprehensive interview preparation checklist with timeline.

    Provides:
    - Preparation timeline
    - Type-specific checklist items
    - Day-of-interview checklist
    - Post-interview steps
    """
    try:
        logger.info(f"📋 Interview Prep: Getting checklist for {request.interview_type} interview")

        agent = create_interview_prep_agent(db)

        # Use the agent to get checklist
        query = f"Generate interview preparation checklist for {request.interview_type} interview"
        if request.interview_date:
            query += f" on {request.interview_date}"

        response = await agent.run(query, context={
            "interview_date": request.interview_date,
            "interview_type": request.interview_type
        })

        logger.info(f"✅ Checklist generation {'successful' if response.success else 'failed'}")

        return InterviewPrepResponse(
            success=response.success,
            checklist=response.output,
            output=response.output,
            metadata=response.metadata,
            error=response.error
        )

    except Exception as e:
        logger.error(f"❌ Error generating checklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interview-prep/stats", response_model=AgentStatsResponse)
async def get_interview_prep_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get Interview Prep Agent statistics and performance metrics.
    """
    try:
        logger.info("📊 Interview Prep: Fetching agent statistics")

        agent = create_interview_prep_agent(db)
        stats = agent.get_stats()

        return AgentStatsResponse(
            name=stats["name"],
            execution_count=stats["execution_count"],
            tools_count=stats["tools_count"],
            memory_size=stats["memory_size"]
        )

    except Exception as e:
        logger.error(f"❌ Error fetching interview prep stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/interview-prep/ws")
async def interview_prep_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time interview preparation.

    Supported message types:
    - prepare: Comprehensive interview preparation
    - generate_questions: Generate interview questions
    - star_answer: Prepare STAR format answer
    - mock_interview: Start mock interview
    - tips: Get interview tips
    - checklist: Get preparation checklist
    - ping: Connection health check
    """
    await websocket.accept()
    logger.info("🔌 Interview Prep WebSocket connection established")

    db = DatabaseManager()
    agent = create_interview_prep_agent(db)

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            request_data = data.get("data", {})

            logger.info(f"📨 Received WebSocket message: {message_type}")

            if message_type == "prepare":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Preparing for interview..."}
                })

                try:
                    result = await agent.prepare_for_interview(
                        job_id=request_data.get("job_id"),
                        company_name=request_data.get("company_name", ""),
                        job_title=request_data.get("job_title", ""),
                        job_description=request_data.get("job_description", ""),
                        interview_date=request_data.get("interview_date", ""),
                        interview_type=request_data.get("interview_type", "general")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket interview preparation: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "generate_questions":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Generating interview questions..."}
                })

                try:
                    result = await agent.generate_practice_questions(
                        job_title=request_data.get("job_title", ""),
                        company_name=request_data.get("company_name", ""),
                        job_description=request_data.get("job_description", ""),
                        question_type=request_data.get("question_type", "mixed"),
                        difficulty=request_data.get("difficulty", "medium")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket question generation: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "star_answer":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Preparing STAR answer..."}
                })

                try:
                    result = await agent.practice_star_answer(
                        question=request_data.get("question", ""),
                        experience_context=request_data.get("experience_context", "")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket STAR answer: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "mock_interview":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Starting mock interview..."}
                })

                try:
                    result = await agent.start_mock_interview(
                        job_title=request_data.get("job_title", ""),
                        focus_area=request_data.get("focus_area", "general"),
                        difficulty=request_data.get("difficulty", "medium")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket mock interview: {e}")
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
        logger.info("🔌 Interview Prep WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass


# ============================================================================
# ORCHESTRATOR AGENT ENDPOINTS
# ============================================================================

# Orchestrator Agent Request/Response Models

class WorkflowTaskDefinition(BaseModel):
    """Definition of a task in a workflow"""
    agent_name: str = Field(..., description="Name of the agent to execute this task")
    task_description: str = Field(..., description="Description of what the task should do")
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input data for the task")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="IDs of tasks this task depends on")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class WorkflowExecutionRequest(BaseModel):
    """Request model for executing a multi-agent workflow"""
    workflow_name: str = Field(..., description="Name of the workflow")
    workflow_description: str = Field(..., description="Description of what the workflow does")
    tasks: List[WorkflowTaskDefinition] = Field(..., description="List of tasks in the workflow")
    execution_mode: str = Field("sequential", description="Execution mode: sequential or parallel")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_name": "Job Application Workflow",
                "workflow_description": "Search for jobs, tailor resume, and draft cover letter",
                "execution_mode": "sequential",
                "tasks": [
                    {
                        "agent_name": "Job Hunter",
                        "task_description": "Search for Software Engineer jobs in San Francisco",
                        "input_data": {"keywords": "Software Engineer", "location": "San Francisco"}
                    },
                    {
                        "agent_name": "Resume Writer",
                        "task_description": "Tailor resume for the top job match",
                        "input_data": {}
                    }
                ]
            }
        }


class RouteTaskRequest(BaseModel):
    """Request model for routing a task to a specific agent"""
    agent_name: str = Field(..., description="Name of the agent to route to")
    task: str = Field(..., description="Task description")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "Email Analyst",
                "task": "Analyze this job interview invitation email",
                "context": {"urgency": "high"}
            }
        }


class CoordinateAgentsRequest(BaseModel):
    """Request model for coordinating multiple agents"""
    task: str = Field(..., description="The complex task requiring multiple agents")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "Help me apply to a Software Engineer position at Google - search for the job, tailor my resume, generate a cover letter, and prepare for the interview",
                "context": {}
            }
        }


class OrchestratorResponse(BaseModel):
    """Response model for orchestrator operations"""
    success: bool
    output: Optional[str] = None
    workflow_id: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status"""
    workflow_id: str
    status: str
    task_count: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    running_tasks: int


class OrchestratorStatsResponse(BaseModel):
    """Response model for orchestrator statistics"""
    name: str
    execution_count: int
    tools_count: int
    memory_size: int
    registered_agents: List[str]
    workflow_stats: Dict[str, Any]
    communication_stats: Dict[str, Any]


# Orchestrator Agent Endpoints

@router.post("/orchestrator/execute-workflow", response_model=OrchestratorResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Execute a multi-agent workflow.

    This endpoint allows you to coordinate multiple agents in a workflow:
    - Define tasks for each agent
    - Specify execution order (sequential or parallel)
    - Set dependencies between tasks
    - Get aggregated results

    Perfect for complex, multi-step operations that require multiple specialized agents.
    """
    try:
        logger.info(f"🎭 Orchestrator: Executing workflow '{request.workflow_name}' with {len(request.tasks)} tasks")

        # Create orchestrator
        orchestrator = create_orchestrator_agent(db)

        # Convert task definitions to dict format
        tasks = [
            {
                "agent_name": task.agent_name,
                "task_description": task.task_description,
                "input_data": task.input_data or {},
                "dependencies": task.dependencies or [],
                "metadata": task.metadata
            }
            for task in request.tasks
        ]

        # Execute workflow
        result = await orchestrator.execute_workflow(
            workflow_name=request.workflow_name,
            workflow_description=request.workflow_description,
            tasks=tasks,
            execution_mode=request.execution_mode
        )

        logger.info(f"✅ Workflow execution {'successful' if result.get('success') else 'failed'}")

        return OrchestratorResponse(
            success=result.get("success", False),
            workflow_id=result.get("workflow_id"),
            results=result.get("results"),
            metadata=result.get("metadata"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"❌ Error executing workflow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing workflow: {str(e)}"
        )


@router.post("/orchestrator/route-task", response_model=OrchestratorResponse)
async def route_task_to_agent(
    request: RouteTaskRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Route a task directly to a specific agent.

    Use this when you know exactly which agent should handle a task.
    The orchestrator will:
    - Validate the agent exists
    - Route the task to the agent
    - Return the agent's response
    """
    try:
        logger.info(f"🎯 Orchestrator: Routing task to {request.agent_name}")

        # Create orchestrator
        orchestrator = create_orchestrator_agent(db)

        # Route task
        result = await orchestrator.route_to_agent(
            agent_name=request.agent_name,
            task=request.task,
            context=request.context
        )

        logger.info(f"✅ Task routing {'successful' if result.success else 'failed'}")

        return OrchestratorResponse(
            success=result.success,
            output=result.output,
            metadata=result.metadata,
            error=result.error
        )

    except Exception as e:
        logger.error(f"❌ Error routing task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error routing task: {str(e)}"
        )


@router.post("/orchestrator/coordinate", response_model=OrchestratorResponse)
async def coordinate_agents(
    request: CoordinateAgentsRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Coordinate multiple agents to complete a complex task.

    The orchestrator will:
    - Analyze the task
    - Determine which agents are needed
    - Create an optimal workflow
    - Execute the workflow
    - Synthesize results

    This is the most intelligent endpoint - just describe what you want to accomplish,
    and the orchestrator will figure out how to coordinate the agents.
    """
    try:
        logger.info(f"🎭 Orchestrator: Coordinating agents for complex task")

        # Create orchestrator
        orchestrator = create_orchestrator_agent(db)

        # Coordinate agents
        result = await orchestrator.coordinate_agents(
            task=request.task,
            context=request.context
        )

        logger.info(f"✅ Agent coordination {'successful' if result.get('success') else 'failed'}")

        return OrchestratorResponse(
            success=result.get("success", False),
            output=result.get("plan") or result.get("message"),
            metadata=result.get("metadata"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"❌ Error coordinating agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error coordinating agents: {str(e)}"
        )


@router.get("/orchestrator/workflow-status/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get the status of a running or completed workflow.

    Returns:
    - Workflow status (pending, running, completed, failed)
    - Task completion statistics
    - Progress information
    """
    try:
        logger.info(f"📊 Orchestrator: Getting status for workflow {workflow_id}")

        # Create orchestrator
        orchestrator = create_orchestrator_agent(db)

        # Get status
        status = orchestrator.get_workflow_status(workflow_id)

        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found"
            )

        return WorkflowStatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting workflow status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting workflow status: {str(e)}"
        )


@router.get("/orchestrator/stats", response_model=OrchestratorStatsResponse)
async def get_orchestrator_stats(db: DatabaseManager = Depends(get_db)):
    """
    Get Orchestrator Agent statistics and performance metrics.

    Returns:
    - Number of registered agents
    - Workflow execution statistics
    - Communication protocol statistics
    - Agent performance metrics
    """
    try:
        logger.info("📊 Orchestrator: Getting agent statistics")

        # Create orchestrator
        orchestrator = create_orchestrator_agent(db)

        # Get statistics
        stats = orchestrator.get_orchestrator_stats()

        return OrchestratorStatsResponse(
            name=stats["name"],
            execution_count=stats["execution_count"],
            tools_count=stats["tools_count"],
            memory_size=stats["memory_size"],
            registered_agents=stats["registered_agents"],
            workflow_stats=stats["workflow_stats"],
            communication_stats=stats["communication_stats"]
        )

    except Exception as e:
        logger.error(f"❌ Error getting orchestrator stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving orchestrator statistics: {str(e)}"
        )


@router.websocket("/orchestrator/ws")
async def orchestrator_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time orchestrator operations.

    Supported message types:
    - execute_workflow: Execute a multi-agent workflow
    - route_task: Route task to specific agent
    - coordinate: Coordinate multiple agents
    - workflow_status: Get workflow status
    - ping: Connection health check
    """
    await websocket.accept()
    logger.info("🔌 Orchestrator WebSocket connection established")

    db = DatabaseManager()
    orchestrator = create_orchestrator_agent(db)

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            request_data = data.get("data", {})

            logger.info(f"📨 Received Orchestrator WebSocket message: {message_type}")

            if message_type == "execute_workflow":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Executing workflow..."}
                })

                try:
                    result = await orchestrator.execute_workflow(
                        workflow_name=request_data.get("workflow_name", ""),
                        workflow_description=request_data.get("workflow_description", ""),
                        tasks=request_data.get("tasks", []),
                        execution_mode=request_data.get("execution_mode", "sequential")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket workflow execution: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "route_task":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Routing task..."}
                })

                try:
                    result = await orchestrator.route_to_agent(
                        agent_name=request_data.get("agent_name", ""),
                        task=request_data.get("task", ""),
                        context=request_data.get("context")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": {
                            "success": result.success,
                            "output": result.output,
                            "metadata": result.metadata,
                            "error": result.error
                        }
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket task routing: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "coordinate":
                await websocket.send_json({
                    "type": "operation_started",
                    "data": {"message": "Coordinating agents..."}
                })

                try:
                    result = await orchestrator.coordinate_agents(
                        task=request_data.get("task", ""),
                        context=request_data.get("context")
                    )

                    await websocket.send_json({
                        "type": "operation_complete",
                        "data": result
                    })

                except Exception as e:
                    logger.error(f"❌ Error in WebSocket agent coordination: {e}")
                    await websocket.send_json({
                        "type": "operation_error",
                        "data": {"error": str(e)}
                    })

            elif message_type == "workflow_status":
                try:
                    workflow_id = request_data.get("workflow_id")
                    status = orchestrator.get_workflow_status(workflow_id)

                    await websocket.send_json({
                        "type": "status_update",
                        "data": status if status else {"error": "Workflow not found"}
                    })

                except Exception as e:
                    logger.error(f"❌ Error getting workflow status: {e}")
                    await websocket.send_json({
                        "type": "error",
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
        logger.info("🔌 Orchestrator WebSocket connection closed")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
