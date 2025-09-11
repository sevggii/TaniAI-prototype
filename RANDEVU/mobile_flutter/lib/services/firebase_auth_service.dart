import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/user_role.dart';

class FirebaseAuthService {
  static final FirebaseAuthService _instance = FirebaseAuthService._internal();
  factory FirebaseAuthService() => _instance;
  FirebaseAuthService._internal();

  final FirebaseAuth _auth = FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  /// Get current user
  User? get currentUser => _auth.currentUser;

  /// Check if user is logged in
  bool get isLoggedIn => _auth.currentUser != null;

  /// Get auth state changes stream
  Stream<User?> get authStateChanges => _auth.authStateChanges();

  /// Register with email and password
  Future<UserModel> register({
    required String name,
    required String email,
    required String password,
    required UserRole role,
  }) async {
    try {
      // Validate password strength
      if (password.length < 6) {
        throw Exception('Şifre en az 6 karakter olmalı');
      }

      // Create Firebase user
      final UserCredential userCredential = await _auth.createUserWithEmailAndPassword(
        email: email.toLowerCase().trim(),
        password: password,
      );

      final User? user = userCredential.user;
      if (user == null) {
        throw Exception('Kullanıcı oluşturulamadı');
      }

      // Update display name
      await user.updateDisplayName(name.trim());

      // Create user document in Firestore
      final userModel = UserModel(
        id: user.uid,
        name: name.trim(),
        email: email.toLowerCase().trim(),
        role: role,
        createdAt: DateTime.now(),
      );

      await _firestore.collection('users').doc(user.uid).set({
        'id': userModel.id,
        'name': userModel.name,
        'email': userModel.email,
        'role': userModel.role.name,
        'createdAt': userModel.createdAt.toIso8601String(),
        'lastLoginAt': DateTime.now().toIso8601String(),
      });

      return userModel;
    } on FirebaseAuthException catch (e) {
      String errorMessage;
      switch (e.code) {
        case 'weak-password':
          errorMessage = 'Şifre çok zayıf';
          break;
        case 'email-already-in-use':
          errorMessage = 'Bu e-posta adresi zaten kayıtlı';
          break;
        case 'invalid-email':
          errorMessage = 'Geçersiz e-posta adresi';
          break;
        default:
          errorMessage = 'Kayıt işlemi başarısız: ${e.message}';
      }
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Kayıt işlemi başarısız: ${e.toString()}');
    }
  }

  /// Login with email and password
  Future<UserModel> login({
    required String email,
    required String password,
    required UserRole role,
    bool rememberMe = false,
  }) async {
    try {
      final UserCredential userCredential = await _auth.signInWithEmailAndPassword(
        email: email.toLowerCase().trim(),
        password: password,
      );

      final User? user = userCredential.user;
      if (user == null) {
        throw Exception('Giriş işlemi başarısız');
      }

      // Check if account is soft deleted
      final isSoftDeleted = await isAccountSoftDeleted(user.uid);
      if (isSoftDeleted) {
        // Restore the account
        await restoreAccount();
      }

      // Get user data from Firestore
      final DocumentSnapshot userDoc = await _firestore.collection('users').doc(user.uid).get();
      
      if (!userDoc.exists) {
        throw Exception('Kullanıcı bilgileri bulunamadı');
      }

      final userData = userDoc.data() as Map<String, dynamic>;
      
      // Update last login time
      await _firestore.collection('users').doc(user.uid).update({
        'lastLoginAt': DateTime.now().toIso8601String(),
      });

      final userModel = UserModel(
        id: userData['id'],
        name: userData['name'],
        email: userData['email'],
        role: UserRole.values.firstWhere((r) => r.name == userData['role']),
        createdAt: DateTime.parse(userData['createdAt']),
      );

      // Save remember me preference
      if (rememberMe) {
        await _saveRememberMeData(email.toLowerCase().trim(), password);
      } else {
        await _clearRememberMeData();
      }

      return userModel;
    } on FirebaseAuthException catch (e) {
      String errorMessage;
      switch (e.code) {
        case 'user-not-found':
          errorMessage = 'Kullanıcı bulunamadı. Lütfen önce kayıt olun.';
          break;
        case 'wrong-password':
          errorMessage = 'Şifre hatalı';
          break;
        case 'invalid-email':
          errorMessage = 'Geçersiz e-posta adresi';
          break;
        case 'user-disabled':
          errorMessage = 'Bu hesap devre dışı bırakılmış';
          break;
        case 'too-many-requests':
          errorMessage = 'Çok fazla başarısız deneme. Lütfen daha sonra tekrar deneyin.';
          break;
        default:
          errorMessage = 'Giriş işlemi başarısız: ${e.message}';
      }
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Giriş işlemi başarısız: ${e.toString()}');
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      await _auth.signOut();
      await _clearRememberMeData();
    } catch (e) {
      throw Exception('Çıkış işlemi başarısız: ${e.toString()}');
    }
  }

