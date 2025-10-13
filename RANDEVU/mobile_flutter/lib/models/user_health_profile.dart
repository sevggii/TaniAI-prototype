import 'package:cloud_firestore/cloud_firestore.dart';

class UserHealthProfile {
  final String userId;
  final List<String> chronicDiseases; // Kronik hastalıklar
  final List<String> allergies; // Alerjiler
  final List<String> currentMedications; // Mevcut ilaçlar
  final List<String> pastSymptoms; // Geçmiş semptomlar
  final Map<String, dynamic> preferences; // Kullanıcı tercihleri
  final DateTime lastUpdated;

  UserHealthProfile({
    required this.userId,
    this.chronicDiseases = const [],
    this.allergies = const [],
    this.currentMedications = const [],
    this.pastSymptoms = const [],
    this.preferences = const {},
    required this.lastUpdated,
  });

  factory UserHealthProfile.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return UserHealthProfile(
      userId: doc.id,
      chronicDiseases: List<String>.from(data['chronicDiseases'] ?? []),
      allergies: List<String>.from(data['allergies'] ?? []),
      currentMedications: List<String>.from(data['currentMedications'] ?? []),
      pastSymptoms: List<String>.from(data['pastSymptoms'] ?? []),
      preferences: Map<String, dynamic>.from(data['preferences'] ?? {}),
      lastUpdated: (data['lastUpdated'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'chronicDiseases': chronicDiseases,
      'allergies': allergies,
      'currentMedications': currentMedications,
      'pastSymptoms': pastSymptoms,
      'preferences': preferences,
      'lastUpdated': Timestamp.fromDate(lastUpdated),
    };
  }

  // Profili güncelle
  UserHealthProfile copyWith({
    List<String>? chronicDiseases,
    List<String>? allergies,
    List<String>? currentMedications,
    List<String>? pastSymptoms,
    Map<String, dynamic>? preferences,
    DateTime? lastUpdated,
  }) {
    return UserHealthProfile(
      userId: userId,
      chronicDiseases: chronicDiseases ?? this.chronicDiseases,
      allergies: allergies ?? this.allergies,
      currentMedications: currentMedications ?? this.currentMedications,
      pastSymptoms: pastSymptoms ?? this.pastSymptoms,
      preferences: preferences ?? this.preferences,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }

  // Profil özeti (AI için)
  String getSummary() {
    final summary = StringBuffer();
    
    if (chronicDiseases.isNotEmpty) {
      summary.writeln('Kronik Hastalıklar: ${chronicDiseases.join(", ")}');
    }
    
    if (allergies.isNotEmpty) {
      summary.writeln('Alerjiler: ${allergies.join(", ")}');
    }
    
    if (currentMedications.isNotEmpty) {
      summary.writeln('Mevcut İlaçlar: ${currentMedications.join(", ")}');
    }
    
    if (pastSymptoms.isNotEmpty) {
      summary.writeln('Geçmiş Semptomlar: ${pastSymptoms.take(5).join(", ")}');
    }
    
    return summary.toString();
  }
}

