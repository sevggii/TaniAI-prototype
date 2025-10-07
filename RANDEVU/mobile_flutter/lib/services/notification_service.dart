import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;
import 'dart:typed_data';

/// Mobil Bildirim Servisi
/// Saatlik ilaç hatırlatmaları ve diğer bildirimler için
class NotificationService {
  static final FlutterLocalNotificationsPlugin _notifications = 
      FlutterLocalNotificationsPlugin();
  
  static bool _initialized = false;

  /// Bildirim servisini başlat
  static Future<void> initialize() async {
    if (_initialized) return;
    
    // Timezone verilerini yükle
    tz.initializeTimeZones();
    
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    
    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
          requestAlertPermission: true,
          requestBadgePermission: true,
          requestSoundPermission: true,
        );
    
    const InitializationSettings initializationSettings =
        InitializationSettings(
          android: initializationSettingsAndroid,
          iOS: initializationSettingsIOS,
        );
    
    await _notifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
    
    _initialized = true;
  }

  /// Bildirime tıklandığında çağrılır
  static void _onNotificationTapped(NotificationResponse response) {
    // Bildirime tıklandığında yapılacak işlemler
    debugPrint('Bildirime tıklandı: ${response.payload}');
  }

  /// İlaç hatırlatma bildirimi ayarla
  static Future<void> scheduleMedicationReminder({
    required int id,
    required String medicationName,
    required String dosage,
    required DateTime scheduledTime,
    required String frequency, // 'günde 1 kez', 'günde 2 kez', vb.
  }) async {
    await initialize();
    
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'medication_reminders',
      'İlaç Hatırlatmaları',
      channelDescription: 'Saatlik ilaç hatırlatma bildirimleri',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      sound: const RawResourceAndroidNotificationSound('notification_sound'),
      vibrationPattern: Int64List.fromList([0, 1000, 500, 1000]),
      enableLights: true,
      color: const Color(0xFF2196F3),
    );
    
    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      sound: 'notification_sound.aiff',
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    final NotificationDetails platformChannelSpecifics =
        NotificationDetails(
          android: androidPlatformChannelSpecifics,
          iOS: iOSPlatformChannelSpecifics,
        );
    
    await _notifications.zonedSchedule(
      id,
      'İlaç Zamanı 💊',
      '$medicationName ($dosage) almayı unutmayın!',
      tz.TZDateTime.from(scheduledTime, tz.local),
      platformChannelSpecifics,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: 'medication_$id',
    );
  }

  /// Günlük tekrarlayan ilaç hatırlatması ayarla
  static Future<void> scheduleDailyMedicationReminder({
    required int id,
    required String medicationName,
    required String dosage,
    required TimeOfDay time,
    required String frequency,
  }) async {
    await initialize();
    
    final now = DateTime.now();
    var scheduledDate = DateTime(
      now.year,
      now.month,
      now.day,
      time.hour,
      time.minute,
    );
    
    // Eğer zaman geçmişse, yarın için ayarla
    if (scheduledDate.isBefore(now)) {
      scheduledDate = scheduledDate.add(const Duration(days: 1));
    }
    
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'daily_medication_reminders',
      'Günlük İlaç Hatırlatmaları',
      channelDescription: 'Günlük tekrarlayan ilaç hatırlatma bildirimleri',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      sound: RawResourceAndroidNotificationSound('notification_sound'),
      vibrationPattern: Int64List.fromList([0, 1000, 500, 1000]),
      enableLights: true,
      color: Color(0xFF4CAF50),
    );
    
    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      sound: 'notification_sound.aiff',
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    final NotificationDetails platformChannelSpecifics =
        NotificationDetails(
          android: androidPlatformChannelSpecifics,
          iOS: iOSPlatformChannelSpecifics,
        );
    
    await _notifications.zonedSchedule(
      id,
      'İlaç Zamanı 💊',
      '$medicationName ($dosage) almayı unutmayın!',
      tz.TZDateTime.from(scheduledDate, tz.local),
      platformChannelSpecifics,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: 'daily_medication_$id',
    );
  }

  /// Randevu hatırlatma bildirimi ayarla
  static Future<void> scheduleAppointmentReminder({
    required int id,
    required String doctorName,
    required String clinicName,
    required DateTime appointmentTime,
    required int reminderMinutesBefore,
  }) async {
    await initialize();
    
    final reminderTime = appointmentTime.subtract(
      Duration(minutes: reminderMinutesBefore),
    );
    
    if (reminderTime.isBefore(DateTime.now())) {
      return; // Geçmiş zaman için bildirim ayarlama
    }
    
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'appointment_reminders',
      'Randevu Hatırlatmaları',
      channelDescription: 'Randevu hatırlatma bildirimleri',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      sound: RawResourceAndroidNotificationSound('notification_sound'),
      vibrationPattern: Int64List.fromList([0, 1000, 500, 1000]),
      enableLights: true,
      color: Color(0xFFFF9800),
    );
    
    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      sound: 'notification_sound.aiff',
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    final NotificationDetails platformChannelSpecifics =
        NotificationDetails(
          android: androidPlatformChannelSpecifics,
          iOS: iOSPlatformChannelSpecifics,
        );
    
    await _notifications.zonedSchedule(
      id,
      'Randevu Hatırlatması 📅',
      '$reminderMinutesBefore dakika sonra $doctorName ile $clinicName randevunuz var!',
      tz.TZDateTime.from(reminderTime, tz.local),
      platformChannelSpecifics,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: 'appointment_$id',
    );
  }

  /// Genel sağlık hatırlatması
  static Future<void> scheduleHealthReminder({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledTime,
  }) async {
    await initialize();
    
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'health_reminders',
      'Sağlık Hatırlatmaları',
      channelDescription: 'Genel sağlık hatırlatma bildirimleri',
      importance: Importance.defaultImportance,
      priority: Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
      sound: RawResourceAndroidNotificationSound('notification_sound'),
      vibrationPattern: Int64List.fromList([0, 500, 250, 500]),
      enableLights: true,
      color: Color(0xFF9C27B0),
    );
    
    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      sound: 'notification_sound.aiff',
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    final NotificationDetails platformChannelSpecifics =
        NotificationDetails(
          android: androidPlatformChannelSpecifics,
          iOS: iOSPlatformChannelSpecifics,
        );
    
    await _notifications.zonedSchedule(
      id,
      title,
      body,
      tz.TZDateTime.from(scheduledTime, tz.local),
      platformChannelSpecifics,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: 'health_$id',
    );
  }

  /// Bekleyen bildirimleri iptal et
  static Future<void> cancelNotification(int id) async {
    await _notifications.cancel(id);
  }

  /// Tüm bildirimleri iptal et
  static Future<void> cancelAllNotifications() async {
    await _notifications.cancelAll();
  }

  /// Bekleyen bildirimleri listele
  static Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _notifications.pendingNotificationRequests();
  }

  /// Bildirim izinlerini kontrol et
  static Future<bool> areNotificationsEnabled() async {
    final result = await _notifications.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>()?.areNotificationsEnabled();
    return result ?? false;
  }

  /// Bildirim izinlerini iste
  static Future<bool> requestNotificationPermissions() async {
    final androidImplementation = _notifications.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    
    final granted = await androidImplementation?.requestNotificationsPermission();
    return granted ?? false;
  }

  /// Anında local bildirim göster
  static Future<void> showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    await initialize();
    
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'instant_notifications',
      'Anında Bildirimler',
      channelDescription: 'Anında gösterilen bildirimler',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      sound: RawResourceAndroidNotificationSound('notification_sound'),
      vibrationPattern: Int64List.fromList([0, 1000, 500, 1000]),
      enableLights: true,
      color: Color(0xFF2196F3),
    );
    
    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      sound: 'notification_sound.aiff',
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    final NotificationDetails platformChannelSpecifics =
        NotificationDetails(
          android: androidPlatformChannelSpecifics,
          iOS: iOSPlatformChannelSpecifics,
        );
    
    await _notifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      platformChannelSpecifics,
      payload: payload,
    );
  }
}

