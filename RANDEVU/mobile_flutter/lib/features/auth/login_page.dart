import 'package:flutter/material.dart';
import '../../models/user_role.dart';
import '../../widgets/login_form.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Giriş Yap'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(
              icon: const Icon(Icons.person),
              text: UserRole.patient.displayName,
            ),
            Tab(
              icon: const Icon(Icons.medical_services),
              text: UserRole.doctor.displayName,
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Compact header with logo
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              child: Icon(
                Icons.local_hospital_rounded,
                size: 36,
                color: theme.colorScheme.primary,
              ),
            ),

            // Tab content - takes remaining space
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Card(
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: TabBarView(
                      controller: _tabController,
                      children: [
                        // Patient login form
                        LoginForm(role: UserRole.patient),
                        // Doctor login form
                        LoginForm(role: UserRole.doctor),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
