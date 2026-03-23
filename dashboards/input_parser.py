import re
import os
import queue
import json

# ── English Number Words ───────────────────────────────────────────────────────
ENG_ONES = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
    "eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,
    "fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,
    "nineteen":19,"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,
    "seventy":70,"eighty":80,"ninety":90,"hundred":100,
}
ENG_MULTIPLIERS = {"thousand":1000,"lakh":100000,"hundred":100}

# ── Hindi Number Words ─────────────────────────────────────────────────────────
HINDI_ONES = {
    "शून्य":0,"एक":1,"दो":2,"तीन":3,"चार":4,"पाँच":5,"पांच":5,
    "छह":6,"छः":6,"सात":7,"आठ":8,"नौ":9,"दस":10,
    "पैंतीस":35,"पचास":50,"तीस":30,"चालीस":40,"बीस":20,
    "इक्कीस":21,"बाईस":22,"तेईस":23,"चौबीस":24,"पच्चीस":25,
    "छब्बीस":26,"सत्ताईस":27,"अट्ठाईस":28,"उनतीस":29,
    "इकतीस":31,"बत्तीस":32,"तैंतीस":33,"चौंतीस":34,
    "छत्तीस":36,"सैंतीस":37,"अड़तीस":38,"उनतालीस":39,
    "साठ":60,"सत्तर":70,"अस्सी":80,"नब्बे":90,"सौ":100,
}
HINDI_MULTIPLIERS = {"हजार":1000,"लाख":100000}

ROMAN_HINDI_ONES = {
    "shunya":0,"zero":0,"ek":1,"do":2,"teen":3,"char":4,"paanch":5,"panch":5,
    "chhe":6,"saat":7,"aath":8,"nau":9,"das":10,"bees":20,"tees":30,
    "chalis":40,"pachas":50,"saath":60,"sattar":70,"assi":80,"nabbe":90,
    "paindees":35,"paintees":35,"paitis":35,"pachees":25,"ikees":21,
}
ROMAN_HINDI_MULTIPLIERS = {"hazar":1000,"hazaar":1000,"lakh":100000}

DECIMAL_WORDS = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,
    "जीरो":0,"शून्य":0,"एक":1,"दो":2,"तीन":3,"चार":4,
    "पाँच":5,"पांच":5,"छह":6,"सात":7,"आठ":8,"नौ":9,
}


def _words_to_number(tokens: list) -> float | None:
    result = 0
    current = 0
    for w in tokens:
        w = w.lower().strip(",.")
        if w in ENG_MULTIPLIERS:
            if current == 0: current = 1
            result += current * ENG_MULTIPLIERS[w]
            current = 0
        elif w in ENG_ONES:
            current += ENG_ONES[w]
        elif w in HINDI_ONES:
            current += HINDI_ONES[w]
        elif w in HINDI_MULTIPLIERS:
            if current == 0: current = 1
            result += current * HINDI_MULTIPLIERS[w]
            current = 0
        elif w in ROMAN_HINDI_ONES:
            current += ROMAN_HINDI_ONES[w]
        elif w in ROMAN_HINDI_MULTIPLIERS:
            if current == 0: current = 1
            result += current * ROMAN_HINDI_MULTIPLIERS[w]
            current = 0
        else:
            try:
                current += float(w)
            except ValueError:
                pass
    result += current
    return result if result > 0 else None


def _parse_decimal(tokens: list, start: int) -> tuple[float | None, int]:
    """
    Parse 'point four' or 'point zero three' starting from index start.
    Returns (value, next_index)
    """
    if start >= len(tokens):
        return None, start
    
    digits = []
    i = start
    while i < len(tokens) and i < start + 5:
        w = tokens[i].lower().strip(",.")
        if w in DECIMAL_WORDS:
            digits.append(str(DECIMAL_WORDS[w]))
            i += 1
        elif w.isdigit() and len(w) == 1:
            digits.append(w)
            i += 1
        else:
            break
    
    if digits:
        try:
            return float(f"0.{''.join(digits)}"), i
        except Exception:
            pass
    return None, start


