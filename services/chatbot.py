# # ═════════════════════════════════════════════════════════════════════════════
# # Chatbot Service - Multi-Intent Financial Advisor
# # ═════════════════════════════════════════════════════════════════════════════

# """
# Intelligent financial advisor chatbot with Hinglish support.
# Features: Intent detection, contextual memory, risk assessment, eligibility checks.
# """

# # Standard Library Imports
# # ─────────────────────────────────────────────────────────────────────────────
# import re

# # Third-Party Imports
# # ─────────────────────────────────────────────────────────────────────────────
# import numpy as np
# import pandas as pd
# from gensim.models import Word2Vec
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics.pairwise import cosine_similarity


# # ═════════════════════════════════════════════════════════════════════════════
# # SECTION 1: HINGLISH NORMALIZATION
# # ═════════════════════════════════════════════════════════════════════════════

# HINGLISH_MAP = {
#     # Want/Need
#     "mujhe": "i want", "muje": "i want", "chahiye": "need",
#     # Will I get
#     "milega": "will i get", "milegi": "will i get",
#     # Questions
#     "kya": "", "kitna": "how much", "kaise": "how", "kab": "when",
#     # Is/Are
#     "hai": "is", "hain": "is",
#     # Possessive
#     "mera": "my", "meri": "my",
#     # Financial terms
#     "kamai": "income", "karj": "debt", "umar": "age", "paisa": "money", "paise": "money",
#     # Products
#     "loan": "loan", "score": "score", "card": "card", "risk": "risk",
#     # Improvement
#     "improve": "improve", "badhaye": "improve", "badhao": "improve",
#     # Commands
#     "batao": "tell me", "bata": "tell", "nahi": "no", "hoga": "will happen",
#     # Gratitude
#     "shukriya": "thank you", "dhanyawad": "thank you",
#     # Greetings/Exit
#     "namaste": "hello", "alvida": "bye", "theek": "ok", "acha": "ok", "accha": "ok",
#     # Documents
#     "documents": "documents", "kagaz": "documents", "papers": "documents",
# }


# def normalize_hinglish(text: str) -> str:
#     """
#     Normalize Hinglish (Hindi-English mix) to English.
    
#     Args:
#         text (str): Input text with Hinglish
        
#     Returns:
#         str: Normalized English text
#     """
#     words = text.lower().split()
#     result = []
#     for word in words:
#         mapped = HINGLISH_MAP.get(word, word)
#         if mapped:
#             result.append(mapped)
#     return " ".join(result)


# # ═════════════════════════════════════════════════════════════════════════════
# # SECTION 2: CONTEXT EXTRACTION & MEMORY
# # ═════════════════════════════════════════════════════════════════════════════

# def extract_context(user_input: str, memory: dict) -> dict:
#     """
#     Extract financial context from user input (Income, Age, Debt, etc).
#     Updates memory with extracted values.
    
#     Args:
#         user_input (str): User's message
#         memory (dict): Session memory to update
        
#     Returns:
#         dict: Updated memory dictionary
#     """
#     text = user_input.lower()

#     # Extract income
#     match = re.search(r"(?:income|kamai|salary|kamaai|earn)[^\d]*(\d+)", text)
#     if match:
#         memory["income"] = int(match.group(1))

#     # Extract age
#     match = re.search(r"(?:age|umar|umra|sal)[^\d]*(\d+)", text)
#     if match:
#         memory["age"] = int(match.group(1))

#     # Extract debt ratio
#     match = re.search(r"(?:debt|karj|loan ratio|debt ratio)[^\d]*(\d*\.?\d+)", text)
#     if match:
#         val = float(match.group(1))
#         memory["debt"] = val if val <= 1 else val / 100

#     # Extract credit utilization
#     match = re.search(r"(?:utilization|util|credit use)[^\d]*(\d*\.?\d+)", text)
#     if match:
#         val = float(match.group(1))
#         memory["utilization"] = val if val <= 1 else val / 100

#     # Extract name
#     match = re.search(r"(?:my name is|main hoon|mera naam|naam)[^\w]*([a-zA-Z]+)", text)
#     if match:
#         memory["name"] = match.group(1).capitalize()

#     # Fill pending fields with bare numbers
#     numbers = re.findall(r'\d+\.?\d*', text)
#     if numbers and memory.get("pending_question"):
#         val = float(numbers[0])
#         pending = memory["pending_question"]
        
