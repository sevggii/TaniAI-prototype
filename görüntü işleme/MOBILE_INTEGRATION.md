# 📱 TanıAI Mobil Entegrasyon Rehberi

## 🎯 Mobil Uygulama Entegrasyonu

Bu rehber, TanıAI Radyolojik Görüntü Analizi sistemini mobil uygulamanıza entegre etmek için gerekli tüm bilgileri içerir.

## 🚀 Hızlı Başlangıç

### 1. API Bağlantısı
```javascript
// JavaScript/React Native
const API_BASE_URL = "https://your-api-domain.com";
const API_KEY = "your_mobile_api_key";

// Görüntü analizi
const analyzeImage = async (imageBase64) => {
  const response = await fetch(`${API_BASE_URL}/mobile/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      image_data: imageBase64,
      analysis_type: "basic",
      target_size: "224,224"
    })
  });
  
  return await response.json();
};
```

### 2. Android (Kotlin/Java)
```kotlin
// Android - Retrofit ile
interface RadiologyAPI {
    @POST("mobile/analyze")
    suspend fun analyzeImage(
        @Header("Authorization") token: String,
        @Body request: AnalysisRequest
    ): Response<AnalysisResponse>
}

data class AnalysisRequest(
    val image_data: String,
    val analysis_type: String = "basic",
    val target_size: String = "224,224"
)
```

### 3. iOS (Swift)
```swift
// iOS - URLSession ile
struct RadiologyAPI {
    static let baseURL = "https://your-api-domain.com"
    static let apiKey = "your_mobile_api_key"
    
