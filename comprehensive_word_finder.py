#!/usr/bin/env python3
"""
COMPREHENSIVE WORD FINDER
Advanced anagram solver for both sequences with extensive dictionary
"""

from itertools import permutations, combinations
import re

class ComprehensiveWordFinder:
    def __init__(self):
        self.lowercase_seq = "aoutkecoymip"
        self.uppercase_seq = "LXGSMLNIXLFGDAXSH"
        
        # Expanded word lists
        self.crypto_words = [
            "key", "token", "coin", "wallet", "address", "hash", "block", "chain",
            "bitcoin", "ethereum", "crypto", "node", "mint", "stake", "pool",
            "defi", "nft", "dao", "dapp", "gas", "wei", "gwei", "satoshi"
        ]
        
        self.gaming_words = [
            "game", "play", "player", "quest", "item", "loot", "gold", "exp",
            "level", "boss", "raid", "guild", "clan", "pvp", "pve", "npc",
            "mod", "hack", "cheat", "code", "konami", "easter", "egg"
        ]
        
        self.common_3_letter = [
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
            "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
            "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy",
            "did", "its", "let", "put", "say", "she", "too", "use", "may", "try",
            "big", "end", "far", "few", "got", "own", "run", "set", "top", "yes",
            "yet", "ask", "bit", "box", "car", "cut", "eat", "eye", "fit", "fly",
            "gun", "hit", "job", "key", "lay", "lot", "map", "net", "oil", "pay",
            "red", "sea", "sit", "tax", "war", "win", "act", "add", "age", "air",
            "arm", "art", "bad", "bag", "bar", "bed", "bet", "bus", "buy", "cat"
        ]
        
        self.common_4_letter = [
            "that", "with", "have", "this", "will", "your", "from", "they", "know",
            "want", "been", "good", "much", "some", "time", "very", "when", "come",
            "here", "just", "like", "long", "make", "many", "over", "such", "take",
            "than", "them", "well", "were", "what", "year", "back", "call", "came",
            "each", "even", "find", "give", "hand", "high", "keep", "last", "left",
            "life", "live", "look", "made", "most", "move", "must", "name", "need",
            "next", "only", "open", "part", "play", "right", "said", "same", "seem",
            "show", "side", "tell", "turn", "used", "want", "ways", "week", "went",
            "work", "area", "book", "case", "done", "down", "each", "fact", "feel",
            "game", "give", "help", "home", "idea", "into", "kind", "land", "line",
            "list", "mind", "note", "page", "plan", "real", "room", "self", "sort",
            "talk", "team", "true", "type", "used", "wall", "word", "army", "face",
            "fire", "form", "head", "hear", "hope", "hour", "keep", "king", "late",
            "live", "love", "mean", "meet", "miss", "move", "once", "pass", "past",
            "pick", "come", "copy", "cost", "dark", "deal", "door", "drop", "easy",
            "fall", "fast", "fear", "file", "fill", "fine", "food", "free", "full",
            "goal", "gold", "grow", "hair", "half", "hang", "hard", "heat", "held",
            "item", "join", "jump", "kept", "kill", "kind", "knew", "lack", "lady",
            "lead", "lean", "left", "less", "loss", "loud", "main", "male", "mark",
            "math", "meat", "mile", "milk", "mind", "mine", "moon", "near", "nice",
            "paid", "park", "path", "pick", "plan", "poor", "push", "race", "rain",
            "read", "rest", "rich", "rock", "role", "rule", "safe", "said", "save",
            "seat", "sell", "send", "ship", "shop", "shot", "sick", "sign", "sing",
            "site", "size", "skin", "soft", "sold", "song", "soon", "sort", "star",
            "stay", "step", "stop", "sure", "talk", "tape", "task", "team", "tend",
            "term", "test", "text", "thin", "tool", "town", "tree", "trip", "walk",
            "warm", "wave", "wear", "week", "wide", "wild", "wind", "wine", "wire",
            "wise", "wood", "word", "wore", "yard", "yeah", "zero", "zone"
        ]
        
        # Tech abbreviations and acronyms
        self.tech_abbrev = [
            "API", "GPU", "CPU", "RAM", "ROM", "USB", "URL", "HTTP", "HTML", "CSS",
            "SQL", "XML", "JSON", "AJAX", "REST", "SDK", "IDE", "GUI", "CLI", "OS",
            "VM", "VPN", "DNS", "IP", "TCP", "UDP", "FTP", "SSH", "SSL", "TLS"
        ]
        
    def find_all_words_in_sequence(self, sequence, min_length=3):
        """Find all possible words that can be formed from sequence letters"""
        sequence = sequence.lower()
        all_words = self.common_3_letter + self.common_4_letter + self.crypto_words + self.gaming_words
        
        found_words = []
        seq_letters = list(sequence)
        
        for word in all_words:
            if len(word) >= min_length:
                word_letters = list(word.lower())
                temp_seq = seq_letters.copy()
                
                can_form = True
                for letter in word_letters:
                    if letter in temp_seq:
                        temp_seq.remove(letter)
                    else:
                        can_form = False
                        break
                
                if can_form:
                    found_words.append(word)
        
        return sorted(found_words, key=len, reverse=True)
    
    def find_word_combinations(self, sequence, target_words=None):
        """Find combinations of words that use all letters"""
        if target_words is None:
            target_words = self.find_all_words_in_sequence(sequence)
        
        combinations = []
        sequence_letters = list(sequence.lower())
        
        # Try pairs of words
        for i, word1 in enumerate(target_words):
            for j, word2 in enumerate(target_words[i:], i):
                combined_letters = list(word1.lower()) + list(word2.lower())
                if sorted(combined_letters) == sorted(sequence_letters):
                    combinations.append(f"{word1} {word2}")
        
        # Try triplets of words
        for i, word1 in enumerate(target_words):
            for j, word2 in enumerate(target_words):
                for k, word3 in enumerate(target_words):
                    if i != j and j != k and i != k:
                        combined_letters = list(word1.lower()) + list(word2.lower()) + list(word3.lower())
                        if sorted(combined_letters) == sorted(sequence_letters):
                            combinations.append(f"{word1} {word2} {word3}")
        
        return list(set(combinations))
    
    def generate_meaningful_phrases(self, sequence):
        """Generate meaningful phrases from the sequence"""
        phrases = []
        
        if sequence.lower() == "aoutkecoymip":
            # More creative attempts for lowercase
            creative_attempts = [
                "cup time okay",
                "pick meayout", 
                "tokyo aceump",
                "mice pot yakuo",
                "yap kite coumo",
                "poke city maou",
                "tame you picko",
                "make pity coou",
                "pace my tokiu",
                "mouic pay keto",
                "tokyo map cuie",
                "cute pom yaiko",
                "topic yake mou",
                "you take micro",
                "make topic you",
                "puck time yoao",
                "tame epic you"
            ]
            
            for attempt in creative_attempts:
                attempt_clean = ''.join(attempt.split()).lower()
                if sorted(attempt_clean) == sorted(sequence.lower()):
                    phrases.append(f"✅ '{attempt}'")
                else:
                    phrases.append(f"❌ '{attempt}'")
        
        elif sequence.upper() == "LXGSMLNIXLFGDAXSH":
            # More attempts for uppercase
            creative_attempts = [
                "SIXFOLD GLAM HXN",
                "FLUX GLAM HXN SID", 
                "NIGHT FLUX MXL ADS",
                "FLASH MIND GLX GX",
                "SLIM GLAD FXN HXG",
                "FIND GLAS HXM LXG",
                "GLAD SPHINX FLM XG",
                "MILD FLASH GXN XG",
                "FLASH MIND XLG XG",
                "GLAM FIND SXL HXG"
            ]
            
            for attempt in creative_attempts:
                attempt_clean = ''.join(attempt.split()).upper()
                if sorted(attempt_clean) == sorted(sequence.upper()):
                    phrases.append(f"✅ '{attempt}'")
                else:
                    phrases.append(f"❌ '{attempt}'")
        
        return phrases
    
    def analyze_both_sequences(self):
        """Comprehensive analysis of both sequences"""
        print("🔍 COMPREHENSIVE WORD ANALYSIS")
        print("=" * 80)
        
        for seq_name, sequence in [("LOWERCASE", self.lowercase_seq), ("UPPERCASE", self.uppercase_seq)]:
            print(f"\n📝 ANALYZING {seq_name} SEQUENCE: '{sequence}'")
            print("-" * 60)
            
            # Find all possible words
            words = self.find_all_words_in_sequence(sequence)
            print(f"🔤 All possible words ({len(words)}): {words[:20]}")
            if len(words) > 20:
                print(f"    ... and {len(words)-20} more")
            
            # Find word combinations
            combinations = self.find_word_combinations(sequence, words[:15])  # Use top 15 words
            if combinations:
                print(f"🎯 Word combinations found: {combinations[:10]}")
                if len(combinations) > 10:
                    print(f"    ... and {len(combinations)-10} more")
            
            # Generate meaningful phrases
            phrases = self.generate_meaningful_phrases(sequence)
            if phrases:
                print(f"💭 Creative phrase attempts:")
                for phrase in phrases[:10]:
                    print(f"    {phrase}")
            
            print()

def main():
    finder = ComprehensiveWordFinder()
    finder.analyze_both_sequences()

if __name__ == "__main__":
    main() 