#         if pending == "income":
#             memory["income"] = int(val)
#         elif pending == "age":
#             memory["age"] = int(val)
#         elif pending == "debt":
#             memory["debt"] = val if val <= 1 else val / 100
#         elif pending == "utilization":
#             memory["utilization"] = val if val <= 1 else val / 100
            
#         memory["pending_question"] = None

#     return memory


# # Global session memory
# memory = {
#     "name": None,
#     "income": None,
#     "age": None,
#     "debt": None,
#     "utilization": None,
#     "last_intent": None,
#     "pending_question": None,
# }


# def reset_memory():
#     """Reset chatbot memory (call when user clears chat)."""
#     global memory
#     memory = {
#         "name": None,
#         "income": None,
#         "age": None,
#         "debt": None,
#         "utilization": None,
#         "last_intent": None,
#         "pending_question": None,
#     }


# # ═════════════════════════════════════════════════════════════════════════════
# # SECTION 3: INTENT TRAINING DATA & MODEL
# # ═════════════════════════════════════════════════════════════════════════════

# TRAIN_DATA = [
#     # Eligibility queries
#     ("am i eligible for credit card", "eligibility"),
#     ("can i get approved", "eligibility"),
#     ("will i get a card", "eligibility"),
#     ("can i get loan", "eligibility"),
#     ("am i eligible for loan", "eligibility"),
#     ("loan approve hoga", "eligibility"),
#     ("i want credit card", "eligibility"),
#     ("i want loan", "eligibility"),
#     ("will i get credit card", "eligibility"),
#     ("loan milega", "eligibility"),
#     ("card milega", "eligibility"),

#     # Risk queries
#     ("what is my risk", "risk"),
#     ("am i risky customer", "risk"),
#     ("chance of default", "risk"),
#     ("tell me my risk score", "risk"),
#     ("default probability", "risk"),
#     ("what is my credit score", "risk"),
#     ("my risk score", "risk"),
#     ("how risky am i", "risk"),

#     # Improvement queries
#     ("how to improve credit score", "improvement"),
#     ("how to reduce risk", "improvement"),
#     ("tips to increase score", "improvement"),
#     ("how to improve score", "improvement"),
#     ("ways to improve finance", "improvement"),
#     ("how to get better score", "improvement"),
#     ("reduce my debt", "improvement"),

#     # Document queries
#     ("what documents do i need", "documents"),
#     ("required documents", "documents"),
#     ("document list", "documents"),
#     ("which papers needed", "documents"),
#     ("kyc documents", "documents"),
#     ("what papers do i need", "documents"),

#     # Small talk
#     ("thank you", "small_talk"),
#     ("thanks", "small_talk"),
#     ("bye", "small_talk"),
#     ("goodbye", "small_talk"),
#     ("you are great", "small_talk"),
#     ("very helpful", "small_talk"),
#     ("ok got it", "small_talk"),
#     ("ok", "small_talk"),
#     ("great", "small_talk"),
#     ("awesome", "small_talk"),

#     # Greetings
#     ("hello", "greeting"),
#     ("hi", "greeting"),
#     ("hey", "greeting"),
#     ("good morning", "greeting"),
#     ("help", "greeting"),
#     ("start", "greeting"),
# ]


# def tokenize(text: str) -> list:
#     """Tokenize text to words."""
#     return text.lower().split()


# # Train Word2Vec embeddings
# _sentences = [tokenize(t[0]) for t in TRAIN_DATA]
# _labels = [t[1] for t in TRAIN_DATA]

# w2v_model = Word2Vec(_sentences, vector_size=100, window=5, min_count=1, workers=1)


# def sentence_vector(sentence: str) -> np.ndarray:
#     """Convert sentence to Word2Vec embedding."""
#     words = tokenize(sentence)
#     vectors = [w2v_model.wv[w] for w in words if w in w2v_model.wv]
#     if not vectors:
#         return np.zeros(100)
#     return np.mean(vectors, axis=0)


# # Train intent classification model
# X = np.array([sentence_vector(t[0]) for t in TRAIN_DATA])
# y = _labels

# intent_model = LogisticRegression(max_iter=500)
# intent_model.fit(X, y)


