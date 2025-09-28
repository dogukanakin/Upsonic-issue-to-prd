# Upsonic-issue-to-prd

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Virtual environment oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install fastapi uvicorn httpx pydantic python-dotenv

# Environment variables ayarlayın
cp .env.example .env
# .env dosyasını düzenleyip GITHUB_TOKEN ve OPENAI_API_KEY ekleyin
```

### 2. Çalıştırma

```bash
source venv/bin/activate
python main.py
```

### 3. Kullanım

1. 🌐 Web tarayıcınızda `http://localhost:8000` adresini açın
2. 📝 GitHub issue URL'ini girin
3. 🚀 "PRD Oluştur" butonuna tıklayın
4. ⏳ Analiz tamamlanmasını bekleyin
5. 📋 PRD'yi kopyalayın veya inceleyin

## 📋 Örnek Kullanım

**Test URL:** `https://github.com/Upsonic/Upsonic/issues/398`

## 🛠️ Teknik Detaylar

### Environment Variables

```env
# GitHub API Configuration
GITHUB_TOKEN=your_github_token_here

# OpenAI API Configuration (for Upsonic)
OPENAI_API_KEY=your_openai_api_key_here

# Upsonic Configuration
UPSONIC_MODEL=openai/gpt-4o-mini
```

### Özellikler ve Limitler

**Özellikler:**
- GitHub API rate limit'leri dahilinde çalışır
- Upsonic Agent ile semantic code analysis (fallback mode destekli)
- Template-based PRD generation
- CORS desteği
- Comprehensive error handling

**Limitler:**
- Codebase analizi için 50 dosya limiti (performans için)
- Comment analizi için ilk 3 comment
- File modification önerileri için ilk 5 dosya

## 🔍 Troubleshooting

### GitHub Token Hatası
```json
{
  "detail": "Failed to fetch GitHub issue: HTTP error occurred: 403"
}
```
**Çözüm:** `.env` dosyasında geçerli `GITHUB_TOKEN` ayarlayın.

### Upsonic Kurulumu
Upsonic kurulu değilse sistem otomatik olarak fallback mode'a geçer:
```json
{
  "analysis_summary": "Automated analysis unavailable, manual review recommended"
}
```

### Port Kullanımda
```
OSError: [Errno 48] Address already in use
```
**Çözüm:**
```bash
# Çalışan uygulamayı durdurun
pkill -f "python main.py"

# Veya farklı port kullanın
ut```

