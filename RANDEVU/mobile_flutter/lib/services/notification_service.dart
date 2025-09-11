import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

/// Friendly, warm and humorous notification service for wellbeing reminders
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();
  NotificationConfig? _config;
  final Map<String, List<String>> _usedMessages = {}; // Track used messages per category

  /// Initialize the notification service
  Future<void> initialize() async {
    print('🔔 Initializing notification service...');
    
    // Initialize timezone data
    tz.initializeTimeZones();
    
    // Set default timezone to Istanbul
    tz.setLocalLocation(tz.getLocation('Europe/Istanbul'));
    print('🌍 Timezone set to: Europe/Istanbul');

    // Android initialization settings
    const AndroidInitializationSettings androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    
    // iOS initialization settings
    const DarwinInitializationSettings iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    // Combined initialization settings
    const InitializationSettings initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    // Initialize the plugin
    await _notifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
    print('✅ Notification plugin initialized');

    // Create Android notification channel
    await _createAndroidChannel();

    // Load notification configuration
    await _loadConfig();
    print('📋 Notification config loaded');
  }

  /// Create Android notification channel
  Future<void> _createAndroidChannel() async {
    if (Platform.isAndroid) {
      const AndroidNotificationChannel channel = AndroidNotificationChannel(
        'wellbeing_reminders',
        'Wellbeing Reminders',
        description: 'Friendly reminders for your daily wellbeing activities',
        importance: Importance.high,
        playSound: true,
        enableVibration: true,
      );

      await _notifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);
    }
  }

  /// Load notification configuration from JSON asset
  Future<void> _loadConfig() async {
    try {
      final String jsonString = await rootBundle.loadString('assets/notifications_config.json');
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      _config = NotificationConfig.fromJson(jsonData);
    } catch (e) {
      debugPrint('Error loading notification config: $e');
    }
  }

  /// Handle notification tap
  void _onNotificationTapped(NotificationResponse response) {
    final String? payload = response.payload;
    if (payload != null) {
      final Map<String, dynamic> data = json.decode(payload);
      final String action = data['action'] ?? 'OPEN_APP';
      
      switch (action) {
        case 'OPEN_APP':
          // App will be opened automatically
          break;
        case 'SNOOZE_30M':
          _snoozeNotification(data['id']);
          break;
        case 'MARK_DONE':
          _markNotificationDone(data['id']);
          break;
      }
    }
  }

  /// Schedule all notifications based on configuration
  Future<void> scheduleAllNotifications() async {
    print('📅 Starting to schedule all notifications...');
    
    if (_config == null) {
      print('❌ Notification config not loaded');
      debugPrint('Notification config not loaded');
      return;
    }

    print('📋 Config loaded: ${_config!.notifications.length} notifications found');

    // Cancel existing notifications first
    await cancelAllNotifications();
    print('🗑️ Existing notifications cancelled');

    int scheduledCount = 0;
    for (final notification in _config!.notifications) {
      print('⏰ Scheduling notification: ${notification.category} at ${notification.time}');
      await _scheduleNotification(notification);
      scheduledCount++;
    }

    print('✅ All wellbeing notifications scheduled! 🌟 Total: $scheduledCount');
    debugPrint('All wellbeing notifications scheduled! 🌟');
  }

  /// Schedule a single notification
  Future<void> _scheduleNotification(NotificationItem item) async {
    if (_config == null) return;

    // Parse time
    final timeParts = item.time.split(':');
    final hour = int.parse(timeParts[0]);
    final minute = int.parse(timeParts[1]);

    // Calculate jitter (±15 minutes by default)
    final jitter = _config!.jitterMinutes;
    final randomJitter = Random().nextInt(jitter * 2 + 1) - jitter;
    final scheduledMinute = minute + randomJitter;

    // Check if time falls within DND period
    if (_isWithinDNDPeriod(hour, scheduledMinute)) {
      debugPrint('Skipping notification at $hour:${scheduledMinute.toString().padLeft(2, '0')} (DND period)');
      return;
    }

    // Schedule for each day of the week
    for (final dayName in _config!.days) {
      final dayOfWeek = _getDayOfWeek(dayName);
      final scheduledTime = _getNextScheduledTime(dayOfWeek, hour, scheduledMinute);
      
      if (scheduledTime != null) {
        await _scheduleSingleNotification(
          id: _generateNotificationId(item, dayOfWeek),
          scheduledTime: scheduledTime,
          item: item,
        );
      }
    }
  }

  /// Schedule a single notification at specific time
  Future<void> _scheduleSingleNotification({
    required int id,
    required DateTime scheduledTime,
    required NotificationItem item,
  }) async {
    // Get random message from category
    final message = _getRandomMessage(item.category, item.messages);
    
    // Android notification details
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      'wellbeing_reminders',
      'Wellbeing Reminders',
      channelDescription: 'Friendly reminders for your daily wellbeing activities',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
      enableLights: true,
      enableVibration: true,
      playSound: true,
      actions: [
        AndroidNotificationAction('snooze', 'Snooze 30m', showsUserInterface: false),
        AndroidNotificationAction('done', 'Mark Done', showsUserInterface: false),
      ],
    );

    // iOS notification details
    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    // Combined notification details
    const NotificationDetails notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    // Create payload for actions
    final payload = json.encode({
      'id': id,
      'category': item.category,
      'action': 'OPEN_APP',
    });

    // Schedule the notification
    await _notifications.zonedSchedule(
      id,
      _getNotificationTitle(item.category),
      message,
      tz.TZDateTime.from(scheduledTime, tz.local),
      notificationDetails,
      payload: payload,
      uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
      matchDateTimeComponents: DateTimeComponents.time,
    );
  }

  /// Get random message from category, avoiding duplicates
  String _getRandomMessage(String category, List<String> messages) {
    // Initialize category if not exists
    if (!_usedMessages.containsKey(category)) {
      _usedMessages[category] = [];
    }

    // Get available messages (not used today)
    final availableMessages = messages.where((msg) => !_usedMessages[category]!.contains(msg)).toList();
    
    // If all messages used, reset the list
    if (availableMessages.isEmpty) {
      _usedMessages[category] = [];
      availableMessages.addAll(messages);
    }

    // Pick random message
    final selectedMessage = availableMessages[Random().nextInt(availableMessages.length)];
    _usedMessages[category]!.add(selectedMessage);

    return selectedMessage;
  }

  /// Get notification title based on category
  String _getNotificationTitle(String category) {
    switch (category) {
      case 'D_vitamini':
        return '🌞 D Vitamini Saati';
      case 'Su_icme':
        return '💧 Su Molası';
      case 'Ara_ogun_meyve':
        return '🍎 Vitamin Molası';
      case 'Yuruyus':
        return '👟 Hareket Zamanı';
      case 'Goz_202020':
        return '👀 Göz Molası';
      case 'Esneme_durus':
        return '🧘 Esneme Zamanı';
      case 'Moral':
        return '✨ Moral Zamanı';
      case 'Nefes':
        return '🌬️ Nefes Molası';
      case 'Gun_kapanisi':
        return '🌙 Gün Kapanışı';
      default:
        return '💖 Sağlık Hatırlatması';
    }
  }

  /// Check if time falls within Do Not Disturb period
  bool _isWithinDNDPeriod(int hour, int minute) {
    if (_config == null) return false;

    final dndStart = _config!.dndStart;
    final dndEnd = _config!.dndEnd;
    
    final startParts = dndStart.split(':');
    final endParts = dndEnd.split(':');
    
    final startHour = int.parse(startParts[0]);
    final startMinute = int.parse(startParts[1]);
    final endHour = int.parse(endParts[0]);
    final endMinute = int.parse(endParts[1]);

    final currentTime = hour * 60 + minute;
    final startTime = startHour * 60 + startMinute;
    final endTime = endHour * 60 + endMinute;

    // Handle overnight DND (e.g., 23:00 to 08:00)
    if (startTime > endTime) {
      return currentTime >= startTime || currentTime <= endTime;
    } else {
      return currentTime >= startTime && currentTime <= endTime;
    }
  }

  /// Get day of week from string
  int _getDayOfWeek(String dayName) {
    switch (dayName) {
      case 'Mon': return DateTime.monday;
      case 'Tue': return DateTime.tuesday;
      case 'Wed': return DateTime.wednesday;
      case 'Thu': return DateTime.thursday;
      case 'Fri': return DateTime.friday;
      case 'Sat': return DateTime.saturday;
      case 'Sun': return DateTime.sunday;
      default: return DateTime.monday;
    }
  }

  /// Get next scheduled time for a specific day
  DateTime? _getNextScheduledTime(int dayOfWeek, int hour, int minute) {
    final now = DateTime.now();
    final today = now.weekday;
    
    // Calculate days until target day
    int daysUntilTarget = (dayOfWeek - today) % 7;
    if (daysUntilTarget == 0) {
      // Same day - check if time has passed
      final targetTime = DateTime(now.year, now.month, now.day, hour, minute);
      if (targetTime.isBefore(now)) {
        daysUntilTarget = 7; // Next week
      }
    }

    return DateTime(now.year, now.month, now.day + daysUntilTarget, hour, minute);
  }

  /// Generate unique notification ID
  int _generateNotificationId(NotificationItem item, int dayOfWeek) {
    return item.hashCode + dayOfWeek;
  }

  /// Snooze notification by 30 minutes
  Future<void> _snoozeNotification(int notificationId) async {
    final snoozeTime = DateTime.now().add(const Duration(minutes: 30));
    
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      'wellbeing_reminders',
      'Wellbeing Reminders',
      channelDescription: 'Friendly reminders for your daily wellbeing activities',
      importance: Importance.high,
      priority: Priority.high,
    );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const NotificationDetails notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notifications.zonedSchedule(
      notificationId + 10000, // Add offset to avoid ID conflicts
      '💤 Snoozed Reminder',
      'Hatırlatma 30 dakika ertelendi 😴',
      tz.TZDateTime.from(snoozeTime, tz.local),
      notificationDetails,
      uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
    );
  }

  /// Mark notification as done
  void _markNotificationDone(int notificationId) {
    // You can implement tracking logic here
    debugPrint('Notification $notificationId marked as done ✅');
  }

  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    await _notifications.cancelAll();
    debugPrint('All notifications cancelled');
  }

  /// Request notification permissions
  Future<bool> requestPermissions() async {
    print('🔐 Requesting notification permissions...');
    
    if (Platform.isAndroid) {
      final AndroidFlutterLocalNotificationsPlugin? androidImplementation =
          _notifications.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      
      final bool? granted = await androidImplementation?.requestNotificationsPermission();
      print('📱 Android permission result: $granted');
      return granted ?? false;
    } else if (Platform.isIOS) {
      final bool? granted = await _notifications
          .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
          ?.requestPermissions(
            alert: true,
            badge: true,
            sound: true,
          );
      print('🍎 iOS permission result: $granted');
      return granted ?? false;
    }
    print('❌ Platform not supported for permissions');
    return false;
  }

  /// Check if notifications are enabled
  Future<bool> areNotificationsEnabled() async {
    if (Platform.isAndroid) {
      final AndroidFlutterLocalNotificationsPlugin? androidImplementation =
          _notifications.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      return await androidImplementation?.areNotificationsEnabled() ?? false;
    }
    return true; // iOS doesn't have this method
  }
}

