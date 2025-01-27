class CryptoProcessor:
    def __init__(self, lexicon: dict, grammar: dict):
        self.lexicon = lexicon
        self.grammar = grammar
        self.reverse_lexicon = {v:k for k,v in lexicon.items()}
    
    def encrypt(self, text: str) -> str:
        # Implementation using lexicon and grammar rules
        # (Similar to previous version but using service-based data)
    
    def decrypt(self, ciphertext: str) -> str:
        # Implementation using reverse lexicon
        # (Similar to previous version but using service-based data)