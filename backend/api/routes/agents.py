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
from agents_framework.agents.application_manager_agent import create_application_manager_agent

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


# ============================================================================
# Application Manager Agent Endpoints
# ============================================================================

class ApplicationManagementRequest(BaseModel):
    """Request model for application management"""
    application_id: int = Field(..., description="Application ID to manage")
    context: Optional[str] = Field(None, description="Additional context (e.g., recent email)")

    class Config:
        json_schema_extra = {
            "example": {
                "application_id": 1,
                "context": "Just received interview invitation email"
            }
        }


class PortfolioAnalysisRequest(BaseModel):
    """Request model for portfolio analysis"""
    focus_area: Optional[str] = Field("all", description="Focus area: all, timeline, success_rate")

    class Config:
        json_schema_extra = {
            "example": {
                "focus_area": "all"
            }
        }


@router.post("/application-manager/manage")
async def manage_application(
    request: ApplicationManagementRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Comprehensively manage a job application with AI insights.

    This endpoint uses AI to:
    - Predict application lifecycle and next stages
    - Calculate application health score (0-100)
    - Recommend specific next actions with priorities
    - Provide strategic guidance

    Returns comprehensive management insights and recommendations.
    """
    try:
        logger.info(f"📊 Application Manager: Managing application {request.application_id}")

        # Create agent
        agent = create_application_manager_agent(db)

        # Manage application
        result = await agent.manage_application(
            application_id=request.application_id,
            context=request.context
        )

        logger.info(f"✅ Application management {'successful' if result['success'] else 'failed'}")

        return result

    except Exception as e:
        logger.error(f"❌ Error managing application: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error managing application: {str(e)}"
        )


@router.post("/application-manager/portfolio")
async def analyze_portfolio(
    request: PortfolioAnalysisRequest,
    db: DatabaseManager = Depends(get_db)
):
    """
    Analyze entire application portfolio for strategic insights.

    This endpoint uses AI to:
    - Identify success patterns across all applications
    - Calculate overall success rate and metrics
    - Provide strategic recommendations
    - Highlight strongest and weakest applications
    - Suggest portfolio optimization strategies

    Useful for understanding overall job search performance.
    """
    try:
        logger.info("📊 Application Manager: Analyzing portfolio")

        # Create agent
        agent = create_application_manager_agent(db)

        # Analyze portfolio
        result = await agent.analyze_portfolio()

        logger.info(f"✅ Portfolio analysis {'successful' if result['success'] else 'failed'}")

        return result

    except Exception as e:
        logger.error(f"❌ Error analyzing portfolio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing portfolio: {str(e)}"
        )


@router.get("/application-manager/lifecycle/{application_id}")
async def get_lifecycle_prediction(
    application_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get lifecycle prediction for a specific application.

    Returns:
    - Current stage
    - Predicted next stages with probabilities
    - Typical timelines
    - Application health status
    """
    try:
        logger.info(f"📊 Application Manager: Predicting lifecycle for {application_id}")

        # Create agent (we'll just use the tool directly for this simple case)
        agent = create_application_manager_agent(db)

        # Get the predict_lifecycle tool
        predict_tool = next(t for t in agent.tools if t.name == "predict_lifecycle")

        # Run the tool
        result = predict_tool.func(str(application_id))

        return {
            "success": True,
            "application_id": application_id,
            "prediction": result
        }

    except Exception as e:
        logger.error(f"❌ Error predicting lifecycle: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting lifecycle: {str(e)}"
        )


@router.get("/application-manager/health/{application_id}")
async def get_health_score(
    application_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get health score for a specific application.

    Returns:
    - Health score (0-100)
    - Health rating (EXCELLENT, GOOD, FAIR, POOR)
    - Score breakdown
    - Recommendations
    """
    try:
        logger.info(f"📊 Application Manager: Calculating health for {application_id}")

        # Create agent
        agent = create_application_manager_agent(db)

        # Get the calculate_health_score tool
        health_tool = next(t for t in agent.tools if t.name == "calculate_health_score")

        # Run the tool
        result = health_tool.func(str(application_id))

        return {
            "success": True,
            "application_id": application_id,
            "health_analysis": result
        }

    except Exception as e:
        logger.error(f"❌ Error calculating health: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating health: {str(e)}"
        )


@router.get("/application-manager/actions/{application_id}")
async def get_next_actions(
    application_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """
    Get recommended next actions for a specific application.

    Returns:
    - Immediate actions (next 7 days) with priorities
    - Long-term actions
    - Timelines for each action
    - Priority levels (critical, high, medium, low)
    """
    try:
        logger.info(f"📊 Application Manager: Getting actions for {application_id}")

        # Create agent
        agent = create_application_manager_agent(db)

        # Get the recommend_next_actions tool
        actions_tool = next(t for t in agent.tools if t.name == "recommend_next_actions")

        # Run the tool
        result = actions_tool.func(str(application_id))

        return {
            "success": True,
            "application_id": application_id,
            "actions": result
        }

    except Exception as e:
        logger.error(f"❌ Error getting actions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting actions: {str(e)}"
        )


@router.get("/application-manager/patterns")
async def get_success_patterns(db: DatabaseManager = Depends(get_db)):
    """
    Identify success patterns across all applications.

    Returns:
    - Success rate statistics
    - Status distribution
    - Average response times
    - Key insights and recommendations
    """
    try:
        logger.info("📊 Application Manager: Identifying patterns")

        # Create agent
        agent = create_application_manager_agent(db)

        # Get the identify_patterns tool
        patterns_tool = next(t for t in agent.tools if t.name == "identify_patterns")

        # Run the tool
        result = patterns_tool.func()

        return {
            "success": True,
            "patterns": result
        }

    except Exception as e:
        logger.error(f"❌ Error identifying patterns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error identifying patterns: {str(e)}"
        )


@router.get("/application-manager/insights")
async def get_insights(
    focus: str = "all",
    db: DatabaseManager = Depends(get_db)
):
    """
    Generate actionable insights about job search.

    Parameters:
    - focus: Focus area (general, timeline, success_rate, recommendations, all)

    Returns comprehensive insights based on focus area.
    """
    try:
        logger.info(f"📊 Application Manager: Generating insights (focus: {focus})")

        # Create agent
        agent = create_application_manager_agent(db)

        # Get the generate_insights tool
        insights_tool = next(t for t in agent.tools if t.name == "generate_insights")

        # Run the tool
        result = insights_tool.func(focus)

        return {
            "success": True,
            "focus": focus,
            "insights": result
        }

    except Exception as e:
        logger.error(f"❌ Error generating insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating insights: {str(e)}"
        )


# Future agent endpoints will be added below