/// Notification configuration model
class NotificationConfig {
  final String timezone;
  final String dndStart;
  final String dndEnd;
  final int jitterMinutes;
  final List<String> days;
  final List<NotificationItem> notifications;

  NotificationConfig({
    required this.timezone,
    required this.dndStart,
    required this.dndEnd,
    required this.jitterMinutes,
    required this.days,
    required this.notifications,
  });

  factory NotificationConfig.fromJson(Map<String, dynamic> json) {
    return NotificationConfig(
      timezone: json['timezone'] ?? 'Europe/Istanbul',
      dndStart: json['do_not_disturb']?['start'] ?? '23:00',
      dndEnd: json['do_not_disturb']?['end'] ?? '08:00',
      jitterMinutes: json['jitter_minutes'] ?? 15,
      days: List<String>.from(json['days'] ?? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']),
      notifications: (json['notifications'] as List)
          .map((item) => NotificationItem.fromJson(item))
          .toList(),
    );
  }
}

/// Individual notification item model
class NotificationItem {
  final String time;
  final String category;
  final List<String> messages;
  final int? weight;

  NotificationItem({
    required this.time,
    required this.category,
    required this.messages,
    this.weight,
  });

  factory NotificationItem.fromJson(Map<String, dynamic> json) {
    return NotificationItem(
      time: json['time'],
      category: json['category'],
      messages: List<String>.from(json['messages']),
      weight: json['weight'],
    );
  }
}
