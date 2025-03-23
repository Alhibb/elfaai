import streamlit as st
import asyncio
import json
import os
import datetime
from agentipy.agent import SolanaAgentKit
from agentipy.langchain.elfaai import get_elfaai_tools

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="Elfa AI Crypto Analysis Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar: Information Panel about AgentiPy Tools ---
st.sidebar.header("📌 About AgentiPy")
st.sidebar.info(
    "**AgentiPy** is an AI-driven agent toolkit for blockchain applications. " 
    "It streamlines decentralized app development by combining asynchronous operations " 
    "with powerful AI analytics. In this dashboard, we use Elfa AI tools to fetch crypto " 
    "mentions, trending tokens, and Twitter stats for insightful blockchain analysis."
)
st.sidebar.markdown("### 🔗 More Examples")
st.sidebar.markdown("[GitHub: AgentiPy Examples](https://github.com/niceberginc/agentipy/tree/main/examples)")
st.sidebar.markdown("### Tools in This Dashboard")
st.sidebar.markdown(
    "- **Smart Mentions**: Retrieves smart mentions from various sources.  \n"
    "- **Top Mentions by Ticker**: Analyzes the most-discussed tokens for a given ticker.  \n"
    "- **Search Mentions by Keywords**: Finds mentions based on keywords over a date range.  \n"
    "- **Trending Tokens**: Identifies top-trending tokens based on activity.  \n"
    "- **Twitter Stats**: Retrieves key Twitter metrics for crypto accounts."
)

