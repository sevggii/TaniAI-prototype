import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

abstract class AuthRepository {
  Future<bool> isLoggedIn();
  Future<void> saveSession(User user);
  Future<User?> getUser();
  Future<void> logout();
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
  Future<void> saveSession(User user) async {
    final sp = await SharedPreferences.getInstance();
    await sp.setBool(_keyIsLoggedIn, true);
    await sp.setString(_keyUserJson, user.toJsonString());
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
    await sp.remove(_keyUserJson);
  }
}
