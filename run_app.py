#!/usr/bin/env python3
"""
Vitamin Diagnosis System - Uygulama Başlatma Scripti
Bu script uygulamayı geliştirme ortamında başlatır.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Python versiyonunu kontrol et"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 veya üzeri gerekli!")
        print(f"📊 Mevcut versiyon: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python versiyonu uygun: {sys.version}")

def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    print("🔍 Bağımlılıklar kontrol ediliyor...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pandas', 'numpy', 
        'scikit-learn', 'pydantic', 'python-jose', 'passlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ Eksik paketler: {', '.join(missing_packages)}")
        print("📦 Paketleri yüklemek için: pip install -r requirements.txt")
        return False
    
    print("✅ Tüm bağımlılıklar mevcut")
    return True

def create_directories():
    """Gerekli dizinleri oluştur"""
    print("📁 Dizinler oluşturuluyor...")
    
    directories = [
        'models',
        'logs',
        'data',
        'uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/")

def setup_environment():
    """Ortam değişkenlerini ayarla"""
    print("🔧 Ortam değişkenleri ayarlanıyor...")
    
    # Varsayılan ortam değişkenleri
    env_vars = {
        'DATABASE_URL': 'sqlite:///./vitamin_diagnosis.db',
        'SECRET_KEY': 'dev-secret-key-change-in-production',
        'DEBUG': 'True',
        'LOG_LEVEL': 'INFO'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"✅ {key} = {value}")

def start_database():
    """Veritabanını başlat (SQLite için gerekli değil)"""
    print("🗄️ Veritabanı hazırlanıyor...")
    
    # SQLite kullanıyoruz, özel başlatma gerekmiyor
    db_path = Path("vitamin_diagnosis.db")
    if not db_path.exists():
        print("📊 Yeni veritabanı oluşturulacak")
    else:
        print("✅ Mevcut veritabanı bulundu")

def start_application():
    """Uygulamayı başlat"""
    print("\n🚀 Vitamin Diagnosis System başlatılıyor...")
    print("=" * 50)
    
    try:
        # Uvicorn ile uygulamayı başlat
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]
        
        print("🌐 API URL: http://localhost:8000")
        print("📚 Swagger UI: http://localhost:8000/docs")
        print("📖 ReDoc: http://localhost:8000/redoc")
        print("\n⏹️ Durdurmak için Ctrl+C kullanın")
        print("=" * 50)
        
        # Uygulamayı başlat
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Uygulama durduruldu")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Uygulama başlatılamadı: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)

def run_tests():
    """Testleri çalıştır"""
    print("🧪 Testler çalıştırılıyor...")
    
    try:
        # Test scriptini çalıştır
        result = subprocess.run([sys.executable, "test_api.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Testler başarılı")
        else:
            print("❌ Testler başarısız")
            print(result.stdout)
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Test çalıştırma hatası: {e}")

def show_menu():
    """Ana menüyü göster"""
    print("\n🔬 Vitamin Diagnosis System")
    print("=" * 30)
    print("1. 🚀 Uygulamayı Başlat")
    print("2. 🧪 Testleri Çalıştır")
    print("3. 📊 Sistem Durumunu Kontrol Et")
    print("4. 📚 API Dokümantasyonunu Aç")
    print("5. ❌ Çıkış")
    print("=" * 30)

def check_system_status():
    """Sistem durumunu kontrol et"""
    print("\n📊 Sistem Durumu")
    print("=" * 20)
    
    # Python versiyonu
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Çalışma dizini
    print(f"📁 Çalışma Dizini: {os.getcwd()}")
    
    # Gerekli dosyalar
    required_files = [
        'app/main.py',
        'app/models.py',
        'app/schemas.py',
        'app/services.py',
        'requirements.txt'
    ]
    
    print("\n📄 Dosya Kontrolü:")
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    # Veritabanı
    db_path = Path("vitamin_diagnosis.db")
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"✅ Veritabanı: {size} bytes")
    else:
        print("📊 Veritabanı: Henüz oluşturulmamış")

def open_documentation():
    """API dokümantasyonunu aç"""
    import webbrowser
    
    print("📚 API Dokümantasyonu açılıyor...")
    
    urls = [
        "http://localhost:8000/docs",
        "http://localhost:8000/redoc"
    ]
    
    for url in urls:
        try:
            webbrowser.open(url)
            print(f"✅ {url} açıldı")
        except Exception as e:
            print(f"❌ {url} açılamadı: {e}")

def main():
    """Ana fonksiyon"""
    print("🔬 Vitamin Diagnosis System - Başlatma Aracı")
    print("=" * 50)
    
    # Sistem kontrolleri
    check_python_version()
    
    if not check_dependencies():
        print("\n❌ Bağımlılıklar eksik, lütfen önce yükleyin:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    create_directories()
    setup_environment()
    start_database()
    
    while True:
        show_menu()
        
        try:
            choice = input("\n🎯 Seçiminizi yapın (1-5): ").strip()
            
            if choice == "1":
                start_application()
            elif choice == "2":
                run_tests()
            elif choice == "3":
                check_system_status()
            elif choice == "4":
                open_documentation()
            elif choice == "5":
                print("👋 Görüşürüz!")
                break
            else:
                print("❌ Geçersiz seçim, lütfen 1-5 arası bir sayı girin")
                
        except KeyboardInterrupt:
            print("\n\n👋 Görüşürüz!")
            break
        except Exception as e:
            print(f"\n❌ Hata: {e}")

if __name__ == "__main__":
    main()
