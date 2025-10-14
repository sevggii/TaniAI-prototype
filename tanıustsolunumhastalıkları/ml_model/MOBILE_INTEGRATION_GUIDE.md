# 📱 Mobil Uygulama Entegrasyon Rehberi

## 🎯 Genel Bakış

Bu rehber, Üst Solunum Yolu Hastalık Tanı Sistemi'ni mobil uygulamanıza nasıl entegre edeceğinizi açıklar.

---

## 🚀 Entegrasyon Seçenekleri

### **Seçenek 1: REST API (Önerilen)** ⭐

#### Neden Öneriliyor?
- ✅ Model sunucuda güvenli
- ✅ Mobil uygulama hafif kalır
- ✅ Kolay güncellenebilir
- ✅ Her platform için uygun (iOS, Android, Flutter, React Native)

#### Backend Kurulumu

```bash
# 1. Gereksinimleri yükle
cd UstSolunumYolu/ml_model
pip install fastapi uvicorn pydantic

# 2. API'yi başlat
python mobile_api_example.py

# Veya uvicorn ile:
uvicorn mobile_api_example:app --host 0.0.0.0 --port 8000
```

#### API Kullanımı

**Endpoint:** `POST http://localhost:8000/api/v1/diagnose`

**Request Body:**
```json
{
  "symptoms": "Ateşim var, nefes alamıyorum, koku alamıyorum",
  "patient_id": "optional-patient-id"
}
```

**Response:**
```json
{
  "diagnosis_id": "uuid-here",
  "disease": "COVID-19",
  "confidence": 0.998,
  "confidence_percentage": "%99.8",
  "severity": "Severe",
  "detected_symptoms": {
    "ateş": 1.0,
    "nefes_darlığı": 1.0,
    "koku_kaybı": 1.0
  },
  "recommendations": [
    "İzolasyon uygulayın",
    "PCR testi yaptırın",
    "Sağlık kuruluşuna bildirin"
  ],
  "probabilities": {
    "COVID-19": 0.998,
    "Grip": 0.001,
    "Soğuk Algınlığı": 0.0,
    "Mevsimsel Alerji": 0.001
  },
  "timestamp": "2024-10-14T12:34:56",
  "warning": "⚠️ Bu sistem ön tanı amaçlıdır. Kesin tanı için doktora başvurun!"
}
```

---

## 📱 Platform Bazlı Örnekler

### 🎨 **Flutter (Dart)**

#### 1. Dependency Ekle (`pubspec.yaml`)
```yaml
dependencies:
  http: ^1.1.0
  provider: ^6.0.5
```

#### 2. API Service Oluştur
```dart
// lib/services/diagnosis_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class DiagnosisService {
  static const String baseUrl = 'http://YOUR_SERVER_IP:8000';
  
  Future<DiagnosisResult> diagnose(String symptoms) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/diagnose'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'symptoms': symptoms,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(utf8.decode(response.bodyBytes));
        return DiagnosisResult.fromJson(data);
      } else {
        throw Exception('Tanı başarısız: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Bağlantı hatası: $e');
    }
  }
  
  Future<List<Disease>> getSupportedDiseases() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/diseases'),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      return (data['supported_diseases'] as List)
          .map((d) => Disease.fromJson(d))
          .toList();
    }
    throw Exception('Hastalık listesi alınamadı');
  }
}

// Model sınıfları
class DiagnosisResult {
  final String diagnosisId;
  final String disease;
  final double confidence;
  final String confidencePercentage;
  final String severity;
  final Map<String, double> detectedSymptoms;
  final List<String> recommendations;
  final Map<String, double> probabilities;
  final String timestamp;
  final String warning;
  
  DiagnosisResult({
    required this.diagnosisId,
    required this.disease,
    required this.confidence,
    required this.confidencePercentage,
    required this.severity,
    required this.detectedSymptoms,
    required this.recommendations,
    required this.probabilities,
    required this.timestamp,
    required this.warning,
  });
  
  factory DiagnosisResult.fromJson(Map<String, dynamic> json) {
    return DiagnosisResult(
      diagnosisId: json['diagnosis_id'],
      disease: json['disease'],
      confidence: json['confidence'].toDouble(),
      confidencePercentage: json['confidence_percentage'],
      severity: json['severity'],
      detectedSymptoms: Map<String, double>.from(
        json['detected_symptoms'].map((k, v) => MapEntry(k, v.toDouble()))
      ),
      recommendations: List<String>.from(json['recommendations']),
      probabilities: Map<String, double>.from(
        json['probabilities'].map((k, v) => MapEntry(k, v.toDouble()))
      ),
      timestamp: json['timestamp'],
      warning: json['warning'],
    );
  }
}

class Disease {
  final String name;
  final String accuracy;
  final List<String> keySymptoms;
  
  Disease({
    required this.name,
    required this.accuracy,
    required this.keySymptoms,
  });
  
  factory Disease.fromJson(Map<String, dynamic> json) {
    return Disease(
      name: json['name'],
      accuracy: json['accuracy'],
      keySymptoms: List<String>.from(json['key_symptoms']),
    );
  }
}
```

