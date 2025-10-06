/// Kalıcı Veri Saklama Servisi
/// SharedPreferences ile kullanıcı verilerini saklar

import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class StorageService {
  static const String _medicationTakenKey = 'medication_taken_today';
  static const String _medicationSkippedKey = 'medication_skipped_today';
  static const String _lastResetDateKey = 'last_reset_date';

  /// İlaç alındı durumlarını kaydet
  static Future<void> saveMedicationTaken(Map<int, bool> takenMap) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = json.encode(takenMap);
    await prefs.setString(_medicationTakenKey, jsonString);
  }

  /// İlaç atlandı durumlarını kaydet
  static Future<void> saveMedicationSkipped(Map<int, bool> skippedMap) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = json.encode(skippedMap);
    await prefs.setString(_medicationSkippedKey, jsonString);
  }

  /// İlaç alındı durumlarını yükle
  static Future<Map<int, bool>> loadMedicationTaken() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = prefs.getString(_medicationTakenKey);
    
    if (jsonString == null) return {};
    
    try {
      final Map<String, dynamic> jsonMap = json.decode(jsonString);
      return jsonMap.map((key, value) => MapEntry(int.parse(key), value as bool));
    } catch (e) {
      return {};
    }
  }

  /// İlaç atlandı durumlarını yükle
  static Future<Map<int, bool>> loadMedicationSkipped() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonString = prefs.getString(_medicationSkippedKey);
    
    if (jsonString == null) return {};
    
    try {
      final Map<String, dynamic> jsonMap = json.decode(jsonString);
      return jsonMap.map((key, value) => MapEntry(int.parse(key), value as bool));
    } catch (e) {
      return {};
    }
  }

  /// Son sıfırlama tarihini kaydet
  static Future<void> saveLastResetDate(DateTime date) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_lastResetDateKey, date.toIso8601String());
  }

  /// Son sıfırlama tarihini yükle
  static Future<DateTime?> loadLastResetDate() async {
    final prefs = await SharedPreferences.getInstance();
    final dateString = prefs.getString(_lastResetDateKey);
    
    if (dateString == null) return null;
    
    try {
      return DateTime.parse(dateString);
    } catch (e) {
      return null;
    }
  }

  /// Günlük verileri sıfırla (yeni gün başladığında)
  static Future<void> resetDailyData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_medicationTakenKey);
    await prefs.remove(_medicationSkippedKey);
    await saveLastResetDate(DateTime.now());
  }

  /// Tüm verileri temizle (logout)
  static Future<void> clearAllData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_medicationTakenKey);
    await prefs.remove(_medicationSkippedKey);
    await prefs.remove(_lastResetDateKey);
  }

  /// Bugün yeni gün mü kontrol et
  static Future<bool> isNewDay() async {
    final lastReset = await loadLastResetDate();
    if (lastReset == null) return true;
    
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final lastResetDay = DateTime(lastReset.year, lastReset.month, lastReset.day);
    
    return today.isAfter(lastResetDay);
  }
}
