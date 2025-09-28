from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
from typing import Dict, Any

from models.issue import IssueAnalysisRequest, IssueAnalysisResponse, GitHubIssue
from models.prd import PRDDocument
from services.github_service import GitHubService, GitHubTool
from services.codebase_analyzer import CodebaseAnalyzer, CodebaseTool
from services.prd_generator import PRDGenerator, PRDTool

# Load environment variables
load_dotenv()
print(f"Environment loaded - OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"GITHUB_TOKEN: {'SET' if os.getenv('GITHUB_TOKEN') else 'NOT SET'}")

# Initialize FastAPI app
app = FastAPI(
    title="Issue to PRD Generator",
    description="Convert GitHub issues to comprehensive Product Requirement Documents using AI analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
github_service = GitHubService()
codebase_analyzer = CodebaseAnalyzer()
prd_generator = PRDGenerator()

# Create tool instances for direct use
try:
    github_tool = GitHubTool()
    codebase_tool = CodebaseTool()
    prd_tool = PRDTool()

    # Upsonic is available if services have agents (they will have models if properly configured)
    UPSONIC_AVAILABLE = (
        codebase_analyzer.agent is not None and
        prd_generator.agent is not None
    )

    print(f"Tools initialized - Upsonic available: {UPSONIC_AVAILABLE}")
except Exception as e:
    # Fallback when tools fail to initialize
    print(f"Tool initialization failed: {e}")
    github_tool = None
    codebase_tool = None
    prd_tool = None
    UPSONIC_AVAILABLE = False


@app.get("/")
async def root():
    """Redirect to the main interface"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "github_api": "connected" if github_service.token else "not_configured",
            "codebase_analyzer": "initialized" if codebase_analyzer.agent else "fallback_mode",
            "prd_generator": "initialized" if prd_generator.agent else "template_mode",
            "tools": {
                "github_tool": "available" if github_tool else "unavailable",
                "codebase_tool": "available" if codebase_tool else "unavailable",
                "prd_tool": "available" if prd_tool else "unavailable"
            },
            "upsonic": {
                "available": UPSONIC_AVAILABLE if 'UPSONIC_AVAILABLE' in locals() else False,
                "task_based_workflow": "enabled" if UPSONIC_AVAILABLE else "disabled",
                "tool_integration": "enabled" if UPSONIC_AVAILABLE else "disabled"
            }
        }
    }


@app.post("/analyze-issue", response_model=IssueAnalysisResponse)
async def analyze_issue(request: IssueAnalysisRequest):
    """
    Analyze a GitHub issue and generate a comprehensive PRD
    
    Args:
        request: Contains the GitHub issue URL
        
    Returns:
        Complete analysis including issue data, related files, and PRD document
    """
    try:
        print(f"Starting analysis for GitHub issue: {request.github_url}")
        
        # Step 1: Fetch issue from GitHub
        try:
            issue = await github_service.fetch_issue(request.github_url)
            print(f"Successfully fetched issue: {issue.title}")
        except Exception as e:
            print(f"Failed to fetch GitHub issue: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch GitHub issue: {str(e)}"
            )
        
        # Step 2: Analyze issue with codebase
        try:
            analysis_data = await codebase_analyzer.analyze_issue_with_codebase(issue)
            print(f"Completed codebase analysis. Found {len(analysis_data.get('relevant_files', []))} relevant files")
            # Ensure keywords are included
            if not analysis_data.get('issue_keywords'):
                analysis_data['issue_keywords'] = codebase_analyzer.extract_keywords_from_issue(issue)
        except Exception as e:
            print(f"Codebase analysis failed, using fallback: {str(e)}")
            analysis_data = {
                "analysis": "Automated analysis unavailable, manual review recommended",
                "relevant_files": [],
                "issue_keywords": codebase_analyzer.extract_keywords_from_issue(issue)
            }
        
        # Step 3: Generate PRD document
        try:
            prd_document = await prd_generator.generate_prd(issue, analysis_data)
            print(f"Successfully generated PRD: {prd_document.title}")
        except Exception as e:
            print(f"PRD generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate PRD document: {str(e)}"
            )
        
        # Step 4: Prepare response
        response = IssueAnalysisResponse(
            issue=issue.to_simplified_dict(),
            related_files=analysis_data.get('relevant_files', []),
            analysis_summary=analysis_data.get('analysis', 'No analysis available'),
            prd_document=prd_document.to_markdown(),
            issue_keywords=analysis_data.get('issue_keywords', []),
            semantic_concepts=analysis_data.get('semantic_concepts', [])
        )
        
        print("Analysis completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in analyze_issue: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )




@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    print(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Check if required environment variables are set
    if not os.getenv("GITHUB_TOKEN"):
        print("Warning: GITHUB_TOKEN not found in environment variables")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
    
    print("Starting Issue to PRD Generator...")
    print("Web Interface: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
