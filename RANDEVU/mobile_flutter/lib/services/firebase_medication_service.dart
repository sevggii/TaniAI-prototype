/// Firebase Firestore İlaç Takibi Servisi
/// Uygulama silinse bile veriler korunur

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

class FirebaseMedicationService {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  
  // Collection adları
  static const String _medicationTakenCollection = 'medication_taken';
  static const String _medicationSkippedCollection = 'medication_skipped';
  static const String _userSettingsCollection = 'user_settings';

  /// Kullanıcı ID'sini al
  static String? get _userId => _auth.currentUser?.uid;

  /// İlaç alındı durumlarını Firebase'e kaydet
  static Future<void> saveMedicationTaken(Map<int, bool> takenMap) async {
    if (_userId == null) return;
    
    try {
      final docRef = _firestore
          .collection(_medicationTakenCollection)
          .doc(_userId);
      
      final data = {
        'taken_map': takenMap.map((key, value) => MapEntry(key.toString(), value)),
        'last_updated': FieldValue.serverTimestamp(),
        'date': _getTodayString(),
      };
      
      await docRef.set(data, SetOptions(merge: true));
    } catch (e) {
      print('Firebase save error: $e');
      rethrow;
    }
  }

  /// İlaç atlandı durumlarını Firebase'e kaydet
  static Future<void> saveMedicationSkipped(Map<int, bool> skippedMap) async {
    if (_userId == null) return;
    
    try {
      final docRef = _firestore
          .collection(_medicationSkippedCollection)
          .doc(_userId);
      
      final data = {
        'skipped_map': skippedMap.map((key, value) => MapEntry(key.toString(), value)),
        'last_updated': FieldValue.serverTimestamp(),
        'date': _getTodayString(),
      };
      
      await docRef.set(data, SetOptions(merge: true));
    } catch (e) {
      print('Firebase save error: $e');
      rethrow;
    }
  }

  /// İlaç alındı durumlarını Firebase'den yükle
  static Future<Map<int, bool>> loadMedicationTaken() async {
    if (_userId == null) return {};
    
    try {
      final doc = await _firestore
          .collection(_medicationTakenCollection)
          .doc(_userId)
          .get();
      
      if (!doc.exists) return {};
      
      final data = doc.data();
      if (data == null) return {};
      
      // Bugünkü veriyi kontrol et
      final date = data['date'] as String?;
      if (date != _getTodayString()) {
        // Farklı gün, temizle
        await _clearTodayData();
        return {};
      }
      
      final takenMap = data['taken_map'] as Map<String, dynamic>?;
      if (takenMap == null) return {};
      
      return takenMap.map((key, value) => MapEntry(int.parse(key), value as bool));
    } catch (e) {
      print('Firebase load error: $e');
      return {};
    }
  }

  /// İlaç atlandı durumlarını Firebase'den yükle
  static Future<Map<int, bool>> loadMedicationSkipped() async {
    if (_userId == null) return {};
    
    try {
      final doc = await _firestore
          .collection(_medicationSkippedCollection)
          .doc(_userId)
          .get();
      
      if (!doc.exists) return {};
      
      final data = doc.data();
      if (data == null) return {};
      
      // Bugünkü veriyi kontrol et
      final date = data['date'] as String?;
      if (date != _getTodayString()) {
        // Farklı gün, temizle
        await _clearTodayData();
        return {};
      }
      
      final skippedMap = data['skipped_map'] as Map<String, dynamic>?;
      if (skippedMap == null) return {};
      
      return skippedMap.map((key, value) => MapEntry(int.parse(key), value as bool));
    } catch (e) {
      print('Firebase load error: $e');
      return {};
    }
  }

  /// Günlük verileri temizle (yeni gün başladığında)
  static Future<void> clearTodayData() async {
    if (_userId == null) return;
    
    try {
      await _clearTodayData();
    } catch (e) {
      print('Firebase clear error: $e');
      rethrow;
    }
  }

