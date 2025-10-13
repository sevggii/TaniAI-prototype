import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';

class VoiceService {
  static final VoiceService _instance = VoiceService._internal();
  factory VoiceService() => _instance;
  VoiceService._internal();

  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  
  bool _isListening = false;
  bool _isSpeaking = false;
  bool _isInitialized = false;
  
  // Callbacks
  Function(String)? onSpeechResult;
  Function(String)? onSpeechError;
  Function()? onSpeechStarted;
  Function()? onSpeechEnded;
  Function()? onTtsStarted;
  Function()? onTtsCompleted;

  bool get isListening => _isListening;
  bool get isSpeaking => _isSpeaking;
  bool get isInitialized => _isInitialized;

  /// Ses servislerini başlat
  Future<bool> initialize() async {
    try {
      // Mikrofon izni kontrol et
      final micPermission = await Permission.microphone.request();
      if (micPermission != PermissionStatus.granted) {
        print('❌ Mikrofon izni verilmedi');
        return false;
      }

      // Speech to Text'i başlat
      final speechAvailable = await _speechToText.initialize(
        onError: (error) {
          print('🎤 Speech to Text Error: $error');
          onSpeechError?.call(error.errorMsg);
        },
        onStatus: (status) {
          print('🎤 Speech Status: $status');
          if (status == 'listening') {
            _isListening = true;
            onSpeechStarted?.call();
          } else if (status == 'notListening') {
            _isListening = false;
            onSpeechEnded?.call();
          }
        },
      );

      if (!speechAvailable) {
        print('❌ Speech to Text kullanılamıyor');
        return false;
      }

      // Text to Speech'i başlat
      await _flutterTts.setLanguage("tr-TR");
      await _flutterTts.setSpeechRate(0.5);
      await _flutterTts.setVolume(1.0);
      await _flutterTts.setPitch(1.0);

      _flutterTts.setStartHandler(() {
        _isSpeaking = true;
        onTtsStarted?.call();
      });

      _flutterTts.setCompletionHandler(() {
        _isSpeaking = false;
        onTtsCompleted?.call();
      });

      _flutterTts.setErrorHandler((msg) {
        _isSpeaking = false;
        print('🔊 TTS Error: $msg');
      });

      _isInitialized = true;
      print('✅ Voice Service başlatıldı');
      return true;
    } catch (e) {
      print('❌ Voice Service başlatma hatası: $e');
      return false;
    }
  }

  /// Konuşmayı dinlemeye başla
  Future<void> startListening() async {
    if (!_isInitialized) {
      print('❌ Voice Service başlatılmamış');
      return;
    }

    if (_isListening) {
      print('⚠️ Zaten dinleniyor');
      return;
    }

    try {
      await _speechToText.listen(
        onResult: (result) {
          final recognizedText = result.recognizedWords;
          print('🎤 Tanınan metin: $recognizedText');
          onSpeechResult?.call(recognizedText);
        },
        listenFor: const Duration(seconds: 30),
        pauseFor: const Duration(seconds: 3),
        partialResults: true,
        localeId: "tr_TR",
        onSoundLevelChange: (level) {
          // Ses seviyesi değişikliği (animasyon için)
        },
      );
    } catch (e) {
      print('❌ Dinleme başlatma hatası: $e');
      onSpeechError?.call('Dinleme başlatılamadı: $e');
    }
  }

  /// Konuşmayı dinlemeyi durdur
  Future<void> stopListening() async {
    if (_isListening) {
      await _speechToText.stop();
      _isListening = false;
    }
  }

  /// Metni sesli olarak oku
  Future<void> speak(String text) async {
    if (!_isInitialized) {
      print('❌ Voice Service başlatılmamış');
      return;
    }

    if (_isSpeaking) {
      await stopSpeaking();
    }

    try {
      // Metni temizle ve optimize et
      final cleanText = _cleanTextForSpeech(text);
      
      await _flutterTts.speak(cleanText);
      print('🔊 Konuşma başlatıldı: $cleanText');
    } catch (e) {
      print('❌ Konuşma hatası: $e');
    }
  }

  /// Konuşmayı durdur
  Future<void> stopSpeaking() async {
    if (_isSpeaking) {
      await _flutterTts.stop();
      _isSpeaking = false;
    }
  }

  /// Metni konuşma için temizle
  String _cleanTextForSpeech(String text) {
    String cleanText = text;
    
    // Markdown formatlarını kaldır (ama Türkçe karakterleri koru!)
    cleanText = cleanText.replaceAll(RegExp(r'\*\*(.*?)\*\*'), r'$1');
    cleanText = cleanText.replaceAll(RegExp(r'\*(.*?)\*'), r'$1');
    cleanText = cleanText.replaceAll(RegExp(r'`(.*?)`'), r'$1');
    
    // Sadece emoji'leri kaldır (Türkçe karakterleri koruyarak)
    cleanText = cleanText.replaceAll(RegExp(r'[\u{1F300}-\u{1F9FF}]', unicode: true), '');
    cleanText = cleanText.replaceAll(RegExp(r'[\u{2600}-\u{26FF}]', unicode: true), '');
    cleanText = cleanText.replaceAll(RegExp(r'[\u{2700}-\u{27BF}]', unicode: true), '');
    
    // Çoklu boşlukları tek boşluğa çevir
    cleanText = cleanText.replaceAll(RegExp(r'\s+'), ' ');
    
    // Noktalama işaretlerini düzenle
    cleanText = cleanText.replaceAll('...', '.');
    cleanText = cleanText.replaceAll('..', '.');
    
    return cleanText.trim();
  }

  /// Servisi temizle
  void dispose() {
    _speechToText.cancel();
    _flutterTts.stop();
    _isListening = false;
    _isSpeaking = false;
    _isInitialized = false;
  }
}
