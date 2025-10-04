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
        Uri.parse('http://10.0.2.2:8000/analyze-complaint'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'complaint': _controller.text.trim(),
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
    final analysisData = rawData['analysis'];
    Map<String, dynamic> clinicData = {};

    if (analysisData is Map<String, dynamic> && analysisData.containsKey('primary_clinic')) {
      clinicData = analysisData;
    } else if (rawData.containsKey('primary_clinic')) {
      clinicData = rawData;
    } else if (rawData['suggestions'] is List && (rawData['suggestions'] as List).isNotEmpty) {
      final suggestions = (rawData['suggestions'] as List)
          .whereType<Map<String, dynamic>>()
          .toList();
      if (suggestions.isNotEmpty) {
        clinicData = {
          'primary_clinic': suggestions.first,
          'secondary_clinics': suggestions.skip(1).toList(),
        };
      }
    }

    final primaryClinic = clinicData['primary_clinic'] as Map<String, dynamic>?;
    final secondaryClinics = (clinicData['secondary_clinics'] as List?)
            ?.whereType<Map<String, dynamic>>()
            .toList() ??
        const [];

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

  Widget _buildClinicCard(String name, String reason, double confidence, {bool isPrimary = false}) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isPrimary ? Colors.blue.shade50 : Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isPrimary ? Colors.blue.shade200 : Colors.grey.shade300,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            name,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: isPrimary ? Colors.blue.shade800 : Colors.grey.shade800,
            ),
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
