import 'dart:math';

class AIPersonalityService {
  static final AIPersonalityService _instance = AIPersonalityService._internal();
  factory AIPersonalityService() => _instance;
  AIPersonalityService._internal();

  final Random _random = Random();
  
  // AI kişiliği özellikleri
  final List<String> _greetings = [
    "Merhaba! 👋 Ben TanıAI Asistanınızım. Size nasıl yardımcı olabilirim?",
    "Selam! 😊 Sağlığınızla ilgili sorularınızı yanıtlamaya hazırım.",
    "Hoş geldiniz! 🏥 Bugün nasıl hissediyorsunuz?",
    "Merhaba! 🌟 Sağlık konularında size yardımcı olmak için buradayım.",
  ];

  final List<String> _encouragingPhrases = [
    "Harika! 👍",
    "Mükemmel! ✨",
    "Çok iyi! 🌟",
    "Harika bir soru! 💡",
    "Anlıyorum! 🤔",
  ];

  final List<String> _empathyPhrases = [
    "Anlıyorum, bu durum sizi endişelendiriyor olabilir. 😔",
    "Bu durumun sizi zorladığını biliyorum. 💙",
    "Endişelenmeyin, size yardımcı olmaya çalışacağım. 🤗",
    "Bu konuda yalnız değilsiniz. 💪",
  ];

  final List<String> _closingPhrases = [
    "Başka bir sorunuz var mı? 😊",
    "Size başka nasıl yardımcı olabilirim? 🤔",
    "Başka bir konuda yardıma ihtiyacınız olursa çekinmeden sorun! 💬",
    "Sağlığınız için her zaman buradayım! 🏥",
  ];

  /// Kişiselleştirilmiş selamlama
  String getPersonalizedGreeting() {
    return _greetings[_random.nextInt(_greetings.length)];
  }

  /// Cesaretlendirici ifade
  String getEncouragingPhrase() {
    return _encouragingPhrases[_random.nextInt(_encouragingPhrases.length)];
  }

  /// Empati ifadesi
  String getEmpathyPhrase() {
    return _empathyPhrases[_random.nextInt(_empathyPhrases.length)];
  }

  /// Kapanış ifadesi
  String getClosingPhrase() {
    return _closingPhrases[_random.nextInt(_closingPhrases.length)];
  }

  /// AI yanıtını kişiselleştir
  String personalizeResponse(String baseResponse, String userMessage) {
    String personalizedResponse = baseResponse;
    
    // Kullanıcı mesajının tonunu analiz et
    final messageTone = _analyzeMessageTone(userMessage);
    
    // Tonuna göre kişiselleştir
    switch (messageTone) {
      case MessageTone.urgent:
        personalizedResponse = "🚨 " + personalizedResponse;
        break;
      case MessageTone.worried:
        personalizedResponse = getEmpathyPhrase() + "\n\n" + personalizedResponse;
        break;
      case MessageTone.casual:
        personalizedResponse = getEncouragingPhrase() + " " + personalizedResponse;
        break;
      case MessageTone.grateful:
        personalizedResponse = personalizedResponse + "\n\n" + "Rica ederim! 😊 " + getClosingPhrase();
        break;
      default:
        break;
    }

    // Emoji ekle
    personalizedResponse = _addRelevantEmojis(personalizedResponse, userMessage);
    
    return personalizedResponse;
  }

  /// Mesaj tonunu analiz et
  MessageTone _analyzeMessageTone(String message) {
    final lowerMessage = message.toLowerCase();
    
    // Acil durum kelimeleri
    if (lowerMessage.contains('acil') || 
        lowerMessage.contains('hemen') || 
        lowerMessage.contains('şiddetli') ||
        lowerMessage.contains('korkuyorum')) {
      return MessageTone.urgent;
    }
    
    // Endişeli ton
    if (lowerMessage.contains('endişe') || 
        lowerMessage.contains('korku') || 
        lowerMessage.contains('stres') ||
        lowerMessage.contains('kaygı')) {
      return MessageTone.worried;
    }
    
    // Teşekkür
    if (lowerMessage.contains('teşekkür') || 
        lowerMessage.contains('sağol') || 
        lowerMessage.contains('thanks')) {
      return MessageTone.grateful;
    }
    
    // Normal konuşma
    return MessageTone.casual;
  }