#### 3. UI Örneği
```dart
// lib/screens/diagnosis_screen.dart
import 'package:flutter/material.dart';
import '../services/diagnosis_service.dart';

class DiagnosisScreen extends StatefulWidget {
  @override
  _DiagnosisScreenState createState() => _DiagnosisScreenState();
}

class _DiagnosisScreenState extends State<DiagnosisScreen> {
  final _symptomController = TextEditingController();
  final _diagnosisService = DiagnosisService();
  
  bool _isLoading = false;
  DiagnosisResult? _result;
  String? _error;
  
  Future<void> _diagnose() async {
    if (_symptomController.text.trim().isEmpty) {
      setState(() {
        _error = 'Lütfen semptomlarınızı giriniz';
      });
      return;
    }
    
    setState(() {
      _isLoading = true;
      _error = null;
      _result = null;
    });
    
    try {
      final result = await _diagnosisService.diagnose(_symptomController.text);
      setState(() {
        _result = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🏥 Hastalık Tanı'),
        backgroundColor: Colors.teal,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Semptom girişi
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Semptomlarmızı Giriniz',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 12),
                    TextField(
                      controller: _symptomController,
                      maxLines: 4,
                      decoration: InputDecoration(
                        hintText: 'Örn: Ateşim var, nefes alamıyorum, koku alamıyorum',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _isLoading ? null : _diagnose,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal,
                        padding: EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: _isLoading
                          ? CircularProgressIndicator(color: Colors.white)
                          : Text(
                              'Tanı Yap',
                              style: TextStyle(fontSize: 16),
                            ),
                    ),
                  ],
                ),
              ),
            ),
            
            SizedBox(height: 16),
            
            // Hata mesajı
            if (_error != null)
              Card(
                color: Colors.red[50],
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    _error!,
                    style: TextStyle(color: Colors.red[900]),
                  ),
                ),
              ),
            
            // Sonuçlar
            if (_result != null) ...[
              // Ana tanı
              Card(
                color: _getColorForSeverity(_result!.severity),
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Icon(
                        _getIconForDisease(_result!.disease),
                        size: 64,
                        color: Colors.white,
                      ),
                      SizedBox(height: 8),
                      Text(
                        _result!.disease,
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        _result!.confidencePercentage,
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.white70,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Ciddiyet: ${_result!.severity}',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              // Tespit edilen semptomlar
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Tespit Edilen Semptomlar',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 12),
                      ..._result!.detectedSymptoms.entries.map((e) =>
                        Padding(
                          padding: EdgeInsets.only(bottom: 8),
                          child: Row(
                            children: [
                              Expanded(child: Text(e.key)),
                              Container(
                                width: 100,
                                child: LinearProgressIndicator(
                                  value: e.value,
                                  backgroundColor: Colors.grey[200],
                                  color: Colors.teal,
                                ),
                              ),
                              SizedBox(width: 8),
                              Text('${(e.value * 100).toInt()}%'),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              // Öneriler
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Öneriler',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 12),
                      ..._result!.recommendations.map((r) =>
                        Padding(
                          padding: EdgeInsets.only(bottom: 8),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('• ', style: TextStyle(fontSize: 18)),
                              Expanded(child: Text(r)),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              
              // Uyarı
              Card(
                color: Colors.orange[50],
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    _result!.warning,
                    style: TextStyle(
                      color: Colors.orange[900],
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Color _getColorForSeverity(String severity) {
    switch (severity.toLowerCase()) {
      case 'mild':
        return Colors.green;
      case 'moderate':
        return Colors.orange;
      case 'severe':
        return Colors.red;
      case 'critical':
        return Colors.red[900]!;
      default:
        return Colors.blue;
    }
  }
  
  IconData _getIconForDisease(String disease) {
    if (disease.contains('COVID')) return Icons.coronavirus;
    if (disease.contains('Grip')) return Icons.sick;
    if (disease.contains('Soğuk')) return Icons.air;
    if (disease.contains('Alerji')) return Icons.local_florist;
    return Icons.medical_services;
  }
  
  @override
  void dispose() {
    _symptomController.dispose();
    super.dispose();
  }
}
```

