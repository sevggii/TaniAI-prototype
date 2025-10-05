"""
RAG (Retrieval-Augmented Generation) + Cache Sistemi
TF-IDF ile benzer vaka bulma ve LRU cache
"""

import json
import pickle
import logging
from typing import List, Dict, Tuple, Optional
from functools import lru_cache
from collections import Counter
import math
import re


class TFIDFRetriever:
    """TF-IDF tabanlı benzer vaka bulucu"""
    
    def __init__(self):
        self.documents = []  # Tüm belgeler
        self.document_clinics = []  # Her belgenin klinik bilgisi
        self.vocabulary = set()  # Tüm kelimeler
        self.idf_scores = {}  # IDF skorları
        self.tf_matrices = []  # TF matrisleri
        self.is_fitted = False
        
    def _normalize_text(self, text: str) -> str:
        """Metni normalize eder"""
        if not text:
            return ""
        
        # Küçük harfe çevir
        text = text.lower().strip()
        
        # Diakritik karakterleri sadeleştir
        replacements = {
            'ğ': 'g', 'Ğ': 'g',
            'ş': 's', 'Ş': 's', 
            'ı': 'i', 'İ': 'i', 'I': 'i',
            'ö': 'o', 'Ö': 'o',
            'ü': 'u', 'Ü': 'u',
            'ç': 'c', 'Ç': 'c'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Noktalama işaretlerini kaldır
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """Metni tokenlara ayırır"""
        normalized = self._normalize_text(text)
        tokens = normalized.split()
        # Stop words'leri filtrele (basit)
        stop_words = {'ve', 'ile', 'bir', 'bu', 'şu', 'o', 'da', 'de', 'ta', 'te', 'mi', 'mı', 'mu', 'mü', 'için', 'olan', 'var', 'yok'}
        return [token for token in tokens if len(token) > 2 and token not in stop_words]
    
    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Term Frequency hesaplar"""
        if not tokens:
            return {}
        
        token_count = Counter(tokens)
        total_tokens = len(tokens)
        
        tf_scores = {}
        for token, count in token_count.items():
            tf_scores[token] = count / total_tokens
        
        return tf_scores
    
    def _calculate_idf(self, documents_tokens: List[List[str]]) -> Dict[str, float]:
        """Inverse Document Frequency hesaplar"""
        total_docs = len(documents_tokens)
        idf_scores = {}
        
        for token in self.vocabulary:
            doc_count = sum(1 for doc_tokens in documents_tokens if token in doc_tokens)
            if doc_count > 0:
                idf_scores[token] = math.log(total_docs / doc_count)
            else:
                idf_scores[token] = 0.0
        
        return idf_scores
    
    def fit(self, jsonl_path: str):
        """JSONL dosyasından veri yükler ve TF-IDF hesaplar"""
        try:
            documents_tokens = []
            
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            complaint = data.get('complaint', '')
                            clinic = data.get('clinic', '')
                            
                            if complaint and clinic:
                                tokens = self._tokenize(complaint)
                                if tokens:  # Boş token listesi değilse
                                    self.documents.append(complaint)
                                    self.document_clinics.append(clinic)
                                    documents_tokens.append(tokens)
                                    self.vocabulary.update(tokens)
                                    
                        except json.JSONDecodeError:
                            logging.warning(f"JSON parse hatası - Satır {line_num}: {line[:50]}...")
                            continue
            
            if not documents_tokens:
                logging.error("Hiç geçerli belge bulunamadı")
                return
            
            # TF-IDF hesapla
            self.idf_scores = self._calculate_idf(documents_tokens)
            
            # Her belge için TF skorlarını hesapla
            for doc_tokens in documents_tokens:
                tf_scores = self._calculate_tf(doc_tokens)
                self.tf_matrices.append(tf_scores)
            
            self.is_fitted = True
            logging.info(f"✅ TF-IDF eğitildi: {len(self.documents)} belge, {len(self.vocabulary)} kelime")
            
        except FileNotFoundError:
            logging.error(f"❌ Dosya bulunamadı: {jsonl_path}")
        except Exception as e:
            logging.error(f"❌ TF-IDF eğitim hatası: {e}")
    
    def _calculate_tfidf_score(self, query_tokens: List[str], doc_tf: Dict[str, float]) -> float:
        """Query ve belge arasında TF-IDF skoru hesaplar"""
        if not query_tokens or not doc_tf:
            return 0.0
        
        score = 0.0
        for token in query_tokens:
            if token in doc_tf and token in self.idf_scores:
                score += doc_tf[token] * self.idf_scores[token]
        
        return score
    
    def retrieve_similar(self, query: str, top_k: int = 3) -> List[Dict[str, any]]:
        """Benzer belgeleri bulur"""
        if not self.is_fitted:
            logging.warning("TF-IDF henüz eğitilmemiş")
            return []
        
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        
        # Her belge için skor hesapla
        scores = []
        for i, doc_tf in enumerate(self.tf_matrices):
            score = self._calculate_tfidf_score(query_tokens, doc_tf)
            if score > 0:
                scores.append({
                    'complaint': self.documents[i],
                    'clinic': self.document_clinics[i],
                    'score': score,
                    'index': i
                })
        
        # Skora göre sırala ve en iyi k'yi al
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_k]


# Global TF-IDF retriever instance
_tfidf_retriever = None

def get_tfidf_retriever() -> TFIDFRetriever:
    """Singleton TF-IDF retriever döndürür"""
    global _tfidf_retriever
    if _tfidf_retriever is None:
        _tfidf_retriever = TFIDFRetriever()
    return _tfidf_retriever


@lru_cache(maxsize=256)
def cached_retrieve_similar(query: str, top_k: int = 3) -> Tuple:
    """
    LRU cache ile benzer belgeleri bulur
    Tuple döndürür çünkü cache hashable olmalı
    """
    retriever = get_tfidf_retriever()
    results = retriever.retrieve_similar(query, top_k)
    
    # Tuple'a çevir (cache için)
    return tuple(
        (result['complaint'], result['clinic'], result['score'], result['index'])
        for result in results
    )


def load_jsonl_embeddings(path: str) -> bool:
    """
    JSONL dosyasından TF-IDF embeddings yükler
    
    Returns:
        bool: Başarılı olup olmadığı
    """
    try:
        retriever = get_tfidf_retriever()
        retriever.fit(path)
        return retriever.is_fitted
    except Exception as e:
        logging.error(f"❌ Embeddings yükleme hatası: {e}")
        return False


def retrieve_similar(text: str, top_k: int = 3) -> List[Dict[str, any]]:
    """
    Cache'li benzer belge bulma
    
    Args:
        text: Arama metni
        top_k: Kaç sonuç döndürüleceği
    
    Returns:
        List[Dict]: Benzer belgeler
    """
    try:
        # Cache'den al
        cached_results = cached_retrieve_similar(text, top_k)
        
        # Dict'e çevir
        results = []
        for complaint, clinic, score, index in cached_results:
            results.append({
                'complaint': complaint,
                'clinic': clinic,
                'score': score,
                'index': index
            })
        
        return results
        
    except Exception as e:
        logging.error(f"❌ Benzer belge bulma hatası: {e}")
        return []


def calculate_rag_confidence(query: str, similar_docs: List[Dict[str, any]]) -> float:
    """
    RAG tabanlı güven skoru hesaplar
    
    Args:
        query: Sorgu metni
        similar_docs: Benzer belgeler
    
    Returns:
        float: RAG güven skoru [0,1]
    """
    if not similar_docs:
        return 0.0
    
    # En yüksek skor
    max_score = max(doc['score'] for doc in similar_docs)
    
    # Skorları normalize et (0-1 aralığına)
    # TF-IDF skorları genellikle 0-10 arasında olur
    normalized_score = min(1.0, max_score / 5.0)
    
    # Benzer belge sayısına göre bonus
    doc_count_bonus = min(0.2, len(similar_docs) * 0.05)
    
    final_confidence = min(1.0, normalized_score + doc_count_bonus)
    
    return final_confidence


def test_rag():
    """Test fonksiyonu"""
    print("🧪 RAG Test Sonuçları:")
    
    # Test verisi oluştur
    test_data = [
        {"complaint": "Başım çok ağrıyor", "clinic": "Nöroloji"},
        {"complaint": "Mide bulantım var", "clinic": "İç Hastalıkları (Dahiliye)"},
        {"complaint": "Göğsümde ağrı var", "clinic": "Kardiyoloji"},
        {"complaint": "Baş ağrısı ve mide bulantısı", "clinic": "İç Hastalıkları (Dahiliye)"},
        {"complaint": "Kalp çarpıntım oluyor", "clinic": "Kardiyoloji"},
    ]
    
    # Test dosyası oluştur
    test_file = "/tmp/test_clinic_data.jsonl"
    with open(test_file, 'w', encoding='utf-8') as f:
        for data in test_data:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    # TF-IDF yükle
    success = load_jsonl_embeddings(test_file)
    if not success:
        print("❌ TF-IDF yükleme başarısız")
        return
    
    # Test sorguları
    test_queries = [
        "başım ağrıyor",
        "mide bulantım var",
        "kalp sorunum var",
        "göğüs ağrısı"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Sorgu: '{query}'")
        similar = retrieve_similar(query, top_k=2)
        
        for i, doc in enumerate(similar, 1):
            print(f"  {i}. {doc['clinic']} (skor: {doc['score']:.3f})")
            print(f"     Şikayet: {doc['complaint']}")
        
        rag_confidence = calculate_rag_confidence(query, similar)
        print(f"  🎯 RAG Güven: {rag_confidence:.2f}")
    
    # Cache testi
    print(f"\n💾 Cache Testi:")
    import time
    start_time = time.time()
    retrieve_similar("başım ağrıyor", top_k=2)
    first_time = time.time() - start_time
    
    start_time = time.time()
    retrieve_similar("başım ağrıyor", top_k=2)
    second_time = time.time() - start_time
    
    print(f"  İlk çağrı: {first_time:.4f}s")
    print(f"  Cache'li çağrı: {second_time:.4f}s")
    print(f"  Hız artışı: {first_time/second_time:.1f}x")


if __name__ == "__main__":
    test_rag()
