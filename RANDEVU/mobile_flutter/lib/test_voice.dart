import 'package:flutter/material.dart';
import 'features/randevu/presentation/voice_randevu_page.dart';

void main() {
  runApp(const TestVoiceApp());
}

class TestVoiceApp extends StatelessWidget {
  const TestVoiceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ses Test',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const VoiceRandevuPage(),
    );
  }
}
