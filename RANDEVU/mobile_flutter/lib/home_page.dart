import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'type_booking_page.dart';
import 'services/auth_local_service.dart';
import 'models/user.dart';
import 'features/profile/profile_page.dart';
import 'features/radiology/radiology_page.dart';
import 'features/meds/meds_page.dart';
import 'features/settings/settings_page.dart';
import 'features/auth/login_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final AuthLocalService _auth = AuthLocalService();
  User? _user;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final u = await _auth.getUser();
    if (mounted) setState(() => _user = u);
  }

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
      drawer: Drawer(
        child: ListView(
          children: [
            UserAccountsDrawerHeader(
              accountName: Text(_user?.name ?? 'Kullanıcı'),
              accountEmail: Text(_user?.email ?? ''),
              currentAccountPicture:
                  const CircleAvatar(child: Icon(Icons.person)),
            ),
            ListTile(
              leading: const Icon(Icons.person),
              title: const Text('Profilim'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const ProfilePage()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.medical_information),
              title: const Text('Radyolojik Görüntü (beta)'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const RadiologyPage()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.medication),
              title: const Text('İlaç Takibi (yakında)'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context)
                    .push(MaterialPageRoute(builder: (_) => const MedsPage()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Ayarlar'),
              onTap: () {
                Navigator.of(context).pop();
                Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const SettingsPage()));
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Çıkış Yap'),
              onTap: () async {
                await _auth.logout();
                if (!mounted) return;
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginPage()),
                  (route) => false,
                );
              },
            ),
          ],
        ),
      ),
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
