import 'dart:convert';
import 'package:crypto/crypto.dart';

String hashText(String raw) {
  final norm = raw.trim().toLowerCase();
  final bytes = utf8.encode(norm);
  return sha256.convert(bytes).toString();
}
