import os
import sys
import json
import re

sys.stdout.reconfigure(encoding="utf-8")

from kariana_rules_engine import KarianaTajweedRuleEngine

class KarianaQuranConverter:
    def __init__(self, font_cmap_path=None):
        self.rule_engine = KarianaTajweedRuleEngine()
        
        # PUA mapping for Tajweed symbols
        # From our smart font build:
        self.tajweed_pua = {
            "MADD_1": "\uE26E",     # taj_s1_Igrave (1-Alif Madd)
            "MADD_4": "\uE281",     # taj_s2_Oacute (4-Alif Madd)
            "GHUNNAH": "\uE282",    # taj_s2_Ocircumflex (Ghunnah)
            "IKHFA": "\uE26F",      # taj_s1_Ograve (Ikhfa delta)
            "QALQALAH": "\uE0C7",   # ar_ex_asciicircum (Qalqalah ^)
            "IQLAB": "\uE270"       # taj_s1_apple (Small Meem)
        }

    def convert_text(self, text):
        """
        Converts standard Unicode Quran text into Kariana styled stream.
        """
        words = text.split()
        converted_words = []
        
        for idx, w in enumerate(words):
            next_w = words[idx + 1] if idx + 1 < len(words) else None
            units = self.rule_engine.analyze_word(w, next_w)
            
            word_str = ""
            for u in units:
                letter = u["letter"]
                diacritics = "".join(u["diacritics"])
                marks = u["marks"]
                
                # Append base letter and diacritics
                word_str += letter + diacritics
                
                # Append tajweed symbol PUA if triggered
                for m in marks:
                    if m in self.tajweed_pua:
                        word_str += self.tajweed_pua[m]
                        
            converted_words.append(word_str)
            
        return " ".join(converted_words)

if __name__ == "__main__":
    converter = KarianaQuranConverter()
    
    # Test on Ayahs 85, 86, 87 of Surah Baqarah
    sample_text = "عَلَيْهِمْ بِالْإِثْمِ وَالْعُدْوَانِ وَإِنْ يَأْتُوكُمْ أُسَارَىٰ تُفَادُوهُمْ"
    converted = converter.convert_text(sample_text)
    
    print("=== ক্বারীয়ানা কুরআন ইউনিভার্সাল কনভার্টার টেস্ট ===")
    print(f"মূল ইউনিকোড ইনপুট:\n  {sample_text}\n")
    print(f"ক্বারীয়ানা স্মার্ট আউটপুট:\n  {converted}\n")
    print(f"আউটপুট হেক্স কোড পয়েন্টসমূহ:\n  {[hex(ord(c)) for c in converted]}")
