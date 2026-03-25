

import streamlit as st
from db import get_connection
import pandas as pd
import threading
import queue
import json
import pickle

from services.risk_prediction import predict_risk_score
from services.fraud_detection import detect_fraud
from services.credit_card_eligibility import predict_credit_card_eligibility
from services.advisor_engine import generate_advice
from services.chatbot import chatbot_response
from database.db import get_connection
from generate_explanation import generate_explanation
from dashboards.whatif_simulator import show_whatif_simulator
from dashboards.pdf_report import generate_pdf_report
from dashboards.voice_output import show_voice_output
from dashboards.input_parser import parse_natural_language

# ── Load XGBoost model once at module level ──────────────────────────────────
try:
    _risk_model = pickle.load(open("models/model.pkl", "rb"))
except Exception:
    _risk_model = None


def _listen_until_stop(lang: str, result_queue: queue.Queue, stop_event: threading.Event):
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer

        model_path = "models/vosk-model-small-en-us-0.15" if lang == "en" else "models/vosk-model-small-hi-0.22"
        model      = Model(model_path)
        rec        = KaldiRecognizer(model, 16000)
        q          = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        full_text = ""
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
            while not stop_event.is_set():
                try:
                    data = q.get(timeout=0.5)
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        if res.get("text"):
                            full_text += " " + res["text"]
                except queue.Empty:
                    continue
            final = json.loads(rec.FinalResult())
            if final.get("text"):
                full_text += " " + final["text"]
        result_queue.put(("ok", full_text.strip()))
    except Exception as e:
        result_queue.put(("error", str(e)))


