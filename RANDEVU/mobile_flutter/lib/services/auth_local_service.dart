import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

abstract class AuthRepository {
  Future<bool> isLoggedIn();
  Future<void> saveUser(User user);
  Future<User?> getUser();
  Future<void> setLoggedIn(bool value);
  Future<void> logout();
  Future<bool> hasUser();
  Future<bool> updatePassword(
      {required String email, required String newPasswordHash});
  Future<bool> verifyRecovery(
      {required String email, required String answerHash});
}

class AuthLocalService implements AuthRepository {
  static const String _keyIsLoggedIn = 'isLoggedIn';
  static const String _keyUserJson = 'userJson';

  @override
  Future<bool> isLoggedIn() async {
    final sp = await SharedPreferences.getInstance();
    return sp.getBool(_keyIsLoggedIn) ?? false;
  }

  @override
  Future<void> saveUser(User user) async {
    final sp = await SharedPreferences.getInstance();
    await sp.setString(_keyUserJson, user.toJsonString());
  }

  @override
  Future<void> setLoggedIn(bool value) async {
    final sp = await SharedPreferences.getInstance();
    await sp.setBool(_keyIsLoggedIn, value);
  }

  @override
  Future<User?> getUser() async {
    final sp = await SharedPreferences.getInstance();
    return User.fromJsonString(sp.getString(_keyUserJson));
  }

  @override
  Future<void> logout() async {
    final sp = await SharedPreferences.getInstance();
    await sp.setBool(_keyIsLoggedIn, false);
    // Note: We do NOT remove _keyUserJson to preserve user data for future logins
  }

  @override
  Future<bool> hasUser() async {
    final sp = await SharedPreferences.getInstance();
    return sp.getString(_keyUserJson) != null;
  }

  @override
  Future<bool> updatePassword(
      {required String email, required String newPasswordHash}) async {
    final user = await getUser();
    if (user == null || user.email != email) return false;

    final updatedUser = User(
      name: user.name,
      email: user.email,
      phone: user.phone,
      passwordHash: newPasswordHash,
      recoveryQuestion: user.recoveryQuestion,
      recoveryAnswerHash: user.recoveryAnswerHash,
    );

    await saveUser(updatedUser);
    return true;
  }

  @override
  Future<bool> verifyRecovery(
      {required String email, required String answerHash}) async {
    final user = await getUser();
    return user != null &&
        user.email == email &&
        user.recoveryAnswerHash == answerHash;
  }
}
