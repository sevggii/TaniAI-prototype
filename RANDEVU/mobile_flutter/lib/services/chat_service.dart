import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/chat_message.dart';
import '../models/user_health_profile.dart';
import 'llm_service.dart';
import 'chat_cache_service.dart';

class ChatService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final String _collectionName = 'chat_messages';
  final ChatCacheService _cacheService = ChatCacheService();
  String? _currentSessionId;

  // Yeni oturum başlat
  String startNewSession() {
    _currentSessionId = DateTime.now().millisecondsSinceEpoch.toString();
    return _currentSessionId!;
  }

  // Mevcut oturum ID'sini al
  String getCurrentSessionId() {
    _currentSessionId ??= DateTime.now().millisecondsSinceEpoch.toString();
    return _currentSessionId!;
  }

  // Mesaj gönder
  Future<void> sendMessage(
    String text,
    String senderId,
    String senderName, {
    bool isAI = false,
    String? sessionId,
  }) async {
    final message = ChatMessage(
      id: '', // Firestore otomatik ID oluşturacak
      text: text,
      senderId: senderId,
      senderName: senderName,
      timestamp: DateTime.now(),
      isAI: isAI,
      sessionId: sessionId ?? getCurrentSessionId(),
    );

    await _firestore.collection(_collectionName).add(message.toFirestore());
  }

  // Sadece bugünün mesajlarını getir
  Stream<QuerySnapshot> getTodayMessages() {
    final today = DateTime.now();
    final startOfDay = DateTime(today.year, today.month, today.day);
    
    return _firestore
        .collection(_collectionName)
        .where('timestamp', isGreaterThanOrEqualTo: Timestamp.fromDate(startOfDay))
        .orderBy('timestamp', descending: false)
        .snapshots();
  }

  // Tüm mesajları getir
  Stream<QuerySnapshot> getMessages() {
    return _firestore
        .collection(_collectionName)
        .orderBy('timestamp', descending: false)
        .snapshots();
  }

  // Belirli bir oturumun mesajlarını getir
  Stream<QuerySnapshot> getSessionMessages(String sessionId) {
    return _firestore
        .collection(_collectionName)
        .where('sessionId', isEqualTo: sessionId)
        .orderBy('timestamp', descending: false)
        .snapshots();
  }

  // Kullanıcının geçmiş konuşmalarını al (son 10 mesaj)
  Future<List<ChatMessage>> getUserHistory(String userId) async {
    try {
      // Index gerektirmeyen basit sorgu - sadece userId ile filtrele
      final snapshot = await _firestore
          .collection(_collectionName)
          .where('senderId', isEqualTo: userId)
          .limit(50) // Daha fazla al, sonra client-side sırala
          .get();
      
      // Client-side'da timestamp'e göre sırala ve son 10'u al
      final messages = snapshot.docs
          .map((doc) => ChatMessage.fromFirestore(doc))
          .toList();
      
      messages.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      return messages.take(10).toList();
    } catch (e) {
      print('Error getting user history: $e');
      return []; // Hata olursa boş liste dön
    }
  }

  // Kullanıcı sağlık profilini al
  Future<UserHealthProfile?> getUserHealthProfile(String userId) async {
    try {
      final doc = await _firestore
          .collection('user_health_profiles')
          .doc(userId)
          .get();
      
      if (doc.exists) {
        return UserHealthProfile.fromFirestore(doc);
      }
      return null;
    } catch (e) {
      print('Error getting health profile: $e');
      return null;
    }
  }

  // AI yanıtı al (HIZLI - cache ile)
  Future<String> getAIResponse(String userMessage, {String? userId}) async {
    try {
      // 1. Önce hızlı yanıtları kontrol et (anında!)
      final quickResponse = _cacheService.getQuickResponse(userMessage);
      if (quickResponse != null) {
        print('⚡ Hızlı yanıt kullanıldı!');
        return quickResponse;
      }

      // 2. Cache'de var mı kontrol et (çok hızlı!)
      final cachedResponse = await _cacheService.getCachedResponse(userMessage);
      if (cachedResponse != null) {
        print('💨 Cache\'den yanıt alındı!');
        return cachedResponse;
      }

      // 3. Bağlam bilgilerini hazırla (paralel olarak)
      String context = '';
      
      if (userId != null) {
        // Paralel olarak profil ve geçmişi al
        final results = await Future.wait([
          getUserHealthProfile(userId),
          getUserHistory(userId),
        ]);
        
        final profile = results[0] as UserHealthProfile?;
        final history = results[1] as List<ChatMessage>;
        
        // Profil bilgisi
        if (profile != null) {
          final profileSummary = profile.getSummary();
          if (profileSummary.isNotEmpty) {
            context += '\n\nKullanıcı Profili:\n$profileSummary';
          }
        }
        
        // Son kullanıcı mesajını ekle (SADECE 1 tane, çok doğal!)
        if (history.isNotEmpty) {
          // Sadece son kullanıcı mesajını bul
          for (var msg in history.reversed) {
            if (!msg.isAI && msg.text.length < 50) {
              // Önceki mesaj: "Başım ağrıyor"
              // Şimdiki mesaj: "geçmiyooo"
              // AI'ya git: "Kullanıcı önce 'Başım ağrıyor' dedi, şimdi: [şimdiki mesaj]"
              context = '\n\nÖnceki mesaj: "${msg.text}"';
              break;
            }
          }
        }
      }
      
      // 4. LLM'den yanıt al
      final fullMessage = context.isEmpty ? userMessage : '$userMessage$context';
      final response = await LLMService.getChatResponse(fullMessage);
      
      // 5. Yanıtı cache'e kaydet (gelecek için)
      await _cacheService.cacheResponse(userMessage, response);
      
      return response;
    } catch (e) {
      print('Chat Service Error: $e');
      return 'Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.';
    }
  }

  // Triyaj yanıtı al
  Future<Map<String, dynamic>> getTriageResponse(String symptoms) async {
    try {
      final response = await LLMService.getTriageResponse(symptoms);
      return response;
    } catch (e) {
      print('Triage Service Error: $e');
      return {
        'success': false,
        'error': 'Triyaj servisi şu anda kullanılamıyor.',
      };
    }
  }

  // Klinik önerisi al
  Future<Map<String, dynamic>> getClinicRecommendation(String symptoms) async {
    try {
      final response = await LLMService.getClinicRecommendation(symptoms);
      return response;
    } catch (e) {
      print('Clinic Recommendation Service Error: $e');
      return {
        'success': false,
        'error': 'Klinik önerisi servisi şu anda kullanılamıyor.',
      };
    }
  }

  // Sohbeti temizle (sadece bugünün mesajlarını)
  Future<void> clearTodayChat() async {
    final today = DateTime.now();
    final startOfDay = DateTime(today.year, today.month, today.day);
    
    final batch = _firestore.batch();
    final messages = await _firestore
        .collection(_collectionName)
        .where('timestamp', isGreaterThanOrEqualTo: Timestamp.fromDate(startOfDay))
        .get();
    
    for (final doc in messages.docs) {
      batch.delete(doc.reference);
    }
    
    await batch.commit();
    
    // Yeni oturum başlat
    startNewSession();
  }

  // Tüm sohbeti temizle
  Future<void> clearAllChat() async {
    final batch = _firestore.batch();
    final messages = await _firestore.collection(_collectionName).get();
    
    for (final doc in messages.docs) {
      batch.delete(doc.reference);
    }
    
    await batch.commit();
    
    // Yeni oturum başlat
    startNewSession();
  }

  // AI yanıtları oluştur
  String _generateAIResponse(String userMessage) {
    final message = userMessage.toLowerCase();
    
    // Randevu ile ilgili
    if (message.contains('randevu') || message.contains('appointment')) {
      return 'Randevu almak için size yardımcı olabilirim! Hangi bölüm için randevu almak istiyorsunuz? Ayrıca sesli randevu almak için telefon özelliğini de kullanabilirsiniz.';
    }
    
    // Semptom ile ilgili
    if (message.contains('semptom') || message.contains('hasta') || message.contains('ağrı')) {
      return 'Semptomlarınız hakkında konuşabiliriz, ancak lütfen unutmayın ki bu sadece genel bilgi amaçlıdır. Kesin teşhis için mutlaka bir doktora başvurmanızı öneririm. Hangi semptomları yaşıyorsunuz?';
    }
    
    // Eczane ile ilgili
    if (message.contains('eczane') || message.contains('ilaç') || message.contains('pharmacy')) {
      return 'Yakınızdaki eczaneleri bulmak için eczane bulma özelliğini kullanabilirsiniz. Ayrıca nöbetçi eczaneleri de görebilirsiniz. Size yardımcı olmak için başka bir şey var mı?';
    }
    
    // Sağlık ile ilgili genel
    if (message.contains('sağlık') || message.contains('health') || message.contains('doktor')) {
      return 'Sağlığınız için buradayım! Randevu alma, semptom sorgulama, eczane bulma gibi konularda size yardımcı olabilirim. Ayrıca radyolojik görüntü analizi ve ilaç takibi özelliklerimiz de mevcut.';
    }
    
    // Radyoloji ile ilgili
    if (message.contains('radyoloji') || message.contains('görüntü') || message.contains('x-ray')) {
      return 'Radyolojik görüntü analizi özelliğimiz mevcut! X-ray, MRI, CT gibi görüntülerinizi yükleyerek AI destekli analiz alabilirsiniz. Bu özellik sadece yardımcı amaçlıdır ve doktor teşhisinin yerini tutmaz.';
    }
    
    // İlaç takibi ile ilgili
    if (message.contains('ilaç takibi') || message.contains('medication')) {
      return 'İlaç takibi özelliğimiz ile ilaçlarınızı düzenli olarak takip edebilir, hatırlatıcılar kurabilirsiniz. Bu sayede ilaçlarınızı zamanında almayı unutmazsınız.';
    }
    
    // Selamlama
    if (message.contains('merhaba') || message.contains('selam') || message.contains('hello') || message.contains('hi')) {
      return 'Merhaba! Ben TanıAI Asistanıyım. Size nasıl yardımcı olabilirim? Randevu alma, semptom sorgulama, eczane bulma gibi konularda size rehberlik edebilirim.';
    }
    
    // Teşekkür
    if (message.contains('teşekkür') || message.contains('sağol') || message.contains('thanks')) {
      return 'Rica ederim! Size yardımcı olabildiğim için mutluyum. Başka bir konuda yardıma ihtiyacınız olursa çekinmeden sorun.';
    }
    
    // Veda
    if (message.contains('görüşürüz') || message.contains('bye') || message.contains('hoşça kal')) {
      return 'Hoşça kalın! Sağlığınız için her zaman buradayım. İyi günler dilerim!';
    }
    
    // Genel yanıt
    return 'Anlıyorum. Size daha iyi yardımcı olabilmem için daha spesifik bir soru sorabilir misiniz? Randevu alma, semptom sorgulama, eczane bulma gibi konularda size rehberlik edebilirim.';
  }
}
