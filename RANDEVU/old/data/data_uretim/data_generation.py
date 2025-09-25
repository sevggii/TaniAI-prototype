#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthetic Data Generation for Turkish Medical Anamnesis Classification
Generates realistic Turkish anamnesis texts for clinic prediction
"""

import pandas as pd
import random
import json
from typing import List, Dict, Tuple
import re

# Turkish clinic list from MHRS_Klinik_Listesi.txt
CLINICS = [
    "Aile Hekimliği",
    "Algoloji", 
    "Amatem (Alkol ve Madde Bağımlılığı)",
    "Anesteziyoloji ve Reanimasyon",
    "Beyin ve Sinir Cerrahisi",
    "Cerrahi Onkolojisi",
    "Çocuk Cerrahisi",
    "Çocuk Diş Hekimliği",
    "Çocuk Endokrinolojisi",
    "Çocuk Enfeksiyon Hastalıkları",
    "Çocuk Gastroenterolojisi",
    "Çocuk Genetik Hastalıkları",
    "Çocuk Hematolojisi ve Onkolojisi",
    "Çocuk Kalp Damar Cerrahisi",
    "Çocuk Kardiyolojisi",
    "Çocuk Nefrolojisi",
    "Çocuk Nörolojisi",
    "Çocuk Sağlığı ve Hastalıkları",
    "Çocuk ve Ergen Ruh Sağlığı ve Hastalıkları",
    "Deri ve Zührevi Hastalıkları (Cildiye)",
    "Diş Hekimliği (Genel Diş)",
    "El Cerrahisi",
    "Endodonti",
    "Endokrinoloji ve Metabolizma Hastalıkları",
    "Enfeksiyon Hastalıkları ve Klinik Mikrobiyoloji",
    "Fiziksel Tıp ve Rehabilitasyon",
    "Gastroenteroloji",
    "Gastroenteroloji Cerrahisi",
    "Genel Cerrahi",
    "Geriatri",
    "Göğüs Cerrahisi",
    "Göğüs Hastalıkları",
    "Göz Hastalıkları",
    "Hematoloji",
    "İç Hastalıkları (Dahiliye)",
    "İmmünoloji ve Alerji Hastalıkları",
    "İş ve Meslek Hastalıkları",
    "Jinekolojik Onkoloji Cerrahisi",
    "Kadın Hastalıkları ve Doğum",
    "Kalp ve Damar Cerrahisi",
    "Kardiyoloji",
    "Klinik Nörofizyoloji",
    "Kulak Burun Boğaz Hastalıkları",
    "Nefroloji",
    "Neonatoloji",
    "Nöroloji",
    "Ortodonti",
    "Ortopedi ve Travmatoloji",
    "Perinatoloji",
    "Periodontoloji",
    "Plastik, Rekonstrüktif ve Estetik Cerrahi",
    "Protetik Diş Tedavisi",
    "Radyasyon Onkolojisi",
    "Restoratif Diş Tedavisi",
    "Romatoloji",
    "Ruh Sağlığı ve Hastalıkları (Psikiyatri)",
    "Sağlık Kurulu Erişkin",
    "Sağlık Kurulu ÇÖZGER (Çocuk Özel Gereksinim Raporu)",
    "Sigara Bırakma Danışmanlığı Birimi",
    "Sigarayı Bıraktırma Kliniği",
    "Spor Hekimliği",
    "Tıbbi Genetik",
    "Tıbbi Onkoloji",
    "Üroloji",
    "Ağız, Diş ve Çene Cerrahisi",
    "Radyoloji"
]

# Turkish symptom and complaint templates for each clinic
CLINIC_SYMPTOMS = {
    "Aile Hekimliği": [
        "genel halsizlik", "ateş", "baş ağrısı", "mide bulantısı", "soğuk algınlığı",
        "öksürük", "boğaz ağrısı", "burun akıntısı", "yorgunluk", "iştahsızlık",
        "uyku problemi", "stres", "genel kontrol", "aşı", "kan tahlili"
    ],
    "Algoloji": [
        "kronik ağrı", "bel ağrısı", "boyun ağrısı", "eklem ağrısı", "baş ağrısı",
        "migren", "sinir ağrısı", "fibromiyalji", "ağrı kesici", "ağrı tedavisi"
    ],
    "Amatem (Alkol ve Madde Bağımlılığı)": [
        "alkol bağımlılığı", "madde bağımlılığı", "detoks", "bağımlılık tedavisi",
        "alkol bırakma", "sigara bırakma", "uyuşturucu bağımlılığı", "rehabilitasyon"
    ],
    "Anesteziyoloji ve Reanimasyon": [
        "ameliyat öncesi değerlendirme", "anestezi", "yoğun bakım", "solunum desteği",
        "sedasyon", "genel anestezi", "lokal anestezi", "postoperatif bakım"
    ],
    "Beyin ve Sinir Cerrahisi": [
        "beyin tümörü", "kafa travması", "bel fıtığı", "boyun fıtığı", "epilepsi cerrahisi",
        "hidrosefali", "anevrizma", "AVM", "beyin kanaması", "sinir sıkışması"
    ],
    "Cerrahi Onkolojisi": [
        "kanser cerrahisi", "tümör çıkarma", "onkoloji", "kemoterapi", "radyoterapi",
        "meme kanseri", "akciğer kanseri", "kolon kanseri", "mide kanseri"
    ],
    "Çocuk Cerrahisi": [
        "çocuk ameliyatı", "doğumsal anomali", "apandisit", "fıtık", "çocuk cerrahisi",
        "pediatrik cerrahi", "bebek ameliyatı", "çocuk hastalığı"
    ],
    "Çocuk Diş Hekimliği": [
        "çocuk diş", "süt dişi", "çocuk diş hekimi", "pedodonti", "çocuk ağız sağlığı",
        "diş çürüğü çocuk", "ortodonti çocuk", "çocuk diş tedavisi"
    ],
    "Çocuk Endokrinolojisi": [
        "çocuk şeker hastalığı", "büyüme hormonu", "tiroit çocuk", "çocuk endokrin",
        "diyabet çocuk", "büyüme geriliği", "erken ergenlik", "çocuk hormon"
    ],
    "Çocuk Enfeksiyon Hastalıkları": [
        "çocuk enfeksiyon", "çocuk ateş", "çocuk öksürük", "çocuk ishal", "çocuk kusma",
        "çocuk döküntü", "çocuk grip", "çocuk enfeksiyon hastalığı"
    ],
    "Çocuk Gastroenterolojisi": [
        "çocuk mide", "çocuk karın ağrısı", "çocuk ishal", "çocuk kusma", "çocuk iştahsızlık",
        "çocuk gastro", "çocuk sindirim", "çocuk beslenme"
    ],
    "Çocuk Genetik Hastalıkları": [
        "çocuk genetik", "doğumsal hastalık", "genetik test", "çocuk genetik hastalık",
        "kromozom anomalisi", "çocuk metabolik hastalık", "genetik danışmanlık"
    ],
    "Çocuk Hematolojisi ve Onkolojisi": [
        "çocuk kanser", "çocuk lösemi", "çocuk kan hastalığı", "çocuk hematoloji",
        "çocuk onkoloji", "çocuk kemik iliği", "çocuk kan kanseri"
    ],
    "Çocuk Kalp Damar Cerrahisi": [
        "çocuk kalp ameliyatı", "doğumsal kalp hastalığı", "çocuk kalp cerrahisi",
        "çocuk kalp", "pediatrik kalp", "çocuk kalp damar", "kalp deliği"
    ],
    "Çocuk Kardiyolojisi": [
        "çocuk kalp", "çocuk kardiyoloji", "çocuk kalp hastalığı", "çocuk EKG",
        "çocuk kalp muayenesi", "çocuk kalp kontrolü", "pediatrik kardiyoloji"
    ],
    "Çocuk Nefrolojisi": [
        "çocuk böbrek", "çocuk nefroloji", "çocuk idrar", "çocuk böbrek hastalığı",
        "çocuk böbrek yetmezliği", "çocuk böbrek taşı", "pediatrik nefroloji"
    ],
    "Çocuk Nörolojisi": [
        "çocuk nöroloji", "çocuk epilepsi", "çocuk baş ağrısı", "çocuk nörolojik",
        "çocuk beyin", "çocuk sinir", "pediatrik nöroloji", "çocuk nörolojik hastalık"
    ],
    "Çocuk Sağlığı ve Hastalıkları": [
        "çocuk doktoru", "çocuk hastalığı", "çocuk muayenesi", "çocuk kontrolü",
        "çocuk sağlığı", "pediatri", "çocuk hekimi", "çocuk bakımı"
    ],
    "Çocuk ve Ergen Ruh Sağlığı ve Hastalıkları": [
        "çocuk psikiyatri", "çocuk ruh sağlığı", "çocuk psikoloji", "çocuk davranış",
        "çocuk gelişim", "çocuk psikiyatrist", "pediatrik psikiyatri", "çocuk mental"
    ],
    "Deri ve Zührevi Hastalıkları (Cildiye)": [
        "cilt hastalığı", "dermatoloji", "cilt döküntü", "egzama", "sedef",
        "cilt kaşıntı", "cilt yanık", "cilt leke", "cilt kanseri", "cilt bakımı"
    ],
    "Diş Hekimliği (Genel Diş)": [
        "diş ağrısı", "diş çürüğü", "diş tedavisi", "diş hekimi", "diş dolgusu",
        "diş çekimi", "diş temizliği", "diş kontrolü", "diş bakımı", "diş protezi"
    ],
    "El Cerrahisi": [
        "el cerrahisi", "el yaralanması", "el ameliyatı", "el travması", "el kırığı",
        "el tendon", "el sinir", "el kas", "el rehabilitasyonu", "el fonksiyonu"
    ],
    "Endodonti": [
        "kanal tedavisi", "diş kökü", "endodonti", "diş siniri", "diş kök tedavisi",
        "diş içi tedavi", "diş pulpa", "diş kök kanalı", "diş kök enfeksiyonu"
    ],
    "Endokrinoloji ve Metabolizma Hastalıkları": [
        "şeker hastalığı", "diyabet", "tiroit", "hormon", "endokrinoloji",
        "metabolizma", "insülin", "glukoz", "tiroit hormonu", "büyüme hormonu"
    ],
    "Enfeksiyon Hastalıkları ve Klinik Mikrobiyoloji": [
        "enfeksiyon", "ateş", "bakteri", "virüs", "mantar", "antibiyotik",
        "enfeksiyon hastalığı", "mikrobiyoloji", "sepsis", "enfeksiyon tedavisi"
    ],
    "Fiziksel Tıp ve Rehabilitasyon": [
        "fizik tedavi", "rehabilitasyon", "kas ağrısı", "eklem ağrısı", "felç",
        "kas güçsüzlüğü", "hareket kısıtlılığı", "fizik tedavi", "egzersiz", "masaj"
    ],
    "Gastroenteroloji": [
        "mide ağrısı", "karın ağrısı", "mide bulantısı", "kusma", "ishal",
        "kabızlık", "mide ülseri", "gastrit", "reflü", "mide yanması"
    ],
    "Gastroenteroloji Cerrahisi": [
        "mide ameliyatı", "bağırsak ameliyatı", "gastro cerrahi", "mide cerrahisi",
        "bağırsak cerrahisi", "apandisit", "fıtık", "mide kanseri", "kolon cerrahisi"
    ],
    "Genel Cerrahi": [
        "ameliyat", "cerrahi", "apandisit", "fıtık", "safra kesesi", "genel cerrahi",
        "ameliyat öncesi", "cerrahi tedavi", "operasyon", "cerrahi müdahale"
    ],
    "Geriatri": [
        "yaşlılık", "geriatri", "yaşlı hasta", "demans", "alzheimer", "yaşlı bakımı",
        "yaşlı sağlığı", "geriatrik", "yaşlılık hastalığı", "yaşlı kontrolü"
    ],
    "Göğüs Cerrahisi": [
        "akciğer ameliyatı", "göğüs cerrahisi", "akciğer cerrahisi", "toraks cerrahisi",
        "akciğer kanseri", "akciğer tümörü", "göğüs ameliyatı", "akciğer cerrahi"
    ],
    "Göğüs Hastalıkları": [
        "akciğer", "göğüs", "nefes darlığı", "öksürük", "akciğer hastalığı",
        "astım", "KOAH", "zatürre", "akciğer enfeksiyonu", "göğüs hastalığı"
    ],
    "Göz Hastalıkları": [
        "göz", "görme", "göz ağrısı", "göz kaşıntı", "göz kızarıklık", "göz sulanma",
        "görme bozukluğu", "göz muayenesi", "göz kontrolü", "oftalmoloji"
    ],
    "Hematoloji": [
        "kan hastalığı", "hematoloji", "anemi", "lösemi", "kan kanseri", "kan tahlili",
        "kan sayımı", "kan pıhtılaşması", "kanama", "kan hastalığı"
    ],
    "İç Hastalıkları (Dahiliye)": [
        "dahiliye", "iç hastalıkları", "genel muayene", "iç organ", "dahiliye muayenesi",
        "iç hastalık", "dahiliye kontrolü", "iç organ hastalığı", "dahiliye hekimi"
    ],
    "İmmünoloji ve Alerji Hastalıkları": [
        "alerji", "immünoloji", "alerjik reaksiyon", "alerji testi", "bağışıklık",
        "alerji tedavisi", "immün sistem", "alerji uzmanı", "alerji hastalığı"
    ],
    "İş ve Meslek Hastalıkları": [
        "iş hastalığı", "meslek hastalığı", "iş kazası", "meslek hastalığı",
        "iş sağlığı", "meslek sağlığı", "iş güvenliği", "meslek hastalığı"
    ],
    "Jinekolojik Onkoloji Cerrahisi": [
        "kadın kanser", "jinekolojik kanser", "rahim kanseri", "yumurtalık kanseri",
        "serviks kanseri", "kadın onkoloji", "jinekolojik cerrahi", "kadın kanser cerrahisi"
    ],
    "Kadın Hastalıkları ve Doğum": [
        "kadın hastalığı", "jinekoloji", "doğum", "hamilelik", "kadın sağlığı",
        "rahim", "yumurtalık", "adet", "menopoz", "kadın kontrolü"
    ],
    "Kalp ve Damar Cerrahisi": [
        "kalp ameliyatı", "kalp cerrahisi", "bypass", "kalp kapak", "kalp cerrahi",
        "damar cerrahisi", "kalp damar", "kalp operasyonu", "kalp cerrahi tedavi"
    ],
    "Kardiyoloji": [
        "kalp", "kardiyoloji", "kalp hastalığı", "kalp ağrısı", "kalp çarpıntısı",
        "kalp kontrolü", "EKG", "kalp muayenesi", "kalp sağlığı", "kardiyoloji"
    ],
    "Klinik Nörofizyoloji": [
        "nörofizyoloji", "EEG", "EMG", "sinir testi", "kas testi", "nörolojik test",
        "sinir iletimi", "kas elektromiyografisi", "beyin dalgaları", "nörofizyoloji"
    ],
    "Kulak Burun Boğaz Hastalıkları": [
        "kulak", "burun", "boğaz", "KBB", "kulak ağrısı", "burun tıkanıklığı",
        "boğaz ağrısı", "işitme", "kulak burun boğaz", "KBB muayenesi"
    ],
    "Nefroloji": [
        "böbrek", "nefroloji", "böbrek hastalığı", "böbrek yetmezliği", "böbrek taşı",
        "idrar", "böbrek fonksiyonu", "böbrek kontrolü", "böbrek muayenesi", "diyaliz"
    ],
    "Neonatoloji": [
        "yenidoğan", "neonatoloji", "bebek", "prematüre", "yenidoğan bakımı",
        "bebek bakımı", "neonatal", "yenidoğan hastalığı", "bebek sağlığı"
    ],
    "Nöroloji": [
        "nöroloji", "beyin", "sinir", "baş ağrısı", "migren", "epilepsi", "felç",
        "nörolojik", "beyin hastalığı", "sinir hastalığı", "nörolojik muayene"
    ],
    "Ortodonti": [
        "ortodonti", "diş teli", "çarpık diş", "diş düzeltme", "ortodontik tedavi",
        "diş bozukluğu", "çene bozukluğu", "diş estetiği", "ortodonti tedavisi"
    ],
    "Ortopedi ve Travmatoloji": [
        "ortopedi", "kırık", "çıkık", "eklem", "kemik", "kas", "tendon", "ligament",
        "travma", "ortopedik", "kemik hastalığı", "eklem hastalığı"
    ],
    "Perinatoloji": [
        "perinatoloji", "riskli gebelik", "gebelik komplikasyonu", "anne karnı",
        "fetal", "gebelik takibi", "riskli hamilelik", "perinatal", "gebelik riski"
    ],
    "Periodontoloji": [
        "periodontoloji", "diş eti", "diş eti hastalığı", "periodontal", "diş eti tedavisi",
        "diş eti çekilmesi", "diş eti kanaması", "periodontal hastalık", "diş eti bakımı"
    ],
    "Plastik, Rekonstrüktif ve Estetik Cerrahi": [
        "plastik cerrahi", "estetik cerrahi", "rekonstrüktif cerrahi", "estetik",
        "güzellik", "plastik cerrahi", "estetik ameliyat", "rekonstrüksiyon", "estetik tedavi"
    ],
    "Protetik Diş Tedavisi": [
        "protez", "diş protezi", "takma diş", "diş protezi", "protez tedavisi",
        "diş protezi", "protez bakımı", "diş protezi", "protez kontrolü"
    ],
    "Radyasyon Onkolojisi": [
        "radyoterapi", "ışın tedavisi", "radyasyon", "onkoloji", "kanser tedavisi",
        "radyasyon onkolojisi", "ışın tedavisi", "radyoterapi", "kanser radyoterapi"
    ],
    "Restoratif Diş Tedavisi": [
        "diş restorasyonu", "diş onarımı", "diş dolgusu", "diş kaplama", "diş kronu",
        "diş köprü", "diş implant", "diş restoratif", "diş tedavisi"
    ],
    "Romatoloji": [
        "romatoloji", "romatizma", "eklem romatizması", "artrit", "romatoid artrit",
        "eklem ağrısı", "romatizmal hastalık", "romatizma tedavisi", "romatolojik"
    ],
    "Ruh Sağlığı ve Hastalıkları (Psikiyatri)": [
        "psikiyatri", "ruh sağlığı", "depresyon", "anksiyete", "psikiyatrist",
        "mental sağlık", "psikolojik", "ruh hastalığı", "psikiyatrik", "mental hastalık"
    ],
    "Sağlık Kurulu Erişkin": [
        "sağlık kurulu", "rapor", "sağlık raporu", "medikal rapor", "sağlık kurulu",
        "tıbbi rapor", "sağlık belgesi", "medikal belge", "sağlık kurulu raporu"
    ],
    "Sağlık Kurulu ÇÖZGER (Çocuk Özel Gereksinim Raporu)": [
        "çözger", "çocuk özel gereksinim", "çocuk raporu", "özel gereksinim",
        "çocuk sağlık raporu", "çözger raporu", "çocuk özel rapor", "çocuk gereksinim raporu"
    ],
    "Sigara Bırakma Danışmanlığı Birimi": [
        "sigara bırakma", "sigara bırakma danışmanlığı", "sigara tedavisi",
        "sigara bırakma programı", "sigara bırakma desteği", "sigara bırakma kliniği"
    ],
    "Sigarayı Bıraktırma Kliniği": [
        "sigara bırakma", "sigara bırakma kliniği", "sigara tedavisi",
        "sigara bırakma programı", "sigara bırakma desteği", "sigara bırakma kliniği"
    ],
    "Spor Hekimliği": [
        "spor hekimliği", "spor yaralanması", "spor sağlığı", "sporcu sağlığı",
        "spor hekimi", "spor yaralanması", "spor sağlığı", "sporcu kontrolü"
    ],
    "Tıbbi Genetik": [
        "genetik", "tıbbi genetik", "genetik test", "genetik danışmanlık",
        "genetik hastalık", "genetik analiz", "genetik muayene", "genetik kontrol"
    ],
    "Tıbbi Onkoloji": [
        "onkoloji", "kanser", "kemoterapi", "kanser tedavisi", "tıbbi onkoloji",
        "kanser ilaç", "onkoloji tedavisi", "kanser ilaç tedavisi", "medikal onkoloji"
    ],
    "Üroloji": [
        "üroloji", "böbrek", "idrar", "mesane", "prostat", "erkek sağlığı",
        "ürolojik", "idrar yolu", "böbrek taşı", "ürolojik muayene"
    ],
    "Ağız, Diş ve Çene Cerrahisi": [
        "ağız cerrahisi", "diş cerrahisi", "çene cerrahisi", "oral cerrahi",
        "diş çekimi", "20 yaş dişi", "çene ameliyatı", "ağız cerrahi", "oral cerrahi"
    ],
    "Radyoloji": [
        "radyoloji", "film", "ultrason", "tomografi", "MR", "radyoloji muayenesi",
        "görüntüleme", "radyoloji raporu", "radyoloji kontrolü", "radyolojik"
    ]
}

# Turkish sentence starters and connectors
SENTENCE_STARTERS = [
    "Hastamız", "Hasta", "Şikayet", "Yakınma", "Problem", "Sorun", "Durum",
    "Hastalık", "Belirti", "Semptom", "Rahatsızlık", "Ağrı", "Sıkıntı"
]

CONNECTORS = [
    "ile", "ve", "ayrıca", "bunun yanında", "ek olarak", "üstelik", "hem de",
    "bir de", "aynı zamanda", "bununla birlikte", "birlikte", "beraber"
]

TIME_EXPRESSIONS = [
    "son 1 haftadır", "son 2 gündür", "son 3 gündür", "son 1 aydır", "son 2 haftadır",
    "dün", "bugün", "bu sabah", "bu akşam", "geçen hafta", "geçen ay", "uzun süredir",
    "yaklaşık 1 haftadır", "yaklaşık 2 gündür", "yaklaşık 1 aydır"
]

SEVERITY_EXPRESSIONS = [
    "hafif", "orta", "şiddetli", "çok şiddetli", "dayanılmaz", "katlanılmaz",
    "rahatsız edici", "can sıkıcı", "zorlayıcı", "engelleyici"
]

def generate_anamnesis_text(clinic: str, symptoms: List[str]) -> str:
    """Generate a realistic Turkish anamnesis text for a given clinic"""
    
    # Select 1-3 symptoms randomly
    selected_symptoms = random.sample(symptoms, min(random.randint(1, 3), len(symptoms)))
    
    # Select time expression
    time_expr = random.choice(TIME_EXPRESSIONS)
    
    # Select severity
    severity = random.choice(SEVERITY_EXPRESSIONS)
    
    # Select sentence starter
    starter = random.choice(SENTENCE_STARTERS)
    
    # Build the anamnesis text
    if len(selected_symptoms) == 1:
        text = f"{starter} {time_expr} {selected_symptoms[0]} şikayeti ile başvurdu."
    elif len(selected_symptoms) == 2:
        connector = random.choice(CONNECTORS)
        text = f"{starter} {time_expr} {selected_symptoms[0]} {connector} {selected_symptoms[1]} şikayeti ile başvurdu."
    else:
        connector1 = random.choice(CONNECTORS)
        connector2 = random.choice(CONNECTORS)
        text = f"{starter} {time_expr} {selected_symptoms[0]} {connector1} {selected_symptoms[1]} {connector2} {selected_symptoms[2]} şikayeti ile başvurdu."
    
    # Add severity information
    if random.random() < 0.7:  # 70% chance to add severity
        text += f" Ağrı {severity} düzeyde."
    
    # Add additional context (30% chance)
    if random.random() < 0.3:
        additional_contexts = [
            " Gece uykuyu bölüyor.",
            " Günlük aktiviteleri etkiliyor.",
            " İlaç kullanımına rağmen devam ediyor.",
            " Son günlerde artış gösteriyor.",
            " Dinlenmeyle azalıyor.",
            " Hareketle artıyor."
        ]
        text += random.choice(additional_contexts)
    
    return text

def generate_dataset(num_samples: int, split: str = "train") -> pd.DataFrame:
    """Generate synthetic dataset with Turkish anamnesis texts"""
    
    data = []
    samples_per_clinic = num_samples // len(CLINICS)
    remaining_samples = num_samples % len(CLINICS)
    
    for i, clinic in enumerate(CLINICS):
        # Calculate samples for this clinic
        clinic_samples = samples_per_clinic
        if i < remaining_samples:
            clinic_samples += 1
        
        # Generate samples for this clinic
        for _ in range(clinic_samples):
            symptoms = CLINIC_SYMPTOMS.get(clinic, ["genel şikayet"])
            anamnesis = generate_anamnesis_text(clinic, symptoms)
            
            data.append({
                'anamnesis': anamnesis,
                'clinic': clinic,
                'split': split
            })
    
    # Shuffle the data
    random.shuffle(data)
    
    return pd.DataFrame(data)

def save_dataset(train_df: pd.DataFrame, test_df: pd.DataFrame):
    """Save datasets to CSV files"""
    
    # Save training data
    train_df[['anamnesis', 'clinic']].to_csv('data/train.csv', index=False, encoding='utf-8')
    
    # Save test data  
    test_df[['anamnesis', 'clinic']].to_csv('data/test.csv', index=False, encoding='utf-8')
    
    print(f"Training dataset saved: {len(train_df)} samples")
    print(f"Test dataset saved: {len(test_df)} samples")
    
    # Print sample distribution
    print("\nTraining data distribution:")
    print(train_df['clinic'].value_counts().head(10))
    
    print("\nTest data distribution:")
    print(test_df['clinic'].value_counts().head(10))

def main():
    """Main function to generate synthetic data"""
    
    print("Generating synthetic Turkish anamnesis dataset...")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate training data (1200 samples)
    print("Generating training data...")
    train_df = generate_dataset(1200, "train")
    
    # Generate test data (1200 samples)
    print("Generating test data...")
    test_df = generate_dataset(1200, "test")
    
    # Save datasets
    save_dataset(train_df, test_df)
    
    # Save clinic list for reference
    with open('data/clinics.json', 'w', encoding='utf-8') as f:
        json.dump(CLINICS, f, ensure_ascii=False, indent=2)
    
    print("\nDataset generation completed!")
    print(f"Total clinics: {len(CLINICS)}")
    print(f"Total training samples: {len(train_df)}")
    print(f"Total test samples: {len(test_df)}")

if __name__ == "__main__":
    main()
