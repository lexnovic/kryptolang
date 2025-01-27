import hashlib
import hmac
from typing import Dict, Tuple, List

class Kryptolang:
    """
    Final debugged version with:
    1. Proper subject/verb separation
    2. Unique subject codes
    3. Correct tense handling
    """
    
    SUBJECTS = [
        "I", "you", "dog", "man", "woman",
        "tree", "water", "fire", "sun", "moon", "meat"
    ]
    CORE_VERBS = {'eat', 'kill', 'see'}
    SWADESH_LIST = SUBJECTS + list(CORE_VERBS)
    
    PHONETIC_RULES = {
        'consonants': ['p', 't', 'k', 's', 'm', 'n', 'l', 'r'],
        'vowels': ['a', 'i', 'u'],
        'max_length': 5
    }

    def __init__(self, passphrase: str):
        self.master_key = hashlib.sha3_256(passphrase.encode()).digest()
        self.lexicon, self.conjugations = self._build_lexicon()
        self.grammar = self._derive_grammar()
        self.subjects = self._create_subject_map()
        self.reverse_lexicon = {v:k for k,v in self.lexicon.items()}

    def _build_lexicon(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Generate unique words for each lexicon entry"""
        lexicon = {}
        conjugations = {}
        key_segment = self.master_key[8:16]
        
        for idx, word in enumerate(self.SWADESH_LIST):
            seed = hmac.new(key_segment, f"{idx}".encode(), hashlib.sha3_256).hexdigest()
            
            crypto_word = ''.join([
                self.PHONETIC_RULES['consonants'][int(seed[i], 16) % 8] if i%2==0 
                else self.PHONETIC_RULES['vowels'][int(seed[i], 16) % 3]
                for i in range(10)
            ])[:self.PHONETIC_RULES['max_length']]
            
            if word in self.CORE_VERBS:
                conjugations.update({
                    crypto_word: word,
                    f"{crypto_word}t": f"{word}ed",
                    f"{crypto_word}s": f"will {word}"
                })
            
            lexicon[word] = crypto_word
            
        return lexicon, conjugations

    def _derive_grammar(self) -> Dict[str, str]:
        return {
            'syntax': ['VO', 'OV'][self.master_key[24] % 2],
            'tense': ['past', 'present', 'future'][self.master_key[25] % 3]
        }

    def _create_subject_map(self) -> Dict[str, str]:
        return {word.lower(): self.lexicon[word] for word in self.SUBJECTS}

    def encrypt(self, text: str) -> str:
        components = {'subject': None, 'verb': None, 'object': []}
        
        try:
            words = [w.lower() for w in text.strip().split()]
            if not words:
                raise ValueError("Empty input")
            
            # Find first valid subject
            try:
                components['subject'] = next(
                    w for w in words 
                    if w in self.subjects
                )
            except StopIteration:
                raise ValueError("Missing valid subject (I/you/noun)")
            
            # Extract verb and objects
            subject_idx = words.index(components['subject'])
            verb_idx = subject_idx + 1
            if verb_idx >= len(words):
                raise ValueError("Missing verb")
            
            components['verb'] = words[verb_idx]
            components['object'] = words[verb_idx+1:]
            
            # Build elements
            subject_code = self.subjects[components['subject']]
            verb_base = self.lexicon.get(components['verb'], components['verb'])
            
            # Apply conjugations only to core verbs
            if components['verb'] in self.CORE_VERBS:
                if self.grammar['tense'] == 'past':
                    verb_form = f"{verb_base}t"
                elif self.grammar['tense'] == 'future':
                    verb_form = f"{verb_base}s"
                else:
                    verb_form = verb_base
            else:
                verb_form = components['verb']
            
            elements = {
                'V': f"{subject_code}-{verb_form}",
                'O': ' '.join(self.lexicon.get(w, w) for w in components['object'])
            }
            
            return ' '.join(elements[p] for p in self.grammar['syntax'] if elements[p])
            
        except Exception as e:
            return f"ENCRYPT_ERROR: {str(e)}"

    def decrypt(self, ciphertext: str) -> str:
        parts = {'subject': None, 'verb': None, 'object': []}
        
        try:
            elements = ciphertext.split()
            
            # Find verb element with subject code
            for i, element in enumerate(elements):
                if '-' in element:
                    subject_code, verb_form = element.split('-', 1)
                    
                    # Lookup subject using full crypto word
                    parts['subject'] = self.reverse_lexicon[subject_code].capitalize()
                    
                    # Handle verb conjugation
                    if verb_form in self.conjugations:
                        parts['verb'] = self.conjugations[verb_form]
                    else:
                        # Check for tense markers
                        if verb_form.endswith('t'):
                            base = verb_form[:-1]
                            parts['verb'] = self.conjugations.get(base, base) + "ed"
                        elif verb_form.endswith('s'):
                            base = verb_form[:-1]
                            parts['verb'] = "will " + self.conjugations.get(base, base)
                        else:
                            parts['verb'] = self.reverse_lexicon.get(verb_form, verb_form)
                    
                    elements.pop(i)
                    break
                
            # Process objects
            parts['object'] = [self.reverse_lexicon.get(e, e) for e in elements]
            
            return ' '.join(filter(None, [
                parts['subject'],
                parts['verb'],
                ' '.join(parts['object']) if parts['object'] else None
            ]))
            
        except Exception as e:
            return f"DECRYPT_ERROR: {str(e)}"

def run_validation_tests():
    test_cases = [
        ("I eat", "VO", "present", "I eat"),
        ("You kill dog", "OV", "past", "You killed dog"),
        ("Man see moon", "VO", "present", "Man see moon"),
        ("Woman eat unknown_food", "OV", "future", "Woman will eat unknown_food"),
        ("Tree absorb water", "VO", "present", "Tree absorb water"),
        ("Dog bark", "OV", "past", "Dog bark"),
        ("Eat meat", "VO", "present", "ENCRYPT_ERROR"),
        ("You see fire", "OV", "future", "You will see fire")
    ]
    
    passed = 0
    for idx, (text, syntax, tense, expected) in enumerate(test_cases, 1):
        print(f"\n{'='*40}")
        print(f"Test {idx}: {text}")
        print(f"Expected: {expected}")
        
        cipher = Kryptolang(f"testkey-{syntax}-{tense}")
        cipher.grammar.update({'syntax': syntax, 'tense': tense})
        
        encrypted = cipher.encrypt(text)
        decrypted = cipher.decrypt(encrypted) if "ERROR" not in encrypted else encrypted
        
        print(f"Encrypted: {encrypted}")
        print(f"Decrypted: {decrypted}")
        
        success = (
            (expected in decrypted) if "ERROR" in expected 
            else decrypted.lower() == expected.lower()
        )
        
        if success:
            passed += 1
            print("✓ PASSED")
        else:
            print("✗ FAILED")
    
    print(f"\nFinal Results: {passed}/{len(test_cases)} passed")
    if passed == len(test_cases):
        print("✅ All tests successful!")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    run_validation_tests()