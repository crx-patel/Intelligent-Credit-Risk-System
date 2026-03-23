import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from services.risk_prediction import predict_risk_score


def get_risk_color(risk_label: str) -> str:
    colors = {
        "Low Risk":    "#22c55e",
        "Medium Risk": "#f59e0b",
        "High Risk":   "#ef4444",
    }
    return colors.get(risk_label, "#6b7280")


def render_gauge(score: float, risk_label: str) -> go.Figure:
    color = get_risk_color(risk_label)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Risk Score", "font": {"size": 18, "color": "#e2e8f0"}},
        gauge={
            "axis": {
                "range": [0, 20],
                "tickwidth": 1,
                "tickcolor": "#94a3b8",
                "tickfont": {"color": "#94a3b8"},
                "tickvals": [0, 4, 8, 11, 14, 17, 20],
            },
            "bar": {"color": color, "thickness": 0.35},
            "bgcolor": "#1e293b",
            "borderwidth": 2,
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, 8],   "color": "#14532d"},
                {"range": [8, 14],  "color": "#78350f"},
                {"range": [14, 20], "color": "#7f1d1d"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
        number={"font": {"size": 36, "color": color}, "suffix": "/20"},
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=20, r=20, t=40, b=10),
        font={"color": "#e2e8f0"},
    )
    return fig


def render_comparison_bar(baseline_data: dict, current_data: dict,
                           baseline_risk: str, current_risk: str) -> go.Figure:
    features = ["Age", "Monthly Income", "Debt Ratio", "Credit Utilization"]
    baseline_vals = [
        baseline_data["age"],
        baseline_data["MonthlyIncome"] / 1000,
        baseline_data["DebtRatio"] * 100,
        baseline_data["RevolvingUtilizationOfUnsecuredLines"] * 100,
    ]
    current_vals = [
        current_data["age"],
        current_data["MonthlyIncome"] / 1000,
        current_data["DebtRatio"] * 100,
        current_data["RevolvingUtilizationOfUnsecuredLines"] * 100,
    ]
    units = ["yrs", "K₹", "%", "%"]
    labels = [f"{f}<br><sub>({u})</sub>" for f, u in zip(features, units)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=f"Your Input ({baseline_risk})",
        x=labels, y=baseline_vals,
        marker_color="#3b82f6", opacity=0.85,
        text=[f"{v:.1f}" for v in baseline_vals],
        textposition="outside", textfont={"color": "#93c5fd"},
    ))
    fig.add_trace(go.Bar(
        name=f"What-If ({current_risk})",
        x=labels, y=current_vals,
        marker_color=get_risk_color(current_risk), opacity=0.85,
        text=[f"{v:.1f}" for v in current_vals],
        textposition="outside", textfont={"color": "#fde68a"},
    ))

    fig.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=320, margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1, font={"color": "#e2e8f0"}),
        font={"color": "#e2e8f0"},
        xaxis=dict(gridcolor="#1e293b", tickfont={"color": "#94a3b8"}),
        yaxis=dict(gridcolor="#1e293b", tickfont={"color": "#94a3b8"}),
    )
    return fig


def render_income_sensitivity(base_data: dict) -> go.Figure:
    incomes = np.linspace(
        max(5000, base_data["MonthlyIncome"] * 0.3),
        base_data["MonthlyIncome"] * 2.5,
        30,
    )
    scores = []
    for inc in incomes:
        test = {**base_data, "MonthlyIncome": inc}
        try:
            score, _ = predict_risk_score(test)
            scores.append(score)
        except Exception:
            scores.append(0.0)

    current_score, _ = predict_risk_score(base_data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=incomes / 1000, y=scores,
        mode="lines+markers",
        line=dict(color="#818cf8", width=3, shape="spline"),
        marker=dict(size=6, color=scores,
                    colorscale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                    showscale=False),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.12)",
        name="Risk vs Income",
    ))
    fig.add_vline(
        x=base_data["MonthlyIncome"] / 1000,
        line_dash="dash", line_color="#facc15", line_width=2,
        annotation_text="Current", annotation_font_color="#facc15",
    )
    fig.update_layout(
        title=dict(text="📈 Income Sensitivity — How Income Affects Risk",
                   font={"color": "#e2e8f0", "size": 14}),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=280, margin=dict(l=10, r=10, t=50, b=30),
        xaxis=dict(title="Monthly Income (₹K)", gridcolor="#1e293b",
                   tickfont={"color": "#94a3b8"}, title_font={"color": "#94a3b8"}),
        yaxis=dict(title="Risk Score", gridcolor="#1e293b",
                   tickfont={"color": "#94a3b8"}, title_font={"color": "#94a3b8"},
                   range=[0, 22]),
        font={"color": "#e2e8f0"},
    )
    return fig