    static func analyzeImage(imageData: String) async throws -> AnalysisResponse {
        let url = URL(string: "\(baseURL)/mobile/analyze")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = AnalysisRequest(
            image_data: imageData,
            analysis_type: "basic",
            target_size: "224,224"
        )
        
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(AnalysisResponse.self, from: data)
    }
}
```

## 📡 API Endpoint'leri

### 🔍 Tek Görüntü Analizi
```http
POST /mobile/analyze
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "image_data": "base64_encoded_image",
  "analysis_type": "basic|advanced|medical",
  "target_size": "224,224"
}
```

**Yanıt:**
```json
{
  "success": true,
  "data": {
    "analysis_type": "basic",
    "features": {
      "mean_intensity": 128.5,
      "std_intensity": 45.2,
      "histogram_entropy": 7.8
    },
    "processing_info": {
      "original_size": [1024, 1024],
      "target_size": [224, 224],
      "file_size": 15678,
      "mobile_optimized": true
    }
  },
  "mobile_optimized": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 📊 Toplu Analiz
```http
POST /mobile/batch-analyze
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "images": ["base64_image1", "base64_image2"],
  "analysis_type": "basic"
}
```

### 🖼️ Görüntü Optimizasyonu
```http
POST /mobile/optimize-image
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "image_data": "base64_encoded_image",
  "target_size": "224,224",
  "quality": 85
}
```

## 🔧 Performans Optimizasyonu

### 1. Görüntü Boyutu Optimizasyonu
```javascript
// Görüntüyü mobil için optimize et
const optimizeImage = async (imageFile) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  // Hedef boyut
  const targetSize = 224;
  canvas.width = targetSize;
  canvas.height = targetSize;
  
  // Görüntüyü çiz
  ctx.drawImage(imageFile, 0, 0, targetSize, targetSize);
  
  // Base64'e çevir
  return canvas.toDataURL('image/jpeg', 0.85).split(',')[1];
};
```

### 2. Cache Yönetimi
```javascript
// Basit cache implementasyonu
class ImageCache {
  constructor(maxSize = 50) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }
  
  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
  
  get(key) {
    return this.cache.get(key);
  }
}
```

### 3. Offline Desteği
```javascript
// Service Worker ile offline analiz
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/mobile/analyze')) {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  }
});
```

## 🛡️ Güvenlik

### 1. API Anahtarı Yönetimi
```javascript
// Güvenli API anahtarı saklama
const getApiKey = () => {
  // Production'da güvenli storage kullanın
  return process.env.REACT_APP_API_KEY || 'dev_key_123';
};
```

### 2. Veri Şifreleme
```javascript
// Hassas verileri şifrele
import CryptoJS from 'crypto-js';

const encryptData = (data, key) => {
  return CryptoJS.AES.encrypt(JSON.stringify(data), key).toString();
};

const decryptData = (encryptedData, key) => {
  const bytes = CryptoJS.AES.decrypt(encryptedData, key);
  return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
};
```

## 📊 Hata Yönetimi

### 1. Retry Mekanizması
```javascript
const analyzeWithRetry = async (imageData, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const result = await analyzeImage(imageData);
      return result;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

### 2. Hata Kodları
```javascript
const handleApiError = (error) => {
  switch (error.status) {
    case 400:
      return "Geçersiz görüntü formatı";
    case 401:
      return "API anahtarı geçersiz";
    case 429:
      return "Çok fazla istek, lütfen bekleyin";
    case 500:
      return "Sunucu hatası, lütfen tekrar deneyin";
    default:
      return "Bilinmeyen hata oluştu";
  }
};
```

## 🎨 UI/UX Önerileri

### 1. Yükleme Durumu
```javascript
const AnalysisComponent = () => {
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const analyzeImage = async (image) => {
    setLoading(true);
    setProgress(0);
    
    // Progress simulation
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 10, 90));
    }, 200);
    
    try {
      const result = await analyzeImageAPI(image);
      setProgress(100);
      return result;
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  };
  
  return (
    <div>
      {loading && <ProgressBar value={progress} />}
      {/* UI components */}
    </div>
  );
};
```

### 2. Sonuç Gösterimi
```javascript
const ResultDisplay = ({ analysisResult }) => {
  if (!analysisResult.success) {
    return <ErrorComponent error={analysisResult.error} />;
  }
  
  return (
    <div className="result-container">
      <h3>Analiz Sonucu</h3>
      <div className="features">
        {Object.entries(analysisResult.data.features).map(([key, value]) => (
          <div key={key} className="feature-item">
            <span className="feature-name">{key}:</span>
            <span className="feature-value">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 📱 Platform Özel Entegrasyonlar

### React Native
```javascript
// react-native-image-picker ile
import { launchImageLibrary } from 'react-native-image-picker';

const selectAndAnalyzeImage = () => {
  launchImageLibrary({ mediaType: 'photo' }, (response) => {
    if (response.assets && response.assets[0]) {
      const imageUri = response.assets[0].uri;
      const base64 = convertToBase64(imageUri);
      analyzeImage(base64);
    }
  });
};
```

### Flutter
```dart
// Flutter ile
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

class RadiologyService {
  static Future<Map<String, dynamic>> analyzeImage(String base64Image) async {
    final response = await http.post(
      Uri.parse('$baseUrl/mobile/analyze'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $apiKey',
      },
      body: jsonEncode({
        'image_data': base64Image,
        'analysis_type': 'basic',
        'target_size': '224,224',
      }),
    );
    
    return jsonDecode(response.body);
  }
}
```

## 🔍 Test ve Debug

### 1. Unit Testler
```javascript
// Jest ile test
describe('RadiologyAPI', () => {
  test('should analyze image successfully', async () => {
    const mockImage = 'data:image/jpeg;base64,/9j/4AAQ...';
    const result = await analyzeImage(mockImage);
    
    expect(result.success).toBe(true);
    expect(result.data.features).toBeDefined();
  });
});
```

### 2. Debug Araçları
```javascript
// Debug modunda detaylı log
const debugAnalyze = async (imageData) => {
  console.log('🔍 Analiz başlatılıyor...');
  console.log('📊 Görüntü boyutu:', imageData.length);
  
  const startTime = Date.now();
  const result = await analyzeImage(imageData);
  const duration = Date.now() - startTime;
  
  console.log('⏱️ Analiz süresi:', duration + 'ms');
  console.log('✅ Sonuç:', result);
  
  return result;
};
```

## 📈 Performans Metrikleri

### Beklenen Performans
- **Tek Görüntü Analizi**: 2-5 saniye
- **Toplu Analiz (10 görüntü)**: 15-30 saniye
- **Görüntü Optimizasyonu**: <1 saniye
- **API Yanıt Süresi**: <500ms

### Optimizasyon İpuçları
1. **Görüntü boyutunu küçültün** (224x224 önerilen)
2. **JPEG kalitesini düşürün** (85% yeterli)
3. **Cache kullanın** tekrarlayan analizler için
4. **Batch analiz** yapın mümkün olduğunda
5. **Offline mod** ekleyin temel analizler için

## 🆘 Destek

### Hata Raporlama
```javascript
const reportError = async (error, context) => {
  await fetch('/mobile/error-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      error: error.message,
      stack: error.stack,
      context: context,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    })
  });
};
```

### İletişim
- **Email**: mobile-support@taniai.com
- **Dokümantasyon**: https://docs.taniai.com/mobile
- **GitHub**: https://github.com/taniai/mobile-sdk

---

**⚠️ Önemli Notlar:**
- API anahtarlarınızı güvenli tutun
- Rate limit'lere dikkat edin
- Offline mod için local storage kullanın
- Test ortamında önce deneyin
- Production'da HTTPS kullanın