# def similarity_fallback(user_input: str) -> str:
#     """Fallback intent detection using cosine similarity."""
#     vec = sentence_vector(user_input).reshape(1, -1)
#     all_vecs = np.array([sentence_vector(t[0]) for t in TRAIN_DATA])
#     sims = cosine_similarity(vec, all_vecs)
#     return TRAIN_DATA[sims.argmax()][1]


# # ═════════════════════════════════════════════════════════════════════════════
# # SECTION 4: PREDICTION HELPER
# # ═════════════════════════════════════════════════════════════════════════════

# def _run_prediction(model, memory: dict) -> float | None:
#     """
#     Run risk prediction using model and stored memory.
    
#     Args:
#         model: XGBoost risk model
#         memory (dict): User's financial context
        
#     Returns:
#         float: Default probability (0-1), or None if prediction fails
#     """
#     try:
#         import joblib
#         import os
        
#         sample = pd.DataFrame({
#             "RevolvingUtilizationOfUnsecuredLines": [memory.get("utilization", 0.3)],
#             "age": [memory.get("age", 30)],
#             "NumberOfTime30-59DaysPastDueNotWorse": [0],
#             "DebtRatio": [memory.get("debt", 0.3)],
#             "MonthlyIncome": [memory.get("income", 50000)],
#             "NumberOfOpenCreditLinesAndLoans": [5],
#             "NumberOfTimes90DaysLate": [0],
#             "NumberRealEstateLoansOrLines": [1],
#             "NumberOfTime60-89DaysPastDueNotWorse": [0],
#             "NumberOfDependents": [1],
#         })
        
#         if os.path.exists("models/scaler.pkl"):
#             sample = joblib.load("models/scaler.pkl").transform(sample)
            
#         prob = model.predict_proba(sample)[:, 1][0]
#         return prob
#     except Exception:
#         return None


# # ═════════════════════════════════════════════════════════════════════════════
# # SECTION 5: RESPONSE HANDLERS - HELPERS
# # ═════════════════════════════════════════════════════════════════════════════

# def _check_and_predict(model, user_input: str) -> str:
#     """Handle follow-up answers and check if more info needed."""
#     if memory["income"] is None:
#         memory["pending_question"] = "income"
#         return "💰 Monthly income kitni hai? (e.g. `50000`)"
        
#     if memory["age"] is None:
#         memory["pending_question"] = "age"
#         return "📅 Aapki age kitni hai? (e.g. `35`)"
        
#     if memory["debt"] is None:
#         memory["pending_question"] = "debt"
#         return "💸 Debt ratio kitna hai? (0 se 1 ke beech, e.g. `0.4`)"

#     memory["pending_question"] = None
#     intent = memory.get("last_intent", "risk")
    
#     if intent == "eligibility":
#         return _handle_eligibility(model, "loan")
#     return _handle_risk(model)


# def _handle_risk(model) -> str:
#     """Generate risk assessment response with progressive data collection."""
#     if memory["income"] is None:
#         memory["pending_question"] = "income"
#         memory["last_intent"] = "risk"
#         return "📊 Risk calculate karne ke liye pehle kuch details chahiye.\n\n💰 **Monthly income kitni hai?** (e.g. `50000`)"

#     if memory["age"] is None:
#         memory["pending_question"] = "age"
#         memory["last_intent"] = "risk"
#         return "📅 **Aapki age kitni hai?** (e.g. `35`)"

#     if memory["debt"] is None:
#         memory["pending_question"] = "debt"
#         memory["last_intent"] = "risk"
#         return "💸 **Debt ratio kitna hai?** (0 se 1 ke beech, e.g. `0.4`)\n_Matlab: monthly debt payments / monthly income_"

#     if memory["utilization"] is None:
#         memory["pending_question"] = "utilization"
#         memory["last_intent"] = "risk"
#         return "💳 **Credit utilization kitna hai?** (0 se 1 ke beech, e.g. `0.3`)\n_Matlab: kitna credit card balance use kar rahe ho_"
    
#     if model is not None:
#         prob = _run_prediction(model, memory)
#         if prob is not None:
#             risk_pct = round(prob * 100, 1)
            
#             if prob < 0.08:
#                 label, msg = "🟢 Low Risk", "Excellent! Loan approval chances bahut achhe hain."
#             elif prob < 0.14:
#                 label, msg = "🟡 Medium Risk", "Moderate risk. Conditional approval possible."
#             else:
#                 label, msg = "🔴 High Risk", "High risk. Score improve karo pehle."

