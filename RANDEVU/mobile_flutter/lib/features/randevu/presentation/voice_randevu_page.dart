import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

import 'package:tanial_randevu/features/randevu/data/triage_api_client.dart';

class VoiceRandevuPage extends StatefulWidget {
  const VoiceRandevuPage({super.key});

  @override
  State<VoiceRandevuPage> createState() => _VoiceRandevuPageState();
}

class _VoiceRandevuPageState extends State<VoiceRandevuPage> {
  final AudioRecorder _audioRecorder = AudioRecorder();
  final TextEditingController _complaintController = TextEditingController();
  final TriageApiClient _triageApiClient = TriageApiClient();
  bool _isRecording = false;
  bool _isProcessing = false;
  String? _transcript;
  List<Map<String, dynamic>> _suggestions = [];
  String? _errorMessage;
  List<String> _explanations = [];

  @override
  void dispose() {
    _audioRecorder.dispose();
    _complaintController.dispose();
    _triageApiClient.close();
    super.dispose();
  }

  Future<void> _startRecording() async {
    try {
      print('🎤 Ses kaydı başlatılıyor...');

      // Mikrofon izni kontrol et
      final status = await Permission.microphone.request();
      print('🎤 Mikrofon izni durumu: $status');

      if (status != PermissionStatus.granted) {
        _showError(
            'Mikrofon izni gerekli! Lütfen ayarlardan mikrofon iznini verin.');
        return;
      }

      // Basit ses kayıt ayarları
      final config = const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000,
        bitRate: 128000,
        numChannels: 1,
      );

      // Ses kaydını başlat
      if (kIsWeb) {
        await _audioRecorder.start(config,
            path: 'voice_randevu_${DateTime.now().millisecondsSinceEpoch}.wav');
        print('🌐 Web\'de ses kaydı başlatıldı');
      } else {
        await _audioRecorder.start(config, path: await _getRecordingPath());
        print('📱 Mobil\'de ses kaydı başlatıldı');
      }

      // 5 saniye sonra otomatik durdur
      Future.delayed(const Duration(seconds: 5), () {
        if (_isRecording) {
          _stopRecording();
        }
      });

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
      print('🛑 Ses kaydı durduruluyor...');
      final result = await _audioRecorder.stop();
      print('🛑 Kayıt sonucu: $result');

      if (result != null) {
        print('📁 Ses dosyası yolu: $result');
        await _processAudio(result as String);
      } else {
        _showError('Ses kaydı durdurulamadı veya boş. Lütfen tekrar deneyin.');
      }
      setState(() {
        _isRecording = false;
      });
    } catch (e) {
      print('❌ Kayıt durdurma hatası: $e');
      _showError('Kayıt durdurulamadı: $e');
    }
  }

  Future<String> _getRecordingPath() async {
    // Sadece mobil'de kullanılır
    final directory = await getTemporaryDirectory();
    return path.join(directory.path,
        'voice_randevu_${DateTime.now().millisecondsSinceEpoch}.wav');
  }

  Future<void> _processAudio(String audioPath) async {
    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      print('🔄 Ses dosyası işleniyor: $audioPath');

      // API'ye ses dosyasını gönder
      final result = await _uploadAudioToAPI(audioPath);
      print('📡 API yanıtı: $result');

      if (result['success'] == true) {
        final transcript = (result['transcript'] as String? ?? '').trim();
        print('📝 Transkript: $transcript');
        if (transcript.isEmpty) {
          _showError('Ses çözümlenemedi, lütfen tekrar deneyin.');
        } else {
          try {
            setState(() {
              _transcript = transcript;
            });
            final triageResult = await _requestTriage(transcript);
            _applyTriageResult(triageResult, transcript);
            print('✅ Triyaj tamamlandı!');
          } on TriageApiException catch (e) {
            print('❌ Triyaj hatası: $e');
            _showError(e.message);
          } catch (e) {
            print('❌ Beklenmeyen triyaj hatası: $e');
            _showError('Triyaj hatası: $e');
          }
        }
      } else {
        print('❌ Ses işleme hatası: ${result['message']}');
        _showError(result['message'] ?? 'Ses işleme hatası');
      }
    } catch (e) {
      print('❌ API hatası: $e');
      _showError('API hatası: $e');
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<Map<String, dynamic>> _uploadAudioToAPI(String audioPath) async {
    try {
      print('📤 API\'ye ses dosyası gönderiliyor...');

      // Web ve mobil için farklı URL'ler
      final apiUrl = kIsWeb
          ? 'http://localhost:8002/whisper/flutter-randevu'
          : 'https://unhung-cori-tartishly.ngrok-free.dev/whisper/flutter-randevu';

      print('🌐 API URL: $apiUrl');

      final request = http.MultipartRequest(
        'POST',
        Uri.parse(apiUrl),
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
              'message':
                  'Web\'de ses blob\'u alınamadı: ${response.statusCode}',
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

      print('📡 API yanıt durumu: ${response.statusCode}');
      print('📡 API yanıt içeriği: $responseBody');

      if (response.statusCode == 200) {
        final result = json.decode(responseBody);
        print('✅ API başarılı yanıt aldı');
        return result;
      } else {
        print('❌ API hatası: ${response.statusCode}');
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

  Future<TriageResult> _requestTriage(String text) {
    final endpoint = resolveTriageEndpoint();
    print('📬 Triyaj endpoint: $endpoint');
    return _triageApiClient.analyzeComplaint(
      endpoint: endpoint,
      text: text,
    );
  }

  void _applyTriageResult(TriageResult result, String text) {
    if (!mounted) {
      return;
    }
    final suggestions = _mapTriageResultToSuggestions(result);
    setState(() {
      _transcript = text;
      _suggestions = suggestions;
      _explanations = result.explanations;
      _errorMessage = null;
    });
  }

  List<Map<String, dynamic>> _mapTriageResultToSuggestions(
    TriageResult result,
  ) {
    final prioritized = List<TriageCandidate>.from(result.candidates);
    final alreadyHasChosen = prioritized.any(
      (candidate) => candidate.clinic == result.clinic,
    );
    if (prioritized.isEmpty && result.clinic.isNotEmpty) {
      prioritized.add(
        TriageCandidate(
          clinic: result.clinic,
          reason: 'Önerilen klinik.',
          confidence: 1.0,
        ),
      );
    } else if (!alreadyHasChosen && result.clinic.isNotEmpty) {
      prioritized.insert(
        0,
        TriageCandidate(
          clinic: result.clinic,
          reason: 'Önerilen klinik.',
          confidence: 1.0,
        ),
      );
    }

    prioritized.sort((a, b) {
      final aSelected = a.clinic == result.clinic;
      final bSelected = b.clinic == result.clinic;
      if (aSelected == bSelected) {
        return b.confidence.compareTo(a.confidence);
      }
      return aSelected ? -1 : 1;
    });

    final urgentMessage = result.redFlag
        ? (result.explanations.isNotEmpty
            ? result.explanations.first
            : 'Acil değerlendirme öneriliyor.')
        : null;

    return prioritized.map((candidate) {
      final isChosen = candidate.clinic == result.clinic;
      return {
        'clinic': candidate.clinic,
        'reason': candidate.reason,
        'confidence': candidate.confidence,
        'urgent': result.redFlag && isChosen,
        'message': result.redFlag && isChosen ? urgentMessage : null,
      };
    }).toList();
  }

  Future<void> _submitComplaint() async {
    final text = _complaintController.text.trim();
    if (text.isEmpty) {
      _showError('Lütfen şikayetinizi yazın.');
      return;
    }

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      final triageResult = await _requestTriage(text);
      _applyTriageResult(triageResult, text);
      print('✅ Yazılı triyaj tamamlandı!');
    } on TriageApiException catch (e) {
      print('❌ Triyaj API hatası: $e');
      _showError(e.message);
    } catch (e) {
      print('❌ Beklenmeyen triyaj hatası: $e');
      _showError('Triyaj hatası: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
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
      _explanations = [];
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
                          color: _isRecording
                              ? Colors.red
                              : theme.colorScheme.primary,
                          boxShadow: [
                            BoxShadow(
                              color: (_isRecording
                                      ? Colors.red
                                      : theme.colorScheme.primary)
                                  .withOpacity(0.3),
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
                      _isRecording
                          ? 'Kayıt devam ediyor...'
                          : 'Kayıt başlatmak için dokunun',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: _isRecording
                            ? Colors.red
                            : theme.colorScheme.onSurface.withOpacity(0.7),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Yazarak Deneyin',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Şikayet metnini girerek triyaj sonucunu anında alın.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurface.withOpacity(0.7),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _complaintController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: 'Şikayet metni',
                        border: OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                      textInputAction: TextInputAction.newline,
                    ),
                    const SizedBox(height: 12),
                    Align(
                      alignment: Alignment.centerRight,
                      child: ElevatedButton.icon(
                        onPressed: _isProcessing ? null : _submitComplaint,
                        icon: const Icon(Icons.send_rounded),
                        label: const Text('Triyaj Et'),
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

            if (_explanations.isNotEmpty) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'ℹ️ Açıklamalar',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 8),
                      ..._explanations.map(
                        (explanation) => Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Text(
                            '• $explanation',
                            style: theme.textTheme.bodyMedium,
                          ),
                        ),
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
                      backgroundColor:
                          isUrgent ? Colors.red : theme.colorScheme.primary,
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
                              color:
                                  theme.colorScheme.onSurface.withOpacity(0.7),
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
