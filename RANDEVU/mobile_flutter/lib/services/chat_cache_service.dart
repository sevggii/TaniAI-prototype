import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class ChatCacheService {
  static final ChatCacheService _instance = ChatCacheService._internal();
  factory ChatCacheService() => _instance;
  ChatCacheService._internal();

  static const String _cachePrefix = 'chat_cache_';
  static const Duration _cacheExpiry = Duration(hours: 24);

  // Cache'den yanıt al
  Future<String?> getCachedResponse(String question) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = _cachePrefix + _hashQuestion(question);
      final cachedData = prefs.getString(cacheKey);
      
      if (cachedData != null) {
        final data = jsonDecode(cachedData);
        final timestamp = DateTime.parse(data['timestamp']);
        
        // Cache süresi dolmuş mu?
        if (DateTime.now().difference(timestamp) < _cacheExpiry) {
          print('✅ Cache\'den yanıt bulundu: $question');
          return data['response'];
        } else {
          // Eski cache'i sil
          await prefs.remove(cacheKey);
        }
      }
      
      return null;
    } catch (e) {
      print('Cache okuma hatası: $e');
      return null;
    }
  }

  // Cache'e yanıt kaydet
  Future<void> cacheResponse(String question, String response) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = _cachePrefix + _hashQuestion(question);
      
      final data = {
        'response': response,
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      await prefs.setString(cacheKey, jsonEncode(data));
      print('💾 Yanıt cache\'e kaydedildi');
    } catch (e) {
      print('Cache yazma hatası: $e');
    }
  }

  // Soruyu hash'le (basit bir hash fonksiyonu)
  String _hashQuestion(String question) {
    return question
        .toLowerCase()
        .trim()
        .replaceAll(RegExp(r'\s+'), '_')
        .replaceAll(RegExp(r'[^\w\s]'), '')
        .substring(0, question.length > 50 ? 50 : question.length);
  }

  // Tüm cache'i temizle
  Future<void> clearCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys();
      
      for (final key in keys) {
        if (key.startsWith(_cachePrefix)) {
          await prefs.remove(key);
        }
      }
      
      print('🧹 Cache temizlendi');
    } catch (e) {
      print('Cache temizleme hatası: $e');
    }
  }

  // Hızlı yanıtlar (sık sorulanlar için)
  static final Map<String, String> quickResponses = {
    'merhaba': 'Merhaba! 👋 Size nasıl yardımcı olabilirim?',
    'selam': 'Selam! 😊 Nasılsınız?',
    'nasilsin': 'İyiyim, teşekkür ederim! Siz nasılsınız? Size nasıl yardımcı olabilirim?',
    'tesekkur': 'Rica ederim! 😊 Başka bir şey için yardıma ihtiyacınız olursa çekinmeden sorun.',
    'saol': 'Bir şey değil! 🌟 Size yardımcı olmaktan mutluluk duyarım.',
    'basim agriyor': '💧 Baş ağrısı için önce 1-2 bardak su için ve dinlenin. Daha detaylı bilgi ister misiniz?',
    'bas agrisi': '💧 Baş ağrısı için önce 1-2 bardak su için ve dinlenin. Daha detaylı bilgi ister misiniz?',
  };

  // Hızlı yanıt kontrolü
  String? getQuickResponse(String message) {
    final cleaned = message.toLowerCase().trim().replaceAll(RegExp(r'[^\w\s]'), '');
    
    for (final entry in quickResponses.entries) {
      if (cleaned.contains(entry.key)) {
        return entry.value;
      }
    }
    
    return null;
  }
}