---

### 🍏 **iOS (Swift)**

```swift
// DiagnosisService.swift
import Foundation

struct SymptomInput: Codable {
    let symptoms: String
    let patient_id: String?
}

struct DiagnosisResult: Codable {
    let diagnosis_id: String
    let disease: String
    let confidence: Double
    let confidence_percentage: String
    let severity: String
    let detected_symptoms: [String: Double]
    let recommendations: [String]
    let probabilities: [String: Double]
    let timestamp: String
    let warning: String
}

class DiagnosisService {
    static let shared = DiagnosisService()
    private let baseURL = "http://YOUR_SERVER_IP:8000"
    
    func diagnose(symptoms: String) async throws -> DiagnosisResult {
        let url = URL(string: "\(baseURL)/api/v1/diagnose")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let input = SymptomInput(symptoms: symptoms, patient_id: nil)
        request.httpBody = try JSONEncoder().encode(input)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw NSError(domain: "DiagnosisError", code: -1)
        }
        
        return try JSONDecoder().decode(DiagnosisResult.self, from: data)
    }
}

// SwiftUI View
import SwiftUI

struct DiagnosisView: View {
    @State private var symptoms = ""
    @State private var result: DiagnosisResult?
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Semptom girişi
                    VStack(alignment: .leading) {
                        Text("Semptomlarınızı Giriniz")
                            .font(.headline)
                        
                        TextEditor(text: $symptoms)
                            .frame(height: 120)
                            .padding(8)
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(8)
                    }
                    .padding()
                    
                    // Tanı butonu
                    Button(action: diagnose) {
                        if isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Tanı Yap")
                                .fontWeight(.bold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.teal)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .padding(.horizontal)
                    .disabled(isLoading || symptoms.isEmpty)
                    
                    // Sonuçlar
                    if let result = result {
                        VStack(spacing: 16) {
                            // Ana tanı kartı
                            VStack {
                                Image(systemName: iconForDisease(result.disease))
                                    .font(.system(size: 64))
                                    .foregroundColor(.white)
                                
                                Text(result.disease)
                                    .font(.title)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                
                                Text(result.confidence_percentage)
                                    .font(.title3)
                                    .foregroundColor(.white.opacity(0.8))
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(colorForSeverity(result.severity))
                            .cornerRadius(12)
                            .padding(.horizontal)
                            
                            // Öneriler
                            VStack(alignment: .leading, spacing: 12) {
                                Text("Öneriler")
                                    .font(.headline)
                                
                                ForEach(result.recommendations, id: \.self) { rec in
                                    HStack(alignment: .top) {
                                        Text("•")
                                        Text(rec)
                                    }
                                }
                            }
                            .padding()
                            .background(Color.gray.opacity(0.1))
                            .cornerRadius(12)
                            .padding(.horizontal)
                            
                            // Uyarı
                            Text(result.warning)
                                .font(.caption)
                                .foregroundColor(.orange)
                                .padding()
                                .background(Color.orange.opacity(0.1))
                                .cornerRadius(8)
                                .padding(.horizontal)
                        }
                    }
                    
                    // Hata mesajı
                    if let error = errorMessage {
                        Text(error)
                            .foregroundColor(.red)
                            .padding()
                    }
                }
            }
            .navigationTitle("🏥 Hastalık Tanı")
        }
    }
    
    func diagnose() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let diagnosisResult = try await DiagnosisService.shared.diagnose(symptoms: symptoms)
                await MainActor.run {
                    self.result = diagnosisResult
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.errorMessage = "Tanı başarısız: \(error.localizedDescription)"
                    self.isLoading = false
                }
            }
        }
    }
    
    func colorForSeverity(_ severity: String) -> Color {
        switch severity.lowercased() {
        case "mild": return .green
        case "moderate": return .orange
        case "severe": return .red
        default: return .blue
        }
    }
    
    func iconForDisease(_ disease: String) -> String {
        if disease.contains("COVID") { return "cross.case.fill" }
        if disease.contains("Grip") { return "bed.double.fill" }
        if disease.contains("Soğuk") { return "wind" }
        if disease.contains("Alerji") { return "leaf.fill" }
        return "stethoscope"
    }
}
```

---

### 🤖 **Android (Kotlin + Jetpack Compose)**