#             name_part = f"**{memory['name']}**, " if memory["name"] else ""
#             return (
#                 f"📊 **Credit Risk Analysis**\n\n"
#                 f"{name_part}aapka result:\n\n"
#                 f"**Default Probability:** {risk_pct}%\n"
#                 f"**Risk Category:** {label}\n\n"
#                 f"{msg}\n\n"
#                 f"💡 Score improve karne ke liye `how to improve score` poochein."
#             )

#     return (
#         "📊 **Risk Score**\n\n"
#         "Pehle **🏠 Home tab** mein details enter karein:\n"
#         "`35 50000 0.4 0.3` (age income debt utilization)\n\n"
#         "Phir main exact risk bata sakta hoon!"
#     )


# def _handle_eligibility(model, user_input: str) -> str:
#     """Generate eligibility assessment response with product detection."""
#     txt = user_input.lower()
    
#     if any(w in txt for w in ["credit card", "card", "cc"]):
#         product, icon, tip = "Credit Card", "💳", "💳 Credit Card tab mein detailed check karo!"
#     elif any(w in txt for w in ["home loan", "home", "ghar"]):
#         product, icon, tip = "Home Loan", "🏠", "🏠 Bank branch mein home loan ke liye apply karo!"
#     elif any(w in txt for w in ["car", "vehicle", "gaadi"]):
#         product, icon, tip = "Car Loan", "🚗", "🚗 Car loan ke liye dealership ya bank contact karo!"
#     else:
#         product, icon, tip = "Loan", "🏦", "🏦 Nearest bank branch mein apply kar sakte ho!"

#     if memory["income"] is None:
#         memory["pending_question"] = "income"
#         memory["last_intent"] = "eligibility"
#         return f"{icon} **{product} Eligibility Check**\n\n💰 **Monthly income kitni hai?** (e.g. `50000`)"

#     if memory["age"] is None:
#         memory["pending_question"] = "age"
#         memory["last_intent"] = "eligibility"
#         return f"📅 **Aapki age kitni hai?** (e.g. `35`)"

#     if memory["debt"] is None:
#         memory["pending_question"] = "debt"
#         memory["last_intent"] = "eligibility"
#         return f"{icon} **Debt ratio kitna hai?** (0 se 1 ke beech, e.g. `0.4`)"

#     if memory["utilization"] is None:
#         memory["pending_question"] = "utilization"
#         memory["last_intent"] = "eligibility"
#         return f"{icon} **Credit utilization kitna hai?** (0 se 1 ke beech, e.g. `0.3`)"
    
#     if model is not None:
#         prob = _run_prediction(model, memory)
#         if prob is not None:
#             approved = prob < 0.5
#             name_part = f"**{memory['name']}**, " if memory["name"] else ""
#             return (
#                 f"{icon} **{product} Eligibility Result**\n\n"
#                 f"{name_part}aapka result:\n\n"
#                 f"{'✅ **Approved!** Aap eligible hain.' if approved else '❌ **Not Eligible** abhi ke liye.'}\n\n"
#                 f"**Default Risk:** {round(prob * 100, 1)}%\n\n"
#                 f"{'🎉 ' + tip if approved else '💡 Score improve karne ke liye `how to improve score` poochein.'}"
#             )

#     return (
#         f"{icon} **{product} Eligibility**\n\n"
#         "Pehle **🏠 Home tab** mein details enter karo:\n"
#         "`35 50000 0.4 0.3` (age income debt utilization)"
#     )


# # ═════════════════════════════════════════════════════════════════════════════
# # SECTION 6: MAIN CHATBOT FUNCTION
# # ═════════════════════════════════════════════════════════════════════════════

# def chatbot_response(user_input: str, model=None, user_data: dict = None) -> str:
#     """
#     Main chatbot response generator.
    
#     Args:
#         user_input (str): User's message
#         model: Risk prediction model
#         user_data (dict): Optional pre-filled user data from Home tab
        
#     Returns:
#         str: Formatted response message
#     """
#     global memory

