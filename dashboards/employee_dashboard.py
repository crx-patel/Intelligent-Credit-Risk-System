# import streamlit as st
# import sqlite3
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go

# from services.risk_prediction import predict_risk_score
# from services.fraud_detection import detect_fraud_detailed


# def show_employee_dashboard():

#     st.title("🏦 Bank Employee Dashboard")
#     st.write(f"Welcome, **{st.session_state.user['full_name']}**!")

#     # Load data
#     conn = sqlite3.connect("credit_predictions.db")
#     df   = pd.read_sql_query("SELECT * FROM predictions", conn)
#     conn.close()

#     # ── Metrics ────────────────────────────────────────────────────────────────
#     col1, col2, col3, col4 = st.columns(4)
#     with col1: st.metric("Total Applications", len(df))
#     with col2: st.metric("High Risk",   len(df[df['risk'] == 'High Risk']))
#     with col3: st.metric("Medium Risk", len(df[df['risk'] == 'Medium Risk']))
#     with col4: st.metric("Low Risk",    len(df[df['risk'] == 'Low Risk']))

#     st.divider()

#     # ── Tabs ───────────────────────────────────────────────────────────────────
#     tab_dashboard, tab_fraud, tab_analyze, tab_applications = st.tabs([
#         "📊 Dashboard", "🚨 Fraud Detection", "🔍 Analyze Customer", "📋 All Applications"
#     ])

#     # ══════════════════════════════════════════════════════════════════════════
#     # TAB 1 — DASHBOARD
#     # ══════════════════════════════════════════════════════════════════════════
#     with tab_dashboard:
#         st.subheader("📊 Risk Distribution")

#         if len(df) > 0:
#             col1, col2 = st.columns(2)

#             with col1:
#                 # Pie chart
#                 risk_counts = df['risk'].value_counts().reset_index()
#                 risk_counts.columns = ['Risk', 'Count']
#                 fig_pie = px.pie(
#                     risk_counts, values='Count', names='Risk',
#                     color='Risk',
#                     color_discrete_map={
#                         'Low Risk':    '#22c55e',
#                         'Medium Risk': '#f59e0b',
#                         'High Risk':   '#ef4444',
#                     },
#                     title="Risk Category Distribution",
#                 )
#                 fig_pie.update_layout(
#                     paper_bgcolor="rgba(0,0,0,0)",
#                     plot_bgcolor="rgba(0,0,0,0)",
#                     font={"color": "#e2e8f0"},
#                 )
#                 st.plotly_chart(fig_pie, use_container_width=True)

#             with col2:
#                 # Bar chart
#                 fig_bar = px.bar(
#                     risk_counts, x='Risk', y='Count',
#                     color='Risk',
#                     color_discrete_map={
#                         'Low Risk':    '#22c55e',
#                         'Medium Risk': '#f59e0b',
#                         'High Risk':   '#ef4444',
#                     },
#                     title="Applications by Risk Category",
#                 )
#                 fig_bar.update_layout(
#                     paper_bgcolor="rgba(0,0,0,0)",
#                     plot_bgcolor="rgba(0,0,0,0)",
#                     font={"color": "#e2e8f0"},
#                     showlegend=False,
#                 )
#                 st.plotly_chart(fig_bar, use_container_width=True)

#             # Fraud distribution
#             if 'fraud' in df.columns:
#                 st.divider()
#                 st.subheader("🚨 Fraud Overview")
#                 fraud_counts = df['fraud'].value_counts().reset_index()
#                 fraud_counts.columns = ['Fraud Status', 'Count']
#                 fig_fraud = px.bar(
#                     fraud_counts, x='Fraud Status', y='Count',
#                     color='Fraud Status',
#                     color_discrete_map={
#                         'No Fraud Detected':  '#22c55e',
#                         'Suspicious Applicant': '#f59e0b',
#                         'Possible Fraud':     '#ef4444',
#                     },
#                     title="Fraud Detection Overview",
#                 )
#                 fig_fraud.update_layout(
#                     paper_bgcolor="rgba(0,0,0,0)",
#                     plot_bgcolor="rgba(0,0,0,0)",
#                     font={"color": "#e2e8f0"},
#                     showlegend=False,
#                 )
#                 st.plotly_chart(fig_fraud, use_container_width=True)
#         else:
#             st.info("📭 No data yet!")

