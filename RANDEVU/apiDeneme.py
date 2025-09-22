#önceki android sürümleri için apk: 
# flutter build apk --debug --target-platform android-arm


from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="deepseek/deepseek-chat-v3.1:free",
  messages=[
    {
      "role": "user",
      "content": "Sana rahatsızlığımı söylediğim zaman bana direk olarak aşağıdaki bölümlerden hangisinden randevu almam gerektiğini söyle.  Yani şöyle: Bu durum için en uygun .... kliniğidir. Randevu oluşturmak istiyorsanız lütfen evet olarak yanıtlayınız tarzında bir şey yaz. Ek olarak o an için, doktora gidene kadar dikkat edilmesi gereken öneriler de ekleyebilirsin. KLİNİK BÖLÜMLERİ: MHRS Merkezi Hekim Randevu Sistemi'nden alınan Klinik Listesi 1. Aile Hekimliği 2. Algoloji 3. Amatem (Alkol ve Madde Bağımlılığı) 4. Anesteziyoloji ve Reanimasyon 5. Beyin ve Sinir Cerrahisi 6. Cerrahi Onkolojisi 7. Çocuk Cerrahisi 8. Çocuk Diş Hekimliği 9. Çocuk Endokrinolojisi 10. Çocuk Enfeksiyon Hastalıkları 11. Çocuk Gastroenterolojisi 12. Çocuk Genetik Hastalıkları 13. Çocuk Hematolojisi ve Onkolojisi 14. Çocuk Kalp Damar Cerrahisi 15. Çocuk Kardiyolojisi 16. Çocuk Nefrolojisi 17. Çocuk Nörolojisi 18. Çocuk Sağlığı ve Hastalıkları 19. Çocuk ve Ergen Ruh Sağlığı ve Hastalıkları 20. Deri ve Zührevi Hastalıkları (Cildiye) 21. Diş Hekimliği (Genel Diş) 22. El Cerrahisi 23. Endodont 24. Endokrinoloji ve Metabolizma Hastalıkları 25. Enfeksiyon Hastalıkları ve Klinik Mikrobiyoloji 26. Fiziksel Tıp ve Rehabilitasyon 27. Gastroenteroloji 28. Gastroenteroloji Cerrahisi 29. Genel Cerrahi 30. Geriatri 31. Göğüs Cerrahisi 32. Göğüs Hastalıkları 33. Göz Hastalıkları 	33.1 Şaşılık 	33.2 Kornea 	33.3 Oküloplasti 34. Hematoloji 35. İç Hastalıkları (Dahiliye) 36. İmmünoloji ve Alerji Hastalıkları 37. İş ve Meslek Hastalıkları 38. Jinekolojik Onkoloji Cerrahisi 39. Kadın Hastalıkları ve Doğum 40. Kalp ve Damar Cerrahisi 41. Kardiyoloji 42. Klinik Nörofizyoloji 43. Kulak Burun Boğaz Hastalıkları 44. Nefroloji 45. Neonatoloji 46. Nöroloji 47. Ortodonti 48. Ortopedi ve Travmatoloji 49. Perinatoloji 50. Periodontoloji 51. Plastik, Rekonstrüktif ve Estetik Cerrahi 52. Protetik Diş Tedavisi 53. Radyasyon Onkolojisi 54. Restoratif Diş Tedavisi 55. Romatoloji 56. Ruh Sağlığı ve Hastalıkları (Psikiyatri) 57. Sağlık Kurulu Erişkin 58. Sağlık Kurulu ÇÖZGER (Çocuk Özel Gereksinim Raporu) 59. Sigara Bırakma Danışmanlığı Birim 60. Sigarayı Bıraktırma Kliniği 61. Spor Hekimliğ 62. Tıbbi Genetik 63. Tıbbi Onkoloji 64. Üroloji 65. Ağız, Diş ve Çene Cerrahisi 66. Radyoloji"+
      
      "Şikayetim: yere düştüm ayağım çok ağrıyor ve hafif şişti."
    }
  ]
)
print(completion.choices[0].message.content)

'''
Bu durum için en uygun **Ortopedi ve Travmatoloji** kliniğidir.

Randevu oluşturmak istiyorsanız lütfen "evet" olarak yanıtlayınız.

**Doktora Gidene Kadar Dikkat Edilmesi Gerekenler:**
*   Ayağınızı mümkün olduğunca yukarıda (kalp seviyesinin üzerinde) tutmaya çalışın.
*   Şişlik olan bölgeye 15-20 dakika boyunca bir buz torbası (buzu bir havluya sararak) uygulayın. Bunu günde birkaç kez tekrarlayın.
*   Ayağınızı zorlamayın, üzerine basmaktan ve yürümekten kaçının.
*   Şişliği ve ağrıyı artıracağından, sıcak kompres veya masaj YAPMAYIN.
*   Mümkünse ayağınızı sıkı olmayan bir bandajla sararak destekleyebilirsiniz.
*   Ağrı çok şiddetliyse doktorunuza danışmadan herhangi bir ilaç kullanmayın.

'''