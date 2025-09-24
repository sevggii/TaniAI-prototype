#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkish Medical Anamnesis Classification Model Training
Trains a machine learning model to predict clinic from Turkish anamnesis text
"""

import pandas as pd
import numpy as np
import re
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score
)
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

# Turkish stopwords
TURKISH_STOPWORDS = {
    'acaba', 'ama', 'ancak', 'artık', 'aslında', 'az', 'bana', 'bazı', 'belki',
    'ben', 'beni', 'benim', 'beri', 'beş', 'bile', 'bin', 'bir', 'birçok',
    'birkaç', 'birşey', 'biz', 'bizim', 'bu', 'buna', 'bunda', 'bundan',
    'bunlar', 'bunları', 'bunların', 'bunu', 'bunun', 'burada', 'çok',
    'çünkü', 'da', 'daha', 'dahi', 'de', 'defa', 'diye', 'dokuz', 'dört',
    'eğer', 'en', 'gibi', 'hem', 'hep', 'hepsi', 'her', 'hiç', 'hiçbir',
    'için', 'iki', 'ile', 'ilgili', 'ise', 'işte', 'kadar', 'karşın',
    'kendi', 'kendine', 'kendini', 'kendisi', 'kendisine', 'kendisini',
    'ki', 'kim', 'kimden', 'kime', 'kimi', 'kimse', 'mı', 'mi', 'mu',
    'mü', 'nasıl', 'ne', 'neden', 'nerede', 'nereden', 'nereye', 'niçin',
    'niye', 'o', 'olan', 'olarak', 'olduğu', 'olduğunu', 'olsa', 'olur',
    'on', 'ona', 'ondan', 'onlar', 'onlara', 'onlardan', 'onları', 'onların',
    'onu', 'onun', 'otuz', 'şey', 'şu', 'şuna', 'şunda', 'şundan', 'şunlar',
    'şunları', 'şunların', 'şunu', 'şunun', 'tüm', 'var', 've', 'veya',
    'ya', 'yani', 'yedi', 'yirmi', 'yok', 'zaten', 'zira'
}

def preprocess_turkish_text(text: str) -> str:
    """
    Preprocess Turkish text for machine learning
    """
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove Turkish-specific characters normalization
    text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u')
    text = text.replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
    
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove Turkish stopwords
    words = text.split()
    words = [word for word in words if word not in TURKISH_STOPWORDS and len(word) > 2]
    
    return ' '.join(words)

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load training and test datasets"""
    
    print("Loading datasets...")
    train_df = pd.read_csv('data/train.csv', encoding='utf-8')
    test_df = pd.read_csv('data/test.csv', encoding='utf-8')
    
    print(f"Training samples: {len(train_df)}")
    print(f"Test samples: {len(test_df)}")
    
    return train_df, test_df

