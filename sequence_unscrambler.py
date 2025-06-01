#!/usr/bin/env python3
"""
SEQUENCE UNSCRAMBLER
Systematic anagram analysis for extracted sequences
"""

from itertools import permutations
import re

class SequenceUnscrambler:
    def __init__(self):
        self.lowercase_seq = "aoutkecoymip"
        self.uppercase_seq = "LXGSMLNIXLFGDAXSH"
        
        # Common English words for pattern matching
        self.common_words = [
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put", "say", "she", "too", "use",
            "make", "take", "come", "game", "time", "work", "like", "back", "call", "just", "know", "over", "also", "after", "first", "well", "year", "where", "much", "good", "great", "right", "think", "little", "world", "school", "state", "family", "student", "group", "country", "problem", "hand", "part", "place", "case", "week", "company", "system", "program", "question", "government", "number", "night", "point", "home", "water", "room", "mother", "area", "money", "story", "fact", "month", "lot", "right", "study", "book", "eye", "job", "word", "business", "issue", "side", "kind", "head", "house", "service", "friend", "father", "power", "hour", "game", "line", "end", "member", "law", "car", "city", "community", "name", "president", "team", "minute", "idea", "kid", "body", "information", "back", "parent", "face", "others", "level", "office", "door", "health", "person", "art", "war", "history", "party", "result", "change", "morning", "reason", "research", "girl", "guy", "moment", "air", "teacher", "force", "education"
        ]
        
        # Gaming/tech related words
        self.gaming_words = [
            "game", "play", "player", "code", "key", "hack", "crack", "konami", "cheat", 
            "token", "coin", "crypto", "bitcoin", "ethereum", "wallet", "address",
            "quest", "puzzle", "mystery", "secret", "hidden", "clue", "riddle",
            "magic", "spell", "potion", "item", "loot", "treasure", "reward"
        ]
        
    def analyze_letter_frequency(self, sequence):
        """Analyze letter frequency in sequence"""
        freq = {}
        for char in sequence.lower():
            freq[char] = freq.get(char, 0) + 1
        return freq
    
    def find_contained_words(self, sequence, word_list):
        """Find words that can be formed from the sequence letters"""
        seq_letters = sequence.lower()
        seq_freq = self.analyze_letter_frequency(seq_letters)
        
        found_words = []
        
        for word in word_list:
            word_freq = self.analyze_letter_frequency(word)
            
            # Check if word can be formed from sequence
            can_form = True
            for letter, count in word_freq.items():
                if seq_freq.get(letter, 0) < count:
                    can_form = False
                    break
            
            if can_form and len(word) >= 3:  # Only words 3+ letters
                found_words.append(word)
        
        return sorted(found_words, key=len, reverse=True)
    
    def find_anagram_patterns(self, sequence):
        """Look for meaningful anagram patterns"""
        patterns = []
        
        # Check for common letter combinations
        common_combos = ['th', 'er', 'on', 'an', 're', 'he', 'in', 'ed', 'nd', 'ha', 'at', 'en', 'es', 'of', 'or', 'nt', 'ea', 'ti', 'to', 'it', 'st', 'io', 'le', 'is', 'ou', 'ar', 'as', 'de', 'rt', 've']
        
        seq_lower = sequence.lower()
        for combo in common_combos:
            if all(char in seq_lower for char in combo):
                patterns.append(f"Contains '{combo}'")
        
        # Check for doubled letters
        doubled = []
        for i in range(len(sequence) - 1):
            if sequence[i].lower() == sequence[i+1].lower():
                doubled.append(sequence[i].lower() + sequence[i+1].lower())
        
        if doubled:
            patterns.append(f"Doubled letters: {doubled}")
        
        return patterns
    
    def systematic_word_search(self, sequence):
        """Systematically search for word combinations"""
        print(f"\n🔍 ANALYZING: {sequence}")
        print("-" * 50)
        
        # Letter frequency
        freq = self.analyze_letter_frequency(sequence)
        print(f"📊 Letter frequency: {freq}")
        print(f"📏 Length: {len(sequence)} letters")
        
        # Find words in common dictionary
        common_found = self.find_contained_words(sequence, self.common_words)
        if common_found:
            print(f"🔤 Common words found: {common_found[:10]}")
        
        # Find gaming/tech words
        gaming_found = self.find_contained_words(sequence, self.gaming_words)
        if gaming_found:
            print(f"🎮 Gaming/tech words found: {gaming_found}")
        
        # Pattern analysis
        patterns = self.find_anagram_patterns(sequence)
        if patterns:
            print(f"📝 Patterns: {patterns}")
        
        return {
            'common_words': common_found,
            'gaming_words': gaming_found,
            'patterns': patterns,
            'frequency': freq
        }
    
    def try_specific_combinations(self, sequence):
        """Try specific meaningful combinations"""
        print(f"\n🎯 SPECIFIC COMBINATION ATTEMPTS for {sequence}")
        print("-" * 50)
        
        combinations = []
        
        if sequence.lower() == "aoutkecoymip":
            # Possible combinations for this sequence
            attempts = [
                "pocket aim you",
                "make you topic", 
                "poke ya to mic",
                "take my pouco",  # pouco = little (Portuguese)
                "make it you cop",
                "you take comp i",
                "compute ya koi",
                "copy make it ou",
                "ya mike to cup",
                "to make you pic"
            ]
            
            for attempt in attempts:
                # Check if letters match
                attempt_letters = ''.join(attempt.split()).lower()
                if sorted(attempt_letters) == sorted(sequence.lower()):
                    combinations.append(f"✅ MATCH: '{attempt}'")
                else:
                    combinations.append(f"❌ No match: '{attempt}'")
        
        elif sequence.upper() == "LXGSMLNIXLFGDAXSH":
            # Possible combinations for this sequence
            attempts = [
                "X FIND GLAXS MLH",  # pharmaceutical reference?
                "FLIX GRAND X SLM",  # streaming reference?
                "GLX FIND SMASH LX", 
                "SLIM GRAND FLX X",
                "FLASH GRID MX LN",
                "GNIX FLASH DLM GS"
            ]
            
            for attempt in attempts:
                attempt_letters = ''.join(attempt.split()).upper()
                if sorted(attempt_letters) == sorted(sequence.upper()):
                    combinations.append(f"✅ MATCH: '{attempt}'")
                else:
                    combinations.append(f"❌ No match: '{attempt}'")
        
        if combinations:
            for combo in combinations:
                print(f"   {combo}")
        else:
            print("   No specific combinations found")
    
    def deep_anagram_analysis(self):
        """Perform deep anagram analysis on both sequences"""
        print("🧩 COMPREHENSIVE ANAGRAM ANALYSIS")
        print("=" * 70)
        
        # Analyze lowercase sequence
        result1 = self.systematic_word_search(self.lowercase_seq)
        self.try_specific_combinations(self.lowercase_seq)
        
        # Analyze uppercase sequence  
        result2 = self.systematic_word_search(self.uppercase_seq)
        self.try_specific_combinations(self.uppercase_seq)
        
        # Cross-analysis
        print(f"\n🔄 CROSS-SEQUENCE ANALYSIS")
        print("-" * 50)
        
        # Check if sequences are related
        total_letters = len(self.lowercase_seq) + len(self.uppercase_seq)
        print(f"📊 Total letters: {total_letters}")
        print(f"📊 Lowercase: {len(self.lowercase_seq)} chars")
        print(f"📊 Uppercase: {len(self.uppercase_seq)} chars")
        
        # Check for shared patterns
        lower_letters = set(self.lowercase_seq.lower())
        upper_letters = set(self.uppercase_seq.lower())
        shared = lower_letters.intersection(upper_letters)
        
        if shared:
            print(f"🔗 Shared letters: {sorted(shared)}")
        
        # Final recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   • Try online anagram solvers for verification")
        print(f"   • Check against specialized dictionaries (crypto, gaming)")
        print(f"   • Consider abbreviations or acronyms")
        print(f"   • Test as encoded coordinates or IDs")

def main():
    unscrambler = SequenceUnscrambler()
    unscrambler.deep_anagram_analysis()

if __name__ == "__main__":
    main() 