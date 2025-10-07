import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'notification_service.dart';
import 'firebase_messaging_service.dart';

/// Global Bildirim Yöneticisi
/// Tüm bildirimleri merkezi olarak yönetir
class GlobalNotificationManager {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  
  static List<NotificationItem> _notifications = [];
  static bool _isLoading = false;

  /// Bildirimleri yükle
  static Future<List<NotificationItem>> loadNotifications() async {
    if (_auth.currentUser == null) return [];
    
    setState(() => _isLoading = true);
    
    try {
      // Firebase'den bildirimleri getir
      final firebaseNotifications = await FirebaseMessagingService.getUserNotifications();
      
      // Local bildirimleri getir
      final localNotifications = await NotificationService.getPendingNotifications();
      
      // Birleştir ve sırala
      _notifications = [
        ...firebaseNotifications.map((data) => NotificationItem.fromFirebase(data)),
        ...localNotifications.map((notification) => NotificationItem.fromLocal(notification)),
      ];
      
      // Tarihe göre sırala (en yeni önce)
      _notifications.sort((a, b) => b.createdAt.compareTo(a.createdAt));
      
      return _notifications;
    } catch (e) {
      debugPrint('Bildirimler yüklenirken hata: $e');
      return [];
    } finally {
      setState(() => _isLoading = false);
    }
  }