#     # ══════════════════════════════════════════════════════════════════════════
#     # TAB 2 — FRAUD DETECTION
#     # ══════════════════════════════════════════════════════════════════════════
#     with tab_fraud:
#         st.subheader("🚨 Fraud Detection Panel")

#         if len(df) > 0 and 'fraud' in df.columns:
#             # High risk fraud cases
#             fraud_cases = df[df['fraud'].isin(['Possible Fraud', 'Suspicious Applicant'])]

#             f1, f2, f3 = st.columns(3)
#             with f1:
#                 possible = len(df[df['fraud'] == 'Possible Fraud'])
#                 st.markdown(f"""<div style="padding:16px; border-radius:10px;
#                     background:#1e293b; border:2px solid #ef4444; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.8rem;">🚨 Possible Fraud</div>
#                     <div style="color:#ef4444; font-size:2rem; font-weight:700;">{possible}</div>
#                     </div>""", unsafe_allow_html=True)
#             with f2:
#                 suspicious = len(df[df['fraud'] == 'Suspicious Applicant'])
#                 st.markdown(f"""<div style="padding:16px; border-radius:10px;
#                     background:#1e293b; border:2px solid #f59e0b; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.8rem;">⚠️ Suspicious</div>
#                     <div style="color:#f59e0b; font-size:2rem; font-weight:700;">{suspicious}</div>
#                     </div>""", unsafe_allow_html=True)
#             with f3:
#                 clean = len(df[df['fraud'] == 'No Fraud Detected'])
#                 st.markdown(f"""<div style="padding:16px; border-radius:10px;
#                     background:#1e293b; border:2px solid #22c55e; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.8rem;">✅ Clean</div>
#                     <div style="color:#22c55e; font-size:2rem; font-weight:700;">{clean}</div>
#                     </div>""", unsafe_allow_html=True)

#             st.divider()

#             if len(fraud_cases) > 0:
#                 st.markdown("#### 🔴 Flagged Applications")
#                 st.dataframe(fraud_cases, use_container_width=True)
#             else:
#                 st.success("✅ No fraud cases detected!")
#         else:
#             st.info("📭 No data yet!")

#     # ══════════════════════════════════════════════════════════════════════════
#     # TAB 3 — ANALYZE CUSTOMER
#     # ══════════════════════════════════════════════════════════════════════════
#     with tab_analyze:
#         st.subheader("🔍 Analyze Customer — Full AI Report")
#         st.caption("Enter customer details to get Risk Score, Confidence Score, and Fraud Analysis")

#         a1, a2 = st.columns(2)
#         with a1:
#             age    = st.number_input("Age",            min_value=18, max_value=100, value=35)
#             income = st.number_input("Monthly Income (₹)", min_value=0, value=30000, step=1000)
#             debt   = st.slider("Debt Ratio",           0.0, 1.0, 0.4, 0.01)
#         with a2:
#             util      = st.slider("Credit Utilization", 0.0, 1.0, 0.3, 0.01)
#             late_30   = st.number_input("Late 30-59 Days", min_value=0, value=0)
#             late_90   = st.number_input("Late 90+ Days",   min_value=0, value=0)

#         if st.button("🔍 Run Full Analysis", use_container_width=True, type="primary"):
#             data = {
#                 "age": age, "MonthlyIncome": income,
#                 "DebtRatio": debt,
#                 "RevolvingUtilizationOfUnsecuredLines": util,
#                 "late_30": late_30, "late_90": late_90,
#             }

#             risk_score, risk   = predict_risk_score(data)
#             fraud_detail       = detect_fraud_detailed(data)

#             # Confidence Score — how confident model is
#             if risk == "High Risk":
#                 confidence = min(100, 60 + risk_score * 2)
#             elif risk == "Medium Risk":
#                 confidence = min(100, 50 + risk_score * 1.5)
#             else:
#                 confidence = min(100, 80 + (8 - risk_score) * 2)
#             confidence = round(confidence, 1)

#             risk_color  = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}.get(risk, "#6b7280")
#             fraud_color = {"No Fraud Detected": "#22c55e", "Suspicious Applicant": "#f59e0b", "Possible Fraud": "#ef4444"}.get(fraud_detail["status"], "#6b7280")

#             st.divider()
#             st.markdown("#### 📊 Analysis Results")

