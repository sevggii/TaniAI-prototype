import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

class NotificationTestPage extends StatefulWidget {
  const NotificationTestPage({super.key});

  @override
  State<NotificationTestPage> createState() => _NotificationTestPageState();
}

class _NotificationTestPageState extends State<NotificationTestPage> {
  final FlutterLocalNotificationsPlugin _notifications = FlutterLocalNotificationsPlugin();
  bool _isInitialized = false;
  bool _hasPermission = false;
  String _status = '';

  @override
  void initState() {
    super.initState();
    _initializeNotifications();
  }

  Future<void> _initializeNotifications() async {
    try {
      setState(() => _status = '🔄 Initializing...');
      
      // Initialize timezone
      tz.initializeTimeZones();
      tz.setLocalLocation(tz.getLocation('Europe/Istanbul'));
      
      // Android settings
      const AndroidInitializationSettings androidSettings = 
          AndroidInitializationSettings('@mipmap/ic_launcher');
      
      // iOS settings
      const DarwinInitializationSettings iosSettings = DarwinInitializationSettings(
        requestAlertPermission: true,
        requestBadgePermission: true,
        requestSoundPermission: true,
      );

      const InitializationSettings initSettings = InitializationSettings(
        android: androidSettings,
        iOS: iosSettings,
      );

      await _notifications.initialize(initSettings);
      
      // Create Android channel
      await _createAndroidChannel();
      
      setState(() {
        _isInitialized = true;
        _status = '✅ Initialized successfully';
      });
      
      await _checkPermissions();
      
    } catch (e) {
      setState(() => _status = '❌ Initialization failed: $e');
    }
  }

  Future<void> _createAndroidChannel() async {
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

  Future<void> _checkPermissions() async {
    try {
      final AndroidFlutterLocalNotificationsPlugin? androidImplementation =
          _notifications.resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
      
      final bool? granted = await androidImplementation?.requestNotificationsPermission();
      
      setState(() {
        _hasPermission = granted ?? false;
        _status = _hasPermission ? '✅ Permission granted' : '❌ Permission denied';
      });
    } catch (e) {
      setState(() => _status = '❌ Permission check failed: $e');
    }
  }

  Future<void> _testImmediateNotification() async {
    try {
      setState(() => _status = '🔄 Sending test notification...');
      
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

      await _notifications.show(
        999,
        'Test Bildirimi',
        'Bu bir test bildirimidir!',
        notificationDetails,
      );
      
      setState(() => _status = '✅ Test notification sent!');
      
    } catch (e) {
      setState(() => _status = '❌ Test notification failed: $e');
    }
  }

  Future<void> _testScheduledNotification() async {
    try {
      setState(() => _status = '🔄 Scheduling test notification...');
      
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

      // Schedule for 10 seconds from now
      final scheduledDate = DateTime.now().add(const Duration(seconds: 10));
      final tzScheduledDate = tz.TZDateTime.from(scheduledDate, tz.local);
      
      await _notifications.zonedSchedule(
        998,
        'Zamanlanmış Test',
        'Bu bildirim 10 saniye sonra gelecek!',
        tzScheduledDate,
        notificationDetails,
        uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.time,
      );
      
      setState(() => _status = '✅ Scheduled notification for 10 seconds from now!');
      
    } catch (e) {
      setState(() => _status = '❌ Scheduled notification failed: $e');
    }
  }

  Future<void> _cancelAllNotifications() async {
    try {
      setState(() => _status = '🔄 Cancelling all notifications...');
      
      await _notifications.cancelAll();
      
      setState(() => _status = '✅ All notifications cancelled!');
      
    } catch (e) {
      setState(() => _status = '❌ Cancel failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bildirim Test'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Bildirim Durumu',
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _status,
                      style: theme.textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Test Butonları',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        onPressed: _isInitialized ? _testImmediateNotification : null,
                        icon: const Icon(Icons.notifications_active),
                        label: const Text('Anında Test Bildirimi'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        onPressed: _isInitialized ? _testScheduledNotification : null,
                        icon: const Icon(Icons.schedule),
                        label: const Text('10 Saniye Sonra Test'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        onPressed: _isInitialized ? _checkPermissions : null,
                        icon: const Icon(Icons.security),
                        label: const Text('İzinleri Kontrol Et'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        onPressed: _isInitialized ? _cancelAllNotifications : null,
                        icon: const Icon(Icons.cancel),
                        label: const Text('Tüm Bildirimleri İptal Et'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            Card(
              color: Colors.blue.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Kontrol Listesi:',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue.shade800,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text('1. Telefon ayarları > Bildirimler > Tanial Randevu'),
                    const Text('2. Bildirimlerin açık olduğunu kontrol edin'),
                    const Text('3. Uygulama arka planda çalışabiliyor mu?'),
                    const Text('4. Batarya optimizasyonu kapalı mı?'),
                    const Text('5. Test bildirimlerini deneyin'),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
