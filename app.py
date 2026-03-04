# app.py - Customer Engagement Diagnostic Toolkit
# Based on: Venkat et al. (2026), IJRDM-11-2024-0639.R9
# FIXED: benchmarks scope issue for download functionality

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Retail CE Diagnostic Toolkit",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {font-size: 2.2rem; font-weight: bold; color: #1a5276; margin-bottom: 1rem;}
    .construct-header {font-size: 1.3rem; font-weight: 600; color: #2874a6; margin: 1.5rem 0 0.5rem 0;}
    .question-text {font-weight: 500; margin: 0.8rem 0 0.3rem 0; color: #34495e;}
    .metric-card {background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 12px 18px; border-radius: 10px; border-left: 4px solid #3498db;}
    .warning-box {background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 10px 0;}
    .critical-box {background-color: #f8d7da; padding: 15px; border-radius: 8px; border-left: 4px solid #dc3545; margin: 10px 0;}
    .success-box {background-color: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin: 10px 0;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. KNOWLEDGE BASE (FROM PDF)
# -----------------------------------------------------------------------------
# Sector benchmarks from Table 1 (Venkat et al., 2026)
BENCHMARKS = {
    "Apparel": {"SAT": 4.97, "TRU": 4.81, "AC": 3.50, "CE": 4.60},
    "Grocery": {"SAT": 5.56, "TRU": 5.28, "AC": 3.94, "CE": 5.10},
    "Pharmacy": {"SAT": 6.29, "TRU": 5.82, "AC": 4.48, "CE": 5.40}
}

# Survey items with EXACT wording guidance from Measures section (p. 10-11)
ITEMS = {
    "Satisfaction": [
        "Overall, I am satisfied with my experience at this retailer.",
        "My experience with this retailer has been displeasing.",
        "I feel content rather than frustrated when shopping with this retailer."
    ],
    "Trust": [
        "This retailer is honest and truthful in dealing with customers.",
        "I trust that this retailer has my best interests in mind.",
        "This retailer can be relied upon to deliver on its promises."
    ],
    "Affective Commitment": [
        "I feel emotionally attached to this retailer.",
        "This retailer has a great deal of personal meaning for me.",
        "I would be happy to continue my relationship with this retailer for a long time."
    ],
    "Attitudinal Loyalty": [
        "I consider this retailer to be my first choice for [category] purchases.",
        "I would recommend this retailer to others.",
        "I feel a sense of belonging with this retailer.",
        "I am loyal to this retailer."
    ],
    "Repurchase Intention": [
        "I intend to shop at this retailer again in the near future.",
        "I will likely make my next [category] purchase from this retailer.",
        "I plan to continue doing business with this retailer."
    ],
    "Advocacy": [
        "I actively recommend this retailer to friends and family.",
        "I speak positively about this retailer to others.",
        "I would defend this retailer if someone criticized it."
    ]
}

# -----------------------------------------------------------------------------
# 3. SIDEBAR - CONTEXT SETUP
# -----------------------------------------------------------------------------
st.sidebar.header("🔧 Diagnostic Setup")

sector = st.sidebar.selectbox(
    "Retail Sector", 
    ["Apparel", "Grocery", "Pharmacy"],
    help="Select the sector that matches your use case. Benchmarks are drawn from the Canadian national surveys in Venkat et al. (2026)."
)

role = st.sidebar.selectbox(
    "Your Role", 
    ["Retailer/Brand Manager", "Consultant", "Researcher"],
    help="Adjusts output language: actionable recommendations vs. academic framing."
)

data_type = st.sidebar.radio(
    "Spending Data Type", 
    ["Self-Report Estimate", "CRM Actual Spend"],
    help="Study 1 used self-reported spend; Study 2 linked survey responses to actual CRM transaction data."
)

# ✅ FIX: Define benchmarks at global scope (accessible throughout script)
benchmarks = BENCHMARKS[sector]

st.sidebar.markdown("---")
st.sidebar.info("""
    **Model Source**  
    Venkat, R., Carter-Rogers, K., Fullerton, G., & Morales, M. (2026).  
    *Customer Engagement in a Retail Setting: An Examination of Antecedents and Outcomes*.  
    International Journal of Retail & Distribution Management.  
    Manuscript ID: IJRDM-11-2024-0639.R9
    
    **Validation**  
    ✓ Canada (N=918 total)  
    ✓ Apparel (N=225), Grocery (N=229), Pharmacy (N=464)  
    ✓ SEM with bootstrapping (1,000 samples)  
    ✓ Second-order CE construct validated
""")

# -----------------------------------------------------------------------------
# 4. MAIN HEADER
# -----------------------------------------------------------------------------
st.markdown('<p class="main-header">🛍️ Retail Customer Engagement Diagnostic Toolkit</p>', unsafe_allow_html=True)
st.markdown(f"**Sector Context:** {sector} | **Benchmark Reference:** {sector} norms from Venkat et al. (2026)")
st.markdown("""
    This diagnostic tool assesses Customer Engagement (CE) health using the validated model:  
    **Satisfaction → Trust → Affective Commitment → Customer Engagement → Outcomes**  
    
    *Rate each statement: 1 = Strongly Disagree → 7 = Strongly Agree*
""")

# -----------------------------------------------------------------------------
# 5. INPUT COLLECTION (WITH VISIBLE QUESTIONS)
# -----------------------------------------------------------------------------
def likert_item(statement, key, reverse=False):
    """Render a Likert item with visible question text + slider"""
    st.markdown(f'<p class="question-text">{statement}</p>', unsafe_allow_html=True)
    value = st.slider("", 1, 7, 4, label_visibility="collapsed", key=key)
    return 8 - value if reverse else value

# Initialize scores dictionary
scores = {}

# --- ANTECEDENTS SECTION ---
with st.expander("📊 Part 1: Antecedents (Drivers of Engagement)", expanded=True):
    
    st.markdown('<p class="construct-header">Satisfaction</p>', unsafe_allow_html=True)
    st.caption("Spreng & MacKoy (1996) • α = .93–.95")
    sat_scores = [
        likert_item(ITEMS["Satisfaction"][0], "sat1"),
        likert_item(ITEMS["Satisfaction"][1], "sat2", reverse=True),
        likert_item(ITEMS["Satisfaction"][2], "sat3")
    ]
    scores["SAT"] = round(np.mean(sat_scores), 2)
    
    st.markdown('<p class="construct-header">Trust</p>', unsafe_allow_html=True)
    st.caption("Doney & Cannon (1997) • α = .88–.89")
    tru_scores = [
        likert_item(ITEMS["Trust"][0], "tru1"),
        likert_item(ITEMS["Trust"][1], "tru2"),
        likert_item(ITEMS["Trust"][2], "tru3")
    ]
    scores["TRU"] = round(np.mean(tru_scores), 2)
    
    st.markdown('<p class="construct-header">Affective Commitment</p>', unsafe_allow_html=True)
    st.caption("Allen & Meyer (1990), adapted • α = .94–.96")
    ac_scores = [
        likert_item(ITEMS["Affective Commitment"][0], "ac1"),
        likert_item(ITEMS["Affective Commitment"][1], "ac2"),
        likert_item(ITEMS["Affective Commitment"][2], "ac3")
    ]
    scores["AC"] = round(np.mean(ac_scores), 2)

# --- ENGAGEMENT MANIFESTATIONS SECTION ---
with st.expander("🚀 Part 2: Engagement Manifestations (Outcomes)"):
    
    st.markdown('<p class="construct-header">Attitudinal Loyalty</p>', unsafe_allow_html=True)
    st.caption("Yoo & Donthu (2001) • α = .88–.92")
    al_scores = [likert_item(ITEMS["Attitudinal Loyalty"][i], f"al{i+1}") for i in range(4)]
    scores["AL"] = round(np.mean(al_scores), 2)
    
    st.markdown('<p class="construct-header">Repurchase Intention</p>', unsafe_allow_html=True)
    st.caption("Zeithaml et al. (1996) • α = .91–.94")
    rep_scores = [likert_item(ITEMS["Repurchase Intention"][i], f"rep{i+1}") for i in range(3)]
    scores["REP"] = round(np.mean(rep_scores), 2)
    
    st.markdown('<p class="construct-header">Advocacy Intention</p>', unsafe_allow_html=True)
    st.caption("Fullerton (2003) • α = .89–.94")
    adv_scores = [likert_item(ITEMS["Advocacy"][i], f"adv{i+1}") for i in range(3)]
    scores["ADV"] = round(np.mean(adv_scores), 2)
    
    st.markdown('<p class="construct-header">Behavioral Loyalty (Spending)</p>', unsafe_allow_html=True)
    if data_type == "Self-Report Estimate":
        spend = st.number_input("Approximate annual spend at this retailer ($)", min_value=0, value=500, step=50)
    else:
        spend = st.number_input("Actual annual spend from CRM data ($)", min_value=0, value=750, step=50)
        st.caption("💡 Study 2 validated the model using actual transaction data linked via loyalty card IDs.")
    
    scores["BL"] = round(min(7.0, max(1.0, 1 + 1.2 * np.log1p(spend / 100))), 2)
    scores["CE"] = round(np.mean([scores["AL"], scores["REP"], scores["ADV"], scores["BL"]]), 2)

# -----------------------------------------------------------------------------
# 6. DIAGNOSTIC ENGINE (TRIGGERED BY BUTTON)
# -----------------------------------------------------------------------------
if st.button("🔍 Calculate Engagement Diagnosis", type="primary"):
    st.markdown("---")
    st.subheader("📈 Your Engagement Profile")
    
    # Helper: status indicator with color coding
    def status_indicator(score, benchmark):
        diff = score - benchmark
        if diff >= 0.5:
            return "🟢 Strong", "above benchmark"
        elif diff >= -0.5:
            return "🟡 Moderate", "near benchmark"
        else:
            return "🔴 Development", "below benchmark"
    
    # Display metric cards in columns
    cols = st.columns(4)
    with cols[0]:
        status, note = status_indicator(scores["SAT"], benchmarks["SAT"])
        st.markdown(f'<div class="metric-card"><strong>Satisfaction</strong><br>{scores["SAT"]:.2f}/7<br><small>{note} ({benchmarks["SAT"]:.2f})</small><br>{status}</div>', unsafe_allow_html=True)
    with cols[1]:
        status, note = status_indicator(scores["TRU"], benchmarks["TRU"])
        st.markdown(f'<div class="metric-card"><strong>Trust</strong><br>{scores["TRU"]:.2f}/7<br><small>{note} ({benchmarks["TRU"]:.2f})</small><br>{status}</div>', unsafe_allow_html=True)
    with cols[2]:
        status, note = status_indicator(scores["AC"], benchmarks["AC"])
        st.markdown(f'<div class="metric-card"><strong>Commitment</strong><br>{scores["AC"]:.2f}/7<br><small>{note} ({benchmarks["AC"]:.2f})</small><br>{status}</div>', unsafe_allow_html=True)
    with cols[3]:
        status, note = status_indicator(scores["CE"], benchmarks["CE"])
        st.markdown(f'<div class="metric-card"><strong>Engagement (CE)</strong><br>{scores["CE"]:.2f}/7<br><small>{note} ({benchmarks["CE"]:.2f})</small><br>{status}</div>', unsafe_allow_html=True)
    
    # Radar chart
    st.markdown("### 🎯 Profile Visualization")
    df_radar = pd.DataFrame(dict(
        Metric=['Satisfaction', 'Trust', 'Commitment', 'Engagement'],
        Your_Score=[scores["SAT"], scores["TRU"], scores["AC"], scores["CE"]],
        Sector_Benchmark=[benchmarks["SAT"], benchmarks["TRU"], benchmarks["AC"], benchmarks["CE"]]
    ))
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df_radar["Your_Score"],
        theta=df_radar["Metric"],
        fill="toself",
        name="Your Score",
        line_color="#2E86AB"
    ))
    fig.add_trace(go.Scatterpolar(
        r=df_radar["Sector_Benchmark"],
        theta=df_radar["Metric"],
        fill="toself",
        name=f"{sector} Benchmark",
        line=dict(color="#E74C3C", dash="dot"),
        opacity=0.7
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 7], tickmode="linear")),
        showlegend=True,
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # -----------------------------------------------------------------
    # DIAGNOSTIC LOGIC TREE
    # -----------------------------------------------------------------
    st.subheader("🔑 Diagnostic Insights")
    insights = []
    
    if scores["SAT"] >= 5.0 and scores["TRU"] < 4.5:
        insights.append({
            "type": "critical",
            "title": "⚠️ Critical Gap: Satisfaction Without Trust",
            "message": "Customers report satisfaction but lack trust. Per Venkat et al. (2026), **Trust fully mediates** the path from Satisfaction → Affective Commitment.",
            "action": "Audit brand promise delivery consistency. Empower frontline staff with resolution authority."
        })
    
    if scores["AC"] < benchmarks["AC"] - 0.3:
        insights.append({
            "type": "warning",
            "title": "💡 Opportunity: Build Emotional Connection",
            "message": "Affective Commitment is below sector norms. Engagement requires emotional attachment.",
            "action": "Introduce personalization, community features, or experiential touchpoints."
        })
    
    if scores["AC"] >= 4.5 and scores["CE"] < 4.5:
        insights.append({
            "type": "warning",
            "title": "🔄 Activation Gap: Commitment Not Translating to Action",
            "message": "Customers feel attached but aren't acting (recommending, repurchasing, spending).",
            "action": "Add behavioral triggers: referral rewards, exclusive early access."
        })
    
    if sector == "Pharmacy" and scores["REP"] < 4.0:
        insights.append({
            "type": "info",
            "title": "💊 Sector Note: Pharmacy Repurchase Constraints",
            "message": "Repurchase may be constrained by prescriptions/insurance, not engagement.",
            "action": "Focus on advocacy and basket expansion rather than visit frequency."
        })
    
    if all([scores[k] > benchmarks[k] + 0.3 for k in ["SAT", "TRU", "AC", "CE"]]):
        insights.append({
            "type": "success",
            "title": "✅ Engagement Flywheel Active",
            "message": "All antecedents exceed sector benchmarks.",
            "action": "Double down on what's working. Test expansion into adjacent categories."
        })
    
    for insight in insights:
        if insight["type"] == "critical":
            st.markdown(f'<div class="critical-box"><strong>{insight["title"]}</strong><br><br>{insight["message"]}<br><br>👉 <em>{insight["action"]}</em></div>', unsafe_allow_html=True)
        elif insight["type"] == "warning":
            st.markdown(f'<div class="warning-box"><strong>{insight["title"]}</strong><br><br>{insight["message"]}<br><br>👉 <em>{insight["action"]}</em></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-box"><strong>{insight["title"]}</strong><br><br>{insight["message"]}<br><br>👉 <em>{insight["action"]}</em></div>', unsafe_allow_html=True)
    
    if not insights:
        st.info("✅ No critical gaps detected. Scores are aligned with or exceed sector benchmarks.")
    
    # -----------------------------------------------------------------
    # EXPECTED IMPACT CALCULATOR
    # -----------------------------------------------------------------
    st.subheader("📈 Expected Impact of Improvements")
    st.markdown("*Based on standardized path coefficients from Venkat et al. (2026), Table 2*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**If Trust increases by +1.0 point:**")
        ce_coef = 0.61 if sector=='Pharmacy' else 0.74 if sector=='Grocery' else 0.78
        adv_coef = 0.77 if sector=='Pharmacy' else 0.82
        st.markdown(f"- → Affective Commitment: +{0.39 if sector=='Grocery' else 0.49 if sector=='Pharmacy' else 0.65:.2f} pts")
        st.markdown(f"- → Customer Engagement: +{ce_coef:.2f} pts")
        st.markdown(f"- → Advocacy: +{adv_coef:.2f} pts")
    
    with col2:
        st.markdown("**If Commitment increases by +1.0 point:**")
        ce_coef = 0.43 if sector=='Pharmacy' else 0.28 if sector=='Grocery' else 0.19
        st.markdown(f"- → Customer Engagement: +{ce_coef:.2f} pts")
        st.markdown(f"- → Attitudinal Loyalty: +{0.78 if sector=='Pharmacy' else 0.72:.2f} pts")
        st.markdown(f"- → Behavioral Spend: +0.20 pts (normalized scale)")

# -----------------------------------------------------------------------------
# 7. DOWNLOAD FUNCTIONALITY (✅ NOW WORKS - benchmarks in scope)
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📥 Export Your Diagnostic")

summary_text = f"""
CUSTOMER ENGAGEMENT DIAGNOSTIC SUMMARY
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Sector: {sector} | Role: {role} | Data Type: {data_type}

SCORES (1-7 scale):
• Satisfaction: {scores["SAT"]:.2f} (Benchmark: {benchmarks["SAT"]:.2f})
• Trust: {scores["TRU"]:.2f} (Benchmark: {benchmarks["TRU"]:.2f})
• Affective Commitment: {scores["AC"]:.2f} (Benchmark: {benchmarks["AC"]:.2f})
• Customer Engagement: {scores["CE"]:.2f} (Benchmark: {benchmarks["CE"]:.2f})

KEY INSIGHTS:
{chr(10).join([f"- {i['title']}: {i['action']}" for i in insights]) if 'insights' in locals() and insights else "- Complete calculation to generate insights"}

RECOMMENDED NEXT STEPS:
1. Prioritize trust-building if SAT>5.0 but TRU<4.5
2. Add emotional connection tactics if AC < benchmark
3. Activate committed customers with behavioral triggers if CE < AC
4. For Pharmacy: focus on advocacy/basket expansion if REP constrained

Model Source: Venkat et al. (2026), IJRDM-11-2024-0639.R9
"""

st.download_button(
    label="📄 Download Diagnostic Summary (Text)",
    data=summary_text,
    file_name=f"CE_Diagnostic_{sector}_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
    mime="text/plain"
)

# -----------------------------------------------------------------------------
# 8. FOOTER & TECHNICAL NOTES
# -----------------------------------------------------------------------------
with st.expander("🔬 Technical Notes for Researchers"):
    st.markdown("""
    **Measurement Model**  
    - CE modeled as reflective second-order latent construct
    - First-order manifestations: Attitudinal Loyalty, Repurchase Intention, Advocacy, Behavioral Loyalty  
    - All scales: 7-point Likert (1=Strongly Disagree, 7=Strongly Agree)  
    - Reverse-coded item: Satisfaction #2 ("displeasing")  
    
    **Validation Metrics (Target Thresholds)**  
    | Criterion | Threshold | Study 1 (Clothing) | Study 1 (Grocery) | Study 2 (Pharmacy) |
    |-----------|-----------|------------------|-------------------|-------------------|
    | Cronbach's α | ≥ .70 | .88–.95 | .89–.96 | .88–.94 |
    | Composite Reliability | ≥ .70 | .88–.95 | .88–.96 | .89–.94 |
    | AVE | ≥ .50 | .64–.86 | .71–.88 | .72–.85 |
    | Model Fit (CFI) | ≥ .95 | .982 | .978 | .987 |
    
    **Limitations**  
    - Cross-sectional design: causal claims require longitudinal/experimental follow-up  
    - Canadian sample: replicate in other cultural/retail contexts before global deployment  
    - Pharmacy repurchase may be constrained by external factors (prescriptions, insurance)  
    """)

st.caption("""
    **Citation for Use**  
    Venkat, R., Carter-Rogers, K., Fullerton, G., & Morales, M. (2026). 
    Customer Engagement in a Retail Setting: An Examination of Antecedents and Outcomes. 
    *International Journal of Retail & Distribution Management*. 
    Manuscript ID: IJRDM-11-2024-0639.R9
""")