import random
import mimetypes

mimetypes.init()


def get_extensions_for_type(general_type)->str:
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext
def random_word_gen():
    alphabet = 'defghijklmnopqrstuvwxyz'
    used_words = set()
    used_words.add('')
    this_word = ''

    while True:
        while this_word in used_words:
            this_word = ''.join(random.choices(alphabet, k=random.randint(5, 14)))
        used_words.add(this_word)
        yield this_word
