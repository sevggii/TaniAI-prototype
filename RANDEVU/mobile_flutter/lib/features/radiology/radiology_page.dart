import 'dart:io';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

class RadiologyPage extends StatefulWidget {
  const RadiologyPage({super.key});

  @override
  State<RadiologyPage> createState() => _RadiologyPageState();
}

class _RadiologyPageState extends State<RadiologyPage> {
  final ImagePicker _picker = ImagePicker();
  XFile? _image;
  bool _isAnalyzing = false;
  Map<String, dynamic>? _analysisResult;
  String? _errorMessage;

  Future<void> _pick(ImageSource source) async {
    try {
      final img = await _picker.pickImage(source: source, imageQuality: 85);
      if (img != null) {
        setState(() {
          _image = img;
          _analysisResult = null;
          _errorMessage = null;
        });
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Görüntü seçilemedi: $e')),
      );
    }
  }

  Future<void> _analyzeImage() async {
    if (_image == null) return;

    setState(() {
      _isAnalyzing = true;
      _errorMessage = null;
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://localhost:8006/analyze_cxr'),
      );

      request.files.add(
        await http.MultipartFile.fromPath(
          'cxr_image',
          _image!.path,
        ),
      );

      var response = await request.send();

      if (response.statusCode == 200) {
        var responseBody = await response.stream.bytesToString();
        var result = json.decode(responseBody);

        setState(() {
          _analysisResult = result;
          _isAnalyzing = false;
        });
      } else {
        setState(() {
          _errorMessage = 'Analiz hatası: ${response.statusCode}';
          _isAnalyzing = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Bağlantı hatası: $e';
        _isAnalyzing = false;
      });
    }
  }

  Widget _buildAnalysisResult() {
    if (_analysisResult == null) return const SizedBox.shrink();

    if (_analysisResult!.containsKey('error')) {
      return Card(
        color: Colors.red.shade50,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.error, color: Colors.red.shade700),
                  const SizedBox(width: 8),
                  Text(
                    'Analiz Hatası',
                    style: TextStyle(
                      color: Colors.red.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(_analysisResult!['error']),
            ],
          ),
        ),
      );
    }

    final probabilities = _analysisResult!['probabilities'] as Map<String, dynamic>;
    final analysis = _analysisResult!['analysis'] as Map<String, dynamic>;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.analytics, color: Colors.blue.shade700),
                const SizedBox(width: 8),
                Text(
                  'Analiz Sonuçları',
                  style: TextStyle(
                    color: Colors.blue.shade700,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // COVID-19 olasılığı
            _buildProbabilityBar(
              'COVID-19',
              probabilities['COVID-19'] ?? 0.0,
              Colors.red,
            ),
            const SizedBox(height: 12),
            
            // Normal olasılığı
            _buildProbabilityBar(
              'Normal',
              probabilities['Normal'] ?? 0.0,
              Colors.green,
            ),
            const SizedBox(height: 16),
            
            // Güven skoru
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.psychology, color: Colors.blue.shade700),
                  const SizedBox(width: 8),
                  Text(
                    'Güven Skoru: ${(analysis['confidence'] * 100).toStringAsFixed(1)}%',
                    style: TextStyle(
                      color: Colors.blue.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProbabilityBar(String label, double probability, Color color) {
    final percentage = (probability * 100).toStringAsFixed(1);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            Text(
              '$percentage%',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: probability,
          backgroundColor: color.withOpacity(0.2),
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Radyolojik Görüntü Analizi'),
        backgroundColor: Colors.blue.shade50,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Görüntü seçme butonları
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                SizedBox(
                  height: 48,
                  child: FilledButton.icon(
                    onPressed: _isAnalyzing ? null : () => _pick(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Galeriden Seç'),
                  ),
                ),
                SizedBox(
                  height: 48,
                  child: OutlinedButton.icon(
                    onPressed: _isAnalyzing ? null : () => _pick(ImageSource.camera),
                    icon: const Icon(Icons.photo_camera),
                    label: const Text('Kameradan Çek'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            // Seçilen görüntü
            if (_image != null)
              Card(
                clipBehavior: Clip.antiAlias,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                child: AspectRatio(
                  aspectRatio: 4 / 3,
                  child: Image.file(File(_image!.path), fit: BoxFit.cover),
                ),
              ),
            
            const SizedBox(height: 16),
            
            // Analiz butonu
            SizedBox(
              height: 48,
              child: FilledButton.icon(
                onPressed: _image != null && !_isAnalyzing ? _analyzeImage : null,
                icon: _isAnalyzing 
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.analytics),
                label: Text(_isAnalyzing ? 'Analiz Ediliyor...' : 'Yapay Zekâ ile Analiz Et'),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Hata mesajı
            if (_errorMessage != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      Icon(Icons.error, color: Colors.red.shade700),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(color: Colors.red.shade700),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            
            const SizedBox(height: 16),
            
            // Analiz sonuçları
            Expanded(
              child: _buildAnalysisResult(),
            ),
          ],
        ),
      ),
    );
  }
}
