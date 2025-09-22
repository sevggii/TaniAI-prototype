import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../services/firebase_auth_service.dart';
import '../../models/user.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final FirebaseAuthService _auth = FirebaseAuthService();
  UserModel? _user;
  User? _firebaseUser;

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    _firebaseUser = FirebaseAuth.instance.currentUser;
    if (_firebaseUser != null) {
      final userData = await _auth.getUserData(_firebaseUser!.uid);
      if (mounted) setState(() => _user = userData);
    }
  }

  @override
  Widget build(BuildContext context) {
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
                  title: Text(_user?.name ?? _firebaseUser?.displayName ?? 'Kullanıcı'),
                  subtitle: Text(_user?.email ?? _firebaseUser?.email ?? ''),
                ),
                const Divider(),
                const SizedBox(height: 8),
                Text('E-posta: ${_user?.email ?? _firebaseUser?.email ?? '-'}'),
                const SizedBox(height: 8),
                Text('Kayıt tarihi: ${_user?.createdAt.toString().split(' ')[0] ?? '-'}'),
                const SizedBox(height: 8),
                Text('Kullanıcı ID: ${_firebaseUser?.uid ?? '-'}'),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
