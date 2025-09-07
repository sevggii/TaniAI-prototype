import 'package:flutter/material.dart';
import '../../services/auth_local_service.dart';
import '../../models/user.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = AuthLocalService();
    final user = auth.current;

    return Scaffold(
      appBar: AppBar(title: const Text('Profilim')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ListTile(
                  leading: const CircleAvatar(child: Icon(Icons.person)),
                  title: Text(user?.name ?? 'Kullanıcı'),
                  subtitle: Text(user?.email ?? ''),
                ),
                const Divider(),
                const SizedBox(height: 8),
                Text('E-posta: ${user?.email ?? '-'}'),
                const SizedBox(height: 8),
                Text('Telefon: ${user?.phone ?? '-'}'),
                const SizedBox(height: 8),
                Text('Kayıt tarihi: ${user?.createdAt.toString().split(' ')[0] ?? '-'}'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
