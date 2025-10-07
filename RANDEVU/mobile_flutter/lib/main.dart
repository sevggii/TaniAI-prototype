import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'firebase_options.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/splash_auth_gate.dart';
import 'services/firebase_auth_service.dart';
import 'services/notification_service.dart';
import 'services/firebase_messaging_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  try {
    // Initialize Firebase
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    print('🔥 Firebase initialized successfully');
    
    // Clean up expired soft deleted accounts
    final authService = FirebaseAuthService();
    await authService.cleanupExpiredAccounts();
    print('🧹 Account cleanup completed');
    
    // Initialize notification service
    await NotificationService.initialize();
    print('🔔 Notification service initialized');
    
    // Initialize Firebase Messaging
    await FirebaseMessagingService.initialize();
    print('📱 Firebase Messaging initialized');
    
    // Set background message handler
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
    
    // Request notification permissions
    final hasPermission = await NotificationService.requestNotificationPermissions();
    print('📱 Notification permission granted: $hasPermission');
    
    if (hasPermission) {
      print('✅ Notification permissions granted');
    } else {
      print('⚠️ Notification permissions not granted - notifications will not work');
    }
    
  } catch (e) {
    print('❌ Error during initialization: $e');
  }
  
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