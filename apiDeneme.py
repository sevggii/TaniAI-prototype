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
      "content": "düştüm ayağım ağrıyor Mhrs'de hangi bölümden randevu almalıyım?"
    }
  ]
)
print(completion.choices[0].message.content)

'''
D:\TaniAI-prototype>C:/Users/Grundig/AppData/Local/Programs/Python/Python310/python.exe d:/TaniAI-prototype/apiDeneme.py
Geçmiş olsun! Ayağınızı incittiğiniz için öncelikle çok dikkatli olmalısınız.

MHRS randevu sisteminde bu durum için en uygun bölüm **"Ortopedi ve Travmatoloji"** polikliniğidir.      

**Ortopedi ve Travmatoloji** bölümü; kemik kırıkları, eklem burkulmaları, çıkıklar, tendon ve bağ yaralanmaları gibi kas-iskelet sistemi problemleriyle ilgilenir. Düşme sonrası oluşan ayak ağrılarında muayene olmanız gereken ilk bölüm burasıdır.

---

### Randevu Almadan Önce Dikkat Etmeniz Gerekenler:

1.  **Ayağınızı Yukarı Kaldırın ve Dinlendirin.**
2.  **Mümkünse soğuk uygulama yapın:** (Buz torbasını bir havluya sararak ağrıyan ve şişen bölgeye 15-20 
dakika boyunca uygulayın. Bu, şişliği ve ağrıyı azaltacaktır).
3.  **Ayağınıza basmaktan ve yük vermekten kaçının.**
4.  **Ayağınızı sıkmayan rahat ayakkabılar giyin.**

---

### Acil Bir Durum Varsa (Bu Belirtilerden Bile Varsa):

Aşağıdaki belirtiler varsa, **randevu beklemeyin**, en yakın **acil servise** başvurun:

*   Ayağınızın üzerine hiç basamıyorsanız,
*   Ayağınızda şekil bozukluğu, çarpıklık varsa,
*   Ayağınızda çok şiddetli bir ağrı ve anormal bir şişlik oluştuysa,
*   Ayağınızı hissetmekte güçlük çekiyor, uyuşukluk varsa.

---

### MHRS'den Randevu Alırken:

1.  MHRS'nin web sitesine (www.mhrs.gov.tr) veya **ALO 182** hattına girin.
2.  Kimlik bilgilerinizle giriş yapın.
3.  "Hastane Randevusu Al" seçeneğini tıklayın.
4.  İlinizi, ilçenizi ve muayene olmak istediğiniz hastaneyi seçin.
5.  Bölüm olarak **"Ortopedi ve Travmatoloji"** yazın veya listeden seçin.
6.  Uygun tarih ve saati seçerek randevunuzu oluşturun.

Tekrar geçmiş olsun, umarım çok ciddi bir şey yoktur ve en kısa sürede iyileşirsiniz.


'''