def preprocess_datasets(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Preprocess the datasets"""
    
    print("Preprocessing Turkish text...")
    
    # Preprocess anamnesis text
    train_df['processed_text'] = train_df['anamnesis'].apply(preprocess_turkish_text)
    test_df['processed_text'] = test_df['anamnesis'].apply(preprocess_turkish_text)
    
    # Remove empty texts
    train_df = train_df[train_df['processed_text'].str.len() > 0]
    test_df = test_df[test_df['processed_text'].str.len() > 0]
    
    print(f"After preprocessing - Training samples: {len(train_df)}")
    print(f"After preprocessing - Test samples: {len(test_df)}")
    
    return train_df, test_df

def create_vectorizer(train_texts: List[str]) -> TfidfVectorizer:
    """Create and fit TF-IDF vectorizer"""
    
    print("Creating TF-IDF vectorizer...")
    
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),  # unigrams and bigrams
        min_df=2,  # ignore terms that appear in less than 2 documents
        max_df=0.95,  # ignore terms that appear in more than 95% of documents
        sublinear_tf=True,  # use sublinear tf scaling
        stop_words=None  # we already removed stopwords
    )
    
    vectorizer.fit(train_texts)
    
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    
    return vectorizer

def train_model(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Tuple[object, Dict]:
    """Train and evaluate multiple models"""
    
    print("Training models...")
    
    models = {
        'Logistic Regression': LogisticRegression(
            random_state=42,
            max_iter=1000,
            C=1.0
        ),
        'SVM': SVC(
            random_state=42,
            kernel='linear',
            C=1.0,
            probability=True
        )
    }
    
    results = {}
    best_model = None
    best_score = 0
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average='macro')
        micro_f1 = f1_score(y_test, y_pred, average='micro')
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'macro_f1': macro_f1,
            'micro_f1': micro_f1,
            'predictions': y_pred
        }
        
        print(f"{name} - Accuracy: {accuracy:.4f}, Macro F1: {macro_f1:.4f}, Micro F1: {micro_f1:.4f}")
        
        # Track best model
        if macro_f1 > best_score:
            best_score = macro_f1
            best_model = model
    
    return best_model, results

def evaluate_model(model: object, X_test: np.ndarray, y_test: np.ndarray, 
                  vectorizer: TfidfVectorizer, clinic_names: List[str]) -> Dict:
    """Comprehensive model evaluation"""
    
    print("\nEvaluating best model...")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    micro_f1 = f1_score(y_test, y_pred, average='micro')
    
    # Per-class metrics
    precision_per_class = precision_score(y_test, y_pred, average=None).tolist()
    recall_per_class = recall_score(y_test, y_pred, average=None).tolist()
    
    # Classification report
    class_report = classification_report(y_test, y_pred, target_names=clinic_names, output_dict=True)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    evaluation_results = {
        'accuracy': accuracy,
        'macro_f1': macro_f1,
        'micro_f1': micro_f1,
        'precision_per_class': precision_per_class,
        'recall_per_class': recall_per_class,
        'classification_report': class_report,
        'confusion_matrix': cm.tolist(),
        'predictions': y_pred.tolist(),
        'true_labels': y_test.tolist()
    }
    
    print(f"Final Results:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Micro F1: {micro_f1:.4f}")
    
    return evaluation_results

def save_model_and_results(model: object, vectorizer: TfidfVectorizer, 
                          evaluation_results: Dict, clinic_names: List[str]):
    """Save trained model and evaluation results"""
    
    print("\nSaving model and results...")
    
    # Save model
    joblib.dump(model, 'models/clinic_classifier.pkl')
    
    # Save vectorizer
    joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
    
    # Save clinic names
    with open('models/clinic_names.json', 'w', encoding='utf-8') as f:
        json.dump(clinic_names, f, ensure_ascii=False, indent=2)
    
    # Save evaluation results
    with open('results/evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(evaluation_results, f, ensure_ascii=False, indent=2)
    
    print("Model and results saved successfully!")

def create_confusion_matrix_plot(evaluation_results: Dict, clinic_names: List[str]):
    """Create and save confusion matrix plot"""
    
    print("Creating confusion matrix plot...")
    
    cm = np.array(evaluation_results['confusion_matrix'])
    
    # Create plot
    plt.figure(figsize=(20, 16))
    
    # For better visualization, we'll show only the top 20 most frequent classes
    # Calculate class frequencies
    class_counts = np.sum(cm, axis=1)
    top_classes_idx = np.argsort(class_counts)[-20:]  # Top 20 classes
    
    # Filter confusion matrix and class names
    cm_filtered = cm[np.ix_(top_classes_idx, top_classes_idx)]
    clinic_names_filtered = [clinic_names[i] for i in top_classes_idx]
    
    sns.heatmap(cm_filtered, annot=True, fmt='d', cmap='Blues',
                xticklabels=clinic_names_filtered,
                yticklabels=clinic_names_filtered)
    
    plt.title('Confusion Matrix - Top 20 Clinics', fontsize=16)
    plt.xlabel('Predicted Clinic', fontsize=12)
    plt.ylabel('True Clinic', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save plot
    plt.savefig('results/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Confusion matrix plot saved!")

def main():
    """Main training pipeline"""
    
    print("Turkish Medical Anamnesis Classification Model Training")
    print("=" * 60)
    
    # Load data
    train_df, test_df = load_data()
    
    # Preprocess data
    train_df, test_df = preprocess_datasets(train_df, test_df)
    
    # Prepare features and labels
    X_train = train_df['processed_text'].values
    y_train = train_df['clinic'].values
    X_test = test_df['processed_text'].values
    y_test = test_df['clinic'].values
    
    # Get unique clinic names
    clinic_names = sorted(train_df['clinic'].unique())
    print(f"Number of unique clinics: {len(clinic_names)}")
    
    # Create vectorizer
    vectorizer = create_vectorizer(X_train)
    
    # Transform texts to vectors
    X_train_vec = vectorizer.transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print(f"Training matrix shape: {X_train_vec.shape}")
    print(f"Test matrix shape: {X_test_vec.shape}")
    
    # Train models
    best_model, all_results = train_model(X_train_vec, y_train, X_test_vec, y_test)
    
    # Evaluate best model
    evaluation_results = evaluate_model(best_model, X_test_vec, y_test, vectorizer, clinic_names)
    
    # Save model and results
    save_model_and_results(best_model, vectorizer, evaluation_results, clinic_names)
    
    # Create confusion matrix plot
    create_confusion_matrix_plot(evaluation_results, clinic_names)
    
    print("\nTraining completed successfully!")
    print("Files saved:")
    print("- models/clinic_classifier.pkl")
    print("- models/tfidf_vectorizer.pkl") 
    print("- models/clinic_names.json")
    print("- results/evaluation_results.json")
    print("- results/confusion_matrix.png")

if __name__ == "__main__":
    main()