def show_whatif_simulator(baseline_input: dict | None = None):

    st.divider()
    st.markdown("## 🤔 What-If Simulator")
    st.caption("Adjust the sliders below and see how your risk score changes in real-time.")

    # Defaults
    default_age    = int(baseline_input["age"])              if baseline_input else 35
    default_income = float(baseline_input["MonthlyIncome"])  if baseline_input else 30000.0
    default_debt   = float(baseline_input["DebtRatio"])      if baseline_input else 0.4
    default_util   = float(baseline_input["RevolvingUtilizationOfUnsecuredLines"]) \
                     if baseline_input else 0.3

    # Baseline risk using actual model score
    if baseline_input:
        baseline_score, baseline_risk = predict_risk_score(baseline_input)
    else:
        baseline_risk  = None
        baseline_score = None

    # Sliders
    col_sliders, col_gauge = st.columns([1, 1], gap="large")

    with col_sliders:
        st.markdown("#### ⚙️ Adjust Parameters")

        sim_age = st.slider("🎂 Age", min_value=18, max_value=80,
                            value=default_age, step=1,
                            help="Your current age in years")
        sim_income = st.slider("💰 Monthly Income (₹)", min_value=5_000,
                               max_value=500_000, value=int(default_income),
                               step=1_000, format="₹%d",
                               help="Your monthly take-home income")
        sim_debt = st.slider("📉 Debt Ratio", min_value=0.0, max_value=1.0,
                             value=default_debt, step=0.01, format="%.2f",
                             help="Monthly debt payments ÷ monthly income")
        sim_util = st.slider("💳 Credit Utilization", min_value=0.0, max_value=1.0,
                             value=default_util, step=0.01, format="%.2f",
                             help="Credit used ÷ total credit limit")

        st.markdown("<br>", unsafe_allow_html=True)
        analyze_clicked = st.button("🔍 Analyze What-If Scenario",
                                    use_container_width=True, type="primary")

        if "whatif_analyzed" not in st.session_state:
            st.session_state.whatif_analyzed = False
        if analyze_clicked:
            st.session_state.whatif_analyzed = True

    if not st.session_state.whatif_analyzed:
        with col_gauge:
            st.markdown("#### 📊 Live Risk Score")
            st.info("👈 Adjust sliders and click **Analyze** to see results!")
        return

    # Prediction
    sim_data = {
        "age": sim_age,
        "MonthlyIncome": sim_income,
        "DebtRatio": sim_debt,
        "RevolvingUtilizationOfUnsecuredLines": sim_util,
    }

    try:
        sim_score, sim_risk = predict_risk_score(sim_data)
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return

    risk_color = get_risk_color(sim_risk)

    with col_gauge:
        st.markdown("#### 📊 Live Risk Score")
        st.plotly_chart(render_gauge(sim_score, sim_risk), use_container_width=True)
        st.markdown(
            f"""<div style="text-align:center; padding:10px 20px; border-radius:12px;
                background:{risk_color}22; border:2px solid {risk_color};
                color:{risk_color}; font-size:1.3rem; font-weight:700; margin-top:-10px;">
                {sim_risk}</div>""",
            unsafe_allow_html=True,
        )

    # Delta cards
    if baseline_input and baseline_score is not None:
        delta       = sim_score - baseline_score
        delta_str   = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"
        delta_color = "#ef4444" if delta > 0 else "#22c55e" if delta < 0 else "#94a3b8"
        delta_label = "⬆ Risk Increased" if delta > 0 else "⬇ Risk Decreased" if delta < 0 else "➡ No Change"

        st.markdown(
            f"""<div style="display:flex; gap:16px; margin:16px 0;
                justify-content:center; flex-wrap:wrap;">
                <div style="padding:14px 28px; border-radius:12px;
                    background:#0f172a; border:1px solid #334155;
                    text-align:center; min-width:160px;">
                    <div style="color:#94a3b8; font-size:0.8rem;">Your Input</div>
                    <div style="color:#3b82f6; font-size:1.4rem; font-weight:700;">{baseline_score:.1f}/20</div>
                    <div style="color:#3b82f6; font-size:0.85rem;">{baseline_risk}</div>
                </div>
                <div style="padding:14px 28px; border-radius:12px;
                    background:#0f172a; border:2px solid {delta_color};
                    text-align:center; min-width:160px;">
                    <div style="color:#94a3b8; font-size:0.8rem;">Change</div>
                    <div style="color:{delta_color}; font-size:1.4rem; font-weight:700;">{delta_str}</div>
                    <div style="color:{delta_color}; font-size:0.85rem;">{delta_label}</div>
                </div>
                <div style="padding:14px 28px; border-radius:12px;
                    background:#0f172a; border:1px solid #334155;
                    text-align:center; min-width:160px;">
                    <div style="color:#94a3b8; font-size:0.8rem;">What-If Result</div>
                    <div style="color:{risk_color}; font-size:1.4rem; font-weight:700;">{sim_score:.1f}/20</div>
                    <div style="color:{risk_color}; font-size:0.85rem;">{sim_risk}</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Tips
    st.markdown("#### 💡 What This Means")
    tips = []
    if sim_debt > 0.5:
        tips.append("📉 **Debt Ratio is high** — Try to reduce monthly debt payments below 50% of income.")
    if sim_util > 0.6:
        tips.append("💳 **Credit Utilization is high** — Keep it below 30% for a better credit profile.")
    if sim_income < 20000:
        tips.append("💰 **Low Income** — Higher income significantly reduces your risk score.")
    if sim_debt <= 0.3 and sim_util <= 0.3:
        tips.append("✅ **Great profile!** Low debt and utilization — you are in a strong financial position.")

    if tips:
        for tip in tips:
            st.markdown(tip)
    else:
        st.success("✅ Your financial parameters look balanced!")

    # Charts
    st.divider()
    st.markdown("#### 📈 Visual Analysis")

    tab1, tab2 = st.tabs(["Baseline vs What-If Comparison", "Income Sensitivity"])

    with tab1:
        if baseline_input:
            st.plotly_chart(
                render_comparison_bar(baseline_input, sim_data, baseline_risk, sim_risk),
                use_container_width=True,
            )
        else:
            st.info("Run a prediction first to see baseline vs what-if comparison.")

    with tab2:
        st.plotly_chart(render_income_sensitivity(sim_data), use_container_width=True)