import os, sys
from pathlib import Path

import wikipedia

# basedir of kotdg. ( i.e. basedir = 'kotdg/' )
basedir = Path(os.path.realpath(__file__)).parent
resourcedir = (basedir / '../resources/').resolve()

def get_random_page_content() -> str:
    page_title = wikipedia.random(1)
    try:
        page_content = wikipedia.page(page_title).summary
    except (wikipedia.DisambiguationError, wikipedia.PageError):
        return get_random_page_content()
    return page_content

def create_strings_from_wikipedia(minimum_length: int, maximum_length: int, count: int, lang: str) -> list:
    """
        Create strings by randomly picking Wikipedia articles and taking sentences from their summaries.
    """
    wikipedia.set_lang(lang)
    sentences = []

    while len(sentences) < count:
        page_content = get_random_page_content()
        processed_content = page_content.replace("\n", " ").split(". ")
        sentence_candidates = [
            s.strip() for s in processed_content 
            if minimum_length <= len(s.split()) <= maximum_length
        ]
        sentences.extend(sentence_candidates)

    return sentences[:count]