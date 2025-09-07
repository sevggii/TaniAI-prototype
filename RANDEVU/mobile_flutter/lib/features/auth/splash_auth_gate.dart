import 'package:flutter/material.dart';
import '../../home_page.dart';
import 'login_page.dart';

class SplashAuthGate extends StatefulWidget {
  const SplashAuthGate({super.key});

  @override
  State<SplashAuthGate> createState() => _SplashAuthGateState();
}

class _SplashAuthGateState extends State<SplashAuthGate> {
  @override
  void initState() {
    super.initState();
    _checkAuthState();
  }

  void _checkAuthState() {
    // Navigate directly to login page
    Future.delayed(const Duration(milliseconds: 500), () {
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginPage()),
      );
    });

    // TODO: Uncomment when Firebase is properly configured
    // FirebaseAuth.instance.authStateChanges().listen((User? user) {
    //   if (!mounted) return;

    //   if (user != null) {
    //     // User is signed in
    //     Navigator.of(context).pushReplacement(
    //       MaterialPageRoute(builder: (_) => const HomePage()),
    //     );
    //   } else {
    //     // User is signed out
    //     Navigator.of(context).pushReplacement(
    //       MaterialPageRoute(builder: (_) => const LoginPage()),
    //     );
    //   }
    // });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.local_hospital_rounded,
                size: 72, color: theme.colorScheme.primary),
            const SizedBox(height: 16),
            const CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
