# Upsonic Cookbook: Issue to PRD Converter

Bu proje, Upsonic framework'ünün gerçek dünya kullanımını gösteren kapsamlı bir örnektir. GitHub issue'larından Product Requirements Document (PRD) oluşturma sürecinde Upsonic'un Agent, Task ve Tool sistemlerini nasıl entegre edeceğinizi öğreneceksiniz.

## 🎯 Proje Genel Bakış

Bu uygulama, GitHub issue'larını alıp AI-powered analysis ile PRD dokümanları üreten bir FastAPI servisi. Upsonic'un temel özelliklerini kullanarak:

- **Semantic Codebase Analysis**: Issue'ları codebase bağlamında analiz eder
- **AI-Powered PRD Generation**: Structured PRD dokümanları oluşturur
- **Fallback Mechanisms**: Upsonic mevcut değilse template-based fallback

## 🏗️ Upsonic Mimarisi

### 1. Tool System Kullanımı

#### CodebaseTool Sınıfı
```python
class CodebaseTool:
    def __init__(self, codebase_path: str):
        self.codebase_path = codebase_path

    def get_python_files(self) -> List[str]:
        # Codebase'deki Python dosyalarını listeler
        pass

    async def analyze_codebase_semantic(self, issue_title: str, issue_body: str, codebase_files: List[str]) -> Dict[str, Any]:
        # Semantic analysis gerçekleştirir
        pass

# Upsonic tool decorator ile decorate etme
if UPSONIC_AVAILABLE:
    CodebaseTool = upsonic.tool()(CodebaseTool)
```

**Neden Tool System?**
- Fonksiyonları AI agent'ın kullanabileceği hale getirir
- Structured input/output sağlar
- Automatic discovery ile agent'a otomatik olarak eklenir

#### PRDTool Sınıfı
```python
class PRDTool:
    async def generate_prd_content(self, issue_title: str, issue_body: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        # PRD içeriği üretir
        return {
            "title": f"PRD: {issue_title}",
            "overview": "AI-generated overview",
            "problem_statement": "Detailed problem description",
            "use_cases": [...],
            "file_modifications": [...],
            "constraints": [...]
        }

# Decorator ile tool haline getirme
if UPSONIC_AVAILABLE:
    PRDTool = upsonic.tool()(PRDTool)
```

### 2. Agent System Entegrasyonu

#### Agent Başlatma
```python
class CodebaseAnalyzer:
    def __init__(self, codebase_path: str):
        self.codebase_path = codebase_path
        self.agent = None
        self.setup_agent()

    def setup_agent(self):
        if UPSONIC_AVAILABLE:
            # Agent oluşturma
            self.agent = upsonic.Agent()

            # Model konfigürasyonu
            self.model = upsonic.models.ModelFactory.create('openai/gpt-4o-mini')

            # Tool instance'ı oluşturma (auto-discovery ile agent'a eklenir)
            self.codebase_tool = CodebaseTool(self.codebase_path)
```

**Agent Özellikleri:**
- **Auto Tool Discovery**: `@tool` decorator ile işaretlenmiş sınıflar otomatik olarak bulunur
- **Model Management**: Farklı AI modelleri ile çalışma yeteneği
- **Task Execution**: Task'ları çalıştırma ve sonuçları işleme

### 3. Task System Kullanımı

#### Task Tabanlı İşleme
```python
async def analyze_issue_with_codebase(self, issue: GitHubIssue) -> Dict[str, Any]:
    if self.agent:
        # Semantic analysis için task oluşturma
        analysis_task = upsonic.Task(
            description=f"""Analyze GitHub issue '{issue.title}' against the Upsonic codebase...

Return ONLY a valid JSON object with this exact structure:
{{
  "analysis": "Brief analysis of the issue",
  "relevant_files": ["src/upsonic/tasks/tasks.py"],
  "issue_keywords": ["response", "truncation"],
  "semantic_concepts": ["response_handling"]
}}""",
            tools=["CodebaseTool"],  # Kullanılacak tool'ları belirtme
            response_format=str
        )

        # Task'ı çalıştırma
        result = await self.agent.do_async(analysis_task, model=self.model)

        # JSON parsing ve dönüşüm
        parsed_result = json.loads(result)
        return parsed_result
```