  /// Yeni bildirim ekle
  static Future<void> addNotification({
    required String title,
    required String body,
    required NotificationType type,
    Map<String, dynamic>? data,
    DateTime? scheduledTime,
  }) async {
    if (_auth.currentUser == null) return;
    
    try {
      final notification = NotificationItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        title: title,
        body: body,
        type: type,
        data: data ?? {},
        createdAt: DateTime.now(),
        scheduledTime: scheduledTime,
        isRead: false,
        isActive: true,
      );
      
      // Firebase'e kaydet
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('notifications')
          .add({
        'title': title,
        'body': body,
        'type': type.name,
        'data': data ?? {},
        'createdAt': FieldValue.serverTimestamp(),
        'scheduledTime': scheduledTime != null ? Timestamp.fromDate(scheduledTime) : null,
        'isRead': false,
        'isActive': true,
      });
      
      // Local listeye ekle
      _notifications.insert(0, notification);
      
      // Eğer zamanlanmışsa, local bildirim de ayarla
      if (scheduledTime != null) {
        await NotificationService.scheduleMedicationReminder(
          id: notification.id.hashCode,
          medicationName: data?['medicationName'] ?? '',
          dosage: data?['dosage'] ?? '',
          scheduledTime: scheduledTime,
          frequency: data?['frequency'] ?? '',
        );
      }
      
      debugPrint('Bildirim eklendi: $title');
    } catch (e) {
      debugPrint('Bildirim ekleme hatası: $e');
    }
  }

  /// İlaç hatırlatması ekle
  static Future<void> addMedicationReminder({
    required String medicationName,
    required String dosage,
    required String frequency,
    required TimeOfDay time,
    List<int> daysOfWeek = const [1, 2, 3, 4, 5, 6, 7],
  }) async {
    final now = DateTime.now();
    var scheduledTime = DateTime(
      now.year,
      now.month,
      now.day,
      time.hour,
      time.minute,
    );
    
    // Eğer zaman geçmişse, yarın için ayarla
    if (scheduledTime.isBefore(now)) {
      scheduledTime = scheduledTime.add(const Duration(days: 1));
    }
    
    await addNotification(
      title: 'İlaç Hatırlatması 💊',
      body: '$medicationName ($dosage) almayı unutmayın!',
      type: NotificationType.medication,
      data: {
        'medicationName': medicationName,
        'dosage': dosage,
        'frequency': frequency,
        'time': '${time.hour}:${time.minute}',
        'daysOfWeek': daysOfWeek,
      },
      scheduledTime: scheduledTime,
    );
  }

  /// Sağlık hatırlatması ekle
  static Future<void> addHealthReminder({
    required String id,
    required String time,
    required String emoji,
    required String title,
    required String description,
  }) async {
    final timeParts = time.split(':');
    final hour = int.parse(timeParts[0]);
    final minute = int.parse(timeParts[1]);
    
    final now = DateTime.now();
    var scheduledTime = DateTime(
      now.year,
      now.month,
      now.day,
      hour,
      minute,
    );
    
    // Eğer zaman geçmişse, yarın için ayarla
    if (scheduledTime.isBefore(now)) {
      scheduledTime = scheduledTime.add(const Duration(days: 1));
    }
    
    await addNotification(
      title: '$emoji $title',
      body: description,
      type: NotificationType.health,
      data: {
        'healthReminderId': id,
        'time': time,
        'emoji': emoji,
        'title': title,
        'description': description,
      },
      scheduledTime: scheduledTime,
    );
  }

  /// Randevu hatırlatması ekle
  static Future<void> addAppointmentReminder({
    required String doctorName,
    required String clinicName,
    required DateTime appointmentTime,
    required int reminderMinutesBefore,
  }) async {
    final reminderTime = appointmentTime.subtract(
      Duration(minutes: reminderMinutesBefore),
    );
    
    await addNotification(
      title: 'Randevu Hatırlatması 📅',
      body: '$reminderMinutesBefore dakika sonra $doctorName ile $clinicName randevunuz var!',
      type: NotificationType.appointment,
      data: {
        'doctorName': doctorName,
        'clinicName': clinicName,
        'appointmentTime': appointmentTime.toIso8601String(),
        'reminderMinutesBefore': reminderMinutesBefore,
      },
      scheduledTime: reminderTime,
    );
  }


  /// Bildirimi okundu olarak işaretle
  static Future<void> markAsRead(String notificationId) async {
    try {
      // Firebase'de güncelle
      await FirebaseMessagingService.markNotificationAsRead(notificationId);
      
      // Local listeyi güncelle
      final index = _notifications.indexWhere((n) => n.id == notificationId);
      if (index != -1) {
        _notifications[index] = _notifications[index].copyWith(isRead: true);
      }
      
      debugPrint('Bildirim okundu olarak işaretlendi: $notificationId');
    } catch (e) {
      debugPrint('Bildirim işaretleme hatası: $e');
    }
  }

  /// Tüm bildirimleri okundu olarak işaretle
  static Future<void> markAllAsRead() async {
    try {
      await FirebaseMessagingService.markAllNotificationsAsRead();
      
      // Local listeyi güncelle
      _notifications = _notifications.map((n) => n.copyWith(isRead: true)).toList();
      
      debugPrint('Tüm bildirimler okundu olarak işaretlendi');
    } catch (e) {
      debugPrint('Tüm bildirimleri işaretleme hatası: $e');
    }
  }

  /// Bildirimi sil
  static Future<void> deleteNotification(String notificationId) async {
    try {
      // Firebase'den sil
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('notifications')
          .doc(notificationId)
          .delete();
      
      // Local bildirimi iptal et
      await NotificationService.cancelNotification(notificationId.hashCode);
      
      // Local listeyi güncelle
      _notifications.removeWhere((n) => n.id == notificationId);
      
      debugPrint('Bildirim silindi: $notificationId');
    } catch (e) {
      debugPrint('Bildirim silme hatası: $e');
    }
  }

  /// Bildirimi aktif/pasif yap
  static Future<void> toggleNotification(String notificationId, bool isActive) async {
    try {
      // Firebase'de güncelle
      await _firestore
          .collection('users')
          .doc(_auth.currentUser!.uid)
          .collection('notifications')
          .doc(notificationId)
          .update({'isActive': isActive});
      
      // Local listeyi güncelle
      final index = _notifications.indexWhere((n) => n.id == notificationId);
      if (index != -1) {
        _notifications[index] = _notifications[index].copyWith(isActive: isActive);
      }
      
      // Local bildirimi iptal et veya yeniden ayarla
      if (isActive) {
        // Yeniden ayarla (burada detaylı implementasyon gerekir)
      } else {
        await NotificationService.cancelNotification(notificationId.hashCode);
      }
      
      debugPrint('Bildirim durumu değiştirildi: $notificationId -> $isActive');
    } catch (e) {
      debugPrint('Bildirim durumu değiştirme hatası: $e');
    }
  }

  /// Okunmamış bildirim sayısını al
  static int getUnreadCount() {
    return _notifications.where((n) => !n.isRead).length;
  }

  /// Aktif bildirim sayısını al
  static int getActiveCount() {
    return _notifications.where((n) => n.isActive).length;
  }

  /// Bildirimleri al
  static List<NotificationItem> getNotifications() {
    return List.from(_notifications);
  }

  /// Yükleniyor mu?
  static bool get isLoading => _isLoading;

  /// State güncelleme fonksiyonu (gerçek uygulamada Provider/Bloc kullanılır)
  static void setState(VoidCallback fn) {
    fn();
  }
}

