import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'type_booking_page.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  Future<void> _startCall(BuildContext context) async {
    final uri = Uri(scheme: 'tel', path: '182');
    final can = await canLaunchUrl(uri);
    if (can) {
      await launchUrl(uri);
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Arama başlatılamadı.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Randevu')),
      body: SafeArea(
        child: Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 8),
                Semantics(
                  label: 'TanıAI Randevu, Hızlı ve kolay randevu',
                  header: true,
                  child: Column(
                    children: [
                      Icon(Icons.local_hospital_rounded,
                          size: 72, color: theme.colorScheme.primary),
                      const SizedBox(height: 16),
                      Text(
                        'Hızlı ve kolay randevu',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                Semantics(
                  button: true,
                  label: 'Ara ile randevu al',
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.call),
                    onPressed: () => _startCall(context),
                    style: ElevatedButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                    ),
                    label: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('Ara ile Randevu'),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Semantics(
                  button: true,
                  label: 'Yazarak randevu al',
                  child: FilledButton.tonalIcon(
                    icon: const Icon(Icons.chat),
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const TypeBookingPage(),
                        ),
                      );
                    },
                    style: FilledButton.styleFrom(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                    ),
                    label: const Padding(
                      padding: EdgeInsets.symmetric(vertical: 8.0),
                      child: Text('Yazarak Randevu'),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
