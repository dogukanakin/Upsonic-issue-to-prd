# Upsonic-issue-to-prd

## Quick Start

### 1. Installation

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit the .env file and add GITHUB_TOKEN and OPENAI_API_KEY
```

### 2. Run

```bash
source venv/bin/activate
python main.py

and

uvicorn main:app --port 8000
```

**Test URL:** `https://github.com/Upsonic/Upsonic/issues/398`


### Environment Variables

```env
# GitHub API Configuration
GITHUB_TOKEN=your_github_token_here

# OpenAI API Configuration (for Upsonic)
OPENAI_API_KEY=your_openai_api_key_here

# Upsonic Configuration
UPSONIC_MODEL=openai/gpt-4o-mini
```
