import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/chat_message.dart';

class ChatService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final String _collectionName = 'chat_messages';

  // Mesaj gönder
  Future<void> sendMessage(
    String text,
    String senderId,
    String senderName, {
    bool isAI = false,
  }) async {
    final message = ChatMessage(
      id: '', // Firestore otomatik ID oluşturacak
      text: text,
      senderId: senderId,
      senderName: senderName,
      timestamp: DateTime.now(),
      isAI: isAI,
    );

    await _firestore.collection(_collectionName).add(message.toFirestore());
  }

  // Mesajları getir
  Stream<QuerySnapshot> getMessages() {
    return _firestore
        .collection(_collectionName)
        .orderBy('timestamp', descending: false)
        .snapshots();
  }

  // AI yanıtı al
  Future<String> getAIResponse(String userMessage) async {
    try {
      // Gerçek AI servisi yerine simüle edilmiş yanıtlar
      await Future.delayed(const Duration(seconds: 2)); // Gerçekçi gecikme
      
      return _generateAIResponse(userMessage);
    } catch (e) {
      return 'Üzgünüm, şu anda bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.';
    }
  }

  // Sohbeti temizle
  Future<void> clearChat() async {
    final batch = _firestore.batch();
    final messages = await _firestore.collection(_collectionName).get();
    
    for (final doc in messages.docs) {
      batch.delete(doc.reference);
    }
    
    await batch.commit();
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
