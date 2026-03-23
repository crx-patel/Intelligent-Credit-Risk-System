# services/chatbot.py — FULL UPGRADED VERSION
# Features: Memory + Small Talk + Hinglish + Follow-up Questions

import re
import numpy as np
from gensim.models import Word2Vec
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity

# ═══════════════════════════════════════════════════════════════
# 1. HINGLISH NORMALIZATION MAP
# ═══════════════════════════════════════════════════════════════
HINGLISH_MAP = {
    "mujhe": "i want",
    "muje": "i want",
    "chahiye": "need",
    "milega": "will i get",
    "milegi": "will i get",
    "kya": "",
    "hai": "is",
    "hain": "is",
    "mera": "my",
    "meri": "my",
    "kamai": "income",
    "karj": "debt",
    "umar": "age",
    "paisa": "money",
    "paise": "money",
    "loan": "loan",
    "score": "score",
    "card": "card",
    "risk": "risk",
    "improve": "improve",
    "badhaye": "improve",
    "badhao": "improve",
    "kitna": "how much",
    "kaise": "how",
    "kab": "when",
    "batao": "tell me",
    "bata": "tell",
    "nahi": "no",
    "hoga": "will happen",
    "shukriya": "thank you",
    "alvida": "bye",
    "namaste": "hello",
    "theek": "ok",
    "acha": "ok",
    "accha": "ok",
    "documents": "documents",
    "kagaz": "documents",
    "papers": "documents",
}

def normalize_hinglish(text: str) -> str:
    words  = text.lower().split()
    result = []
    for word in words:
        mapped = HINGLISH_MAP.get(word, word)
        if mapped:
            result.append(mapped)
    return " ".join(result)


# ═══════════════════════════════════════════════════════════════
# 2. CONTEXT EXTRACTOR (Memory updater)
# ═══════════════════════════════════════════════════════════════
def extract_context(user_input: str, memory: dict) -> dict:
    text = user_input.lower()

    # Income
    m = re.search(r"(?:income|kamai|salary|kamaai|earn)[^\d]*(\d+)", text)
    if m:
        memory["income"] = int(m.group(1))

    # Age
    m = re.search(r"(?:age|umar|umra|sal)[^\d]*(\d+)", text)
    if m:
        memory["age"] = int(m.group(1))

    # Debt ratio
    m = re.search(r"(?:debt|karj|loan ratio|debt ratio)[^\d]*(\d*\.?\d+)", text)
    if m:
        val = float(m.group(1))
        memory["debt"] = val if val <= 1 else val / 100

    # Credit utilization
    m = re.search(r"(?:utilization|util|credit use)[^\d]*(\d*\.?\d+)", text)
    if m:
        val = float(m.group(1))
        memory["utilization"] = val if val <= 1 else val / 100

    # Name
    m = re.search(r"(?:my name is|main hoon|mera naam|naam)[^\w]*([a-zA-Z]+)", text)
    if m:
        memory["name"] = m.group(1).capitalize()

    # Bare numbers — fill pending fields
    numbers = re.findall(r'\d+\.?\d*', text)
    if numbers and memory.get("pending_question"):
        val = float(numbers[0])
        pq  = memory["pending_question"]
        if pq == "income":
            memory["income"] = int(val)
        elif pq == "age":
            memory["age"] = int(val)
        elif pq == "debt":
            memory["debt"] = val if val <= 1 else val / 100
        elif pq == "utilization":
            memory["utilization"] = val if val <= 1 else val / 100
        memory["pending_question"] = None

    return memory