/// Bildirim Türleri
enum NotificationType {
  medication,
  appointment,
  health,
  system,
  reminder,
}

/// Bildirim Modeli
class NotificationItem {
  final String id;
  final String title;
  final String body;
  final NotificationType type;
  final Map<String, dynamic> data;
  final DateTime createdAt;
  final DateTime? scheduledTime;
  final bool isRead;
  final bool isActive;

  const NotificationItem({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    required this.data,
    required this.createdAt,
    this.scheduledTime,
    this.isRead = false,
    this.isActive = true,
  });

  factory NotificationItem.fromFirebase(Map<String, dynamic> data) {
    return NotificationItem(
      id: data['id'] ?? '',
      title: data['title'] ?? '',
      body: data['body'] ?? '',
      type: NotificationType.values.firstWhere(
        (e) => e.name == data['type'],
        orElse: () => NotificationType.system,
      ),
      data: Map<String, dynamic>.from(data['data'] ?? {}),
      createdAt: (data['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
      scheduledTime: (data['scheduledTime'] as Timestamp?)?.toDate(),
      isRead: data['isRead'] ?? false,
      isActive: data['isActive'] ?? true,
    );
  }

  factory NotificationItem.fromLocal(dynamic notification) {
    return NotificationItem(
      id: notification.id.toString(),
      title: notification.title ?? '',
      body: notification.body ?? '',
      type: NotificationType.reminder,
      data: {},
      createdAt: DateTime.now(),
      isRead: false,
      isActive: true,
    );
  }

  NotificationItem copyWith({
    String? id,
    String? title,
    String? body,
    NotificationType? type,
    Map<String, dynamic>? data,
    DateTime? createdAt,
    DateTime? scheduledTime,
    bool? isRead,
    bool? isActive,
  }) {
    return NotificationItem(
      id: id ?? this.id,
      title: title ?? this.title,
      body: body ?? this.body,
      type: type ?? this.type,
      data: data ?? this.data,
      createdAt: createdAt ?? this.createdAt,
      scheduledTime: scheduledTime ?? this.scheduledTime,
      isRead: isRead ?? this.isRead,
      isActive: isActive ?? this.isActive,
    );
  }

  /// Bildirim türüne göre ikon
  IconData get icon {
    switch (type) {
      case NotificationType.medication:
        return Icons.medication_rounded;
      case NotificationType.appointment:
        return Icons.calendar_today_rounded;
      case NotificationType.health:
        return Icons.health_and_safety_rounded;
      case NotificationType.system:
        return Icons.info_rounded;
      case NotificationType.reminder:
        return Icons.alarm_rounded;
    }
  }

  /// Bildirim türüne göre renk
  Color get color {
    switch (type) {
      case NotificationType.medication:
        return Colors.green;
      case NotificationType.appointment:
        return Colors.blue;
      case NotificationType.health:
        return Colors.orange;
      case NotificationType.system:
        return Colors.grey;
      case NotificationType.reminder:
        return Colors.purple;
    }
  }

  /// Zaman formatı
  String get formattedTime {
    final now = DateTime.now();
    final difference = now.difference(createdAt);
    
    if (difference.inDays > 0) {
      return '${difference.inDays} gün önce';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} saat önce';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} dakika önce';
    } else {
      return 'Az önce';
    }
  }
}

/// Günlük Sağlık Hatırlatmaları Yöneticisi
class DailyHealthReminders {
  static final List<HealthReminder> _dailyReminders = [
    HealthReminder(
      id: 'water_reminder_1',
      time: '09:45',
      emoji: '💧',
      title: 'Su İçme Hatırlatması',
      description: 'Günlük su ihtiyacınızı karşılamak için su içmeyi unutmayın!',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'vitamin_d_1',
      time: '10:30',
      emoji: '☀️',
      title: 'D Vitamini Hatırlatması',
      description: 'Güneş ışığı almak için dışarı çıkın veya D vitamini takviyesi alın.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'snack_reminder',
      time: '11:45',
      emoji: '🍎',
      title: 'Ara Öğün (Meyve) Hatırlatması',
      description: 'Sağlıklı bir ara öğün için meyve yemeyi unutmayın!',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'walking_reminder',
      time: '13:30',
      emoji: '👟',
      title: 'Yürüyüş Hatırlatması',
      description: 'Günlük yürüyüşünüzü yapmak için zaman ayırın.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'eye_break',
      time: '14:20',
      emoji: '👀',
      title: 'Göz Molası (20-20-20 kuralı)',
      description: '20 dakikada bir, 20 saniye boyunca 20 metre uzağa bakın.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'vitamin_d_2',
      time: '15:00',
      emoji: '☀️',
      title: 'D Vitamini Hatırlatması (2. sefer)',
      description: 'İkinci D vitamini dozunuz için zaman geldi.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'stretching_reminder',
      time: '16:10',
      emoji: '💎',
      title: 'Esneme/Duruş Hatırlatması',
      description: 'Vücudunuzu esnetin ve duruşunuzu düzeltin.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'morale_reminder',
      time: '17:00',
      emoji: '✨',
      title: 'Moral Hatırlatması',
      description: 'Gününüzün nasıl geçtiğini düşünün ve kendinizi ödüllendirin.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'breathing_exercise',
      time: '18:30',
      emoji: '💎',
      title: 'Nefes Egzersizi Hatırlatması',
      description: 'Rahatlamak için derin nefes egzersizleri yapın.',
      type: NotificationType.health,
    ),
    HealthReminder(
      id: 'day_end_reminder',
      time: '20:30',
      emoji: '💎',
      title: 'Gün Kapanışı Hatırlatması',
      description: 'Günü değerlendirin ve yarın için hazırlık yapın.',
      type: NotificationType.health,
    ),
  ];

  /// Günlük sağlık hatırlatmalarını yükle
  static Future<void> loadDailyHealthReminders() async {
    for (final reminder in _dailyReminders) {
      await GlobalNotificationManager.addHealthReminder(
        id: reminder.id,
        time: reminder.time,
        emoji: reminder.emoji,
        title: reminder.title,
        description: reminder.description,
      );
    }
  }

  /// Günlük hatırlatmaları al
  static List<HealthReminder> getDailyReminders() {
    return List.from(_dailyReminders);
  }
}

/// Sağlık Hatırlatması Modeli
class HealthReminder {
  final String id;
  final String time;
  final String emoji;
  final String title;
  final String description;
  final NotificationType type;

  HealthReminder({
    required this.id,
    required this.time,
    required this.emoji,
    required this.title,
    required this.description,
    required this.type,
  });
}
