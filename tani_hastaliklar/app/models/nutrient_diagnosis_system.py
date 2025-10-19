from typing import Dict, List, Any
from .nutrient_models import NutrientDeficiencyModel

class NutrientDiagnosisSystem:
    def __init__(self):
        # MVP: Vitamin D, B12, Demir, Çinko, Magnezyum
        self.mvp_nutrients = ['D', 'B12', 'Demir', 'Cinko', 'Magnezyum']
        
        # Genişletilmiş: Vitamin A, C, E, Folat (B9), Kalsiyum, Potasyum, Selenyum
        self.extended_nutrients = ['A', 'C', 'E', 'B9', 'Kalsiyum', 'Potasyum', 'Selenyum']
        
        # Yeni Teşhis Modülleri: Hepatit B, Gebelik, Tiroid
        self.diagnosis_modules = ['HepatitB', 'Gebelik', 'Tiroid']
        
        # Tüm nutrientler + teşhis modülleri
        self.all_nutrients = self.mvp_nutrients + self.extended_nutrients + self.diagnosis_modules
        
        self.models = {}
        self.all_symptoms = set()
        self.load_all_models()
        self.collect_all_symptoms()
    
    def load_all_models(self):
        """Tüm nutrient modellerini yükler"""
        print("🔄 Nutrient modelleri yükleniyor...")
        for nutrient in self.all_nutrients:
            self.models[nutrient] = NutrientDeficiencyModel(nutrient)
            self.models[nutrient].load_model()
        print("✅ Tüm nutrient modelleri yüklendi")
    
    def collect_all_symptoms(self):
        """Tüm semptomları toplar"""
        for nutrient, model in self.models.items():
            self.all_symptoms.update(model.symptoms)
        print(f"✅ Toplam {len(self.all_symptoms)} semptom toplandı")
    
    def diagnose_all_nutrients(self, symptoms_dict: Dict[str, int]) -> Dict[str, Any]:
        """Tüm nutrientler için teşhis yapar"""
        results = {}
        
        for nutrient, model in self.models.items():
            try:
                prediction = model.predict(symptoms_dict)
                recommendations = model.get_recommendations(prediction)
                
                results[nutrient] = {
                    'prediction': prediction,
                    'recommendations': recommendations
                }
            except Exception as e:
                print(f"⚠️ {nutrient} teşhisinde hata: {e}")
                results[nutrient] = {
                    'prediction': {'nutrient': nutrient, 'deficiency_probability': 0.0, 'prediction': 0, 'risk_level': 'Düşük', 'confidence': 0.0},
                    'recommendations': {'immediate_actions': [], 'dietary_recommendations': [], 'supplement_recommendations': [], 'tests_recommended': []}
                }
        
        return results
    
    def get_priority_nutrients(self, results: Dict[str, Any]) -> List[str]:
        """Risk seviyesine göre öncelikli nutrientleri döndürür"""
        priority_list = []
        
        for nutrient, data in results.items():
            prediction = data['prediction']
            # Tıbbi literatüre dayalı eşik - %30'dan yüksek olasılık varsa öncelikli
            if prediction['deficiency_probability'] > 0.30:
                priority_list.append({
                    'nutrient': nutrient,
                    'probability': prediction['deficiency_probability'],
                    'risk_level': prediction['risk_level'],
                    'confidence': prediction['confidence']
                })
        
        # Olasılığa göre sırala
        priority_list.sort(key=lambda x: x['probability'], reverse=True)
        
        return [item['nutrient'] for item in priority_list]
    
    def get_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Genel özet raporu oluşturur"""
        deficient_nutrients = []
        high_risk_nutrients = []
        mvp_deficient = []
        extended_deficient = []
        total_risk_score = 0
        
        for nutrient, data in results.items():
            prediction = data['prediction']
            # Tıbbi literatüre dayalı eşik - %30'dan yüksek olasılık varsa eksik
            if prediction['deficiency_probability'] > 0.30:
                deficient_nutrients.append(nutrient)
                total_risk_score += prediction['deficiency_probability']
                
                if prediction['risk_level'] == 'Yüksek':
                    high_risk_nutrients.append(nutrient)
                
                if nutrient in self.mvp_nutrients:
                    mvp_deficient.append(nutrient)
                else:
                    extended_deficient.append(nutrient)
        
        # Genel risk seviyesi
        if len(deficient_nutrients) == 0:
            overall_risk = "Düşük"
        elif len(high_risk_nutrients) > 0:
            overall_risk = "Yüksek"
        elif len(deficient_nutrients) >= 3:
            overall_risk = "Orta"
        else:
            overall_risk = "Düşük"
        
        return {
            'total_nutrients_checked': len(self.all_nutrients),
            'deficient_nutrients': deficient_nutrients,
            'high_risk_nutrients': high_risk_nutrients,
            'mvp_deficient': mvp_deficient,
            'extended_deficient': extended_deficient,
            'overall_risk_level': overall_risk,
            'total_risk_score': total_risk_score,
            'deficiency_count': len(deficient_nutrients)
        }
    
    def get_overall_recommendations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Genel önerileri toplar"""
        all_immediate_actions = set()
        all_dietary_recommendations = set()
        all_supplement_recommendations = set()
        all_tests_recommended = set()
        
        for nutrient, data in results.items():
            recommendations = data['recommendations']
            
            all_immediate_actions.update(recommendations['immediate_actions'])
            all_dietary_recommendations.update(recommendations['dietary_recommendations'])
            all_supplement_recommendations.update(recommendations['supplement_recommendations'])
            all_tests_recommended.update(recommendations['tests_recommended'])
        
        return {
            'immediate_actions': list(all_immediate_actions),
            'dietary_recommendations': list(all_dietary_recommendations),
            'supplement_recommendations': list(all_supplement_recommendations),
            'tests_recommended': list(all_tests_recommended)
        }
    
    def get_all_symptoms(self) -> List[str]:
        """Tüm semptomları döndürür"""
        return sorted(list(self.all_symptoms))
    
    def train_all_models(self):
        """Tüm modelleri yeniden eğitir"""
        print("🔄 Tüm nutrient modelleri yeniden eğitiliyor...")
        for nutrient, model in self.models.items():
            model.train_model()
            model.save_model()
        print("✅ Tüm modeller eğitildi ve kaydedildi")
    
    def get_nutrient_info(self, nutrient: str) -> Dict[str, Any]:
        """Nutrient hakkında bilgi döndürür"""
        nutrient_info = {
            'D': {
                'name': 'D Vitamini (Kolekalsiferol)',
                'type': 'Vitamin',
                'function': 'Kemik sağlığı, kalsiyum emilimi, bağışıklık sistemi',
                'sources': 'Güneş ışığı, yağlı balık, yumurta, mantar',
                'deficiency_effects': 'Raşitizm, kemik ağrıları, kas zayıflığı, depresyon',
                'mvp': True,
                'reference_ranges': {
                    'serum_25_oh_d': {
                        'normal': '30-100 ng/mL',
                        'insufficient': '20-29 ng/mL',
                        'deficient': '<20 ng/mL',
                        'toxic': '>100 ng/mL'
                    },
                    'daily_intake': {
                        'adults': '600-800 IU (15-20 mcg)',
                        'elderly': '800-1000 IU (20-25 mcg)',
                        'pregnancy': '600-800 IU (15-20 mcg)'
                    }
                }
            },
            'B12': {
                'name': 'B12 Vitamini (Kobalamin)',
                'type': 'Vitamin',
                'function': 'Sinir sistemi, kırmızı kan hücreleri, DNA sentezi',
                'sources': 'Et, süt, yumurta, balık, karaciğer',
                'deficiency_effects': 'Pernisiyöz anemi, nörolojik sorunlar, hafıza kaybı',
                'mvp': True,
                'reference_ranges': {
                    'serum_b12': {
                        'normal': '200-900 pg/mL',
                        'borderline': '150-200 pg/mL',
                        'deficient': '<150 pg/mL',
                        'optimal': '>400 pg/mL'
                    },
                    'daily_intake': {
                        'adults': '2.4 mcg',
                        'pregnancy': '2.6 mcg',
                        'lactation': '2.8 mcg'
                    }
                }
            },
            'Demir': {
                'name': 'Demir (Iron)',
                'type': 'Mineral',
                'function': 'Oksijen taşınması, enerji üretimi, bağışıklık',
                'sources': 'Kırmızı et, karaciğer, ıspanak, baklagiller',
                'deficiency_effects': 'Anemi, yorgunluk, halsizlik, baş dönmesi, saç dökülmesi, tırnak bozukluğu',
                'mvp': True,
                'reference_ranges': {
                    'serum_ferritin': {
                        'men': '30-400 ng/mL',
                        'women': '15-150 ng/mL',
                        'deficient_men': '<30 ng/mL',
                        'deficient_women': '<15 ng/mL'
                    },
                    'serum_iron': {
                        'normal': '60-170 mcg/dL',
                        'deficient': '<60 mcg/dL'
                    },
                    'transferrin_saturation': {
                        'normal': '20-50%',
                        'deficient': '<20%'
                    },
                    'daily_intake': {
                        'men': '8 mg',
                        'women': '18 mg',
                        'pregnancy': '27 mg'
                    }
                }
            },
            'Cinko': {
                'name': 'Çinko (Zinc)',
                'type': 'Mineral',
                'function': 'Bağışıklık sistemi, yara iyileşmesi, protein sentezi',
                'sources': 'Et, kabuklu deniz ürünleri, fındık, tam tahıllar',
                'deficiency_effects': 'Enfeksiyon yatkınlığı, yavaş iyileşme, tat bozukluğu, saç dökülmesi, tırnak bozukluğu',
                'mvp': True,
                'reference_ranges': {
                    'serum_zinc': {
                        'normal': '70-120 mcg/dL',
                        'deficient': '<70 mcg/dL',
                        'toxic': '>150 mcg/dL'
                    },
                    'daily_intake': {
                        'men': '11 mg',
                        'women': '8 mg',
                        'pregnancy': '11 mg',
                        'lactation': '12 mg'
                    }
                }
            },
            'Magnezyum': {
                'name': 'Magnezyum (Magnesium)',
                'type': 'Mineral',
                'function': 'Kas ve sinir fonksiyonları, enerji üretimi, kemik sağlığı',
                'sources': 'Yeşil yapraklı sebzeler, fındık, tohumlar, tam tahıllar',
                'deficiency_effects': 'Kas krampları, uyuşma, kalp çarpıntısı, yorgunluk',
                'mvp': True,
                'reference_ranges': {
                    'serum_magnesium': {
                        'normal': '1.7-2.2 mg/dL',
                        'deficient': '<1.7 mg/dL',
                        'toxic': '>3.0 mg/dL'
                    },
                    'rbc_magnesium': {
                        'normal': '4.0-6.0 mg/dL',
                        'deficient': '<4.0 mg/dL'
                    },
                    'daily_intake': {
                        'men': '400-420 mg',
                        'women': '310-320 mg',
                        'pregnancy': '350-360 mg',
                        'lactation': '310-320 mg'
                    }
                }
            },
            'A': {
                'name': 'A Vitamini (Retinol)',
                'type': 'Vitamin',
                'function': 'Görme, bağışıklık sistemi, cilt sağlığı',
                'sources': 'Karaciğer, havuç, ıspanak, tatlı patates',
                'deficiency_effects': 'Gece körlüğü, kuru cilt, enfeksiyonlara yatkınlık',
                'mvp': False,
                'reference_ranges': {
                    'serum_retinol': {
                        'normal': '30-60 mcg/dL',
                        'deficient': '<20 mcg/dL',
                        'toxic': '>100 mcg/dL'
                    },
                    'daily_intake': {
                        'men': '900 mcg RAE',
                        'women': '700 mcg RAE',
                        'pregnancy': '770 mcg RAE',
                        'lactation': '1300 mcg RAE'
                    }
                }
            },
            'C': {
                'name': 'C Vitamini (Askorbik Asit)',
                'type': 'Vitamin',
                'function': 'Bağışıklık sistemi, kolajen sentezi, antioksidan',
                'sources': 'Turunçgiller, çilek, brokoli, kivi',
                'deficiency_effects': 'Skorbüt, yavaş iyileşme, diş eti kanaması',
                'mvp': False,
                'reference_ranges': {
                    'serum_ascorbic_acid': {
                        'normal': '0.6-2.0 mg/dL',
                        'deficient': '<0.2 mg/dL',
                        'optimal': '>1.0 mg/dL'
                    },
                    'daily_intake': {
                        'adults': '90 mg (men), 75 mg (women)',
                        'pregnancy': '85 mg',
                        'lactation': '120 mg',
                        'smokers': '+35 mg'
                    }
                }
            },
            'E': {
                'name': 'E Vitamini (Tokoferol)',
                'type': 'Vitamin',
                'function': 'Antioksidan, hücre koruması, bağışıklık',
                'sources': 'Fındık, tohumlar, bitkisel yağlar, avokado',
                'deficiency_effects': 'Sinir hasarı, kas zayıflığı, görme sorunları',
                'mvp': False,
                'reference_ranges': {
                    'serum_alpha_tocopherol': {
                        'normal': '5-20 mg/L',
                        'deficient': '<5 mg/L',
                        'optimal': '>12 mg/L'
                    },
                    'daily_intake': {
                        'adults': '15 mg (22.4 IU)',
                        'pregnancy': '15 mg',
                        'lactation': '19 mg'
                    }
                }
            },
            'B9': {
                'name': 'B9 Vitamini (Folat)',
                'type': 'Vitamin',
                'function': 'DNA sentezi, kırmızı kan hücreleri, gebelik sağlığı',
                'sources': 'Yeşil yapraklı sebzeler, baklagiller, karaciğer',
                'deficiency_effects': 'Anemi, doğum kusurları, hafıza sorunları',
                'mvp': False,
                'reference_ranges': {
                    'serum_folate': {
                        'normal': '3-20 ng/mL',
                        'deficient': '<3 ng/mL',
                        'optimal': '>7 ng/mL'
                    },
                    'rbc_folate': {
                        'normal': '140-628 ng/mL',
                        'deficient': '<140 ng/mL'
                    },
                    'daily_intake': {
                        'adults': '400 mcg DFE',
                        'pregnancy': '600 mcg DFE',
                        'lactation': '500 mcg DFE'
                    }
                }
            },
            'Kalsiyum': {
                'name': 'Kalsiyum (Calcium)',
                'type': 'Mineral',
                'function': 'Kemik ve diş sağlığı, kas kasılması, sinir iletimi',
                'sources': 'Süt ürünleri, yeşil yapraklı sebzeler, sardalya',
                'deficiency_effects': 'Osteoporoz, kas krampları, diş bozuklukları',
                'mvp': False,
                'reference_ranges': {
                    'serum_calcium': {
                        'normal': '8.5-10.5 mg/dL',
                        'deficient': '<8.5 mg/dL',
                        'toxic': '>10.5 mg/dL'
                    },
                    'ionized_calcium': {
                        'normal': '4.5-5.3 mg/dL',
                        'deficient': '<4.5 mg/dL'
                    },
                    'daily_intake': {
                        'adults': '1000-1200 mg',
                        'women_50+': '1200 mg',
                        'men_70+': '1200 mg',
                        'pregnancy': '1000 mg',
                        'lactation': '1000 mg'
                    }
                }
            },
            'Potasyum': {
                'name': 'Potasyum (Potassium)',
                'type': 'Mineral',
                'function': 'Kalp ritmi, kas fonksiyonları, kan basıncı',
                'sources': 'Muz, patates, ıspanak, avokado',
                'deficiency_effects': 'Kas güçsüzlüğü, kalp ritim bozukluğu, yorgunluk',
                'mvp': False,
                'reference_ranges': {
                    'serum_potassium': {
                        'normal': '3.5-5.0 mEq/L',
                        'deficient': '<3.5 mEq/L',
                        'toxic': '>5.0 mEq/L'
                    },
                    'daily_intake': {
                        'adults': '3500-4700 mg',
                        'pregnancy': '3500 mg',
                        'lactation': '3500 mg'
                    }
                }
            },
            'Selenyum': {
                'name': 'Selenyum (Selenium)',
                'type': 'Mineral',
                'function': 'Antioksidan, tiroid sağlığı, bağışıklık',
                'sources': 'Balık, fındık, et, yumurta',
                'deficiency_effects': 'Yorgunluk, kas güçsüzlüğü, bağışıklık düşüklüğü',
                'mvp': False,
                'reference_ranges': {
                    'serum_selenium': {
                        'normal': '70-150 mcg/L',
                        'deficient': '<70 mcg/L',
                        'toxic': '>400 mcg/L'
                    },
                    'daily_intake': {
                        'adults': '55 mcg',
                        'pregnancy': '60 mcg',
                        'lactation': '70 mcg'
                    }
                }
            },
            'HepatitB': {
                'name': 'Hepatit B',
                'type': 'Viral Enfeksiyon',
                'function': 'Karaciğer enfeksiyonu',
                'sources': 'Kan, cinsel temas, anneden bebeğe',
                'deficiency_effects': 'Sarılık, yorgunluk, karın ağrısı, bulantı',
                'mvp': True,
                'reference_ranges': {
                    'hbsag': {
                        'negative': '<0.05 IU/mL',
                        'positive': '>0.05 IU/mL'
                    },
                    'anti_hbc': {
                        'negative': '<1.0 S/CO',
                        'positive': '>1.0 S/CO'
                    },
                    'viral_load': {
                        'undetectable': '<20 IU/mL',
                        'low': '20-2000 IU/mL',
                        'high': '>2000 IU/mL'
                    }
                }
            },
            'Gebelik': {
                'name': 'Gebelik',
                'type': 'Fizyolojik Durum',
                'function': 'Hamilelik durumu',
                'sources': 'Döllenme sonrası',
                'deficiency_effects': 'Adet gecikmesi, bulantı, meme hassasiyeti',
                'mvp': True,
                'reference_ranges': {
                    'beta_hcg': {
                        'negative': '<5 mIU/mL',
                        'positive': '>25 mIU/mL',
                        'pregnancy_weeks': {
                            '3-4': '5-426 mIU/mL',
                            '4-5': '19-7340 mIU/mL',
                            '5-6': '1080-56500 mIU/mL'
                        }
                    }
                }
            },
            'Tiroid': {
                'name': 'Tiroid Bozukluğu',
                'type': 'Endokrin Bozukluk',
                'function': 'Metabolizma düzenleme',
                'sources': 'Genetik, iyot eksikliği, otoimmün',
                'deficiency_effects': 'Yorgunluk, kilo değişimi, saç dökülmesi',
                'mvp': True,
                'reference_ranges': {
                    'tsh': {
                        'normal': '0.4-4.0 mIU/L',
                        'hypothyroid': '>4.0 mIU/L',
                        'hyperthyroid': '<0.4 mIU/L'
                    },
                    't3': {
                        'normal': '80-200 ng/dL',
                        'low': '<80 ng/dL',
                        'high': '>200 ng/dL'
                    },
                    't4': {
                        'normal': '5.0-12.0 μg/dL',
                        'low': '<5.0 μg/dL',
                        'high': '>12.0 μg/dL'
                    }
                }
            }
        }
        
        return nutrient_info.get(nutrient, {})
    
    def get_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Demo senaryolarını döndürür"""
        return [
            {
                'name': 'Ayşe - 32 yaşında ofis çalışanı',
                'age': 32,
                'gender': 'Kadın',
                'profession': 'Ofis çalışanı',
                'symptoms': {
                    'yorgunluk': 3,
                    'halsizlik': 3,
                    'bas_donmesi': 2,
                    'enerji_dusuklugu': 3,
                    'odaklanma_sorunu': 2,
                    'cilt_solgunlugu': 2
                },
                'daily_impact': 'İşte odaklanamıyor, öğleden sonra enerji düşüklüğü hissediyor',
                'expected_results': {
                    'Demir': 0.81,
                    'D': 0.68
                },
                'recommendation': 'Demir ve Vitamin D eksikliği ihtimali yüksek. Kesin tanı için kan testi önerilir.'
            },
            {
                'name': 'Elif - 27 yaşında yeni anne',
                'age': 27,
                'gender': 'Kadın',
                'profession': 'Yeni anne',
                'symptoms': {
                    'unutkanlik': 3,
                    'sinirlilik': 3,
                    'uyusma': 2,
                    'karincalanma': 2,
                    'hafiza_sorunlari': 3,
                    'dikkat_sorunu': 2,
                    'yorgunluk': 2
                },
                'daily_impact': 'Bebek bakımı sırasında yorgunluk ve dikkatsizlik',
                'expected_results': {
                    'B12': 0.77,
                    'B9': 0.60
                },
                'recommendation': 'B12 ve Folat eksikliği ihtimali yüksek. Doktor kontrolü ve kan testi önerilir.'
            },
            {
                'name': 'Mehmet - 45 yaşında işçi',
                'age': 45,
                'gender': 'Erkek',
                'profession': 'İşçi',
                'symptoms': {
                    'sari': 3,
                    'yorgunluk': 3,
                    'karin_agrisi': 2,
                    'bulanti': 2,
                    'ates': 1,
                    'istahsizlik': 2
                },
                'daily_impact': 'İşte odaklanamıyor, sürekli yorgun hissediyor',
                'expected_results': {
                    'HepatitB': 0.85
                },
                'recommendation': 'Hepatit B enfeksiyonu ihtimali yüksek. Acil doktor kontrolü ve hepatit testleri önerilir.'
            },
            {
                'name': 'Zeynep - 28 yaşında öğretmen',
                'age': 28,
                'gender': 'Kadın',
                'profession': 'Öğretmen',
                'symptoms': {
                    'adet_gecikmesi': 3,
                    'bulanti': 2,
                    'meme_hassasiyeti': 2,
                    'yorgunluk': 2,
                    'sik_idrara_cikma': 1
                },
                'daily_impact': 'Derslerde odaklanamıyor, sürekli yorgun',
                'expected_results': {
                    'Gebelik': 0.78
                },
                'recommendation': 'Gebelik ihtimali yüksek. Gebelik testi ve doktor kontrolü önerilir.'
            },
            {
                'name': 'Ahmet - 52 yaşında memur',
                'age': 52,
                'gender': 'Erkek',
                'profession': 'Memur',
                'symptoms': {
                    'yorgunluk': 3,
                    'kilo_degisimi': 2,
                    'sac_dokulmesi': 2,
                    'kalp_carpintisi': 2,
                    'terleme': 1,
                    'titreme': 1
                },
                'daily_impact': 'İşte performans düşüklüğü, sürekli yorgunluk',
                'expected_results': {
                    'Tiroid': 0.72
                },
                'recommendation': 'Tiroid bozukluğu ihtimali yüksek. Tiroid testleri ve endokrinoloji kontrolü önerilir.'
            }
        ]