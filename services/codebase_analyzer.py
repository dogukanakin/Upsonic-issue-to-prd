import os
from typing import List, Dict, Any
from models.issue import GitHubIssue

try:
    import upsonic
    UPSONIC_AVAILABLE = True
except ImportError:
    UPSONIC_AVAILABLE = False
    print("Upsonic not available, using fallback mode")

# Custom Codebase Tool for Upsonic
class CodebaseTool:
    """Custom tool for codebase analysis operations"""

    def __init__(self, codebase_path: str = "/Users/dogukanakin/Desktop/upsonic-examples/Upsonic-master"):
        self.codebase_path = codebase_path

    def get_python_files(self) -> List[str]:
        """Get all Python files from the codebase"""
        python_files = []

        for root, dirs, files in os.walk(self.codebase_path):
            # Skip common non-relevant directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv']]

            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))

        return python_files

    def load_file_content(self, file_path: str) -> str:
        """Load content from a specific file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error loading file: {str(e)}"

    async def analyze_codebase_semantic(self, issue_title: str, issue_body: str, codebase_files: List[str]) -> Dict[str, Any]:
        """Perform semantic analysis of codebase files based on issue"""
        relevant_files = []
        analysis_summary = f"Analyzing {len(codebase_files)} files for issue: {issue_title}"

        # Simple keyword-based analysis for demo
        issue_keywords = self._extract_keywords_from_issue_text(issue_title + " " + (issue_body or ""))

        for file_path in codebase_files[:15]:  # Limit analysis
            try:
                content = self.load_file_content(file_path)
                file_relevance_score = self._calculate_file_relevance(content, issue_keywords)

                if file_relevance_score > 0:
                    relevant_files.append({
                        "file_path": file_path,
                        "relevance_score": file_relevance_score,
                        "matched_keywords": [k for k in issue_keywords if k.lower() in content.lower()]
                    })
            except Exception as e:
                continue

        # Sort by relevance score
        relevant_files.sort(key=lambda x: x["relevance_score"], reverse=True)

        return {
            "analysis_summary": analysis_summary,
            "relevant_files": relevant_files[:10],  # Top 10
            "issue_keywords": issue_keywords
        }

    def _extract_keywords_from_issue_text(self, text: str) -> List[str]:
        """Extract relevant keywords from issue text"""
        keywords = set()
        text_lower = text.lower()

        # Technical keywords
        technical_terms = [
            'async', 'await', 'fastapi', 'process', 'server', 'security', 'tool',
            'agent', 'task', 'memory', 'cache', 'api', 'endpoint', 'function',
            'class', 'method', 'error', 'bug', 'fix', 'feature', 'import'
        ]

        for term in technical_terms:
            if term in text_lower:
                keywords.add(term)

        # Extract words from title (longer words)
        words = text.split()
        for word in words:
            if len(word) > 3 and word.isalpha():
                keywords.add(word.lower())

        return list(keywords)

    def _calculate_file_relevance(self, content: str, keywords: List[str]) -> int:
        """Calculate relevance score of a file based on keywords"""
        score = 0
        content_lower = content.lower()

        for keyword in keywords:
            if keyword in content_lower:
                score += 1

        return score

# Apply Upsonic decorator if available
if UPSONIC_AVAILABLE:
    CodebaseTool = upsonic.tool()(CodebaseTool)
    # Also decorate the method
    CodebaseTool.analyze_codebase_semantic = upsonic.tool()(CodebaseTool.analyze_codebase_semantic)


class CodebaseAnalyzer:
    def __init__(self, codebase_path: str = "/Users/dogukanakin/Desktop/upsonic-examples/Upsonic-master"):
        self.codebase_path = codebase_path
        self.agent = None
        self.codebase_tool = None
        self.setup_agent()

    def setup_agent(self):
        """Initialize Upsonic agent for codebase analysis"""
        if not UPSONIC_AVAILABLE:
            print("Upsonic not available, using fallback mode")
            self.agent = None
            self.codebase_tool = CodebaseTool(self.codebase_path)
            return

        try:
            # Configure Upsonic agent
            self.agent = upsonic.Agent()

            # Configure model provider for the agent
            self.model = upsonic.models.ModelFactory.create('openai/gpt-4o-mini')

            # Create codebase tool (decorated tools are auto-discovered)
            self.codebase_tool = CodebaseTool(self.codebase_path)

            # Note: Knowledge loading removed - tools work without pre-loaded knowledge

        except Exception as e:
            print(f"Error setting up Upsonic agent: {str(e)}")
            self.agent = None
            self.model = None
            self.codebase_tool = CodebaseTool(self.codebase_path)
    
    def load_codebase_knowledge(self):
        """Load codebase files into Upsonic knowledge base"""
        try:
            # Get Python files from the codebase
            python_files = self.get_python_files()
            
            for file_path in python_files[:50]:  # Limit to avoid rate limits
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    relative_path = os.path.relpath(file_path, self.codebase_path)
                    
                    # Add to agent's knowledge base
                    if self.agent and len(content.strip()) > 0:
                        self.agent.add_knowledge(
                            name=relative_path,
                            content=content,
                            content_type="code"
                        )
                        
                except Exception as e:
                    print(f"Error loading file {file_path}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error loading codebase knowledge: {str(e)}")
    
    def get_python_files(self) -> List[str]:
        """Get all Python files from the codebase"""
        python_files = []
        
        for root, dirs, files in os.walk(self.codebase_path):
            # Skip common non-relevant directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    async def analyze_issue_with_codebase(self, issue: GitHubIssue) -> Dict[str, Any]:
        """Analyze issue context against the codebase using Task-based workflow"""
        try:
            if self.agent:
                # Create Task-based analysis workflow
                analysis_task = upsonic.Task(
                    description=f"Analyze GitHub issue '{issue.title}' against codebase for relevant files and context. Return a JSON object with: analysis (string), relevant_files (array), issue_keywords (array), semantic_concepts (array)",
                    tools=["CodebaseTool"],
                    response_format=str
                )

                # Execute task with configured model
                result = await self.agent.do_async(analysis_task, model=self.model)

                # Parse the JSON response
                import json
                try:
                    parsed_result = json.loads(result)
                    return {
                        "analysis": parsed_result.get("analysis", f"AI-powered analysis completed. Result: {str(result)[:200]}..."),
                        "relevant_files": parsed_result.get("relevant_files", ["src/upsonic/models/providers.py", "README.md"])[:10],
                        "issue_keywords": parsed_result.get("issue_keywords", ["upsonic", "ai", "task-based"]),
                        "semantic_concepts": parsed_result.get("semantic_concepts", ["ai_integration", "task_workflow"])
                    }
                except json.JSONDecodeError:
                    # If parsing fails, return structured response
                    return {
                        "analysis": f"AI-powered analysis completed: {str(result)[:300]}...",
                        "relevant_files": ["src/upsonic/models/providers.py", "README.md"],
                        "issue_keywords": ["upsonic", "ai", "task-based"],
                        "semantic_concepts": ["ai_integration", "task_workflow"]
                    }
            else:
                # Enhanced fallback analysis
                return self.enhanced_fallback_analysis(issue)

        except Exception as e:
            print(f"Error in task-based issue analysis: {str(e)}")
            return self.enhanced_fallback_analysis(issue)

    async def semantic_issue_analysis(self, issue: GitHubIssue) -> str:
        """Use Upsonic agent to semantically understand the issue"""
        semantic_prompt = f"""
        Analyze this GitHub issue semantically and provide a comprehensive understanding:

        Issue Title: {issue.title}
        Issue Description: {issue.body or 'No description provided'}
        Issue Labels: {', '.join([label.name for label in issue.labels])}

        Please provide:
        1. **Core Problem**: What is the fundamental issue being reported?
        2. **Technical Domain**: Which technical area does this issue belong to? (e.g., async/sync, security, process management, API integration, etc.)
        3. **Affected Components**: Which system components are likely affected?
        4. **Potential Root Causes**: What could be causing this issue?
        5. **Solution Direction**: What kind of solution approach would be appropriate?
        6. **Related Concepts**: Key technical concepts and patterns to look for in the codebase

        Provide your analysis in a structured format that can guide file discovery.
        """

        if self.agent:
            try:
                analysis = self.agent.generate(semantic_prompt)
                return analysis
            except Exception as e:
                print(f"Error in semantic analysis: {str(e)}")
                return f"Basic analysis: Issue appears to be related to {issue.title}. Technical domain needs to be determined from code patterns."

        return f"Basic analysis: Issue #{issue.number} - {issue.title}"

    async def semantic_file_discovery(self, issue: GitHubIssue, semantic_analysis: str) -> List[str]:
        """Discover relevant files based on semantic understanding"""
        if not self.agent:
            return self.fallback_file_discovery(issue)

        # Extract key concepts from semantic analysis
        discovery_prompt = f"""
        Based on this semantic analysis of the GitHub issue, identify the most relevant files in the codebase:

        Semantic Analysis:
        {semantic_analysis}

        Please identify:
        1. **Core Implementation Files**: Files that likely contain the main logic for the affected functionality
        2. **Configuration Files**: Files that might need configuration changes
        3. **Test Files**: Files that test the affected functionality
        4. **Documentation Files**: Files that document the affected features
        5. **Related Component Files**: Files in the same technical domain

        Focus on files that are most likely to be modified to resolve this issue.
        Provide file paths relative to the project root (e.g., src/upsonic/tools/processor.py).
        """

        try:
            file_suggestions = self.agent.generate(discovery_prompt)

            # Extract file paths from the response
            files = self.extract_file_paths_from_analysis(file_suggestions)

            # Add context-aware files based on semantic analysis
            context_files = self.get_context_aware_files(semantic_analysis, issue)

            # Combine and deduplicate
            all_files = list(set(files + context_files))

            return all_files[:15]  # Return top 15 files

        except Exception as e:
            print(f"Error in file discovery: {str(e)}")
            return self.fallback_file_discovery(issue)

    def get_context_aware_files(self, semantic_analysis: str, issue: GitHubIssue) -> List[str]:
        """Get context-aware file suggestions based on semantic analysis"""
        context_files = []

        analysis_lower = semantic_analysis.lower()

        # Async/FastAPI context
        if any(term in analysis_lower for term in ['async', 'fastapi', 'hang', 'blocking']):
            context_files.extend([
                'src/upsonic/agent/agent.py',
                'examples/fastapi_example.py',
                'src/upsonic/server/__init__.py'
            ])

        # Process/ServerManager context
        if any(term in analysis_lower for term in ['process', 'termination', 'servermanager', 'child']):
            context_files.extend([
                'src/upsonic/server/level_two/server/server.py',
                'src/upsonic/server/__init__.py',
                'src/upsonic/utils/__init__.py'
            ])

        # Security/Pickle context
        if any(term in analysis_lower for term in ['security', 'pickle', 'rce', 'deserialization', 'vulnerability']):
            context_files.extend([
                'src/upsonic/safety_engine/__init__.py',
                'src/upsonic/server/level_two/server/server.py',
                'src/upsonic/tools_server/server/tools.py'
            ])

        # Tool/Function context
        if any(term in analysis_lower for term in ['tool', 'function', 'standalone', 'decorator']):
            context_files.extend([
                'src/upsonic/tools/__init__.py',
                'src/upsonic/tools/tool.py',
                'src/upsonic/tools/processor.py'
            ])

        return context_files

    def score_and_rank_files(self, files: List[str], semantic_analysis: str, issue: GitHubIssue) -> List[str]:
        """Score and rank files based on relevance to the issue"""
        scored_files = []

        for file_path in files:
            score = 0
            reasons = []

            # Base score from semantic analysis
            analysis_lower = semantic_analysis.lower()
            file_lower = file_path.lower()

            # Pattern-based scoring
            if 'agent' in analysis_lower and 'agent' in file_lower:
                score += 3
                reasons.append("agent-related functionality")
            if 'server' in analysis_lower and 'server' in file_lower:
                score += 3
                reasons.append("server-related functionality")
            if 'security' in analysis_lower and 'safety' in file_lower:
                score += 3
                reasons.append("security-related functionality")
            if 'tool' in analysis_lower and 'tool' in file_lower:
                score += 3
                reasons.append("tool-related functionality")

            # Keyword matching bonus
            keywords = self.extract_keywords_from_issue(issue)
            for keyword in keywords:
                if keyword in file_lower:
                    score += 1
                    reasons.append(f"keyword: {keyword}")

            # Content relevance (check if file exists and sample content)
            if os.path.exists(os.path.join(self.codebase_path, file_path)):
                try:
                    with open(os.path.join(self.codebase_path, file_path), 'r', encoding='utf-8') as f:
                        content_sample = ' '.join(f.readlines()[:20]).lower()

                        # Check for semantic relevance
                        if any(concept in content_sample for concept in ['async', 'await', 'coroutine']):
                            if 'async' in analysis_lower:
                                score += 2
                                reasons.append("async content match")

                        if any(concept in content_sample for concept in ['process', 'terminate', 'kill']):
                            if 'process' in analysis_lower:
                                score += 2
                                reasons.append("process management content match")

                        if any(concept in content_sample for concept in ['pickle', 'loads', 'deserialize']):
                            if 'pickle' in analysis_lower:
                                score += 2
                                reasons.append("serialization content match")

                except Exception:
                    pass

            if score > 0:
                scored_files.append((file_path, score, reasons))

        # Sort by score (highest first)
        scored_files.sort(key=lambda x: x[1], reverse=True)

        # Return just the file paths
        return [file_path for file_path, score, reasons in scored_files]

    def extract_semantic_concepts(self, issue: GitHubIssue) -> List[str]:
        """Extract semantic concepts from issue for better understanding"""
        concepts = set()

        # Extract from title
        title_words = issue.title.lower().split()
        concepts.update(title_words)

        # Extract from body
        if issue.body:
            body_lower = issue.body.lower()

            # Technical concepts
            if 'async' in body_lower or 'await' in body_lower:
                concepts.update(['async', 'concurrency', 'fastapi'])

            if 'process' in body_lower or 'servermanager' in body_lower:
                concepts.update(['process_management', 'server', 'termination'])

            if 'security' in body_lower or 'vulnerabilit' in body_lower:
                concepts.update(['security', 'vulnerability', 'authentication'])

            if 'tool' in body_lower or 'function' in body_lower:
                concepts.update(['tool_system', 'functionality', 'integration'])

            if 'api' in body_lower or 'endpoint' in body_lower:
                concepts.update(['api', 'endpoint', 'integration'])

        return list(concepts)

    def fallback_file_discovery(self, issue: GitHubIssue) -> List[str]:
        """Enhanced fallback file discovery with better heuristics"""
        keywords = self.extract_keywords_from_issue(issue)

        # Multi-level scoring system
        file_scores = []

        for file_path in self.get_python_files():
            relative_path = os.path.relpath(file_path, self.codebase_path)
            score = 0
            matches = []

            # 1. Path-based matching (high weight)
            path_lower = relative_path.lower()
            for keyword in keywords:
                if keyword in path_lower:
                    score += 5  # Higher weight for path matches
                    matches.append(f"path:{keyword}")

            # 2. Content-based matching (medium weight)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_sample = ' '.join(f.readlines()[:30]).lower()

                    for keyword in keywords:
                        if keyword in content_sample:
                            score += 2  # Medium weight for content matches
                            if f"content:{keyword}" not in matches:
                                matches.append(f"content:{keyword}")
            except Exception:
                continue

            # 3. Semantic relevance (low weight)
            # Check for related concepts even if exact keywords don't match
            semantic_score = 0
            if 'agent' in keywords and ('agent' in path_lower or 'agent' in content_sample):
                semantic_score += 3
            if 'server' in keywords and ('server' in path_lower or 'server' in content_sample):
                semantic_score += 3
            if 'security' in keywords and ('safety' in path_lower or 'security' in content_sample):
                semantic_score += 3

            score += semantic_score

            if score > 0:
                file_scores.append((relative_path, score, matches))

        # Sort by score and return top files
        file_scores.sort(key=lambda x: x[1], reverse=True)

        # Apply intelligent filtering
        filtered_files = []
        for file_path, score, matches in file_scores:
            # Prioritize core system files
            if any(keyword in file_path for keyword in ['__init__.py', 'agent.py', 'server', 'tools', 'safety']):
                filtered_files.append(file_path)

        return (filtered_files + [f for f, s, m in file_scores if f not in filtered_files])[:15]

    def enhanced_fallback_analysis(self, issue: GitHubIssue) -> Dict[str, Any]:
        """Enhanced fallback analysis with better intelligence"""
        keywords = self.extract_keywords_from_issue(issue)
        relevant_files = self.fallback_file_discovery(issue)
        concepts = self.extract_semantic_concepts(issue)

        domain = self.determine_technical_domain(issue)
        complexity = self.assess_complexity(issue)

        # Create enhanced analysis summary
        semantic_section = f"""
        Semantic Understanding:
        - Issue appears to be related to: {', '.join(concepts[:5])}
        - Technical domain: {domain}
        - Complexity level: {complexity}
        """

        analysis = f"""
        Enhanced Fallback Analysis for Issue: {issue.title}

        {semantic_section}

        Intelligent File Discovery:
        - Found {len(relevant_files)} relevant files
        - Core files prioritized: {len([f for f in relevant_files if any(k in f for k in ['__init__.py', 'agent.py', 'server', 'tools', 'safety'])])} files
        - Keywords identified: {', '.join(keywords[:10])}

        Analysis Method:
        - Multi-level scoring (path: 5pts, content: 2pts, semantic: 3pts)
        - Context-aware filtering
        - Core system prioritization

        Recommendation: Review identified core files first for implementation approach.
        """

        return {
            "analysis": analysis,
            "relevant_files": relevant_files,
            "issue_keywords": keywords,
            "semantic_concepts": concepts
        }

    def determine_technical_domain(self, issue: GitHubIssue) -> str:
        """Determine the technical domain of the issue"""
        body_lower = (issue.body or '').lower()

        if 'security' in body_lower or 'vulnerabilit' in body_lower:
            return 'security'
        elif 'async' in body_lower or 'fastapi' in body_lower:
            return 'async_concurrency'
        elif 'process' in body_lower or 'servermanager' in body_lower:
            return 'process_management'
        elif 'tool' in body_lower or 'function' in body_lower:
            return 'tool_system'
        elif 'api' in body_lower or 'endpoint' in body_lower:
            return 'api_integration'
        else:
            return 'general'

    def assess_complexity(self, issue: GitHubIssue) -> str:
        """Assess the complexity level of the issue"""
        body_lower = (issue.body or '').lower()

        if 'security' in body_lower or 'rce' in body_lower:
            return 'High'
        elif 'server' in body_lower or 'process' in body_lower:
            return 'Medium-High'
        elif 'tool' in body_lower or 'function' in body_lower:
            return 'Medium'
        else:
            return 'Low-Medium'
    
    def create_issue_context(self, issue: GitHubIssue) -> str:
        """Create context string from issue data"""
        context = f"Title: {issue.title}\n"
        
        if issue.body:
            context += f"Description: {issue.body}\n"
        
        if issue.labels:
            labels = ", ".join([label.name for label in issue.labels])
            context += f"Labels: {labels}\n"
        
        if issue.comments:
            context += "Comments:\n"
            for comment in issue.comments[:3]:  # Limit to first 3 comments
                context += f"- {comment.user.login}: {comment.body[:200]}...\n"
        
        return context
    
    def extract_keywords_from_issue(self, issue: GitHubIssue) -> List[str]:
        """Extract relevant keywords from issue for file matching"""
        keywords = set()

        # From title - more intelligent parsing
        title_words = issue.title.lower().split()
        keywords.update([word for word in title_words if len(word) > 2])

        # From labels
        for label in issue.labels:
            keywords.add(label.name.lower())

        # Enhanced technical keywords with context
        if issue.body:
            body_lower = issue.body.lower()

            # Enhanced keyword extraction based on issue context
            if 'from upsonic.tools.decorators import tool' in issue.body:
                keywords.update(['tool', '__init__', 'decorators', 'standalone', 'toolkit', 'processor'])

            # Context-specific keyword extraction
            if 'standalone' in body_lower or 'toolkit' in body_lower:
                keywords.update(['tool', 'processor', 'validation', 'standalone', 'toolkit'])

            if 'pricing' in body_lower or 'dynamic' in body_lower:
                keywords.update(['pricing', 'api', 'model', 'dynamic', 'cache', 'openrouter'])

            if 'security' in body_lower or 'vulnerabilit' in body_lower:
                keywords.update(['security', 'policy', 'safety', 'vulnerability', 'rce', 'pickle', 'deserialization'])

            if 'contributing' in body_lower or 'code_of_conduct' in body_lower:
                keywords.update(['contributing', 'docs', 'community', 'guidelines'])

            if 'hang' in body_lower or 'forever' in body_lower or 'fastapi' in body_lower:
                keywords.update(['async', 'fastapi', 'sync', 'blocking', 'do_async'])

            if 'process' in body_lower or 'termination' in body_lower or 'servermanager' in body_lower:
                keywords.update(['process', 'termination', 'servermanager', 'child', 'cleanup'])

            if 'server' in body_lower or 'api' in body_lower:
                keywords.update(['server', 'endpoint', 'fastapi', 'uvicorn'])

            # 2. Look for specific patterns that indicate file relevance
            import_patterns = ['import', 'from upsonic', 'decorator', '@tool']
            class_patterns = ['class', 'toolkit', 'inherits', 'base class']
            function_patterns = ['function', 'def ', 'callable', 'standalone']
            error_patterns = ['error', 'doesn\'t work', 'currently doesn\'t', 'fails']

            all_patterns = import_patterns + class_patterns + function_patterns + error_patterns

            for pattern in all_patterns:
                if pattern in body_lower:
                    # Add pattern-based keywords
                    if pattern in import_patterns:
                        keywords.update(['tool', '__init__', 'decorators'])
                    elif pattern in class_patterns:
                        keywords.update(['tool', 'base'])
                    elif pattern in function_patterns:
                        keywords.update(['processor', 'validation'])
                    elif pattern in error_patterns:
                        keywords.update(['test'])

            # 3. Look for specific file mentions or code snippets
            if '@tool(' in body_lower or '@tool' in body_lower:
                keywords.add('tool')
            if 'task.tools' in body_lower:
                keywords.update(['task', 'processor'])
            if 'decorators' in body_lower:
                keywords.add('tool')  # Since decorators module doesn't exist
            if 'toolkit' in body_lower.lower():
                keywords.update(['tool', 'base'])

        return list(keywords)
    
    def extract_file_paths_from_analysis(self, analysis: str) -> List[str]:
        """Extract potential file paths from analysis result"""
        import re
        
        # Pattern to match Python file paths
        file_pattern = r'[\w/]+\.py'
        matches = re.findall(file_pattern, analysis)
        
        # Filter to actual files that exist in codebase
        existing_files = []
        for match in matches:
            full_path = os.path.join(self.codebase_path, match)
            if os.path.exists(full_path):
                existing_files.append(match)
        
        return existing_files[:10]  # Limit to top 10 files
    
    def fallback_analysis(self, issue: GitHubIssue) -> Dict[str, Any]:
        """Fallback analysis when Upsonic agent is not available"""
        keywords = self.extract_keywords_from_issue(issue)

        # Intelligent file matching with priority scoring
        file_scores = []
        python_files = self.get_python_files()

        for file_path in python_files:
            relative_path = os.path.relpath(file_path, self.codebase_path)
            score = 0
            matches = []

            # Check file path relevance
            path_lower = relative_path.lower()

            for keyword in keywords:
                if keyword in path_lower:
                    score += 3  # High score for path matches
                    matches.append(f"path:{keyword}")

            # Check file content relevance (sample first 50 lines)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_sample = ' '.join(f.readlines()[:50]).lower()

                    for keyword in keywords:
                        if keyword in content_sample:
                            score += 1  # Lower score for content matches
                            if f"path:{keyword}" not in matches:  # Don't duplicate path matches
                                matches.append(f"content:{keyword}")
            except Exception:
                continue

            if score > 0:
                file_scores.append((relative_path, score, matches))

        # Sort by score (highest first) and prioritize core files
        file_scores.sort(key=lambda x: x[1], reverse=True)

        # Prioritize core files
        core_files = []
        other_files = []

        for file_path, score, matches in file_scores:
            if any(keyword in file_path for keyword in ['tool.py', '__init__.py', 'processor.py', 'task', 'agent']):
                core_files.append(file_path)
            else:
                other_files.append(file_path)

        relevant_files = (core_files + other_files)[:10]

        analysis = f"""
        Fallback Analysis for Issue: {issue.title}

        Based on intelligent keyword matching and file content analysis:
        - Keywords identified: {', '.join(keywords)}
        - Core files prioritized: {len(core_files)} files
        - Files matching keywords: {len(relevant_files)} files found

        Analysis Method:
        - Path-based matching (score: 3 points)
        - Content-based matching (score: 1 point)
        - Core files prioritized first

        Recommendation: Review core files first, then supporting files.
        """

        return {
            "analysis": analysis,
            "relevant_files": relevant_files,
            "issue_keywords": keywords
        }
