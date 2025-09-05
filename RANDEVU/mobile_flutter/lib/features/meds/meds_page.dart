import 'package:flutter/material.dart';

class MedsPage extends StatelessWidget {
  const MedsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('İlaç Takibi (yakında)')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text('Yakında: İlaç listesi ve hatırlatmalar'),
                SizedBox(height: 8),
                Text('Not: hatırlatmalar için SMS/Push entegrasyonu eklenecek'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