```kotlin
// DiagnosisService.kt
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody

@Serializable
data class SymptomInput(
    val symptoms: String,
    val patient_id: String? = null
)

@Serializable
data class DiagnosisResult(
    val diagnosis_id: String,
    val disease: String,
    val confidence: Double,
    val confidence_percentage: String,
    val severity: String,
    val detected_symptoms: Map<String, Double>,
    val recommendations: List<String>,
    val probabilities: Map<String, Double>,
    val timestamp: String,
    val warning: String
)

class DiagnosisService {
    private val client = OkHttpClient()
    private val baseUrl = "http://YOUR_SERVER_IP:8000"
    private val json = Json { ignoreUnknownKeys = true }
    
    suspend fun diagnose(symptoms: String): DiagnosisResult = withContext(Dispatchers.IO) {
        val input = SymptomInput(symptoms = symptoms)
        val jsonBody = json.encodeToString(input)
        
        val request = Request.Builder()
            .url("$baseUrl/api/v1/diagnose")
            .post(jsonBody.toRequestBody("application/json".toMediaType()))
            .build()
        
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw Exception("Tanı başarısız: ${response.code}")
            }
            
            val responseBody = response.body?.string() ?: throw Exception("Boş yanıt")
            json.decodeFromString<DiagnosisResult>(responseBody)
        }
    }
}

// DiagnosisScreen.kt (Jetpack Compose)
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.launch

@Composable
fun DiagnosisScreen(viewModel: DiagnosisViewModel = viewModel()) {
    val state by viewModel.state.collectAsState()
    val scope = rememberCoroutineScope()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("🏥 Hastalık Tanı") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Semptom girişi
            OutlinedTextField(
                value = state.symptoms,
                onValueChange = { viewModel.updateSymptoms(it) },
                label = { Text("Semptomlarınızı Giriniz") },
                placeholder = { Text("Örn: Ateşim var, nefes alamıyorum") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(150.dp),
                maxLines = 5
            )
            
            // Tanı butonu
            Button(
                onClick = {
                    scope.launch {
                        viewModel.diagnose()
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !state.isLoading && state.symptoms.isNotBlank()
            ) {
                if (state.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White
                    )
                } else {
                    Text("Tanı Yap")
                }
            }
            
            // Sonuçlar
            state.result?.let { result ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = getSeverityColor(result.severity)
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = result.disease,
                            style = MaterialTheme.typography.headlineMedium,
                            color = Color.White
                        )
                        Text(
                            text = result.confidence_percentage,
                            style = MaterialTheme.typography.titleMedium,
                            color = Color.White.copy(alpha = 0.8f)
                        )
                    }
                }
                
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Öneriler",
                            style = MaterialTheme.typography.titleMedium
                        )
                        result.recommendations.forEach { rec ->
                            Text("• $rec")
                        }
                    }
                }
            }
            
            // Hata mesajı
            state.error?.let { error ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = Color.Red.copy(alpha = 0.1f)
                    )
                ) {
                    Text(
                        text = error,
                        modifier = Modifier.padding(16.dp),
                        color = Color.Red
                    )
                }
            }
        }
    }
}

fun getSeverityColor(severity: String): Color {
    return when (severity.lowercase()) {
        "mild" -> Color(0xFF4CAF50)
        "moderate" -> Color(0xFFFF9800)
        "severe" -> Color(0xFFF44336)
        else -> Color(0xFF2196F3)
    }
}
```

---

### ⚛️ **React Native**

```javascript
// DiagnosisService.js
const API_BASE_URL = 'http://YOUR_SERVER_IP:8000';

export const diagnose = async (symptoms) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/diagnose`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ symptoms }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Diagnosis error:', error);
    throw error;
  }
};

export const getSupportedDiseases = async () => {
  const response = await fetch(`${API_BASE_URL}/api/v1/diseases`);
  return await response.json();
};

// DiagnosisScreen.js
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
} from 'react-native';
import { diagnose } from './DiagnosisService';

