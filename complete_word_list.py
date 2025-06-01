#!/usr/bin/env python3
"""
COMPLETE WORD LIST GENERATOR
Exhaustive word finding for both sequences
"""

class CompleteWordList:
    def __init__(self):
        self.lowercase_seq = "aoutkecoymip"
        self.uppercase_seq = "LXGSMLNIXLFGDAXSH"
        
        # Comprehensive word dictionary
        self.all_words = [
            # 3-letter words
            "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
            "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
            "how", "man", "new", "now", "old", "see", "two", "way", "who", "boy",
            "did", "its", "let", "put", "say", "she", "too", "use", "may", "try",
            "big", "end", "far", "few", "got", "own", "run", "set", "top", "yes",
            "yet", "ask", "bit", "box", "car", "cut", "eat", "eye", "fit", "fly",
            "gun", "hit", "job", "key", "lay", "lot", "map", "net", "oil", "pay",
            "red", "sea", "sit", "tax", "war", "win", "act", "add", "age", "air",
            "arm", "art", "bad", "bag", "bar", "bed", "bet", "bus", "buy", "cat",
            "cup", "die", "dog", "due", "era", "fun", "gas", "god", "ice", "kid",
            "leg", "lie", "log", "mad", "men", "mix", "mud", "per", "pie", "pop",
            "raw", "sad", "sky", "sun", "tea", "tie", "tip", "top", "toy", "try",
            "van", "web", "win", "zip", "ace", "amp", "any", "app", "arc", "ash",
            "ban", "bat", "bay", "bee", "bid", "bin", "bow", "bug", "cab", "cam",
            "cap", "cod", "cow", "cry", "dam", "den", "dew", "dim", "dot", "dry",
            "ear", "eel", "egg", "elf", "elk", "elm", "eve", "fan", "fat", "fig",
            "fin", "fix", "fog", "fox", "gap", "gel", "gem", "gym", "ham", "hat",
            "hen", "hex", "hip", "hop", "hot", "hub", "hug", "hut", "ink", "inn",
            "ion", "jar", "jaw", "jet", "jog", "joy", "lab", "lap", "law", "lid",
            "lip", "mat", "max", "mob", "mom", "mop", "nap", "nod", "nun", "nut",
            "oak", "odd", "orb", "ore", "owl", "pad", "pan", "pat", "paw", "pen",
            "pet", "pin", "pit", "pod", "pot", "pub", "pup", "rag", "ram", "ran",
            "rap", "rat", "ray", "rib", "rid", "rim", "rip", "rob", "rod", "row",
            "rub", "rug", "rum", "sag", "saw", "sex", "shy", "sin", "sip", "six",
            "ski", "sly", "sob", "sod", "son", "soy", "spa", "spy", "tab", "tag",
            "tan", "tap", "tar", "toe", "ton", "tot", "tub", "tug", "two", "vet",
            "wad", "war", "way", "wet", "wig", "wit", "wow", "yak", "yam", "yen",
            "zap", "zen", "zoo",
            
            # 4-letter words
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
            "wise", "wood", "word", "wore", "yard", "yeah", "zero", "zone", "able",
            "acid", "aged", "also", "area", "army", "away", "baby", "ball", "band",
            "bank", "base", "beat", "been", "bell", "best", "bike", "bill", "bird",
            "blow", "blue", "boat", "body", "bone", "book", "boom", "born", "both",
            "bowl", "bulk", "burn", "bush", "busy", "calm", "camp", "card", "care",
            "cash", "cast", "cave", "cell", "chat", "chip", "city", "clay", "clean",
            "clip", "club", "coal", "coat", "code", "coin", "cold", "cool", "cord",
            "corn", "crew", "crop", "crow", "cure", "cute", "dame", "data", "date",
            "dawn", "dead", "deal", "dear", "debt", "deck", "deep", "desk", "dial",
            "dice", "diet", "dirt", "dish", "dock", "dose", "duck", "dump", "dust",
            "duty", "each", "earl", "earn", "east", "edge", "else", "epic", "even",
            "evil", "exit", "face", "fact", "fail", "fair", "fall", "fame", "farm",
            "fast", "fate", "fear", "feed", "feel", "feet", "fell", "felt", "file",
            "film", "find", "fine", "fire", "firm", "fish", "fist", "five", "flag",
            "flat", "flew", "flip", "flow", "folk", "food", "foot", "ford", "fork",
            "fort", "four", "free", "fuel", "full", "fund", "gain", "game", "gate",
            "gear", "gift", "girl", "give", "glad", "goal", "goat", "gods", "goes",
            "gold", "golf", "gone", "good", "grab", "gray", "grew", "grid", "grip",
            "grow", "gulf", "hall", "hand", "hang", "hard", "harm", "hate", "have",
            "head", "heal", "hear", "heat", "held", "hell", "help", "herb", "hide",
            "high", "hill", "hint", "hire", "hold", "hole", "holy", "home", "hood",
            "hook", "hope", "horn", "host", "hour", "huge", "hung", "hunt", "hurt",
            "icon", "idea", "inch", "iron", "item", "jack", "jail", "jane", "jazz",
            "join", "joke", "jump", "june", "jury", "just", "keen", "keep", "kept",
            "keys", "kick", "kill", "kind", "king", "kiss", "knee", "knew", "know",
            "lack", "lady", "laid", "lake", "lamp", "land", "lane", "last", "late",
            "lead", "leaf", "lean", "left", "legs", "lens", "less", "levy", "lies",
            "life", "lift", "like", "lime", "line", "link", "lion", "lips", "list",
            "live", "load", "loan", "lock", "long", "look", "loop", "lord", "lose",
            "loss", "lost", "lots", "loud", "love", "luck", "lung", "made", "mail",
            "main", "make", "male", "mall", "many", "mark", "mars", "mass", "mate",
            "math", "mayo", "meal", "mean", "meat", "meet", "melt", "memo", "mice",
            "mile", "milk", "mind", "mine", "mint", "miss", "mist", "mode", "mood",
            "moon", "more", "most", "move", "much", "must", "name", "navy", "near",
            "neck", "need", "news", "next", "nice", "nine", "node", "none", "noon",
            "norm", "nose", "note", "nova", "oath", "odds", "once", "only", "open",
            "oral", "over", "pace", "pack", "page", "paid", "pain", "pair", "palm",
            "park", "part", "pass", "past", "path", "peak", "pick", "pile", "pill",
            "pink", "pipe", "plan", "play", "plot", "plus", "poem", "poet", "pole",
            "poll", "pool", "poor", "port", "post", "pour", "pray", "pull", "pump",
            "pure", "push", "quad", "quit", "race", "rain", "rank", "rare", "rate",
            "read", "real", "rear", "rely", "rent", "rest", "rich", "ride", "ring",
            "rise", "risk", "road", "rock", "role", "roll", "room", "root", "rope",
            "rose", "rule", "runs", "rush", "safe", "said", "sail", "sake", "sale",
            "salt", "same", "sand", "save", "seal", "seat", "seed", "seek", "seem",
            "seen", "self", "sell", "send", "sent", "ship", "shop", "shot", "show",
            "shut", "sick", "side", "sign", "silk", "sing", "sink", "site", "size",
            "skin", "skip", "slip", "slow", "snap", "snow", "soap", "sock", "soft",
            "soil", "sold", "sole", "some", "song", "soon", "sort", "soul", "soup",
            "spin", "spot", "star", "stay", "step", "stop", "such", "suit", "sure",
            "swim", "take", "tale", "talk", "tall", "tank", "tape", "task", "team",
            "tear", "tell", "tend", "tent", "term", "test", "text", "than", "that",
            "them", "then", "they", "thin", "this", "thus", "tide", "tied", "ties",
            "time", "tiny", "tips", "tire", "told", "tone", "took", "tool", "torn",
            "tour", "town", "toys", "tree", "trim", "trip", "true", "tube", "tune",
            "turn", "twin", "type", "unit", "upon", "used", "user", "uses", "vast",
            "very", "view", "void", "vote", "wage", "wait", "wake", "walk", "wall",
            "want", "ward", "warm", "warn", "wash", "wave", "ways", "weak", "wear",
            "week", "well", "went", "were", "west", "what", "when", "wide", "wife",
            "wild", "will", "wind", "wine", "wing", "wire", "wise", "wish", "with",
            "wood", "wool", "word", "wore", "work", "worn", "wrap", "yard", "year",
            "yoga", "york", "your", "zero", "zone",
            
            # 5+ letter words
            "about", "above", "abuse", "actor", "acute", "admit", "adopt", "adult", "after", "again",
            "agent", "agree", "ahead", "alarm", "album", "alert", "alien", "align", "alike", "alive",
            "allow", "alone", "along", "alter", "amid", "among", "anger", "angle", "angry", "apart",
            "apple", "apply", "arena", "argue", "arise", "array", "arrow", "aside", "asset", "avoid",
            "awake", "award", "aware", "badly", "baker", "bases", "basic", "beach", "began", "begin",
            "being", "below", "bench", "billy", "birth", "black", "blame", "blank", "blind", "block",
            "blood", "board", "boost", "booth", "bound", "brain", "brand", "bread", "break", "breed",
            "brick", "brief", "bring", "broad", "broke", "brown", "build", "built", "buyer", "cable",
            "calif", "carry", "catch", "cause", "chain", "chair", "chaos", "charm", "chart", "chase",
            "cheap", "check", "chest", "chief", "child", "china", "chose", "civil", "claim", "class",
            "clean", "clear", "click", "climb", "clock", "close", "cloud", "coach", "coast", "could",
            "count", "court", "cover", "craft", "crash", "crazy", "cream", "crime", "cross", "crowd",
            "crown", "crude", "curve", "cycle", "daily", "dance", "dated", "dealt", "death", "debut",
            "delay", "depth", "doing", "doubt", "dozen", "draft", "drama", "drank", "dream", "dress",
            "drill", "drink", "drive", "drove", "dying", "eager", "early", "earth", "eight", "elite",
            "empty", "enemy", "enjoy", "enter", "entry", "equal", "error", "event", "every", "exact",
            "exist", "extra", "faith", "false", "fault", "fiber", "field", "fifth", "fifty", "fight",
            "final", "first", "fixed", "flash", "fleet", "floor", "fluid", "focus", "force", "forth",
            "forty", "forum", "found", "frame", "frank", "fraud", "fresh", "front", "fruit", "fully",
            "funny", "giant", "given", "glass", "globe", "going", "grace", "grade", "grand", "grant",
            "grass", "grave", "great", "green", "gross", "group", "grown", "guard", "guess", "guest",
            "guide", "happy", "harry", "heart", "heavy", "hence", "henry", "horse", "hotel", "house",
            "human", "ideal", "image", "index", "inner", "input", "issue", "japan", "jimmy", "joint",
            "jones", "judge", "known", "label", "large", "laser", "later", "laugh", "layer", "learn",
            "lease", "least", "leave", "legal", "level", "lewis", "light", "limit", "links", "lives",
            "local", "loose", "lower", "lucky", "lunch", "lying", "magic", "major", "maker", "march",
            "maria", "match", "maybe", "mayor", "meant", "media", "metal", "might", "minor", "minus",
            "mixed", "model", "money", "month", "moral", "motor", "mount", "mouse", "mouth", "moved",
            "movie", "music", "needs", "never", "newly", "night", "noise", "north", "noted", "novel",
            "nurse", "occur", "ocean", "offer", "often", "order", "other", "ought", "paint", "panel",
            "paper", "party", "peace", "peter", "phase", "phone", "photo", "piano", "picked", "piece",
            "pilot", "pitch", "place", "plain", "plane", "plant", "plate", "point", "pound", "power",
            "press", "price", "pride", "prime", "print", "prior", "prize", "proof", "proud", "prove",
            "queen", "quick", "quiet", "quite", "radio", "raise", "range", "rapid", "ratio", "reach",
            "ready", "realm", "rebel", "refer", "relax", "repay", "reply", "right", "rigid", "rival",
            "river", "robin", "roger", "roman", "rough", "round", "route", "royal", "rural", "scale",
            "scene", "scope", "score", "sense", "serve", "seven", "shall", "shape", "share", "sharp",
            "sheet", "shelf", "shell", "shift", "shine", "shirt", "shock", "shoot", "short", "shown",
            "sides", "sight", "silly", "since", "sixth", "sixty", "sized", "skill", "sleep", "slide",
            "small", "smart", "smile", "smith", "smoke", "snake", "snow", "solid", "solve", "sorry",
            "sound", "south", "space", "spare", "speak", "speed", "spend", "spent", "split", "spoke",
            "sport", "staff", "stage", "stake", "stand", "start", "state", "steam", "steel", "steep",
            "steer", "steve", "stick", "still", "stock", "stone", "stood", "store", "storm", "story",
            "strip", "stuck", "study", "stuff", "style", "sugar", "suite", "super", "sweet", "swift",
            "swing", "swiss", "table", "taken", "taste", "taxes", "teach", "teeth", "terry", "texas",
            "thank", "theft", "their", "theme", "there", "these", "thick", "thing", "think", "third",
            "those", "three", "threw", "throw", "thumb", "tiger", "tight", "timer", "tired", "title",
            "today", "token", "topic", "total", "touch", "tough", "tower", "track", "trade", "train",
            "treat", "trend", "trial", "tribe", "trick", "tried", "tries", "truck", "truly", "trunk",
            "trust", "truth", "twice", "twist", "tyler", "ultra", "uncle", "under", "undue", "union",
            "unity", "until", "upper", "upset", "urban", "usage", "usual", "valid", "value", "video",
            "virus", "visit", "vital", "vocal", "voice", "waste", "watch", "water", "wheel", "where",
            "which", "while", "white", "whole", "whose", "woman", "women", "world", "worry", "worse",
            "worst", "worth", "would", "write", "wrong", "wrote", "young", "youth",
            
            # Gaming/Tech words
            "game", "play", "player", "quest", "item", "loot", "gold", "exp", "level", "boss", "raid",
            "guild", "clan", "pvp", "pve", "npc", "mod", "hack", "cheat", "code", "konami", "easter",
            "egg", "pixel", "sprite", "avatar", "combo", "skill", "magic", "spell", "potion", "armor",
            "weapon", "shield", "health", "mana", "energy", "score", "points", "lives", "coins", "gems",
            "power", "upgrade", "unlock", "achieve", "victory", "defeat", "battle", "fight", "attack",
            "defend", "move", "action", "turn", "round", "stage", "world", "zone", "area", "map",
            "location", "checkpoint", "save", "load", "pause", "menu", "option", "setting", "config",
            "profile", "account", "login", "logout", "register", "download", "install", "update",
            "patch", "version", "release", "beta", "alpha", "demo", "trial", "full", "premium", "dlc",
            "expansion", "content", "feature", "bug", "glitch", "lag", "ping", "server", "client",
            "network", "online", "offline", "multiplayer", "singleplayer", "coop", "versus", "match",
            "lobby", "room", "host", "join", "invite", "friend", "team", "party", "group", "squad",
            
            # Crypto/Blockchain words
            "key", "token", "coin", "wallet", "address", "hash", "block", "chain", "bitcoin", "ethereum",
            "crypto", "node", "mint", "stake", "pool", "defi", "nft", "dao", "dapp", "gas", "wei",
            "gwei", "satoshi", "mining", "proof", "consensus", "ledger", "transaction", "smart",
            "contract", "fork", "merge", "burn", "yield", "farming", "liquidity", "exchange", "trade",
            "buy", "sell", "hodl", "bull", "bear", "market", "price", "value", "volume", "supply",
            "demand", "inflation", "deflation", "volatility", "pump", "dump", "moon", "lambo", "rekt",
            "fomo", "fud", "shill", "whale", "bag", "diamond", "hands", "paper", "rocket", "moon",
            "mars", "pluto", "alpha", "beta", "gamma", "delta", "theta", "sigma", "protocol", "layer",
            "bridge", "wrapped", "synthetic", "oracle", "governance", "voting", "proposal", "treasury",
            "community", "ecosystem", "degen", "ape", "wagmi", "gm", "ngmi", "iykyk", "letsgo"
        ]
        
        # Tech abbreviations and acronyms
        self.tech_words = [
            "api", "app", "cpu", "gpu", "ram", "rom", "usb", "url", "http", "html", "css", "sql",
            "xml", "json", "ajax", "rest", "sdk", "ide", "gui", "cli", "os", "vm", "vpn", "dns",
            "ip", "tcp", "udp", "ftp", "ssh", "ssl", "tls", "aws", "gcp", "ai", "ml", "iot", "ar",
            "vr", "ui", "ux", "db", "cms", "crm", "erp", "seo", "ppc", "roi", "kpi", "b2b", "b2c",
            "saas", "paas", "iaas", "cicd", "devops", "agile", "scrum", "lean", "mvp", "poc", "qa",
            "uat", "prod", "dev", "test", "staging", "docker", "k8s", "nginx", "apache", "mysql",
            "postgres", "mongodb", "redis", "kafka", "spark", "hadoop", "elasticsearch", "kibana",
            "grafana", "prometheus", "jenkins", "gitlab", "github", "bitbucket", "jira", "slack",
            "teams", "zoom", "meet", "webex", "skype", "discord", "telegram", "whatsapp", "signal"
        ]
    
    def can_form_word(self, word, sequence):
        """Check if a word can be formed from sequence letters"""
        word = word.lower()
        sequence = sequence.lower()
        
        # Count letters in sequence
        seq_count = {}
        for char in sequence:
            seq_count[char] = seq_count.get(char, 0) + 1
        
        # Count letters needed for word
        word_count = {}
        for char in word:
            word_count[char] = word_count.get(char, 0) + 1
        
        # Check if we have enough letters
        for char, needed in word_count.items():
            if seq_count.get(char, 0) < needed:
                return False
        
        return True
    
    def find_all_possible_words(self, sequence, min_length=2):
        """Find all words that can be formed from the sequence"""
        all_dictionaries = self.all_words + self.tech_words
        possible_words = []
        
        for word in all_dictionaries:
            if len(word) >= min_length and self.can_form_word(word, sequence):
                possible_words.append(word)
        
        # Remove duplicates and sort by length
        possible_words = list(set(possible_words))
        return sorted(possible_words, key=lambda x: (-len(x), x))
    
    def generate_complete_word_lists(self):
        """Generate complete word lists for both sequences"""
        print("🔍 COMPLETE WORD LISTS FOR BOTH SEQUENCES")
        print("=" * 80)
        
        # Analyze lowercase sequence
        print(f"\n📝 LOWERCASE SEQUENCE: '{self.lowercase_seq}'")
        print("-" * 60)
        
        lowercase_words = self.find_all_possible_words(self.lowercase_seq, min_length=2)
        
        print(f"📊 Total words found: {len(lowercase_words)}")
        print(f"🔤 2-letter words: {[w for w in lowercase_words if len(w) == 2]}")
        print(f"🔤 3-letter words: {[w for w in lowercase_words if len(w) == 3]}")
        print(f"🔤 4-letter words: {[w for w in lowercase_words if len(w) == 4]}")
        print(f"🔤 5-letter words: {[w for w in lowercase_words if len(w) == 5]}")
        print(f"🔤 6+ letter words: {[w for w in lowercase_words if len(w) >= 6]}")
        
        print(f"\n📋 ALL WORDS (by length):")
        current_length = 0
        for word in lowercase_words:
            if len(word) != current_length:
                current_length = len(word)
                print(f"\n{current_length}-letter words:")
            print(f"  {word}")
        
        # Analyze uppercase sequence
        print(f"\n\n📝 UPPERCASE SEQUENCE: '{self.uppercase_seq}'")
        print("-" * 60)
        
        uppercase_words = self.find_all_possible_words(self.uppercase_seq, min_length=2)
        
        print(f"📊 Total words found: {len(uppercase_words)}")
        print(f"🔤 2-letter words: {[w for w in uppercase_words if len(w) == 2]}")
        print(f"🔤 3-letter words: {[w for w in uppercase_words if len(w) == 3]}")
        print(f"🔤 4-letter words: {[w for w in uppercase_words if len(w) == 4]}")
        print(f"🔤 5-letter words: {[w for w in uppercase_words if len(w) == 5]}")
        print(f"🔤 6+ letter words: {[w for w in uppercase_words if len(w) >= 6]}")
        
        print(f"\n📋 ALL WORDS (by length):")
        current_length = 0
        for word in uppercase_words:
            if len(word) != current_length:
                current_length = len(word)
                print(f"\n{current_length}-letter words:")
            print(f"  {word}")
        
        # Summary
        print(f"\n\n📊 SUMMARY:")
        print(f"Lowercase sequence total words: {len(lowercase_words)}")
        print(f"Uppercase sequence total words: {len(uppercase_words)}")
        
        # Common words between sequences
        common_words = set(lowercase_words) & set(uppercase_words)
        if common_words:
            print(f"🔗 Common words: {sorted(common_words)}")

def main():
    word_finder = CompleteWordList()
    word_finder.generate_complete_word_lists()

if __name__ == "__main__":
    main() 