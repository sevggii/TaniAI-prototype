/// İlaç Takibi Ana Sayfası
/// İlaç listesi, bugünkü ilaçlar ve özet bilgiler

import 'package:flutter/material.dart';
import '../../models/medication.dart';
import '../../services/medication_service.dart';
import '../../services/firebase_medication_service.dart';
import 'add_medication_page.dart';
import 'medication_detail_page.dart';

class MedicationPage extends StatefulWidget {
  const MedicationPage({super.key});

  @override
  State<MedicationPage> createState() => _MedicationPageState();
}

class _MedicationPageState extends State<MedicationPage> with TickerProviderStateMixin {
  late TabController _tabController;
  List<Medication> _medications = [];
  List<Medication> _medicationsDueToday = [];
  MedicationSummary? _summary;
  List<MedicationAlert> _alerts = [];
  bool _isLoading = true;
  
  // İlaç durumlarını takip etmek için
  Map<int, bool> _medicationTakenToday = {};
  Map<int, bool> _medicationSkippedToday = {};

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _initializeData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _initializeData() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Önce günlük verileri yükle
      await _loadDailyData();
      
      // Sonra API verilerini yükle
      await _loadData();
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showErrorSnackBar('Veriler yüklenirken hata oluştu: $e');
    }
  }

  Future<void> _loadDailyData() async {
    try {
      // Firebase'den günlük verileri yükle
      _medicationTakenToday = await FirebaseMedicationService.loadMedicationTaken();
      _medicationSkippedToday = await FirebaseMedicationService.loadMedicationSkipped();
    } catch (e) {
      print('Firebase load error: $e');
      // Hata durumunda boş map'ler kullan
      _medicationTakenToday.clear();
      _medicationSkippedToday.clear();
    }
  }

  Future<void> _loadData() async {
    try {
      final results = await Future.wait([
        MedicationService.getMedications(),
        MedicationService.getMedicationsDueToday(),
        MedicationService.getMedicationSummary(),
        MedicationService.getMedicationAlerts(),
      ]);

      setState(() {
        _medications = results[0] as List<Medication>;
        _medicationsDueToday = results[1] as List<Medication>;
        _summary = results[2] as MedicationSummary;
        _alerts = results[3] as List<MedicationAlert>;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      _showErrorSnackBar('Veriler yüklenirken hata oluştu: $e');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('İlaç Takibi'),
        backgroundColor: Colors.blue.shade600,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.add_rounded, color: Colors.white),
            onPressed: () async {
              final result = await Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const AddMedicationPage(),
                ),
              );
              if (result == true) {
                _loadData();
              }
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabs: const [
            Tab(text: 'Bugün'),
            Tab(text: 'Tüm İlaçlar'),
            Tab(text: 'Özet'),
          ],
        ),
      ),
      body: Container(
        color: Colors.grey.shade50,
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildTodayTab(),
            _buildAllMedicationsTab(),
            _buildSummaryTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildTodayTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Uyarılar
            if (_alerts.isNotEmpty) ...[
              _buildAlertsSection(),
              const SizedBox(height: 16),
            ],
            
                  // Bugünkü İlaçlar
                  _buildTodayMedicationsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildAllMedicationsTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: _medications.isEmpty
          ? _buildEmptyState()
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _medications.length,
              itemBuilder: (context, index) {
                final medication = _medications[index];
                return _buildMedicationCard(medication);
              },
            ),
    );
  }

  Widget _buildSummaryTab() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_summary == null) {
      return const Center(
        child: Text('Özet bilgileri yüklenemedi'),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSummaryCards(),
            const SizedBox(height: 16),
            _buildComplianceSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.amber.shade50, Colors.orange.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Colors.amber.shade200,
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.info_rounded,
                color: Colors.amber.shade600,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                'Bilgilendirmeler (${_alerts.length})',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.amber.shade700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ..._alerts.map((alert) => _buildAlertItem(alert)).toList(),
        ],
      ),
    );
  }

  Widget _buildAlertItem(MedicationAlert alert) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Colors.amber.shade200,
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(
            Icons.info_rounded,
            color: Colors.amber.shade600,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.title,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber.shade700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  alert.message,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade700,
                  ),
                ),
              ],
            ),
          ),
          if (alert.requiresAction)
            IconButton(
              icon: Icon(Icons.check_rounded, color: Colors.green.shade600, size: 24),
              onPressed: () async {
                await MedicationService.markAlertAsRead(alert.id);
                _loadData();
              },
            ),
        ],
      ),
    );
  }

  Widget _buildTodayMedicationsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Basit başlık
        Text(
          'Bugünkü İlaçlar',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        if (_medicationsDueToday.isEmpty)
          _buildEmptyTodayState()
        else
          ..._medicationsDueToday.map((medication) => _buildTodayMedicationCard(medication)).toList(),
      ],
    );
  }

  Widget _buildEmptyTodayState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green.shade50, Colors.green.shade100],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.green.withOpacity(0.2),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(
          color: Colors.green.shade200,
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.green.shade400, Colors.green.shade600],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(40),
              boxShadow: [
                BoxShadow(
                  color: Colors.green.withOpacity(0.3),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Icon(
              Icons.check_circle_rounded,
              size: 48,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            'Harika! 🎉',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.green.shade800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Bugünkü tüm ilaçlar alındı',
            style: TextStyle(
              fontSize: 16,
              color: Colors.green.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTodayMedicationCard(Medication medication) {
    final isTaken = _medicationTakenToday[medication.id] ?? false;
    final isSkipped = _medicationSkippedToday[medication.id] ?? false;
    final isCompleted = isTaken || isSkipped;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isCompleted 
            ? [Colors.green.shade50, Colors.green.shade100]
            : [Colors.white, Colors.blue.shade50],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: isCompleted 
              ? Colors.green.withOpacity(0.2)
              : Colors.blue.withOpacity(0.1),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(
          color: isCompleted 
            ? Colors.green.shade200
            : Colors.blue.shade100,
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // İlaç bilgisi - Estetik
            Row(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: isCompleted 
                        ? [Colors.green.shade400, Colors.green.shade600]
                        : [Colors.blue.shade400, Colors.blue.shade600],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: isCompleted 
                          ? Colors.green.withOpacity(0.3)
                          : Colors.blue.withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Icon(
                    Icons.medication_rounded,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        medication.medicationName,
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: isCompleted ? Colors.green.shade800 : Colors.grey.shade800,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${medication.dosageAmount} ${medication.dosageUnit.displayName}',
                        style: TextStyle(
                          fontSize: 15,
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isCompleted)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: isTaken 
                          ? [Colors.green.shade400, Colors.green.shade600]
                          : [Colors.orange.shade400, Colors.orange.shade600],
                      ),
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: isTaken 
                            ? Colors.green.withOpacity(0.3)
                            : Colors.orange.withOpacity(0.3),
                          blurRadius: 6,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Text(
                      isTaken ? '✓ Alındı' : '⏭ Atlandı',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
              ],
            ),
            
            // İlaç yenileme uyarısı - Yumuşak
            if (medication.isLowOnPills && !isCompleted) ...[
              const SizedBox(height: 16),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.amber.shade50, Colors.orange.shade50],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.amber.shade200,
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.amber.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade100,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.info_rounded,
                        color: Colors.amber.shade700,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'İlaç az kaldı! Yenileme zamanı',
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                          color: Colors.amber.shade800,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            
            // Estetik butonlar
            if (!isCompleted) ...[
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF4CAF50), Color(0xFF45A049)],
                        ),
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.green.withOpacity(0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        onPressed: () => _takeMedication(medication),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text(
                          'Aldım',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFF9800), Color(0xFFF57C00)],
                        ),
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.orange.withOpacity(0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        onPressed: () => _skipMedication(medication),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text(
                          'Atla',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ] else ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.grey.shade300,
                    width: 1,
                  ),
                ),
                child: TextButton(
                  onPressed: () => _undoMedication(medication),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: const Text(
                    'Geri Al',
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }


  Widget _buildQuickActionsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF4CAF50).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.flash_on_rounded,
                color: Color(0xFF4CAF50),
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Hızlı Aksiyonlar',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildQuickActionCard(
                'İlaç Ekle',
                Icons.add_rounded,
                const Color(0xFF4CAF50),
                () async {
                  final result = await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => const AddMedicationPage(),
                    ),
                  );
                  if (result == true) {
                    _loadData();
                  }
                },
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildQuickActionCard(
                'Geçmiş',
                Icons.history_rounded,
                const Color(0xFF2196F3),
                () {
                  // Geçmiş sayfasına git
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionCard(String title, IconData icon, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [color, color.withOpacity(0.8)],
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.3),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: Colors.white, size: 32),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMedicationCard(Medication medication) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Card(
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        child: InkWell(
          onTap: () async {
            final result = await Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => MedicationDetailPage(medication: medication),
              ),
            );
            if (result == true) {
              _loadData();
            }
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: _getStatusColor(medication.status).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.medication_rounded,
                        color: _getStatusColor(medication.status),
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            medication.medicationName,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          Text(
                            '${medication.dosageAmount} ${medication.dosageUnit.displayName} - ${medication.frequencyType.displayName}',
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.withOpacity(0.8),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: _getStatusColor(medication.status).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _getStatusColor(medication.status).withOpacity(0.3),
                          width: 1,
                        ),
                      ),
                      child: Text(
                        medication.status.displayName,
                        style: TextStyle(
                          fontSize: 12,
                          color: _getStatusColor(medication.status),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
                if (medication.remainingPills != null) ...[
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Icon(
                        Icons.inventory_2_rounded,
                        size: 16,
                        color: Colors.grey.withOpacity(0.6),
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Kalan: ${medication.remainingPills} adet',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.withOpacity(0.6),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.medication_rounded,
            size: 64,
            color: Colors.grey.withOpacity(0.6),
          ),
          const SizedBox(height: 16),
          Text(
            'Henüz ilaç eklenmemiş',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w500,
              color: Colors.grey.withOpacity(0.8),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'İlk ilacınızı eklemek için + butonuna tıklayın',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () async {
              final result = await Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => const AddMedicationPage(),
                ),
              );
              if (result == true) {
                _loadData();
              }
            },
            icon: const Icon(Icons.add_rounded),
            label: const Text('İlaç Ekle'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF4CAF50),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCards() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF4CAF50).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.analytics_rounded,
                color: Color(0xFF4CAF50),
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'İlaç Özeti',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.5,
          children: [
            _buildSummaryCard(
              'Toplam İlaç',
              _summary!.totalMedications.toString(),
              Icons.medication_rounded,
              const Color(0xFF4CAF50),
            ),
            _buildSummaryCard(
              'Aktif İlaç',
              _summary!.activeMedications.toString(),
              Icons.check_circle_rounded,
              const Color(0xFF2196F3),
            ),
            _buildSummaryCard(
              'Bugün Alınacak',
              _summary!.medicationsDueToday.toString(),
              Icons.today_rounded,
              const Color(0xFFFF9800),
            ),
            _buildSummaryCard(
              'Atlanan Doz',
              _summary!.missedDosesToday.toString(),
              Icons.warning_rounded,
              const Color(0xFFFF5722),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSummaryCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color, color.withOpacity(0.8)],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: Colors.white, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildComplianceSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF4CAF50).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.trending_up_rounded,
                color: Color(0xFF4CAF50),
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Uyum Oranı',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Genel Uyum',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    '95%', // Mock data
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.green.shade600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              LinearProgressIndicator(
                value: 0.95, // Mock data
                backgroundColor: Colors.grey.withOpacity(0.3),
                valueColor: AlwaysStoppedAnimation<Color>(Colors.green.shade600),
                minHeight: 8,
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildComplianceItem('Alınan', _summary!.activeMedications, Colors.green),
                  _buildComplianceItem('Atlanan', _summary!.missedDosesToday, Colors.red),
                  _buildComplianceItem('Geciken', 0, Colors.orange), // Mock data
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildComplianceItem(String label, int value, Color color) {
    return Column(
      children: [
        Text(
          value.toString(),
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.withOpacity(0.8),
          ),
        ),
      ],
    );
  }

  Color _getStatusColor(MedicationStatus status) {
    switch (status) {
      case MedicationStatus.active:
        return Colors.green;
      case MedicationStatus.paused:
        return Colors.orange;
      case MedicationStatus.completed:
        return Colors.blue;
      case MedicationStatus.discontinued:
        return Colors.red;
      case MedicationStatus.expired:
        return Colors.red;
    }
  }

  Future<void> _takeMedication(Medication medication) async {
    try {
      // API'ye kaydet
      await MedicationService.takeMedicationNow(medication.id);
      
      // UI'yi hemen güncelle
      setState(() {
        _medicationTakenToday[medication.id] = true;
        _medicationSkippedToday[medication.id] = false;
      });
      
      // Firebase'e kalıcı olarak kaydet
      await _saveToFirebase();
      
      // Geçmişe kaydet
      await FirebaseMedicationService.saveDailyHistory(
        medicationId: medication.id,
        medicationName: medication.medicationName,
        wasTaken: true,
        wasSkipped: false,
        timestamp: DateTime.now(),
      );
      
      _showSuccessSnackBar('${medication.medicationName} alındı olarak kaydedildi');
      
      // Arka planda verileri güncelle
      _loadData();
    } catch (e) {
      _showErrorSnackBar('İlaç kaydedilemedi: $e');
    }
  }

  Future<void> _skipMedication(Medication medication) async {
    try {
      // API'ye kaydet
      await MedicationService.skipMedication(medication.id);
      
      // UI'yi hemen güncelle
      setState(() {
        _medicationSkippedToday[medication.id] = true;
        _medicationTakenToday[medication.id] = false;
      });
      
      // Firebase'e kalıcı olarak kaydet
      await _saveToFirebase();
      
      // Geçmişe kaydet
      await FirebaseMedicationService.saveDailyHistory(
        medicationId: medication.id,
        medicationName: medication.medicationName,
        wasTaken: false,
        wasSkipped: true,
        timestamp: DateTime.now(),
      );
      
      _showSuccessSnackBar('${medication.medicationName} atlandı olarak kaydedildi');
      
      // Arka planda verileri güncelle
      _loadData();
    } catch (e) {
      _showErrorSnackBar('İlaç atlanamadı: $e');
    }
  }

  Future<void> _undoMedication(Medication medication) async {
    try {
      // UI'yi hemen güncelle
      setState(() {
        _medicationTakenToday[medication.id] = false;
        _medicationSkippedToday[medication.id] = false;
      });
      
      // Firebase'e kalıcı olarak kaydet
      await _saveToFirebase();
      
      // Geçmişe kaydet
      await FirebaseMedicationService.saveDailyHistory(
        medicationId: medication.id,
        medicationName: medication.medicationName,
        wasTaken: false,
        wasSkipped: false,
        timestamp: DateTime.now(),
        notes: 'Geri alındı',
      );
      
      _showSuccessSnackBar('${medication.medicationName} geri alındı');
    } catch (e) {
      _showErrorSnackBar('Geri alma işlemi başarısız: $e');
    }
  }

  /// Firebase'e verileri kaydet
  Future<void> _saveToFirebase() async {
    try {
      await Future.wait([
        FirebaseMedicationService.saveMedicationTaken(_medicationTakenToday),
        FirebaseMedicationService.saveMedicationSkipped(_medicationSkippedToday),
      ]);
    } catch (e) {
      print('Firebase save error: $e');
      // Hata durumunda kullanıcıyı bilgilendir ama uygulamayı durdurma
    }
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
      ),
    );
  }
}