def show_customer_dashboard():

    st.title("💳 Credit Risk Analyzer")
    st.write(f"Welcome, **{st.session_state.user['full_name']}**!")

    defaults = {
        "last_input_data":  None,
        "last_prediction":  None,
        "messages":         [],
        "whatif_analyzed":  False,
        "voice_pending":    "",
        "mic_active":       False,
        "stop_event":       None,
        "result_queue":     None,
        "listen_thread":    None,
        "chat_messages":    [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    tab_home, tab_whatif, tab_report, tab_download, tab_history, tab_cc, tab_chat = st.tabs([
        "🏠 Home", "🤔 What-If Simulator", "📄 View Report", "⬇️ Download PDF", "📅 Loan History", "💳 Credit Card", "🤖 AI Chatbot",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — HOME
    # ══════════════════════════════════════════════════════════════════════════
    with tab_home:
        st.subheader("🔍 Credit Risk Analysis")

        with st.expander("💡 How to enter your details?", expanded=False):
            st.markdown("""
**You can type in any of these formats:**
- **Numbers:** `35 50000 0.4 0.3`
- **English:** `I am 35 years old, my income is 50000, debt ratio 0.4, credit utilization 0.3`
- **Hindi:** `meri umar 35 hai, kamai 50000, karj 0.4, credit 0.3`
- **Labeled:** `age: 35, salary: 50000, debt: 0.4, util: 0.3`

**Fields needed:** Age | Monthly Income (₹) | Debt Ratio (0-1) | Credit Utilization (0-1)
            """)

        st.markdown("#### 🎙️ Voice Input")
        vcol1, vcol2, vcol3 = st.columns([1, 1, 1])

        with vcol1:
            voice_lang = st.selectbox(
                "Language", ["English", "Hindi"],
                key="voice_input_lang", label_visibility="collapsed",
            )
            vlang_code = "en" if voice_lang == "English" else "hi"

        with vcol2:
            if not st.session_state.mic_active:
                if st.button("🎙️ Start Listening", use_container_width=True, type="primary"):
                    stop_event   = threading.Event()
                    result_queue = queue.Queue()
                    thread       = threading.Thread(
                        target=_listen_until_stop,
                        args=(vlang_code, result_queue, stop_event),
                        daemon=True,
                    )
                    st.session_state.stop_event    = stop_event
                    st.session_state.result_queue  = result_queue
                    st.session_state.listen_thread = thread
                    st.session_state.mic_active    = True
                    thread.start()
                    st.rerun()
            else:
                if st.button("⏹️ Stop Listening", use_container_width=True, type="secondary"):
                    if st.session_state.stop_event:
                        st.session_state.stop_event.set()
                    if st.session_state.listen_thread:
                        st.session_state.listen_thread.join(timeout=3)
                    if st.session_state.result_queue:
                        try:
                            status, text = st.session_state.result_queue.get_nowait()
                            st.session_state.voice_pending = text if status == "ok" and text else ""
                        except queue.Empty:
                            st.session_state.voice_pending = ""
                    st.session_state.mic_active = False
                    st.rerun()

        with vcol3:
            if st.session_state.mic_active:
                st.markdown("""<div style="padding:8px 14px; border-radius:8px;
                    background:#7f1d1d; border:1px solid #ef4444;
                    color:#fca5a5; font-size:0.9rem; text-align:center;">
                    🔴 Listening...</div>""", unsafe_allow_html=True)

        if st.session_state.voice_pending:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("✅ **Voice captured — edit if needed, then click Send:**")
            edited = st.text_input("Heard:", value=st.session_state.voice_pending,
                                   key="voice_edit_box", label_visibility="collapsed")
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("📨 Send to Chat", use_container_width=True, type="primary"):
                    st.session_state.messages.append({"role": "user", "content": edited})
                    st.session_state.voice_pending = ""
                    data = parse_natural_language(edited)
                    if data is None:
                        resp = "⚠️ Could not extract details. Please try:\n\n- `35 50000 0.4 0.3`"
                    else:
                        try:
                            risk_score, risk = predict_risk_score(data)
                            fraud             = detect_fraud(data)
                            advice            = generate_advice(risk)
                            explanation       = generate_explanation(risk)
                            save_prediction(data, risk, fraud)
                            st.session_state.last_input_data = data
                            st.session_state.last_prediction = {
                                "risk": risk, "risk_score": risk_score,
                                "fraud": fraud, "advice": advice, "explanation": explanation,
                            }
                            st.session_state.whatif_analyzed = False
                            advice_text = "\n".join([f"• {tip}" for tip in advice])
                            resp = f"""**✅ Details Parsed!**
Age: {int(data['age'])} | Income: ₹{data['MonthlyIncome']:,.0f} | Debt: {data['DebtRatio']:.2f} | Util: {data['RevolvingUtilizationOfUnsecuredLines']:.2f}

**Risk Category:** {risk} (Score: {risk_score:.1f}/20)

**AI Explanation:**
{explanation}

**Financial Advice:**
{advice_text}

📄 *Go to View Report tab to listen or download PDF*"""
                        except Exception as e:
                            resp = f"❌ Error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": resp})
                    st.rerun()
            with c2:
                if st.button("❌ Discard", use_container_width=True):
                    st.session_state.voice_pending = ""
                    st.rerun()

        st.divider()

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Type here — e.g. '35 50000 0.4 0.3' or natural language")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            data = parse_natural_language(user_input)
            if data is None:
                response = (
                    "⚠️ Could not extract your details. Please try:\n\n"
                    "- `35 50000 0.4 0.3`\n"
                    "- `I am 35 years old, income 50000, debt ratio 0.4, credit utilization 0.3`\n"
                    "- `meri umar 35, kamai 50000, karj 0.4, credit 0.3`"
                )
            else:
                try:
                    risk_score, risk = predict_risk_score(data)
                    fraud             = detect_fraud(data)
                    advice            = generate_advice(risk)
                    explanation       = generate_explanation(risk)
                    save_prediction(data, risk, fraud)
                    st.session_state.last_input_data = data
                    st.session_state.last_prediction = {
                        "risk": risk, "risk_score": risk_score,
                        "fraud": fraud, "advice": advice, "explanation": explanation,
                    }
                    st.session_state.whatif_analyzed = False
                    advice_text = "\n".join([f"• {tip}" for tip in advice])
                    response = f"""**✅ Details Parsed Successfully!**
Age: {int(data['age'])} | Income: ₹{data['MonthlyIncome']:,.0f} | Debt: {data['DebtRatio']:.2f} | Util: {data['RevolvingUtilizationOfUnsecuredLines']:.2f}

**Risk Category:** {risk} (Score: {risk_score:.1f}/20)

**AI Explanation:**
{explanation}

**Financial Advice:**
{advice_text}

📄 *Go to View Report tab to listen or download PDF*"""
                except Exception as e:
                    response = f"❌ Error: {str(e)}"

            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.session_state.last_prediction:
            pred = st.session_state.last_prediction
            risk_color = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}.get(pred["risk"], "#6b7280")
            st.markdown(f"""
            <div style="margin-top:20px; padding:16px 24px; border-radius:12px;
                background:#1e293b; border:2px solid {risk_color};
                display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <div style="color:#94a3b8; font-size:0.8rem;">Last Prediction</div>
                    <div style="color:{risk_color}; font-size:1.5rem; font-weight:700;">{pred['risk']}</div>
                    <div style="color:#94a3b8; font-size:0.85rem;">Score: {pred['risk_score']:.1f}/20</div>
                </div>
                <div style="color:#64748b; font-size:0.8rem;">
                    👆 Use tabs above to view report,<br>download PDF or run What-If analysis
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — WHAT-IF SIMULATOR
    # ══════════════════════════════════════════════════════════════════════════
    with tab_whatif:
        if st.session_state.last_input_data is None:
            st.warning("⚠️ Please run a prediction first from the **🏠 Home** tab!")
        else:
            show_whatif_simulator(baseline_input=st.session_state.last_input_data)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — VIEW REPORT
    # ══════════════════════════════════════════════════════════════════════════
    with tab_report:
        if st.session_state.last_prediction is None:
            st.warning("⚠️ Please run a prediction first from the **🏠 Home** tab!")
        else:
            pred = st.session_state.last_prediction
            data = st.session_state.last_input_data
            risk_color = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}.get(pred["risk"], "#6b7280")

            st.subheader("📄 Credit Risk Report")
            st.markdown(f"**Customer:** {st.session_state.user['full_name']}")
            st.divider()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:2px solid {risk_color}; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.8rem;">Risk Category</div>
                    <div style="color:{risk_color}; font-size:1.4rem; font-weight:700;">{pred['risk']}</div>
                    </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:1px solid #334155; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.8rem;">Risk Score</div>
                    <div style="color:#e2e8f0; font-size:1.4rem; font-weight:700;">{pred['risk_score']:.1f}/20</div>
                    </div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("#### 👤 Customer Details")
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"- **Age:** {int(data['age'])} years")
                st.markdown(f"- **Monthly Income:** ₹{data['MonthlyIncome']:,.0f}")
            with d2:
                st.markdown(f"- **Debt Ratio:** {data['DebtRatio']*100:.1f}%")
                st.markdown(f"- **Credit Utilization:** {data['RevolvingUtilizationOfUnsecuredLines']*100:.1f}%")

            st.divider()
            st.markdown("#### 🤖 AI Explanation")
            st.markdown(f"""<div style="padding:14px; border-radius:10px;
                background:#1e293b; border:1px solid #334155; color:#e2e8f0;">
                {pred['explanation']}</div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("#### 💡 Financial Advice")
            for i, tip in enumerate(pred["advice"]):
                st.markdown(f"**{i+1}.** {tip}")

            show_voice_output(
                customer_name=st.session_state.user.get("full_name", "Customer"),
                data=data, risk=pred["risk"], risk_score=pred["risk_score"],
                fraud=pred["fraud"], explanation=pred["explanation"], advice=pred["advice"],
            )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — DOWNLOAD PDF
    # ══════════════════════════════════════════════════════════════════════════
    with tab_download:
        if st.session_state.last_prediction is None:
            st.warning("⚠️ Please run a prediction first from the **🏠 Home** tab!")
        else:
            pred = st.session_state.last_prediction
            st.subheader("⬇️ Download PDF Report")
            st.divider()
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                try:
                    pdf_bytes = generate_pdf_report(
                        customer_name=st.session_state.user.get("full_name", "Customer"),
                        data=st.session_state.last_input_data,
                        risk=pred["risk"], risk_score=pred["risk_score"],
                        fraud=pred["fraud"], explanation=pred["explanation"], advice=pred["advice"],
                    )
                    st.download_button(
                        label="📄 Download PDF Report", data=pdf_bytes,
                        file_name=f"credit_report_{st.session_state.user.get('full_name','customer').replace(' ','_')}.pdf",
                        mime="application/pdf", use_container_width=True, type="primary",
                    )
                    st.success("✅ PDF ready!")
                except Exception as e:
                    st.error(f"❌ PDF error: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — LOAN HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    with tab_history:
        st.subheader("📅 Your Loan Application History")
        try:
            # conn = sqlite3.connect("credit_predictions.db")
            # df   = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", conn)
            # conn.close()
            
            conn = get_connection()
            df  = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", conn)
            conn.close()
            if len(df) == 0:
                st.info("📭 No applications found yet.")
            else:
                m1, m2, m3, m4 = st.columns(4)
                with m1: st.metric("Total",       len(df))
                with m2: st.metric("High Risk",   len(df[df['risk'] == 'High Risk']))
                with m3: st.metric("Medium Risk", len(df[df['risk'] == 'Medium Risk']))
                with m4: st.metric("Low Risk",    len(df[df['risk'] == 'Low Risk']))
                st.divider()
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Could not load history: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 6 — CREDIT CARD ELIGIBILITY
    # ══════════════════════════════════════════════════════════════════════════
    with tab_cc:
        st.subheader("💳 Check Your Credit Card Eligibility")
        st.caption("Fill in your details below — we'll check if you qualify for a credit card")

        if "cc_result" not in st.session_state:
            st.session_state.cc_result = None

        cc1, cc2 = st.columns(2)

        with cc1:
            st.markdown("**👤 About You**")
            cc_gender          = st.selectbox("Gender", ["Male", "Female"], key="cust_cc_gender")
            cc_age             = st.slider("Your Age", 18, 70, 30, key="cust_cc_age")
            cc_family_status   = st.selectbox("Marital Status", ["Married", "Single"], key="cust_cc_fam")
            cc_cnt_children    = st.number_input("Number of Children", 0, 5, 0, key="cust_cc_children")
            cc_cnt_fam_members = st.number_input("Total Family Members", 1, 8, 2, key="cust_cc_fam_mem")

        with cc2:
            st.markdown("**💰 Your Finances**")
            cc_income_type    = st.selectbox("Employment Type",
                                             ["Working", "Pensioner"],
                                             key="cust_cc_income_type")
            cc_amt_income     = st.number_input("Annual Income (₹)", 50000, 10000000, 300000,
                                                step=10000, key="cust_cc_income")
            cc_education_type = st.selectbox("Education Level",
                                             ["Secondary", "Higher"],
                                             key="cust_cc_edu")
            cc_housing_type   = st.selectbox("Where do you live?",
                                             ["House / apartment", "Apartment", "Other"],
                                             key="cust_cc_housing")
            cc_employment_yrs = st.slider("Years Employed", 0, 40, 3, key="cust_cc_emp")

        st.divider()
        cc3, cc4 = st.columns(2)
        with cc3:
            cc_owns_car    = st.radio("Do you own a car?",      ["Yes", "No"],
                                      horizontal=True, key="cust_cc_car")
        with cc4:
            cc_owns_realty = st.radio("Do you own a property?", ["Yes", "No"],
                                      horizontal=True, key="cust_cc_realty")

        st.divider()

        if st.button("🔍 Check My Eligibility", use_container_width=True,
                     type="primary", key="cust_cc_check"):

            cc_data = {
                "gender":          cc_gender,
                "age":             cc_age,
                "family_status":   cc_family_status,
                "cnt_children":    cc_cnt_children,
                "cnt_fam_members": cc_cnt_fam_members,
                "income_type":     cc_income_type,
                "amt_income":      cc_amt_income,
                "education_type":  cc_education_type,
                "housing_type":    cc_housing_type,
                "employment_yrs":  cc_employment_yrs,
                "owns_car":        cc_owns_car,
                "owns_realty":     cc_owns_realty,
            }

            eligible, prob, risk_label = predict_credit_card_eligibility(cc_data)
            st.session_state.cc_result = {
                "eligible": eligible, "prob": prob, "risk_label": risk_label
            }

        if st.session_state.cc_result:
            res            = st.session_state.cc_result
            eligible       = res["eligible"]
            prob           = res["prob"]
            risk_label     = res["risk_label"]
            eligible_color = "#22c55e" if eligible else "#ef4444"
            risk_c         = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b",
                              "High Risk": "#ef4444"}.get(risk_label, "#6b7280")

            st.markdown("---")
            st.markdown("### 📊 Your Result")

            if eligible:
                st.markdown(f"""<div style="padding:24px; border-radius:14px;
                    background:#1e293b; border:2px solid #22c55e; text-align:center; margin-bottom:16px;">
                    <div style="color:#22c55e; font-size:2rem; font-weight:800;">✅ Congratulations!</div>
                    <div style="color:#e2e8f0; font-size:1rem; margin-top:6px;">
                        You are eligible for a Credit Card
                    </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="padding:24px; border-radius:14px;
                    background:#1e293b; border:2px solid #ef4444; text-align:center; margin-bottom:16px;">
                    <div style="color:#ef4444; font-size:2rem; font-weight:800;">❌ Not Eligible</div>
                    <div style="color:#e2e8f0; font-size:1rem; margin-top:6px;">
                        You don't qualify for a credit card at this time
                    </div>
                    </div>""", unsafe_allow_html=True)

            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:1px solid #334155; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.78rem;">Default Risk Score</div>
                    <div style="color:{eligible_color}; font-size:1.4rem; font-weight:700;">{prob*100:.1f}%</div>
                    </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:2px solid {risk_c}; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.78rem;">Risk Category</div>
                    <div style="color:{risk_c}; font-size:1.4rem; font-weight:700;">{risk_label}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Your risk level:** {prob*100:.1f}% (lower is better ✅)")
            st.progress(float(prob))
            st.caption("🟡 Cut-off line at 43% — below this = eligible")
            st.divider()

            st.markdown("#### 💡 What This Means For You")
            if prob < 0.20:
                st.success("""✅ **Excellent profile!** You have very low financial risk.
You're likely eligible for a premium credit card with a higher limit.
→ Visit your nearest bank branch with income proof.""")
            elif prob < 0.43:
                st.info("""ℹ️ **Good profile.** You qualify, but at a moderate risk level.
You may be offered a standard credit card with a moderate limit.
→ Keeping your debt ratio low will improve your chances for a premium card.""")
            elif prob < 0.65:
                st.warning("""⚠️ **Borderline.** Your application may need extra review.
→ Tips to improve:
- Increase your income or reduce existing debt
- Show stable employment history
- Apply again after 6 months of financial stability""")
            else:
                st.error("""❌ **High risk profile.** A credit card is not recommended right now.
→ Steps to improve your eligibility:
- Reduce your debt ratio below 0.4
- Maintain stable employment for 2+ years
- Build a savings record and try again in 1 year""")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 7 — AI CHATBOT
    # ══════════════════════════════════════════════════════════════════════════
    with tab_chat:
        st.subheader("🤖 AI Credit Chatbot")
        st.caption("Loan, risk, documents — kuch bhi poochein!")

        # Display chat history
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Clear button
        if st.session_state.chat_messages:
            if st.button("🗑️ Clear Chat", key="clear_chatbot"):
                st.session_state.chat_messages = []
                st.rerun()

        # Chat input
        chat_input = st.chat_input("Poochein kuch bhi... e.g. 'what is my risk?'")

        if chat_input:
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": chat_input})

            # Get response from chatbot — pass model + last_input_data
            response = chatbot_response(
                user_input=chat_input,
                model=_risk_model,
                user_data=st.session_state.get("last_input_data"),
            )

            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()