# ═══════════════════════════════════════════════════════════════
# 3. TRAINING DATA
# ═══════════════════════════════════════════════════════════════
TRAIN_DATA = [
    # eligibility
    ("am i eligible for credit card", "eligibility"),
    ("can i get approved", "eligibility"),
    ("will i get a card", "eligibility"),
    ("can i get loan", "eligibility"),
    ("am i eligible for loan", "eligibility"),
    ("loan approve hoga", "eligibility"),
    ("i want credit card", "eligibility"),
    ("i want loan", "eligibility"),
    ("will i get credit card", "eligibility"),
    ("loan milega", "eligibility"),
    ("card milega", "eligibility"),

    # risk
    ("what is my risk", "risk"),
    ("am i risky customer", "risk"),
    ("chance of default", "risk"),
    ("tell me my risk score", "risk"),
    ("default probability", "risk"),
    ("what is my credit score", "risk"),
    ("my risk score", "risk"),
    ("how risky am i", "risk"),

    # improvement
    ("how to improve credit score", "improvement"),
    ("how to reduce risk", "improvement"),
    ("tips to increase score", "improvement"),
    ("how to improve score", "improvement"),
    ("ways to improve finance", "improvement"),
    ("how to get better score", "improvement"),
    ("reduce my debt", "improvement"),

    # documents
    ("what documents do i need", "documents"),
    ("required documents", "documents"),
    ("document list", "documents"),
    ("which papers needed", "documents"),
    ("kyc documents", "documents"),
    ("what papers do i need", "documents"),

    # small_talk
    ("thank you", "small_talk"),
    ("thanks", "small_talk"),
    ("bye", "small_talk"),
    ("goodbye", "small_talk"),
    ("you are great", "small_talk"),
    ("very helpful", "small_talk"),
    ("ok got it", "small_talk"),
    ("ok", "small_talk"),
    ("great", "small_talk"),
    ("awesome", "small_talk"),

    # greeting
    ("hello", "greeting"),
    ("hi", "greeting"),
    ("hey", "greeting"),
    ("good morning", "greeting"),
    ("help", "greeting"),
    ("start", "greeting"),
]

# ═══════════════════════════════════════════════════════════════
# 4. WORD2VEC + INTENT MODEL
# ═══════════════════════════════════════════════════════════════
def tokenize(text: str):
    return text.lower().split()

_sentences = [tokenize(t[0]) for t in TRAIN_DATA]
_labels    = [t[1] for t in TRAIN_DATA]

w2v_model = Word2Vec(_sentences, vector_size=100, window=5, min_count=1, workers=1)

def sentence_vector(sentence: str) -> np.ndarray:
    words   = tokenize(sentence)
    vectors = [w2v_model.wv[w] for w in words if w in w2v_model.wv]
    if not vectors:
        return np.zeros(100)
    return np.mean(vectors, axis=0)

X = np.array([sentence_vector(t[0]) for t in TRAIN_DATA])
y = _labels

intent_model = LogisticRegression(max_iter=500)
intent_model.fit(X, y)

def similarity_fallback(user_input: str) -> str:
    vec      = sentence_vector(user_input).reshape(1, -1)
    all_vecs = np.array([sentence_vector(t[0]) for t in TRAIN_DATA])
    sims     = cosine_similarity(vec, all_vecs)
    return TRAIN_DATA[sims.argmax()][1]


# ═══════════════════════════════════════════════════════════════
# 5. PREDICTION HELPER
# ═══════════════════════════════════════════════════════════════
def _run_prediction(model, memory: dict):
    try:
        import joblib, os, pandas as pd
        sample = pd.DataFrame({
            "RevolvingUtilizationOfUnsecuredLines": [memory.get("utilization", 0.3)],
            "age":                                  [memory.get("age", 30)],
            "NumberOfTime30-59DaysPastDueNotWorse": [0],
            "DebtRatio":                            [memory.get("debt", 0.3)],
            "MonthlyIncome":                        [memory.get("income", 50000)],
            "NumberOfOpenCreditLinesAndLoans":      [5],
            "NumberOfTimes90DaysLate":              [0],
            "NumberRealEstateLoansOrLines":         [1],
            "NumberOfTime60-89DaysPastDueNotWorse": [0],
            "NumberOfDependents":                   [1],
        })
        if os.path.exists("models/scaler.pkl"):
            sample = joblib.load("models/scaler.pkl").transform(sample)
        prob = model.predict_proba(sample)[:, 1][0]
        return prob
    except Exception as e:
        return None