def _extract_number_from_tokens(tokens: list, start: int, end: int) -> float | None:
    """Extract a number (possibly with 'point') from tokens[start:end]"""
    segment = tokens[start:end]
    
    # Check for decimal in segment
    point_words = ["point", "पॉइंट", "पाइंट", "दशमलव"]
    for pi, t in enumerate(segment):
        if t.lower().strip(",.") in point_words:
            left  = segment[:pi]
            right = segment[pi+1:]
            left_num = _words_to_number(left) or 0
            if right:
                dec_val, _ = _parse_decimal(right, 0)
                if dec_val is not None:
                    return left_num + dec_val
    
    # No decimal — just a whole number
    return _words_to_number(segment)


def parse_natural_language(text: str) -> dict | None:
    """
    Parse any format:
    - "35 50000 0.4 0.3"
    - "I am thirty five years old, income fifty thousand, debt zero point four, credit zero point three"
    - "meri umar paintees hai kamai pachas hazar karj zero point char credit zero point teen"
    - "पैंतीस कमाई पचास हजार कर्ज जीरो पॉइंट चार"
    """
    text = text.strip()
    tokens = text.lower().split()

    # ── Fast path: 4 plain numbers ─────────────────────────────────────────────
    parts = text.split()
    if len(parts) == 4:
        try:
            a, b, c, d = map(float, parts)
            if 18 <= a <= 100 and b > 0:
                return {"age":a,"MonthlyIncome":b,"DebtRatio":c,
                        "RevolvingUtilizationOfUnsecuredLines":d}
        except ValueError:
            pass

    # ── Find field boundaries using keywords ───────────────────────────────────
    AGE_KW    = {"age","umar","umra","old","sal","saal","years","year","उम्र","उमर","साल","i am","iam"}
    INCOME_KW = {"income","salary","kamai","tankhwah","महीना","mahina","कमाई","आय","earning","earn"}
    DEBT_KW   = {"debt","karj","loan","कर्ज","ऋण","ratio","address","गज"}
    UTIL_KW   = {"credit","util","utilization","क्रेडिट","उपयोग","pen","pane","granted"}
    POINT_KW  = {"point","पॉइंट","पाइंट","दशमलव"}

    # Find keyword positions
    kw_positions = {}
    for i, t in enumerate(tokens):
        t_clean = t.strip(",.")
        if t_clean in AGE_KW:    kw_positions.setdefault("age", i)
        if t_clean in INCOME_KW: kw_positions.setdefault("income", i)
        if t_clean in DEBT_KW:   kw_positions.setdefault("debt", i)
        if t_clean in UTIL_KW:   kw_positions.setdefault("util", i)

    age = income = debt = util = None

    # ── Extract age ────────────────────────────────────────────────────────────
    # Try after "i am" or "age"
    age_idx = kw_positions.get("age")
    if age_idx is not None:
        next_idx = kw_positions.get("income", age_idx + 6)
        val = _extract_number_from_tokens(tokens, age_idx + 1, min(age_idx + 5, next_idx))
        if val and 18 <= val <= 100:
            age = val
        # Also try before keyword
        if age is None:
            val = _extract_number_from_tokens(tokens, max(0, age_idx - 4), age_idx)
            if val and 18 <= val <= 100:
                age = val

    # ── Extract income ────────────────────────────────────────────────────────
    inc_idx = kw_positions.get("income")
    if inc_idx is not None:
        next_idx = kw_positions.get("debt", inc_idx + 8)
        val = _extract_number_from_tokens(tokens, inc_idx + 1, min(inc_idx + 7, next_idx))
        if val and val > 100:
            income = val

    # ── Extract debt ratio ────────────────────────────────────────────────────
    debt_idx = kw_positions.get("debt")
    if debt_idx is not None:
        next_idx = kw_positions.get("util", debt_idx + 8)
        val = _extract_number_from_tokens(tokens, debt_idx + 1, min(debt_idx + 7, next_idx))
        if val is not None and 0 <= val <= 5:
            debt = min(val, 1.0)

    # ── Extract credit util ───────────────────────────────────────────────────
    util_idx = kw_positions.get("util")
    if util_idx is not None:
        val = _extract_number_from_tokens(tokens, util_idx + 1, min(util_idx + 7, len(tokens)))
        if val is not None and 0 <= val <= 5:
            util = min(val, 1.0)

    if all(v is not None for v in [age, income, debt, util]):
        return {"age":age,"MonthlyIncome":income,"DebtRatio":debt,
                "RevolvingUtilizationOfUnsecuredLines":util}

    # ── Fallback: extract all numbers/number-words in order ───────────────────
    numbers = []
    i = 0
    while i < len(tokens):
        t = tokens[i].strip(",.")
        
        # Check decimal pattern
        if t in POINT_KW:
            if numbers:
                dec_val, next_i = _parse_decimal(tokens, i + 1)
                if dec_val is not None:
                    numbers[-1] = numbers[-1] + dec_val
                    i = next_i
                    continue

        # Try digit
        try:
            numbers.append(float(t))
            i += 1
            continue
        except ValueError:
            pass

        # Try number word — collect consecutive number words
        word_buf = []
        j = i
        while j < len(tokens) and j < i + 6:
            w = tokens[j].strip(",.")
            if (w in ENG_ONES or w in ENG_MULTIPLIERS or
                w in HINDI_ONES or w in HINDI_MULTIPLIERS or
                w in ROMAN_HINDI_ONES or w in ROMAN_HINDI_MULTIPLIERS):
                word_buf.append(w)
                j += 1
            else:
                break

        if word_buf:
            val = _words_to_number(word_buf)
            if val:
                numbers.append(val)
            i = j
            continue

        i += 1

    if len(numbers) >= 4:
        a, b, c, d = numbers[0], numbers[1], numbers[2], numbers[3]
        if 18 <= a <= 100 and b > 100:
            return {"age":a,"MonthlyIncome":b,"DebtRatio":min(c,1.0),
                    "RevolvingUtilizationOfUnsecuredLines":min(d,1.0)}

    return None


