# import os
# import tempfile
# import streamlit as st
# from gtts import gTTS

# try:
#     from deep_translator import GoogleTranslator
#     TRANSLATOR_AVAILABLE = True
# except ImportError:
#     TRANSLATOR_AVAILABLE = False

# HINDI_RISK_TEMPLATES = {
#     "Low Risk": "Aapki financial sthiti bahut achhi hai. Aapka credit jokhim kam hai. Aap loan ke liye ek achhe umeedwar hain.",
#     "Medium Risk": "Aapki financial sthiti theek hai lekin sudhar ki zarurat hai. Aapka credit jokhim madhyam hai.",
#     "High Risk": "Aapki financial sthiti mein kafi sudhar ki zarurat hai. Aapka credit jokhim zyada hai. Kripya apna karj kam karein.",
# }

# HINDI_ADVICE_TEMPLATES = {
#     "Low Risk":    ["Apni bachat ko badhate rahein.", "Credit card ka bill samay par chukayein.", "Emergency fund banaye rakhein."],
#     "Medium Risk": ["Apna karj dhire dhire kam karein.", "Credit card ka upyog simit karein.", "Apni monthly income badhane ki koshish karein."],
#     "High Risk":   ["Turant apna karj kam karein.", "Kisi financial advisor se salah lein.", "Naya loan lene se bachein."],
# }


# def translate_to_hindi(text: str) -> str:
#     if not TRANSLATOR_AVAILABLE or not text.strip():
#         return text
#     try:
#         chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
#         translated = []
#         for chunk in chunks:
#             result = GoogleTranslator(source="en", target="hi").translate(chunk)
#             translated.append(result or chunk)
#         return " ".join(translated)
#     except Exception:
#         return text


# def build_report_text(customer_name, data, risk, risk_score, fraud, explanation, advice, lang="en"):

#     if lang == "hi":
#         try:
#             explanation_hi = translate_to_hindi(explanation)
#         except Exception:
#             explanation_hi = HINDI_RISK_TEMPLATES.get(risk, explanation)

#         try:
#             advice_hi_list = [translate_to_hindi(tip) for tip in advice]
#             advice_hi = ". ".join(advice_hi_list)
#         except Exception:
#             advice_hi = ". ".join(HINDI_ADVICE_TEMPLATES.get(risk, ["Apna khayal rakhein."]))

#         risk_hi = {"Low Risk": "kam jokhim", "Medium Risk": "madhyam jokhim", "High Risk": "adhik jokhim"}.get(risk, risk)

#         return f"""Namaskar, {customer_name} ji.
# Yeh aapki Credit Risk Report hai.
# Aapka Risk Score {risk_score:.1f} bees mein se hai.
# Aapki Risk Category hai: {risk_hi}.
# Artificial Intelligence Vivaran: {explanation_hi}
# Aapke liye Vittiya Salah: {advice_hi}.
# Dhanyavaad. Apna khayal rakhein aur apni vittiya sthiti ko behtar banate rahein."""

#     else:
#         advice_text = ". ".join(advice) if advice else "No advice available."

#         return f"""Hello {customer_name}.
# This is your Credit Risk Assessment Report.
# Your risk score is {risk_score:.1f} out of 20.
# Your risk category is {risk}.
# AI Explanation: {explanation}
# Here is your personalized financial advice: {advice_text}.
# Thank you. Please take care of your finances."""


# def text_to_speech(text: str, lang: str = "en") -> bytes:
#     tts = gTTS(text=text, lang=lang, slow=False)
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#         tmp_path = tmp.name
#         tts.save(tmp_path)
#     with open(tmp_path, "rb") as f:
#         audio_bytes = f.read()
#     os.unlink(tmp_path)
#     return audio_bytes


# def show_voice_output(customer_name, data, risk, risk_score, fraud, explanation, advice):

#     st.divider()
#     st.markdown("#### 🔊 Listen to Your Report")
#     st.caption("Select language and click Play to hear your credit risk report.")

#     col1, col2 = st.columns([1, 2])

#     with col1:
#         lang      = st.selectbox("🌐 Language", options=["English", "Hindi"], key="voice_lang")
#         lang_code = "en" if lang == "English" else "hi"

#     with col2:
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("🔊 Play Report", use_container_width=True, type="primary"):
#             with st.spinner("Generating audio... please wait"):
#                 try:
#                     report_text = build_report_text(customer_name, data, risk, risk_score, fraud, explanation, advice, lang_code)
#                     audio_bytes = text_to_speech(report_text, lang=lang_code)
#                     st.audio(audio_bytes, format="audio/mp3", autoplay=True)
#                     st.success("✅ Audio ready!")
#                 except Exception as e:
#                     st.error(f"❌ Voice error: {e}")

