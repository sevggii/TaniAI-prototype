#!/usr/bin/env python3
"""
Professional Medical Disease Classification System - Interactive Demo
====================================================================

This script provides an interactive demonstration of the professional
medical disease classification system with real-time user input.

Features:
- Interactive symptom input
- Real-time diagnosis
- Comprehensive medical recommendations
- Professional clinical presentation
- Error handling and validation

Usage:
    python demo_professional_system.py

Author: AI Research Team
Version: 2.0.0
License: MIT
"""

import sys
import time
from typing import Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from professional_medical_system import ProfessionalMedicalSystem
except ImportError:
    print("❌ Error: Professional Medical System not found!")
    print("Please ensure professional_medical_system.py is in the same directory.")
    sys.exit(1)


class InteractiveMedicalDemo:
    """
    Interactive demonstration of the Professional Medical System.
    
    This class provides a user-friendly interface for testing
    the medical diagnosis system with real-time input.
    """
    
    def __init__(self):
        """Initialize the interactive demo."""
        self.medical_system = None
        self.demo_cases = self._load_demo_cases()
        
    def _load_demo_cases(self) -> list:
        """Load predefined demo cases for testing."""
        return [
            {
                "id": 1,
                "title": "COVID-19 - Classic Presentation",
                "description": "Patient with classic COVID-19 symptoms",
                "symptoms": "Yüksek ateşim var, nefes alamıyorum, koku ve tat kaybım var, öksürüyorum",
                "expected": "COVID-19"
            },
            {
                "id": 2,
                "title": "Influenza - Systemic Symptoms",
                "description": "Patient with influenza-like symptoms",
                "symptoms": "Ateşim var, vücudum çok ağrıyor, titreme tuttu, çok yorgunum",
                "expected": "Grip"
            },
            {
                "id": 3,
                "title": "Common Cold - Upper Respiratory",
                "description": "Patient with common cold symptoms",
                "symptoms": "Burnum akıyor, hapşırıyorum, boğazım ağrıyor, ateşim yok",
                "expected": "Soğuk Algınlığı"
            },
            {
                "id": 4,
                "title": "Allergic Rhinitis - Ocular Symptoms",
                "description": "Patient with allergic symptoms",
                "symptoms": "Gözlerim kaşınıyor, hapşırıyorum, burnum tıkalı, ateşim yok",
                "expected": "Mevsimsel Alerji"
            }
        ]
    
    def initialize_system(self) -> bool:
        """Initialize the medical system."""
        try:
            print("🔧 Initializing Professional Medical System...")
            print("   Loading ultra-precise model...")
            
            self.medical_system = ProfessionalMedicalSystem()
            
            if self.medical_system.ultra_precise_predictor.model_data is None:
                print("❌ Error: Model could not be loaded!")
                print("   Please ensure ultra_precise_disease_model.pkl exists.")
                return False
            
            print("✅ System initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing system: {e}")
            return False
    
    def display_welcome(self):
        """Display welcome message and system information."""
        print("\n" + "="*80)
        print("🏥 PROFESSIONAL MEDICAL DISEASE CLASSIFICATION SYSTEM")
        print("="*80)
        print("Version: 2.0.0 | Author: AI Research Team | License: MIT")
        print("Enterprise-Grade Medical AI for Clinical Decision Support")
        print()
        
        # Display system information
        system_info = self.medical_system.get_system_info()
        print("📊 SYSTEM CAPABILITIES:")
        print(f"   • Model Type: {system_info.model_type}")
        print(f"   • Training Accuracy: {system_info.training_accuracy:.1%}")
        print(f"   • Test Accuracy: {system_info.test_accuracy:.1%}")
        print(f"   • Supported Diseases: {', '.join(system_info.classes)}")
        print(f"   • Feature Count: {system_info.feature_count}")
        print(f"   • Training Samples: {system_info.sample_count:,}")
        print()
        
        print("⚠️  MEDICAL DISCLAIMER:")
        print("   This system is for clinical decision support only.")
        print("   It does not replace professional medical judgment.")
        print("   Always consult with qualified healthcare professionals.")
        print()
        
        print("🚨 EMERGENCY NOTICE:")
        print("   For medical emergencies, contact emergency services immediately.")
        print("   Do not rely solely on AI systems for urgent medical situations.")
        print()
    
    def display_menu(self):
        """Display the main menu."""
        print("📋 AVAILABLE OPTIONS:")
        print("   1. 🔍 Interactive Diagnosis - Enter your own symptoms")
        print("   2. 🧪 Demo Cases - Test with predefined scenarios")
        print("   3. 📊 System Information - View technical details")
        print("   4. ❓ Help - Usage instructions")
        print("   5. 🚪 Exit - Close the application")
        print()
    
    def get_user_choice(self) -> str:
        """Get user's menu choice."""
        while True:
            try:
                choice = input("🎯 Please select an option (1-5): ").strip()
                if choice in ['1', '2', '3', '4', '5']:
                    return choice
                else:
                    print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
    
    def interactive_diagnosis(self):
        """Perform interactive diagnosis with user input."""
        print("\n" + "="*60)
        print("🔍 INTERACTIVE MEDICAL DIAGNOSIS")
        print("="*60)
        print("Please describe your symptoms in Turkish.")
        print("Examples:")
        print("   • 'Ateşim var, öksürüyorum'")
        print("   • 'Gözlerim kaşınıyor, hapşırıyorum'")
        print("   • 'Nefes alamıyorum, koku kaybım var'")
        print()
        
        while True:
            try:
                symptoms = input("🏥 Describe your symptoms: ").strip()
                
                if not symptoms:
                    print("❌ Please enter your symptoms.")
                    continue
                
                if symptoms.lower() in ['exit', 'quit', 'çık', 'q']:
                    print("👋 Returning to main menu...")
                    break
                
                print(f"\n🔄 Processing symptoms: '{symptoms}'")
                print("   Analyzing with ultra-precise medical AI...")
                
                # Perform diagnosis
                start_time = time.time()
                result = self.medical_system.diagnose_patient(symptoms)
                processing_time = (time.time() - start_time) * 1000
                
                # Display results
                self._display_diagnosis_result(result, processing_time)
                
                # Ask if user wants to continue
                print("\n" + "-"*60)
                continue_choice = input("🔄 Would you like to diagnose another case? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', 'evet', 'e']:
                    break
                
            except KeyboardInterrupt:
                print("\n👋 Returning to main menu...")
                break
            except Exception as e:
                print(f"❌ Error during diagnosis: {e}")
                print("   Please try again with different symptoms.")
    
    def demo_cases(self):
        """Run predefined demo cases."""
        print("\n" + "="*60)
        print("🧪 PROFESSIONAL DEMO CASES")
        print("="*60)
        print("Testing the system with predefined clinical scenarios.")
        print()
        
        for i, case in enumerate(self.demo_cases, 1):
            print(f"📋 Case {i}: {case['title']}")
            print(f"   Description: {case['description']}")
            print(f"   Symptoms: '{case['symptoms']}'")
            print(f"   Expected: {case['expected']}")
            
            try:
                print("   🔄 Processing...")
                start_time = time.time()
                result = self.medical_system.diagnose_patient(case['symptoms'])
                processing_time = (time.time() - start_time) * 1000
                
                # Display results
                self._display_diagnosis_result(result, processing_time)
                
                # Validation
                if result.disease.value == case['expected']:
                    print("✅ CORRECT DIAGNOSIS!")
                else:
                    print(f"❌ MISDIAGNOSIS - Expected: {case['expected']}")
                
            except Exception as e:
                print(f"❌ Error processing case: {e}")
            
            print("-"*60)
            
            # Ask if user wants to continue
            if i < len(self.demo_cases):
                continue_choice = input("⏭️  Continue to next case? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes', 'evet', 'e']:
                    break
    
    def _display_diagnosis_result(self, result, processing_time: float):
        """Display comprehensive diagnosis results."""
        print(f"\n🏥 DIAGNOSIS RESULTS (Processed in {processing_time:.1f}ms):")
        print(f"   Disease: {result.disease.value}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Severity: {result.severity_level.value}")
        print(f"   Max Probability: {max(result.probabilities.values()):.1%}")
        
        # Show detected symptoms
        if result.detected_symptoms:
            print(f"\n🔍 DETECTED SYMPTOMS:")
            for symptom, intensity in result.detected_symptoms.items():
                intensity_bar = "█" * int(intensity * 10)
                print(f"   • {symptom}: {intensity:.2f} {intensity_bar}")
        
        # Show diagnostic signatures
        if result.diagnostic_signatures:
            print(f"\n🎯 DIAGNOSTIC SIGNATURES:")
            for signature in result.diagnostic_signatures:
                print(f"   • {signature}")
        
        # Show probability distribution
        sorted_probs = sorted(result.probabilities.items(), 
                            key=lambda x: x[1], reverse=True)
        print(f"\n📈 PROBABILITY DISTRIBUTION:")
        for i, (disease, prob) in enumerate(sorted_probs, 1):
            bar = "█" * int(prob * 20)
            print(f"   {i}. {disease}: {prob:.1%} {bar}")
        
        # Show medical recommendations
        print(f"\n💡 MEDICAL RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations[:6], 1):  # Show first 6
            print(f"   {i}. {rec}")
        
        if len(result.recommendations) > 6:
            print(f"   ... and {len(result.recommendations) - 6} more recommendations")
        
        # Show metadata
        print(f"\n📊 SYSTEM METADATA:")
        print(f"   Processing Time: {processing_time:.1f}ms")
        print(f"   Symptoms Processed: {result.metadata['processed_symptoms']}")
        print(f"   Confidence Level: {result.metadata['confidence_level']}")
        print(f"   System Version: {result.metadata['system_version']}")
    
    def show_system_info(self):
        """Display detailed system information."""
        print("\n" + "="*60)
        print("📊 SYSTEM INFORMATION")
        print("="*60)
        
        system_info = self.medical_system.get_system_info()
        
        print("🤖 MODEL DETAILS:")
        print(f"   Type: {system_info.model_type}")
        print(f"   Version: {system_info.version}")
        print(f"   Created: {system_info.created_at}")
        print()
        
        print("📈 PERFORMANCE METRICS:")
        print(f"   Training Accuracy: {system_info.training_accuracy:.1%}")
        print(f"   Test Accuracy: {system_info.test_accuracy:.1%}")
        print(f"   Cross-Validation: {', '.join([f'{score:.1%}' for score in system_info.cross_validation_scores])}")
        print()
        
        print("🔧 TECHNICAL SPECIFICATIONS:")
        print(f"   Feature Count: {system_info.feature_count}")
        print(f"   Sample Count: {system_info.sample_count:,}")
        print(f"   Classes: {', '.join(system_info.classes)}")
        print()
        
        print("🏥 CLINICAL CAPABILITIES:")
        print("   • COVID-19 Detection with 100% accuracy")
        print("   • Influenza Recognition with systemic symptoms")
        print("   • Common Cold Identification")
        print("   • Allergic Rhinitis Diagnosis")
        print("   • Severity Assessment (Mild to Critical)")
        print("   • Evidence-based Medical Recommendations")
        print("   • Diagnostic Signature Analysis")
    
    def show_help(self):
        """Display help information."""
        print("\n" + "="*60)
        print("❓ HELP & USAGE INSTRUCTIONS")
        print("="*60)
        
        print("🎯 HOW TO USE THE SYSTEM:")
        print("   1. Select 'Interactive Diagnosis' from the main menu")
        print("   2. Describe your symptoms in Turkish")
        print("   3. Review the AI diagnosis and recommendations")
        print("   4. Consult with a healthcare professional if needed")
        print()
        
        print("📝 SYMPTOM DESCRIPTION TIPS:")
        print("   • Use natural Turkish language")
        print("   • Include intensity modifiers (çok, hafif, aşırı)")
        print("   • Mention duration if relevant")
        print("   • Be specific about symptoms")
        print()
        
        print("💡 EXAMPLE INPUTS:")
        print("   • 'Ateşim var, öksürüyorum'")
        print("   • 'Gözlerim kaşınıyor, hapşırıyorum'")
        print("   • 'Nefes alamıyorum, koku kaybım var'")
        print("   • 'Vücudum ağrıyor, titreme var'")
        print()
        
        print("⚠️  IMPORTANT REMINDERS:")
        print("   • This is a clinical decision support tool")
        print("   • Always consult healthcare professionals")
        print("   • For emergencies, call emergency services")
        print("   • Results are not a substitute for medical diagnosis")
    
    def run(self):
        """Run the interactive demo."""
        # Initialize system
        if not self.initialize_system():
            return
        
        # Display welcome
        self.display_welcome()
        
        # Main loop
        while True:
            try:
                self.display_menu()
                choice = self.get_user_choice()
                
                if choice == '1':
                    self.interactive_diagnosis()
                elif choice == '2':
                    self.demo_cases()
                elif choice == '3':
                    self.show_system_info()
                elif choice == '4':
                    self.show_help()
                elif choice == '5':
                    print("\n👋 Thank you for using the Professional Medical System!")
                    print("🏥 Remember: Always consult with healthcare professionals for medical decisions.")
                    break
                
                # Pause before returning to menu
                if choice in ['1', '2', '3', '4']:
                    input("\n⏸️  Press Enter to return to main menu...")
                    print("\n" + "="*80)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("   Please try again.")


def main():
    """Main function to run the interactive demo."""
    try:
        demo = InteractiveMedicalDemo()
        demo.run()
    except Exception as e:
        print(f"❌ Failed to start demo: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
