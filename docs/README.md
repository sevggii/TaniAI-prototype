# TanıAI – Yapay Zeka Destekli Dijital Sağlık Asistanı (Prototype)

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

