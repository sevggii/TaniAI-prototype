import 'package:flutter/material.dart';

class TypeBookingPage extends StatefulWidget {
  const TypeBookingPage({super.key});

  @override
  State<TypeBookingPage> createState() => _TypeBookingPageState();
}

class _TypeBookingPageState extends State<TypeBookingPage> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _submit() {
    FocusScope.of(context).unfocus();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Mesaj alındı.')),
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
                    decoration: const InputDecoration(
                      labelText: 'Mesajınız',
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Semantics(
                  button: true,
                  label: 'Devam',
                  child: ElevatedButton(
                    onPressed: _submit,
                    child: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12.0),
                      child: Text('Devam'),
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
