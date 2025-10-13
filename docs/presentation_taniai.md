# TanıAI Randevu Sunumu

## Slayt 1 – Başlangıç & Vizyon
- **Mesaj:** “Sağlık hizmetlerine erişimi herkes için kolaylaştıran yapay zeka asistanı”
- TanıAI Randevu logosu veya sade bir başlık ekranı
- Kısa slogan: “Sesle randevu, akıllı semptom analizi, kişisel sağlık rehberi”
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/mainpage_chat.png`

## Slayt 2 – Sorun Tanımı
- MHRS’de randevu bulmanın zorluğu; özellikle yaşlı ve görme engelli bireyler için erişim problemi
- Semptom takibinin yapılamaması, doktora geç başvuru riski
- Acil durumlarda doğru branşa yönlendirme eksikliği
- Öne çıkan metrik: 66 farklı klinikte randevu seçenekleri, ancak erişilebilir deneyim eksik

## Slayt 3 – Çözümümüz
- Sesli komutlarla (Whisper + TTS) randevu alma: “182’yi ara”, “Kardiyoloji randevusu bul”
- Yapay zeka destekli semptom analizi ve triage önerileri
- MHRS entegrasyonu ile tek ekrandan randevu tamamlama
- Günlük sağlık hatırlatmaları ve kişisel öneriler
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/whisper_mobile.png`

## Slayt 4 – Kullanıcı Deneyimi Akışı
- 1️⃣ Sesli veya yazılı semptom paylaşımı
- 2️⃣ AI triage: aciliyet, önerilen branş ve test önerileri
- 3️⃣ Randevu ve ilaca yönelik aksiyon butonları
- 4️⃣ Bildirimler ile takip; kritik durum uyarıları
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/klinik_oneri_basagrisi.png`

## Slayt 5 – Ana Özellikler
- **Sesli Randevu:** Tek tuşla telefon görüşmesi ya da otomatik MHRS yönlendirmesi
- **Akıllı Chat:** TanıAI asistanı ile semptom, randevu ve sağlık önerileri diyalogları
- **İlaç Takibi:** Günlük ilaç planı, doz takibi, alınmadığında hatırlatma
- **Yakın Eczane & Klinik Bulma:** Konum tabanlı öneriler
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/ilac_takibi_new.png`

## Slayt 6 – Bildirim & Hatırlatmalar
- Global bildirim yöneticisi ile özelleştirilmiş ilaç ve randevu hatırlatmaları
- Günlük sağlık rutinleri: su içme, güneşe çıkma, nefes egzersizi
- Acil durum uyarıları: yüksek riskli semptomlarda önceliklendirme
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/bildirimler.png`

## Slayt 7 – Teknoloji Mimarisi
- **Frontend:** Flutter ile Android, iOS, web ve masaüstü için tek kod tabanı
- **Backend:** FastAPI + PostgreSQL ile ölçeklenebilir mikro servis altyapısı
- **NLP:** HuggingFace Transformers, spaCy; TRIAGE için özel modeller
- **Sesli Asistan:** Whisper ASR, TTS entegrasyonu, Twilio/Google STT
- Bulut altyapısı: Firebase kimlik doğrulama, real-time veri, loglama
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/whisper_web2.png`

## Slayt 8 – Farkımız
- Erişilebilirlik odaklı tasarım (büyük tipografi, ekran okuyucu uyumu)
- Sesle çalışan randevu süreci ve işaret dili planları
- Toplumsal fayda: yaşlı, engelli ve teknolojiye uzak kitlelere odak
- MHRS ile tam uyum ve sahadaki hekim geri bildirimleriyle doğrulanmış iş akışı

## Slayt 9 – Hedefler & Yol Haritası
- 100.000+ aktif kullanıcıya erişmek ve Sağlık Bakanlığı işbirliği sağlamak
- Kısa vadede: Klinik ve eczane ağını genişletmek, kullanıcı testleri
- Orta vadede: NHS / Medicaid gibi global sistemlerle entegrasyon pilotları
- Uzun vadede: Sağlık verisi analizi ile öngörüsel bakım kabiliyetleri

## Slayt 10 – Kapanış & Davet
- “TanıAI ile randevular daha erişilebilir, semptomlar daha anlaşılır”
- İş birliği çağrısı: kamu kurumları, hastane zincirleri, yatırımcılar
- Demo daveti: canlı prototip veya video demo bağlantısı
- İletişim: hello@taniai.health (placeholder, şirket e-postası ile değiştirilebilir)
- Önerilen görsel: `RANDEVU/app_ekran_goruntuleri/whisper_web.png`
