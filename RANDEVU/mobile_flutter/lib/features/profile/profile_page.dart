import 'package:flutter/material.dart';
import '../../services/auth_local_service.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = AuthLocalService();
    return Scaffold(
      appBar: AppBar(title: const Text('Profilim')),
      body: FutureBuilder(
        future: auth.getUser(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final user = snapshot.data;
          return Padding(
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
                    Text('Telefon: ${user?.phone ?? '-'}'),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