#     # Update memory with pre-filled data if available
#     if user_data:
#         memory["income"] = user_data.get("MonthlyIncome", memory["income"])
#         memory["age"] = user_data.get("age", memory["age"])
#         memory["debt"] = user_data.get("DebtRatio", memory["debt"])
#         memory["utilization"] = user_data.get("RevolvingUtilizationOfUnsecuredLines", memory["utilization"])

#     # Extract context from user input
#     memory = extract_context(user_input, memory)

#     # Normalize Hinglish
#     normalized = normalize_hinglish(user_input)

#     # Handle pending follow-up questions
#     if memory["pending_question"] and re.search(r'\d', user_input):
#         return _check_and_predict(model, user_input)

#     # Detect intent
#     vec = sentence_vector(normalized).reshape(1, -1)
#     probs = intent_model.predict_proba(vec)[0]
#     intent = intent_model.classes_[probs.argmax()]
#     confidence = probs.max()

#     if confidence < 0.45:
#         intent = similarity_fallback(normalized)

#     memory["last_intent"] = intent

#     # ════════════════════════════════════════════════════════════════════════
#     # INTENT RESPONSES
#     # ════════════════════════════════════════════════════════════════════════

#     if intent == "greeting":
#         name_part = f" **{memory['name']}**" if memory["name"] else ""
#         return (
#             f"👋 Hello{name_part}! Main **AI Credit Assistant** hoon.\n\n"
#             "Aap mujhse pooch sakte ho:\n"
#             "- 📊 `what is my risk` — credit risk score\n"
#             "- 💳 `can i get credit card` — card eligibility\n"
#             "- 🏦 `can i get loan` — loan eligibility\n"
#             "- 💡 `how to improve score` — tips\n"
#             "- 📄 `documents needed` — required docs\n\n"
#             "Kya jaanna chahte ho? 😊"
#         )

#     elif intent == "small_talk":
#         txt = user_input.lower()
#         if any(w in txt for w in ["thank", "thanks", "shukriya", "dhanyawad"]):
#             return "😊 Khushi hui madad karke! Kuch aur poochna ho toh batao."
#         elif any(w in txt for w in ["bye", "goodbye", "alvida", "tata"]):
#             return "👋 Alvida! Apna financial health achha rakho. 💪"
#         elif any(w in txt for w in ["great", "good", "best", "helpful", "awesome", "nice"]):
#             return "🙏 Shukriya! Main hamesha yahan hoon help ke liye. 😊"
#         else:
#             return "😊 Theek hai! Kuch aur poochna ho toh batao."

#     elif intent == "risk":
#         return _handle_risk(model)

#     elif intent == "eligibility":
#         return _handle_eligibility(model, user_input)

#     elif intent == "improvement":
#         tips = [
#             "1. ✅ **EMI aur bills time pe bharein** — payment history #1 factor hai",
#             "2. 💳 **Credit utilization 30% se kam** rakhen",
#             "3. 🚫 **Multiple loans ek saath mat lein**",
#             "4. 📊 **CIBIL report regularly check** karein — errors report karein",
#             "5. 💰 **Debt ratio 40% se kam** rakhen",
#             "6. 🏦 **Emergency fund** banayein — 3-6 months expenses",
#         ]
        
#         extra = ""
#         if memory["debt"] and memory["debt"] > 0.4:
#             extra = f"\n\n⚠️ **Aapka debt ratio {memory['debt']:.1%} hai** — ye high hai. Pehle ye kam karo!"
#         if memory["utilization"] and memory["utilization"] > 0.3:
#             extra += f"\n⚠️ **Credit utilization {memory['utilization']:.1%} hai** — 30% se neeche laao."

#         return "📈 **Credit Score Improve Karne ke Tips:**\n\n" + "\n".join(tips) + extra + "\n\n🎯 6 mahine follow karne se score significantly improve hoga!"

#     elif intent == "documents":
#         return (
#             "📄 **Required Documents Checklist:**\n\n"
#             "**🪪 Identity Proof (koi ek):**\n"
#             "- Aadhar Card\n- PAN Card\n- Passport\n\n"
#             "**🏠 Address Proof (koi ek):**\n"
#             "- Utility Bill (last 3 months)\n- Rent Agreement\n- Voter ID\n\n"
#             "**💰 Income Proof:**\n"
#             "- Last 3 months Salary Slips\n"
#             "- Last 6 months Bank Statement\n"
#             "- ITR (last 2 years)\n\n"
#             "✅ Saare documents ready rakhen bank visit se pehle!"
#         )

