import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TypeBookingPage extends StatefulWidget {
  const TypeBookingPage({super.key});

  @override
  State<TypeBookingPage> createState() => _TypeBookingPageState();
}

class _TypeBookingPageState extends State<TypeBookingPage> {
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_controller.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lütfen belirtilerinizi yazın.')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    FocusScope.of(context).unfocus();

    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:8000/triage'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'text': _controller.text.trim(),
        }),
      );

      if (response.statusCode == 200) {
        final responseData = json.decode(response.body);
        _showClinicRecommendations(responseData);
      } else {
        throw Exception('API hatası: ${response.statusCode}');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Hata: ${e.toString()}')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showClinicRecommendations(Map<String, dynamic> rawData) {
    // Yeni API format: {"clinic": "acil servis", "candidates": [...], "red_flag": true}
    final primaryClinicName = rawData['clinic'] as String?;
    final candidates = (rawData['candidates'] as List?)
            ?.whereType<Map<String, dynamic>>()
            .toList() ??
        const [];
    final redFlag = rawData['red_flag'] as bool? ?? false;
    final explanations = (rawData['explanations'] as List?)
            ?.whereType<String>()
            .toList() ??
        const [];

    if (primaryClinicName == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Klinik önerisi alınamadı. Lütfen tekrar deneyin.')),
      );
      return;
    }

    // Primary clinic'i formatla
    final primaryClinic = {
      'name': primaryClinicName,
      'reason': explanations.isNotEmpty ? explanations.first : 'LLM önerisi',
      'confidence': candidates.isNotEmpty ? candidates.first['confidence'] ?? 0.8 : 0.8,
    };

    // Secondary clinics'i formatla
    final secondaryClinics = candidates
        .skip(1)
        .map((candidate) => {
              'name': candidate['clinic'] ?? '',
              'reason': candidate['reason'] ?? '',
              'confidence': candidate['confidence'] ?? 0.5,
            })
        .toList();

    if (primaryClinic == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Klinik önerisi alınamadı. Lütfen tekrar deneyin.')),
      );
      return;
    }

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Klinik Önerileri'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Ana Öneri:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _buildClinicCard(
                primaryClinic['name']?.toString() ?? 'Bilinmiyor',
                primaryClinic['reason']?.toString() ?? 'Açıklama mevcut değil',
                _asDouble(primaryClinic['confidence']),
                isPrimary: true,
                isRedFlag: redFlag,
              ),
              const SizedBox(height: 16),
              if (secondaryClinics.isNotEmpty) ...[
                const Text(
                  'Alternatif Öneriler:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...secondaryClinics.map((clinic) => Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: _buildClinicCard(
                        clinic['name']?.toString() ?? 'Bilinmiyor',
                        clinic['reason']?.toString() ?? 'Açıklama mevcut değil',
                        _asDouble(clinic['confidence']),
                      ),
                    )),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  double _asDouble(dynamic value) {
    if (value is num) return value.toDouble();
    return double.tryParse(value?.toString() ?? '') ?? 0.0;
  }

  Widget _buildClinicCard(String name, String reason, double confidence, {bool isPrimary = false, bool isRedFlag = false}) {
    Color cardColor = isPrimary ? Colors.blue.shade50 : Colors.grey.shade50;
    Color borderColor = isPrimary ? Colors.blue.shade200 : Colors.grey.shade300;
    
    if (isRedFlag) {
      cardColor = Colors.red.shade50;
      borderColor = Colors.red.shade300;
    }
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: borderColor,
          width: isRedFlag ? 2 : 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  name,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isPrimary ? Colors.blue.shade800 : Colors.grey.shade800,
                  ),
                ),
              ),
              if (isRedFlag)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.red.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'ACİL',
                    style: TextStyle(
                      color: Colors.red.shade800,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            reason,
            style: TextStyle(
              color: Colors.grey.shade700,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Güven: ${(confidence * 100).toStringAsFixed(0)}%',
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Yazarak Randevu')),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 24),
                Text(
                  'Belirtilerinizi veya talebinizi yazın.',
                  style: theme.textTheme.titleMedium,
                  textAlign: TextAlign.start,
                ),
                const SizedBox(height: 16),
                Semantics(
                  label: 'Mesajınızı yazın',
                  textField: true,
                  child: TextField(
                    controller: _controller,
                    minLines: 4,
                    maxLines: 8,
                    textInputAction: TextInputAction.newline,
                    textCapitalization: TextCapitalization.none,
                    keyboardType: TextInputType.multiline,
                    enableSuggestions: true,
                    autocorrect: true,
                    decoration: const InputDecoration(
                      labelText: 'Mesajınız',
                      hintText: 'Örnek: başım ağrıyor, mide bulantım var...',
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Semantics(
                  button: true,
                  label: 'Devam',
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _submit,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 12.0),
                      child: _isLoading
                          ? const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                ),
                                SizedBox(width: 8),
                                Text('Analiz ediliyor...'),
                              ],
                            )
                          : const Text('Klinik Önerisi Al'),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
