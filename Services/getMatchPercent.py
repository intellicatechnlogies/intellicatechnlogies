from re                                     import findall as search_text
from difflib                                import get_close_matches, SequenceMatcher

def getMatchPercent(OCR_TEXT: str=None, ADDRESS_STR: str=None):
    OCR_KWDS  = OCR_TEXT.strip().replace(",","").split(" ")
    ADDR_KWDS = ADDRESS_STR.strip().replace(",","").split(" ")
    matches = []
    for KWD_A in ADDR_KWDS:
        closeMatch = get_close_matches(word=KWD_A, possibilities=OCR_KWDS, n=1)
        if len(closeMatch) == 1:
            matches.append(SequenceMatcher(a=KWD_A, b=closeMatch[0]).ratio())
        else:
            matches.append(0.0)

    return (sum(matches)*100)//len(ADDR_KWDS)