# ═══════════════════════════════════════════════════════════════
# 6. GLOBAL MEMORY (per session — reset on restart)
# ═══════════════════════════════════════════════════════════════
memory = {
    "name":             None,
    "income":           None,
    "age":              None,
    "debt":             None,
    "utilization":      None,
    "last_intent":      None,
    "pending_question": None,
}


def reset_memory():
    """Call this when user clears chat — resets all stored context."""
    global memory
    memory = {
        "name":             None,
        "income":           None,
        "age":              None,
        "debt":             None,
        "utilization":      None,
        "last_intent":      None,
        "pending_question": None,
    }

# ═══════════════════════════════════════════════════════════════
# 7. MAIN CHATBOT FUNCTION
# ═══════════════════════════════════════════════════════════════
def chatbot_response(user_input: str, model=None, user_data: dict = None) -> str:
    global memory

    # ── If user_data available (from Home tab), use it ────────────────────
    if user_data:
        memory["income"]      = user_data.get("MonthlyIncome", memory["income"])
        memory["age"]         = user_data.get("age", memory["age"])
        memory["debt"]        = user_data.get("DebtRatio", memory["debt"])
        memory["utilization"] = user_data.get("RevolvingUtilizationOfUnsecuredLines", memory["utilization"])

    # ── Extract context from current message ─────────────────────────────
    memory = extract_context(user_input, memory)

    # ── Normalize Hinglish ────────────────────────────────────────────────
    normalized = normalize_hinglish(user_input)

    # ── Handle pending follow-up question first ───────────────────────────
    if memory["pending_question"] and re.search(r'\d', user_input):
        pq = memory["pending_question"]
        # extract_context already filled the value above
        # Now check what's still missing
        return _check_and_predict(model, user_input)

    # ── Intent detection ──────────────────────────────────────────────────
    vec        = sentence_vector(normalized).reshape(1, -1)
    probs      = intent_model.predict_proba(vec)[0]
    intent     = intent_model.classes_[probs.argmax()]
    confidence = probs.max()

    if confidence < 0.45:
        intent = similarity_fallback(normalized)

    memory["last_intent"] = intent

    # ══════════════════════════════════════════════════════════════════════
    # INTENT RESPONSES
    # ══════════════════════════════════════════════════════════════════════

    # ── GREETING ─────────────────────────────────────────────────────────
    if intent == "greeting":
        name_part = f" **{memory['name']}**" if memory["name"] else ""
        return (
            f"👋 Hello{name_part}! Main **AI Credit Assistant** hoon.\n\n"
            "Aap mujhse pooch sakte ho:\n"
            "- 📊 `what is my risk` — credit risk score\n"
            "- 💳 `can i get credit card` — card eligibility\n"
            "- 🏦 `can i get loan` — loan eligibility\n"
            "- 💡 `how to improve score` — tips\n"
            "- 📄 `documents needed` — required docs\n\n"
            "Kya jaanna chahte ho? 😊"
        )

    # ── SMALL TALK ────────────────────────────────────────────────────────
    elif intent == "small_talk":
        txt = user_input.lower()
        if any(w in txt for w in ["thank", "thanks", "shukriya", "dhanyawad"]):
            return "😊 Khushi hui madad karke! Kuch aur poochna ho toh batao."
        elif any(w in txt for w in ["bye", "goodbye", "alvida", "tata"]):
            return "👋 Alvida! Apna financial health achha rakho. 💪"
        elif any(w in txt for w in ["great", "good", "best", "helpful", "awesome", "nice"]):
            return "🙏 Shukriya! Main hamesha yahan hoon help ke liye. 😊"
        else:
            return "😊 Theek hai! Kuch aur poochna ho toh batao."

    # ── RISK ─────────────────────────────────────────────────────────────
    elif intent == "risk":
        return _handle_risk(model)

    # ── ELIGIBILITY ──────────────────────────────────────────────────────
    elif intent == "eligibility":
        return _handle_eligibility(model, user_input)

    # ── IMPROVEMENT ──────────────────────────────────────────────────────
    elif intent == "improvement":
        # Personalized tips based on memory
        tips = [
            "1. ✅ **EMI aur bills time pe bharein** — payment history #1 factor hai",
            "2. 💳 **Credit utilization 30% se kam** rakhen",
            "3. 🚫 **Multiple loans ek saath mat lein**",
            "4. 📊 **CIBIL report regularly check** karein — errors report karein",
            "5. 💰 **Debt ratio 40% se kam** rakhen",
            "6. 🏦 **Emergency fund** banayein — 3-6 months expenses",
        ]
        extra = ""
        if memory["debt"] and memory["debt"] > 0.4:
            extra = f"\n\n⚠️ **Aapka debt ratio {memory['debt']:.1%} hai** — ye high hai. Pehle ye kam karo!"
        if memory["utilization"] and memory["utilization"] > 0.3:
            extra += f"\n⚠️ **Credit utilization {memory['utilization']:.1%} hai** — 30% se neeche laao."

        return "📈 **Credit Score Improve Karne ke Tips:**\n\n" + "\n".join(tips) + extra + "\n\n🎯 6 mahine follow karne se score significantly improve hoga!"

    # ── DOCUMENTS ────────────────────────────────────────────────────────
    elif intent == "documents":
        return (
            "📄 **Required Documents Checklist:**\n\n"
            "**🪪 Identity Proof (koi ek):**\n"
            "- Aadhar Card\n- PAN Card\n- Passport\n\n"
            "**🏠 Address Proof (koi ek):**\n"
            "- Utility Bill (last 3 months)\n- Rent Agreement\n- Voter ID\n\n"
            "**💰 Income Proof:**\n"
            "- Last 3 months Salary Slips\n"
            "- Last 6 months Bank Statement\n"
            "- ITR (last 2 years)\n\n"
            "✅ Saare documents ready rakhen bank visit se pehle!"
        )

    # ── FALLBACK ─────────────────────────────────────────────────────────
    return (
        "❓ **Samajh nahi aaya.**\n\n"
        "Ye try karo:\n"
        "- `what is my risk`\n"
        "- `can i get loan`\n"
        "- `how to improve score`\n"
        "- `documents needed`\n"
        "- `hello`"
    )