#     # Fallback response
#     return (
#         "❓ **Samajh nahi aaya.**\n\n"
#         "Ye try karo:\n"
#         "- `what is my risk`\n"
#         "- `can i get loan`\n"
#         "- `how to improve score`\n"
#         "- `documents needed`\n"
#         "- `hello`"
#     )

# ═════════════════════════════════════════════════════════════════════════════
# Chatbot Service - Multi-Intent Financial Advisor
# ═════════════════════════════════════════════════════════════════════════════

"""
Intelligent financial advisor chatbot with Hinglish support.
Features: Intent detection (TF-IDF + Logistic Regression), contextual memory,
          risk assessment, eligibility checks.
"""

# Standard Library Imports
# ─────────────────────────────────────────────────────────────────────────────
import re

# Third-Party Imports
# ─────────────────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1: HINGLISH NORMALIZATION
# ═════════════════════════════════════════════════════════════════════════════

HINGLISH_MAP = {
    # Want/Need
    "mujhe": "i want", "muje": "i want", "chahiye": "need",
    # Will I get
    "milega": "will i get", "milegi": "will i get",
    # Questions
    "kya": "", "kitna": "how much", "kaise": "how", "kab": "when",
    # Is/Are
    "hai": "is", "hain": "is",
    # Possessive
    "mera": "my", "meri": "my",
    # Financial terms
    "kamai": "income", "karj": "debt", "umar": "age", "paisa": "money", "paise": "money",
    # Products
    "loan": "loan", "score": "score", "card": "card", "risk": "risk",
    # Improvement
    "improve": "improve", "badhaye": "improve", "badhao": "improve",
    # Commands
    "batao": "tell me", "bata": "tell", "nahi": "no", "hoga": "will happen",
    # Gratitude
    "shukriya": "thank you", "dhanyawad": "thank you",
    # Greetings/Exit
    "namaste": "hello", "alvida": "bye", "theek": "ok", "acha": "ok", "accha": "ok",
    # Documents
    "documents": "documents", "kagaz": "documents", "papers": "documents",
}


def normalize_hinglish(text: str) -> str:
    """
    Normalize Hinglish (Hindi-English mix) to English.

    Args:
        text (str): Input text with Hinglish

    Returns:
        str: Normalized English text
    """
    words = text.lower().split()
    result = []
    for word in words:
        mapped = HINGLISH_MAP.get(word, word)
        if mapped:
            result.append(mapped)
    return " ".join(result)


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2: CONTEXT EXTRACTION & MEMORY
# ═════════════════════════════════════════════════════════════════════════════

def extract_context(user_input: str, memory: dict) -> dict:
    """
    Extract financial context from user input (Income, Age, Debt, etc).
    Updates memory with extracted values.

    Args:
        user_input (str): User's message
        memory (dict): Session memory to update

    Returns:
        dict: Updated memory dictionary
    """
    text = user_input.lower()

    # Extract income
    match = re.search(r"(?:income|kamai|salary|kamaai|earn)[^\d]*(\d+)", text)
    if match:
        memory["income"] = int(match.group(1))

    # Extract age
    match = re.search(r"(?:age|umar|umra|sal)[^\d]*(\d+)", text)
    if match:
        memory["age"] = int(match.group(1))

    # Extract debt ratio
    match = re.search(r"(?:debt|karj|loan ratio|debt ratio)[^\d]*(\d*\.?\d+)", text)
    if match:
        val = float(match.group(1))
        memory["debt"] = val if val <= 1 else val / 100

    # Extract credit utilization
    match = re.search(r"(?:utilization|util|credit use)[^\d]*(\d*\.?\d+)", text)
    if match:
        val = float(match.group(1))
        memory["utilization"] = val if val <= 1 else val / 100

    # Extract name
    match = re.search(r"(?:my name is|main hoon|mera naam|naam)[^\w]*([a-zA-Z]+)", text)
    if match:
        memory["name"] = match.group(1).capitalize()

    # Fill pending fields with bare numbers
    numbers = re.findall(r'\d+\.?\d*', text)
    if numbers and memory.get("pending_question"):
        val = float(numbers[0])
        pending = memory["pending_question"]

        if pending == "income":
            memory["income"] = int(val)
        elif pending == "age":
            memory["age"] = int(val)
        elif pending == "debt":
            memory["debt"] = val if val <= 1 else val / 100
        elif pending == "utilization":
            memory["utilization"] = val if val <= 1 else val / 100

        memory["pending_question"] = None

    return memory