#             r1, r2, r3, r4 = st.columns(4)
#             with r1:
#                 st.markdown(f"""<div style="padding:14px; border-radius:10px;
#                     background:#1e293b; border:2px solid {risk_color}; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.75rem;">Risk Category</div>
#                     <div style="color:{risk_color}; font-size:1.1rem; font-weight:700;">{risk}</div>
#                     </div>""", unsafe_allow_html=True)
#             with r2:
#                 st.markdown(f"""<div style="padding:14px; border-radius:10px;
#                     background:#1e293b; border:1px solid #334155; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.75rem;">Risk Score</div>
#                     <div style="color:#e2e8f0; font-size:1.1rem; font-weight:700;">{risk_score:.1f}/20</div>
#                     </div>""", unsafe_allow_html=True)
#             with r3:
#                 st.markdown(f"""<div style="padding:14px; border-radius:10px;
#                     background:#1e293b; border:1px solid #334155; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.75rem;">Model Confidence</div>
#                     <div style="color:#818cf8; font-size:1.1rem; font-weight:700;">{confidence}%</div>
#                     </div>""", unsafe_allow_html=True)
#             with r4:
#                 st.markdown(f"""<div style="padding:14px; border-radius:10px;
#                     background:#1e293b; border:2px solid {fraud_color}; text-align:center;">
#                     <div style="color:#94a3b8; font-size:0.75rem;">Fraud Status</div>
#                     <div style="color:{fraud_color}; font-size:0.9rem; font-weight:700;">{fraud_detail['status']}</div>
#                     </div>""", unsafe_allow_html=True)

#             # Fraud score bar
#             st.divider()
#             st.markdown("#### 🚨 Fraud Risk Meter")
#             fraud_score = fraud_detail.get("score", 0)
#             fig_gauge = go.Figure(go.Indicator(
#                 mode="gauge+number",
#                 value=fraud_score,
#                 title={"text": "Fraud Risk Score", "font": {"color": "#e2e8f0"}},
#                 gauge={
#                     "axis": {"range": [0, 100], "tickfont": {"color": "#94a3b8"}},
#                     "bar":  {"color": fraud_color},
#                     "steps": [
#                         {"range": [0, 30],   "color": "#14532d"},
#                         {"range": [30, 60],  "color": "#78350f"},
#                         {"range": [60, 100], "color": "#7f1d1d"},
#                     ],
#                 },
#                 number={"font": {"color": fraud_color}, "suffix": "/100"},
#             ))
#             fig_gauge.update_layout(
#                 paper_bgcolor="rgba(0,0,0,0)", height=250,
#                 font={"color": "#e2e8f0"},
#             )
#             st.plotly_chart(fig_gauge, use_container_width=True)

#     # ══════════════════════════════════════════════════════════════════════════
#     # TAB 4 — ALL APPLICATIONS
#     # ══════════════════════════════════════════════════════════════════════════
#     with tab_applications:
#         st.subheader("📋 All Applications")
#         if len(df) > 0:
#             # Filter
#             risk_filter = st.multiselect(
#                 "Filter by Risk:",
#                 ["High Risk", "Medium Risk", "Low Risk"],
#                 default=["High Risk", "Medium Risk", "Low Risk"],
#             )
#             filtered = df[df['risk'].isin(risk_filter)]
#             st.dataframe(filtered, use_container_width=True)
#             st.caption(f"Showing {len(filtered)} of {len(df)} applications")
#         else:
#             st.info("📭 No data yet!")






import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.risk_prediction import predict_risk_score
from services.fraud_detection import detect_fraud_detailed