# ═══════════════════════════════════════════════════════════════
# 8. HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _check_and_predict(model, user_input: str) -> str:
    """After follow-up answer received — check if more info needed or predict."""
    if memory["income"] is None:
        memory["pending_question"] = "income"
        return "💰 Monthly income kitni hai? (e.g. `50000`)"
    if memory["age"] is None:
        memory["pending_question"] = "age"
        return "📅 Aapki age kitni hai? (e.g. `35`)"
    if memory["debt"] is None:
        memory["pending_question"] = "debt"
        return "💸 Debt ratio kitna hai? (0 se 1 ke beech, e.g. `0.4`)"

    memory["pending_question"] = None
    intent = memory.get("last_intent", "risk")
    if intent == "eligibility":
        return _handle_eligibility(model, "loan")
    return _handle_risk(model)


def _handle_risk(model) -> str:
    """Risk response — with follow-up if data missing."""
    if memory["income"] is None:
        memory["pending_question"] = "income"
        memory["last_intent"]      = "risk"
        return "📊 Risk calculate karne ke liye pehle kuch details chahiye.\n\n💰 **Monthly income kitni hai?** (e.g. `50000`)"

    if memory["age"] is None:
        memory["pending_question"] = "age"
        memory["last_intent"]      = "risk"
        return "📅 **Aapki age kitni hai?** (e.g. `35`)"

    if memory["debt"] is None:
        memory["pending_question"] = "debt"
        memory["last_intent"]      = "risk"
        return "💸 **Debt ratio kitna hai?** (0 se 1 ke beech, e.g. `0.4`)\n_Matlab: monthly debt payments / monthly income_"

    if memory["utilization"] is None:
        memory["pending_question"] = "utilization"
        memory["last_intent"]      = "risk"
        return "💳 **Credit utilization kitna hai?** (0 se 1 ke beech, e.g. `0.3`)\n_Matlab: kitna credit card balance use kar rahe ho_"
    if model is not None:
        prob = _run_prediction(model, memory)
        if prob is not None:
            risk_pct = round(prob * 100, 1)
            if prob < 0.08:
                label, msg = "🟢 Low Risk", "Excellent! Loan approval chances bahut achhe hain."
            elif prob < 0.14:
                label, msg = "🟡 Medium Risk", "Moderate risk. Conditional approval possible."
            else:
                label, msg = "🔴 High Risk", "High risk. Score improve karo pehle."

            name_part = f"**{memory['name']}**, " if memory["name"] else ""
            return (
                f"📊 **Credit Risk Analysis**\n\n"
                f"{name_part}aapka result:\n\n"
                f"**Default Probability:** {risk_pct}%\n"
                f"**Risk Category:** {label}\n\n"
                f"{msg}\n\n"
                f"💡 Score improve karne ke liye `how to improve score` poochein."
            )

    return (
        "📊 **Risk Score**\n\n"
        "Pehle **🏠 Home tab** mein details enter karein:\n"
        "`35 50000 0.4 0.3` (age income debt utilization)\n\n"
        "Phir main exact risk bata sakta hoon!"
    )