# Global session memory
memory = {
    "name": None,
    "income": None,
    "age": None,
    "debt": None,
    "utilization": None,
    "last_intent": None,
    "pending_question": None,
}


def reset_memory():
    """Reset chatbot memory (call when user clears chat)."""
    global memory
    memory = {
        "name": None,
        "income": None,
        "age": None,
        "debt": None,
        "utilization": None,
        "last_intent": None,
        "pending_question": None,
    }


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3: INTENT TRAINING DATA & MODEL  (TF-IDF BASED — no gensim)
# ═════════════════════════════════════════════════════════════════════════════

TRAIN_DATA = [
    # Eligibility queries
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

    # Risk queries
    ("what is my risk", "risk"),
    ("am i risky customer", "risk"),
    ("chance of default", "risk"),
    ("tell me my risk score", "risk"),
    ("default probability", "risk"),
    ("what is my credit score", "risk"),
    ("my risk score", "risk"),
    ("how risky am i", "risk"),

    # Improvement queries
    ("how to improve credit score", "improvement"),
    ("how to reduce risk", "improvement"),
    ("tips to increase score", "improvement"),
    ("how to improve score", "improvement"),
    ("ways to improve finance", "improvement"),
    ("how to get better score", "improvement"),
    ("reduce my debt", "improvement"),

    # Document queries
    ("what documents do i need", "documents"),
    ("required documents", "documents"),
    ("document list", "documents"),
    ("which papers needed", "documents"),
    ("kyc documents", "documents"),
    ("what papers do i need", "documents"),

    # Small talk
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

    # Greetings
    ("hello", "greeting"),
    ("hi", "greeting"),
    ("hey", "greeting"),
    ("good morning", "greeting"),
    ("help", "greeting"),
    ("start", "greeting"),
]

# ─────────────────────────────────────────────────────────────────────────────
# Build TF-IDF vectorizer + Logistic Regression intent model
# ─────────────────────────────────────────────────────────────────────────────
_train_texts  = [t[0] for t in TRAIN_DATA]
_train_labels = [t[1] for t in TRAIN_DATA]

# TfidfVectorizer: char n-grams (2-4) + word n-grams (1-2) give good
# coverage for short Hinglish phrases without any external embeddings.
tfidf_vectorizer = TfidfVectorizer(
    analyzer="word",
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=1,
)
X = tfidf_vectorizer.fit_transform(_train_texts)

intent_model = LogisticRegression(max_iter=500, C=5.0)
intent_model.fit(X, _train_labels)

# Pre-compute training vectors for cosine-similarity fallback
_train_vectors = X  # already a sparse matrix; cosine_similarity handles it


def tfidf_vector(text: str):
    """Transform a single text string into its TF-IDF sparse vector."""
    return tfidf_vectorizer.transform([text])


def similarity_fallback(user_input: str) -> str:
    """
    Fallback intent detection using cosine similarity in TF-IDF space.
    Used when classifier confidence is below the threshold.
    """
    vec  = tfidf_vector(user_input)
    sims = cosine_similarity(vec, _train_vectors)
    best_idx = int(sims.argmax())
    return TRAIN_DATA[best_idx][1]


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4: PREDICTION HELPER
# ═════════════════════════════════════════════════════════════════════════════