#         if st.button("⬇️ Download Audio", use_container_width=True):
#             with st.spinner("Preparing audio file..."):
#                 try:
#                     report_text = build_report_text(customer_name, data, risk, risk_score, fraud, explanation, advice, lang_code)
#                     audio_bytes = text_to_speech(report_text, lang=lang_code)
#                     st.download_button(
#                         label="📥 Save Audio File",
#                         data=audio_bytes,
#                         file_name=f"credit_report_{customer_name.replace(' ', '_')}_{lang}.mp3",
#                         mime="audio/mp3",
#                         use_container_width=True,
#                     )
#                 except Exception as e:
#                     st.error(f"❌ Audio error: {e}")



import os
import tempfile
import streamlit as st
from gtts import gTTS

# Optional translator
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False


# ------------------ Hindi Templates ------------------
HINDI_RISK_TEMPLATES = {
    "Low Risk": "Aapki financial sthiti bahut achhi hai. Aapka credit jokhim kam hai.",
    "Medium Risk": "Aapki financial sthiti theek hai lekin sudhar ki zarurat hai.",
    "High Risk": "Aapki financial sthiti mein sudhar ki zarurat hai. Aapka jokhim zyada hai.",
}

HINDI_ADVICE_TEMPLATES = {
    "Low Risk": ["Apni bachat badhate rahein.", "Bill samay par chukayein."],
    "Medium Risk": ["Karj kam karein.", "Kharch control karein."],
    "High Risk": ["Turant karj kam karein.", "Financial advisor se baat karein."],
}


# ------------------ Translation ------------------
def translate_to_hindi(text: str) -> str:
    if not TRANSLATOR_AVAILABLE or not text.strip():
        return text

    try:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        translated = []

        for chunk in chunks:
            result = GoogleTranslator(source="en", target="hi").translate(chunk)
            translated.append(result if result else chunk)

        return " ".join(translated)

    except Exception:
        return text


# ------------------ Report Builder ------------------
def build_report_text(customer_name, data, risk, risk_score, fraud, explanation, advice, lang="en"):

    if lang == "hi":
        explanation_hi = translate_to_hindi(explanation)
        advice_hi = ". ".join([translate_to_hindi(a) for a in advice]) if advice else ""

        risk_map = {
            "Low Risk": "kam jokhim",
            "Medium Risk": "madhyam jokhim",
            "High Risk": "adhik jokhim"
        }

        return f"""
Namaskar {customer_name} ji.
Yeh aapki credit risk report hai.
Aapka score {risk_score:.1f} hai.
Aapki category hai: {risk_map.get(risk, risk)}.
Vishleshan: {explanation_hi}.
Salah: {advice_hi}.
Dhanyavaad.
"""

    else:
        advice_text = ". ".join(advice) if advice else "No advice available."

        return f"""
Hello {customer_name}.
This is your Credit Risk Report.
Your score is {risk_score:.1f}.
Category: {risk}.
Explanation: {explanation}.
Advice: {advice_text}.
Thank you.
"""


# ------------------ Text to Speech ------------------
def text_to_speech(text: str, lang: str = "en") -> bytes:
    try:
        tts = gTTS(text=text, lang=lang, slow=False)

        with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
            tts.save(tmp.name)
            tmp.seek(0)
            return tmp.read()

    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None


# ------------------ UI Function ------------------
def show_voice_output(customer_name, data, risk, risk_score, fraud, explanation, advice):

    st.divider()
    st.markdown("#### 🔊 Listen to Your Report")

    col1, col2 = st.columns([1, 2])

    with col1:
        lang = st.selectbox("🌐 Language", ["English", "Hindi"])
        lang_code = "en" if lang == "English" else "hi"

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)

        # -------- PLAY AUDIO --------
        if st.button("🔊 Play Report", use_container_width=True):
            with st.spinner("Generating audio..."):
                report_text = build_report_text(
                    customer_name, data, risk, risk_score, fraud,
                    explanation, advice, lang_code
                )

                audio_bytes = text_to_speech(report_text, lang_code)

                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.success("Audio ready!")

        # -------- DOWNLOAD AUDIO --------
        if st.button("⬇️ Download Audio", use_container_width=True):
            report_text = build_report_text(
                customer_name, data, risk, risk_score, fraud,
                explanation, advice, lang_code
            )

            audio_bytes = text_to_speech(report_text, lang_code)

            if audio_bytes:
                st.download_button(
                    "📥 Download MP3",
                    data=audio_bytes,
                    file_name=f"{customer_name}_report.mp3",
                    mime="audio/mp3"
                )