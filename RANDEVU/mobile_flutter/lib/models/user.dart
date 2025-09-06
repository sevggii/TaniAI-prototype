import 'dart:convert';

class User {
  final String name;
  final String email;
  final String? phone;
  final String passwordHash;
  final String recoveryQuestion;
  final String recoveryAnswerHash;

  const User({
    required this.name,
    required this.email,
    this.phone,
    required this.passwordHash,
    required this.recoveryQuestion,
    required this.recoveryAnswerHash,
  });

  Map<String, dynamic> toJson() => {
        'name': name,
        'email': email,
        'phone': phone,
        'passwordHash': passwordHash,
        'recoveryQuestion': recoveryQuestion,
        'recoveryAnswerHash': recoveryAnswerHash,
      };

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      name: json['name'] as String? ?? '',
      email: json['email'] as String? ?? '',
      phone: json['phone'] as String?,
      passwordHash: json['passwordHash'] as String? ?? '',
      recoveryQuestion: json['recoveryQuestion'] as String? ?? '',
      recoveryAnswerHash: json['recoveryAnswerHash'] as String? ?? '',
    );
  }

  static User? fromJsonString(String? jsonString) {
    if (jsonString == null || jsonString.isEmpty) return null;
    try {
      final map = jsonDecode(jsonString) as Map<String, dynamic>;
      return User.fromJson(map);
    } catch (_) {
      return null;
    }
  }

  String toJsonString() => jsonEncode(toJson());
}