def _run_prediction(model, memory: dict):
    """
    Run risk prediction using model and stored memory.

    Args:
        model: XGBoost risk model
        memory (dict): User's financial context

    Returns:
        float | None: Default probability (0-1), or None if prediction fails
    """
    try:
        import joblib
        import os

        sample = pd.DataFrame({
            "RevolvingUtilizationOfUnsecuredLines": [memory.get("utilization", 0.3)],
            "age": [memory.get("age", 30)],
            "NumberOfTime30-59DaysPastDueNotWorse": [0],
            "DebtRatio": [memory.get("debt", 0.3)],
            "MonthlyIncome": [memory.get("income", 50000)],
            "NumberOfOpenCreditLinesAndLoans": [5],
            "NumberOfTimes90DaysLate": [0],
            "NumberRealEstateLoansOrLines": [1],
            "NumberOfTime60-89DaysPastDueNotWorse": [0],
            "NumberOfDependents": [1],
        })

        if os.path.exists("models/scaler.pkl"):
            sample = joblib.load("models/scaler.pkl").transform(sample)

        prob = model.predict_proba(sample)[:, 1][0]
        return prob
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5: RESPONSE HANDLERS - HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def _check_and_predict(model, user_input: str) -> str:
    """Handle follow-up answers and check if more info needed."""
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
    """Generate risk assessment response with progressive data collection."""
    if memory["income"] is None:
        memory["pending_question"] = "income"
        memory["last_intent"] = "risk"
        return "📊 Risk calculate karne ke liye pehle kuch details chahiye.\n\n💰 **Monthly income kitni hai?** (e.g. `50000`)"

    if memory["age"] is None:
        memory["pending_question"] = "age"
        memory["last_intent"] = "risk"
        return "📅 **Aapki age kitni hai?** (e.g. `35`)"

    if memory["debt"] is None:
        memory["pending_question"] = "debt"
        memory["last_intent"] = "risk"
        return "💸 **Debt ratio kitna hai?** (0 se 1 ke beech, e.g. `0.4`)\n_Matlab: monthly debt payments / monthly income_"

    if memory["utilization"] is None:
        memory["pending_question"] = "utilization"
        memory["last_intent"] = "risk"
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
    """Generate eligibility assessment response with product detection."""
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
        memory["last_intent"] = "eligibility"
        return f"{icon} **{product} Eligibility Check**\n\n💰 **Monthly income kitni hai?** (e.g. `50000`)"

    if memory["age"] is None:
        memory["pending_question"] = "age"
        memory["last_intent"] = "eligibility"
        return f"📅 **Aapki age kitni hai?** (e.g. `35`)"

    if memory["debt"] is None:
        memory["pending_question"] = "debt"
        memory["last_intent"] = "eligibility"
        return f"{icon} **Debt ratio kitna hai?** (0 se 1 ke beech, e.g. `0.4`)"

    if memory["utilization"] is None:
        memory["pending_question"] = "utilization"
        memory["last_intent"] = "eligibility"
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


# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6: MAIN CHATBOT FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def chatbot_response(user_input: str, model=None, user_data: dict = None) -> str:
    """
    Main chatbot response generator.

    Args:
        user_input (str): User's message
        model: Risk prediction model
        user_data (dict): Optional pre-filled user data from Home tab

    Returns:
        str: Formatted response message
    """
    global memory

    # Update memory with pre-filled data if available
    if user_data:
        memory["income"]       = user_data.get("MonthlyIncome", memory["income"])
        memory["age"]          = user_data.get("age", memory["age"])
        memory["debt"]         = user_data.get("DebtRatio", memory["debt"])
        memory["utilization"]  = user_data.get("RevolvingUtilizationOfUnsecuredLines", memory["utilization"])

    # Extract context from user input
    memory = extract_context(user_input, memory)

    # Normalize Hinglish
    normalized = normalize_hinglish(user_input)

    # Handle pending follow-up questions (bare number replies)
    if memory["pending_question"] and re.search(r'\d', user_input):
        return _check_and_predict(model, user_input)

    # ── Intent Detection ──────────────────────────────────────────────────────
    # 1. Try the TF-IDF + LogisticRegression classifier first
    vec    = tfidf_vector(normalized)
    probs  = intent_model.predict_proba(vec)[0]
    intent = intent_model.classes_[probs.argmax()]
    confidence = probs.max()

    # 2. If confidence is low, fall back to cosine similarity in TF-IDF space
    if confidence < 0.45:
        intent = similarity_fallback(normalized)

    memory["last_intent"] = intent

    # ════════════════════════════════════════════════════════════════════════
    # INTENT RESPONSES
    # ════════════════════════════════════════════════════════════════════════

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

    elif intent == "risk":
        return _handle_risk(model)

    elif intent == "eligibility":
        return _handle_eligibility(model, user_input)

    elif intent == "improvement":
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

    # Fallback response
    return (
        "❓ **Samajh nahi aaya.**\n\n"
        "Ye try karo:\n"
        "- `what is my risk`\n"
        "- `can i get loan`\n"
        "- `how to improve score`\n"
        "- `documents needed`\n"
        "- `hello`"
    )