import 'dart:math';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../../core/theme/app_theme.dart';
import '../../models/chat_message.dart';
import '../../services/chat_service.dart';
import '../../services/voice_service.dart';
import '../../services/ai_personality_service.dart';

class ChatPage extends StatefulWidget {
  final String? initialMessage;
  
  const ChatPage({super.key, this.initialMessage});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final FocusNode _messageFocusNode = FocusNode(); // Klavye kontrolü için
  final ChatService _chatService = ChatService();
  final VoiceService _voiceService = VoiceService();
  final AIPersonalityService _personalityService = AIPersonalityService();
  
  late AnimationController _animationController;
  late AnimationController _typingAnimationController;
  late AnimationController _voiceAnimationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _typingAnimation;
  late Animation<double> _voiceAnimation;
  
  User? _currentUser;
  bool _isTyping = false;
  bool _isVoiceEnabled = false;
  List<String> _conversationHistory = [];

  @override
  void initState() {
    super.initState();
    _currentUser = FirebaseAuth.instance.currentUser;
    _setupAnimations();
    _initializeVoiceService();
    _scrollToBottom();
    
    // Eğer initial message varsa, otomatik gönder
    if (widget.initialMessage != null && widget.initialMessage!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _messageController.text = widget.initialMessage!;
        _sendMessage();
      });
    }
  }

  void _setupAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _typingAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _voiceAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOutCubic,
    ));
    
    _typingAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _typingAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _voiceAnimation = Tween<double>(
      begin: 0.8,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _voiceAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _animationController.forward();
  }

  Future<void> _initializeVoiceService() async {
    final success = await _voiceService.initialize();
    if (success) {
      setState(() {
        _isVoiceEnabled = true;
      });
      
      // Voice service callbacks
      _voiceService.onSpeechResult = (text) {
        _messageController.text = text;
        _sendMessage();
      };
      
      _voiceService.onSpeechError = (error) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ses tanıma hatası: $error')),
        );
      };
      
      _voiceService.onTtsCompleted = () {
        setState(() {});
      };
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _messageFocusNode.dispose(); // FocusNode'u temizle
    _animationController.dispose();
    _typingAnimationController.dispose();
    _voiceAnimationController.dispose();
    _voiceService.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    final message = _messageController.text.trim();
    _messageController.clear();
    
    // Klavyeyi kapat (önemli!)
    _messageFocusNode.unfocus();

    // Konuşma geçmişine ekle
    _conversationHistory.add(message);

    // Kullanıcı mesajını gönder
    await _chatService.sendMessage(
      message,
      _currentUser!.uid,
      _currentUser!.displayName ?? 'Kullanıcı',
    );

    // AI yanıtı için typing göstergesi
    setState(() {
      _isTyping = true;
    });
    
    // Typing animasyonunu başlat
    _typingAnimationController.repeat(reverse: true);

    try {
      // Mesaj tipine göre farklı işlemler yap (TIMEOUT ile)
      String aiResponse;
      
      final responseFuture = _getAIResponseByType(message);
      aiResponse = await responseFuture.timeout(
        const Duration(seconds: 10),
        onTimeout: () {
          return 'Yanıt vermem biraz uzun sürdü. Daha basit bir şekilde sorar mısınız? 😊';
        },
      );
      
      // AI yanıtını kişiselleştir (DEVRE DIŞI - Türkçe karakter sorunu)
      // aiResponse = _personalityService.personalizeResponse(aiResponse, message);
      // aiResponse = _personalityService.personalizeWithHistory(aiResponse, _conversationHistory);
      
      setState(() {
        _isTyping = false;
      });
      
      // Typing animasyonunu durdur
      _typingAnimationController.stop();
      _typingAnimationController.reset();

      // Streaming ile AI yanıtını göster (ChatGPT tarzı)
      await _streamAIResponse(aiResponse);

      // Konuşma geçmişine AI yanıtını ekle
      _conversationHistory.add(aiResponse);

      // AI yanıtını sesli olarak oku
      if (_isVoiceEnabled) {
        await _voiceService.speak(aiResponse);
      }

      // _scrollToBottom() artık StreamBuilder'da otomatik yapılıyor
    } catch (e) {
      print('Mesaj gönderme hatası: $e');
      setState(() {
        _isTyping = false;
      });
      _typingAnimationController.stop();
      _typingAnimationController.reset();
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bir hata oluştu, lütfen tekrar deneyin')),
      );
    }
  }

  // Mesaj tipine göre AI yanıtı al
  Future<String> _getAIResponseByType(String message) async {
    // Basit çözüm: Sadece son mesajı gönder, gerisini backend halleder
    return await _chatService.getAIResponse(message, userId: _currentUser?.uid);
  }

  // Randevu isteği mi kontrol et
  bool _isAppointmentRequest(String message) {
    final lowerMessage = message.toLowerCase();
    return lowerMessage.contains('randevu') || 
           lowerMessage.contains('appointment') ||
           lowerMessage.contains('doktor') ||
           lowerMessage.contains('muayene');
  }

  // Yeni konuşma başlat
  Future<void> _startNewConversation() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Yeni Konuşma'),
        content: const Text('Yeni bir konuşma başlatmak istediğinizden emin misiniz? Mevcut konuşma geçmişte kalacak.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Başlat'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      _chatService.startNewSession();
      _conversationHistory.clear();
      setState(() {});
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✨ Yeni konuşma başlatıldı!'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  // ChatGPT tarzı streaming yanıt (karakter karakter yazma)
  Future<void> _streamAIResponse(String fullResponse) async {
    // Direkt tam yanıtı Firebase'e kaydet (streaming sadece görsel olacak)
    await _chatService.sendMessage(
      fullResponse,
      'ai_assistant',
      'TanıAI Asistanı',
      isAI: true,
    );
  }

  // Sesli giriş başlat/durdur
  Future<void> _toggleVoiceInput() async {
    if (!_isVoiceEnabled) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ses servisi kullanılamıyor')),
      );
      return;
    }

    if (_voiceService.isListening) {
      await _voiceService.stopListening();
      _voiceAnimationController.stop();
    } else {
      await _voiceService.startListening();
      _voiceAnimationController.repeat(reverse: true);
    }
  }

  // AI yanıtını sesli olarak oku/durdur
  Future<void> _toggleVoiceOutput() async {
    if (!_isVoiceEnabled) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ses servisi kullanılamıyor')),
      );
      return;
    }

    if (_voiceService.isSpeaking) {
      await _voiceService.stopSpeaking();
    } else {
      // Son AI mesajını bul ve oku
      // Bu basit bir implementasyon, gerçek uygulamada daha gelişmiş olabilir
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Son mesajı okumak için önce bir mesaj gönderin')),
      );
    }
  }

  // Semptom sorgusu mu kontrol et
  bool _isSymptomQuery(String message) {
    final lowerMessage = message.toLowerCase();
    return lowerMessage.contains('semptom') ||
           lowerMessage.contains('ağrı') ||
           lowerMessage.contains('hasta') ||
           lowerMessage.contains('rahatsızlık') ||
           lowerMessage.contains('şikayet');
  }

  // Randevu isteğini işle
  Future<String> _handleAppointmentRequest(String message) async {
    try {
      // Triyaj yaparak uygun klinik önerisi al
      final triageResponse = await _chatService.getTriageResponse(message);
      
      if (triageResponse['success']) {
        final data = triageResponse['data'];
        final urgency = data['urgency'] ?? 'normal';
        final recommendedClinic = data['recommended_clinic'] ?? 'Genel Pratisyen';
        
        String response = 'Randevu talebinizi aldım. ';
        
        if (urgency == 'high') {
          response += '⚠️ Acil durum tespit ettim. En kısa sürede bir sağlık kuruluşuna başvurmanızı öneririm. ';
        } else if (urgency == 'medium') {
          response += '🟡 Orta öncelikli bir durum. 24-48 saat içinde randevu almanızı öneririm. ';
        } else {
          response += '✅ Normal öncelikli durum. Uygun bir zamanda randevu alabilirsiniz. ';
        }
        
        response += 'Önerilen bölüm: **$recommendedClinic**\n\n';
        response += 'Randevu almak için aşağıdaki seçenekleri kullanabilirsiniz:\n';
        response += '• 📞 Sesli randevu (telefon)\n';
        response += '• 🏥 Yakın hastaneler\n';
        response += '• 📅 Online randevu sistemi';
        
        return response;
      } else {
        // Fallback yanıt
        return 'Randevu almak için size yardımcı olabilirim! Hangi bölüm için randevu almak istiyorsunuz? Ayrıca sesli randevu almak için telefon özelliğini de kullanabilirsiniz.';
      }
    } catch (e) {
      return 'Randevu almak için size yardımcı olabilirim! Hangi bölüm için randevu almak istiyorsunuz? Ayrıca sesli randevu almak için telefon özelliğini de kullanabilirsiniz.';
    }
  }

  // Semptom sorgusunu işle
  Future<String> _handleSymptomQuery(String message) async {
    try {
      // Triyaj yaparak semptom analizi al
      final triageResponse = await _chatService.getTriageResponse(message);
      
      if (triageResponse['success']) {
        final data = triageResponse['data'];
        final urgency = data['urgency'] ?? 'normal';
        final analysis = data['analysis'] ?? '';
        final recommendations = data['recommendations'] ?? [];
        final recommendedClinic = data['recommended_clinic'] ?? 'Genel Pratisyen';
        
        String response = 'Semptomlarınızı analiz ettim: 🩺\n\n';
        
        if (analysis.isNotEmpty) {
          response += '📋 **Analiz:** $analysis\n\n';
        }
        
        if (urgency == 'high') {
          response += '🚨 **Acil Durum:** Bu semptomlar acil müdahale gerektirebilir. En kısa sürede bir sağlık kuruluşuna başvurun.\n\n';
          response += '📞 **Hemen Yapılacaklar:**\n';
          response += '• 112\'yi arayın (gerekirse)\n';
          response += '• Acil servise gidin\n';
          response += '• Yanınızda birisi olsun\n\n';
        } else if (urgency == 'medium') {
          response += '⚠️ **Orta Öncelik:** Bu semptomlar dikkat gerektiriyor. 24-48 saat içinde bir doktora başvurmanızı öneririm.\n\n';
        } else {
          response += '✅ **Normal Öncelik:** Bu semptomlar genellikle ciddi değildir, ancak takip edilmesi gerekebilir.\n\n';
        }
        
        response += '🏥 **Önerilen Bölüm:** $recommendedClinic\n\n';
        
        if (recommendations.isNotEmpty) {
          response += '💡 **Öneriler:**\n';
          for (var rec in recommendations) {
            response += '• $rec\n';
          }
          response += '\n';
        }
        
        response += '📅 **Randevu Seçenekleri:**\n';
        response += '• 📞 Sesli randevu (telefon)\n';
        response += '• 🏥 Yakın hastaneler\n';
        response += '• 📱 Online randevu sistemi\n\n';
        
        response += '⚠️ **Önemli:** Bu analiz sadece genel bilgi amaçlıdır. Kesin teşhis için mutlaka bir doktora başvurun.';
        
        return response;
      } else {
        // Fallback yanıt - daha akıllı
        return _getSmartFallbackResponse(message);
      }
    } catch (e) {
      return _getSmartFallbackResponse(message);
    }
  }

  // Akıllı fallback yanıtı
  String _getSmartFallbackResponse(String message) {
    final lowerMessage = message.toLowerCase();
    
    if (lowerMessage.contains('baş') && lowerMessage.contains('ağrı')) {
      return 'Baş ağrınız için size yardımcı olabilirim. 🧠\n\n'
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
          '🏥 **Önerilen Bölüm:** Nöroloji veya İç Hastalıkları\n\n'
          '⚠️ **Dikkat:** Şiddetli, ani başlayan veya sürekli baş ağrıları için mutlaka doktora başvurun.';
    }
    
    if (lowerMessage.contains('karın') && lowerMessage.contains('ağrı')) {
      return 'Karın ağrınız için size yardımcı olabilirim. 🫄\n\n'
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
          '🏥 **Önerilen Bölüm:** Gastroenteroloji veya İç Hastalıkları\n\n'
          '⚠️ **Dikkat:** Şiddetli, ani başlayan veya sürekli karın ağrıları için mutlaka doktora başvurun.';
    }
    
    if (lowerMessage.contains('göğüs') && lowerMessage.contains('ağrı')) {
      return '🚨 **ACİL DURUM!**\n\n'
          'Göğüs ağrısı ciddi bir durum olabilir. Hemen aşağıdaki adımları takip edin:\n\n'
          '📞 **Hemen Yapılacaklar:**\n'
          '• 112\'yi arayın\n'
          '• Acil servise gidin\n'
          '• Yanınızda birisi olsun\n'
          '• Dinlenin, hareket etmeyin\n\n'
          '🏥 **Önerilen Bölüm:** Acil Servis veya Kardiyoloji\n\n'
          '⚠️ **Göğüs ağrısı kalp krizi belirtisi olabilir. Zaman kaybetmeyin!**';
    }
    
    // Genel semptom yanıtı
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
        '🏥 **Randevu için:** "Randevu almak istiyorum" yazabilirsiniz.\n\n'
        '⚠️ **Önemli:** Bu analiz sadece genel bilgi amaçlıdır. Kesin teşhis için mutlaka bir doktora başvurun.';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return GestureDetector(
      onTap: () {
        // Ekrana tıklandığında klavyeyi kapat
        _messageFocusNode.unfocus();
      },
      child: Scaffold(
        extendBodyBehindAppBar: true,
        appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF667eea), Color(0xFF764ba2)],
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF667eea).withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(
                Icons.smart_toy_rounded,
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'TanıAI Asistanı',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                      fontSize: 18,
                    ),
                  ),
                  Row(
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: Colors.green,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        'Çevrimiçi',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: Colors.green,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          // Yeni konuşma başlat butonu
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: const Icon(Icons.add_comment_rounded),
              tooltip: 'Yeni Konuşma',
              onPressed: () {
                _startNewConversation();
              },
            ),
          ),
          // Menü butonu
          Container(
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: IconButton(
              icon: const Icon(Icons.more_vert_rounded),
              onPressed: () {
                _showChatOptions(context);
              },
            ),
          ),
        ],
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              const Color(0xFF667eea).withOpacity(0.1),
              const Color(0xFF764ba2).withOpacity(0.05),
              const Color(0xFFf093fb).withOpacity(0.03),
              Colors.white,
            ],
            stops: const [0.0, 0.3, 0.7, 1.0],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Chat mesajları
              Expanded(
                child: StreamBuilder<QuerySnapshot>(
                  stream: _chatService.getTodayMessages(),
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return _buildLoadingState(theme);
                    }

                    if (snapshot.hasError) {
                      return _buildErrorState(theme, snapshot.error.toString());
                    }

                    final messages = snapshot.data?.docs
                        .map((doc) => ChatMessage.fromFirestore(doc))
                        .toList() ?? [];

                    if (messages.isEmpty) {
                      return _buildEmptyState(theme);
                    }

                    // Mesajları TERS çevir - en yeni mesaj EN ALTTA olsun
                    final reversedMessages = messages.reversed.toList();

                    return FadeTransition(
                      opacity: _fadeAnimation,
                      child: SlideTransition(
                        position: _slideAnimation,
                        child: ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.all(16),
                          reverse: true, // EN ALTTA başlat (WhatsApp gibi!)
                          physics: const ClampingScrollPhysics(),
                          itemCount: reversedMessages.length + (_isTyping ? 1 : 0),
                          itemBuilder: (context, index) {
                            // Typing indicator en ÜSTTE (reverse=true olduğu için)
                            if (index == 0 && _isTyping) {
                              return _buildTypingIndicator(theme);
                            }
                            
                            // Typing varsa index'i 1 azalt
                            final messageIndex = _isTyping ? index - 1 : index;
                            final message = reversedMessages[messageIndex];
                            return _buildMessageBubble(context, theme, message);
                          },
                        ),
                      ),
                    );
                  },
                ),
              ),
              
              // Mesaj gönderme alanı
              _buildMessageInput(theme),
            ],
          ),
        ),
      ),
      ), // GestureDetector kapanışı
    );
  }

  Widget _buildLoadingState(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.smart_toy_rounded,
              color: Colors.white,
              size: 40,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'TanıAI Asistanı hazırlanıyor...',
            style: theme.textTheme.titleMedium?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(ThemeData theme, String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline_rounded,
            size: 64,
            color: theme.colorScheme.error,
          ),
          const SizedBox(height: 16),
          Text(
            'Bir hata oluştu',
            style: theme.textTheme.titleLarge?.copyWith(
              color: theme.colorScheme.error,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(ThemeData theme) {
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // AI Avatar ve hoş geldin
            Container(
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(32),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryGradient.colors[0].withOpacity(0.3),
                    blurRadius: 30,
                    offset: const Offset(0, 15),
                  ),
                ],
              ),
              child: const Icon(
                Icons.smart_toy_rounded,
                color: Colors.white,
                size: 64,
              ),
            ),
            const SizedBox(height: 32),
            Text(
              'Merhaba! 👋',
              style: theme.textTheme.headlineLarge?.copyWith(
                fontWeight: FontWeight.w800,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Ben TanıAI Asistanıyım',
              style: theme.textTheme.titleLarge?.copyWith(
                color: AppTheme.primaryGradient.colors[0],
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: Colors.grey[200]!,
                  width: 1,
                ),
              ),
              child: Text(
                'Sağlık konularında size yardımcı olmak için buradayım. Randevu alma, semptom sorgulama ve genel sağlık bilgileri konularında rehberlik edebilirim.',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: Colors.grey[700],
                  height: 1.5,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            const SizedBox(height: 32),
            _buildQuickActions(theme),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActions(ThemeData theme) {
    final quickActions = [
      {
        'title': 'Randevu Al',
        'subtitle': 'Hızlı randevu alma',
        'icon': Icons.event_rounded,
        'message': 'Randevu almak istiyorum',
        'gradient': const LinearGradient(
          colors: [Color(0xFF34C759), Color(0xFF30D158)],
        ),
      },
      {
        'title': 'Semptom Sorgula',
        'subtitle': 'Sağlık durumu analizi',
        'icon': Icons.medical_information_rounded,
        'message': 'Semptomlarım hakkında bilgi almak istiyorum',
        'gradient': const LinearGradient(
          colors: [Color(0xFFFF3B30), Color(0xFFFF6B6B)],
        ),
      },
      {
        'title': 'Eczane Bul',
        'subtitle': 'Yakın eczaneler',
        'icon': Icons.local_pharmacy_rounded,
        'message': 'Yakınımdaki eczaneleri bul',
        'gradient': const LinearGradient(
          colors: [Color(0xFF007AFF), Color(0xFF5AC8FA)],
        ),
      },
    ];

    return Column(
      children: quickActions.map((action) {
        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () {
                _messageController.text = action['message'] as String;
                _sendMessage();
              },
              borderRadius: BorderRadius.circular(16),
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: action['gradient'] as LinearGradient,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: (action['gradient'] as LinearGradient).colors[0].withOpacity(0.3),
                      blurRadius: 12,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: Icon(
                        action['icon'] as IconData,
                        color: Colors.white,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            action['title'] as String,
                            style: theme.textTheme.titleMedium?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            action['subtitle'] as String,
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: Colors.white.withOpacity(0.9),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(
                        Icons.arrow_forward_ios_rounded,
                        color: Colors.white,
                        size: 16,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildMessageBubble(BuildContext context, ThemeData theme, ChatMessage message) {
    final isMe = message.senderId == _currentUser?.uid;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isMe) ...[
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Icon(
                Icons.smart_toy_rounded,
                color: Colors.white,
                size: 18,
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.75,
              ),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: isMe 
                  ? AppTheme.primaryGradient
                  : LinearGradient(
                      colors: [
                        theme.colorScheme.surface,
                        theme.colorScheme.surface,
                      ],
                    ),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(isMe ? 20 : 4),
                  bottomRight: Radius.circular(isMe ? 4 : 20),
                ),
                boxShadow: [
                  BoxShadow(
                    color: (isMe 
                      ? AppTheme.primaryGradient.colors[0] 
                      : Colors.black).withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (!isMe)
                    Text(
                      message.senderName,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface.withOpacity(0.7),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  if (!isMe) const SizedBox(height: 4),
                  Text(
                    message.text,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: isMe ? Colors.white : theme.colorScheme.onSurface,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _formatTime(message.timestamp),
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: isMe 
                            ? Colors.white.withOpacity(0.7)
                            : theme.colorScheme.onSurface.withOpacity(0.5),
                        ),
                      ),
                      // AI mesajları için sesli okuma butonu
                      if (!isMe && _isVoiceEnabled)
                        GestureDetector(
                          onTap: () => _voiceService.speak(message.text),
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              _voiceService.isSpeaking ? Icons.volume_up : Icons.volume_up_outlined,
                              size: 16,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          if (isMe) ...[
            const SizedBox(width: 8),
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(
                Icons.person_rounded,
                color: theme.colorScheme.primary,
                size: 18,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTypingIndicator(ThemeData theme) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.smart_toy_rounded,
              color: Colors.white,
              size: 18,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  theme.colorScheme.surface,
                  theme.colorScheme.surface.withOpacity(0.8),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: theme.colorScheme.primary.withOpacity(0.1),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                AnimatedBuilder(
                  animation: _typingAnimation,
                  builder: (context, child) {
                    return Row(
                      children: [
                        _buildTypingDot(theme, 0),
                        const SizedBox(width: 4),
                        _buildTypingDot(theme, 1),
                        const SizedBox(width: 4),
                        _buildTypingDot(theme, 2),
                      ],
                    );
                  },
                ),
                const SizedBox(width: 12),
                Text(
                  'TanıAI düşünüyor...',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.7),
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingDot(ThemeData theme, int index) {
    final delay = index * 0.2;
    final animationValue = (_typingAnimation.value - delay).clamp(0.0, 1.0);
    final opacity = (sin(animationValue * pi * 2) + 1) / 2;
    
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withOpacity(opacity),
        borderRadius: BorderRadius.circular(4),
      ),
    );
  }

  Widget _buildMessageInput(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                    color: theme.colorScheme.outline.withOpacity(0.2),
                  ),
                ),
                child: TextField(
                  controller: _messageController,
                  focusNode: _messageFocusNode, // Klavye kontrolü
                  autofocus: false, // Otomatik focus KAPALI
                  decoration: InputDecoration(
                    hintText: 'Mesajınızı yazın...',
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                    hintStyle: theme.textTheme.bodyLarge?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                    ),
                  ),
                  style: theme.textTheme.bodyLarge,
                  maxLines: null,
                  textCapitalization: TextCapitalization.sentences,
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // Sesli giriş butonu
            if (_isVoiceEnabled) ...[
              AnimatedBuilder(
                animation: _voiceAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _voiceService.isListening ? _voiceAnimation.value : 1.0,
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: _voiceService.isListening 
                            ? LinearGradient(
                                colors: [Colors.red.shade400, Colors.red.shade600],
                              )
                            : LinearGradient(
                                colors: [Colors.blue.shade400, Colors.blue.shade600],
                              ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: (_voiceService.isListening ? Colors.red : Colors.blue)
                                .withOpacity(0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Material(
                        color: Colors.transparent,
                        child: InkWell(
                          onTap: _toggleVoiceInput,
                          borderRadius: BorderRadius.circular(20),
                          child: Container(
                            padding: const EdgeInsets.all(12),
                            child: Icon(
                              _voiceService.isListening 
                                  ? Icons.mic_rounded 
                                  : Icons.mic_none_rounded,
                              color: Colors.white,
                              size: 20,
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(width: 8),
            ],
            // Gönder butonu
            Container(
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryGradient.colors[0].withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: _sendMessage,
                  borderRadius: BorderRadius.circular(24),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    child: const Icon(
                      Icons.send_rounded,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showChatOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: const Icon(Icons.delete_outline_rounded),
              title: const Text('Sohbeti Temizle'),
              onTap: () {
                Navigator.pop(context);
                _showClearChatDialog(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.info_outline_rounded),
              title: const Text('Hakkında'),
              onTap: () {
                Navigator.pop(context);
                _showAboutDialog(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showClearChatDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sohbeti Temizle'),
        content: const Text('Tüm mesajları silmek istediğinizden emin misiniz?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () async {
              await _chatService.clearTodayChat();
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Bugünün sohbeti temizlendi')),
              );
            },
            child: const Text('Bugünü Temizle'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('TanıAI Asistanı'),
        content: const Text(
          'TanıAI Asistanı, sağlık konularında size yardımcı olmak için tasarlanmış yapay zeka destekli bir sohbet asistanıdır. Randevu alma, semptom sorgulama ve genel sağlık bilgileri konularında size rehberlik edebilir.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inDays > 0) {
      return '${difference.inDays} gün önce';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} saat önce';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} dakika önce';
    } else {
      return 'Az önce';
    }
  }
}
