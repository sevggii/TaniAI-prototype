import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/splash_auth_gate.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const TanialRandevuApp());
}

class TanialRandevuApp extends StatelessWidget {
  const TanialRandevuApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TanıAI Randevu',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: ThemeMode.system,
      home: const SplashAuthGate(),
    );
  }
}
