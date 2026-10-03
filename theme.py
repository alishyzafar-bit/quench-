import streamlit as st

def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --bg: #080A0F;
      --surface: #10141C;
      --surface-2: #151A24;
      --line: #252C38;
      --text: #F4F1EA;
      --muted: #9299A8;
      --gold: #F5B942;
      --gold-soft: #D99B2B;
      --violet: #8B7CF6;
      --mint: #55D6BE;
      --rose: #F07C8E;
    }

    .stApp { background: var(--bg); color: var(--text); }
    [data-testid="stHeader"] { background: rgba(8,10,15,.88); }
    .block-container { max-width: 1380px; padding-top: 2rem; padding-bottom: 3rem; }

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -.025em; }

    .hero {
      padding: 2.2rem 2.4rem 2rem;
      border: 1px solid var(--line);
      border-radius: 24px;
      background:
        radial-gradient(circle at 85% 20%, rgba(139,124,246,.13), transparent 32%),
        radial-gradient(circle at 15% 90%, rgba(245,185,66,.08), transparent 30%),
        var(--surface);
      margin-bottom: 1.4rem;
    }
    .hero-kicker { color: var(--gold); font-size: .72rem; font-weight: 700; letter-spacing: .16em; }
    .hero h1 { font-size: 3rem; margin: .3rem 0 .25rem; }
    .hero h1 span { color: var(--gold); }
    .hero h1 small { color: var(--muted); font-size: 1rem; font-family: 'DM Sans'; }
    .hero p { color: var(--muted); margin: 0; max-width: 720px; }

    .section-label { color: var(--muted); font-size: .68rem; font-weight: 700; letter-spacing: .16em; margin: .9rem 0 .7rem; }

    [data-testid="stHorizontalBlock"] { gap: .8rem; }
    div[data-testid="stVerticalBlock"] > div:has(> div.metric-card) { height: 100%; }

    .metric-card {
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 1rem 1.05rem;
      background: var(--surface);
      min-height: 92px;
      position: relative;
      overflow: hidden;
    }
    .metric-card::after { content:""; position:absolute; width:70px; height:70px; border-radius:50%; right:-32px; top:-32px; background:rgba(255,255,255,.025); }
    .metric-label { color: var(--muted); font-size: .65rem; letter-spacing: .1em; font-weight: 700; }
    .metric-value { font-family:'Space Grotesk'; font-size: 1.25rem; margin-top:.45rem; }
    .metric-card.gold { border-top: 2px solid var(--gold); }
    .metric-card.violet { border-top: 2px solid var(--violet); }
    .metric-card.green { border-top: 2px solid var(--mint); }
    .metric-card.rose { border-top: 2px solid var(--rose); }
    .metric-card.phase { border-top: 2px solid #A99CFF; }

    .panel-title { font-family:'Space Grotesk'; font-weight:600; font-size:1.05rem; margin-top:.6rem; }
    .phase-note, .method-note {
      border: 1px solid var(--line); background: var(--surface);
      border-radius: 14px; padding: .95rem 1rem; color: var(--muted);
      font-size: .86rem; line-height:1.55;
    }
    .method-note { margin-top: 1.2rem; border-left: 3px solid var(--gold); }
    .phase-note b, .method-note b { color: var(--text); }
    .scope-strip {
      border:1px solid rgba(245,185,66,.24); background:rgba(245,185,66,.055);
      color:var(--muted); border-radius:12px; padding:.75rem .95rem;
      font-size:.78rem; margin:.65rem 0 1rem;
    }
    .scope-strip b { color:var(--text); }
    .muted { color:var(--muted); }

    .stTabs [data-baseweb="tab-list"] { gap: .35rem; background: transparent; }
    .stTabs [data-baseweb="tab"] {
      background: var(--surface); border:1px solid var(--line); border-radius: 10px;
      color: var(--muted); padding: .55rem 1rem;
    }
    .stTabs [aria-selected="true"] { color: var(--text); border-color: #3A4251; background:var(--surface-2); }

    div.stButton > button, div.stDownloadButton > button {
      border-radius: 10px; border:1px solid var(--line); background:var(--surface-2);
      color:var(--text); font-weight:600; min-height:42px;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
      border-color: var(--gold); color:var(--gold); background:var(--surface-2);
    }

    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background:var(--gold); }
    [data-testid="stProgress"] > div > div { background:var(--gold); }
    .stCaption, [data-testid="stMarkdownContainer"] p { color: var(--muted); }
    </style>
    """, unsafe_allow_html=True)
