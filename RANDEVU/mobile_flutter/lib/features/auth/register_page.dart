import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../services/auth_local_service.dart';
import '../../services/hash.dart';
import '../../home_page.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordAgainController = TextEditingController();
  final _recoveryAnswerController = TextEditingController();
  bool _obscure1 = true;
  bool _obscure2 = true;
  bool _kvkk = false;
  String _selectedQuestion = 'İlk evcil hayvanınız?';
  final _auth = AuthLocalService();

  final List<String> _recoveryQuestions = [
    'İlk evcil hayvanınız?',
    'İlkokul öğretmeninizin adı?',
    'En sevdiğiniz şehir?',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _passwordAgainController.dispose();
    _recoveryAnswerController.dispose();
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
    if (v.length < 6) return 'En az 6 karakter';
    return null;
  }

  Future<void> _submit() async {
    if (!_kvkk) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Aydınlatma metnini onaylayın.')),
      );
      return;
    }
    if (!_formKey.currentState!.validate()) return;
    if (_passwordController.text != _passwordAgainController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Şifreler eşleşmiyor')),
      );
      return;
    }
    if (_recoveryAnswerController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Güvenlik cevabı gerekli')),
      );
      return;
    }

    final user = User(
      name: _nameController.text.trim(),
      email: _emailController.text.trim(),
      phone: _phoneController.text.trim().isEmpty
          ? null
          : _phoneController.text.trim(),
      passwordHash: hashText(_passwordController.text),
      recoveryQuestion: _selectedQuestion,
      recoveryAnswerHash: hashText(_recoveryAnswerController.text),
    );

    await _auth.saveUser(user);
    await _auth.setLoggedIn(true);
    if (!mounted) return;
    ScaffoldMessenger.of(context)
        .showSnackBar(const SnackBar(content: Text('Kayıt tamamlandı')));
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const HomePage()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Kaydol')),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 560),
              child: Card(
                elevation: 0,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Icon(Icons.local_hospital_rounded,
                            size: 56, color: theme.colorScheme.primary),
                        const SizedBox(height: 24),
                        TextFormField(
                          controller: _nameController,
                          textCapitalization: TextCapitalization.words,
                          decoration:
                              const InputDecoration(labelText: 'Ad Soyad'),
                          validator: (v) => (v == null || v.trim().isEmpty)
                              ? 'Ad Soyad gerekli'
                              : null,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                              labelText: 'Telefon (opsiyonel)'),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          decoration:
                              const InputDecoration(labelText: 'E-posta'),
                          validator: _validateEmail,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _passwordController,
                          obscureText: _obscure1,
                          decoration: InputDecoration(
                            labelText: 'Şifre',
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
                          controller: _passwordAgainController,
                          obscureText: _obscure2,
                          decoration: InputDecoration(
                            labelText: 'Şifre Tekrar',
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
                        const SizedBox(height: 16),
                        DropdownButtonFormField<String>(
                          value: _selectedQuestion,
                          decoration: const InputDecoration(
                            labelText: 'Güvenlik Sorusu',
                          ),
                          items: _recoveryQuestions.map((String question) {
                            return DropdownMenuItem<String>(
                              value: question,
                              child: Text(question),
                            );
                          }).toList(),
                          onChanged: (String? newValue) {
                            if (newValue != null) {
                              setState(() {
                                _selectedQuestion = newValue;
                              });
                            }
                          },
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _recoveryAnswerController,
                          decoration: const InputDecoration(
                            labelText: 'Güvenlik Cevabı',
                          ),
                          validator: (v) => (v == null || v.trim().isEmpty)
                              ? 'Güvenlik cevabı gerekli'
                              : null,
                        ),
                        const SizedBox(height: 12),
                        CheckboxListTile(
                          value: _kvkk,
                          onChanged: (v) => setState(() => _kvkk = v ?? false),
                          title: const Text(
                              'Aydınlatma metnini okudum, onaylıyorum.'),
                          controlAffinity: ListTileControlAffinity.leading,
                          contentPadding: EdgeInsets.zero,
                        ),
                        const SizedBox(height: 8),
                        SizedBox(
                          height: 48,
                          child: FilledButton(
                            onPressed: _submit,
                            child: const Text('Kaydol'),
                          ),
                        ),
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
