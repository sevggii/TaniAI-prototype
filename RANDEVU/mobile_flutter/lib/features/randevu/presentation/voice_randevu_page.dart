import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:flutter/foundation.dart';

class VoiceRandevuPage extends StatefulWidget {
  const VoiceRandevuPage({super.key});

  @override
  State<VoiceRandevuPage> createState() => _VoiceRandevuPageState();
}

class _VoiceRandevuPageState extends State<VoiceRandevuPage> {
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isProcessing = false;
  String? _transcript;
  List<dynamic> _suggestions = [];
  String? _errorMessage;

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    try {
      // Mikrofon izni kontrol et
      final status = await Permission.microphone.request();
      if (status != PermissionStatus.granted) {
        _showError('Mikrofon izni gerekli!');
        return;
      }

      // Web için farklı kodlayıcı kullan - WAV formatı daha iyi transkripsiyon için
      final config = kIsWeb 
        ? const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 16000)
        : const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 16000);

      // Web'de basit path ile başlat
      if (kIsWeb) {
        await _audioRecorder.start(config, path: 'voice_randevu_${DateTime.now().millisecondsSinceEpoch}.wav');
      } else {
        await _audioRecorder.start(config, path: await _getRecordingPath());
      }
      
      setState(() {
        _isRecording = true;
        _errorMessage = null;
      });
    } catch (e) {
      _showError('Kayıt başlatılamadı: $e');
    }
  }

  Future<void> _stopRecording() async {
    try {
      final result = await _audioRecorder.stop();
      if (result != null) {
        if (kIsWeb) {
          // Web'de result String (blob URL) olarak gelir
          await _processAudio(result as String);
        } else {
          // Mobil'de dosya yolu olarak gelir
          await _processAudio(result as String);
        }
      } else {
        _showError('Ses kaydı durdurulamadı veya boş.');
      }
      setState(() {
        _isRecording = false;
      });
    } catch (e) {
      _showError('Kayıt durdurulamadı: $e');
    }
  }

  Future<String> _getRecordingPath() async {
    // Sadece mobil'de kullanılır
    final directory = await getTemporaryDirectory();
    return path.join(directory.path, 'voice_randevu_${DateTime.now().millisecondsSinceEpoch}.wav');
  }

  Future<void> _processAudio(String audioPath) async {
    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      // API'ye ses dosyasını gönder
      final result = await _uploadAudioToAPI(audioPath);
      
      if (result['success']) {
        setState(() {
          _transcript = result['transcript'];
          _suggestions = result['suggestions'];
        });
      } else {
        _showError(result['message'] ?? 'Ses işleme hatası');
      }
    } catch (e) {
      _showError('API hatası: $e');
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<Map<String, dynamic>> _uploadAudioToAPI(String audioPath) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('http://10.0.2.2:8002/whisper/flutter-randevu'),
      );

      if (kIsWeb) {
        // Web'de blob URL'den byte alıp yükle
        try {
          final response = await http.get(Uri.parse(audioPath));
          if (response.statusCode == 200) {
            request.files.add(
              http.MultipartFile.fromBytes(
                'audio_file',
                response.bodyBytes,
                filename: 'voice_randevu.wav',
              ),
            );
          } else {
            return {
              'success': false,
              'message': 'Web\'de ses blob\'u alınamadı: ${response.statusCode}',
            };
          }
        } catch (e) {
          return {
            'success': false,
            'message': 'Web blob hatası: $e',
          };
        }
      } else {
        // Mobil'de normal dosya yükleme
        final file = File(audioPath);
        request.files.add(
          await http.MultipartFile.fromPath(
            'audio_file',
            audioPath,
            filename: 'voice_randevu.wav',
          ),
        );
      }

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return json.decode(responseBody);
      } else {
        return {
          'success': false,
          'message': 'API Hatası: ${response.statusCode} - $responseBody',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Bağlantı hatası: $e',
      };
    }
  }

  void _showError(String message) {
    setState(() {
      _errorMessage = message;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  void _reset() {
    setState(() {
      _transcript = null;
      _suggestions = [];
      _errorMessage = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('🎤 Ses ile Randevu'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Ana kart
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    Icon(
                      Icons.mic_rounded,
                      size: 64,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Şikayetinizi Sesli Olarak Anlatın',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Mikrofon butonuna basarak şikayetinizi kaydedin, AI size en uygun kliniği önerecek.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withOpacity(0.7),
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    
                    // Kayıt butonu
                    GestureDetector(
                      onTap: _isRecording ? _stopRecording : _startRecording,
                      child: Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _isRecording ? Colors.red : theme.colorScheme.primary,
                          boxShadow: [
                            BoxShadow(
                              color: (_isRecording ? Colors.red : theme.colorScheme.primary).withOpacity(0.3),
                              blurRadius: 20,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: Icon(
                          _isRecording ? Icons.stop_rounded : Icons.mic_rounded,
                          color: Colors.white,
                          size: 48,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    Text(
                      _isRecording ? 'Kayıt devam ediyor...' : 'Kayıt başlatmak için dokunun',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: _isRecording ? Colors.red : theme.colorScheme.onSurface.withOpacity(0.7),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // İşleme durumu
            if (_isProcessing)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      const CircularProgressIndicator(),
                      const SizedBox(width: 16),
                      Text(
                        'Ses işleniyor...',
                        style: theme.textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),
            
            // Hata mesajı
            if (_errorMessage != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.error_rounded, color: Colors.red),
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
            
            // Transkript
            if (_transcript != null) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '📝 Anladığım:',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _transcript!,
                        style: theme.textTheme.bodyLarge,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],
            
            // Öneriler
            if (_suggestions.isNotEmpty) ...[
              Text(
                '🏥 Önerilen Klinikler:',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              ..._suggestions.asMap().entries.map((entry) {
                final index = entry.key;
                final suggestion = entry.value;
                final isUrgent = suggestion['urgent'] == true;
                
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  color: isUrgent ? Colors.red.shade50 : null,
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: isUrgent ? Colors.red : theme.colorScheme.primary,
                      child: Text(
                        '${index + 1}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    title: Text(
                      suggestion['clinic'],
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: isUrgent ? Colors.red.shade700 : null,
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(suggestion['reason']),
                        if (suggestion['confidence'] != null)
                          Text(
                            'Güven: ${(suggestion['confidence'] * 100).toStringAsFixed(0)}%',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurface.withOpacity(0.7),
                            ),
                          ),
                        if (isUrgent && suggestion['message'] != null)
                          Text(
                            suggestion['message'],
                            style: TextStyle(
                              color: Colors.red.shade700,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                      ],
                    ),
                    trailing: isUrgent 
                        ? const Icon(Icons.warning_rounded, color: Colors.red)
                        : const Icon(Icons.arrow_forward_ios_rounded),
                  ),
                );
              }).toList(),
              
              const SizedBox(height: 16),
              
              // Yeniden deneme butonu
              ElevatedButton.icon(
                onPressed: _reset,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('Yeniden Dene'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
