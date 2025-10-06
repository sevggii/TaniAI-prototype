/// İlaç Ekleme Sayfası
/// Yeni ilaç ekleme formu

import 'package:flutter/material.dart';
import '../../models/medication.dart';
import '../../services/medication_service.dart';

class AddMedicationPage extends StatefulWidget {
  const AddMedicationPage({super.key});

  @override
  State<AddMedicationPage> createState() => _AddMedicationPageState();
}

class _AddMedicationPageState extends State<AddMedicationPage> {
  final _formKey = GlobalKey<FormState>();
  final _medicationNameController = TextEditingController();
  final _dosageAmountController = TextEditingController();
  final _prescribingDoctorController = TextEditingController();
  final _pharmacyNameController = TextEditingController();
  final _specialInstructionsController = TextEditingController();
  final _remainingPillsController = TextEditingController();

  DosageUnit _selectedDosageUnit = DosageUnit.mg;
  FrequencyType _selectedFrequencyType = FrequencyType.daily;
  List<String> _reminderTimes = ['08:00'];
  bool _requiresFood = false;
  bool _requiresWater = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _medicationNameController.dispose();
    _dosageAmountController.dispose();
    _prescribingDoctorController.dispose();
    _pharmacyNameController.dispose();
    _specialInstructionsController.dispose();
    _remainingPillsController.dispose();
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
                gradient: const LinearGradient(
                  colors: [Color(0xFF4CAF50), Color(0xFF45A049)],
                ),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.add_rounded,
                color: Colors.white,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'İlaç Ekle',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveMedication,
            child: Text(
              'Kaydet',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              const Color(0xFF4CAF50).withOpacity(0.1),
              const Color(0xFF45A049).withOpacity(0.05),
              Colors.white,
            ],
            stops: const [0.0, 0.3, 1.0],
          ),
        ),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionTitle('Temel Bilgiler'),
                _buildBasicInfoSection(),
                const SizedBox(height: 24),
                
                _buildSectionTitle('Dozaj Bilgileri'),
                _buildDosageSection(),
                const SizedBox(height: 24),
                
                _buildSectionTitle('Hatırlatma Saatleri'),
                _buildReminderSection(),
                const SizedBox(height: 24),
                
                _buildSectionTitle('Ek Bilgiler'),
                _buildAdditionalInfoSection(),
                const SizedBox(height: 24),
                
                _buildSectionTitle('Güvenlik'),
                _buildSafetySection(),
                const SizedBox(height: 32),
                
                _buildSaveButton(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF4CAF50).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.info_rounded,
              color: Color(0xFF4CAF50),
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Text(
            title,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBasicInfoSection() {
    return Container(
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
          TextFormField(
            controller: _medicationNameController,
            decoration: const InputDecoration(
              labelText: 'İlaç Adı *',
              hintText: 'Örn: Paracetamol',
              prefixIcon: Icon(Icons.medication_rounded),
              border: OutlineInputBorder(),
            ),
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'İlaç adı gereklidir';
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _prescribingDoctorController,
            decoration: const InputDecoration(
              labelText: 'Reçete Yazan Doktor',
              hintText: 'Örn: Dr. Ahmet Yılmaz',
              prefixIcon: Icon(Icons.person_rounded),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _pharmacyNameController,
            decoration: const InputDecoration(
              labelText: 'Eczane Adı',
              hintText: 'Örn: Merkez Eczanesi',
              prefixIcon: Icon(Icons.local_pharmacy_rounded),
              border: OutlineInputBorder(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDosageSection() {
    return Container(
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
            children: [
              Expanded(
                flex: 2,
                child: TextFormField(
                  controller: _dosageAmountController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Doz Miktarı *',
                    hintText: '500',
                    prefixIcon: Icon(Icons.straighten_rounded),
                    border: OutlineInputBorder(),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Doz miktarı gereklidir';
                    }
                    if (double.tryParse(value) == null) {
                      return 'Geçerli bir sayı girin';
                    }
                    return null;
                  },
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: DropdownButtonFormField<DosageUnit>(
                  value: _selectedDosageUnit,
                  decoration: const InputDecoration(
                    labelText: 'Birim',
                    border: OutlineInputBorder(),
                  ),
                  items: DosageUnit.values.map((unit) {
                    return DropdownMenuItem(
                      value: unit,
                      child: Text(unit.displayName),
                    );
                  }).toList(),
                  onChanged: (value) {
                    setState(() {
                      _selectedDosageUnit = value!;
                    });
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<FrequencyType>(
            value: _selectedFrequencyType,
            decoration: const InputDecoration(
              labelText: 'Kullanım Sıklığı *',
              border: OutlineInputBorder(),
            ),
            items: FrequencyType.values.map((frequency) {
              return DropdownMenuItem(
                value: frequency,
                child: Text(frequency.displayName),
              );
            }).toList(),
            onChanged: (value) {
              setState(() {
                _selectedFrequencyType = value!;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildReminderSection() {
    return Container(
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Hatırlatma Saatleri',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              IconButton(
                onPressed: _addReminderTime,
                icon: const Icon(Icons.add_rounded),
                style: IconButton.styleFrom(
                  backgroundColor: const Color(0xFF4CAF50),
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ..._reminderTimes.asMap().entries.map((entry) {
            final index = entry.key;
            final time = entry.value;
            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      initialValue: time,
                      decoration: const InputDecoration(
                        labelText: 'Saat',
                        hintText: '08:00',
                        border: OutlineInputBorder(),
                      ),
                      onChanged: (value) {
                        _reminderTimes[index] = value;
                      },
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    onPressed: () => _removeReminderTime(index),
                    icon: const Icon(Icons.remove_rounded),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.red.withOpacity(0.1),
                      foregroundColor: Colors.red,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildAdditionalInfoSection() {
    return Container(
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
          TextFormField(
            controller: _specialInstructionsController,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Özel Talimatlar',
              hintText: 'Örn: Yemekle birlikte alın',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextFormField(
            controller: _remainingPillsController,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              labelText: 'Kalan Hap Sayısı',
              hintText: '30',
              prefixIcon: Icon(Icons.inventory_2_rounded),
              border: OutlineInputBorder(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSafetySection() {
    return Container(
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
          SwitchListTile(
            title: const Text('Yemekle Birlikte Alınması Gerekiyor'),
            subtitle: const Text('İlaç yemekle birlikte alınmalı'),
            value: _requiresFood,
            onChanged: (value) {
              setState(() {
                _requiresFood = value;
              });
            },
            activeColor: const Color(0xFF4CAF50),
          ),
          SwitchListTile(
            title: const Text('Su ile Birlikte Alınması Gerekiyor'),
            subtitle: const Text('İlaç su ile birlikte alınmalı'),
            value: _requiresWater,
            onChanged: (value) {
              setState(() {
                _requiresWater = value;
              });
            },
            activeColor: const Color(0xFF4CAF50),
          ),
        ],
      ),
    );
  }

  Widget _buildSaveButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isLoading ? null : _saveMedication,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF4CAF50),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 4,
        ),
        child: _isLoading
            ? const SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : const Text(
                'İlaç Kaydet',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
      ),
    );
  }

  void _addReminderTime() {
    setState(() {
      _reminderTimes.add('08:00');
    });
  }

  void _removeReminderTime(int index) {
    if (_reminderTimes.length > 1) {
      setState(() {
        _reminderTimes.removeAt(index);
      });
    }
  }

  Future<void> _saveMedication() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final medicationData = {
        'medication_name': _medicationNameController.text.trim(),
        'dosage_amount': double.parse(_dosageAmountController.text),
        'dosage_unit': _selectedDosageUnit.value,
        'frequency_type': _selectedFrequencyType.value,
        'reminder_times': _reminderTimes,
        'start_date': DateTime.now().toIso8601String(),
        'prescribing_doctor': _prescribingDoctorController.text.trim().isEmpty 
            ? null : _prescribingDoctorController.text.trim(),
        'pharmacy_name': _pharmacyNameController.text.trim().isEmpty 
            ? null : _pharmacyNameController.text.trim(),
        'special_instructions': _specialInstructionsController.text.trim().isEmpty 
            ? null : _specialInstructionsController.text.trim(),
        'requires_food': _requiresFood,
        'requires_water': _requiresWater,
        'remaining_pills': _remainingPillsController.text.trim().isEmpty 
            ? null : int.parse(_remainingPillsController.text),
        'refill_reminder_days': 7,
      };

      await MedicationService.createMedication(medicationData);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('İlaç başarıyla eklendi!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('İlaç eklenirken hata oluştu: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}