def voice_to_text(lang: str = "en", duration: int = 8) -> tuple[str, str]:
    """Offline voice recognition using Vosk."""
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer

        model_path = f"models/vosk-model-small-en-us-0.15" if lang == "en" else f"models/vosk-model-small-hi-0.22"
        model      = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        q          = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        result_text = ""
        with sd.RawInputStream(samplerate=16000, blocksize=8000,
                               dtype="int16", channels=1, callback=callback):
            for _ in range(int(16000 / 8000 * duration)):
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get("text"):
                        result_text += " " + result["text"]

            final = json.loads(recognizer.FinalResult())
            if final.get("text"):
                result_text += " " + final["text"]

        result_text = result_text.strip()
        if not result_text:
            return "", "No speech detected. Please try again."
        return result_text, ""

    except Exception as e:
        return "", f"Voice error: {str(e)}"


# ── English Number Words to Digits ────────────────────────────────────────────
EN_ONES = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
    "eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,
    "fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,
    "nineteen":19,"twenty":20,"thirty":30,"forty":40,"fifty":50,
    "sixty":60,"seventy":70,"eighty":80,"ninety":90,
}
EN_MULTIPLIERS = {
    "hundred": 100, "thousand": 1000, "lakh": 100000, "lac": 100000,
}


def _en_words_to_number(words: list) -> float | None:
    """Convert English number words to float. e.g. ['thirty','thousand'] → 30000"""
    result  = 0
    current = 0
    for w in words:
        w = w.lower().strip().rstrip(".,")
        if w in EN_ONES:
            current += EN_ONES[w]
        elif w in EN_MULTIPLIERS:
            if w == "hundred":
                current = (current if current else 1) * 100
            else:
                result += (current if current else 1) * EN_MULTIPLIERS[w]
                current = 0
        else:
            try:
                current += float(w)
            except ValueError:
                pass
    result += current
    return result if result > 0 else None


