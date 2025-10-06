import 'dart:convert';
import 'package:http/http.dart' as http;

class LLMService {
  static const String _baseUrl = 'http://localhost:8001'; // FastAPI backend
  static const Duration _timeout = Duration(seconds: 30);

  /// LLM ile chat yanıtı al
  static Future<String> getChatResponse(String userMessage) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/chat'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'message': userMessage,
          'context': 'medical_assistant',
        }),
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['response'] ?? 'Üzgünüm, bir yanıt oluşturamadım.';
      } else {
        return 'Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.';
      }
    } catch (e) {
      print('LLM API Error: $e');
      return _getFallbackResponse(userMessage);
    }
  }

  /// Klinik triyaj için LLM yanıtı al
  static Future<Map<String, dynamic>> getTriageResponse(String symptoms) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/triage'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'text': symptoms,
        }),
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'data': data,
        };
      } else {
        return {
          'success': false,
          'error': 'Triyaj servisi şu anda kullanılamıyor.',
        };
      }
    } catch (e) {
      print('Triage API Error: $e');
      return {
        'success': false,
        'error': 'Triyaj servisi şu anda kullanılamıyor.',
      };
    }
  }

  /// Klinik önerisi al
  static Future<Map<String, dynamic>> getClinicRecommendation(String symptoms) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/recommend-clinic'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'symptoms': symptoms,
        }),
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return {
          'success': true,
          'data': data,
        };
      } else {
        return {
          'success': false,
          'error': 'Klinik önerisi servisi şu anda kullanılamıyor.',
        };
      }
    } catch (e) {
      print('Clinic Recommendation API Error: $e');
      return {
        'success': false,
        'error': 'Klinik önerisi servisi şu anda kullanılamıyor.',
      };
    }
  }

  /// Fallback yanıtlar (LLM servisi çalışmıyorsa)
  static String _getFallbackResponse(String userMessage) {
    final message = userMessage.toLowerCase();
    
    // Baş ağrısı - spesifik yanıt
    if (message.contains('baş') && message.contains('ağrı')) {
      return 'Baş ağrınız için size yardımcı olabilirim. Baş ağrısı birçok nedenden kaynaklanabilir:\n\n'
          '🔍 **Olası Nedenler:**\n'
          '• Stres ve yorgunluk\n'
          '• Migren\n'
          '• Sinüzit\n'
          '• Tansiyon\n'
          '• Dehidrasyon\n\n'
          '💡 **Öneriler:**\n'
          '• Bol su için\n'
          '• Karanlık ve sessiz bir yerde dinlenin\n'
          '• Hafif masaj yapın\n'
          '• Ağrı kesici alabilirsiniz\n\n'
          '⚠️ **Dikkat:** Şiddetli, ani başlayan veya sürekli baş ağrıları için mutlaka doktora başvurun.';
    }
    
    // Karın ağrısı - spesifik yanıt
    if (message.contains('karın') && message.contains('ağrı')) {
      return 'Karın ağrınız için size yardımcı olabilirim. Karın ağrısı farklı nedenlerden kaynaklanabilir:\n\n'
          '🔍 **Olası Nedenler:**\n'
          '• Hazımsızlık\n'
          '• Gaz\n'
          '• Stres\n'
          '• Gıda intoleransı\n'
          '• Mide ülseri\n\n'
          '💡 **Öneriler:**\n'
          '• Hafif yiyecekler tüketin\n'
          '• Bol su için\n'
          '• Sıcak su torbası kullanın\n'
          '• Dinlenin\n\n'
          '⚠️ **Dikkat:** Şiddetli, ani başlayan veya sürekli karın ağrıları için mutlaka doktora başvurun.';
    }
    
    // Göğüs ağrısı - acil durum
    if (message.contains('göğüs') && message.contains('ağrı')) {
      return '🚨 **ACİL DURUM!**\n\n'
          'Göğüs ağrısı ciddi bir durum olabilir. Hemen aşağıdaki adımları takip edin:\n\n'
          '📞 **Hemen Yapılacaklar:**\n'
          '• 112\'yi arayın\n'
          '• Acil servise gidin\n'
          '• Yanınızda birisi olsun\n'
          '• Dinlenin, hareket etmeyin\n\n'
          '⚠️ **Göğüs ağrısı kalp krizi belirtisi olabilir. Zaman kaybetmeyin!**';
    }
    
    // Randevu ile ilgili
    if (message.contains('randevu') || message.contains('appointment') || message.contains('doktor')) {
      return 'Randevu almak için size yardımcı olabilirim! 🏥\n\n'
          '**Hangi bölüm için randevu almak istiyorsunuz?**\n\n'
          '📋 **Mevcut Bölümler:**\n'
          '• Genel Pratisyen\n'
          '• Kardiyoloji\n'
          '• Nöroloji\n'
          '• Ortopedi\n'
          '• Dermatoloji\n'
          '• İç Hastalıkları\n\n'
          '💡 **Randevu Seçenekleri:**\n'
          '• 📞 Sesli randevu (telefon)\n'
          '• 🏥 Yakın hastaneler\n'
          '• 📅 Online randevu sistemi';
    }
    
    // Semptom ile ilgili - genel
    if (message.contains('semptom') || message.contains('hasta') || message.contains('ağrı') || message.contains('rahatsızlık')) {
      return 'Semptomlarınız hakkında konuşabiliriz. Size daha iyi yardımcı olabilmem için:\n\n'
          '🔍 **Lütfen belirtin:**\n'
          '• Hangi semptomları yaşıyorsunuz?\n'
          '• Ne kadar süredir devam ediyor?\n'
          '• Şiddeti nasıl? (hafif/orta/şiddetli)\n'
          '• Başka belirtiler var mı?\n\n'
          '💡 **Örnek semptomlar:**\n'
          '• Baş ağrısı\n'
          '• Karın ağrısı\n'
          '• Ateş\n'
          '• Bulantı\n'
          '• Yorgunluk\n\n'
          '⚠️ **Önemli:** Bu analiz sadece genel bilgi amaçlıdır. Kesin teşhis için mutlaka bir doktora başvurun.';
    }
    
    // Eczane ile ilgili
    if (message.contains('eczane') || message.contains('ilaç') || message.contains('pharmacy')) {
      return 'Eczane ve ilaç konularında size yardımcı olabilirim! 💊\n\n'
          '🏥 **Eczane Hizmetleri:**\n'
          '• Yakınızdaki eczaneleri bulun\n'
          '• Nöbetçi eczaneleri görün\n'
          '• İlaç bilgileri alın\n'
          '• Reçete sorgulama\n\n'
          '📱 **Nasıl Kullanabilirsiniz:**\n'
          '• "Eczane bul" butonuna tıklayın\n'
          '• Konumunuzu paylaşın\n'
          '• En yakın eczaneleri görün\n\n'
          '💡 **İpucu:** Nöbetçi eczane için 114\'ü arayabilirsiniz.';
    }
    
    // Selamlama
    if (message.contains('merhaba') || message.contains('selam') || message.contains('hello') || message.contains('hi')) {
      return 'Merhaba! 👋 Ben TanıAI Asistanıyım.\n\n'
          '🏥 **Size nasıl yardımcı olabilirim?**\n\n'
          '📋 **Hizmetlerim:**\n'
          '• 🩺 Semptom analizi\n'
          '• 📅 Randevu alma\n'
          '• 💊 Eczane bulma\n'
          '• 🏥 Klinik önerisi\n'
          '• 📊 Sağlık bilgileri\n\n'
          '💬 **Sadece konuşarak başlayın:**\n'
          '"Başım ağrıyor" veya "Randevu almak istiyorum" gibi.';
    }
    
    // Teşekkür
    if (message.contains('teşekkür') || message.contains('sağol') || message.contains('thanks')) {
      return 'Rica ederim! 😊\n\n'
          'Size yardımcı olabildiğim için mutluyum. Sağlığınız için her zaman buradayım.\n\n'
          '💡 **Başka bir konuda yardıma ihtiyacınız olursa çekinmeden sorun!**';
    }
    
    // Veda
    if (message.contains('görüşürüz') || message.contains('bye') || message.contains('hoşça kal')) {
      return 'Hoşça kalın! 👋\n\n'
          'Sağlığınız için her zaman buradayım. İyi günler dilerim! 🌟\n\n'
          '💡 **Unutmayın:** Sağlık sorunlarınız için mutlaka doktora başvurun.';
    }
    
    // Genel yanıt - daha yardımcı
    return 'Anlıyorum. Size daha iyi yardımcı olabilmem için daha spesifik bilgi verebilir misiniz? 🤔\n\n'
        '💡 **Örnek sorular:**\n'
        '• "Başım ağrıyor"\n'
        '• "Randevu almak istiyorum"\n'
        '• "Yakınımdaki eczaneleri bul"\n'
        '• "Karın ağrım var"\n\n'
        '🏥 **Hizmetlerim:**\n'
        '• Semptom analizi\n'
        '• Randevu yönlendirmesi\n'
        '• Eczane bulma\n'
        '• Klinik önerisi';
  }
}
