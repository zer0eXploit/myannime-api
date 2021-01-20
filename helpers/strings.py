'''
helper.string

Used for internalization. Set the default locale to `en-us` and loads strings from json file.

'''
import json

default_locale = 'en-us'
string_cache = {}


def refresh():
    '''
    Reads text from default locale and caches it.
    '''
    global default_locale
    global string_cache
    with open(f'strings/{default_locale}.json') as f:
        string_cache = json.load(f)


def get_text(key: str):
    return string_cache[key]


def set_default_locale(locale: str):
    global default_locale
    default_locale = locale
    refresh()


refresh()
