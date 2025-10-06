/// İlaç Takibi Modelleri
/// Backend API ile uyumlu veri modelleri

class Medication {
  final int id;
  final int userId;
  final String medicationName;
  final String? genericName;
  final String? brandName;
  final String? drugId;
  
  final double dosageAmount;
  final DosageUnit dosageUnit;
  final FrequencyType frequencyType;
  final String? customFrequency;
  final List<String> reminderTimes;
  
  final DateTime startDate;
  final DateTime? endDate;
  final DateTime? prescribedDate;
  final MedicationStatus status;
  final bool isActive;
  
  final String? prescriptionNumber;
  final String? prescribingDoctor;
  final String? pharmacyName;
  
  final String? indication;
  final String? contraindications;
  final String? specialInstructions;
  
  final double? maxDailyDose;
  final double? minDailyDose;
  final bool requiresFood;
  final bool requiresWater;
  
  final int? totalPrescribed;
  final int? remainingPills;
  final int refillReminderDays;
  
  final DateTime createdAt;
  final DateTime updatedAt;

  Medication({
    required this.id,
    required this.userId,
    required this.medicationName,
    this.genericName,
    this.brandName,
    this.drugId,
    required this.dosageAmount,
    required this.dosageUnit,
    required this.frequencyType,
    this.customFrequency,
    required this.reminderTimes,
    required this.startDate,
    this.endDate,
    this.prescribedDate,
    required this.status,
    required this.isActive,
    this.prescriptionNumber,
    this.prescribingDoctor,
    this.pharmacyName,
    this.indication,
    this.contraindications,
    this.specialInstructions,
    this.maxDailyDose,
    this.minDailyDose,
    required this.requiresFood,
    required this.requiresWater,
    this.totalPrescribed,
    this.remainingPills,
    required this.refillReminderDays,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Medication.fromJson(Map<String, dynamic> json) {
    return Medication(
      id: json['id'],
      userId: json['user_id'],
      medicationName: json['medication_name'],
      genericName: json['generic_name'],
      brandName: json['brand_name'],
      drugId: json['drug_id'],
      dosageAmount: (json['dosage_amount'] as num).toDouble(),
      dosageUnit: DosageUnit.fromString(json['dosage_unit']),
      frequencyType: FrequencyType.fromString(json['frequency_type']),
      customFrequency: json['custom_frequency'],
      reminderTimes: List<String>.from(json['reminder_times']),
      startDate: DateTime.parse(json['start_date']),
      endDate: json['end_date'] != null ? DateTime.parse(json['end_date']) : null,
      prescribedDate: json['prescribed_date'] != null ? DateTime.parse(json['prescribed_date']) : null,
      status: MedicationStatus.fromString(json['status']),
      isActive: json['is_active'],
      prescriptionNumber: json['prescription_number'],
      prescribingDoctor: json['prescribing_doctor'],
      pharmacyName: json['pharmacy_name'],
      indication: json['indication'],
      contraindications: json['contraindications'],
      specialInstructions: json['special_instructions'],
      maxDailyDose: json['max_daily_dose'] != null ? (json['max_daily_dose'] as num).toDouble() : null,
      minDailyDose: json['min_daily_dose'] != null ? (json['min_daily_dose'] as num).toDouble() : null,
      requiresFood: json['requires_food'],
      requiresWater: json['requires_water'],
      totalPrescribed: json['total_prescribed'],
      remainingPills: json['remaining_pills'],
      refillReminderDays: json['refill_reminder_days'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'medication_name': medicationName,
      'generic_name': genericName,
      'brand_name': brandName,
      'drug_id': drugId,
      'dosage_amount': dosageAmount,
      'dosage_unit': dosageUnit.value,
      'frequency_type': frequencyType.value,
      'custom_frequency': customFrequency,
      'reminder_times': reminderTimes,
      'start_date': startDate.toIso8601String(),
      'end_date': endDate?.toIso8601String(),
      'prescribed_date': prescribedDate?.toIso8601String(),
      'status': status.value,
      'is_active': isActive,
      'prescription_number': prescriptionNumber,
      'prescribing_doctor': prescribingDoctor,
      'pharmacy_name': pharmacyName,
      'indication': indication,
      'contraindications': contraindications,
      'special_instructions': specialInstructions,
      'max_daily_dose': maxDailyDose,
      'min_daily_dose': minDailyDose,
      'requires_food': requiresFood,
      'requires_water': requiresWater,
      'total_prescribed': totalPrescribed,
      'remaining_pills': remainingPills,
      'refill_reminder_days': refillReminderDays,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// İlaç alınma zamanı geldi mi?
  bool get isDueNow {
    final now = DateTime.now();
    final currentTime = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
    return reminderTimes.contains(currentTime);
  }

  /// Sonraki alınma zamanı
  String? get nextReminderTime {
    final now = DateTime.now();
    final currentTime = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
    
    final sortedTimes = [...reminderTimes]..sort();
    for (final time in sortedTimes) {
      if (time.compareTo(currentTime) > 0) {
        return time;
      }
    }
    return sortedTimes.isNotEmpty ? sortedTimes.first : null;
  }

  /// Kalan hap sayısı düşük mü?
  bool get isLowOnPills {
    return remainingPills != null && remainingPills! <= refillReminderDays;
  }

  /// İlaç aktif mi?
  bool get isCurrentlyActive {
    final now = DateTime.now();
    return isActive && 
           status == MedicationStatus.active &&
           startDate.isBefore(now) &&
           (endDate == null || endDate!.isAfter(now));
  }
}

class MedicationLog {
  final int id;
  final int medicationId;
  final int userId;
  final DateTime takenAt;
  final DateTime? scheduledTime;
  final double dosageTaken;
  final DosageUnit dosageUnit;
  
  final bool wasTaken;
  final bool wasSkipped;
  final bool wasDelayed;
  final int? delayMinutes;
  
  final String? notes;
  final bool sideEffectsNoted;
  final DateTime createdAt;

  MedicationLog({
    required this.id,
    required this.medicationId,
    required this.userId,
    required this.takenAt,
    this.scheduledTime,
    required this.dosageTaken,
    required this.dosageUnit,
    required this.wasTaken,
    required this.wasSkipped,
    required this.wasDelayed,
    this.delayMinutes,
    this.notes,
    required this.sideEffectsNoted,
    required this.createdAt,
  });

  factory MedicationLog.fromJson(Map<String, dynamic> json) {
    return MedicationLog(
      id: json['id'],
      medicationId: json['medication_id'],
      userId: json['user_id'],
      takenAt: DateTime.parse(json['taken_at']),
      scheduledTime: json['scheduled_time'] != null ? DateTime.parse(json['scheduled_time']) : null,
      dosageTaken: (json['dosage_taken'] as num).toDouble(),
      dosageUnit: DosageUnit.fromString(json['dosage_unit']),
      wasTaken: json['was_taken'],
      wasSkipped: json['was_skipped'],
      wasDelayed: json['was_delayed'],
      delayMinutes: json['delay_minutes'],
      notes: json['notes'],
      sideEffectsNoted: json['side_effects_noted'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'medication_id': medicationId,
      'user_id': userId,
      'taken_at': takenAt.toIso8601String(),
      'scheduled_time': scheduledTime?.toIso8601String(),
      'dosage_taken': dosageTaken,
      'dosage_unit': dosageUnit.value,
      'was_taken': wasTaken,
      'was_skipped': wasSkipped,
      'was_delayed': wasDelayed,
      'delay_minutes': delayMinutes,
      'notes': notes,
      'side_effects_noted': sideEffectsNoted,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class MedicationSummary {
  final int totalMedications;
  final int activeMedications;
  final int medicationsDueToday;
  final int missedDosesToday;
  final int upcomingRefills;
  final int activeSideEffects;
  final int criticalInteractions;

  MedicationSummary({
    required this.totalMedications,
    required this.activeMedications,
    required this.medicationsDueToday,
    required this.missedDosesToday,
    required this.upcomingRefills,
    required this.activeSideEffects,
    required this.criticalInteractions,
  });

  factory MedicationSummary.fromJson(Map<String, dynamic> json) {
    return MedicationSummary(
      totalMedications: json['total_medications'],
      activeMedications: json['active_medications'],
      medicationsDueToday: json['medications_due_today'],
      missedDosesToday: json['missed_doses_today'],
      upcomingRefills: json['upcoming_refills'],
      activeSideEffects: json['active_side_effects'],
      criticalInteractions: json['critical_interactions'],
    );
  }
}

class MedicationAlert {
  final int id;
  final int userId;
  final String alertType;
  final SeverityLevel severity;
  final String title;
  final String message;
  
  final bool isRead;
  final bool isDismissed;
  final bool requiresAction;
  
  final DateTime createdAt;
  final DateTime? readAt;
  final DateTime? dismissedAt;

  MedicationAlert({
    required this.id,
    required this.userId,
    required this.alertType,
    required this.severity,
    required this.title,
    required this.message,
    required this.isRead,
    required this.isDismissed,
    required this.requiresAction,
    required this.createdAt,
    this.readAt,
    this.dismissedAt,
  });

  factory MedicationAlert.fromJson(Map<String, dynamic> json) {
    return MedicationAlert(
      id: json['id'],
      userId: json['user_id'],
      alertType: json['alert_type'],
      severity: SeverityLevel.fromString(json['severity']),
      title: json['title'],
      message: json['message'],
      isRead: json['is_read'],
      isDismissed: json['is_dismissed'],
      requiresAction: json['requires_action'],
      createdAt: DateTime.parse(json['created_at']),
      readAt: json['read_at'] != null ? DateTime.parse(json['read_at']) : null,
      dismissedAt: json['dismissed_at'] != null ? DateTime.parse(json['dismissed_at']) : null,
    );
  }
}

// Enum'lar
enum DosageUnit {
  mg('mg'),
  mcg('mcg'),
  g('g'),
  ml('ml'),
  tablet('tablet'),
  capsule('capsule'),
  drop('drop'),
  puff('puff'),
  unit('unit'),
  iu('iu');

  const DosageUnit(this.value);
  final String value;

  static DosageUnit fromString(String value) {
    return DosageUnit.values.firstWhere((e) => e.value == value);
  }

  String get displayName {
    switch (this) {
      case DosageUnit.mg:
        return 'Miligram';
      case DosageUnit.mcg:
        return 'Mikrogram';
      case DosageUnit.g:
        return 'Gram';
      case DosageUnit.ml:
        return 'Mililitre';
      case DosageUnit.tablet:
        return 'Tablet';
      case DosageUnit.capsule:
        return 'Kapsül';
      case DosageUnit.drop:
        return 'Damla';
      case DosageUnit.puff:
        return 'Puf';
      case DosageUnit.unit:
        return 'Ünite';
      case DosageUnit.iu:
        return 'Uluslararası Ünite';
    }
  }
}

enum FrequencyType {
  daily('daily'),
  twiceDaily('twice_daily'),
  threeTimesDaily('three_times_daily'),
  fourTimesDaily('four_times_daily'),
  weekly('weekly'),
  monthly('monthly'),
  asNeeded('as_needed'),
  custom('custom');

  const FrequencyType(this.value);
  final String value;

  static FrequencyType fromString(String value) {
    return FrequencyType.values.firstWhere((e) => e.value == value);
  }

  String get displayName {
    switch (this) {
      case FrequencyType.daily:
        return 'Günlük';
      case FrequencyType.twiceDaily:
        return 'Günde 2 kez';
      case FrequencyType.threeTimesDaily:
        return 'Günde 3 kez';
      case FrequencyType.fourTimesDaily:
        return 'Günde 4 kez';
      case FrequencyType.weekly:
        return 'Haftalık';
      case FrequencyType.monthly:
        return 'Aylık';
      case FrequencyType.asNeeded:
        return 'Gerektiğinde';
      case FrequencyType.custom:
        return 'Özel';
    }
  }
}

enum MedicationStatus {
  active('active'),
  paused('paused'),
  completed('completed'),
  discontinued('discontinued'),
  expired('expired');

  const MedicationStatus(this.value);
  final String value;

  static MedicationStatus fromString(String value) {
    return MedicationStatus.values.firstWhere((e) => e.value == value);
  }

  String get displayName {
    switch (this) {
      case MedicationStatus.active:
        return 'Aktif';
      case MedicationStatus.paused:
        return 'Durdurulmuş';
      case MedicationStatus.completed:
        return 'Tamamlanmış';
      case MedicationStatus.discontinued:
        return 'Kesilmiş';
      case MedicationStatus.expired:
        return 'Süresi Dolmuş';
    }
  }

  String get color {
    switch (this) {
      case MedicationStatus.active:
        return 'green';
      case MedicationStatus.paused:
        return 'orange';
      case MedicationStatus.completed:
        return 'blue';
      case MedicationStatus.discontinued:
        return 'red';
      case MedicationStatus.expired:
        return 'red';
    }
  }
}

enum SeverityLevel {
  mild('mild'),
  moderate('moderate'),
  severe('severe'),
  critical('critical');

  const SeverityLevel(this.value);
  final String value;

  static SeverityLevel fromString(String value) {
    return SeverityLevel.values.firstWhere((e) => e.value == value);
  }

  String get displayName {
    switch (this) {
      case SeverityLevel.mild:
        return 'Hafif';
      case SeverityLevel.moderate:
        return 'Orta';
      case SeverityLevel.severe:
        return 'Şiddetli';
      case SeverityLevel.critical:
        return 'Kritik';
    }
  }

  String get color {
    switch (this) {
      case SeverityLevel.mild:
        return 'green';
      case SeverityLevel.moderate:
        return 'yellow';
      case SeverityLevel.severe:
        return 'orange';
      case SeverityLevel.critical:
        return 'red';
    }
  }
}