  /// Send password reset email
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email.toLowerCase().trim());
    } on FirebaseAuthException catch (e) {
      String errorMessage;
      switch (e.code) {
        case 'user-not-found':
          errorMessage = 'Bu e-posta adresi kayıtlı değil';
          break;
        case 'invalid-email':
          errorMessage = 'Geçersiz e-posta adresi';
          break;
        default:
          errorMessage = 'Şifre sıfırlama e-postası gönderilemedi: ${e.message}';
      }
      throw Exception(errorMessage);
    } catch (e) {
      throw Exception('Şifre sıfırlama e-postası gönderilemedi: ${e.toString()}');
    }
  }

  /// Update user profile
  Future<void> updateProfile({
    String? name,
    String? email,
  }) async {
    final user = _auth.currentUser;
    if (user == null) {
      throw Exception('Kullanıcı giriş yapmamış');
    }

    try {
      // Update Firebase Auth profile
      if (name != null) {
        await user.updateDisplayName(name);
      }
      if (email != null) {
        await user.updateEmail(email);
      }

      // Update Firestore document
      final updateData = <String, dynamic>{};
      if (name != null) updateData['name'] = name;
      if (email != null) updateData['email'] = email.toLowerCase().trim();

      if (updateData.isNotEmpty) {
        await _firestore.collection('users').doc(user.uid).update(updateData);
      }
    } catch (e) {
      throw Exception('Profil güncellenemedi: ${e.toString()}');
    }
  }

  /// Get user data from Firestore
  Future<UserModel?> getUserData(String uid) async {
    try {
      final DocumentSnapshot userDoc = await _firestore.collection('users').doc(uid).get();
      
      if (!userDoc.exists) {
        return null;
      }

      final userData = userDoc.data() as Map<String, dynamic>;
      
      return UserModel(
        id: userData['id'],
        name: userData['name'],
        email: userData['email'],
        role: UserRole.values.firstWhere((r) => r.name == userData['role']),
        createdAt: DateTime.parse(userData['createdAt']),
      );
    } catch (e) {
      print('Error getting user data: $e');
      return null;
    }
  }

  /// Delete user account
  Future<void> deleteAccount() async {
    final user = _auth.currentUser;
    if (user == null) {
      throw Exception('Kullanıcı giriş yapmamış');
    }

    try {
      // Delete user document from Firestore
      await _firestore.collection('users').doc(user.uid).delete();
      
      // Delete Firebase Auth account
      await user.delete();
      
      // Clear remember me data
      await _clearRememberMeData();
    } catch (e) {
      throw Exception('Hesap silinemedi: ${e.toString()}');
    }
  }

  /// Save remember me data to SharedPreferences
  Future<void> _saveRememberMeData(String email, String password) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('remember_me', true);
      await prefs.setString('remembered_email', email);
      await prefs.setString('remembered_password', password);
    } catch (e) {
      print('Error saving remember me data: $e');
    }
  }

  /// Clear remember me data from SharedPreferences
  Future<void> _clearRememberMeData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('remember_me');
      await prefs.remove('remembered_email');
      await prefs.remove('remembered_password');
    } catch (e) {
      print('Error clearing remember me data: $e');
    }
  }

  /// Get remembered login data
  Future<Map<String, String>?> getRememberedLoginData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final rememberMe = prefs.getBool('remember_me') ?? false;
      
      if (rememberMe) {
        final email = prefs.getString('remembered_email');
        final password = prefs.getString('remembered_password');
        
        if (email != null && password != null) {
          return {'email': email, 'password': password};
        }
      }
      return null;
    } catch (e) {
      print('Error getting remembered login data: $e');
      return null;
    }
  }

  /// Check if user should be remembered
  Future<bool> shouldRememberUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getBool('remember_me') ?? false;
    } catch (e) {
      print('Error checking remember me status: $e');
      return false;
    }
  }

  /// Soft delete user account (with recovery period)
  Future<void> softDeleteAccount() async {
    final user = _auth.currentUser;
    if (user == null) {
      throw Exception('Kullanıcı giriş yapmamış');
    }

    try {
      final deleteTime = DateTime.now();
      final recoveryDeadline = deleteTime.add(const Duration(minutes: 5)); // 5 dakika geri dönüş süresi
      
      // Update user document with soft delete info
      await _firestore.collection('users').doc(user.uid).update({
        'isSoftDeleted': true,
        'softDeletedAt': deleteTime.toIso8601String(),
        'recoveryDeadline': recoveryDeadline.toIso8601String(),
      });

      // Sign out user
      await _auth.signOut();
      await _clearRememberMeData();
    } catch (e) {
      throw Exception('Hesap silme işlemi başarısız: ${e.toString()}');
    }
  }

  /// Restore soft deleted account
  Future<void> restoreAccount() async {
    final user = _auth.currentUser;
    if (user == null) {
      throw Exception('Kullanıcı giriş yapmamış');
    }

    try {
      // Remove soft delete info
      await _firestore.collection('users').doc(user.uid).update({
        'isSoftDeleted': false,
        'softDeletedAt': null,
        'recoveryDeadline': null,
      });
    } catch (e) {
      throw Exception('Hesap geri yükleme işlemi başarısız: ${e.toString()}');
    }
  }

  /// Check if account is soft deleted and within recovery period
  Future<bool> isAccountSoftDeleted(String uid) async {
    try {
      final userDoc = await _firestore.collection('users').doc(uid).get();
      
      if (!userDoc.exists) {
        return false;
      }

      final userData = userDoc.data() as Map<String, dynamic>;
      final isSoftDeleted = userData['isSoftDeleted'] ?? false;
      
      if (!isSoftDeleted) {
        return false;
      }

      final recoveryDeadlineStr = userData['recoveryDeadline'];
      if (recoveryDeadlineStr == null) {
        return false;
      }

      final recoveryDeadline = DateTime.parse(recoveryDeadlineStr);
      final now = DateTime.now();

      // If recovery period has passed, permanently delete
      if (now.isAfter(recoveryDeadline)) {
        await _permanentlyDeleteAccount(uid);
        return false;
      }

      return true;
    } catch (e) {
      print('Error checking soft delete status: $e');
      return false;
    }
  }

  /// Permanently delete account (internal use)
  Future<void> _permanentlyDeleteAccount(String uid) async {
    try {
      // Delete user document from Firestore
      await _firestore.collection('users').doc(uid).delete();
      
      // Delete Firebase Auth account
      final user = _auth.currentUser;
      if (user != null && user.uid == uid) {
        await user.delete();
      }
    } catch (e) {
      print('Error permanently deleting account: $e');
    }
  }

  /// Check and clean up expired soft deleted accounts
  Future<void> cleanupExpiredAccounts() async {
    try {
      final now = DateTime.now();
      final querySnapshot = await _firestore
          .collection('users')
          .where('isSoftDeleted', isEqualTo: true)
          .get();

      for (final doc in querySnapshot.docs) {
        final userData = doc.data();
        final recoveryDeadlineStr = userData['recoveryDeadline'];
        
        if (recoveryDeadlineStr != null) {
          final recoveryDeadline = DateTime.parse(recoveryDeadlineStr);
          
          if (now.isAfter(recoveryDeadline)) {
            await _permanentlyDeleteAccount(doc.id);
          }
        }
      }
    } catch (e) {
      print('Error cleaning up expired accounts: $e');
    }
  }
}
