from collections import OrderedDict

class TextParser:
    @staticmethod
    def parse(text: str) -> dict:
        """Parse text into structured components with unique words"""
        words = [w.lower() for w in text.strip().split()]
        return {
            'unique_words': list(OrderedDict.fromkeys(words)),
            'subjects': [w for w in words if w in ['i', 'you', 'he', 'she', 'it']],
            'verbs': [w for w in words if w in ['eat', 'kill', 'see']],
            'objects': [w for w in words if w not in ['i', 'you', 'he', 'she', 'it', 'eat', 'kill', 'see']]
        }