def _convert_en_number_words(text: str) -> str:
    """
    Replace English number word sequences in text with digits.
    e.g. 'thirty thousand' → '30000', 'zero point three' → '0.3'
    """
    text = text.lower()

    # Handle decimal: "zero point four" → "0.4"
    decimal_pattern = r'\b(zero|one|two|three|four|five|six|seven|eight|nine)\s+point\s+((?:zero|one|two|three|four|five|six|seven|eight|nine)\s*)+'
    def replace_decimal(m):
        left  = m.group(1)
        right = m.group(0).split("point", 1)[1].strip()
        l_val = EN_ONES.get(left, 0)
        r_digits = [str(EN_ONES.get(w.strip(), w.strip())) for w in right.split()]
        return f"{l_val}.{''.join(r_digits)}"

    text = re.sub(decimal_pattern, replace_decimal, text)

    # Handle whole number word sequences
    all_words = list(EN_ONES.keys()) + list(EN_MULTIPLIERS.keys())
    pattern = r'\b(?:' + '|'.join(all_words) + r')(?:\s+(?:' + '|'.join(all_words) + r'))*\b'

    def replace_number(m):
        words  = m.group(0).split()
        result = _en_words_to_number(words)
        if result is not None:
            return str(int(result)) if result == int(result) else str(result)
        return m.group(0)

    text = re.sub(pattern, replace_number, text, flags=re.IGNORECASE)
    return text


# Patch parse_natural_language to convert English number words first
_parse_with_hindi = parse_natural_language

def parse_natural_language(text: str) -> dict | None:
    # Convert English number words → digits first
    converted = _convert_en_number_words(text)
    result = _parse_with_hindi(converted)
    if result:
        return result
    # Also try original text
    return _parse_with_hindi(text)


# ── Hindi Number Words to Digits (Text Conversion) ────────────────────────────
HINDI_WORD_MAP = {
    # Devanagari
    "शून्य":0,"एक":1,"दो":2,"तीन":3,"चार":4,"पाँच":5,"पांच":5,
    "छह":6,"छः":6,"सात":7,"आठ":8,"नौ":9,"दस":10,
    "ग्यारह":11,"बारह":12,"तेरह":13,"चौदह":14,"पंद्रह":15,
    "सोलह":16,"सत्रह":17,"अठारह":18,"उन्नीस":19,"बीस":20,
    "इक्कीस":21,"बाईस":22,"तेईस":23,"चौबीस":24,"पच्चीस":25,
    "छब्बीस":26,"सत्ताईस":27,"अट्ठाईस":28,"उनतीस":29,"तीस":30,
    "इकतीस":31,"बत्तीस":32,"तैंतीस":33,"चौंतीस":34,"पैंतीस":35,
    "छत्तीस":36,"सैंतीस":37,"अड़तीस":38,"उनतालीस":39,"चालीस":40,
    "इकतालीस":41,"बयालीस":42,"तैंतालीस":43,"चौवालीस":44,"पैंतालीस":45,
    "छियालीस":46,"सैंतालीस":47,"अड़तालीस":48,"उनचास":49,"पचास":50,
    "इक्यावन":51,"बावन":52,"तिरपन":53,"चौवन":54,"पचपन":55,
    "छप्पन":56,"सत्तावन":57,"अट्ठावन":58,"उनसठ":59,"साठ":60,
    "इकसठ":61,"बासठ":62,"तिरसठ":63,"चौंसठ":64,"पैंसठ":65,
    "छियासठ":66,"सड़सठ":67,"अड़सठ":68,"उनहत्तर":69,"सत्तर":70,
    "इकहत्तर":71,"बहत्तर":72,"तिहत्तर":73,"चौहत्तर":74,"पचहत्तर":75,
    "छिहत्तर":76,"सतहत्तर":77,"अठहत्तर":78,"उनासी":79,"अस्सी":80,
    "इक्यासी":81,"बयासी":82,"तिरासी":83,"चौरासी":84,"पचासी":85,
    "छियासी":86,"सत्तासी":87,"अट्ठासी":88,"नवासी":89,"नब्बे":90,
    "इक्यानबे":91,"बानबे":92,"तिरानबे":93,"चौरानबे":94,"पचानबे":95,
    "छियानबे":96,"सत्तानबे":97,"अट्ठानबे":98,"निन्यानबे":99,"सौ":100,
    # Roman Hindi
    "shunya":0,"ek":1,"do":2,"teen":3,"chaar":4,"char":4,"paanch":5,"panch":5,
    "chhe":6,"saat":7,"aath":8,"nau":9,"das":10,
    "gyarah":11,"barah":12,"terah":13,"chaudah":14,"pandrah":15,
    "solah":16,"satrah":17,"atharah":18,"unnis":19,"bees":20,
    "ikkees":21,"baees":22,"teis":23,"chaubees":24,"pachees":25,
    "chhabbees":26,"sattaees":27,"atthaees":28,"untees":29,"tees":30,
    "ikattees":31,"battees":32,"taintees":33,"chauntees":34,"paintees":35,
    "paindees":35,"paitis":35,"chhattees":36,"saintees":37,"adtees":38,
    "untaalees":39,"chaalees":40,"pachaas":50,"saath":60,"sattar":70,
    "assi":80,"nabbe":90,"sau":100,
}

