import re
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")

# Arabic Unicode Constants
FATHA = '\u064E'
DAMMA = '\u064F'
KASRA = '\u0650'
FATHATAN = '\u064B'
DAMMATAN = '\u064C'
KASRATAN = '\u064D'
SUKUN = '\u0652'
SHADDA = '\u0651'
DAGGER_ALIF = '\u0670'
ALIF = '\u0627'
ALIF_WASLA = '\u0671'
ALIF_HAMZA_ABOVE = '\u0623'
ALIF_HAMZA_BELOW = '\u0625'
WAW = '\u0648'
YA = '\u064A'
ALIF_MAQSURA = '\u0649'
NOON = '\u0646'
MEEM = '\u0645'
BAA = '\u0628'

QALQALAH_LETTERS = set(['\u0642', '\u0637', '\u0628', '\u062c', '\u062f']) # ق, ط, ب, ج, د
IKHFA_LETTERS = set(['\u062a', '\u062b', '\u062c', '\u062f', '\u0630', '\u0632', '\u0633', '\u0634', '\u0635', '\u0636', '\u0637', '\u0638', '\u0641', '\u0642', '\u0643']) # 15 letters
IDGHAM_GHUNNAH_LETTERS = set(['\u064a', '\u0646', '\u0645', '\u0648']) # ي, ن, م, و
IDGHAM_BILA_GHUNNAH_LETTERS = set(['\u0644', '\u0631']) # ل, ر
HARAKAT_SET = set([FATHA, DAMMA, KASRA, FATHATAN, DAMMATAN, KASRATAN, SUKUN, SHADDA, DAGGER_ALIF])

class KarianaTajweedRuleEngine:
    def __init__(self):
        pass

    def analyze_word(self, word, next_word=None):
        """
        Analyzes a single Arabic word in context and returns tokens annotated with Tajweed marks.
        Annotations include:
          - 'MADD_1': 1-Alif Madd -> S1:Igrave
          - 'MADD_4': 4-Alif Madd -> S2:Oacute
          - 'GHUNNAH': Wajib Ghunnah / Idgham -> S2:Ocircumflex
          - 'IKHFA': Ikhfa -> S1:Ograve
          - 'QALQALAH': Qalqalah -> Sukun ^
        """
        annotated = []
        n = len(word)
        i = 0
        
        while i < n:
            char = word[i]
            # collect letter and its diacritics
            diacritics = []
            j = i + 1
            while j < n and word[j] in HARAKAT_SET:
                diacritics.append(word[j])
                j += 1
            
            unit = {
                "letter": char,
                "diacritics": diacritics,
                "marks": [],
                "raw": word[i:j]
            }
            
            # 1. QALQALAH check
            if char in QALQALAH_LETTERS and SUKUN in diacritics:
                unit["marks"].append("QALQALAH") # Special Sukun ^
            
            # 2. WAJIB GHUNNAH (Noon or Meem with Shadda)
            if char in (NOON, MEEM) and SHADDA in diacritics:
                unit["marks"].append("GHUNNAH") # S2:Ocircumflex
            
            # 3. 1-ALIF MADD (Madd Asli / Tabee)
            # Dagger Alif (Khara Zabar)
            if DAGGER_ALIF in diacritics:
                unit["marks"].append("MADD_1") # S1:Igrave
            
            # Fatha followed by Alif / Alif Maqsura
            elif FATHA in diacritics:
                if j < n and word[j] in (ALIF, ALIF_MAQSURA):
                    # Check if next has Hamzah (Madd Muttasil -> 4 Alif)
                    k = j + 1
                    if k < n and word[k] in ('\u0621', ALIF_HAMZA_ABOVE):
                        unit["marks"].append("MADD_4")
                    else:
                        unit["marks"].append("MADD_1")
            
            # Damma followed by Waw
            elif DAMMA in diacritics:
                if j < n and word[j] == WAW:
                    # check if Waw has no harakat or sukun
                    unit["marks"].append("MADD_1")
                    
            # Kasra followed by Ya
            elif KASRA in diacritics:
                if j < n and word[j] in (YA, '\u0649'):
                    unit["marks"].append("MADD_1")
            
            # 4. 4-ALIF MADD (General Madd sign ~ above letter)
            if '\u0653' in diacritics: # Maddah above
                unit["marks"].append("MADD_4")
                
            annotated.append(unit)
            i = j
            
        # Contextual check between current word and next_word
        if annotated and next_word:
            last_unit = annotated[-1]
            last_diacritics = last_unit["diacritics"]
            has_tanween = any(d in (FATHATAN, DAMMATAN, KASRATAN) for d in last_diacritics)
            is_noon_sakin = (last_unit["letter"] == NOON and (SUKUN in last_diacritics or not last_diacritics))
            
            # First letter of next word
            next_first = next_word[0] if next_word else None
            if has_tanween or is_noon_sakin:
                if next_first in IDGHAM_GHUNNAH_LETTERS:
                    last_unit["marks"].append("GHUNNAH") # S2:Ocircumflex
                elif next_first in IKHFA_LETTERS:
                    last_unit["marks"].append("IKHFA") # S1:Ograve
                elif next_first == BAA:
                    last_unit["marks"].append("IQLAB") # small meem
                    
        return annotated

if __name__ == "__main__":
    engine = KarianaTajweedRuleEngine()
    
    # Test on Line 1 of Page 21 (Baqarah Ayah 85 end):
    # عَلَيْهِمْ بِالْإِثْمِ وَالْعُدْوَانِ وَإِنْ يَأْتُوكُمْ أُسَارَىٰ تُفَادُوهُمْ
    sample_text = "عَلَيْهِمْ بِالْإِثْمِ وَالْعُدْوَانِ وَإِنْ يَأْتُوكُمْ أُسَارَىٰ تُفَادُوهُمْ"
    words = sample_text.split()
    
    print(f"টেস্টিং টেক্সট: {sample_text}\n")
    for idx, w in enumerate(words):
        next_w = words[idx+1] if idx + 1 < len(words) else None
        res = engine.analyze_word(w, next_w)
        marks_found = [(u["letter"], u["marks"]) for u in res if u["marks"]]
        print(f"শব্দ [{w:15s}]:")
        for u in res:
            if u["marks"]:
                print(f"  হরফ: '{u['letter']}' -> তাজবীদ মার্কস: {u['marks']}")