# --- Custom CSS: Modern UI styling with animations and icons ---
st.markdown(
    """
    <!-- Load Google Fonts and FontAwesome for icons -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"
          integrity="sha512-HHsOCz8a2hG7Bw3nxDJ7TjT5jXGZNp1P8A1c6b+N9u/3Yg3i82DRL1wL5q+D/sR60QYKc57C7+MWLl1N9OZ8fg=="
          crossorigin="anonymous" referrerpolicy="no-referrer" />
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f0f2f6;
        color: #333;
    }
    /* Card styling with fade-in animation */
    .card {
        background: #fff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        opacity: 0;
        animation: fadeIn 0.8s forwards;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    /* Card header with icon */
    .card-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    /* Button styling with hover effect */
    .stButton>button {
        background-color: #4e73df;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 1rem;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2e59d9;
        transform: scale(1.02);
    }
    /* Spinner animation */
    .spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #4e73df;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: auto;
    }
    /* Keyframe animations */
    @keyframes fadeIn {
        to { opacity: 1; }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialization: Using environment variables for private keys ---
@st.cache_resource(show_spinner=False)
def init_solana():
    try:
        # Retrieve keys securely from environment variables
        solana_kit = SolanaAgentKit(
            private_key=os.getenv("SOLANA_PRIVATE_KEY"),
            elfa_ai_api_key=os.getenv("ELFA_AI_API_KEY")
        )
        return solana_kit, get_elfaai_tools(solana_kit)
    except Exception as e:
        st.error(f"Error initializing AgentiPy: {e}")
        return None, None

solana_kit, tools = init_solana()
if solana_kit is None:
    st.stop()

# --- Main Content ---
st.title("Elfa AI Crypto Analysis Dashboard")
st.write("Leverage AI to track trending tokens, analyze mentions, and get real-time insights.")

# Analysis option selector
analysis_option = st.selectbox(
    "Choose an analysis option:",
    ("Get Smart Mentions", "Get Top Mentions by Ticker", "Search Mentions by Keywords", "Get Trending Tokens", "Get Twitter Stats")
)

def run_async(coro):
    return asyncio.run(coro)

# --- Analysis Forms with Animated Cards ---
if analysis_option == "Get Smart Mentions":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-header"><i class="fa fa-lightbulb"></i> Get Smart Mentions</div>',
            unsafe_allow_html=True
        )
        limit = st.number_input("Number of smart mentions", min_value=1, value=5, step=1)
        offset = st.number_input("Offset", min_value=0, value=0, step=1)
        if st.button("Run Smart Mentions", key="smart_mentions"):
            with st.spinner("Fetching Smart Mentions..."):
                smart_mentions_input = json.dumps({"limit": int(limit), "offset": int(offset)})
                tool = next((t for t in tools if t.name == "elfa_ai_get_smart_mentions"), None)
                if tool:
                    result = run_async(tool._arun(smart_mentions_input))
                    st.json(result)
                else:
                    st.error("Smart Mentions tool not found.")
        st.markdown('</div>', unsafe_allow_html=True)

elif analysis_option == "Get Top Mentions by Ticker":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-header"><i class="fa fa-chart-line"></i> Get Top Mentions by Ticker</div>',
            unsafe_allow_html=True
        )
        ticker = st.text_input("Token Ticker", value="SOL")
        time_window = st.text_input("Time Window", value="1h")
        page = st.number_input("Page Number", min_value=1, value=1, step=1)
        page_size = st.number_input("Page Size", min_value=1, value=5, step=1)
        include_details = st.checkbox("Include Account Details")
        if st.button("Run Top Mentions", key="top_mentions"):
            with st.spinner("Fetching Top Mentions..."):
                top_mentions_input = json.dumps({
                    "ticker": ticker,
                    "time_window": time_window,
                    "page": int(page),
                    "page_size": int(page_size),
                    "include_account_details": include_details
                })
                tool = next((t for t in tools if t.name == "elfa_ai_get_top_mentions_by_ticker"), None)
                if tool:
                    result = run_async(tool._arun(top_mentions_input))
                    st.json(result)
                else:
                    st.error("Top Mentions tool not found.")
        st.markdown('</div>', unsafe_allow_html=True)

elif analysis_option == "Search Mentions by Keywords":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-header"><i class="fa fa-search"></i> Search Mentions by Keywords</div>',
            unsafe_allow_html=True
        )
        keywords = st.text_input("Keywords")
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=1))
        with col2:
            to_date = st.date_input("End Date", value=datetime.date.today())
        limit_input = st.number_input("Number of results (min 20, max 30)", min_value=1, value=5, step=1)
        if st.button("Run Search", key="search_mentions"):
            with st.spinner("Searching mentions..."):
                try:
                    from_ts = int(datetime.datetime.combine(from_date, datetime.time()).timestamp())
                    to_ts = int(datetime.datetime.combine(to_date, datetime.time()).timestamp())
                except Exception as e:
                    st.error(f"Date error: {e}")
                    st.stop()
                one_day = 86400
                thirty_days = 30 * one_day
                if not (one_day <= (to_ts - from_ts) <= thirty_days):
                    st.error("Error: Date range must be between 1 and 30 days.")
                else:
                    requested_limit = int(limit_input)
                    if requested_limit < 20:
                        st.info("Limit below minimum; using 20.")
                        requested_limit = 20
                    elif requested_limit > 30:
                        st.info("Limit above maximum; using 30.")
                        requested_limit = 30
                    search_mentions_input = json.dumps({
                        "keywords": keywords,
                        "from_timestamp": from_ts,
                        "to_timestamp": to_ts,
                        "limit": requested_limit,
                        "cursor": ""
                    })
                    tool = next((t for t in tools if t.name == "elfa_ai_search_mentions_by_keywords"), None)
                    if tool:
                        result = run_async(tool._arun(search_mentions_input))
                        st.json(result)
                    else:
                        st.error("Search Mentions tool not found.")
        st.markdown('</div>', unsafe_allow_html=True)

elif analysis_option == "Get Trending Tokens":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-header"><i class="fa fa-fire"></i> Get Trending Tokens</div>',
            unsafe_allow_html=True
        )
        time_window = st.text_input("Time Window", value="24h")
        page = st.number_input("Page Number", min_value=1, value=1, step=1)
        page_size = st.number_input("Number of Tokens", min_value=1, value=10, step=1)
        min_mentions = st.number_input("Minimum Mentions", min_value=1, value=5, step=1)
        if st.button("Run Trending Tokens", key="trending_tokens"):
            with st.spinner("Fetching Trending Tokens..."):
                trending_tokens_input = json.dumps({
                    "time_window": time_window,
                    "page": int(page),
                    "page_size": int(page_size),
                    "min_mentions": int(min_mentions)
                })
                tool = next((t for t in tools if t.name == "elfa_ai_get_trending_tokens"), None)
                if tool:
                    result = run_async(tool._arun(trending_tokens_input))
                    st.json(result)
                else:
                    st.error("Trending Tokens tool not found.")
        st.markdown('</div>', unsafe_allow_html=True)

elif analysis_option == "Get Twitter Stats":
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-header"><i class="fa fa-twitter"></i> Get Twitter Stats</div>',
            unsafe_allow_html=True
        )
        username = st.text_input("Twitter Username")
        if st.button("Run Twitter Stats", key="twitter_stats"):
            with st.spinner("Fetching Twitter Stats..."):
                twitter_stats_input = json.dumps({"username": username})
                tool = next((t for t in tools if t.name == "elfa_ai_get_smart_twitter_account_stats"), None)
                if tool:
                    result = run_async(tool._arun(twitter_stats_input))
                    st.json(result)
                else:
                    st.error("Twitter Stats tool not found.")
        st.markdown('</div>', unsafe_allow_html=True)
