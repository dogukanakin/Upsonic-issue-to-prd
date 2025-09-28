from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class GitHubUser(BaseModel):
    login: str
    id: int
    avatar_url: str
    html_url: str


class GitHubLabel(BaseModel):
    name: str
    color: str
    description: Optional[str] = None


class GitHubComment(BaseModel):
    id: int
    user: GitHubUser
    body: str
    created_at: str
    updated_at: str


class GitHubIssue(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    user: GitHubUser
    labels: List[GitHubLabel] = []
    state: str
    created_at: str
    updated_at: str
    html_url: str
    comments: List[GitHubComment] = []


class IssueAnalysisRequest(BaseModel):
    github_url: str


class IssueAnalysisResponse(BaseModel):
    issue: GitHubIssue
    related_files: List[str] = []
    analysis_summary: str
    prd_document: str
    issue_keywords: List[str] = []
    semantic_concepts: List[str] = []
