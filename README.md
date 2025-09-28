# Issue to PRD Generator MVP

GitHub Issue'larını otomatik olarak PRD belgelerine dönüştüren basit web uygulaması.

## ✨ Özellikler

- 🔍 **GitHub API Entegrasyonu**: Issue bilgilerini otomatik olarak çeker
- 🧠 **AI Destekli Analiz**: Upsonic Agent ile codebase analizi (fallback mode destekli)
- 📄 **PRD Döküman Üretimi**: Profesyonel PRD belgeleri oluşturur
- 🌐 **Modern Web Interface**: Kullanıcı dostu arayüz
- 📋 **Tek Tıkla Kopyalama**: PRD'yi kolayca kopyalayabilirsiniz
- 📱 **Responsive Design**: Mobil ve desktop uyumlu

## 🚀 Hızlı Başlangıç

### 1. Kurulum

```bash
# Projeyi klonlayın
cd issue-to-prd

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

Bu URL'yi girip test edebilirsiniz. Sistem otomatik olarak:
- Issue bilgilerini çeker
- Codebase'de ilgili dosyaları bulur
- Comprehensive PRD dökümanı oluşturur

## 🔧 API Endpoints

### POST /analyze-issue

```bash
curl -X POST "http://localhost:8000/analyze-issue" \
     -H "Content-Type: application/json" \
     -d '{"github_url": "https://github.com/owner/repo/issues/123"}'
```

**Response:**
```json
{
  "issue": {
    "id": 123,
    "number": 123,
    "title": "Issue Title",
    "body": "Issue description...",
    "user": {...},
    "labels": [...],
    "comments": [...]
  },
  "related_files": ["src/file1.py", "src/file2.py"],
  "analysis_summary": "AI analysis summary...",
  "prd_document": "# PRD Document in Markdown..."
}
```

### GET /health

```bash
curl http://localhost:8000/health
```

## 📄 PRD Döküman Formatı

Oluşturulan PRD belgeleri şu bölümlerden oluşur:

1. **Overview** - Projenin genel açıklaması
2. **Problem Statement** - Issue'nun detaylı tanımı
3. **Use Cases** - Kullanım senaryoları ve kabul kriterleri
4. **Technical Requirements** - Teknik gereksinimler (öncelik ve kategoriye göre)
5. **File Modifications** - Önerilen dosya değişiklikleri
6. **Constraints** - Kısıtlamalar
7. **Risks & Considerations** - Riskler ve dikkat edilecek noktalar
8. **Estimated Effort** - Tahmini iş yükü

## 🛠️ Teknik Detaylar

### Proje Yapısı

```
issue-to-prd/
├── main.py                 # FastAPI uygulaması
├── static/
│   └── index.html         # Web arayüzü
├── models/                # Pydantic modelleri
│   ├── issue.py           # GitHub issue modelleri
│   └── prd.py             # PRD document modelleri
├── services/              # İş mantığı servisleri
│   ├── github_service.py  # GitHub API entegrasyonu
│   ├── codebase_analyzer.py # Codebase analizi
│   └── prd_generator.py   # PRD döküman üretimi
├── requirements.txt       # Python bağımlılıkları
├── start.sh              # Başlatma scripti
└── README.md             # Bu dosya
```

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
uvicorn main:app --port 8001
```

## 📚 API Dokümantasyonu

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje eğitim amaçlıdır ve açık kaynak olarak sunulmuştur.

## 🆘 Destek

Sorunlar için GitHub Issues kullanın veya [demo_examples.md](demo_examples.md) dosyasını inceleyin.# Upsonic-issue-to-prd
