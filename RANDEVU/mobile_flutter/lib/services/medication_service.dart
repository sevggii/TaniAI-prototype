/// İlaç Takibi API Servisi
/// Backend API ile iletişim kurar

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/medication.dart';

class MedicationService {
  static const String _baseUrl = 'http://127.0.0.1:8002'; // İlaç Takibi API URL

  // İlaç CRUD İşlemleri
  static Future<List<Medication>> getMedications() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/medications/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((json) => Medication.fromJson(json)).toList();
      } else {
        throw Exception('İlaçlar getirilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      return _getMockMedications(); // Fallback mock data
    }
  }

  static Future<Medication?> getMedication(int medicationId) async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/medications/$medicationId'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return Medication.fromJson(data);
      } else if (response.statusCode == 404) {
        return null;
      } else {
        throw Exception('İlaç getirilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      return null;
    }
  }

  static Future<Medication> createMedication(Map<String, dynamic> medicationData) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/medications/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(medicationData),
      );

      if (response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return Medication.fromJson(data);
      } else {
        throw Exception('İlaç oluşturulamadı: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      throw Exception('İlaç oluşturulamadı: $e');
    }
  }

  static Future<Medication> updateMedication(int medicationId, Map<String, dynamic> updateData) async {
    try {
      final response = await http.put(
        Uri.parse('$_baseUrl/medications/$medicationId'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(updateData),
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return Medication.fromJson(data);
      } else {
        throw Exception('İlaç güncellenemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      throw Exception('İlaç güncellenemedi: $e');
    }
  }

  static Future<bool> deleteMedication(int medicationId) async {
    try {
      final response = await http.delete(
        Uri.parse('$_baseUrl/medications/$medicationId'),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 204;
    } catch (e) {
      print('Medication Service Error: $e');
      return false;
    }
  }

  // İlaç Kullanım Takibi
  static Future<MedicationLog> logMedicationTaken(Map<String, dynamic> logData) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/medications/logs'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(logData),
      );

      if (response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return MedicationLog.fromJson(data);
      } else {
        throw Exception('İlaç kullanımı kaydedilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      throw Exception('İlaç kullanımı kaydedilemedi: $e');
    }
  }

  static Future<List<MedicationLog>> getMedicationLogs() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/medications/logs'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((json) => MedicationLog.fromJson(json)).toList();
      } else {
        throw Exception('İlaç kullanım kayıtları getirilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      return _getMockMedicationLogs(); // Fallback mock data
    }
  }

  // Hızlı İlaç Alma
  static Future<MedicationLog> takeMedicationNow(int medicationId, {double? dosageTaken, String? notes}) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/medications/$medicationId/take'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'dosage_taken': dosageTaken,
          'notes': notes,
        }),
      );

      if (response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return MedicationLog.fromJson(data);
      } else {
        throw Exception('İlaç alınamadı: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      throw Exception('İlaç alınamadı: $e');
    }
  }

  // İlaç Atla
  static Future<MedicationLog> skipMedication(int medicationId, {String? reason}) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/medications/$medicationId/skip'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'reason': reason,
        }),
      );

      if (response.statusCode == 201) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return MedicationLog.fromJson(data);
      } else {
        throw Exception('İlaç atlanamadı: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      throw Exception('İlaç atlanamadı: $e');
    }
  }

  // Bugünkü İlaçlar
  static Future<List<Medication>> getMedicationsDueToday() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/medications/today/due'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((json) => Medication.fromJson(json)).toList();
      } else {
        throw Exception('Bugünkü ilaçlar getirilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      return _getMockMedicationsDueToday(); // Fallback mock data
    }
  }

  // İlaç Özeti
  static Future<MedicationSummary> getMedicationSummary() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/medications/summary'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return MedicationSummary.fromJson(data);
      } else {
        throw Exception('İlaç özeti getirilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      return _getMockMedicationSummary(); // Fallback mock data
    }
  }

  // Uyarılar
  static Future<List<MedicationAlert>> getMedicationAlerts() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/medications/alerts'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((json) => MedicationAlert.fromJson(json)).toList();
      } else {
        throw Exception('İlaç uyarıları getirilemedi: ${response.statusCode}');
      }
    } catch (e) {
      print('Medication Service Error: $e');
      return _getMockMedicationAlerts(); // Fallback mock data
    }
  }

  static Future<bool> markAlertAsRead(int alertId) async {
    try {
      final response = await http.patch(
        Uri.parse('$_baseUrl/medications/alerts/$alertId/read'),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 204;
    } catch (e) {
      print('Medication Service Error: $e');
      return false;
    }
  }

  static Future<bool> dismissAlert(int alertId) async {
    try {
      final response = await http.patch(
        Uri.parse('$_baseUrl/medications/alerts/$alertId/dismiss'),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 204;
    } catch (e) {
      print('Medication Service Error: $e');
      return false;
    }
  }

  // Mock Data (Fallback)
  static List<Medication> _getMockMedications() {
    return [
      Medication(
        id: 1,
        userId: 1,
        medicationName: 'Paracetamol',
        genericName: 'Acetaminophen',
        brandName: 'Tylenol',
        dosageAmount: 500,
        dosageUnit: DosageUnit.mg,
        frequencyType: FrequencyType.twiceDaily,
        reminderTimes: ['08:00', '20:00'],
        startDate: DateTime.now().subtract(const Duration(days: 30)),
        status: MedicationStatus.active,
        isActive: true,
        requiresFood: false,
        requiresWater: true,
        refillReminderDays: 7,
        remainingPills: 15,
        totalPrescribed: 30,
        createdAt: DateTime.now().subtract(const Duration(days: 30)),
        updatedAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
      Medication(
        id: 2,
        userId: 1,
        medicationName: 'Vitamin D3',
        genericName: 'Cholecalciferol',
        brandName: 'D-Vitamin',
        dosageAmount: 1000,
        dosageUnit: DosageUnit.iu,
        frequencyType: FrequencyType.daily,
        reminderTimes: ['09:00'],
        startDate: DateTime.now().subtract(const Duration(days: 15)),
        status: MedicationStatus.active,
        isActive: true,
        requiresFood: true,
        requiresWater: true,
        refillReminderDays: 7,
        remainingPills: 25,
        totalPrescribed: 30,
        createdAt: DateTime.now().subtract(const Duration(days: 15)),
        updatedAt: DateTime.now().subtract(const Duration(days: 1)),
      ),
    ];
  }

  static List<MedicationLog> _getMockMedicationLogs() {
    return [
      MedicationLog(
        id: 1,
        medicationId: 1,
        userId: 1,
        takenAt: DateTime.now().subtract(const Duration(hours: 2)),
        dosageTaken: 500,
        dosageUnit: DosageUnit.mg,
        wasTaken: true,
        wasSkipped: false,
        wasDelayed: false,
        sideEffectsNoted: false,
        createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      ),
      MedicationLog(
        id: 2,
        medicationId: 2,
        userId: 1,
        takenAt: DateTime.now().subtract(const Duration(hours: 1)),
        dosageTaken: 1000,
        dosageUnit: DosageUnit.iu,
        wasTaken: true,
        wasSkipped: false,
        wasDelayed: false,
        sideEffectsNoted: false,
        createdAt: DateTime.now().subtract(const Duration(hours: 1)),
      ),
    ];
  }

  static List<Medication> _getMockMedicationsDueToday() {
    return _getMockMedications().where((med) => med.isCurrentlyActive).toList();
  }

  static MedicationSummary _getMockMedicationSummary() {
    return MedicationSummary(
      totalMedications: 2,
      activeMedications: 2,
      medicationsDueToday: 2,
      missedDosesToday: 0,
      upcomingRefills: 0,
      activeSideEffects: 0,
      criticalInteractions: 0,
    );
  }

  static List<MedicationAlert> _getMockMedicationAlerts() {
    return [
      MedicationAlert(
        id: 1,
        userId: 1,
        alertType: 'refill',
        severity: SeverityLevel.mild,
        title: 'İlaç Yenileme Hatırlatması',
        message: 'Paracetamol yenilenmesi gerekiyor',
        isRead: false,
        isDismissed: false,
        requiresAction: true,
        createdAt: DateTime.now().subtract(const Duration(hours: 1)),
      ),
    ];
  }
}
