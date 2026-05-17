"""
app.py — Minotauros Agricultural Intelligence
Gradio UI for the Real Estate Beyond RGB platform.
"""

import json
import os

import gradio as gr
import pandas as pd
import plotly.graph_objects as go

from src.data_loader import load_plots, load_crop_knowledge_base
from src.investment_analysis import build_full_investment_analysis


from dotenv import load_dotenv
load_dotenv()  # φορτώνει το .env πριν από οτιδήποτε άλλο


# ── Brand palette ──────────────────────────────────────────────────────────────
C_DARK   = "#1a4a2e"
C_GREEN  = "#2d7a4f"
C_GOLD   = "#c8a84b"
C_CREAM  = "#f5f0e8"
C_RED    = "#c0392b"
C_BROWN  = "#5a3e1b"
PLOT_COLORS = [C_DARK, C_GREEN, C_GOLD, C_BROWN]

SCENARIO_LABELS = ["Base", "Optimistic", "Pessimistic"]
SCENARIO_MAP    = {"Base": "base", "Optimistic": "upside", "Pessimistic": "downside"}

# ── Data cache ─────────────────────────────────────────────────────────────────
_cache: dict = {}

def get_analysis(risk: str) -> pd.DataFrame:
    if risk not in _cache:
        plots = load_plots()
        crops = load_crop_knowledge_base()
        rows  = build_full_investment_analysis(
            plots=plots, crops=crops, investor_risk_level=risk
        )
        _cache[risk] = pd.DataFrame(rows)
    return _cache[risk].copy()

PLOT_NAMES = ["All plots"] + [p["name"] for p in load_plots()]
CROP_NAMES = [c["name"] for c in load_crop_knowledge_base()]

