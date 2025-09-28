from typing import Dict, Any, List
from models.issue import GitHubIssue
from models.prd import PRDDocument, TechnicalRequirement, FileModification, UseCase

try:
    import upsonic
    UPSONIC_AVAILABLE = True
except ImportError:
    UPSONIC_AVAILABLE = False
    print("Upsonic not available in PRD generator, using template mode")

# Custom PRD Tool for Upsonic
class PRDTool:
    """Custom tool for PRD document generation"""

    async def generate_prd_content(self, issue_title: str, issue_body: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PRD content based on issue and analysis data"""
        # Extract key information
        issue_type = self._determine_issue_type_from_text(issue_title, issue_body or "")
        priority = self._determine_priority_from_text(issue_title, issue_body or "")

        # Generate PRD sections
        title = f"PRD: {issue_title}"
        overview = self._generate_overview(issue_title, issue_type)
        problem_statement = self._generate_problem_statement(issue_title, issue_body, analysis_data)
        use_cases = self._generate_use_cases(issue_title, issue_type)
        file_modifications = self._generate_file_modifications(issue_title, analysis_data)
        constraints = self._generate_constraints(issue_type)

        return {
            "title": title,
            "overview": overview,
            "problem_statement": problem_statement,
            "use_cases": use_cases,
            "file_modifications": file_modifications,
            "constraints": constraints,
            "priority": priority,
            "issue_type": issue_type
        }

    def _determine_issue_type_from_text(self, title: str, body: str) -> str:
        """Determine issue type from text content"""
        text_lower = (title + " " + body).lower()

        if any(word in text_lower for word in ['bug', 'error', 'fix']):
            return "bug_fix"
        elif any(word in text_lower for word in ['feature', 'enhancement', 'new']):
            return "feature"
        elif any(word in text_lower for word in ['documentation', 'docs']):
            return "documentation"
        elif any(word in text_lower for word in ['refactor', 'cleanup']):
            return "refactor"
        else:
            return "general"

    def _determine_priority_from_text(self, title: str, body: str) -> str:
        """Determine priority from text content"""
        text_lower = (title + " " + body).lower()

        if any(word in text_lower for word in ['critical', 'urgent', 'high']):
            return "High"
        elif any(word in text_lower for word in ['medium', 'normal']):
            return "Medium"
        else:
            return "Low"

    def _generate_overview(self, title: str, issue_type: str) -> str:
        """Generate overview section"""
        type_descriptions = {
            "bug_fix": "This PRD addresses a bug fix requirement",
            "feature": "This PRD outlines the development of a new feature",
            "documentation": "This PRD focuses on documentation improvements",
            "refactor": "This PRD covers code refactoring and improvements",
            "general": "This PRD addresses the reported issue"
        }

        base_description = type_descriptions.get(issue_type, "This PRD addresses the reported issue")
        return f"{base_description} based on: '{title}'. The goal is to provide a clear roadmap for resolution while maintaining code quality and system stability."

    def _generate_problem_statement(self, title: str, body: str, analysis_data: Dict[str, Any]) -> str:
        """Generate problem statement"""
        problem = f"**Issue**: {title}\n\n"

        if body:
            problem += f"**Description**: {body[:500]}{'...' if len(body) > 500 else ''}\n\n"

        # Add analysis context if available
        if analysis_data.get('relevant_files'):
            problem += f"**Relevant Files Identified**: {len(analysis_data['relevant_files'])} files may need attention\n\n"

        return problem

    def _generate_use_cases(self, title: str, issue_type: str) -> List[Dict[str, Any]]:
        """Generate use cases"""
        if issue_type == "bug_fix":
            return [{
                "title": "Bug Resolution",
                "description": f"As a user/developer, I need the issue '{title}' to be resolved so that the system works as expected.",
                "acceptance_criteria": [
                    "The reported issue no longer occurs",
                    "No new issues are introduced",
                    "Existing functionality remains intact",
                    "Changes are properly tested"
                ]
            }]
        elif issue_type == "feature":
            return [{
                "title": "New Feature Implementation",
                "description": f"As a user, I want the new feature '{title}' to be implemented to enhance functionality.",
                "acceptance_criteria": [
                    "Feature works as described",
                    "Feature integrates seamlessly with existing code",
                    "Proper error handling is implemented",
                    "Documentation is updated"
                ]
            }]
        else:
            return [{
                "title": "Issue Resolution",
                "description": f"Resolve the issue: {title}",
                "acceptance_criteria": [
                    "Issue requirements are met",
                    "Solution is properly tested",
                    "Code follows project standards"
                ]
            }]

    def _generate_file_modifications(self, title: str, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate file modification suggestions"""
        modifications = []
        relevant_files = analysis_data.get('relevant_files', [])

        # Add relevant files as modification suggestions
        for file_path in relevant_files[:5]:  # Top 5 files
            modifications.append({
                "file_path": file_path,
                "reason": "Identified as relevant to the issue based on analysis",
                "suggested_changes": "Review and modify as needed to resolve the issue"
            })

        return modifications

    def _generate_constraints(self, issue_type: str) -> List[str]:
        """Generate constraints"""
        constraints = [
            "Must maintain backward compatibility",
            "Must follow existing code patterns and standards",
            "Must include appropriate error handling"
        ]

        if issue_type == "bug_fix":
            constraints.append("Must not introduce new bugs while fixing the current issue")

        return constraints

# Apply Upsonic decorator if available
if UPSONIC_AVAILABLE:
    PRDTool = upsonic.tool()(PRDTool)
    # Also decorate the method
    PRDTool.generate_prd_content = upsonic.tool()(PRDTool.generate_prd_content)


class PRDGenerator:
    def __init__(self):
        self.agent = None
        self.prd_tool = None
        self.setup_agent()

    def setup_agent(self):
        """Initialize Upsonic agent for PRD generation"""
        if not UPSONIC_AVAILABLE:
            print("Upsonic not available, using template mode")
            self.agent = None
            return

        try:
            self.agent = upsonic.Agent()
            # Configure model provider for the agent
            self.model = upsonic.models.ModelFactory.create('openai/gpt-4o-mini')
            self.prd_tool = PRDTool()  # Decorated tools are auto-discovered
        except Exception as e:
            print(f"Error setting up PRD generator agent: {str(e)}")
            self.agent = None
            self.model = None
    
    async def generate_prd(self, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> PRDDocument:
        """Generate comprehensive PRD document using Task-based workflow"""
        try:
            if self.agent:
                # Create Task-based PRD generation
                prd_task = upsonic.Task(
                    description=f"""Generate comprehensive PRD document for GitHub issue: {issue.title}.

Return a JSON object with the following structure:
{{
  "title": "PRD title",
  "overview": "Brief overview of the PRD",
  "problem_statement": "Detailed problem description",
  "use_cases": [
    {{
      "title": "Use case title",
      "description": "Use case description",
      "acceptance_criteria": ["criterion 1", "criterion 2"]
    }}
  ],
  "file_modifications": [
    {{
      "file_path": "path/to/file.py",
      "reason": "Why this file needs modification",
      "suggested_changes": "Detailed description of changes needed"
    }}
  ],
  "constraints": [
    "Constraint 1: Description",
    "Constraint 2: Description",
    "Constraint 3: Description"
  ]
}}

Make file_modifications specific and actionable with concrete file paths and detailed change descriptions.
Make constraints comprehensive and specific to the issue type.""",
                    tools=["PRDTool"],
                    response_format=str
                )

                # Execute task with configured model
                result = await self.agent.do_async(prd_task, model=self.model)

                # Convert result to PRDDocument
                return self._convert_task_result_to_prd(result, issue, analysis_data)
            else:
                return self.generate_prd_template_based(issue, analysis_data)
        except Exception as e:
            print(f"Error generating PRD: {str(e)}")
            # Ensure we have the issue parameter in scope for fallback
            try:
                return self.generate_prd_template_based(issue, analysis_data)
            except NameError:
                # This should not happen, but just in case
                print("Warning: issue parameter not in scope for fallback")
                return self.generate_prd_template_based(issue, analysis_data)

    def _convert_task_result_to_prd(self, task_result, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> PRDDocument:
        """Convert Task result to PRDDocument"""
        try:
            # Handle string results (JSON)
            if isinstance(task_result, str):
                import json
                # Remove markdown code blocks if present
                clean_result = task_result.strip()
                if clean_result.startswith('```json'):
                    clean_result = clean_result[7:]  # Remove ```json
                if clean_result.startswith('```'):
                    clean_result = clean_result[3:]  # Remove ```
                if clean_result.endswith('```'):
                    clean_result = clean_result[:-3]  # Remove ```
                clean_result = clean_result.strip()

                try:
                    task_result = json.loads(clean_result)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create basic PRD from string
                    return PRDDocument(
                        title=f"PRD: {issue.title}",
                        overview=f"AI-generated PRD based on analysis: {task_result[:500]}...",
                        problem_statement=self.generate_problem_statement(issue, analysis_data),
                        use_cases=[UseCase(
                            title="Issue Resolution",
                            description=f"Resolve issue: {issue.title}",
                            acceptance_criteria=["Requirements are met"]
                        )],
                        file_modifications=[],
                        constraints=["Maintain backward compatibility"]
                    )

            # Extract PRD data from task result
            title = task_result.get("title", f"PRD: {issue.title}")
            overview = task_result.get("overview", self.generate_overview(issue, task_result.get("issue_type", "general")))
            problem_statement = task_result.get("problem_statement", self.generate_problem_statement(issue, analysis_data))

            # Convert use cases
            use_cases_data = task_result.get("use_cases", [])
            use_cases = []
            for uc_data in use_cases_data:
                use_cases.append(UseCase(
                    title=uc_data.get("title", "Issue Resolution"),
                    description=uc_data.get("description", f"Resolve issue: {issue.title}"),
                    acceptance_criteria=uc_data.get("acceptance_criteria", ["Requirements are met"])
                ))

            # Convert file modifications - use template-based if AI result is empty
            file_modifications_data = task_result.get("file_modifications", [])
            if file_modifications_data:
                file_modifications = []
                for fm_data in file_modifications_data:
                    file_modifications.append(FileModification(
                        file_path=fm_data.get("file_path", ""),
                        reason=fm_data.get("reason", "Identified as relevant"),
                        suggested_changes=fm_data.get("suggested_changes", "Review and modify as needed")
                    ))
            else:
                # Use template-based file modifications which are more comprehensive
                file_modifications = self.generate_file_modifications(issue, analysis_data)

            # Get constraints - use template-based if AI result is empty/weak
            ai_constraints = task_result.get("constraints", [])
            if ai_constraints and len(ai_constraints) > 1:
                constraints = ai_constraints
            else:
                # Use template-based constraints which are more comprehensive
                constraints = self.generate_constraints(issue, task_result.get("issue_type", "general"))

            return PRDDocument(
                title=title,
                overview=overview,
                problem_statement=problem_statement,
                use_cases=use_cases,
                file_modifications=file_modifications,
                constraints=constraints
            )

        except Exception as e:
            print(f"Error converting task result to PRD: {str(e)}")
            # Fallback to template-based generation
            return self.generate_prd_template_based(issue, analysis_data)

    async def generate_prd_with_agent(self, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> PRDDocument:
        """Generate PRD using Upsonic agent"""
        
        prd_prompt = f"""
        Create a comprehensive Project Requirements Document (PRD) for this GitHub issue.
        
        Issue Details:
        - Title: {issue.title}
        - Description: {issue.body or 'No description provided'}
        - Labels: {', '.join([label.name for label in issue.labels])}
        - State: {issue.state}
        
        Code Analysis:
        {analysis_data.get('analysis', 'No analysis available')}
        
        Relevant Files:
        {', '.join(analysis_data.get('relevant_files', []))}
        
        Generate a structured PRD with:
        1. Clear title and overview
        2. Problem statement
        3. Use cases with acceptance criteria
        4. Specific file modification suggestions
        5. Constraints
        
        Format as structured data that can be parsed into sections.
        """
        
        prd_content = self.agent.generate(prd_prompt)
        
        # Parse the generated content into structured PRD
        return self.parse_generated_prd(prd_content, issue, analysis_data)
    
    def generate_prd_template_based(self, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> PRDDocument:
        """Generate PRD using template-based approach"""

        # Determine issue type and priority
        issue_type = self.determine_issue_type(issue)
        priority = self.determine_priority(issue)

        # Generate title and overview
        title = f"PRD: {issue.title}"
        overview = self.generate_overview(issue, issue_type)

        # Generate problem statement
        problem_statement = self.generate_problem_statement(issue, analysis_data)

        # Generate use cases
        use_cases = self.generate_use_cases(issue, issue_type)

        # Generate file modifications with issue context
        file_modifications = self.generate_file_modifications(issue, analysis_data)

        # Generate constraints
        constraints = self.generate_constraints(issue, issue_type)

        return PRDDocument(
            title=title,
            overview=overview,
            problem_statement=problem_statement,
            use_cases=use_cases,
            file_modifications=file_modifications,
            constraints=constraints
        )
    
    def determine_issue_type(self, issue: GitHubIssue) -> str:
        """Determine the type of issue (bug, feature, enhancement, etc.)"""
        label_names = [label.name.lower() for label in issue.labels]
        
        if any(label in ['bug', 'error', 'fix'] for label in label_names):
            return "bug_fix"
        elif any(label in ['feature', 'enhancement', 'new'] for label in label_names):
            return "feature"
        elif any(label in ['documentation', 'docs'] for label in label_names):
            return "documentation"
        elif any(label in ['refactor', 'cleanup', 'improvement'] for label in label_names):
            return "refactor"
        else:
            return "general"
    
    def determine_priority(self, issue: GitHubIssue) -> str:
        """Determine priority based on labels and content"""
        label_names = [label.name.lower() for label in issue.labels]
        
        if any(label in ['critical', 'urgent', 'high'] for label in label_names):
            return "High"
        elif any(label in ['medium', 'normal'] for label in label_names):
            return "Medium"
        else:
            return "Low"
    
    def generate_overview(self, issue: GitHubIssue, issue_type: str) -> str:
        """Generate overview section"""
        type_descriptions = {
            "bug_fix": "This PRD addresses a bug fix requirement",
            "feature": "This PRD outlines the development of a new feature",
            "documentation": "This PRD focuses on documentation improvements",
            "refactor": "This PRD covers code refactoring and improvements",
            "general": "This PRD addresses the reported issue"
        }
        
        base_description = type_descriptions.get(issue_type, "This PRD addresses the reported issue")
        
        return f"{base_description} based on GitHub issue #{issue.number}: '{issue.title}'. The goal is to provide a clear roadmap for resolution while maintaining code quality and system stability."
    
    def generate_problem_statement(self, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> str:
        """Generate problem statement with deeper analysis"""
        problem = f"**Issue**: {issue.title}\n\n"
        
        if issue.body:
            # Look for specific technical problems in the issue body
            body = issue.body
            problem += f"**Description**: {body[:500]}{'...' if len(body) > 500 else ''}\n\n"
            
            # Enhanced root cause analysis based on issue context
            if '@tool' in body and 'decorators' in body:
                problem += "**Root Cause Analysis**: Issue appears to be related to incorrect import path. "
                problem += "User is importing from 'upsonic.tools.decorators' which doesn't exist. "
                problem += "Correct import should be from 'upsonic.tools.tool'.\n\n"
            elif 'pricing' in body.lower() or 'dynamic' in body.lower():
                problem += "**Root Cause Analysis**: Current static pricing system in MODEL_REGISTRY has several limitations. "
                problem += "System needs dynamic pricing integration with OpenRouter API for real-time pricing data, "
                problem += "caching mechanisms, and comprehensive model coverage.\n\n"
            elif 'security' in body.lower() or 'vulnerabilit' in body.lower():
                problem += "**Root Cause Analysis**: Security vulnerabilities are being reported publicly in Issues section. "
                problem += "Missing SECURITY.md file with clear reporting guidelines and private vulnerability disclosure process. "
                problem += "Need proper security policy documentation.\n\n"
            elif 'contributing' in body.lower() or 'code_of_conduct' in body.lower():
                problem += "**Root Cause Analysis**: Missing standard community documentation files. "
                problem += "CODE_OF_CONDUCT.md and CONTRIBUTING.md are essential for open source projects. "
                problem += "Also need standardized PR naming conventions and contribution workflow.\n\n"
            elif 'doesn\'t work' in body.lower() or 'currently doesn\'t work' in body.lower():
                problem += "**Issue Type**: Functionality not working as expected\n\n"
            elif 'hang' in body.lower() or 'forever' in body.lower() or 'async' in body.lower():
                problem += "**Root Cause Analysis**: Issue appears to be related to async/sync mismatch in FastAPI. "
                problem += "Agent.do() is a synchronous method being called in an async FastAPI endpoint, "
                problem += "which can cause blocking behavior. Solution requires using agent.do_async() instead.\n\n"
            elif 'process' in body.lower() or 'termination' in body.lower() or 'servermanager' in body.lower():
                problem += "**Root Cause Analysis**: ServerManager.stop() method doesn't properly terminate child processes. "
                problem += "Process tree cleanup is incomplete, leaving orphaned processes running. "
                problem += "Need to implement proper process group termination with SIGTERM/SIGKILL fallback.\n\n"
            elif 'pickle' in body.lower() or 'deserialization' in body.lower() or 'rce' in body.lower():
                problem += "**Root Cause Analysis**: Unsafe pickle deserialization vulnerability allowing Remote Code Execution. "
                problem += "Functions like get_temporary_memory() and add_tool() use pickle.loads() without validation, "
                problem += "enabling arbitrary code execution through crafted serialized data.\n\n"
            elif 'boilerplate' in body.lower():
                problem += "**Issue Type**: Developer experience improvement - reducing boilerplate code\n\n"
        
        # Add codebase context if available
        if analysis_data.get('relevant_files') and len(analysis_data.get('relevant_files', [])) > 0:
            problem += f"**Relevant Files Identified**: {len(analysis_data['relevant_files'])} files may need attention\n\n"
        
        return problem
    
    def generate_use_cases(self, issue: GitHubIssue, issue_type: str) -> List[UseCase]:
        """Generate use cases based on issue type"""
        use_cases = []
        
        if issue_type == "bug_fix":
            use_cases.append(UseCase(
                title="Bug Resolution",
                description=f"As a user/developer, I need the issue '{issue.title}' to be resolved so that the system works as expected.",
                acceptance_criteria=[
                    "The reported issue no longer occurs",
                    "No new issues are introduced",
                    "Existing functionality remains intact",
                    "Changes are properly tested"
                ]
            ))
        
        elif issue_type == "feature":
            use_cases.append(UseCase(
                title="New Feature Implementation",
                description=f"As a user, I want the new feature '{issue.title}' to be implemented to enhance functionality.",
                acceptance_criteria=[
                    "Feature works as described in the issue",
                    "Feature integrates seamlessly with existing code",
                    "Proper error handling is implemented",
                    "Documentation is updated"
                ]
            ))
        
        else:
            use_cases.append(UseCase(
                title="Issue Resolution",
                description=f"Resolve the issue: {issue.title}",
                acceptance_criteria=[
                    "Issue requirements are met",
                    "Solution is properly tested",
                    "Code follows project standards"
                ]
            ))
        
        return use_cases
    
    
    def generate_file_modifications(self, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> List[FileModification]:
        """Generate specific file modification suggestions"""
        modifications = []

        relevant_files = analysis_data.get('relevant_files', [])

        # Context-aware file suggestions based on issue content
        core_files_map = {}

        # Tool/standalone function issues
        if 'standalone' in issue.body.lower() or 'toolkit' in issue.body.lower():
            core_files_map.update({
                'src/upsonic/tools/__init__.py': {
                    'reason': 'Primary import path fix needed',
                    'changes': 'Add import alias: `from .tool import tool as tool`. This will allow users to import the decorator as `from upsonic.tools import tool` instead of the non-existent decorators module.'
                },
                'src/upsonic/tools/tool.py': {
                    'reason': 'Core decorator implementation verification',
                    'changes': 'Verify that @tool decorator properly sets _upsonic_tool_config attribute on decorated functions. Ensure the decorator works correctly with standalone functions.'
                },
                'src/upsonic/tools/processor.py': {
                    'reason': 'Tool validation and processing logic',
                    'changes': 'Review normalize_and_process method to ensure standalone @tool decorated functions are properly recognized and validated. Check that functions with _upsonic_tool_config attribute are handled correctly.'
                }
            })

        # Pricing issues
        if 'pricing' in issue.body.lower() or 'dynamic' in issue.body.lower():
            core_files_map.update({
                'src/upsonic/models/providers.py': {
                    'reason': 'Model pricing data management',
                    'changes': 'Implement dynamic pricing system with OpenRouter API integration. Add caching layer and real-time price fetching capabilities.'
                },
                'src/upsonic/agent/agent.py': {
                    'reason': 'Agent model pricing integration',
                    'changes': 'Integrate dynamic pricing system into agent initialization. Add pricing validation and fallback mechanisms.'
                }
            })

        # Security issues
        if 'security' in issue.body.lower() or 'vulnerabilit' in issue.body.lower():
            core_files_map.update({
                'SECURITY.md': {
                    'reason': 'Security policy documentation',
                    'changes': 'Create comprehensive SECURITY.md file with vulnerability reporting guidelines, private disclosure process, and security contact information.'
                },
                'src/upsonic/safety_engine/__init__.py': {
                    'reason': 'Safety engine integration',
                    'changes': 'Review and enhance safety engine policies for vulnerability detection and prevention mechanisms.'
                }
            })

        # Web API / FastAPI async issues
        if 'hang' in issue.body.lower() or 'forever' in issue.body.lower() or 'fastapi' in issue.body.lower():
            core_files_map.update({
                'src/upsonic/agent/agent.py': {
                    'reason': 'Agent async/sync method implementation',
                    'changes': 'Verify do_async() method exists and works correctly. Ensure proper async handling for FastAPI integration.'
                },
                'examples/fastapi_example.py': {
                    'reason': 'FastAPI integration example',
                    'changes': 'Update FastAPI example to use agent.do_async() instead of agent.do() for async endpoints.'
                }
            })

        # Process/ServerManager issues
        if 'process' in issue.body.lower() or 'termination' in issue.body.lower() or 'servermanager' in issue.body.lower():
            core_files_map.update({
                'src/upsonic/server/level_two/server/server.py': {
                    'reason': 'ServerManager process termination logic',
                    'changes': 'Implement proper child process termination in stop() method using process groups and SIGTERM/SIGKILL fallback.'
                },
                'src/upsonic/server/__init__.py': {
                    'reason': 'Server management utilities',
                    'changes': 'Add process tree cleanup utilities and ensure proper resource cleanup on server shutdown.'
                }
            })

        # Pickle deserialization security issues
        if 'pickle' in issue.body.lower() or 'deserialization' in issue.body.lower() or 'rce' in issue.body.lower():
            core_files_map.update({
                'src/upsonic/server/level_two/server/server.py': {
                    'reason': 'get_temporary_memory function security',
                    'changes': 'Replace unsafe pickle.loads() with secure deserialization. Implement input validation and sandboxing for temporary memory storage.'
                },
                'src/upsonic/tools_server/server/tools.py': {
                    'reason': 'add_tool function security',
                    'changes': 'Replace unsafe cloudpickle.loads() with secure function validation. Implement input sanitization and execution sandboxing.'
                },
                'src/upsonic/safety_engine/__init__.py': {
                    'reason': 'Safety engine for malicious input detection',
                    'changes': 'Add security policies to detect and prevent malicious pickle payloads and unsafe deserialization attempts.'
                }
            })

        # Documentation issues
        if 'contributing' in issue.body.lower() or 'code_of_conduct' in issue.body.lower():
            core_files_map.update({
                'CONTRIBUTING.md': {
                    'reason': 'Community contribution guidelines',
                    'changes': 'Create CONTRIBUTING.md with contribution workflow, PR naming conventions, coding standards, and issue reporting guidelines.'
                },
                'CODE_OF_CONDUCT.md': {
                    'reason': 'Community behavior standards',
                    'changes': 'Create CODE_OF_CONDUCT.md defining acceptable behavior, reporting mechanisms, and consequences for violations.'
                }
            })

        # Check if core files are in relevant files and add specific suggestions
        for file_path in relevant_files:
            if file_path in core_files_map:
                file_info = core_files_map[file_path]
                modifications.append(FileModification(
                    file_path=file_path,
                    reason=file_info['reason'],
                    suggested_changes=file_info['changes']
                ))

        # If core files aren't found, suggest them anyway for this specific issue
        missing_core_files = [f for f in core_files_map.keys() if f not in relevant_files]
        for file_path in missing_core_files[:3]:  # Limit to 3 missing core files
            file_info = core_files_map[file_path]
            modifications.append(FileModification(
                file_path=file_path,
                reason=file_info['reason'] + ' (Identified as critical for this issue)',
                suggested_changes=file_info['changes']
            ))

        # Add context-aware documentation suggestions
        if 'standalone' in issue.body.lower() or 'toolkit' in issue.body.lower():
            modifications.append(FileModification(
                file_path="README.md or docs/examples/",
                reason="Documentation and examples need correct import paths",
                suggested_changes="Replace any instances of 'from upsonic.tools.decorators import tool' with 'from upsonic.tools.tool import tool' in documentation and example code."
            ))
        elif 'pricing' in issue.body.lower() or 'dynamic' in issue.body.lower():
            modifications.append(FileModification(
                file_path="README.md",
                reason="Documentation needs dynamic pricing examples",
                suggested_changes="Add examples showing dynamic pricing integration with OpenRouter API, caching mechanisms, and real-time model availability detection."
            ))
        elif 'hang' in issue.body.lower() or 'forever' in issue.body.lower() or 'fastapi' in issue.body.lower():
            modifications.append(FileModification(
                file_path="examples/fastapi_async_example.py",
                reason="FastAPI async integration example",
                suggested_changes="Create example showing proper async FastAPI integration using agent.do_async() instead of blocking agent.do() calls."
            ))
        elif 'process' in issue.body.lower() or 'termination' in issue.body.lower() or 'servermanager' in issue.body.lower():
            modifications.append(FileModification(
                file_path="docs/server_management.md",
                reason="Server process management documentation",
                suggested_changes="Document proper server shutdown procedures, process tree cleanup, and resource management best practices."
            ))
        elif 'pickle' in issue.body.lower() or 'deserialization' in issue.body.lower() or 'rce' in issue.body.lower():
            modifications.append(FileModification(
                file_path="SECURITY.md",
                reason="Security vulnerability documentation",
                suggested_changes="Document security measures against pickle deserialization attacks, input validation requirements, and secure coding practices."
            ))
        elif 'security' in issue.body.lower() or 'vulnerabilit' in issue.body.lower():
            modifications.append(FileModification(
                file_path="SECURITY.md",
                reason="Security policy documentation",
                suggested_changes="Create SECURITY.md with vulnerability reporting guidelines, private disclosure process, and security contact information."
            ))
        elif 'contributing' in issue.body.lower() or 'code_of_conduct' in issue.body.lower():
            modifications.append(FileModification(
                file_path="CONTRIBUTING.md",
                reason="Community contribution guidelines",
                suggested_changes="Create CONTRIBUTING.md with contribution workflow, PR naming conventions, coding standards, and issue reporting guidelines."
            ))

        # Add context-aware test case suggestions
        if 'standalone' in issue.body.lower() or 'toolkit' in issue.body.lower():
            modifications.append(FileModification(
                file_path="tests/test_tool_function_standalone.py",
                reason="Add test case for standalone tool functions",
                suggested_changes="Create test case that verifies @tool decorated functions can be used directly in Task.tools without Toolkit wrapper class."
            ))
        elif 'pricing' in issue.body.lower() or 'dynamic' in issue.body.lower():
            modifications.append(FileModification(
                file_path="tests/test_dynamic_pricing.py",
                reason="Add test case for dynamic pricing system",
                suggested_changes="Create tests for OpenRouter API integration, caching mechanisms, and real-time pricing validation."
            ))
        elif 'hang' in issue.body.lower() or 'forever' in issue.body.lower() or 'fastapi' in issue.body.lower():
            modifications.append(FileModification(
                file_path="tests/test_fastapi_integration.py",
                reason="Add test case for FastAPI async integration",
                suggested_changes="Create tests for async FastAPI endpoints using agent.do_async() method and proper async handling."
            ))
        elif 'process' in issue.body.lower() or 'termination' in issue.body.lower() or 'servermanager' in issue.body.lower():
            modifications.append(FileModification(
                file_path="tests/test_server_process_termination.py",
                reason="Add test case for server process termination",
                suggested_changes="Create tests for proper child process cleanup in ServerManager.stop() method and process tree termination."
            ))
        elif 'pickle' in issue.body.lower() or 'deserialization' in issue.body.lower() or 'rce' in issue.body.lower():
            modifications.append(FileModification(
                file_path="tests/test_secure_deserialization.py",
                reason="Add test case for secure deserialization",
                suggested_changes="Create tests for safe pickle/cloudpickle deserialization, input validation, and RCE prevention mechanisms."
            ))
        elif 'security' in issue.body.lower() or 'vulnerabilit' in issue.body.lower():
            modifications.append(FileModification(
                file_path="tests/test_security_engine.py",
                reason="Add test case for security vulnerability detection",
                suggested_changes="Create tests for security policy enforcement and vulnerability detection mechanisms."
            ))

        return modifications
    
    def generate_constraints(self, issue: GitHubIssue, issue_type: str) -> List[str]:
        """Generate constraints"""
        constraints = [
            "Must maintain backward compatibility",
            "Must follow existing code patterns and standards",
            "Must include appropriate error handling"
        ]
        
        if issue_type == "bug_fix":
            constraints.append("Must not introduce new bugs while fixing the current issue")
        
        return constraints
    
    
    def parse_generated_prd(self, content: str, issue: GitHubIssue, analysis_data: Dict[str, Any]) -> PRDDocument:
        """Parse generated PRD content into structured format"""
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        # For now, fall back to template-based generation
        return self.generate_prd_template_based(issue, analysis_data)
