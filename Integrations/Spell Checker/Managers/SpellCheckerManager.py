from spellchecker import SpellChecker

# CONSTS
WORD_WHITELIST = ['microsoft', 'apple', 'google', 'siemplify', 'playbook', 'playbooks', 'usecase', 'usecases', 'saas']

class SpellCheckerManager(object):
    def __init__(self):
        self.spell = SpellChecker()
        self.spell.word_frequency.load_words(WORD_WHITELIST)
        
    def check_text(self, text, chunk_size = 300):
        results = []
        text_list = text.split(u" ")
        chunk = u""
        for word in text_list:
            if len(chunk) + len(word) < chunk_size:
                chunk += u" " + word
            else:
                results.extend(self.check_text_chunk(chunk))
                chunk = word
        if chunk:
            results.extend(self.check_text_chunk(chunk))
        return results
    
    def check_text_chunk(self, chunk):
        return self.spell.unknown(chunk)