  /// İlgili emoji'leri ekle
  String _addRelevantEmojis(String response, String userMessage) {
    final lowerMessage = userMessage.toLowerCase();
    
    // Baş ağrısı
    if (lowerMessage.contains('baş') && lowerMessage.contains('ağrı')) {
      return response.replaceAll('Baş ağrı', '🤕 Baş ağrı');
    }
    
    // Karın ağrısı
    if (lowerMessage.contains('karın') && lowerMessage.contains('ağrı')) {
      return response.replaceAll('Karın ağrı', '🤢 Karın ağrı');
    }
    
    // Göğüs ağrısı
    if (lowerMessage.contains('göğüs') && lowerMessage.contains('ağrı')) {
      return response.replaceAll('Göğüs ağrı', '💔 Göğüs ağrı');
    }
    
    // Randevu
    if (lowerMessage.contains('randevu') || lowerMessage.contains('doktor')) {
      return response.replaceAll('Randevu', '📅 Randevu');
    }
    
    // Eczane
    if (lowerMessage.contains('eczane') || lowerMessage.contains('ilaç')) {
      return response.replaceAll('Eczane', '💊 Eczane');
    }
    
    // Ateş
    if (lowerMessage.contains('ateş') || lowerMessage.contains('fever')) {
      return response.replaceAll('Ateş', '🌡️ Ateş');
    }
    
    return response;
  }

  /// Konuşma geçmişine göre kişiselleştir
  String personalizeWithHistory(String response, List<String> conversationHistory) {
    // Son 3 mesajı analiz et
    final recentMessages = conversationHistory.take(3).toList();
    
    // Tekrarlanan konuları tespit et
    final commonTopics = _findCommonTopics(recentMessages);
    
    if (commonTopics.isNotEmpty) {
      final topic = commonTopics.first;
      return _addContextualResponse(response, topic);
    }
    
    return response;
  }

  /// Ortak konuları bul
  List<String> _findCommonTopics(List<String> messages) {
    final topics = <String>[];
    
    for (final message in messages) {
      final lowerMessage = message.toLowerCase();
      
      if (lowerMessage.contains('baş ağrı')) topics.add('baş_ağrı');
      if (lowerMessage.contains('karın ağrı')) topics.add('karın_ağrı');
      if (lowerMessage.contains('randevu')) topics.add('randevu');
      if (lowerMessage.contains('eczane')) topics.add('eczane');
    }
    
    // En çok tekrarlanan konuyu bul
    final topicCount = <String, int>{};
    for (final topic in topics) {
      topicCount[topic] = (topicCount[topic] ?? 0) + 1;
    }
    
    if (topicCount.isNotEmpty) {
      final sortedTopics = topicCount.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      return [sortedTopics.first.key];
    }
    
    return [];
  }

  /// Bağlamsal yanıt ekle
  String _addContextualResponse(String response, String topic) {
    switch (topic) {
      case 'baş_ağrı':
        return response + "\n\n💡 **Hatırlatma:** Baş ağrınız devam ederse mutlaka doktora başvurun.";
      case 'karın_ağrı':
        return response + "\n\n💡 **Hatırlatma:** Karın ağrınız şiddetlenirse acil servise gidin.";
      case 'randevu':
        return response + "\n\n📞 **İpucu:** Randevu almak için sesli komut da kullanabilirsiniz!";
      case 'eczane':
        return response + "\n\n🏥 **İpucu:** Nöbetçi eczane için 114'ü arayabilirsiniz.";
      default:
        return response;
    }
  }
}

enum MessageTone {
  urgent,
  worried,
  casual,
  grateful,
}
