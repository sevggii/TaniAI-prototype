import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class VisionApiService {
  static const String baseUrl = String.fromEnvironment('VISION_API_URL', defaultValue: 'http://localhost:8006');
  
  /// Chest X-ray görüntüsünü analiz eder
  static Future<Map<String, dynamic>?> analyzeChestXray(File imageFile) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/analyze_cxr'),
      );
      
      // Görüntü dosyasını ekle
      request.files.add(
        await http.MultipartFile.fromPath(
          'cxr_image',
          imageFile.path,
        ),
      );
      
      var response = await request.send();
      
      if (response.statusCode == 200) {
        var responseBody = await response.stream.bytesToString();
        return json.decode(responseBody);
      } else {
        print('Vision API Error: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Vision API Exception: $e');
      return null;
    }
  }
  
  /// Belirti tabanlı tanı yapar
  static Future<Map<String, dynamic>?> diagnoseSymptoms(Map<String, bool> symptoms) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/diagnose'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'symptoms': symptoms}),
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        print('Diagnosis API Error: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Diagnosis API Exception: $e');
      return null;
    }
  }
  
  /// Kombine tanı (belirti + görüntü)
  static Future<Map<String, dynamic>?> combinedDiagnosis({
    required Map<String, bool> symptoms,
    File? chestXray,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/combined_diagnosis'),
      );
      
      // Belirtileri ekle
      request.fields['symptoms'] = json.encode(symptoms);
      
      // Görüntü varsa ekle
      if (chestXray != null) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'cxr_image',
            chestXray.path,
          ),
        );
      }
      
      var response = await request.send();
      
      if (response.statusCode == 200) {
        var responseBody = await response.stream.bytesToString();
        return json.decode(responseBody);
      } else {
        print('Combined Diagnosis API Error: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Combined Diagnosis API Exception: $e');
      return null;
    }
  }
}
