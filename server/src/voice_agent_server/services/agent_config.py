import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId

from agents import Agent, function_tool
from agents.tool import UserLocation

# Import database operations
from .database import (
    create_application_with_dedup,
    update_application_status,
    add_note_to_application,
    schedule_followup,
    search_applications,
    get_application_summary,
    find_application_by_reference
)

STYLE_INSTRUCTIONS = """
You are a helpful job application tracking assistant. You can communicate in multiple languages:
- English (primary)
- Spanish (español)
- French (français)
- German (deutsch)

When users speak in any of these languages, respond in the same language they used.
Use a conversational tone and respond naturally to voice commands.
When users speak about job applications, help them track their progress through the hiring pipeline.
Always provide clear, actionable responses and confirm actions taken.

Example responses:
- English: "I've added your application to Google for Software Engineer position."
- Spanish: "He agregado tu solicitud a Google para el puesto de Ingeniero de Software."
- French: "J'ai ajouté votre candidature chez Google pour le poste d'Ingénieur Logiciel."
- German: "Ich habe Ihre Bewerbung bei Google für die Position als Software-Ingenieur hinzugefügt."
"""

@function_tool
async def add_job_application(company: str, role_title: str, location: Optional[str] = None, 
                       source: Optional[str] = None, job_post_url: Optional[str] = None,
                       status_stage: str = "draft", salary_min: Optional[float] = None,
                       salary_max: Optional[float] = None, currency: str = "USD",
                       remote_ok: Optional[bool] = None, skills_required: Optional[List[str]] = None,
                       job_posted_date: Optional[str] = None, due_at: Optional[str] = None,
                       channel: Optional[str] = None, note: Optional[str] = None) -> str:
    """
    Add a new job application or update existing one within 14-day window.
    
    Args:
        company: Company name (required)
        role_title: Job title (required)
        location: Job location (e.g., "Mountain View, CA")
        source: Application source (e.g., "LinkedIn", "Referral")
        job_post_url: URL to the job posting
        status_stage: Current status (draft, applied, hr_screen, tech_screen, onsite, offer, rejected, withdrawn)
        salary_min: Minimum salary
        salary_max: Maximum salary
        currency: Salary currency (USD, EUR, etc.)
        remote_ok: Whether remote work is available
        skills_required: List of required skills
        job_posted_date: When job was posted (ISO date)
        due_at: Follow-up due date (ISO date)
        channel: Follow-up channel (email, linkedin, call)
        note: Initial note for the application
    """
    try:
        # Prepare application data
        app_data = {
            "company": company,
            "role_title": role_title,
            "location": location,
            "source": source,
            "job_post_url": job_post_url,
            "status_stage": status_stage,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "currency": currency,
            "remote_ok": remote_ok,
            "skills_required": skills_required or [],
            "job_posted_date": job_posted_date
        }
        
        # Create application with deduplication
        result = await create_application_with_dedup(app_data)
        
        # Add note if provided
        if note:
            await add_note_to_application(result["application_id"], note)
        
        # Schedule follow-up if provided
        if due_at and channel:
            await schedule_followup(result["application_id"], due_at, channel)
        
        return json.dumps({
            "success": True,
            "message": result["message"],
            "application_id": result["application_id"],
            "updated": result.get("updated", False)
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@function_tool
async def update_application_status_by_reference(application_ref: str, status_stage: str) -> str:
    """
    Update the status of an existing application by company name or role title.
    
    Args:
        application_ref: Company name or role title to identify the application
        status_stage: New status (draft, applied, hr_screen, tech_screen, onsite, offer, rejected, withdrawn)
    """
    try:
        # Find application by reference
        application = await find_application_by_reference(application_ref)
        
        if not application:
            return json.dumps({
                "success": False,
                "error": f"No application found for '{application_ref}'"
            })
        
        # Update status
        success = await update_application_status(str(application["_id"]), status_stage)
        
        if success:
            return json.dumps({
                "success": True,
                "message": f"Status updated to {status_stage} for {application['company']} {application['role_title']}",
                "application_id": str(application["_id"])
            })
        else:
            return json.dumps({
                "success": False,
                "error": "Failed to update application status"
            })
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@function_tool
async def add_note_to_application_by_reference(application_ref: str, note: str) -> str:
    """
    Add a note to an existing application by company name or role title.
    
    Args:
        application_ref: Company name or role title to identify the application
        note: Note content to add
    """
    try:
        # Find application by reference
        application = await find_application_by_reference(application_ref)
        
        if not application:
            return json.dumps({
                "success": False,
                "error": f"No application found for '{application_ref}'"
            })
        
        # Add note
        note_id = await add_note_to_application(str(application["_id"]), note)
        
        return json.dumps({
            "success": True,
            "message": f"Note added for {application['company']} {application['role_title']}",
            "application_id": str(application["_id"]),
            "note_id": note_id
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@function_tool
async def schedule_followup_by_reference(application_ref: str, due_at: str, channel: str = "email", note: Optional[str] = None) -> str:
    """
    Schedule a follow-up reminder for an application by company name or role title.
    
    Args:
        application_ref: Company name or role title to identify the application
        due_at: Follow-up due date (ISO date)
        channel: Follow-up channel (email, linkedin, call)
        note: Optional note for the follow-up
    """
    try:
        # Find application by reference
        application = await find_application_by_reference(application_ref)
        
        if not application:
            return json.dumps({
                "success": False,
                "error": f"No application found for '{application_ref}'"
            })
        
        # Schedule follow-up
        followup_id = await schedule_followup(str(application["_id"]), due_at, channel, note)
        
        return json.dumps({
            "success": True,
            "message": f"Follow-up scheduled for {application['company']} on {due_at}",
            "application_id": str(application["_id"]),
            "followup_id": followup_id
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@function_tool
async def search_job_applications(query: str = "", status_stage: Optional[str] = None, 
                          company: Optional[str] = None, time_range: Optional[str] = None) -> str:
    """
    Search and retrieve job applications with various filters.
    
    Args:
        query: General search query
        status_stage: Filter by status (draft, applied, hr_screen, tech_screen, onsite, offer, rejected, withdrawn)
        company: Filter by company name
        time_range: Filter by time range (last_week, this_week, last_month, this_month)
    """
    try:
        # Build search criteria
        criteria = {}
        if status_stage:
            criteria["status_stage"] = status_stage
        if company:
            criteria["company"] = company
        if time_range:
            criteria["time_range"] = time_range
        
        # Search applications
        applications = await search_applications(criteria)
        
        # Format the response for better readability
        if not applications:
            return json.dumps({
                "success": True,
                "message": "No applications found matching your criteria.",
                "applications": [],
                "count": 0
            })
        
        # Create a summary for voice response
        status_counts = {}
        companies = set()
        for app in applications:
            status = app.get("status_stage", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            companies.add(app.get("company", "Unknown"))
        
        summary_parts = []
        for status, count in status_counts.items():
            summary_parts.append(f"{count} {status}")
        
        summary = f"Found {len(applications)} applications: {', '.join(summary_parts)}"
        if companies:
            summary += f" at companies including {', '.join(list(companies)[:3])}"
        
        return json.dumps({
            "success": True,
            "message": summary,
            "applications": applications,
            "count": len(applications),
            "status_breakdown": status_counts
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@function_tool
async def get_all_applications() -> str:
    """
    Get all job applications in the user's pipeline.
    """
    try:
        # Get all applications
        applications = await search_applications({})
        
        if not applications:
            return json.dumps({
                "success": True,
                "message": "You don't have any job applications in your pipeline yet.",
                "applications": [],
                "count": 0
            })
        
        # Group by status for better organization
        status_groups = {}
        for app in applications:
            status = app.get("status_stage", "unknown")
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(app)
        
        # Create a summary
        summary_parts = []
        for status, apps in status_groups.items():
            summary_parts.append(f"{len(apps)} {status}")
        
        summary = f"You have {len(applications)} total applications: {', '.join(summary_parts)}"
        
        # Add some details about recent applications
        recent_apps = sorted(applications, key=lambda x: x.get("created_at", ""), reverse=True)[:3]
        if recent_apps:
            recent_companies = [app.get("company", "Unknown") for app in recent_apps]
            summary += f". Your most recent applications are at {', '.join(recent_companies)}"
        
        return json.dumps({
            "success": True,
            "message": summary,
            "applications": applications,
            "count": len(applications),
            "status_groups": status_groups
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@function_tool
async def get_pipeline_summary() -> str:
    """
    Get a summary of the job application pipeline and statistics.
    """
    try:
        summary = await get_application_summary()
        
        return json.dumps({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

# Create the main job tracking agent
job_tracking_agent = Agent(
    name="Job Application Tracker",
    instructions=f"""
You are a helpful job application tracking assistant. {STYLE_INSTRUCTIONS}

Your primary functions:
1. Help users add new job applications with company name, role title, and optional details
2. Update application status through the hiring pipeline (draft → applied → hr_screen → tech_screen → onsite → offer/rejected)
3. Add notes to applications for important details
4. Schedule follow-up reminders for applications
5. Search and retrieve applications based on various criteria
6. Provide pipeline summaries and insights
7. Show all applications in the user's to-do list/pipeline

When users speak naturally about their job search, interpret their intent and use the appropriate function.
Always confirm actions taken and provide helpful feedback.

For requests like "show me my applications", "what applications do I have", "my to-do list", use get_all_applications.
For specific searches like "draft applications" or "applications from last week", use search_job_applications.

Example voice commands you can handle:
- "Add Google Software Engineer in Mountain View"
- "Update status to applied for Microsoft"
- "Add note: Had great conversation with hiring manager"
- "Schedule follow-up for next Friday"
- "Show me all applications from last week"
- "What's my pipeline status?"
- "Show me my to-do list"
- "What applications do I have?"
""",
    model="gpt-4o-mini",
    tools=[
        add_job_application,
        update_application_status_by_reference,
        add_note_to_application_by_reference,
        schedule_followup_by_reference,
        search_job_applications,
        get_all_applications,
        get_pipeline_summary
    ],
)

# Set as the starting agent
starting_agent = job_tracking_agent
