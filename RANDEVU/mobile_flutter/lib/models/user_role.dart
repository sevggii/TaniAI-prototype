enum UserRole {
  patient,
  doctor;

  String get displayName {
    switch (this) {
      case UserRole.patient:
        return 'Hasta';
      case UserRole.doctor:
        return 'Doktor';
    }
  }

  String get iconName {
    switch (this) {
      case UserRole.patient:
        return 'person';
      case UserRole.doctor:
        return 'medical_services';
    }
  }

  String get value {
    switch (this) {
      case UserRole.patient:
        return 'patient';
      case UserRole.doctor:
        return 'doctor';
    }
  }

  static UserRole fromString(String value) {
    switch (value.toLowerCase()) {
      case 'doctor':
        return UserRole.doctor;
      case 'patient':
      default:
        return UserRole.patient;
    }
  }
}
