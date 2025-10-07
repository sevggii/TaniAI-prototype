import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/notification_service.dart';

/// İlaç Hatırlatma Sayfası
/// İlaç programı ve hatırlatma ayarları
class MedicationReminderPage extends StatefulWidget {
  const MedicationReminderPage({super.key});

  @override
  State<MedicationReminderPage> createState() => _MedicationReminderPageState();
}

class _MedicationReminderPageState extends State<MedicationReminderPage>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  List<MedicationReminder> _reminders = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _loadReminders();
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

  Future<void> _loadReminders() async {
    setState(() => _isLoading = true);
    
    try {
      // Örnek ilaç hatırlatmaları (gerçek uygulamada veritabanından gelecek)
      _reminders = [
        const MedicationReminder(
          id: 1,
          medicationName: 'Aspirin',
          dosage: '100mg',
          time: TimeOfDay(hour: 8, minute: 0),
          frequency: 'Günde 1 kez',
        ),
        const MedicationReminder(
          id: 2,
          medicationName: 'Vitamin D',
          dosage: '1000 IU',
          time: TimeOfDay(hour: 20, minute: 0),
          frequency: 'Günde 1 kez',
        ),
        const MedicationReminder(
          id: 3,
          medicationName: 'Metformin',
          dosage: '500mg',
          time: TimeOfDay(hour: 12, minute: 0),
          frequency: 'Günde 2 kez',
        ),
      ];
      
    } catch (e) {
      debugPrint('İlaç hatırlatmaları yüklenirken hata: $e');
    } finally {
      setState(() => _isLoading = false);
    }
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
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.green.shade400, Colors.teal.shade400],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.medication_rounded,
                color: Colors.white,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'İlaç Hatırlatmaları',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.green.shade600,
        elevation: 0,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.add_rounded, color: Colors.white),
            onPressed: _showAddReminderDialog,
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.green.shade50,
              Colors.teal.shade50,
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
                          
                          // İlaç Hatırlatmaları Listesi
                          _buildRemindersList(theme),
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
    final activeReminders = _reminders.where((r) => r.isActive).length;
    final nextReminder = _getNextReminder();
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.white,
            Colors.green.shade50,
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
                colors: [Colors.green.shade400, Colors.teal.shade400],
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.medication_rounded,
              color: Colors.white,
              size: 40,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'İlaç Hatırlatma Özeti',
            style: theme.textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.green.shade800,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('Aktif Hatırlatma', activeReminders, Colors.green),
              _buildStatItem('Toplam İlaç', _reminders.length, Colors.blue),
              _buildStatItem('Sonraki', nextReminder != null ? 1 : 0, Colors.orange),
            ],
          ),
          if (nextReminder != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: Colors.orange.shade200,
                  width: 1,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.schedule_rounded,
                    color: Colors.orange.shade600,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Sonraki Hatırlatma',
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.orange.shade700,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        Text(
                          '${nextReminder.medicationName} - ${_formatTime(nextReminder.time)}',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.orange.shade800,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
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

  Widget _buildRemindersList(ThemeData theme) {
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
                    colors: [Colors.green.shade400, Colors.teal.shade400],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.list_rounded,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Text(
                  'İlaç Hatırlatmaları',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _reminders.isEmpty
              ? _buildEmptyState()
              : Column(
                  children: _reminders.map((reminder) =>
                      _buildReminderCard(theme, reminder)).toList(),
                ),
        ],
      ),
    );
  }

  Widget _buildReminderCard(ThemeData theme, MedicationReminder reminder) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: reminder.isActive
              ? [Colors.green.shade50, Colors.green.shade100]
              : [Colors.grey.shade50, Colors.grey.shade100],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: reminder.isActive
              ? Colors.green.shade200
              : Colors.grey.shade200,
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: (reminder.isActive ? Colors.green : Colors.grey).withOpacity(0.2),
            blurRadius: 8,
            offset: const Offset(0, 4),
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
                    colors: reminder.isActive
                        ? [Colors.green.shade400, Colors.green.shade600]
                        : [Colors.grey.shade400, Colors.grey.shade600],
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.medication_rounded,
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
                      reminder.medicationName,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: reminder.isActive
                            ? Colors.green.shade800
                            : Colors.grey.shade800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${reminder.dosage} - ${reminder.frequency}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              Switch(
                value: reminder.isActive,
                onChanged: (value) {
                  setState(() {
                    _reminders = _reminders.map((r) {
                      if (r.id == reminder.id) {
                        return MedicationReminder(
                          id: r.id,
                          medicationName: r.medicationName,
                          dosage: r.dosage,
                          time: r.time,
                          frequency: r.frequency,
                          isActive: value,
                          daysOfWeek: r.daysOfWeek,
                        );
                      }
                      return r;
                    }).toList();
                  });
                  
                  if (value) {
                    // Hatırlatmayı etkinleştir
                    NotificationService.scheduleDailyMedicationReminder(
                      id: reminder.id,
                      medicationName: reminder.medicationName,
                      dosage: reminder.dosage,
                      time: reminder.time,
                      frequency: reminder.frequency,
                    );
                  } else {
                    // Hatırlatmayı iptal et
                    NotificationService.cancelNotification(reminder.id);
                  }
                  
                  HapticFeedback.lightImpact();
                },
                activeColor: Colors.green.shade600,
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Zaman ve Günler
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Colors.grey.shade200,
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.access_time_rounded,
                      color: Colors.green.shade600,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Hatırlatma Zamanı',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.green.shade700,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  _formatTime(reminder.time),
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.green.shade800,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(
                      Icons.calendar_today_rounded,
                      color: Colors.blue.shade600,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Günler',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.blue.shade700,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  _formatDaysOfWeek(reminder.daysOfWeek),
                  style: TextStyle(
                    fontSize: 15,
                    color: Colors.blue.shade800,
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Eylem Butonları
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => _editReminder(reminder),
                  icon: const Icon(Icons.edit_rounded),
                  label: const Text('Düzenle'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.blue.shade600,
                    side: BorderSide(color: Colors.blue.shade300),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () => _deleteReminder(reminder),
                  icon: const Icon(Icons.delete_rounded),
                  label: const Text('Sil'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.red.shade600,
                    side: BorderSide(color: Colors.red.shade300),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Icon(
            Icons.medication_outlined,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            'Henüz ilaç hatırlatması eklenmemiş',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'Yeni hatırlatma eklemek için + butonuna basın',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  MedicationReminder? _getNextReminder() {
    final now = DateTime.now();
    final currentTime = TimeOfDay.fromDateTime(now);
    
    final activeReminders = _reminders.where((r) => r.isActive).toList();
    if (activeReminders.isEmpty) return null;
    
    // Bugün için sonraki hatırlatmayı bul
    for (final reminder in activeReminders) {
      if (reminder.time.hour > currentTime.hour ||
          (reminder.time.hour == currentTime.hour && reminder.time.minute > currentTime.minute)) {
        return reminder;
      }
    }
    
    // Bugün için hatırlatma yoksa, yarın için ilkini döndür
    return activeReminders.first;
  }

  String _formatTime(TimeOfDay time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  String _formatDaysOfWeek(List<int> days) {
    const dayNames = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
    
    if (days.length == 7) {
      return 'Her gün';
    }
    
    return days.map((day) => dayNames[day - 1]).join(', ');
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

  void _editReminder(MedicationReminder reminder) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('İlaç Hatırlatmasını Düzenle'),
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

  void _deleteReminder(MedicationReminder reminder) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('İlaç Hatırlatmasını Sil'),
        content: Text('${reminder.medicationName} hatırlatmasını silmek istediğinizden emin misiniz?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () {
              setState(() {
                _reminders.removeWhere((r) => r.id == reminder.id);
              });
              NotificationService.cancelNotification(reminder.id);
              Navigator.pop(context);
              HapticFeedback.mediumImpact();
            },
            child: const Text('Sil'),
          ),
        ],
      ),
    );
  }
}
