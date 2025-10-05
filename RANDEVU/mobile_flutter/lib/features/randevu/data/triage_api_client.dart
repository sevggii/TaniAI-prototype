import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class TriageApiException implements Exception {
  TriageApiException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() =>
      'TriageApiException(statusCode: $statusCode, message: $message)';
}

class TriageCandidate {
  const TriageCandidate({
    required this.clinic,
    required this.reason,
    required this.confidence,
  });

  final String clinic;
  final String reason;
  final double confidence;
}

class TriageResult {
  const TriageResult({
    required this.clinic,
    required this.candidates,
    required this.redFlag,
    required this.explanations,
    required this.canonicalized,
  });

  final String clinic;
  final List<TriageCandidate> candidates;
  final bool redFlag;
  final List<String> explanations;
  final bool canonicalized;

  factory TriageResult.fromJson(Map<String, dynamic> json) {
    final rawCandidates = json['candidates'] as List<dynamic>? ?? <dynamic>[];
    final candidates = rawCandidates
        .map((dynamic item) {
          final map = item as Map<String, dynamic>?;
          if (map == null) {
            return null;
          }
          final confidence = map['confidence'];
          return TriageCandidate(
            clinic: (map['clinic'] as String? ?? '').trim(),
            reason:
                (map['reason'] as String? ?? 'Gerekçe belirtilmedi.').trim(),
            confidence: confidence is num ? confidence.toDouble() : 0.0,
          );
        })
        .whereType<TriageCandidate>()
        .where((candidate) => candidate.clinic.isNotEmpty)
        .toList();

    return TriageResult(
      clinic: json['clinic'] as String? ?? '',
      candidates: candidates,
      redFlag: json['red_flag'] as bool? ?? false,
      explanations: (json['explanations'] as List<dynamic>? ?? <dynamic>[])
          .map((dynamic item) => item.toString())
          .where((element) => element.trim().isNotEmpty)
          .toList(),
      canonicalized: json['canonicalized'] as bool? ?? false,
    );
  }
}

class TriageApiClient {
  TriageApiClient({http.Client? httpClient})
      : _client = httpClient ?? http.Client();

  final http.Client _client;

  Future<TriageResult> analyzeComplaint({
    required String endpoint,
    required String text,
  }) async {
    final uri = Uri.parse(endpoint);
    final response = await _client.post(
      uri,
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text}),
    );

    if (response.statusCode != 200) {
      throw TriageApiException(
        'Triyaj servisi ${response.statusCode} yanıtı döndürdü: ${response.body}',
        statusCode: response.statusCode,
      );
    }

    final decoded = jsonDecode(response.body) as Map<String, dynamic>;
    final result = TriageResult.fromJson(decoded);

    if (result.clinic.isEmpty && !result.redFlag) {
      throw TriageApiException('Triyaj servisi geçerli klinik döndürmedi.');
    }
    return result;
  }

  void close() {
    _client.close();
  }
}

String resolveTriageEndpoint() {
  const override = String.fromEnvironment('TRIAGE_API_URL');
  if (override.isNotEmpty) {
    return override;
  }
  if (kIsWeb) {
    return 'http://localhost:8000/triage';
  }
  return 'http://10.0.2.2:8000/triage';
}
