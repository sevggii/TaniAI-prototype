import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/user_role.dart';
import 'hash.dart';

class AuthLocalService {
  static final AuthLocalService _instance = AuthLocalService._internal();
  factory AuthLocalService() => _instance;
  AuthLocalService._internal();

  UserModel? _currentUser;
  final String _userKey = 'current_user';
  final String _usersKey = 'registered_users';

  /// Get current user
  UserModel? get current => _currentUser;

  /// Check if user is logged in
  bool get isLoggedIn => _currentUser != null;

  /// Initialize service and load user from storage
  Future<void> initialize() async {
    await _loadUserFromStorage();
  }

  /// Load user from local storage
  Future<void> _loadUserFromStorage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userData = prefs.getString(_userKey);
      if (userData != null) {
        _currentUser = UserModel.fromJsonString(userData);
      }
    } catch (e) {
      print('Error loading user from storage: $e');
    }
  }

  /// Save user to local storage
  Future<void> _saveUserToStorage(UserModel user) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, user.toJsonString());
    } catch (e) {
      print('Error saving user to storage: $e');
    }
  }

  /// Get all registered users
  Future<List<User>> _getRegisteredUsers() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final usersData = prefs.getString(_usersKey);
      if (usersData != null) {
        final List<dynamic> usersList = List<dynamic>.from(
          (usersData.split('|||').map((userJson) {
            try {
              return User.fromJsonString(userJson);
            } catch (e) {
              return null;
            }
          }).where((user) => user != null))
        );
        return usersList.cast<User>();
      }
    } catch (e) {
      print('Error loading registered users: $e');
    }
    return [];
  }

  /// Save registered users
  Future<void> _saveRegisteredUsers(List<User> users) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final usersData = users.map((user) => user.toJsonString()).join('|||');
      await prefs.setString(_usersKey, usersData);
    } catch (e) {
      print('Error saving registered users: $e');
    }
  }

  /// Check if email is already registered
  Future<bool> _isEmailRegistered(String email) async {
    final users = await _getRegisteredUsers();
    return users.any((user) => user.email.toLowerCase() == email.toLowerCase());
  }

  /// Register with email and password (local only)
  Future<void> register({
    required String name,
    required String email,
    required String password,
    required UserRole role,
  }) async {
    try {
      // Check if user already exists
      if (_currentUser != null) {
        throw Exception('Kullanıcı zaten giriş yapmış');
      }

      // Check if email is already registered
      if (await _isEmailRegistered(email)) {
        throw Exception('Bu e-posta adresi zaten kayıtlı');
      }

      // Validate password strength
      if (password.length < 6) {
        throw Exception('Şifre en az 6 karakter olmalı');
      }

      // Create new user with hashed password
      final hashedPassword = hashText(password);
      final user = User(
        name: name.trim(),
        email: email.toLowerCase().trim(),
        passwordHash: hashedPassword,
        recoveryQuestion: 'Favori renk?', // Default recovery question
        recoveryAnswerHash: hashText('mavi'), // Default recovery answer
      );

      // Save user to registered users list
      final users = await _getRegisteredUsers();
      users.add(user);
      await _saveRegisteredUsers(users);

      // Create user model for current session
      final userModel = UserModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: name.trim(),
        email: email.toLowerCase().trim(),
        role: role,
        createdAt: DateTime.now(),
      );

      // Save user locally
      _currentUser = userModel;
      await _saveUserToStorage(userModel);

      // Simulate network delay
      await Future.delayed(const Duration(seconds: 1));
    } catch (e) {
      throw Exception('Kayıt işlemi başarısız: ${e.toString()}');
    }
  }

  /// Login with email and password (local only)
  Future<void> login({
    required String email,
    required String password,
    required UserRole role,
  }) async {
    try {
      // Get registered users
      final users = await _getRegisteredUsers();
      
      // Find user by email
      final user = users.firstWhere(
        (u) => u.email.toLowerCase() == email.toLowerCase(),
        orElse: () => throw Exception('Kullanıcı bulunamadı. Lütfen önce kayıt olun.'),
      );

      // Verify password
      final hashedPassword = hashText(password);
      if (user.passwordHash != hashedPassword) {
        throw Exception('Şifre hatalı');
      }

      // Create user model for current session
      final userModel = UserModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: user.name,
        email: user.email,
        role: role,
        createdAt: DateTime.now(),
      );

      // Save user locally
      _currentUser = userModel;
      await _saveUserToStorage(userModel);

      // Simulate network delay
      await Future.delayed(const Duration(seconds: 1));
    } catch (e) {
      throw Exception('Giriş işlemi başarısız: ${e.toString()}');
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_userKey);
      _currentUser = null;
    } catch (e) {
      print('Error during logout: $e');
    }
  }

  /// Send password reset email (simulated)
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      // Check if email is registered
      if (!await _isEmailRegistered(email)) {
        throw Exception('Bu e-posta adresi kayıtlı değil');
      }

      // Simulate network delay
      await Future.delayed(const Duration(seconds: 1));

      // For demo, just print a message
      print('Password reset email would be sent to: $email');
    } catch (e) {
      throw Exception(
          'Şifre sıfırlama e-postası gönderilemedi: ${e.toString()}');
    }
  }

  /// Update user profile
  Future<void> updateProfile({
    String? name,
    String? email,
  }) async {
    if (_currentUser == null) {
      throw Exception('Kullanıcı giriş yapmamış');
    }

    try {
      _currentUser = _currentUser!.copyWith(
        name: name ?? _currentUser!.name,
        email: email ?? _currentUser!.email,
      );

      await _saveUserToStorage(_currentUser!);
    } catch (e) {
      throw Exception('Profil güncellenemedi: ${e.toString()}');
    }
  }

  /// Get user count (for debugging)
  Future<int> getUserCount() async {
    final users = await _getRegisteredUsers();
    return users.length;
  }

  /// Clear all data (for testing)
  Future<void> clearAllData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_userKey);
      await prefs.remove(_usersKey);
      _currentUser = null;
    } catch (e) {
      print('Error clearing data: $e');
    }
  }
}