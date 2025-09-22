import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';

class FirebaseTestPage extends StatefulWidget {
  const FirebaseTestPage({super.key});

  @override
  State<FirebaseTestPage> createState() => _FirebaseTestPageState();
}

class _FirebaseTestPageState extends State<FirebaseTestPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _status = '';

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _testPasswordReset() async {
    if (_emailController.text.isEmpty) {
      setState(() => _status = '❌ Email gerekli');
      return;
    }

    setState(() {
      _isLoading = true;
      _status = '🔄 Şifre sıfırlama e-postası gönderiliyor...';
    });

    try {
      await FirebaseAuth.instance.sendPasswordResetEmail(
        email: _emailController.text.toLowerCase().trim(),
      );
      
      setState(() => _status = '✅ Şifre sıfırlama e-postası gönderildi!');
    } on FirebaseAuthException catch (e) {
      setState(() => _status = '❌ Hata: ${e.code} - ${e.message}');
    } catch (e) {
      setState(() => _status = '❌ Genel hata: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _testLogin() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      setState(() => _status = '❌ Email ve şifre gerekli');
      return;
    }

    setState(() {
      _isLoading = true;
      _status = '🔄 Giriş yapılıyor...';
    });

    try {
      await FirebaseAuth.instance.signInWithEmailAndPassword(
        email: _emailController.text.toLowerCase().trim(),
        password: _passwordController.text,
      );
      
      setState(() => _status = '✅ Giriş başarılı!');
    } on FirebaseAuthException catch (e) {
      setState(() => _status = '❌ Giriş hatası: ${e.code} - ${e.message}');
    } catch (e) {
      setState(() => _status = '❌ Genel hata: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Firebase Test'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Firebase Authentication Test',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Bu sayfa Firebase Authentication ayarlarını test etmek için kullanılır.',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Icons.email),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            
            TextFormField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Şifre',
                prefixIcon: Icon(Icons.lock),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _testPasswordReset,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Şifre Sıfırla Test'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _testLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                    child: const Text('Giriş Test'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            
            if (_isLoading)
              const Center(child: CircularProgressIndicator()),
            
            if (_status.isNotEmpty) ...[
              Card(
                color: _status.contains('✅') ? Colors.green.shade50 : 
                       _status.contains('❌') ? Colors.red.shade50 : Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    _status,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: _status.contains('✅') ? Colors.green.shade800 : 
                             _status.contains('❌') ? Colors.red.shade800 : Colors.blue.shade800,
                    ),
                  ),
                ),
              ),
            ],
            
            const SizedBox(height: 16),
            
            Card(
              color: Colors.blue.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Firebase Console Kontrol Listesi:',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text('1. Firebase Console > Authentication > Settings'),
                    const Text('2. Authorized domains kontrolü'),
                    const Text('3. Email/Password provider aktif mi?'),
                    const Text('4. Email templates ayarları'),
                    const Text('5. SMTP ayarları (varsa)'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
