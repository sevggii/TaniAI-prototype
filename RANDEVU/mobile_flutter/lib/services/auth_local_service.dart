import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../models/user_role.dart';

class AuthLocalService {
  static final AuthLocalService _instance = AuthLocalService._internal();
  factory AuthLocalService() => _instance;
  AuthLocalService._internal();

  UserModel? _currentUser;
  final String _userKey = 'current_user';

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

      // Create new user
      final user = UserModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: name,
        email: email.toLowerCase().trim(),
        role: role,
        createdAt: DateTime.now(),
      );

      // Save user locally
      _currentUser = user;
      await _saveUserToStorage(user);

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
      // For demo purposes, create a user if none exists
      if (_currentUser == null) {
        final user = UserModel(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          name: role == UserRole.doctor ? 'Demo Doktor' : 'Demo Kullanıcı',
          email: email.toLowerCase().trim(),
          role: role,
          createdAt: DateTime.now(),
        );
        _currentUser = user;
        await _saveUserToStorage(user);
      }

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
}