def _handle_eligibility(model, user_input: str) -> str:
    """Eligibility response — detect product + follow-up if data missing."""
    txt = user_input.lower()
    if any(w in txt for w in ["credit card", "card", "cc"]):
        product, icon, tip = "Credit Card", "💳", "💳 Credit Card tab mein detailed check karo!"
    elif any(w in txt for w in ["home loan", "home", "ghar"]):
        product, icon, tip = "Home Loan", "🏠", "🏠 Bank branch mein home loan ke liye apply karo!"
    elif any(w in txt for w in ["car", "vehicle", "gaadi"]):
        product, icon, tip = "Car Loan", "🚗", "🚗 Car loan ke liye dealership ya bank contact karo!"
    else:
        product, icon, tip = "Loan", "🏦", "🏦 Nearest bank branch mein apply kar sakte ho!"

    if memory["income"] is None:
        memory["pending_question"] = "income"
        memory["last_intent"]      = "eligibility"
        return f"{icon} **{product} Eligibility Check**\n\n💰 **Monthly income kitni hai?** (e.g. `50000`)"

    if memory["age"] is None:
        memory["pending_question"] = "age"
        memory["last_intent"]      = "eligibility"
        return f"📅 **Aapki age kitni hai?** (e.g. `35`)"

    if memory["debt"] is None:
        memory["pending_question"] = "debt"
        memory["last_intent"]      = "eligibility"
        return f"{icon} **Debt ratio kitna hai?** (0 se 1 ke beech, e.g. `0.4`)"

    if memory["utilization"] is None:
        memory["pending_question"] = "utilization"
        memory["last_intent"]      = "eligibility"
        return f"{icon} **Credit utilization kitna hai?** (0 se 1 ke beech, e.g. `0.3`)"
    if model is not None:
        prob = _run_prediction(model, memory)
        if prob is not None:
            approved = prob < 0.5
            name_part = f"**{memory['name']}**, " if memory["name"] else ""
            return (
                f"{icon} **{product} Eligibility Result**\n\n"
                f"{name_part}aapka result:\n\n"
                f"{'✅ **Approved!** Aap eligible hain.' if approved else '❌ **Not Eligible** abhi ke liye.'}\n\n"
                f"**Default Risk:** {round(prob * 100, 1)}%\n\n"
                f"{'🎉 ' + tip if approved else '💡 Score improve karne ke liye `how to improve score` poochein.'}"
            )

    return (
        f"{icon} **{product} Eligibility**\n\n"
        "Pehle **🏠 Home tab** mein details enter karo:\n"
        "`35 50000 0.4 0.3` (age income debt utilization)"
    )