HINDI_MULT_MAP = {
    "हजार":1000,"hazaar":1000,"hazar":1000,
    "लाख":100000,"lakh":100000,"lac":100000,
    "करोड़":10000000,"crore":10000000,
}

HINDI_DECIMAL_WORDS = {"पॉइंट","प्वाइंट","दशमलव","बिंदु","point","दशमलव"}


def _hi_words_to_number(words: list) -> float | None:
    result = current = 0
    for w in words:
        w = w.strip(".,।")
        if w in HINDI_MULT_MAP:
            result += (current if current else 1) * HINDI_MULT_MAP[w]
            current = 0
        elif w in HINDI_WORD_MAP:
            current += HINDI_WORD_MAP[w]
        else:
            try:
                current += float(w)
            except ValueError:
                pass
    result += current
    return result if result > 0 else None


def _convert_hindi_number_words(text: str) -> str:
    """
    Replace Hindi number word sequences in text with digits.
    e.g. 'पचास हजार' → '50000', 'जीरो पॉइंट चार' → '0.4'
    """
    tokens = text.split()
    result_tokens = []
    i = 0

    while i < len(tokens):
        t = tokens[i].strip(".,।")

        # Check for decimal pattern: <number_word> <point_word> <digit_words...>
        if t in HINDI_DECIMAL_WORDS or t.lower() in HINDI_DECIMAL_WORDS:
            # previous token was the integer part
            if result_tokens:
                left = result_tokens.pop()
                try:
                    left_val = int(float(left))
                except ValueError:
                    result_tokens.append(left)
                    result_tokens.append(t)
                    i += 1
                    continue
                # collect right side digits
                right_digits = []
                j = i + 1
                while j < len(tokens):
                    w = tokens[j].strip(".,।")
                    if w in HINDI_WORD_MAP and HINDI_WORD_MAP[w] < 10:
                        right_digits.append(str(HINDI_WORD_MAP[w]))
                        j += 1
                    elif w.isdigit() and len(w) == 1:
                        right_digits.append(w)
                        j += 1
                    else:
                        break
                if right_digits:
                    result_tokens.append(f"{left_val}.{''.join(right_digits)}")
                    i = j
                    continue
                else:
                    result_tokens.append(left)
            result_tokens.append(t)
            i += 1
            continue

        # Collect consecutive number words
        num_words = []
        j = i
        while j < len(tokens):
            w = tokens[j].strip(".,।")
            if w in HINDI_WORD_MAP or w in HINDI_MULT_MAP:
                num_words.append(w)
                j += 1
            else:
                break

        if num_words:
            val = _hi_words_to_number(num_words)
            if val is not None:
                result_tokens.append(str(int(val)) if val == int(val) else str(val))
                i = j
                continue

        result_tokens.append(tokens[i])
        i += 1

    return " ".join(result_tokens)


# Final patch — convert Hindi words too before parsing
_parse_en_converted = parse_natural_language

def parse_natural_language(text: str) -> dict | None:
    # Convert Hindi number words → digits
    hi_converted = _convert_hindi_number_words(text)
    result = _parse_en_converted(hi_converted)
    if result:
        return result
    return _parse_en_converted(text)