# ── Chart builders ─────────────────────────────────────────────────────────────
def make_cumulative_chart(cf: pd.DataFrame, crop: str, plot: str) -> go.Figure:
    fig = go.Figure()
    # Shaded area below zero (loss zone)
    fig.add_hrect(
        y0=cf["cumulative_cashflow_eur"].min() * 1.1,
        y1=0,
        fillcolor="rgba(192,57,43,0.06)",
        line_width=0,
    )
    fig.add_trace(go.Scatter(
        x=cf["calendar_year"],
        y=cf["cumulative_cashflow_eur"],
        mode="lines+markers",
        line=dict(color=C_GREEN, width=3),
        marker=dict(size=8, color=C_GOLD, line=dict(color=C_GREEN, width=2)),
        fill="tozeroy",
        fillcolor="rgba(45,122,79,0.10)",
        name="Cumulative Cashflow",
        hovertemplate="Year %{x}<br>€%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(
        y=0, line_dash="dot", line_color=C_GOLD, line_width=2,
        annotation_text="Break-even",
        annotation_position="bottom right",
        annotation_font_color=C_GOLD,
    )
    fig.update_layout(
        title=dict(text=f"Cumulative Cashflow — {crop}", font=dict(color=C_DARK, size=14, family="Georgia")),
        xaxis_title="Year", yaxis_title="€",
        template="plotly_white",
        margin=dict(t=50, b=40, l=60, r=20),
        hovermode="x unified",
        font=dict(color=C_DARK, family="Georgia"),
        plot_bgcolor=C_CREAM,
        paper_bgcolor="#ffffff",
    )
    return fig


def make_bar_chart(cf: pd.DataFrame, crop: str, plot: str) -> go.Figure:
    colors = [C_GREEN if v >= 0 else C_RED for v in cf["cashflow_eur"]]
    fig = go.Figure(go.Bar(
        x=cf["calendar_year"],
        y=cf["cashflow_eur"],
        marker_color=colors,
        marker_line_color=C_DARK,
        marker_line_width=0.5,
        text=[f"€{v:,.0f}" for v in cf["cashflow_eur"]],
        textposition="outside",
        textfont=dict(size=9, color=C_DARK),
        hovertemplate="Year %{x}<br>€%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=C_DARK, line_width=1.5)
    fig.update_layout(
        title=dict(text=f"Annual Cashflow — {crop}", font=dict(color=C_DARK, size=14, family="Georgia")),
        xaxis_title="Year", yaxis_title="€",
        template="plotly_white",
        margin=dict(t=50, b=40, l=60, r=20),
        font=dict(color=C_DARK, family="Georgia"),
        plot_bgcolor=C_CREAM,
        paper_bgcolor="#ffffff",
    )
    return fig


def make_npv_comparison(df: pd.DataFrame, crop: str) -> go.Figure:
    bar_colors = [C_GREEN if v >= 0 else C_RED for v in df["npv_eur"]]
    fig = go.Figure(go.Bar(
        x=df["plot_name"],
        y=df["npv_eur"],
        marker_color=bar_colors,
        marker_line_color=C_DARK,
        marker_line_width=0.5,
        text=[f"€{v:,.0f}" for v in df["npv_eur"]],
        textposition="auto",
        textfont=dict(color="#ffffff", size=11, family="Georgia"),
        hovertemplate="%{x}<br>NPV: €%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"NPV by Plot — {crop}", font=dict(color=C_DARK, size=14, family="Georgia")),
        template="plotly_white",
        yaxis_title="€", xaxis_title="Land Plot",
        font=dict(color=C_DARK, family="Georgia"),
        margin=dict(t=50, b=40, l=60, r=20),
        plot_bgcolor=C_CREAM,
        paper_bgcolor="#ffffff",
    )
    return fig


def make_suitability_comparison(df: pd.DataFrame, crop: str) -> go.Figure:
    cats = ["pH Score", "Water Score", "Vegetation Score", "Risk Score"]
    cols = ["ph_score", "water_score", "vegetation_score", "risk_score"]
    fig = go.Figure()
    for i, (_, row) in enumerate(df.iterrows()):
        fig.add_trace(go.Bar(
            name=row["plot_name"],
            x=cats,
            y=[row[c] for c in cols],
            marker_color=PLOT_COLORS[i % 4],
            hovertemplate=f"{row['plot_name']}<br>%{{x}}: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(
        barmode="group",
        title=dict(text=f"Suitability Components — {crop}", font=dict(color=C_DARK, size=14, family="Georgia")),
        template="plotly_white",
        yaxis=dict(range=[0, 1.15], title="Score (0–1)"),
        font=dict(color=C_DARK, family="Georgia"),
        margin=dict(t=50, b=40, l=60, r=20),
        plot_bgcolor=C_CREAM,
        paper_bgcolor="#ffffff",
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


# ── KPI HTML builders ──────────────────────────────────────────────────────────
def _card(label: str, value: str, bg: str = C_GREEN, text: str = "#ffffff") -> str:
    return f"""
    <div style="background:{bg};color:{text};padding:16px 20px;border-radius:10px;
                flex:1;text-align:center;min-width:120px;
                box-shadow:0 3px 10px rgba(0,0,0,0.18);letter-spacing:.3px;">
      <div style="font-size:10px;opacity:.75;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">{label}</div>
      <div style="font-size:21px;font-weight:700;font-family:Georgia,serif">{value}</div>
    </div>"""


def kpi_row_html(row: pd.Series) -> str:
    irr  = "N/A" if pd.isna(row["irr"]) else f"{float(row['irr']):.1%}"
    pay = "N/A" if pd.isna(row["payback_year"]) else str(int(row["payback_year"]))
    npv_bg = C_GREEN if row["npv_eur"] >= 0 else C_RED
    return f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin:14px 0;">
      {_card("Best Crop", row['crop_name'], C_DARK)}
      {_card("Plot", row['plot_name'], C_GREEN)}
      {_card("NPV", f"€{row['npv_eur']:,.0f}", npv_bg)}
      {_card("IRR", irr, C_GOLD)}
      {_card("Payback Year", pay, C_DARK)}
      {_card("Suitability", f"{row['suitability_score']:.2f}", C_GREEN)}
      {_card("CAPEX", f"€{row['total_initial_investment_eur']:,.0f}", C_BROWN)}
    </div>"""


def comparison_cards_html(df: pd.DataFrame) -> str:
    html = '<div style="display:flex;gap:12px;flex-wrap:wrap;margin:14px 0;">'
    for _, row in df.iterrows():
        irr  = "N/A" if pd.isna(row["irr"]) else f"{float(row['irr']):.1%}"
        pay = "N/A" if pd.isna(row["payback_year"]) else str(int(row["payback_year"]))
        npv_color = C_GREEN if row["npv_eur"] >= 0 else C_RED
        suit_bar_w = int(row["suitability_score"] * 100)
        html += f"""
        <div style="background:#ffffff;border:2px solid {C_GREEN};border-radius:10px;
                    padding:16px 20px;min-width:180px;flex:1;
                    box-shadow:0 2px 8px rgba(0,0,0,0.10);">
          <div style="font-weight:700;color:{C_DARK};font-size:15px;font-family:Georgia,serif;
                      margin-bottom:10px;border-bottom:2px solid {C_GOLD};padding-bottom:6px">{row['plot_name']}</div>
          <div style="color:{npv_color};font-size:24px;font-weight:700;font-family:Georgia,serif">€{row['npv_eur']:,.0f}</div>
          <div style="font-size:10px;color:#999;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px">NPV</div>
          <div style="font-size:13px;color:#444;margin-bottom:3px">IRR: <b>{irr}</b></div>
          <div style="font-size:13px;color:#444;margin-bottom:3px">Payback: <b>{pay}</b></div>
          <div style="font-size:13px;color:#444;margin-bottom:8px">CAPEX: <b>€{row['total_initial_investment_eur']:,.0f}</b></div>
          <div style="font-size:11px;color:#777;margin-bottom:4px">Suitability</div>
          <div style="background:#e0e0e0;border-radius:4px;height:8px;margin-bottom:4px">
            <div style="background:{C_GREEN};width:{suit_bar_w}%;height:8px;border-radius:4px"></div>
          </div>
          <div style="font-size:11px;color:{C_DARK};font-weight:700;margin-bottom:8px">{row['suitability_score']:.2f}</div>
          <div style="font-size:11px;color:#888">NDVI {row['ndvi_mean']:.3f} · NDMI {row['ndmi_mean']:.3f} · pH {row['estimated_ph']}</div>
        </div>"""
    html += "</div>"
    return html


# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_table_t1(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["crop_name", "plot_name", "npv_eur", "irr", "payback_year",
              "suitability_score", "total_initial_investment_eur",
              "ndvi_mean", "ndmi_mean", "estimated_ph", "ph_class"]].copy()
    out.columns = ["Crop", "Plot", "NPV (€)", "IRR", "Payback",
                   "Suitability", "CAPEX (€)", "NDVI", "NDMI", "Est. pH", "pH Class"]
    out["NPV (€)"]   = out["NPV (€)"].apply(lambda x: f"{x:,.0f}")
    out["IRR"]       = out["IRR"].apply(lambda x: "N/A" if pd.isna(x) else f"{float(x):.1%}")
    out["CAPEX (€)"] = out["CAPEX (€)"].apply(lambda x: f"{x:,.0f}")
    return out


def fmt_table_t2(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["plot_name", "npv_eur", "irr", "payback_year", "suitability_score",
              "ph_score", "water_score", "vegetation_score", "risk_score",
              "estimated_ph", "ndvi_mean", "ndmi_mean", "total_initial_investment_eur"]].copy()
    out.columns = ["Plot", "NPV (€)", "IRR", "Payback", "Suitability",
                   "pH Score", "Water", "Vegetation", "Risk",
                   "Est. pH", "NDVI", "NDMI", "CAPEX (€)"]
    out["NPV (€)"]   = out["NPV (€)"].apply(lambda x: f"{x:,.0f}")
    out["IRR"]       = out["IRR"].apply(lambda x: "N/A" if pd.isna(x) else f"{float(x):.1%}")
    out["CAPEX (€)"] = out["CAPEX (€)"].apply(lambda x: f"{x:,.0f}")
    return out

def json_safe(obj):
    import numpy as np
    import pandas as pd

    if obj is None:
        return None

    if isinstance(obj, float) and pd.isna(obj):
        return None

    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.floating,)):
        if pd.isna(obj):
            return None
        return float(obj)

    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()

    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [json_safe(v) for v in obj]

    return obj

# ── Tab 1 callback ─────────────────────────────────────────────────────────────
def tab1_cb(plot_sel, risk, scenario_lbl, capital, feasible_only, crop_sel):
    scenario = SCENARIO_MAP[scenario_lbl]
    df = get_analysis(risk)

    filt = df[df["scenario_name"] == scenario].copy()
    if plot_sel != "All plots":
        filt = filt[filt["plot_name"] == plot_sel].copy()

    filt["capital_feasible"] = filt["total_initial_investment_eur"] <= float(capital)
    if feasible_only:
        filt = filt[filt["capital_feasible"]].copy()

    empty = go.Figure()
    if len(filt) == 0:
        no_res = "<p style='color:#888;padding:10px'>No results for selected filters.</p>"
        return (empty, empty, pd.DataFrame(), no_res,
                gr.update(choices=[], value=None), "{}")

    filt = filt.sort_values("npv_eur", ascending=False).reset_index(drop=True)
    available_crops = filt["crop_name"].unique().tolist()

    if crop_sel not in available_crops:
        crop_sel = available_crops[0]

    sel = filt[filt["crop_name"] == crop_sel].iloc[0]
    cf  = pd.DataFrame(sel["cashflow_table"])

    fig_cum = make_cumulative_chart(cf, sel["crop_name"], sel["plot_name"])
    fig_bar = make_bar_chart(cf, sel["crop_name"], sel["plot_name"])

    ctx = {
        "tab": "Investment Ranker",
        "filters": {"plot": plot_sel, "risk": risk, "scenario": scenario_lbl},
        "selected_crop": sel["crop_name"],
        "selected_plot": sel["plot_name"],
        "npv_eur": round(float(sel["npv_eur"]), 0),
        "irr": None if pd.isna(sel["irr"]) else round(float(sel["irr"]), 4),
        "payback_year": sel["payback_year"],
        "suitability_score": float(sel["suitability_score"]),
        "ph_score": float(sel["ph_score"]),
        "water_score": float(sel["water_score"]),
        "vegetation_score": float(sel["vegetation_score"]),
        "risk_score": float(sel["risk_score"]),
        "total_investment_eur": float(sel["total_initial_investment_eur"]),
        "ndvi": float(sel["ndvi_mean"]),
        "ndmi": float(sel["ndmi_mean"]),
        "estimated_ph": float(sel["estimated_ph"]),
        "ph_class": sel["ph_class"],
        "all_ranked_crops": available_crops,
        "top3": [
            {
                "crop": r["crop_name"],
                "plot": r["plot_name"],
                "npv": round(float(r["npv_eur"]), 0),
                "irr": None if pd.isna(r["irr"]) else round(float(r["irr"]), 4),
            }
            for _, r in filt.head(3).iterrows()
        ],
    }

    return (
        fig_cum,
        fig_bar,
        fmt_table_t1(filt),
        kpi_row_html(sel),
        gr.update(choices=available_crops, value=crop_sel),
        json.dumps(json_safe(ctx), ensure_ascii=False),
    )


# ── Tab 2 callback ─────────────────────────────────────────────────────────────
def tab2_cb(crop_sel, scenario_lbl, risk):
    scenario = SCENARIO_MAP[scenario_lbl]
    df = get_analysis(risk)

    filt = df[(df["crop_name"] == crop_sel) & (df["scenario_name"] == scenario)].copy()

    empty = go.Figure()
    if len(filt) == 0:
        no_res = "<p style='color:#888;padding:10px'>No data for selected filters.</p>"
        return empty, empty, pd.DataFrame(), no_res, "{}"

    fig_npv  = make_npv_comparison(filt, crop_sel)
    fig_suit = make_suitability_comparison(filt, crop_sel)

    ctx = {
        "tab": "Plot Comparison",
        "crop": crop_sel,
        "scenario": scenario_lbl,
        "risk": risk,
        "plots": [
            {
                "plot": r["plot_name"],
                "npv": round(float(r["npv_eur"]), 0),
                "irr": None if pd.isna(r["irr"]) else round(float(r["irr"]), 4),
                "suitability": float(r["suitability_score"]),
                "payback": r["payback_year"],
                "ndvi": float(r["ndvi_mean"]),
                "ndmi": float(r["ndmi_mean"]),
                "estimated_ph": float(r["estimated_ph"]),
            }
            for _, r in filt.iterrows()
        ],
    }

    return (
        fig_npv,
        fig_suit,
        fmt_table_t2(filt),
        comparison_cards_html(filt),
        json.dumps(json_safe(ctx), ensure_ascii=False),
    )


# ── Gemini chatbot ─────────────────────────────────────────────────────────────
def minotauros_chat(message: str, history: list, context_json: str, api_key_input: str):
    import os
    import traceback
    import google.generativeai as genai

    if history is None:
        history = []

    if not message or not message.strip():
        return history, history

    key = (api_key_input or "").strip() or os.getenv("GEMINI_API_KEY", "")

    if not key:
        history.append({"role": "user", "content": message})
        history.append({
            "role": "assistant",
            "content": "⚠️ Missing Gemini API key. Add it in the Gemini API Key field or in the .env file."
        })
        return history, history

    system = f"""You are Minotauros, an expert agricultural investment AI assistant for the
Real Estate Beyond RGB platform.

CURRENT DASHBOARD CONTEXT:
{context_json}

KEY CONCEPTS:
- NPV: Net Present Value
- IRR: Internal Rate of Return
- Payback Year: first year cumulative cashflow turns positive
- Suitability Score: spectral land-crop fit from pH, water, vegetation and risk
- NDVI: vegetation health proxy
- NDMI: moisture proxy
- Estimated pH: rule-based hyperspectral proxy, not laboratory measurement

STYLE RULES:
- Answer in the same language as the user.
- Be short, direct and practical.
- Use numbers from the dashboard context when available.
- Do not invent NPV, IRR, payback, CAPEX or suitability values.
- If data is missing, say clearly that it is not available in the dashboard.
- For Makeathon demo mode, explain like an investor assistant, not like an academic report.
"""

    try:
        genai.configure(api_key=key)

        model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview",
            system_instruction=system,
        )

        gemini_history = []

        for item in history:
            role = item.get("role")
            content = item.get("content")

            if not content:
                continue

            if role == "user":
                gemini_history.append({
                    "role": "user",
                    "parts": [content]
                })

            elif role == "assistant":
                gemini_history.append({
                    "role": "model",
                    "parts": [content]
                })

        chat_obj = model.start_chat(history=gemini_history)
        response = chat_obj.send_message(message)

        reply = response.text if response.text else "Δεν έλαβα απάντηση από το Gemini."

    except Exception as exc:
        print("CHATBOT ERROR:")
        print(traceback.format_exc())
        reply = f"⚠️ Chatbot error: {exc}"

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return history, history


# ── Custom CSS ─────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;600&display=swap');

.gradio-container {
    max-width: 1420px !important;
    font-family: 'Source Sans 3', sans-serif;
    background: #f5f0e8;
}
.main-header {
    background: linear-gradient(135deg, #1a4a2e 0%, #2d7a4f 60%, #1a4a2e 100%);
    padding: 22px 32px;
    border-radius: 14px;
    margin-bottom: 18px;
    border-bottom: 4px solid #c8a84b;
    box-shadow: 0 4px 20px rgba(26,74,46,0.25);
}
.main-header h1 {
    color: #c8a84b;
    margin: 0 0 4px;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 28px;
    letter-spacing: 2px;
}
.main-header p {
    color: #b0ccba;
    margin: 0;
    font-size: 13px;
    letter-spacing: .5px;
}
.tab-nav { border-bottom: 2px solid #c8a84b !important; }
.tab-nav button {
    color: #1a4a2e !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
.tab-nav button.selected {
    border-bottom: 3px solid #c8a84b !important;
    color: #1a4a2e !important;
}
.chatbot-container { border: 2px solid #2d7a4f; border-radius: 10px; }
label { color: #1a4a2e !important; font-weight: 600 !important; font-size: 13px !important; }
.accordion-header { background: #1a4a2e !important; color: #c8a84b !important; }
footer { display: none !important; }
"""

HEADER_HTML = """
<div class="main-header">
  <h1>🐂 MINOTAUROS AGRICULTURAL INTELLIGENCE</h1>
  <p>Real Estate Beyond RGB · EnMap Hyperspectral Analysis · Agricultural Land Investment · Greece</p>
</div>
"""

DISCLAIMER_HTML = """
<div style="background:#fffbe6;border:1px solid #c8a84b;border-radius:8px;
            padding:10px 16px;font-size:12px;color:#5a3e1b;margin-top:6px;">
  ⚠️ <b>Disclaimer:</b> pH values are spectral proxies — not laboratory measurements.
  EnMap indices are used for preliminary screening only. Financial projections are scenario-based
  and do not constitute guaranteed returns. Always validate with field surveys before investing.
</div>"""

# ── Build Gradio app ───────────────────────────────────────────────────────────
with gr.Blocks(css=CSS, title="Minotauros Agricultural Intelligence") as demo:

    context_state      = gr.State("{}")
    chat_history_state = gr.State([])

    gr.HTML(HEADER_HTML)

    with gr.Tabs():

        # ── TAB 1: INVESTMENT RANKER ─────────────────────────────────────────
        with gr.Tab("📊 Investment Ranker"):

            with gr.Row():
                t1_plot     = gr.Dropdown(PLOT_NAMES, value="All plots", label="Location / Plot", scale=2)
                t1_risk     = gr.Dropdown(["low", "medium", "high"], value="medium", label="Risk Tolerance", scale=1)
                t1_scenario = gr.Dropdown(SCENARIO_LABELS, value="Base", label="Price Scenario", scale=1)
                t1_capital  = gr.Number(value=1_000_000, label="Available Capital (€)", minimum=0, scale=2)
                t1_feasible = gr.Checkbox(label="Feasible only", value=False, scale=1)

            t1_kpi = gr.HTML()

            with gr.Row():
                t1_fig_cum = gr.Plot(label="Cumulative Cashflow")
                t1_fig_bar = gr.Plot(label="Annual Cashflow")

            t1_crop = gr.Dropdown(
                choices=CROP_NAMES,
                value=CROP_NAMES[0],
                label="🌿 Select crop to inspect charts",
            )

            with gr.Accordion("📋 Full Ranked Table", open=False):
                t1_table = gr.Dataframe(interactive=False, wrap=True)

            gr.HTML(DISCLAIMER_HTML)

            t1_inputs  = [t1_plot, t1_risk, t1_scenario, t1_capital, t1_feasible, t1_crop]
            t1_outputs = [t1_fig_cum, t1_fig_bar, t1_table, t1_kpi, t1_crop, context_state]

            for comp in [t1_plot, t1_risk, t1_scenario, t1_capital, t1_feasible]:
                comp.change(tab1_cb, inputs=t1_inputs, outputs=t1_outputs)
            t1_crop.change(tab1_cb, inputs=t1_inputs, outputs=t1_outputs)

        # ── TAB 2: PLOT COMPARISON ────────────────────────────────────────────
        with gr.Tab("🗺️ Plot Comparison"):

            with gr.Row():
                t2_crop     = gr.Dropdown(CROP_NAMES, value=CROP_NAMES[0], label="Crop to Compare", scale=2)
                t2_scenario = gr.Dropdown(SCENARIO_LABELS, value="Base", label="Price Scenario", scale=1)
                t2_risk     = gr.Dropdown(["low", "medium", "high"], value="medium", label="Risk Tolerance", scale=1)

            t2_cards = gr.HTML()

            with gr.Row():
                t2_fig_npv  = gr.Plot(label="NPV by Plot")
                t2_fig_suit = gr.Plot(label="Suitability Components by Plot")

            with gr.Accordion("📋 Detailed Comparison Table", open=False):
                t2_table = gr.Dataframe(interactive=False, wrap=True)

            gr.HTML(DISCLAIMER_HTML)

            t2_inputs  = [t2_crop, t2_scenario, t2_risk]
            t2_outputs = [t2_fig_npv, t2_fig_suit, t2_table, t2_cards, context_state]

            for comp in [t2_crop, t2_scenario, t2_risk]:
                comp.change(tab2_cb, inputs=t2_inputs, outputs=t2_outputs)

    # ── MINOTAUROS CHATBOT ────────────────────────────────────────────────────
    with gr.Accordion("🐂 Ask Minotauros AI — Context-aware investment assistant", open=False):
        gr.Markdown(
            "**Minotauros** reads your current dashboard view and answers questions "
            "about crops, plots, NPV, IRR, suitability scores, or investment strategy. "
            "Switch tabs or change filters, then ask away.",
            elem_classes=["chatbot-hint"],
        )

        chatbot = gr.Chatbot(
            label="Minotauros",
            height=380,
        )

        with gr.Row():
            chat_input = gr.Textbox(
                placeholder="e.g. Why is pistachio ranked first? What is the IRR for Arkadia?",
                label="",
                scale=5,
                container=False,
            )
            send_btn = gr.Button("Send ➤", variant="primary", scale=1)

        with gr.Accordion("⚙️ Gemini API Key", open=False):
            gemini_key = gr.Textbox(
                label="Gemini API Key",
                placeholder="AIza... (or set GEMINI_API_KEY env var)",
                type="password",
                info="Your key is used only for this session and never stored.",
            )

        def _clear_input():
            return ""

        send_btn.click(
            minotauros_chat,
            inputs=[chat_input, chat_history_state, context_state, gemini_key],
            outputs=[chatbot, chat_history_state],
        ).then(_clear_input, None, chat_input)

        chat_input.submit(
            minotauros_chat,
            inputs=[chat_input, chat_history_state, context_state, gemini_key],
            outputs=[chatbot, chat_history_state],
        ).then(_clear_input, None, chat_input)

    # ── Auto-load both tabs on page open ──────────────────────────────────────
    demo.load(tab1_cb, inputs=t1_inputs, outputs=t1_outputs)
    demo.load(tab2_cb, inputs=t2_inputs, outputs=t2_outputs)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
