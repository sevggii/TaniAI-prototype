import 'package:cloud_firestore/cloud_firestore.dart';

class ChatMessage {
  final String id;
  final String text;
  final String senderId;
  final String senderName;
  final DateTime timestamp;
  final bool isAI;
  final String? sessionId; // Konuşma oturumu ID'si

  ChatMessage({
    required this.id,
    required this.text,
    required this.senderId,
    required this.senderName,
    required this.timestamp,
    this.isAI = false,
    this.sessionId,
  });

  factory ChatMessage.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>;
    return ChatMessage(
      id: doc.id,
      text: data['text'] ?? '',
      senderId: data['senderId'] ?? '',
      senderName: data['senderName'] ?? '',
      timestamp: (data['timestamp'] as Timestamp).toDate(),
      isAI: data['isAI'] ?? false,
      sessionId: data['sessionId'],
    );
  }

  Map<String, dynamic> toFirestore() {
    return {
      'text': text,
      'senderId': senderId,
      'senderName': senderName,
      'timestamp': Timestamp.fromDate(timestamp),
      'isAI': isAI,
      'sessionId': sessionId,
    };
  }

  ChatMessage copyWith({
    String? id,
    String? text,
    String? senderId,
    String? senderName,
    DateTime? timestamp,
    bool? isAI,
    String? sessionId,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      text: text ?? this.text,
      senderId: senderId ?? this.senderId,
      senderName: senderName ?? this.senderName,
      timestamp: timestamp ?? this.timestamp,
      isAI: isAI ?? this.isAI,
      sessionId: sessionId ?? this.sessionId,
    );
  }
}