def show_employee_dashboard():

    st.title("🏦 Bank Employee Dashboard")
    st.write(f"Welcome, **{st.session_state.user['full_name']}**!")

    # Load data
    conn = sqlite3.connect("credit_predictions.db")
    df   = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close()

    # ── Metrics ────────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Applications", len(df))
    with col2: st.metric("High Risk",   len(df[df['risk'] == 'High Risk']))
    with col3: st.metric("Medium Risk", len(df[df['risk'] == 'Medium Risk']))
    with col4: st.metric("Low Risk",    len(df[df['risk'] == 'Low Risk']))

    st.divider()

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_dashboard, tab_fraud, tab_analyze, tab_applications = st.tabs([
        "📊 Dashboard", "🚨 Fraud Detection", "🔍 Analyze Customer", "📋 All Applications"
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    with tab_dashboard:
        st.subheader("📊 Risk Distribution")

        if len(df) > 0:
            col1, col2 = st.columns(2)

            with col1:
                # Pie chart
                risk_counts = df['risk'].value_counts().reset_index()
                risk_counts.columns = ['Risk', 'Count']
                fig_pie = px.pie(
                    risk_counts, values='Count', names='Risk',
                    color='Risk',
                    color_discrete_map={
                        'Low Risk':    '#22c55e',
                        'Medium Risk': '#f59e0b',
                        'High Risk':   '#ef4444',
                    },
                    title="Risk Category Distribution",
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#e2e8f0"},
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Bar chart
                fig_bar = px.bar(
                    risk_counts, x='Risk', y='Count',
                    color='Risk',
                    color_discrete_map={
                        'Low Risk':    '#22c55e',
                        'Medium Risk': '#f59e0b',
                        'High Risk':   '#ef4444',
                    },
                    title="Applications by Risk Category",
                )
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#e2e8f0"},
                    showlegend=False,
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Fraud distribution
            if 'fraud' in df.columns:
                st.divider()
                st.subheader("🚨 Fraud Overview")
                fraud_counts = df['fraud'].value_counts().reset_index()
                fraud_counts.columns = ['Fraud Status', 'Count']
                fig_fraud = px.bar(
                    fraud_counts, x='Fraud Status', y='Count',
                    color='Fraud Status',
                    color_discrete_map={
                        'No Fraud Detected':  '#22c55e',
                        'Suspicious Applicant': '#f59e0b',
                        'Possible Fraud':     '#ef4444',
                    },
                    title="Fraud Detection Overview",
                )
                fig_fraud.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": "#e2e8f0"},
                    showlegend=False,
                )
                st.plotly_chart(fig_fraud, use_container_width=True)
        else:
            st.info("📭 No data yet!")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — FRAUD DETECTION
    # ══════════════════════════════════════════════════════════════════════════
    with tab_fraud:
        st.subheader("🚨 Fraud Detection Panel")

        if len(df) > 0 and 'fraud' in df.columns:
            # High risk fraud cases
            fraud_cases = df[df['fraud'].isin(['Possible Fraud', 'Suspicious Applicant'])]

            f1, f2, f3 = st.columns(3)
            with f1:
                possible = len(df[df['fraud'] == 'Possible Fraud'])
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:2px solid #ef4444; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.8rem;">🚨 Possible Fraud</div>
                    <div style="color:#ef4444; font-size:2rem; font-weight:700;">{possible}</div>
                    </div>""", unsafe_allow_html=True)
            with f2:
                suspicious = len(df[df['fraud'] == 'Suspicious Applicant'])
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:2px solid #f59e0b; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.8rem;">⚠️ Suspicious</div>
                    <div style="color:#f59e0b; font-size:2rem; font-weight:700;">{suspicious}</div>
                    </div>""", unsafe_allow_html=True)
            with f3:
                clean = len(df[df['fraud'] == 'No Fraud Detected'])
                st.markdown(f"""<div style="padding:16px; border-radius:10px;
                    background:#1e293b; border:2px solid #22c55e; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.8rem;">✅ Clean</div>
                    <div style="color:#22c55e; font-size:2rem; font-weight:700;">{clean}</div>
                    </div>""", unsafe_allow_html=True)

            st.divider()

            if len(fraud_cases) > 0:
                st.markdown("#### 🔴 Flagged Applications")
                st.dataframe(fraud_cases, use_container_width=True)
            else:
                st.success("✅ No fraud cases detected!")
        else:
            st.info("📭 No data yet!")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — ANALYZE CUSTOMER
    # ══════════════════════════════════════════════════════════════════════════
    with tab_analyze:
        st.subheader("🔍 Analyze Customer — Full AI Report")
        st.caption("Enter customer details to get Risk Score, Confidence Score, and Fraud Analysis")

        a1, a2 = st.columns(2)
        with a1:
            age    = st.number_input("Age",            min_value=18, max_value=100, value=35)
            income = st.number_input("Monthly Income (₹)", min_value=0, value=30000, step=1000)
            debt   = st.slider("Debt Ratio",           0.0, 1.0, 0.4, 0.01)
        with a2:
            util      = st.slider("Credit Utilization", 0.0, 1.0, 0.3, 0.01)
            late_30   = st.number_input("Late 30-59 Days", min_value=0, value=0)
            late_90   = st.number_input("Late 90+ Days",   min_value=0, value=0)

        if st.button("🔍 Run Full Analysis", use_container_width=True, type="primary"):
            data = {
                "age": age, "MonthlyIncome": income,
                "DebtRatio": debt,
                "RevolvingUtilizationOfUnsecuredLines": util,
                "late_30": late_30, "late_90": late_90,
            }

            risk_score, risk   = predict_risk_score(data)
            fraud_detail       = detect_fraud_detailed(data)

            # Confidence Score — how confident model is
            if risk == "High Risk":
                confidence = min(100, 60 + risk_score * 2)
            elif risk == "Medium Risk":
                confidence = min(100, 50 + risk_score * 1.5)
            else:
                confidence = min(100, 80 + (8 - risk_score) * 2)
            confidence = round(confidence, 1)

            risk_color  = {"Low Risk": "#22c55e", "Medium Risk": "#f59e0b", "High Risk": "#ef4444"}.get(risk, "#6b7280")
            fraud_color = {"No Fraud Detected": "#22c55e", "Suspicious Applicant": "#f59e0b", "Possible Fraud": "#ef4444"}.get(fraud_detail["status"], "#6b7280")

            st.divider()
            st.markdown("#### 📊 Analysis Results")

            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.markdown(f"""<div style="padding:14px; border-radius:10px;
                    background:#1e293b; border:2px solid {risk_color}; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.75rem;">Risk Category</div>
                    <div style="color:{risk_color}; font-size:1.1rem; font-weight:700;">{risk}</div>
                    </div>""", unsafe_allow_html=True)
            with r2:
                st.markdown(f"""<div style="padding:14px; border-radius:10px;
                    background:#1e293b; border:1px solid #334155; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.75rem;">Risk Score</div>
                    <div style="color:#e2e8f0; font-size:1.1rem; font-weight:700;">{risk_score:.1f}/20</div>
                    </div>""", unsafe_allow_html=True)
            with r3:
                st.markdown(f"""<div style="padding:14px; border-radius:10px;
                    background:#1e293b; border:1px solid #334155; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.75rem;">Model Confidence</div>
                    <div style="color:#818cf8; font-size:1.1rem; font-weight:700;">{confidence}%</div>
                    </div>""", unsafe_allow_html=True)
            with r4:
                st.markdown(f"""<div style="padding:14px; border-radius:10px;
                    background:#1e293b; border:2px solid {fraud_color}; text-align:center;">
                    <div style="color:#94a3b8; font-size:0.75rem;">Fraud Status</div>
                    <div style="color:{fraud_color}; font-size:0.9rem; font-weight:700;">{fraud_detail['status']}</div>
                    </div>""", unsafe_allow_html=True)

            # Fraud score bar
            st.divider()
            st.markdown("#### 🚨 Fraud Risk Meter")
            fraud_score = fraud_detail.get("score", 0)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=fraud_score,
                title={"text": "Fraud Risk Score", "font": {"color": "#e2e8f0"}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"color": "#94a3b8"}},
                    "bar":  {"color": fraud_color},
                    "steps": [
                        {"range": [0, 30],   "color": "#14532d"},
                        {"range": [30, 60],  "color": "#78350f"},
                        {"range": [60, 100], "color": "#7f1d1d"},
                    ],
                },
                number={"font": {"color": fraud_color}, "suffix": "/100"},
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=250,
                font={"color": "#e2e8f0"},
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — ALL APPLICATIONS
    # ══════════════════════════════════════════════════════════════════════════
    with tab_applications:
        st.subheader("📋 All Applications")
        if len(df) > 0:
            # Filter
            risk_filter = st.multiselect(
                "Filter by Risk:",
                ["High Risk", "Medium Risk", "Low Risk"],
                default=["High Risk", "Medium Risk", "Low Risk"],
            )
            filtered = df[df['risk'].isin(risk_filter)]
            st.dataframe(filtered, use_container_width=True)
            st.caption(f"Showing {len(filtered)} of {len(df)} applications")
        else:
            st.info("📭 No data yet!")