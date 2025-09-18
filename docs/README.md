Hazırladığım detaylı proje aşamaları için Drive linki: 
https://docs.google.com/document/d/1cadQ5AE0x6mB9naU3eaiiUHk9nh4kHJM1YPdK8P_96I/edit?usp=drivesdk 

Notion üzerinde eklediğim proje adımları;
https://www.notion.so/Tan-AI-Projesi-21fcb1d2e2b2809aa56ceb1a6d8fe1e4


🌍 TanıAI Randevu

Akıllı, erişilebilir ve sesle çalışan sağlık randevu & semptom analizi platformu

⸻

🚑 Hangi Sorunu Çözüyoruz?
	•	Türkiye’de MHRS randevu alma süreci karmaşık, özellikle yaşlılar ve görme engelliler için erişilebilir değil.
	•	Semptom takibi yapacak kolay bir sistem yok; kullanıcılar çoğu zaman doktora gitme ihtiyacını geç fark ediyor.

⸻

💡 Çözümümüz
	•	Sesli Asistan: Siri tarzı komutlarla (örn. “182’yi ara”) randevu alma.
	•	Whisper ASR + AI Analiz: Türkçe konuşmayı metne çevirip semptomları otomatik tanıyan yapay zekâ.
	•	MHRS Entegrasyonu: 66 farklı klinikten doğrudan randevu alma.
	•	Dostane Bildirimler: Su içme, güneşe çıkma, egzersiz gibi günlük sağlık hatırlatmaları.
	•	Erişilebilirlik: İşaret dili ve görme engelliler için sesli yönlendirme planları.

⸻

🎯 Farkımız
	•	✅ Tamamen cross-platform: Android, iOS, Web, masaüstü.
	•	✅ Toplumsal fayda odaklı: Yaşlı, engelli ve teknolojiye uzak kitleler için erişim kolaylığı.
	•	✅ Sağlık ekosistemi uyumlu: MHRS ile tam uyum.
	•	✅ Ölçeklenebilir altyapı: Firebase, modern Flutter, FastAPI.

⸻

🚀 Hedefimiz
	•	İlk etapta Türkiye’de 100.000+ aktif kullanıcıya ulaşmak.
	•	Sağlık Bakanlığı işbirliği ile ulusal randevu kolaylaştırıcı platform haline gelmek.
	•	Orta vadede globalde benzer sistemlere (NHS, Medicaid) entegre olmak.

⸻

📌 Vizyonumuz

“Sağlık hizmetlerine erişimi, herkes için kolay, hızlı ve kapsayıcı hale getiren yapay zekâ asistanı.”


----------
# TanıAI - Yapay Zeka Destekli Dijital Sağlık Platformu (Prototype)

TanıAI, bireylerin semptomlarını analiz ederek doğru uzmanlık alanlarına yönlendiren, test önerileri sunan ve kritik vakaları önceliklendiren bir yapay zeka tabanlı sağlık destek platformudur.

Bu prototip, yarışma kapsamında geliştirilen MVP (Minimum Viable Product) versiyonudur. Amaç, sistemin temel fonksiyonlarının teknik olarak çalıştığını göstermek ve gerçek kullanıcı senaryolarıyla test etmektir.

---

## 🎯 MVP Kapsamı

- ✅ Semptom girişi (yazılı ve/veya sesli)
- ✅ AI analiz + test önerisi (kan/röntgen vs.)
- ✅ Kritik vaka önceliklendirmesi
- ✅ Temel kullanıcı arayüzü (mobil ya da web)
- ✅ Veri kayıt/loglama sistemi (PostgreSQL + bulut entegrasyonu)
- ✅ Opsiyonel: Sesli erişim altyapısı (Twilio / Google STT)

---

## 🧠 Kullanım Akışı

1. Kullanıcı semptomlarını yazar veya sesli olarak ifade eder.
2. Sistem NLP ile analiz yapar.
3. Olası tanılar ve test önerileri listelenir.
4. Kritik vakalar işaretlenir.
5. Sonuçlar kullanıcı arayüzünde gösterilir.

---

## 🧰 Kullanılan Teknolojiler

| Katman      | Teknoloji                          |
|-------------|------------------------------------|
| Backend     | FastAPI, PostgreSQL                |
| NLP         | HuggingFace Transformers, spaCy   |
| Frontend    | Flutter veya React                 |
| Sesli Sistem| Twilio / Google Speech-to-Text     |

---

## 📁 Klasör Yapısı
/backend → API, analiz, veri yönetimi

/frontend → Kullanıcı arayüzü

/ml_model → NLP modeli, örnek veriler

/docs → Proje dökümanları
/test → Unit testler
