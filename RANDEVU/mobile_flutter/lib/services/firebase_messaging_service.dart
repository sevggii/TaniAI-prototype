import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'notification_service.dart';

/// Firebase Cloud Messaging Servisi
/// Push bildirimler ve global bildirim yönetimi
class FirebaseMessagingService {
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  
  static String? _fcmToken;
  static bool _initialized = false;

  /// FCM servisini başlat
  static Future<void> initialize() async {
    if (_initialized) return;
    
    try {
      // Bildirim izinlerini iste
      await _requestPermissions();
      
      // FCM token'ı al
      _fcmToken = await _messaging.getToken();
      debugPrint('FCM Token: $_fcmToken');
      
      // Token'ı kullanıcıya kaydet
      await _saveTokenToUser();
      
      // Token yenileme dinleyicisi
      _messaging.onTokenRefresh.listen((newToken) {
        _fcmToken = newToken;
        _saveTokenToUser();
        debugPrint('FCM Token yenilendi: $newToken');
      });
      
      // Foreground mesaj dinleyicisi
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
      
      // Background mesaj dinleyicisi
      FirebaseMessaging.onMessageOpenedApp.listen(_handleBackgroundMessage);
      
      // Uygulama kapalıyken gelen mesaj dinleyicisi
      _handleInitialMessage();
      
      _initialized = true;
      debugPrint('Firebase Messaging başlatıldı');
      
    } catch (e) {
      debugPrint('Firebase Messaging başlatma hatası: $e');
    }
  }

