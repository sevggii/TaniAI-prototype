# 🌟 Dostane Sağlık Hatırlatma Sistemi

Bu Flutter uygulaması, kullanıcıların günlük sağlık alışkanlıklarını desteklemek için tasarlanmış dostane, sıcak ve mizahi bir bildirim sistemi içerir.

## 🎯 Özellikler

### 📱 Bildirim Sistemi
- **Dostane Mesajlar**: Türkçe, sıcak ve mizahi hatırlatmalar
- **Akıllı Zamanlama**: Europe/Istanbul saat dilimi ile çalışır
- **Jitter**: ±15 dakika rastgele zamanlama (tekrarları önler)
- **DND Desteği**: 23:00-08:00 arası sessiz saatlerde bildirim gönderilmez
- **Çeşitlilik**: Her kategori için farklı mesajlar, aynı gün tekrar etmez

### 🏥 Sağlık Kategorileri
- **🌞 D Vitamini**: Güneşlenme hatırlatmaları
- **💧 Su İçme**: Hidrasyon hatırlatmaları  
- **🍎 Ara Öğün**: Meyve yeme hatırlatmaları
- **👟 Yürüyüş**: Hareket hatırlatmaları
- **👀 Göz Molası**: 20-20-20 kuralı hatırlatmaları
- **🧘 Esneme**: Duruş düzeltme hatırlatmaları
- **✨ Moral**: Pozitif düşünce hatırlatmaları
- **🌬️ Nefes**: Derin nefes alma hatırlatmaları
- **🌙 Gün Kapanışı**: Gün sonu huzur hatırlatmaları

### ⚙️ Teknik Özellikler
- **Cross-Platform**: Android, iOS, Web, Windows desteği
- **Timezone Aware**: Europe/Istanbul saat dilimi
- **Smart Scheduling**: Haftalık tekrarlama
- **Action Buttons**: Snooze (30dk), Mark Done, Open App
- **Permission Management**: Otomatik izin yönetimi
- **Configurable**: JSON dosyasından kolay konfigürasyon

## 🚀 Kurulum ve Kullanım

### 1. Paket Bağımlılıkları
```yaml
dependencies:
  flutter_local_notifications: ^17.2.3
  timezone: ^0.9.4
```

### 2. Platform Konfigürasyonu

#### Android (android/app/src/main/AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
```

#### iOS (ios/Runner/Info.plist)
```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>remote-notification</string>
</array>
```

### 3. Kullanım

#### Servisi Başlatma
```dart
// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize notification service
  final notificationService = NotificationService();
  await notificationService.initialize();
  
  // Request permissions and schedule notifications
  final hasPermission = await notificationService.requestPermissions();
  if (hasPermission) {
    await notificationService.scheduleAllNotifications();
  }
  
  runApp(const MyApp());
}
```

#### Bildirimleri Kontrol Etme
```dart
// Settings sayfasında
final notificationService = NotificationService();

// Bildirimleri etkinleştir
await notificationService.requestPermissions();
await notificationService.scheduleAllNotifications();

// Bildirimleri devre dışı bırak
await notificationService.cancelAllNotifications();
```

## 📋 Konfigürasyon

### JSON Konfigürasyon Dosyası (assets/notifications_config.json)
```json
{
  "timezone": "Europe/Istanbul",
  "do_not_disturb": {
    "start": "23:00",
    "end": "08:00"
  },
  "jitter_minutes": 15,
  "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  "notifications": [
    {
      "time": "10:30",
      "category": "D_vitamini",
      "messages": [
        "🌞 Günaydın dostum! Hadi biraz güneşe çık, D vitamini seni bekliyor 😎",
        "☀️ Küçük bir güneş molası? Hem enerji hem de D vitamini bonusu 💪"
      ],
      "weight": 1
    }
  ]
}
```

### Yeni Bildirim Ekleme
1. `assets/notifications_config.json` dosyasını düzenleyin
2. Yeni kategori ve mesajlar ekleyin
3. Uygulamayı yeniden başlatın

## 🎨 Mesaj Örnekleri

### D Vitamini
- "🌞 Günaydın dostum! Hadi biraz güneşe çık, D vitamini seni bekliyor 😎"
- "☀️ Küçük bir güneş molası? Hem enerji hem de D vitamini bonusu 💪"

### Su İçme
- "💧 Hadi dostum, bir bardak su içelim mi beraber? 🥤"
- "🚰 Su molası! Bardaklar seni özlemiş olabilir 😌"

### Moral
- "✨ Küçük şeylere bile değer katıyorsun, biliyor musun? Sen özelsin 💖"
- "🌞 Gülüşün dünyaya iyi geliyor; bugün de paylaşsana biraz 😍"

## 🔧 API Referansı

### NotificationService Sınıfı

#### Temel Metodlar
```dart
// Servisi başlat
await notificationService.initialize();

// İzinleri iste
bool hasPermission = await notificationService.requestPermissions();

// Tüm bildirimleri zamanla
await notificationService.scheduleAllNotifications();

// Tüm bildirimleri iptal et
await notificationService.cancelAllNotifications();

// Bildirimlerin etkin olup olmadığını kontrol et
bool enabled = await notificationService.areNotificationsEnabled();
```

#### Özel Metodlar
```dart
// Soft delete hesap kontrolü
bool isSoftDeleted = await notificationService.isAccountSoftDeleted(uid);

// Süresi geçmiş hesapları temizle
await notificationService.cleanupExpiredAccounts();
```

## 🎯 Kullanım Senaryoları

### 1. Günlük Sağlık Rutini
- Sabah: D vitamini hatırlatması
- Öğlen: Su içme ve ara öğün hatırlatmaları
- Öğleden sonra: Yürüyüş ve göz molası
- Akşam: Esneme ve nefes egzersizleri
- Gece: Gün kapanışı ve huzur

### 2. Hafta Sonu Desteği
- Tüm günler için aktif
- Hafta sonu için özel mesajlar
- Esnek zamanlama

### 3. Kullanıcı Kontrolü
- Settings sayfasından açma/kapama
- İzin yönetimi
- Bildirim geçmişi

## 🚨 Önemli Notlar

1. **İzinler**: İlk çalıştırmada bildirim izni istenir
2. **DND**: Gece saatlerinde bildirim gönderilmez
3. **Jitter**: Her bildirim ±15 dakika rastgele zamanlanır
4. **Tekrar**: Aynı gün aynı mesaj tekrar etmez
5. **Timezone**: Europe/Istanbul saat dilimi kullanılır

## 🔄 Güncelleme ve Bakım

### Yeni Mesaj Ekleme
1. JSON dosyasını düzenleyin
2. Yeni kategori veya mesaj ekleyin
3. Uygulamayı yeniden başlatın

### Süre Ayarlama
- DND süresi: JSON'da `do_not_disturb` bölümü
- Jitter: `jitter_minutes` değeri
- Tekrar günleri: `days` dizisi

Bu sistem, kullanıcıların sağlık alışkanlıklarını desteklemek için tasarlanmış dostane ve etkili bir çözümdür! 🌟
