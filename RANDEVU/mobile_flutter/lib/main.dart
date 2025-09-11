import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/splash_auth_gate.dart';
import 'services/firebase_auth_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  
  // Clean up expired soft deleted accounts
  final authService = FirebaseAuthService();
  await authService.cleanupExpiredAccounts();
  
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
