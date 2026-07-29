import re
import pandas as pd

# ------------------------------------------------------------------
# Engineering Synonyms
# Add more as you encounter them.
# ------------------------------------------------------------------

SYNONYMS = {
    "assy": "assembly",
    "assy.": "assembly",
    "asm": "assembly",
    "brg": "bearing",
    "brkt": "bracket",
    "brkt.": "bracket",
    "brkts": "brackets",
    "ind": "indicator",
    "ind.": "indicator",
    "lvl": "level",
    "gb": "gearbox",
    "gbx": "gearbox",
    "m.m": "mm",
    "m.m.": "mm",
    "millimeter": "mm",
    "millimetre": "mm",
    "dia": "diameter",
    "dia.": "diameter"
}

# ------------------------------------------------------------------
# Words that don't affect engineering meaning
# ------------------------------------------------------------------

STOP_WORDS = {
    "the",
    "of",
    "for",
    "with",
    "and",
    "&",
    "to",
    "in",
    "on",
    "a",
    "an"
}

# ------------------------------------------------------------------
# Important engineering words
# These will later receive extra weight.
# ------------------------------------------------------------------

ENGINEERING_WORDS = {
    "bolt",
    "nut",
    "washer",
    "bearing",
    "shaft",
    "gear",
    "gearbox",
    "sprocket",
    "chain",
    "plate",
    "cover",
    "pipe",
    "seal",
    "ring",
    "pin",
    "bush",
    "housing",
    "casting",
    "wheel",
    "roller",
    "indicator",
    "assembly"
}


# ------------------------------------------------------------------
# Normalize text
# ------------------------------------------------------------------

def clean_description(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Replace -, /, (), commas etc.
    text = re.sub(r"[^\w\s]", " ", text)

    # Separate numbers from letters
    #
    # 6mm -> 6 mm
    # m16 -> m 16
    # 6204zz -> 6204 zz

    text = re.sub(r"([a-z])([0-9])", r"\1 \2", text)
    text = re.sub(r"([0-9])([a-z])", r"\1 \2", text)

    text = re.sub(r"\s+", " ", text).strip()

    words = []

    for word in text.split():

        word = SYNONYMS.get(word, word)

        if word not in STOP_WORDS:
            words.append(word)

    return " ".join(words)


# ------------------------------------------------------------------
# Tokenize
# ------------------------------------------------------------------

def tokenize(text):

    cleaned = clean_description(text)

    return cleaned.split()


# ------------------------------------------------------------------
# Sort tokens
#
# RapidFuzz token_sort_ratio performs much better
# when words are sorted.
# ------------------------------------------------------------------

def sorted_tokens(text):

    tokens = tokenize(text)

    tokens = sorted(tokens)

    return " ".join(tokens)


# ------------------------------------------------------------------
# Numbers
#
# Example:
#
# M16 Bolt
# 6204 Bearing
# 6 MM
# ------------------------------------------------------------------

def extract_numbers(text):

    cleaned = clean_description(text)

    return re.findall(r"\d+", cleaned)


# ------------------------------------------------------------------
# Engineering keywords
# ------------------------------------------------------------------

def engineering_tokens(text):

    tokens = tokenize(text)

    return [t for t in tokens if t in ENGINEERING_WORDS]


# ------------------------------------------------------------------
# Common words
# ------------------------------------------------------------------

def common_words(text1, text2):

    s1 = set(tokenize(text1))
    s2 = set(tokenize(text2))

    return sorted(list(s1.intersection(s2)))


# ------------------------------------------------------------------
# Engineering keyword score
#
# Returns percentage
# ------------------------------------------------------------------

def engineering_score(text1, text2):

    a = set(engineering_tokens(text1))
    b = set(engineering_tokens(text2))

    if len(a) == 0:
        return 100

    common = len(a.intersection(b))

    return round(common / len(a) * 100, 2)


# ------------------------------------------------------------------
# Number Match Score
# ------------------------------------------------------------------

def number_score(text1, text2):

    a = set(extract_numbers(text1))
    b = set(extract_numbers(text2))

    if len(a) == 0:
        return 100

    common = len(a.intersection(b))

    return round(common / len(a) * 100, 2)