/// İlaç Hatırlatma Modeli
class MedicationReminder {
  final int id;
  final String medicationName;
  final String dosage;
  final TimeOfDay time;
  final String frequency;
  final bool isActive;
  final List<int> daysOfWeek; // 1-7 (Pazartesi-Pazar)

  const MedicationReminder({
    required this.id,
    required this.medicationName,
    required this.dosage,
    required this.time,
    required this.frequency,
    this.isActive = true,
    this.daysOfWeek = const [1, 2, 3, 4, 5, 6, 7], // Her gün
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'medicationName': medicationName,
      'dosage': dosage,
      'time': '${time.hour}:${time.minute}',
      'frequency': frequency,
      'isActive': isActive,
      'daysOfWeek': daysOfWeek,
    };
  }

  factory MedicationReminder.fromJson(Map<String, dynamic> json) {
    final timeParts = json['time'].split(':');
    return MedicationReminder(
      id: json['id'],
      medicationName: json['medicationName'],
      dosage: json['dosage'],
      time: TimeOfDay(
        hour: int.parse(timeParts[0]),
        minute: int.parse(timeParts[1]),
      ),
      frequency: json['frequency'],
      isActive: json['isActive'],
      daysOfWeek: List<int>.from(json['daysOfWeek']),
    );
  }
}

/// Bildirim Ayarları Modeli
class NotificationSettings {
  final bool medicationReminders;
  final bool appointmentReminders;
  final bool healthReminders;
  final bool soundEnabled;
  final bool vibrationEnabled;
  final bool lightsEnabled;
  final int reminderMinutesBefore;

  const NotificationSettings({
    this.medicationReminders = true,
    this.appointmentReminders = true,
    this.healthReminders = true,
    this.soundEnabled = true,
    this.vibrationEnabled = true,
    this.lightsEnabled = true,
    this.reminderMinutesBefore = 30,
  });

  Map<String, dynamic> toJson() {
    return {
      'medicationReminders': medicationReminders,
      'appointmentReminders': appointmentReminders,
      'healthReminders': healthReminders,
      'soundEnabled': soundEnabled,
      'vibrationEnabled': vibrationEnabled,
      'lightsEnabled': lightsEnabled,
      'reminderMinutesBefore': reminderMinutesBefore,
    };
  }

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    return NotificationSettings(
      medicationReminders: json['medicationReminders'] ?? true,
      appointmentReminders: json['appointmentReminders'] ?? true,
      healthReminders: json['healthReminders'] ?? true,
      soundEnabled: json['soundEnabled'] ?? true,
      vibrationEnabled: json['vibrationEnabled'] ?? true,
      lightsEnabled: json['lightsEnabled'] ?? true,
      reminderMinutesBefore: json['reminderMinutesBefore'] ?? 30,
    );
  }
}