export default function DiagnosisScreen() {
  const [symptoms, setSymptoms] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDiagnose = async () => {
    if (!symptoms.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const diagnosisResult = await diagnose(symptoms);
      setResult(diagnosisResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'mild': return '#4CAF50';
      case 'moderate': return '#FF9800';
      case 'severe': return '#F44336';
      default: return '#2196F3';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerText}>🏥 Hastalık Tanı</Text>
      </View>

      {/* Semptom girişi */}
      <View style={styles.card}>
        <Text style={styles.label}>Semptomlarınızı Giriniz</Text>
        <TextInput
          style={styles.textInput}
          multiline
          numberOfLines={4}
          value={symptoms}
          onChangeText={setSymptoms}
          placeholder="Örn: Ateşim var, nefes alamıyorum"
        />
        
        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleDiagnose}
          disabled={loading || !symptoms.trim()}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Tanı Yap</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Sonuçlar */}
      {result && (
        <>
          <View style={[
            styles.resultCard,
            { backgroundColor: getSeverityColor(result.severity) }
          ]}>
            <Text style={styles.diseaseText}>{result.disease}</Text>
            <Text style={styles.confidenceText}>
              {result.confidence_percentage}
            </Text>
            <Text style={styles.severityText}>
              Ciddiyet: {result.severity}
            </Text>
          </View>

          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Öneriler</Text>
            {result.recommendations.map((rec, index) => (
              <Text key={index} style={styles.recommendation}>
                • {rec}
              </Text>
            ))}
          </View>

          <View style={styles.warningCard}>
            <Text style={styles.warningText}>{result.warning}</Text>
          </View>
        </>
      )}

      {/* Hata mesajı */}
      {error && (
        <View style={styles.errorCard}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#009688',
    padding: 20,
    alignItems: 'center',
  },
  headerText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  card: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    elevation: 2,
  },
  label: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    minHeight: 100,
    textAlignVertical: 'top',
    marginBottom: 16,
  },
  button: {
    backgroundColor: '#009688',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  resultCard: {
    margin: 16,
    padding: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  diseaseText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  confidenceText: {
    fontSize: 20,
    color: 'rgba(255,255,255,0.9)',
    marginBottom: 4,
  },
  severityText: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.8)',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  recommendation: {
    fontSize: 14,
    marginBottom: 8,
    lineHeight: 20,
  },
  warningCard: {
    backgroundColor: '#FFF3E0',
    margin: 16,
    padding: 16,
    borderRadius: 8,
  },
  warningText: {
    color: '#E65100',
    fontWeight: 'bold',
  },
  errorCard: {
    backgroundColor: '#FFEBEE',
    margin: 16,
    padding: 16,
    borderRadius: 8,
  },
  errorText: {
    color: '#C62828',
  },
});
```

---

## 🚀 Deployment Seçenekleri

### **1. Heroku**
```bash
# Procfile oluştur
echo "web: uvicorn mobile_api_example:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create my-diagnosis-api
git push heroku main
```

### **2. AWS (EC2)**
```bash
# EC2 instance'ına bağlan
ssh -i key.pem ubuntu@ec2-xxx.amazonaws.com

# Kurulum
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements_professional.txt
pip3 install fastapi uvicorn

# Servisi başlat
uvicorn mobile_api_example:app --host 0.0.0.0 --port 8000
```

### **3. Docker**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements_professional.txt .
RUN pip install --no-cache-dir -r requirements_professional.txt
RUN pip install fastapi uvicorn

COPY . .

EXPOSE 8000

CMD ["uvicorn", "mobile_api_example:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build ve çalıştır
docker build -t diagnosis-api .
docker run -p 8000:8000 diagnosis-api
```

---

## 🔒 Güvenlik Önerileri

### 1. **API Key Kullanımı**
```python
# API'ye güvenlik ekle
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Endpoint'e ekle
@app.post("/api/v1/diagnose", dependencies=[Depends(verify_api_key)])
async def diagnose(...):
    ...
```

### 2. **Rate Limiting**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/diagnose")
@limiter.limit("10/minute")
async def diagnose(...):
    ...
```

### 3. **HTTPS Kullanımı**
Production'da mutlaka HTTPS kullanın (Let's Encrypt ile ücretsiz)

---

## 📊 Test Etme

### cURL ile Test
```bash
curl -X POST "http://localhost:8000/api/v1/diagnose" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": "Ateşim var, nefes alamıyorum, koku alamıyorum"}'
```

### Postman ile Test
1. POST: `http://localhost:8000/api/v1/diagnose`
2. Body (JSON):
```json
{
  "symptoms": "Ateşim var, nefes alamıyorum, koku alamıyorum"
}
```

---

## 🎯 Sonuç

Sisteminiz mobil uygulamaya **tamamen entegre edilebilir**! 

### ✅ Önerilen Yol:
1. **FastAPI ile REST API** oluşturun (sağladım)
2. **AWS/Heroku'ya deploy** edin
3. **Flutter/React Native** ile mobil uygulama geliştirin
4. API'yi çağırın

### 📱 Uygulama Özellikleri:
- Semptom girişi (ses tanıma eklenebilir)
- Anında tanı sonucu
- Geçmiş kayıtları
- Doktor önerileri
- Acil durum uyarıları

Başka sorunuz varsa yardımcı olmaktan mutluluk duyarım! 🚀

