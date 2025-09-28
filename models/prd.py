from pydantic import BaseModel
from typing import List, Optional


class TechnicalRequirement(BaseModel):
    description: str
    priority: str  # "High", "Medium", "Low"
    category: str  # "Backend", "Frontend", "Database", etc.


class FileModification(BaseModel):
    file_path: str
    reason: str
    suggested_changes: str


class UseCase(BaseModel):
    title: str
    description: str
    acceptance_criteria: List[str]


class PRDDocument(BaseModel):
    title: str
    overview: str
    problem_statement: str
    use_cases: List[UseCase]
    file_modifications: List[FileModification]
    constraints: List[str]
    
    def to_markdown(self) -> str:
        """Convert PRD to markdown format"""
        md_content = f"""# {self.title}

## Overview
{self.overview}

## Problem Statement
{self.problem_statement}

## Use Cases
"""
        for i, use_case in enumerate(self.use_cases, 1):
            md_content += f"\n### {i}. {use_case.title}\n{use_case.description}\n\n**Acceptance Criteria:**\n"
            for criterion in use_case.acceptance_criteria:
                md_content += f"- {criterion}\n"
            md_content += "\n"
        
        md_content += "\n## Suggested File Modifications\n"
        for file_mod in self.file_modifications:
            md_content += f"\n### {file_mod.file_path}\n**Reason:** {file_mod.reason}\n\n**Suggested Changes:**\n{file_mod.suggested_changes}\n\n"
        
        if self.constraints:
            md_content += "## Constraints\n"
            for constraint in self.constraints:
                md_content += f"- {constraint}\n"
            md_content += "\n"
        
        return md_content
