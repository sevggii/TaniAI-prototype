import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../services/auth_local_service.dart';
import '../../services/hash.dart';
import '../../home_page.dart';
import 'register_page.dart';

class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordPageState();
}

class _ForgotPasswordPageState extends State<ForgotPasswordPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _answerController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _newPasswordAgainController = TextEditingController();

  bool _obscure1 = true;
  bool _obscure2 = true;
  final _auth = AuthLocalService();

  int _currentStep = 1;
  String _recoveryQuestion = '';
  String _userEmail = '';

  @override
  void dispose() {
    _emailController.dispose();
    _answerController.dispose();
    _newPasswordController.dispose();
    _newPasswordAgainController.dispose();
    super.dispose();
  }

  String? _validateEmail(String? value) {
    final v = value?.trim() ?? '';
    if (v.isEmpty) return 'E-posta gerekli';
    final regex = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!regex.hasMatch(v)) return 'Geçerli bir e-posta girin';
    return null;
  }

  String? _validatePassword(String? value) {
    final v = value ?? '';
    if (v.isEmpty) return 'Şifre gerekli';
    if (v.length < 6) return 'Şifre en az 6 karakter olmalı';
    return null;
  }

  Future<void> _verifyEmail() async {
    if (!_formKey.currentState!.validate()) return;

    final email = _emailController.text.trim();
    final user = await _auth.getUser();

    if (user == null) {
      _showNoUserDialog();
      return;
    }

    if (user.email != email) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Bu e-posta ile kayıt bulunamadı.')),
      );
      return;
    }

    setState(() {
      _currentStep = 2;
      _recoveryQuestion = user.recoveryQuestion;
      _userEmail = email;
    });
  }

  Future<void> _verifyAnswer() async {
    if (_answerController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Güvenlik cevabı gerekli')),
      );
      return;
    }

    final answerHash = hashText(_answerController.text);
    final isValid = await _auth.verifyRecovery(
      email: _userEmail,
      answerHash: answerHash,
    );

    if (!isValid) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cevap hatalı.')),
      );
      return;
    }

    setState(() {
      _currentStep = 3;
    });
  }

  Future<void> _resetPassword() async {
    if (!_formKey.currentState!.validate()) return;

    if (_newPasswordController.text != _newPasswordAgainController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Şifreler eşleşmiyor.')),
      );
      return;
    }

    final newPasswordHash = hashText(_newPasswordController.text);
    final success = await _auth.updatePassword(
      email: _userEmail,
      newPasswordHash: newPasswordHash,
    );

    if (!success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Şifre güncellenirken hata oluştu')),
      );
      return;
    }

    await _auth.setLoggedIn(true);
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Şifre güncellendi, giriş yapıldı.')),
    );

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const HomePage()),
      (route) => false,
    );
  }

  void _showNoUserDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Kayıt Bulunamadı'),
        content: const Text('Lütfen kaydolun.'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const RegisterPage()),
              );
            },
            child: const Text('Kaydol'),
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(4, (index) {
        final stepNumber = index + 1;
        final isActive = stepNumber <= _currentStep;
        final isCompleted = stepNumber < _currentStep;

        return Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isActive
                    ? Theme.of(context).colorScheme.primary
                    : Theme.of(context).colorScheme.outline,
              ),
              child: Center(
                child: isCompleted
                    ? const Icon(Icons.check, color: Colors.white, size: 16)
                    : Text(
                        '$stepNumber',
                        style: TextStyle(
                          color: isActive ? Colors.white : Colors.grey,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
            if (index < 3)
              Container(
                width: 40,
                height: 2,
                color: isCompleted
                    ? Theme.of(context).colorScheme.primary
                    : Theme.of(context).colorScheme.outline,
              ),
          ],
        );
      }),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Şifremi Unuttum')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 480),
              child: Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Icon(
                          Icons.lock_reset,
                          size: 56,
                          color: theme.colorScheme.primary,
                        ),
                        const SizedBox(height: 24),
                        _buildStepIndicator(),
                        const SizedBox(height: 32),

                        // Step 1: Email
                        if (_currentStep == 1) ...[
                          TextFormField(
                            controller: _emailController,
                            keyboardType: TextInputType.emailAddress,
                            decoration: const InputDecoration(
                              labelText: 'E-posta',
                            ),
                            validator: _validateEmail,
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            height: 48,
                            child: FilledButton(
                              onPressed: _verifyEmail,
                              child: const Text('Doğrula'),
                            ),
                          ),
                        ],

                        // Step 2: Security Question
                        if (_currentStep == 2) ...[
                          const Text(
                            'Güvenlik Sorunuz',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              border:
                                  Border.all(color: theme.colorScheme.outline),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              _recoveryQuestion,
                              style: const TextStyle(fontSize: 16),
                            ),
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            controller: _answerController,
                            decoration: const InputDecoration(
                              labelText: 'Güvenlik Cevabınız',
                            ),
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            height: 48,
                            child: FilledButton(
                              onPressed: _verifyAnswer,
                              child: const Text('Onayla'),
                            ),
                          ),
                        ],

                        // Step 3: New Password
                        if (_currentStep == 3) ...[
                          TextFormField(
                            controller: _newPasswordController,
                            obscureText: _obscure1,
                            decoration: InputDecoration(
                              labelText: 'Yeni Şifre',
                              suffixIcon: IconButton(
                                onPressed: () =>
                                    setState(() => _obscure1 = !_obscure1),
                                icon: Icon(_obscure1
                                    ? Icons.visibility
                                    : Icons.visibility_off),
                                tooltip: 'Şifreyi göster/gizle',
                              ),
                            ),
                            validator: _validatePassword,
                          ),
                          const SizedBox(height: 16),
                          TextFormField(
                            controller: _newPasswordAgainController,
                            obscureText: _obscure2,
                            decoration: InputDecoration(
                              labelText: 'Yeni Şifre (Tekrar)',
                              suffixIcon: IconButton(
                                onPressed: () =>
                                    setState(() => _obscure2 = !_obscure2),
                                icon: Icon(_obscure2
                                    ? Icons.visibility
                                    : Icons.visibility_off),
                                tooltip: 'Şifreyi göster/gizle',
                              ),
                            ),
                            validator: _validatePassword,
                          ),
                          const SizedBox(height: 24),
                          SizedBox(
                            height: 48,
                            child: FilledButton(
                              onPressed: _resetPassword,
                              child: const Text('Şifreyi Sıfırla'),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
