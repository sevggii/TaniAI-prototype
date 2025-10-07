import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/notification_service.dart';
import '../../services/global_notification_manager.dart';

/// Bildirimler ve Alarm Sayfası
/// İlaç hatırlatmaları, randevu hatırlatmaları ve diğer bildirimler
class NotificationsPage extends StatefulWidget {
  final VoidCallback? onNotificationRead;
  
  const NotificationsPage({super.key, this.onNotificationRead});

  @override
  State<NotificationsPage> createState() => _NotificationsPageState();
}

class _NotificationsPageState extends State<NotificationsPage>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  List<NotificationItem> _notifications = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _loadData();
  }

  void _setupAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _animationController.forward();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    try {
      // Global bildirim yöneticisini başlat
      await GlobalNotificationManager.loadNotifications();
      
      // Günlük sağlık hatırlatmalarını yükle
      await DailyHealthReminders.loadDailyHealthReminders();
      
      // Bildirimleri al
      _notifications = GlobalNotificationManager.getNotifications();
      
      // Eğer bildirim yoksa örnek veriler ekle
      if (_notifications.isEmpty) {
        await _addSampleNotifications();
        _notifications = GlobalNotificationManager.getNotifications();
      }
      
    } catch (e) {
      debugPrint('Bildirimler yüklenirken hata: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _addSampleNotifications() async {
    // Örnek ilaç hatırlatmaları ekle
    await GlobalNotificationManager.addMedicationReminder(
      medicationName: 'Aspirin',
      dosage: '100mg',
      frequency: 'Günde 1 kez',
      time: const TimeOfDay(hour: 8, minute: 0),
    );
    
    await GlobalNotificationManager.addMedicationReminder(
      medicationName: 'Vitamin D',
      dosage: '1000 IU',
      frequency: 'Günde 1 kez',
      time: const TimeOfDay(hour: 20, minute: 0),
    );
    
    await GlobalNotificationManager.addMedicationReminder(
      medicationName: 'Metformin',
      dosage: '500mg',
      frequency: 'Günde 2 kez',
      time: const TimeOfDay(hour: 12, minute: 0),
    );
    
    // Örnek randevu hatırlatması ekle
    await GlobalNotificationManager.addAppointmentReminder(
      doctorName: 'Dr. Ahmet Yılmaz',
      clinicName: 'Kardiyoloji Kliniği',
      appointmentTime: DateTime.now().add(const Duration(days: 1)),
      reminderMinutesBefore: 30,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_rounded, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.orange.shade400, Colors.red.shade400],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.alarm_rounded,
                color: Colors.white,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Bildirimler & Alarmlar',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.orange.shade600,
        elevation: 0,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_rounded, color: Colors.white),
            onPressed: _showSettingsDialog,
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.orange.shade50,
              Colors.red.shade50,
              Colors.white,
            ],
            stops: const [0.0, 0.3, 1.0],
          ),
        ),
        child: SafeArea(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : FadeTransition(
                  opacity: _fadeAnimation,
                  child: SlideTransition(
                    position: _slideAnimation,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Özet Kartı
                          _buildSummaryCard(theme),
                          const SizedBox(height: 24),
                          
                          // İlaç Hatırlatmaları
                          _buildMedicationRemindersSection(theme),
                          const SizedBox(height: 24),
                          
                          // Bekleyen Bildirimler
                          _buildPendingNotificationsSection(theme),
                          const SizedBox(height: 24),
                          
                          // Hızlı Eylemler
                          _buildQuickActionsSection(theme),
                          const SizedBox(height: 20),
                        ],
                      ),
                    ),
                  ),
                ),
        ),
      ),
    );
  }

  Widget _buildSummaryCard(ThemeData theme) {
    final activeCount = _notifications.where((n) => n.isActive).length;
    final unreadCount = _notifications.where((n) => !n.isRead).length;
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.white,
            Colors.orange.shade50,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.orange.shade400, Colors.red.shade400],
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.alarm_rounded,
              color: Colors.white,
              size: 40,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Bildirim Özeti',
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.orange.shade800,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('Aktif Bildirim', activeCount, Colors.green),
              _buildStatItem('Okunmamış', unreadCount, Colors.blue),
              _buildStatItem('Toplam', _notifications.length, Colors.orange),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, int value, Color color) {
    return Column(
      children: [
        Text(
          value.toString(),
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildMedicationRemindersSection(ThemeData theme) {
    final medicationNotifications = _notifications.where((n) => n.type == NotificationType.medication).toList();
    
    return _buildSection(
      theme,
      'İlaç Hatırlatmaları',
      Icons.medication_rounded,
      medicationNotifications.isEmpty
          ? _buildEmptyState('Henüz ilaç hatırlatması eklenmemiş')
          : Column(
              children: medicationNotifications.map((notification) =>
                  _buildNotificationCard(theme, notification)).toList(),
            ),
    );
  }

  Widget _buildNotificationCard(ThemeData theme, NotificationItem notification) {
    return GestureDetector(
      onTap: () {
        // Bildirimi okundu olarak işaretle
        if (!notification.isRead) {
          GlobalNotificationManager.markAsRead(notification.id);
          _loadData(); // Listeyi yenile
          widget.onNotificationRead?.call(); // Ana sayfayı güncelle
          HapticFeedback.lightImpact();
        }
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: notification.isActive
              ? [notification.color.withOpacity(0.1), notification.color.withOpacity(0.05)]
              : [Colors.grey.shade50, Colors.grey.shade100],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: notification.isActive
              ? notification.color.withOpacity(0.3)
              : Colors.grey.shade200,
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: (notification.isActive ? notification.color : Colors.grey).withOpacity(0.2),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: notification.isActive
                    ? [notification.color, notification.color.withOpacity(0.8)]
                    : [Colors.grey.shade400, Colors.grey.shade600],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              notification.icon,
              color: Colors.white,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  notification.title,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: notification.isActive
                        ? notification.color
                        : Colors.grey.shade800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  notification.body,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.access_time_rounded,
                      size: 16,
                      color: Colors.grey.shade600,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      notification.formattedTime,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey.shade600,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Column(
            children: [
              Switch(
                value: notification.isActive,
                onChanged: (value) {
                  GlobalNotificationManager.toggleNotification(notification.id, value);
                  _loadData(); // Listeyi yenile
                  HapticFeedback.lightImpact();
                },
                activeColor: notification.color,
              ),
              if (!notification.isRead)
                Container(
                  margin: const EdgeInsets.only(top: 4),
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
            ],
          ),
        ],
      ),
    ),
    );
  }

  Widget _buildPendingNotificationsSection(ThemeData theme) {
    final pendingNotifications = _notifications.where((n) => !n.isRead).toList();
    
    return _buildSection(
      theme,
      'Bekleyen Bildirimler',
      Icons.schedule_rounded,
      pendingNotifications.isEmpty
          ? _buildEmptyState('Bekleyen bildirim yok')
          : Column(
              children: pendingNotifications.map((notification) =>
                  _buildNotificationCard(theme, notification)).toList(),
            ),
    );
  }


  Widget _buildQuickActionsSection(ThemeData theme) {
    return _buildSection(
      theme,
      'Hızlı Eylemler',
      Icons.flash_on_rounded,
      Row(
        children: [
          Expanded(
            child: _buildQuickActionButton(
              'Yeni Hatırlatma',
              Icons.add_rounded,
              Colors.green,
              () => _showAddReminderDialog(),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildQuickActionButton(
              'Tümünü İptal',
              Icons.cancel_rounded,
              Colors.red,
              () => _cancelAllNotifications(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton(String label, IconData icon, Color color, VoidCallback onPressed) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, color: Colors.white),
      label: Text(
        label,
        style: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  Widget _buildSection(ThemeData theme, String title, IconData icon, Widget content) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.orange.shade400, Colors.red.shade400],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(
                  icon,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  title,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          content,
        ],
      ),
    );
  }

  Widget _buildEmptyState(String message) {
    return Container(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Icon(
            Icons.notifications_off_rounded,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  void _showAddReminderDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Yeni İlaç Hatırlatması'),
        content: const Text('Bu özellik yakında eklenecek!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }

  void _cancelAllNotifications() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Tüm Bildirimleri İptal Et'),
        content: const Text('Tüm bekleyen bildirimleri iptal etmek istediğinizden emin misiniz?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () {
              NotificationService.cancelAllNotifications();
              _loadData();
              Navigator.pop(context);
              HapticFeedback.mediumImpact();
            },
            child: const Text('Evet, İptal Et'),
          ),
        ],
      ),
    );
  }

  void _showSettingsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Bildirim Ayarları'),
        content: const Text('Bildirim ayarları yakında eklenecek!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Tamam'),
          ),
        ],
      ),
    );
  }
}