**Task System Faydaları:**
- **Structured Prompts**: Karmaşık işleri parçalara bölme
- **Tool Integration**: Belirli tool'ları task'a bağlama
- **Async Support**: Asenkron execution
- **Response Formatting**: Beklenen output formatını belirleme

### 4. Fallback Mekanizmaları

#### Graceful Degradation
```python
async def analyze_issue_with_codebase(self, issue: GitHubIssue) -> Dict[str, Any]:
    try:
        if self.agent:
            # AI-powered analysis
            return await self.perform_ai_analysis(issue)
        else:
            # Fallback to template-based analysis
            return self.enhanced_fallback_analysis(issue)
    except Exception as e:
        # Error handling
        return self.enhanced_fallback_analysis(issue)
```

**Fallback Stratejisi:**
- Upsonic mevcut değilse template-based çalışma
- Error durumlarında graceful degradation
- Feature parity koruması

## 🚀 Servis Entegrasyonu

### FastAPI ile Upsonic Entegrasyonu
```python
@app.post("/analyze-issue")
async def analyze_issue(request: IssueAnalysisRequest):
    # GitHub issue çekme
    issue = await github_service.fetch_issue(request.github_url)

    # Codebase analysis
    analysis_data = await codebase_analyzer.analyze_issue_with_codebase(issue)

    # PRD generation
    prd_document = await prd_generator.generate_prd(issue, analysis_data)

    return IssueAnalysisResponse(...)
```

## 📋 Best Practices

### 1. Tool Design
- **Single Responsibility**: Her tool tek bir sorumluluğa odaklanmalı
- **Clear Interfaces**: Input/output formatları net olmalı
- **Error Handling**: Robust error handling implementasyonu

### 2. Task Management
- **Descriptive Prompts**: Task açıklamaları detaylı olmalı
- **Structured Output**: JSON formatlarında output isteme
- **Tool Selection**: İhtiyaca göre tool seçimi

### 3. Agent Configuration
- **Model Selection**: Use case'e göre uygun model seçimi
- **Resource Management**: Agent lifecycle management
- **Fallback Planning**: Her zaman fallback stratejisi

### 4. Error Handling
- **Graceful Degradation**: Sistem çalışmaya devam etmeli
- **User Feedback**: Hata durumlarında bilgi verme
- **Logging**: Detaylı loglama

## 🔧 Teknik Detaylar

### Dependencies
```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
python-dotenv==1.0.0
upsonic  # Latest version
```

### Environment Variables
```bash
# .env
OPENAI_API_KEY=your_openai_key
GITHUB_TOKEN=your_github_token
```

### Upsonic Tool Registration
```python
# Tool'lar otomatik olarak register edilir
if UPSONIC_AVAILABLE:
    CodebaseTool = upsonic.tool()(CodebaseTool)
    PRDTool = upsonic.tool()(PRDTool)
    GitHubTool = upsonic.tool()(GitHubTool)
```

## 🎯 Öğrenilen Dersler

1. **Modular Architecture**: Tool'ları ayrı sınıflar halinde organize etme
2. **Async First**: Tüm operasyonu async olarak tasarlama
3. **Fallback Design**: Sistem güvenilirliğini artırma
4. **Structured Communication**: Agent-Task-Tool arasındaki iletişimi yapılandırma
5. **Error Resilience**: Robust error handling implementasyonu

## 🚀 Genişletme Önerileri

- **Additional Tools**: Daha fazla domain-specific tool ekleme
- **Multi-Agent Systems**: Farklı görevler için ayrı agent'lar
- **Caching Layer**: Analysis sonuçlarını cacheleme
- **Metrics & Monitoring**: Performance monitoring ekleme
- **Configurable Models**: Runtime'da model değiştirme

Bu cookbook, Upsonic'u production-ready uygulamalarda nasıl kullanacağınızı gösteren kapsamlı bir rehber niteliğindedir.