  /// Bildirim izinlerini iste
  static Future<void> _requestPermissions() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );
    
    debugPrint('Bildirim izinleri: ${settings.authorizationStatus}');
  }

  /// Token'ı kullanıcıya kaydet
  static Future<void> _saveTokenToUser() async {
    if (_fcmToken == null || _auth.currentUser == null) return;
    
    try {
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .update({
        'fcmToken': _fcmToken,
        'lastTokenUpdate': FieldValue.serverTimestamp(),
      });
      
      debugPrint('FCM Token kullanıcıya kaydedildi');
    } catch (e) {
      debugPrint('FCM Token kaydetme hatası: $e');
    }
  }

  /// Foreground mesaj işleme
  static void _handleForegroundMessage(RemoteMessage message) {
    debugPrint('Foreground mesaj alındı: ${message.messageId}');
    
    // Local bildirim göster
    NotificationService.showLocalNotification(
      title: message.notification?.title ?? 'TanıAI',
      body: message.notification?.body ?? '',
      payload: message.data.toString(),
    );
  }

  /// Background mesaj işleme
  static void _handleBackgroundMessage(RemoteMessage message) {
    debugPrint('Background mesaj alındı: ${message.messageId}');
    
    // Mesaj verilerini işle
    _processMessageData(message.data);
  }

  /// Uygulama kapalıyken gelen mesaj işleme
  static Future<void> _handleInitialMessage() async {
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      debugPrint('Uygulama kapalıyken mesaj alındı: ${initialMessage.messageId}');
      _processMessageData(initialMessage.data);
    }
  }

  /// Mesaj verilerini işle
  static void _processMessageData(Map<String, dynamic> data) {
    final type = data['type'] as String?;
    
    switch (type) {
      case 'medication_reminder':
        _handleMedicationReminder(data);
        break;
      case 'appointment_reminder':
        _handleAppointmentReminder(data);
        break;
      case 'health_reminder':
        _handleHealthReminder(data);
        break;
      default:
        debugPrint('Bilinmeyen mesaj türü: $type');
    }
  }

  /// İlaç hatırlatma mesajı işleme
  static void _handleMedicationReminder(Map<String, dynamic> data) {
    final medicationName = data['medicationName'] as String?;
    final dosage = data['dosage'] as String?;
    
    debugPrint('İlaç hatırlatma: $medicationName ($dosage)');
    
    // İlaç alındı olarak işaretle (gerçek uygulamada veritabanını güncelle)
    _markMedicationAsTaken(medicationName, dosage);
  }

  /// Randevu hatırlatma mesajı işleme
  static void _handleAppointmentReminder(Map<String, dynamic> data) {
    final doctorName = data['doctorName'] as String?;
    final clinicName = data['clinicName'] as String?;
    final appointmentTime = data['appointmentTime'] as String?;
    
    debugPrint('Randevu hatırlatma: $doctorName - $clinicName - $appointmentTime');
  }

  /// Sağlık hatırlatma mesajı işleme
  static void _handleHealthReminder(Map<String, dynamic> data) {
    final reminderType = data['reminderType'] as String?;
    final message = data['message'] as String?;
    
    debugPrint('Sağlık hatırlatma: $reminderType - $message');
  }

  /// İlacı alındı olarak işaretle
  static Future<void> _markMedicationAsTaken(String? medicationName, String? dosage) async {
    if (_auth.currentUser == null || medicationName == null) return;
    
    try {
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('medication_history')
          .add({
        'medicationName': medicationName,
        'dosage': dosage,
        'takenAt': FieldValue.serverTimestamp(),
        'source': 'push_notification',
      });
      
      debugPrint('İlaç alındı olarak işaretlendi: $medicationName');
    } catch (e) {
      debugPrint('İlaç işaretleme hatası: $e');
    }
  }

  /// İlaç hatırlatma bildirimi gönder
  static Future<void> sendMedicationReminder({
    required String userId,
    required String medicationName,
    required String dosage,
    required String frequency,
    required DateTime scheduledTime,
  }) async {
    try {
      // Firestore'da hatırlatma kaydı oluştur
      await _firestore
          .collection('users')
          .doc(userId)
          .collection('medication_reminders')
          .add({
        'medicationName': medicationName,
        'dosage': dosage,
        'frequency': frequency,
        'scheduledTime': Timestamp.fromDate(scheduledTime),
        'createdAt': FieldValue.serverTimestamp(),
        'isActive': true,
      });
      
      debugPrint('İlaç hatırlatma kaydedildi: $medicationName');
    } catch (e) {
      debugPrint('İlaç hatırlatma kaydetme hatası: $e');
    }
  }

  /// Randevu hatırlatma bildirimi gönder
  static Future<void> sendAppointmentReminder({
    required String userId,
    required String doctorName,
    required String clinicName,
    required DateTime appointmentTime,
    required int reminderMinutesBefore,
  }) async {
    try {
      await _firestore
          .collection('users')
          .doc(userId)
          .collection('appointment_reminders')
          .add({
        'doctorName': doctorName,
        'clinicName': clinicName,
        'appointmentTime': Timestamp.fromDate(appointmentTime),
        'reminderMinutesBefore': reminderMinutesBefore,
        'createdAt': FieldValue.serverTimestamp(),
        'isActive': true,
      });
      
      debugPrint('Randevu hatırlatma kaydedildi: $doctorName');
    } catch (e) {
      debugPrint('Randevu hatırlatma kaydetme hatası: $e');
    }
  }

  /// Kullanıcının bildirimlerini getir
  static Future<List<Map<String, dynamic>>> getUserNotifications() async {
    if (_auth.currentUser == null) return [];
    
    try {
      final snapshot = await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('notifications')
          .orderBy('createdAt', descending: true)
          .limit(50)
          .get();
      
      return snapshot.docs.map((doc) {
        final data = doc.data();
        data['id'] = doc.id;
        return data;
      }).toList();
    } catch (e) {
      debugPrint('Bildirimler getirme hatası: $e');
      return [];
    }
  }

  /// Bildirimi okundu olarak işaretle
  static Future<void> markNotificationAsRead(String notificationId) async {
    if (_auth.currentUser == null) return;
    
    try {
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('notifications')
          .doc(notificationId)
          .update({
        'isRead': true,
        'readAt': FieldValue.serverTimestamp(),
      });
      
      debugPrint('Bildirim okundu olarak işaretlendi: $notificationId');
    } catch (e) {
      debugPrint('Bildirim işaretleme hatası: $e');
    }
  }

  /// Tüm bildirimleri okundu olarak işaretle
  static Future<void> markAllNotificationsAsRead() async {
    if (_auth.currentUser == null) return;
    
    try {
      final batch = _firestore.batch();
      final snapshot = await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('notifications')
          .where('isRead', isEqualTo: false)
          .get();
      
      for (final doc in snapshot.docs) {
        batch.update(doc.reference, {
          'isRead': true,
          'readAt': FieldValue.serverTimestamp(),
        });
      }
      
      await batch.commit();
      debugPrint('Tüm bildirimler okundu olarak işaretlendi');
    } catch (e) {
      debugPrint('Tüm bildirimleri işaretleme hatası: $e');
    }
  }

  /// Bildirim ayarlarını getir
  static Future<Map<String, dynamic>?> getNotificationSettings() async {
    if (_auth.currentUser == null) return null;
    
    try {
      final doc = await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('settings')
          .doc('notifications')
          .get();
      
      return doc.exists ? doc.data() : null;
    } catch (e) {
      debugPrint('Bildirim ayarları getirme hatası: $e');
      return null;
    }
  }

  /// Bildirim ayarlarını kaydet
  static Future<void> saveNotificationSettings(Map<String, dynamic> settings) async {
    if (_auth.currentUser == null) return;
    
    try {
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('settings')
          .doc('notifications')
          .set({
        ...settings,
        'updatedAt': FieldValue.serverTimestamp(),
      });
      
      debugPrint('Bildirim ayarları kaydedildi');
    } catch (e) {
      debugPrint('Bildirim ayarları kaydetme hatası: $e');
    }
  }

  /// FCM Token'ı al
  static String? get fcmToken => _fcmToken;

  /// Servis başlatıldı mı?
  static bool get isInitialized => _initialized;
}

/// Background mesaj işleyici (top-level function)
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  debugPrint('Background mesaj işlendi: ${message.messageId}');
  
  // Background'da yapılacak işlemler
  // Örneğin: veritabanı güncellemeleri, analytics, vb.
}