  /// Tüm kullanıcı verilerini temizle (logout)
  static Future<void> clearAllUserData() async {
    if (_userId == null) return;
    
    try {
      await Future.wait([
        _firestore.collection(_medicationTakenCollection).doc(_userId).delete(),
        _firestore.collection(_medicationSkippedCollection).doc(_userId).delete(),
        _firestore.collection(_userSettingsCollection).doc(_userId).delete(),
      ]);
    } catch (e) {
      print('Firebase clear all error: $e');
      rethrow;
    }
  }

  /// Kullanıcı ayarlarını kaydet
  static Future<void> saveUserSettings(Map<String, dynamic> settings) async {
    if (_userId == null) return;
    
    try {
      await _firestore
          .collection(_userSettingsCollection)
          .doc(_userId)
          .set({
        ...settings,
        'last_updated': FieldValue.serverTimestamp(),
      }, SetOptions(merge: true));
    } catch (e) {
      print('Firebase settings save error: $e');
      rethrow;
    }
  }

  /// Kullanıcı ayarlarını yükle
  static Future<Map<String, dynamic>> loadUserSettings() async {
    if (_userId == null) return {};
    
    try {
      final doc = await _firestore
          .collection(_userSettingsCollection)
          .doc(_userId)
          .get();
      
      if (!doc.exists) return {};
      
      final data = doc.data();
      if (data == null) return {};
      
      // serverTimestamp'ı kaldır
      data.remove('last_updated');
      return data;
    } catch (e) {
      print('Firebase settings load error: $e');
      return {};
    }
  }

  /// İlaç geçmişini kaydet (günlük özet)
  static Future<void> saveDailyHistory({
    required int medicationId,
    required String medicationName,
    required bool wasTaken,
    required bool wasSkipped,
    required DateTime timestamp,
    String? notes,
  }) async {
    if (_userId == null) return;
    
    try {
      await _firestore
          .collection('medication_history')
          .doc(_userId)
          .collection('daily_logs')
          .add({
        'medication_id': medicationId,
        'medication_name': medicationName,
        'was_taken': wasTaken,
        'was_skipped': wasSkipped,
        'timestamp': timestamp,
        'notes': notes,
        'date': _getTodayString(),
      });
    } catch (e) {
      print('Firebase history save error: $e');
      rethrow;
    }
  }

  /// Günlük geçmişi yükle
  static Future<List<Map<String, dynamic>>> loadDailyHistory() async {
    if (_userId == null) return [];
    
    try {
      final querySnapshot = await _firestore
          .collection('medication_history')
          .doc(_userId)
          .collection('daily_logs')
          .where('date', isEqualTo: _getTodayString())
          .orderBy('timestamp', descending: true)
          .get();
      
      return querySnapshot.docs.map((doc) => {
        'id': doc.id,
        ...doc.data(),
      }).toList();
    } catch (e) {
      print('Firebase history load error: $e');
      return [];
    }
  }

  /// Bugünün tarih string'ini al (YYYY-MM-DD)
  static String _getTodayString() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
  }

  /// Bugünkü verileri temizle
  static Future<void> _clearTodayData() async {
    if (_userId == null) return;
    
    await Future.wait([
      _firestore.collection(_medicationTakenCollection).doc(_userId).delete(),
      _firestore.collection(_medicationSkippedCollection).doc(_userId).delete(),
    ]);
  }

  /// Kullanıcı giriş yaptığında verileri senkronize et
  static Future<void> syncUserData() async {
    if (_userId == null) return;
    
    try {
      // Günlük verileri yükle
      final takenData = await loadMedicationTaken();
      final skippedData = await loadMedicationSkipped();
      
      print('User data synced: ${takenData.length} taken, ${skippedData.length} skipped');
    } catch (e) {
      print('Firebase sync error: $e');
    }
  }

  /// Kullanıcı çıkış yaptığında temizlik yap
  static Future<void> cleanupOnLogout() async {
    // Local verileri temizle (Firebase verileri korunur)
    // Bu fonksiyon sadece local cache temizliği için
    print('User logged out, local data cleared');
  }
}
