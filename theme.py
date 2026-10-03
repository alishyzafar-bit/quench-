import streamlit as st


def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --bg: #F4F1EA;
      --surface: #FFFFFF;
      --surface-2: #F8F6F1;
      --surface-3: #EEF2F1;
      --line: #D9DED9;
      --text: #182126;
      --muted: #68747A;
      --orange: #E85D2A;
      --amber: #F3A33B;
      --teal: #1597A8;
      --teal-soft: #DDF2F4;
      --danger: #C94A3A;
      --shadow: 0 12px 35px rgba(24,33,38,.07);
    }

    .stApp {
      background:
        radial-gradient(circle at 8% 5%, rgba(243,163,59,.12), transparent 24%),
        radial-gradient(circle at 92% 18%, rgba(21,151,168,.10), transparent 24%),
        var(--bg);
      color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(244,241,234,.82); }
    .block-container { max-width: 1380px; padding-top: 1.4rem; padding-bottom: 4rem; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--text); }
    h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif; color: var(--text); letter-spacing: -.03em; }

    .hero {
      position: relative;
      overflow: hidden;
      padding: 3rem 3.2rem 2.7rem;
      border: 1px solid var(--line);
      border-radius: 28px;
      background:
        radial-gradient(circle at 88% 30%, rgba(21,151,168,.15), transparent 28%),
        radial-gradient(circle at 68% 120%, rgba(232,93,42,.18), transparent 36%),
        linear-gradient(135deg, #FFFFFF 0%, #F8F6F1 100%);
      margin-bottom: 1.2rem;
      box-shadow: var(--shadow);
    }
    .hero::after {
      content:""; position:absolute; width:220px; height:220px; right:-75px; bottom:-105px;
      border: 34px solid rgba(232,93,42,.08); border-radius:50%;
    }
    .hero-kicker { color: var(--orange); font-size: .70rem; font-weight: 800; letter-spacing: .18em; }
    .hero h1 { font-size: 3.5rem; line-height: .98; margin: .45rem 0 .7rem; }
    .hero h1 span { color: var(--orange); }
    .hero h1 small { color: var(--muted); font-size: 1rem; font-family: 'DM Sans'; vertical-align: middle; }
    .hero p { color: var(--muted); margin: 0; max-width: 720px; font-size: 1rem; line-height: 1.6; }
    .hero-tagline { margin-top: 1.15rem; font-family:'Space Grotesk'; font-weight:700; color:var(--text); letter-spacing:.02em; }

    .section-label { color: var(--muted); font-size: .68rem; font-weight: 800; letter-spacing: .16em; margin: 1rem 0 .65rem; }
    .section-label::before { content:""; display:inline-block; width:22px; height:3px; background:var(--orange); margin:0 8px 3px 0; border-radius:3px; }
    [data-testid="stHorizontalBlock"] { gap: .8rem; }

    .metric-card {
      border: 1px solid var(--line); border-radius: 18px; padding: 1.05rem 1.1rem;
      background: var(--surface); min-height: 100px; position:relative; overflow:hidden; box-shadow: 0 5px 18px rgba(24,33,38,.045);
    }
    .metric-card::after { content:""; position:absolute; width:74px; height:74px; border-radius:50%; right:-34px; top:-34px; background:rgba(21,151,168,.06); }
    .metric-label { color: var(--muted); font-size: .62rem; letter-spacing: .11em; font-weight: 800; }
    .metric-value { font-family:'Space Grotesk'; font-size: 1.32rem; margin-top:.48rem; color:var(--text); }
    .metric-card.gold { border-top: 3px solid var(--amber); }
    .metric-card.violet { border-top: 3px solid var(--teal); }
    .metric-card.green { border-top: 3px solid var(--teal); }
    .metric-card.rose { border-top: 3px solid var(--orange); }
    .metric-card.phase { border-top: 3px solid var(--orange); }

    .panel-title { font-family:'Space Grotesk'; font-weight:700; font-size:1.08rem; margin-top:.6rem; color:var(--text); }
    .phase-note, .method-note, .limit-card, .why-card {
      border: 1px solid var(--line); background: var(--surface);
      border-radius: 16px; padding: 1rem 1.05rem; color: var(--muted);
      font-size: .86rem; line-height:1.58; box-shadow:0 5px 18px rgba(24,33,38,.04);
    }
    .method-note { margin-top: 1.2rem; border-left: 4px solid var(--orange); }
    .limit-card { border-left: 4px solid var(--teal); }
    .why-card { background: linear-gradient(135deg,#fff,#F7FBFA); }
    .phase-note b, .method-note b, .limit-card b, .why-card b { color: var(--text); }
    .scope-strip {
      border:1px solid rgba(232,93,42,.24); background:rgba(232,93,42,.065);
      color:var(--muted); border-radius:13px; padding:.78rem 1rem;
      font-size:.79rem; margin:.65rem 0 1rem;
    }
    .scope-strip b { color:var(--text); }
    .muted { color:var(--muted); }
    .change-strip {
      border:1px solid rgba(21,151,168,.25); background:var(--teal-soft); color:var(--text);
      border-radius:14px; padding:.9rem 1rem; margin:.9rem 0;
    }

    .stTabs [data-baseweb="tab-list"] { gap: .45rem; background: transparent; }
    .stTabs [data-baseweb="tab"] {
      background: rgba(255,255,255,.7); border:1px solid var(--line); border-radius: 12px;
      color: var(--muted); padding: .62rem 1rem; font-weight:600;
    }
    .stTabs [aria-selected="true"] { color: var(--text); border-color:var(--orange); background:var(--surface); box-shadow:0 4px 14px rgba(24,33,38,.06); }

    div.stButton > button, div.stDownloadButton > button {
      border-radius: 12px; border:1px solid var(--line); background:var(--text);
      color:#FFFFFF; font-weight:700; min-height:44px; transition:.18s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
      border-color:var(--orange); background:var(--orange); color:#FFFFFF; transform:translateY(-1px);
    }
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background:var(--orange); }
    [data-testid="stProgress"] > div > div { background:var(--orange); }
    .stCaption, [data-testid="stMarkdownContainer"] p { color: var(--muted); }

    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
      background:var(--surface); border-color:var(--line); border-radius:11px;
    }
    [data-testid="stExpander"] { border:1px solid var(--line); border-radius:14px; background:rgba(255,255,255,.65); }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; overflow:hidden; }
    </style>
    """, unsafe_allow_html=True)
