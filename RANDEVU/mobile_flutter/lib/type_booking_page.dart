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
              // LLM Server'a istek gönder (klinik_dataset.jsonl kullanıyor)
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
        final data = responseData['analysis']; // API response'u 'analysis' objesi içinde
        _showClinicRecommendations(data);
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

  void _showClinicRecommendations(Map<String, dynamic> data) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Klinik Önerileri'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (data['primary_clinic'] != null) ...[
                const Text(
                  'Ana Öneri:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                _buildClinicCard(
                  data['primary_clinic']['name'],
                  data['primary_clinic']['reason'],
                  data['primary_clinic']['confidence'],
                  isPrimary: true,
                ),
                const SizedBox(height: 16),
              ],
              if (data['secondary_clinics'] != null) ...[
                const Text(
                  'Alternatif Öneriler:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...data['secondary_clinics'].map<Widget>((clinic) => 
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: _buildClinicCard(
                      clinic['name'],
                      clinic['reason'],
                      clinic['confidence'],
                    ),
                  ),
                ),
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
