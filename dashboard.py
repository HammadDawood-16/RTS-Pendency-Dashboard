import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import altair as alt
import gdown
import datetime
import urllib.parse
import io

# Set page configuration
st.set_page_config(page_title="RTS Pendency Dashboard", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* --- THEME ACCENT COLOR OVERRIDE (#1a7b6b) FOR BOTH THEMES --- */
    
    /* 1. Checkboxes (checked state) */
    div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] div[aria-checked="true"] {
        background-color: #1a7b6b !important;
        border-color: #1a7b6b !important;
    }
    /* 2. Active Tabs (underline and text) */
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom-color: #1a7b6b !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #1a7b6b !important;
    }
    /* 3. Text Inputs & Search Bars (focus border) */
    div[data-baseweb="input"]:focus-within {
        border-color: #1a7b6b !important;
    }
    /* 4. Popover & Tertiary Buttons (hover/active text and border) */
    div[data-testid="stPopover"] button[aria-expanded="true"],
    button[kind="tertiary"]:hover,
    button[kind="tertiary"]:active {
        border-color: #1a7b6b !important;
        color: #1a7b6b !important;
    }
    button[kind="tertiary"]:hover *,
    button[kind="tertiary"]:active * {
        color: #1a7b6b !important;
    }

    /* Hide the marker's container to fix vertical alignment */
    .element-container:has(.mail-btn-marker) {
        display: none !important;
    }

    /* Style for both download and link buttons to make them matching pills */
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stLinkButton"] a,
    .element-container:has(.mail-btn-marker) + .element-container button[kind="secondary"] {
        border-radius: 50px !important;
        padding: 0.5rem 1.8rem !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: 2px solid #1a7b6b !important;
        background-color: transparent !important;
        color: #1a7b6b !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    div[data-testid="stDownloadButton"] button:hover,
    div[data-testid="stLinkButton"] a:hover,
    .element-container:has(.mail-btn-marker) + .element-container button[kind="secondary"]:hover {
        background-color: #1a7b6b !important;
        color: white !important;
        text-decoration: none !important;
    }
    /* Force text/spans inside the link button to inherit matching colors */
    div[data-testid="stLinkButton"] a *,
    .element-container:has(.mail-btn-marker) + .element-container button[kind="secondary"] * {
        color: inherit !important;
        text-decoration: none !important;
    }

    /* Fix the height and breadth of the multiselect boxes and enable scrolling */
    .stMultiSelect div[data-baseweb="select"] {
        height: 85px !important;
        max-height: 85px !important;
        width: 220px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
    }
    /* Force text wrapping inside the multiselect chips and dropdown options */
    .stMultiSelect span, .stMultiSelect div[data-baseweb="tag"] {
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }
    /* Force text wrapping inside the dropdown menu list items */
    ul[data-baseweb="menu"] li {
        white-space: normal !important;
        word-wrap: break-word !important;
    }

    /* BRUTE-FORCE METRIC CONTAINER (PILL) SIZING */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        height: fit-content !important;    /* Shrink wrap to text height */
        min-height: 0 !important;
        width: fit-content !important;     /* Shrink wrap the text strictly */
        min-width: 0 !important;           /* Allow it to shrink fully */
        margin: 0 auto !important;         /* Center the entire pill horizontally */
        padding: 8px 16px !important;      /* Restore padding for larger text */
        border-radius: 50px !important;    /* Full pill rounded corners */
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;       /* Keep the hover effect inside rounded corners */
        cursor: pointer !important;
    }
    /* Stack the text vertically since the eye is now an overlay */
    div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;                 /* Remove gap */
        padding: 0 !important;             /* Destroy hidden inner spacing */
        display: flex !important;
        flex-direction: column !important; /* Stack text properly */
        justify-content: center !important; 
        align-items: center !important;
        height: fit-content !important;
        width: fit-content !important;
    }
    /* STOP STREAMLIT'S HIDDEN CONTAINERS FROM STRETCHING */
    div[data-testid="stVerticalBlockBorderWrapper"] .element-container {
        width: fit-content !important;
        height: fit-content !important;
        flex: 0 0 auto !important;         /* Do not grow or stretch */
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Style the new text-based metric label */
    div[data-testid="stVerticalBlockBorderWrapper"] p.metric-label,
    html body p.metric-label,
    .stMarkdown p.metric-label {
        font-size: 28px !important;
        line-height: 1.2 !important;
        margin: 0 !important;
        opacity: 0.8 !important;
        text-align: center !important;
        font-weight: bold !important;
    }
    
    /* --- METRIC NUMBER STYLING --- */
    /* Target ONLY the metric buttons by making them the only Primary buttons on the dashboard */
    button[kind="primary"] {
        height: auto !important;
        min-height: 0 !important;
        padding: 5px 0 !important;
        overflow: visible !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important; /* Inherit the adaptive Light/Dark text color */
    }
    button[kind="primary"]:hover,
    button[kind="primary"]:focus,
    button[kind="primary"]:active {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
    }
    /* Force the huge text size with unbeatable specificity */
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] div {
        font-size: 50px !important;
        line-height: normal !important;
        margin: 0 !important;
        font-weight: 900 !important;
        color: inherit !important;
    }
    /* 4. Underline the text only when hovering the parent pill */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover button[kind="primary"] p,
    div[data-testid="stVerticalBlockBorderWrapper"]:hover button[kind="primary"] span,
    div[data-testid="stVerticalBlockBorderWrapper"]:hover button[kind="primary"] div {
        text-decoration: underline !important;
    }
    /* Add a subtle hover effect to the entire metric pill */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        background-color: rgba(128, 128, 128, 0.1) !important; /* Theme-agnostic hover for both Dark and Light mode */
    }

    /* TIGHTEN CUSTOM GRID ROWS (Scoped to Tabs to protect filters) */
    div[data-testid="stTabs"] div[data-testid="stCheckbox"] {
        padding: 0 !important;
    }
    div[data-testid="stTabs"] div[data-testid="stCheckbox"] label {
        min-height: 0 !important;
        padding-bottom: 2px !important;
        padding-top: 2px !important;
        gap: 4px !important;
    }
    /* BULLETPROOF: Hide any checkbox UI element that does NOT contain the text paragraph (Scoped to Tabs) */
    div[data-testid="stTabs"] div[data-testid="stCheckbox"] label > div:not(:has(p)),
    div[data-testid="stTabs"] div[data-testid="stCheckbox"] label > span:not(:has(p)) {
        display: none !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Embedded Logo
img_html = '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAPAAAADwCAMAAAAJixmgAAAAwFBMVEUAinHV0iYAiXIAh3MAh3LY0yPX0yTZ1CAAhXQAim/b1R4AjWzV0yAAhXIAg3QAjmwAkGrIzijByyvO0CWOtE0AkWmpwTufvEPQzys4mGR4rVKrwjqStkrAzCjKzyUllGe7yTCGs0uAr1C1xjWEqVx5pV9pomCauUhYn2BMnGIUlGdrqlNhpldQoFwhkmpko12WtU5Hn15Pm2M1lWeKrVeArlSbvEG6xTuMsVFPn1+mvEaZu0N5qVgol2RkqFRNmGeGn/EFAAAG9UlEQVR4nO2caXvaOhCFzdiWwMgJNgRCIOCENqyBpDRplqb3//+ra0izGS+SwbKtzvsdPzpodDSjTdMQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEEQBEGKABi6YUDerZAGVBvfWuOH71D9NzQb9U7Foj6nT1fGP6BZ77q08gplzfHEttXWDDPXrHxA6aD/aOgKa661aeULhLLz1rSmg5qi4bFZ2YHQptfq1pSMbbtFdwW/ah5dqqi51jZDBfuYtNm7HNbUGs9QH5EowRvNpNk7m4FKmmN6+F1ze36iK6PZ7oeP4UBstxcnthq2rZ+xRMEbzdagd90wFNAM3ZBpKUKz01FAMyydONf6AqGW21nVS6651ktwrR3N46tamUtJHtcKaGbueKKXNiXhdK2g5tObyVE5NfO7VlCzc9Mto2ZYDtII3mqm5611CUvJpFwrvp+9uy6Uq5/tsaBrBTX7Jca6TGVVGtf6isma7culVpbYhpc99W41m4P2fFiO8Qwn/LlWrGY26PglRhlyEqFcK0nzdaPwZZXd2cu1Apqpc397XGzN+p8DCvZt27Tc+8fjApcYMDuo4MrfEuOxDgXVDI20uVasZur1JwUtq+BgrhXQzNzWDyig5uohXSuo2Xv4YRdtetYXVkaCXzW7D+ujQmmGWYaCt5pN52ejQJrhJAPXCmq2vLtlYVJPe48KUUAz690dF2MXw37OyrW+slnR/70sgGbI0rUCmv10e77M27ehK03wq+bnRSPXsgpO3D0rRMGf+1NVvmUV9PYRbFrMdSwq9InN9Hx/W6/mpNnYI9cyK+3r7vFseuaKruib1H2+reeyGgar1IOYjm794ehj1y9EI3s7PfenNfndDD/S9rDZO9bfPqKfpVjT35RVLemaU7sWcWbGx2eMi1QLoP54Hl1O5ZaS8CudYGtuf/4KpF3jJrTyy0/D5AlO6VrEPfnSSNCCx9wEvmW5KyOqfQcnpWuZ94EmQsPdY+OGrezw5mUgeJJq9FmrYBTCsJl+SidsKiuq/Z5J0U7i7g47vbuHYtqrSRKs6Wlci45DOsRY7LFX1ezK6mIjjb+ySVjzjIc90rZLPeSLWQC/xV2LuPXQ/jBEj418QFuybAuuxBtJ++HxBztnsIsouC6+hxge0duPeSknJ3ohbWKyPeHM34u0VGiktOrmo7RsSxd2LdqKToz0dNOxOQp3hSwwvgm7VlyWYKeanNi1LJNOkWsRLzbztS/FFbMLqUXiqVjr6EN8bxh90X/Q1ytTcFUwuTSH8a2DWkdslas5lxfPGwTPaxEvqXnQEJmcTOdRrl7ftYQEJ0W0tjnVyF8rUmctWa8GU6ExZ3FMIPoL7+RkjWQud/zFEFmCI6Mqxyfta74/0XrKY7H2SCS5pD+5ItA+4xkn9OYoa3GhjYu4lRcK40yJjIvEjxI254mWw6MLuJbZ41xvg1rSVqzpTKUVDIG2CbgW/c3rqdAYxSqmXle2Pb9j8wtu8if5MIybjmk7IX/Jkuo5r2vRJ4EVZHiJdkP6LK882oX/Rg9biYShHjU5+dlzrsfW9DtOwcRZCrXTnoeWnubgj7ythjC4XcvsCPpqNWxyMp3bnOz5HeA8r8WEN4H03b2rPO35DYi9Lv5O2IZD0pfrwcmJ9ob5xvMGnc+1hCNa21ROXycnOq7lflqL27Uil2fjgLXzSTHtF+JUMd89ROKlKuX06eBNMbEWedvVK1DncS3zOV2ury89SgkhlDr/FUOvptV4XIul3eGD6mTsnDrjVXHu7fFUiDEbDomAsaEwcvnuIUrc/skeHtdKHdFFhOP2NBnlny8ckOQ3H6wzhSKap0JkLwpFNIdrmaPcM/6DkuhaVPIGUNYkvlQzyHEJKhMS3tcye4rpTdpDtBaqCdZjN+6Jo1pEbw6HxkV0WzW9Ca5lLZRKs7bE5VrEbSjXw1o1ZvOLdtTTq+nzaNcS23AoCTEv1RAnz42grIi5PR16HlwBInMttnPDQQkiXYs4RVg7PzyRL9XQG/Um4Q3wEiVY2h0buUS5FnHU7GA/psNdi94oOAlvqd6HxrSlXKH0RrhrkfN8To9JAF7CTmTQG6WWZz8DjbAK0crhuKssjJAKMeGGQ7mxO7uC6YOyEe3H9PXuIKZrdSNag+6OTZu/FNYb9uYDu1M169iy++ZDU+WIDnnzwWwr7NFayJsPjPs8eDkJvlQjenq2dATffDDbanfwzhMI4qdnywasP6fTEl/XyA1jzt4Vm+fKVsKf0OfsNaqJdT77B/T6FcTyqckoY85dQV+JPjhQNabfr4a26gb9GSjwu+cIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiAIgiDIgfgfDcNx+ZG9I8YAAAAASUVORK5CYII=" style="width: 55px; height: 55px; border-radius: 50%; object-fit: cover; margin-right: 15px; background-color: #00897b; border: 2px solid #4CAF50;">'

st.markdown(f'''
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    {img_html}
    <div style="display: flex; flex-direction: column; justify-content: center;">
        <div style="color: #4CAF50; font-weight: bold; font-size: 14px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 2px;">LM Network</div>
        <h1 style="margin: 0; padding: 0; font-size: 34px; font-weight: 700; line-height: 1.2;">RTS Pendency Dashboard</h1>
    </div>
</div>
''', unsafe_allow_html=True)

with st.sidebar:
    # Safely get the Cloud URL
    try:
        REPORT_DOWNLOAD_URL = st.secrets["REPORT_DOWNLOAD_URL"]
    except (FileNotFoundError, KeyError):
        REPORT_DOWNLOAD_URL = None

    # Safely get Mail To and Mail CC default values from secrets if they exist
    try:
        default_to = st.secrets.get("MAIL_TO", "")
        default_cc = st.secrets.get("MAIL_CC", "")
    except Exception:
        default_to = ""
        default_cc = ""

    st.markdown("---")
    st.markdown("### 📧 Mail Configuration")

    mail_to = st.text_input(
        "Mail To",
        value=default_to,
        placeholder="recipient@example.com",
        help="Default recipient address for pre-filled compose window."
    )
    mail_cc = st.text_input(
        "Mail CC",
        value=default_cc,
        placeholder="cc@example.com",
        help="Default CC address for pre-filled compose window."
    )

# --- DOWNLOAD/MAIL BUTTONS CONTAINER ---
# This container will be filled below, after filters are applied and metrics computed,
# so the downloaded files/drafts reflect the applied global filters.
btn_container = st.container()

@st.cache_data(ttl=900) # Cache expires every 15 minutes (900 seconds) to fetch fresh cloud data
def load_data(file_source, mtime=None):
    """Loads the processed data and caches it for performance."""
    try:
        # If the source is a URL (like Google Drive)
        if isinstance(file_source, str) and file_source.startswith("http"):
            temp_file = "temp_cloud_report.xlsx"
            # gdown automatically bypasses the Google Drive large file virus warning
            gdown.download(file_source, temp_file, quiet=True)
            df = pd.read_excel(temp_file, sheet_name="Processed Data", engine="calamine")
        else:
            # Explicitly read the 'Processed Data' tab where the script writes the output
            df = pd.read_excel(file_source, sheet_name="Processed Data", engine="calamine")
            
        # Ensure PyArrow compatibility by converting mixed-type object columns to strings
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)
            
        return df
    except Exception as e:
        st.error(f"Could not load data. Ensure the file has a 'Processed Data' sheet. Error: {e}")
        return pd.DataFrame()

file_path = "Final_ZOHO_Report.xlsx"
if os.path.exists(file_path):
    df = load_data(file_path, os.path.getmtime(file_path))
elif REPORT_DOWNLOAD_URL:
    try:
        df = load_data(REPORT_DOWNLOAD_URL)
    except Exception as e:
        st.error(f"Could not load data from cloud storage. Ensure the Google Drive link is correct. Error: {e}")
        df = pd.DataFrame()
else:
    st.info("👈 Please ensure 'Final_ZOHO_Report.xlsx' exists locally or a valid REPORT_DOWNLOAD_URL is configured in Streamlit Secrets.")
    df = pd.DataFrame()

if not df.empty:
    # --- TOP FILTERS ---
    with st.expander("Global Filters", expanded=True):
        filter_configs = [
            ("Hub Name", "current_hub"),
            ("Hub Type", "Hub Type"),
            ("State Head", "State Head"),
            ("LM State Head", "LM State Head"),
            ("SZM", "SZM"),
            ("CT", "CT"),
            ("POD", "POD Zone"),
            ("Picked Month", "picked_month"),
            ("HOV", "HOV")
        ]
        
        def reset_filters():
            st.session_state["universal_search_input"] = ""
            for label, _ in filter_configs:
                state_key = f"filter_state_{label}"
                st.session_state[state_key] = {"all": True, "items": set()}
                keys_to_delete = [k for k in st.session_state.keys() if k.startswith(f"item_cb_{label}_") or k == f"all_cb_{label}" or k == f"search_{label}"]
                for k in keys_to_delete:
                    del st.session_state[k]
                    
        col_search, col_reset = st.columns([0.9, 0.1])
        with col_search:
            universal_search = st.text_input("🔍 Universal Search", placeholder="Search for any value across all columns...", label_visibility="collapsed", key="universal_search_input")
        with col_reset:
            st.button("🔄 Reset", on_click=reset_filters, use_container_width=True)

        if universal_search:
            mask = df.astype(str).apply(lambda col: col.str.contains(universal_search, case=False, na=False, regex=False)).any(axis=1)
            df = df[mask]
        
        # Distribute the filters cleanly across columns (side by side)
        cols = st.columns(len(filter_configs))
        
        # Bulletproof Callbacks defined OUTSIDE the loop
        def toggle_all(cb_key, s_key, current_options, label):
            is_all = st.session_state[cb_key]
            st.session_state[s_key]["all"] = is_all
            # Unconditionally clear items to guarantee perfect Select/Unselect All toggling
            st.session_state[s_key]["items"] = set()
            # Force update the UI state for all individual checkboxes
            for opt in current_options:
                st.session_state[f"item_cb_{label}_{opt}"] = is_all

        def toggle_item(item, cb_key, current_options, s_key, all_cb_key):
            is_checked = st.session_state[cb_key]
            if st.session_state[s_key]["all"]:
                st.session_state[s_key]["all"] = False
                st.session_state[s_key]["items"] = set(current_options)
                st.session_state[all_cb_key] = False
                
            if is_checked:
                st.session_state[s_key]["items"].add(item)
            else:
                st.session_state[s_key]["items"].discard(item)
                
            if len(st.session_state[s_key]["items"].intersection(current_options)) == len(current_options) and len(current_options) > 0:
                st.session_state[s_key]["all"] = True
                st.session_state[s_key]["items"] = set()
                st.session_state[all_cb_key] = True

        for i, (label, col_name) in enumerate(filter_configs):
            # Fallback if POD Zone is missing but POD Mapping exists
            if label == "POD" and col_name not in df.columns and "POD Mapping" in df.columns:
                col_name = "POD Mapping"
                
            if col_name in df.columns:
                # Convert items to string to allow proper sorting
                df[col_name] = df[col_name].fillna('Unknown').astype(str)
                options = sorted(df[col_name].unique().tolist())
                with cols[i]:
                    with st.popover(label, use_container_width=True):
                        # Sticky Search Input
                        search_val = st.text_input(f"Search {label}", placeholder="Search...", key=f"search_{label}", label_visibility="collapsed")
                        
                        state_key = f"filter_state_{label}"
                        if state_key not in st.session_state:
                            st.session_state[state_key] = {"all": True, "items": set()}

                        all_cb_key = f"all_cb_{label}"
                        st.checkbox("Select All", value=st.session_state[state_key]["all"], on_change=toggle_all, args=(all_cb_key, state_key, options, label), key=all_cb_key)

                        st.markdown("<hr style='margin: 5px 0;'/>", unsafe_allow_html=True)
                        
                        for opt in options:
                            if search_val.lower() in opt.lower():
                                cb_key = f"item_cb_{label}_{opt}"
                                val = True if st.session_state[state_key]["all"] else (opt in st.session_state[state_key]["items"])
                                st.checkbox(opt, value=val, on_change=toggle_item, args=(opt, cb_key, options, state_key, all_cb_key), key=cb_key)

                    # Safely apply the filter
                    if not st.session_state[state_key]["all"]:
                        df = df[df[col_name].isin(st.session_state[state_key]["items"])]
        
    def format_indian_currency(value):
        if value >= 10_000_000:
            return f"₹ {value / 10_000_000:.1f}cr"
        elif value >= 100_000:
            return f"₹ {value / 100_000:.1f}L"
        elif value >= 1_000:
            return f"₹ {value / 1_000:.1f}k"
        return f"₹ {value:,.2f}"

    # 1. Calculate the values safely based on final data
    total_shipments = len(df)
    
    if 'debit_value' in df.columns:
        clean_debit = df['debit_value'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        debit_series = pd.to_numeric(clean_debit, errors='coerce').fillna(0)
    elif 'price' in df.columns:
        clean_price = df['price'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        debit_series = pd.to_numeric(clean_price, errors='coerce').fillna(0)
    else:
        debit_series = pd.Series([0] * len(df))
        
    total_debit = debit_series.sum()
    hov_count = (debit_series >= 1000).sum()
    
    if 'ageing_from_received' in df.columns:
        clean_ageing = df['ageing_from_received'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        ageing_series = pd.to_numeric(clean_ageing, errors='coerce').fillna(0)
    else:
        ageing_series = pd.Series([0] * len(df))
        
    ageing_5_plus = (ageing_series > 5).sum()
    ageing_hov_count = ((ageing_series > 5) & (debit_series >= 1000)).sum()
    
    if 'order_status' in df.columns and 'LSA' in df.columns:
        ofd_d0_mask = (df['order_status'].astype(str).str.strip().str.upper() == 'OUT_FOR_DELIVERY') & (pd.to_numeric(df['LSA'], errors='coerce').fillna(0) > 0)
        ofd_d0_count = ofd_d0_mask.sum()
        ofd_d0_df = df[ofd_d0_mask]
        
        ofd_live_mask = (df['order_status'].astype(str).str.strip().str.upper() == 'OUT_FOR_DELIVERY') & (pd.to_numeric(df['LSA'], errors='coerce').fillna(0) == 0)
        ofd_live_count = ofd_live_mask.sum()
        ofd_live_df = df[ofd_live_mask]
    else:
        ofd_d0_count = 0
        ofd_d0_df = df.iloc[0:0]
        ofd_live_count = 0
        ofd_live_df = df.iloc[0:0]

    @st.dialog("Data Preview", width="large")
    def show_data_preview(title, data_subset):
        st.write(f"Showing all {len(data_subset):,} records for: **{title}**")
        st.dataframe(data_subset, use_container_width=True, hide_index=True)

    # Cached generator for CSV file from filtered dataframe to prevent heavy recalculations on rerun
    @st.cache_data(show_spinner="Preparing CSV file...", hash_funcs={pd.DataFrame: lambda d: (d.shape, d.iloc[0, 0] if len(d) > 0 else None, d.iloc[-1, 0] if len(d) > 0 else None)})
    def generate_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')

    # Populate the buttons container defined at the top
    with btn_container:
        _, btn_col1, btn_col2 = st.columns((14, 1, 1))
        with btn_col1:
            csv_data = generate_csv(df)
            st.download_button(
                label=".csv",
                data=csv_data,
                file_name="Final_ZOHO_Report.csv",
                mime="text/csv",
                help="Download the filtered report file as CSV (much faster than Excel)."
            )
        with btn_col2:
            st.markdown("<span class='mail-btn-marker'></span>", unsafe_allow_html=True)
            import smtplib
            from email.message import EmailMessage
            import io
            
            if st.button("Mail", help="Send HTML email directly via SMTP"):
                sender = st.secrets.get("GMAIL_SENDER", "")
                password = st.secrets.get("GMAIL_APP_PASSWORD", "")
                
                if not sender or not password:
                    st.error("Missing GMAIL_SENDER or GMAIL_APP_PASSWORD in secrets.")
                else:
                    with st.spinner("Sending email..."):
                        try:
                            # 1. GENERATE HTML
                            gen_date = datetime.datetime.now().strftime('%d/%m/%Y, %I:%M:%S %p').lower()
                            
                            # Pills Table
                            pills_html = f'''
                            <table style="width: 100%; border-collapse: separate; border-spacing: 10px 0;">
                              <tr>
                                <td style="background-color: #f5f5f5; border: 1px solid #ccc; padding: 15px 10px; border-radius: 5px; width: 20%;">
                                   <div style="font-size: 11px; color: #555; text-transform: uppercase;">Total Shipments</div>
                                   <div style="font-size: 18px; font-weight: bold; margin-top: 5px; color: #111;">{total_shipments:,}</div>
                                </td>
                                <td style="background-color: #fff0f0; border: 1px solid #fcc; padding: 15px 10px; border-radius: 5px; width: 20%;">
                                   <div style="font-size: 11px; color: #555; text-transform: uppercase;">Debit Value</div>
                                   <div style="font-size: 18px; font-weight: bold; margin-top: 5px; color: #d32f2f;">{format_indian_currency(total_debit)}</div>
                                </td>
                                <td style="background-color: #f0f8ff; border: 1px solid #cce; padding: 15px 10px; border-radius: 5px; width: 20%;">
                                   <div style="font-size: 11px; color: #555; text-transform: uppercase;">Overall HOV (1k+)</div>
                                   <div style="font-size: 18px; font-weight: bold; margin-top: 5px; color: #1976d2;">{hov_count:,}</div>
                                </td>
                                <td style="background-color: #fff8e1; border: 1px solid #ffe082; padding: 15px 10px; border-radius: 5px; width: 20%;">
                                   <div style="font-size: 11px; color: #555; text-transform: uppercase;">5+ Ageing</div>
                                   <div style="font-size: 18px; font-weight: bold; margin-top: 5px; color: #f57f17;">{ageing_5_plus:,}</div>
                                </td>
                                <td style="background-color: #fce4ec; border: 1px solid #f48fb1; padding: 15px 10px; border-radius: 5px; width: 20%;">
                                   <div style="font-size: 11px; color: #555; text-transform: uppercase;">5+ Ageing HOV (1k+)</div>
                                   <div style="font-size: 18px; font-weight: bold; margin-top: 5px; color: #c2185b;">{ageing_hov_count:,}</div>
                                </td>
                              </tr>
                            </table>
                            '''
                            
                            # Bucket Split Table
                            bucket_rows = ""
                            if 'bucket' in df.columns and 'debit_value' in df.columns:
                                mail_debit = pd.to_numeric(df['debit_value'], errors='coerce').fillna(0)
                                df['_temp_mail_debit'] = mail_debit
                                df['Ageing_0_2'] = ((ageing_series >= 0) & (ageing_series <= 2)).astype(int)
                                df['Ageing_3_5'] = ((ageing_series >= 3) & (ageing_series <= 5)).astype(int)
                                df['Ageing_5_plus'] = (ageing_series > 5).astype(int)
                                b_grp = df.groupby('bucket').agg(
                                    Shipments=('bucket', 'count'),
                                    Ageing_0_2=('Ageing_0_2', 'sum'),
                                    Ageing_3_5=('Ageing_3_5', 'sum'),
                                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                    Debit=('_temp_mail_debit', 'sum')
                                ).sort_values('Shipments', ascending=False)
                                for b_name, b_row in b_grp.iterrows():
                                    bucket_rows += f'''
                                    <tr style="border-bottom: 1px solid #eee;">
                                        <td style="padding: 10px 5px;">{b_name}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{b_row['Shipments']:,}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{int(b_row['Ageing_0_2']):,}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{int(b_row['Ageing_3_5']):,}</td>
                                        <td style="padding: 10px 5px; text-align: right; color: #d32f2f;">{int(b_row['Ageing_5_plus']):,}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{format_indian_currency(b_row['Debit'])}</td>
                                    </tr>
                                    '''
                            
                            # Hubs Table
                            hub_rows = ""
                            if 'current_hub' in df.columns and 'debit_value' in df.columns:
                                mail_debit = pd.to_numeric(df['debit_value'], errors='coerce').fillna(0)
                                df['_temp_mail_debit'] = mail_debit
                                h_grp = df.groupby('current_hub').agg(
                                    Shipments=('current_hub', 'count'),
                                    Ageing_0_2=('Ageing_0_2', 'sum'),
                                    Ageing_3_5=('Ageing_3_5', 'sum'),
                                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                    Debit=('_temp_mail_debit', 'sum')
                                ).sort_values('Debit', ascending=False).head(5)
                                for i, (h_name, h_row) in enumerate(h_grp.iterrows(), 1):
                                    hub_rows += f'''
                                    <tr style="border-bottom: 1px solid #eee;">
                                        <td style="padding: 10px 5px; color: #888;">{i}</td>
                                        <td style="padding: 10px 5px; font-weight: bold;">{h_name}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{h_row['Shipments']:,}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{int(h_row['Ageing_0_2']):,}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{int(h_row['Ageing_3_5']):,}</td>
                                        <td style="padding: 10px 5px; text-align: right; color: #d32f2f;">{int(h_row['Ageing_5_plus']):,}</td>
                                        <td style="padding: 10px 5px; text-align: right;">{format_indian_currency(h_row['Debit'])}</td>
                                    </tr>
                                    '''

                            html_content = f'''
                            <html>
                            <body style="font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; color: #333; padding: 20px;">
                                <h2 style="margin-top: 5px; margin-bottom: 5px;">Shadowfax - RTS Pendency Snapshot</h2>
                                <div style="color: #888; font-size: 12px; margin-bottom: 20px;">Generated {gen_date}</div>
                                
                                <hr style="border: 0; border-top: 2px solid #333; margin-bottom: 20px;" />
                                
                                {pills_html}
                                
                                <h4 style="margin-top: 40px; margin-bottom: 10px; color: #555; text-transform: uppercase; font-size: 13px; letter-spacing: 0.5px;">Bucket Split</h4>
                                <table style="width: 100%; border-collapse: collapse;">
                                    <tr style="background-color: #f9f9f9; border-bottom: 2px solid #eee; text-align: left; font-size: 12px; color: #666;">
                                        <th style="padding: 10px 5px; font-weight: normal;">BUCKET</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">COUNT</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">0-2 DAYS</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">3-5 DAYS</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">5+ DAYS</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">DEBIT</th>
                                    </tr>
                                    {bucket_rows}
                                </table>
                                
                                <h4 style="margin-top: 40px; margin-bottom: 10px; color: #555; text-transform: uppercase; font-size: 13px; letter-spacing: 0.5px;">Top 5 Hubs by Open Debit</h4>
                                <table style="width: 100%; border-collapse: collapse;">
                                    <tr style="background-color: #f9f9f9; border-bottom: 2px solid #eee; text-align: left; font-size: 12px; color: #666;">
                                        <th style="padding: 10px 5px; font-weight: normal;">#</th>
                                        <th style="padding: 10px 5px; font-weight: normal;">HUB</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">COUNT</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">0-2 DAYS</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">3-5 DAYS</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">5+ DAYS</th>
                                        <th style="padding: 10px 5px; font-weight: normal; text-align: right;">DEBIT</th>
                                    </tr>
                                    {hub_rows}
                                </table>
                                

                            </body>
                            </html>
                            '''
                            
                            # 2. CONSTRUCT EMAIL MESSAGE
                            msg = EmailMessage()
                            msg['Subject'] = f"RTS Pendency Report - {datetime.date.today().strftime('%d-%b-%Y')}"
                            msg['From'] = sender
                            msg['To'] = mail_to if mail_to else sender
                            if mail_cc:
                                msg['Cc'] = mail_cc
                            
                            msg.set_content("Please enable HTML to view this message.")
                            
                            import io
                            import zipfile
                            
                            csv_bytes = generate_csv(df)
                            csv_size_mb = len(csv_bytes) / (1024 * 1024)
                            
                            if csv_size_mb < 15:
                                msg.add_alternative(html_content, subtype='html')
                                msg.add_attachment(
                                    csv_bytes,
                                    maintype='text',
                                    subtype='csv',
                                    filename=f'RTS_Pendency_{datetime.date.today().strftime("%d-%b-%Y")}.csv'
                                )
                            else:
                                # Compress CSV to ZIP in memory since it's too large
                                zip_buffer = io.BytesIO()
                                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                    zip_file.writestr(f'RTS_Pendency_{datetime.date.today().strftime("%d-%b-%Y")}.csv', csv_bytes)
                                
                                zip_bytes = zip_buffer.getvalue()
                                zip_size_mb = len(zip_bytes) / (1024 * 1024)
                                
                                if zip_size_mb < 20:
                                    msg.add_alternative(html_content, subtype='html')
                                    msg.add_attachment(
                                        zip_bytes,
                                        maintype='application',
                                        subtype='zip',
                                        filename=f'RTS_Pendency_{datetime.date.today().strftime("%d-%b-%Y")}.zip'
                                    )
                                else:
                                    html_notice = f'''
                                    <div style="margin-top: 20px; padding: 10px; background-color: #fff3e0; border: 1px dashed #ff9800; color: #e65100; font-size: 12px; text-align: center;">
                                        ⚠️ <strong>Attachment skipped:</strong> The compressed dataset is still too large ({zip_size_mb:.1f} MB) for email. Please download it directly from the dashboard.
                                    </div>
                                    </body>
                                    </html>
                                    '''
                                    html_content = html_content.replace('</body>\n                            </html>', html_notice.strip())
                                    msg.add_alternative(html_content, subtype='html')
                            
                            # 3. SEND EMAIL
                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                smtp.login(sender, password)
                                smtp.send_message(msg)
                                
                            st.toast("Successfully Sent!", icon="✅")
                        except Exception as e:
                            st.error(f"Failed to send email: {str(e)}")



    # Prepare the dataset for hierarchy (Safely handle missing columns)
    hier_df = df.copy()
    hier_df['State Head'] = hier_df.get('State Head', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['SZM'] = hier_df.get('SZM', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['current_hub'] = hier_df.get('current_hub', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['Hub Type'] = hier_df.get('Hub Type', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    
    # Fallback if POD Zone is missing but POD Mapping exists
    if 'POD Zone' not in hier_df.columns and 'POD Mapping' in hier_df.columns:
        hier_df['POD Zone'] = hier_df['POD Mapping']
    hier_df['POD Zone'] = hier_df.get('POD Zone', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['LM State Head'] = hier_df.get('LM State Head', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['flag2'] = hier_df.get('flag2', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['bucket'] = hier_df.get('bucket', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['order_status'] = hier_df.get('order_status', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    
    # Map the safely calculated debit_series from the Overview tab
    hier_df['Debit Value Numeric'] = debit_series.values
    
    # --- MAP AGEING AND DEBIT METRICS ---
    hier_df['Ageing Numeric'] = ageing_series.values
    hier_df['Ageing_0_2'] = ((hier_df['Ageing Numeric'] >= 0) & (hier_df['Ageing Numeric'] <= 2)).astype(int)
    hier_df['Ageing_3_5'] = ((hier_df['Ageing Numeric'] >= 3) & (hier_df['Ageing Numeric'] <= 5)).astype(int)
    hier_df['Ageing_5_plus'] = (hier_df['Ageing Numeric'] > 5).astype(int)
    hier_df['Debit_5_plus'] = hier_df['Ageing_5_plus'] * hier_df['Debit Value Numeric']
    
    def get_sort_label(val_str, col, cur_col, cur_asc):
        return val_str

    # --- TABS ---
    tab_overview, tab_shszmpod, tab_hubs = st.tabs(["Overview", "State Head/SZM/POD", "Hubs"])
    
    with tab_overview:
        # 2. Display as Broad Pills in 7 Columns
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>Total Shipments</p>", unsafe_allow_html=True)
                if st.button(f"{total_shipments:,}", key="btn_total", help="Click to view Total Shipments data", type="primary", use_container_width=True):
                    show_data_preview("Total Shipments", df)
                
        with col2:
            with st.container(border=True):
                st.markdown("<p class='metric-label' style='color: #4CAF50;'>OFD (Live)</p>", unsafe_allow_html=True)
                if st.button(f"{ofd_live_count:,}", key="btn_ofd_live", help="Click to view OFD (Live) data", type="primary", use_container_width=True):
                    show_data_preview("OFD (Live)", ofd_live_df)
                    
        with col3:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>OFD (D0+)</p>", unsafe_allow_html=True)
                if st.button(f"{ofd_d0_count:,}", key="btn_ofd_d0", help="Click to view OFD (D0+) data", type="primary", use_container_width=True):
                    show_data_preview("OFD (D0+)", ofd_d0_df)
                    
        with col4:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>Debit Value</p>", unsafe_allow_html=True)
                if st.button(f"{format_indian_currency(total_debit)}", key="btn_debit", help="Click to view Debit Value data", type="primary", use_container_width=True):
                    show_data_preview("Debit Value", df)
                
        with col5:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>Overall HOV (1k+)</p>", unsafe_allow_html=True)
                if st.button(f"{hov_count:,}", key="btn_hov", help="Click to view Overall HOV (1k+) data", type="primary", use_container_width=True):
                    show_data_preview("Overall HOV (1k+)", df[debit_series >= 1000])
                
        with col6:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>5+ Ageing</p>", unsafe_allow_html=True)
                if st.button(f"{ageing_5_plus:,}", key="btn_ageing", help="Click to view 5+ Ageing data", type="primary", use_container_width=True):
                    show_data_preview("5+ Ageing", df[ageing_series > 5])
                
        with col7:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>5+ Ageing HOV (1k+)</p>", unsafe_allow_html=True)
                if st.button(f"{ageing_hov_count:,}", key="btn_ageing_hov", help="Click to view 5+ Ageing HOV (1k+) data", type="primary", use_container_width=True):
                    show_data_preview("5+ Ageing HOV (1k+)", df[(ageing_series > 5) & (debit_series >= 1000)])
    
        # --- CHARTS ---
        import inspect
        has_on_select = 'on_select' in inspect.signature(st.plotly_chart).parameters
        
        # Extract Donut chart selection from session state to cross-filter the Bar chart
        selected_flags = []
        if "pie_chart" in st.session_state:
            sel_dict = st.session_state.pie_chart.get("selection", {})
            if "leg_sel" in sel_dict and sel_dict["leg_sel"]:
                selected_flags = [item["Flag"] for item in sel_dict["leg_sel"]]
            elif "slice_sel" in sel_dict and sel_dict["slice_sel"]:
                selected_flags = [item["Flag"] for item in sel_dict["slice_sel"]]
            elif "flag_sel" in sel_dict and sel_dict["flag_sel"]: # Fallback
                selected_flags = [item["Flag"] for item in sel_dict["flag_sel"]]
                
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            if 'flag2' in df.columns:
                st.subheader("Orders by Flag")
                flag_counts = df['flag2'].value_counts().reset_index()
                flag_counts.columns = ['Flag', 'Count']
                flag_counts['Share'] = (flag_counts['Count'] / flag_counts['Count'].sum() * 100).round(1).astype(str) + '%'
                
                # Filter out labels for tiny slices (< 3%) directly in Pandas to guarantee they render correctly
                min_count = flag_counts['Count'].sum() * 0.03
                flag_counts['Share_Text'] = flag_counts['Share'].where(flag_counts['Count'] >= min_count, '')
                
                # Full domain to keep the legend stable when slices are dynamically filtered out
                domain = flag_counts['Flag'].tolist()
                
                # Two separate selections: one for the legend (filtering), one for the slices (filtering + popup)
                leg_sel = alt.selection_point(fields=['Flag'], bind='legend', name='leg_sel')
                slice_sel = alt.selection_point(fields=['Flag'], name='slice_sel')
                
                # Adding explicit 'order' ensures that both the arc and the text layers
                # stack the slices in the exact same sequence. Without this, Altair can
                # get confused by the different tooltip/text encodings and cluster all
                # the text labels together at the 12 o'clock position!
                base_chart = alt.Chart(flag_counts).encode(
                    theta=alt.Theta(field="Count", type="quantitative", stack=True),
                    order=alt.Order(field="Count", type="quantitative", sort="descending")
                )
                
                donut_arc = base_chart.mark_arc(innerRadius=80, outerRadius=140, stroke='transparent', strokeWidth=2).encode(
                    color=alt.Color(field="Flag", type="nominal", scale=alt.Scale(domain=domain), legend=alt.Legend(title="Flag", orient="right", labelFontSize=13, titleFontSize=14)),
                    tooltip=['Flag', 'Count', 'Share'],
                    opacity=alt.condition(leg_sel & slice_sel, alt.value(1.0), alt.value(0.3))
                ).add_params(leg_sel, slice_sel)
                
                donut_text = base_chart.mark_text(radius=110, size=14, fontWeight='bold').encode(
                    text='Share_Text:N',
                    opacity=alt.condition(leg_sel & slice_sel, alt.value(1.0), alt.value(0.3))
                )
                
                donut_chart = alt.layer(donut_arc, donut_text).properties(height=400)

                if has_on_select:
                    st.markdown("<p style='font-size:12px; color:gray; margin-top:-15px;'>💡 Click legend to filter, click slices for raw data</p>", unsafe_allow_html=True)
                    if "last_pie_sel" not in st.session_state: st.session_state.last_pie_sel = None
                    
                    event_pie = st.altair_chart(donut_chart, use_container_width=True, on_select="rerun", key="pie_chart")
                    
                    try:
                        # Only trigger the pop-up if the SLICE was clicked (slice_sel has data)
                        sel_data = event_pie.selection.get("slice_sel", []) if hasattr(event_pie.selection, "get") else event_pie.selection["slice_sel"]
                        if sel_data and len(sel_data) > 0:
                            selected_flags_prev = [item.get("Flag") for item in sel_data if item.get("Flag")]
                            if selected_flags_prev:
                                sel_key = "|".join(sorted(selected_flags_prev))
                                if sel_key != st.session_state.last_pie_sel:
                                    st.session_state.last_pie_sel = sel_key
                                    show_data_preview(f"Flag: {', '.join(selected_flags_prev)}", df[df['flag2'].isin(selected_flags_prev)])
                            else:
                                st.session_state.last_pie_sel = None
                        else:
                            st.session_state.last_pie_sel = None
                    except Exception:
                        st.session_state.last_pie_sel = None
                else:
                    st.altair_chart(donut_chart, use_container_width=True)
                
        with row1_col2:
            if 'bucket' in df.columns:
                st.subheader("Orders by Bucket")
                
                # Apply cross-filtering from the Donut Chart!
                bar_df = df.copy()
                # An empty list means no selection was made (default Altair state = all items active)
                if len(selected_flags) > 0:
                    bar_df = bar_df[bar_df['flag2'].isin(selected_flags)]
                
                bucket_counts = bar_df['bucket'].value_counts().reset_index()
                bucket_counts.columns = ['Bucket', 'Count']
                
                # Converted to Altair for "View as Table" native Streamlit menu support
                click_sel_bar = alt.selection_point(fields=['Bucket'], name='bucket_sel')
                
                # Custom sort order for the Bucket chart
                bucket_sort_order = [
                    "BRSNR",
                    "Pending for OFD (with < 3 attempts done)",
                    "Pending for OFD (with >= 3 attempts done)",
                    "Misrouted (Not yet Bagged)",
                    "Pincode updated (Not yet Bagged)",
                    "Connection Pendency",
                    "0 Attempt",
                    "1&2 Attempt",
                    "3<= Attempt",
                    "OFD",
                    "Delivered"
                ]
                
                base_bar = alt.Chart(bucket_counts).encode(
                    x=alt.X('Count:Q', title='Total Orders'),
                    y=alt.Y('Bucket:N', title='Bucket', sort=bucket_sort_order),
                    tooltip=['Bucket', 'Count']
                )
                
                bars = base_bar.mark_bar(cornerRadiusEnd=2).encode(
                    color=alt.Color('Bucket:N', legend=None),
                    opacity=alt.condition(click_sel_bar, alt.value(1.0), alt.value(0.3))
                ).add_params(click_sel_bar)
                
                text = base_bar.mark_text(align='left', baseline='middle', dx=5, fontWeight='bold').encode(
                    text='Count:Q',
                    color=alt.Color('Bucket:N', legend=None),
                    opacity=alt.condition(click_sel_bar, alt.value(1.0), alt.value(0.3))
                )
                
                bar_chart = alt.layer(bars, text).properties(height=400)
                
                if has_on_select:
                    st.markdown("<p style='font-size:12px; color:gray; margin-top:-15px;'>💡 Click on any bar to view raw data (Shift+Click for multiple)</p>", unsafe_allow_html=True)
                    if "last_bar_sel" not in st.session_state: st.session_state.last_bar_sel = None
                    
                    event_bucket = st.altair_chart(bar_chart, use_container_width=True, on_select="rerun", key="bar_chart")
                    
                    try:
                        sel_data = event_bucket.selection.get("bucket_sel", []) if hasattr(event_bucket.selection, "get") else event_bucket.selection["bucket_sel"]
                        if sel_data and len(sel_data) > 0:
                            selected_buckets = [item.get("Bucket") for item in sel_data if item.get("Bucket")]
                            if selected_buckets:
                                sel_key = "|".join(sorted(selected_buckets))
                                if sel_key != st.session_state.last_bar_sel:
                                    st.session_state.last_bar_sel = sel_key
                                    show_data_preview(f"Bucket: {', '.join(selected_buckets)}", df[df['bucket'].isin(selected_buckets)])
                            else:
                                st.session_state.last_bar_sel = None
                        else:
                            st.session_state.last_bar_sel = None
                    except Exception:
                        st.session_state.last_bar_sel = None
                else:
                    st.altair_chart(bar_chart, use_container_width=True)
    
        # --- LINE CHART: ATTEMPTS BUCKET ---
        if 'attempt_number' in df.columns:
            st.subheader("Shipments by Attempt")
            
            clean_attempts = pd.to_numeric(df['attempt_number'], errors='coerce')
            
            def map_attempt_bucket(val):
                if pd.isna(val):
                    return "Unknown"
                elif val <= 1:
                    return "0-1"
                elif val <= 3:
                    return "2-3"
                else:
                    return "3+"
                    
            attempt_series = clean_attempts.apply(map_attempt_bucket)
            attempt_counts = attempt_series.value_counts().reset_index()
            attempt_counts.columns = ['Attempt Bucket', 'Count']
            
            # Ensure logical chronological order for the line chart
            sort_order = {"0-1": 1, "2-3": 2, "3+": 3, "Unknown": 4}
            attempt_counts['sort_key'] = attempt_counts['Attempt Bucket'].map(sort_order)
            attempt_counts = attempt_counts.sort_values('sort_key').drop('sort_key', axis=1)
            
            # Converted to Altair for "View as Table" native Streamlit menu support
            click_sel_line = alt.selection_point(fields=['Attempt Bucket'], name='line_sel')
            
            base_line = alt.Chart(attempt_counts).encode(
                x=alt.X('Attempt Bucket:N', title='Attempt Bucket', sort=None), # sort=None preserves chronological order
                y=alt.Y('Count:Q', title='Total Orders'),
                tooltip=['Attempt Bucket', 'Count']
            )
            
            line = base_line.mark_line(color='#1f77b4', strokeWidth=3)
            
            points = base_line.mark_circle(size=100, opacity=1).encode(
                color=alt.value('#1f77b4'),
                opacity=alt.condition(click_sel_line, alt.value(1.0), alt.value(0.3)),
                size=alt.condition(click_sel_line, alt.value(150), alt.value(100))
            ).add_params(click_sel_line)
            
            text = base_line.mark_text(align='center', baseline='bottom', dy=-15, fontWeight='bold').encode(
                text='Count:Q',
                color=alt.value('#1f77b4'),
                opacity=alt.condition(click_sel_line, alt.value(1.0), alt.value(0.3))
            )
            
            line_chart = alt.layer(line, points, text).properties(height=400)
            
            if has_on_select:
                st.markdown("<p style='font-size:12px; color:gray; margin-top:-15px;'>💡 Click on any point to view raw data (Shift+Click for multiple)</p>", unsafe_allow_html=True)
                if "last_line_sel" not in st.session_state: st.session_state.last_line_sel = None
                
                event_line = st.altair_chart(line_chart, use_container_width=True, on_select="rerun", key="line_chart")
                
                try:
                    sel_data = event_line.selection.get("line_sel", []) if hasattr(event_line.selection, "get") else event_line.selection["line_sel"]
                    if sel_data and len(sel_data) > 0:
                        selected_attempts = [item.get("Attempt Bucket") for item in sel_data if item.get("Attempt Bucket")]
                        if selected_attempts:
                            sel_key = "|".join(sorted(selected_attempts))
                            if sel_key != st.session_state.last_line_sel:
                                st.session_state.last_line_sel = sel_key
                                show_data_preview(f"Attempt Bucket: {', '.join(selected_attempts)}", df[attempt_series.isin(selected_attempts)])
                        else:
                            st.session_state.last_line_sel = None
                    else:
                        st.session_state.last_line_sel = None
                except Exception:
                    st.session_state.last_line_sel = None
            else:
                st.altair_chart(line_chart, use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Flag > Bucket > Order Status")
        
        # --- FLAG SORTING STATE ---
        if "flag_sort_col" not in st.session_state:
            st.session_state.flag_sort_col = "Shipments"
        if "flag_sort_asc" not in st.session_state:
            st.session_state.flag_sort_asc = False
            
        def toggle_flag_sort(col):
            if st.session_state.flag_sort_col == col:
                st.session_state.flag_sort_asc = not st.session_state.flag_sort_asc
            else:
                st.session_state.flag_sort_col = col
                st.session_state.flag_sort_asc = False if col != 'Flag' else True
                
        with st.container(border=True):
            # --- TABLE HEADER ---
            f_head1, f_head2, f_head3, f_head4, f_head5, f_head6 = st.columns([2.0, 1.0, 0.8, 0.8, 0.8, 1.1])
            
            def flag_sort_icon(col):
                return ""
    
            with f_head1:
                st.button(f"👤 Flag / Level{flag_sort_icon('Flag')}", on_click=toggle_flag_sort, args=('Flag',), key="sort_flag_name", type="tertiary")
            with f_head2:
                st.button(f"📦 Shipments{flag_sort_icon('Shipments')}", on_click=toggle_flag_sort, args=('Shipments',), key="sort_flag_ship", type="tertiary")
            with f_head3:
                st.button(f"🟢 0-2 Days{flag_sort_icon('Ageing_0_2')}", on_click=toggle_flag_sort, args=('Ageing_0_2',), key="sort_flag_a02", type="tertiary")
            with f_head4:
                st.button(f"🟡 3-5 Days{flag_sort_icon('Ageing_3_5')}", on_click=toggle_flag_sort, args=('Ageing_3_5',), key="sort_flag_a35", type="tertiary")
            with f_head5:
                st.button(f"🔴 5+ Days{flag_sort_icon('Ageing_5_plus')}", on_click=toggle_flag_sort, args=('Ageing_5_plus',), key="sort_flag_a5p", type="tertiary")
            with f_head6:
                st.button(f"💸 5+ Debit{flag_sort_icon('Debit_5_plus')}", on_click=toggle_flag_sort, args=('Debit_5_plus',), key="sort_flag_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            # Group Level 1: Flag
            with st.container(height=600, border=False):
                flag_groups = hier_df.groupby('flag2').agg(
                    Shipments=('flag2', 'count'),
                    Ageing_0_2=('Ageing_0_2', 'sum'),
                    Ageing_3_5=('Ageing_3_5', 'sum'),
                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                    Debit_5_plus=('Debit_5_plus', 'sum')
                ).reset_index()
            
                # Apply sorting based on session state
                flag_groups = flag_groups.sort_values('flag2' if st.session_state.flag_sort_col == 'Flag' else st.session_state.flag_sort_col, ascending=st.session_state.flag_sort_asc)
            
                for _, flag_row in flag_groups.iterrows():
                    flag_name = flag_row['flag2']
                    flag_ship = flag_row['Shipments']
                    flag_a02 = flag_row['Ageing_0_2']
                    flag_a35 = flag_row['Ageing_3_5']
                    flag_a5p = flag_row['Ageing_5_plus']
                    flag_d5p = flag_row['Debit_5_plus']
                
                    flag_expanded = st.session_state.get(f"flag_{flag_name}", False)
                    flag_icon = "▼" if flag_expanded else "▶"
                
                    # Custom Table Row: Flag
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.15, 1.85, 1.0, 0.8, 0.8, 0.8, 1.1])
                    expand_flag = c1.checkbox(f"{flag_icon}", key=f"flag_{flag_name}")
                    with c2:
                        if st.button(f"Flag: {flag_name}", key=f"btn_prev_flag_{flag_name}", type="tertiary"):
                            show_data_preview(f"Flag: {flag_name}", hier_df[hier_df['flag2'] == flag_name])
                    c3.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{flag_ship:,}</b></p>", unsafe_allow_html=True)
                    c4.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{flag_a02:,}</b></p>", unsafe_allow_html=True)
                    c5.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{flag_a35:,}</b></p>", unsafe_allow_html=True)
                    c6.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{flag_a5p:,}</b></p>", unsafe_allow_html=True)
                    c7.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{format_indian_currency(flag_d5p)}</b></p>", unsafe_allow_html=True)
                
                    if expand_flag:
                        flag_df = hier_df[hier_df['flag2'] == flag_name]
                    
                        # Group Level 2: Bucket
                        bucket_groups = flag_df.groupby('bucket').agg(
                            Shipments=('bucket', 'count'),
                            Ageing_0_2=('Ageing_0_2', 'sum'),
                            Ageing_3_5=('Ageing_3_5', 'sum'),
                            Ageing_5_plus=('Ageing_5_plus', 'sum'),
                            Debit_5_plus=('Debit_5_plus', 'sum')
                        ).reset_index()
                        bucket_groups = bucket_groups.sort_values('Shipments', ascending=False)
                    
                        for _, bucket_row in bucket_groups.iterrows():
                            bucket_name = bucket_row['bucket']
                            bucket_ship = bucket_row['Shipments']
                            bucket_a02 = bucket_row['Ageing_0_2']
                            bucket_a35 = bucket_row['Ageing_3_5']
                            bucket_a5p = bucket_row['Ageing_5_plus']
                            bucket_d5p = bucket_row['Debit_5_plus']
                        
                            bucket_expanded = st.session_state.get(f"bucket_{flag_name}_{bucket_name}", False)
                            bucket_icon = "▼" if bucket_expanded else "▶"
                        
                            # Custom Table Row: Bucket (Indented visually)
                            sc_space, sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([0.1, 0.15, 1.75, 1.0, 0.8, 0.8, 0.8, 1.1])
                            expand_bucket = sc1.checkbox(f"{bucket_icon}", key=f"bucket_{flag_name}_{bucket_name}")
                            with sc2:
                                if st.button(f"Bucket: {bucket_name}", key=f"btn_prev_bucket_{flag_name}_{bucket_name}", type="tertiary"):
                                    show_data_preview(f"Bucket: {bucket_name}", flag_df[flag_df['bucket'] == bucket_name])
                            sc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{bucket_ship:,}</p>", unsafe_allow_html=True)
                            sc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{bucket_a02:,}</p>", unsafe_allow_html=True)
                            sc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{bucket_a35:,}</p>", unsafe_allow_html=True)
                            sc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{bucket_a5p:,}</p>", unsafe_allow_html=True)
                            sc7.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(bucket_d5p)}</p>", unsafe_allow_html=True)
                        
                            if expand_bucket:
                                bucket_df = flag_df[flag_df['bucket'] == bucket_name]
                            
                                # Group Level 3: Order Status (Displayed as clickable text rows)
                                os_groups = bucket_df.groupby('order_status').agg(
                                    Shipments=('order_status', 'count'),
                                    Ageing_0_2=('Ageing_0_2', 'sum'),
                                    Ageing_3_5=('Ageing_3_5', 'sum'),
                                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                    Debit_5_plus=('Debit_5_plus', 'sum')
                                ).reset_index()
                                os_groups = os_groups.sort_values('Shipments', ascending=False)
                            
                                for _, os_row in os_groups.iterrows():
                                    os_name = os_row['order_status']
                                    os_ship = os_row['Shipments']
                                    os_a02 = os_row['Ageing_0_2']
                                    os_a35 = os_row['Ageing_3_5']
                                    os_a5p = os_row['Ageing_5_plus']
                                    os_d5p = os_row['Debit_5_plus']
                                
                                    hc_space, hc1, hc2, hc3, hc4, hc5, hc6 = st.columns([0.35, 1.65, 1.0, 0.8, 0.8, 0.8, 1.1])
                                    with hc1:
                                        if st.button(f"{os_name}", key=f"btn_os_{flag_name}_{bucket_name}_{os_name}", type="tertiary"):
                                            show_data_preview(f"{os_name}", bucket_df[bucket_df['order_status'] == os_name])
                                
                                    hc2.markdown(f"<p style='margin: 0; padding-top: 2px;'>{os_ship:,}</p>", unsafe_allow_html=True)
                                    hc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{os_a02:,}</p>", unsafe_allow_html=True)
                                    hc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{os_a35:,}</p>", unsafe_allow_html=True)
                                    hc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{os_a5p:,}</p>", unsafe_allow_html=True)
                                    hc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(os_d5p)}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)

    with tab_shszmpod:
        st.subheader("State Head > SZM > Hub")
        
        # --- SORTING STATE ---
        if "sh_sort_col" not in st.session_state:
            st.session_state.sh_sort_col = "Shipments"
        if "sh_sort_asc" not in st.session_state:
            st.session_state.sh_sort_asc = False
            
        def toggle_sh_sort(col):
            if st.session_state.sh_sort_col == col:
                st.session_state.sh_sort_asc = not st.session_state.sh_sort_asc
            else:
                st.session_state.sh_sort_col = col
                st.session_state.sh_sort_asc = False if col != 'State Head' else True
        
        # --- POD SORTING STATE ---
        if "pod_sort_col" not in st.session_state:
            st.session_state.pod_sort_col = "Shipments"
        if "pod_sort_asc" not in st.session_state:
            st.session_state.pod_sort_asc = False
            
        def toggle_pod_sort(col):
            if st.session_state.pod_sort_col == col:
                st.session_state.pod_sort_asc = not st.session_state.pod_sort_asc
            else:
                st.session_state.pod_sort_col = col
                st.session_state.pod_sort_asc = False if col != 'POD' else True

        # --- SH LEVEL 2 & 3 SORTING STATES ---
        if "sh_lvl2_sort_col" not in st.session_state:
            st.session_state.sh_lvl2_sort_col = "Shipments"
        if "sh_lvl2_sort_asc" not in st.session_state:
            st.session_state.sh_lvl2_sort_asc = False
            
        def toggle_sh_lvl2_sort(col):
            if st.session_state.sh_lvl2_sort_col == col:
                st.session_state.sh_lvl2_sort_asc = not st.session_state.sh_lvl2_sort_asc
            else:
                st.session_state.sh_lvl2_sort_col = col
                st.session_state.sh_lvl2_sort_asc = False

        if "sh_lvl2_hub_sort_col" not in st.session_state:
            st.session_state.sh_lvl2_hub_sort_col = "Shipments"
        if "sh_lvl2_hub_sort_asc" not in st.session_state:
            st.session_state.sh_lvl2_hub_sort_asc = False
            
        def toggle_sh_lvl2_hub_sort(col):
            if st.session_state.sh_lvl2_hub_sort_col == col:
                st.session_state.sh_lvl2_hub_sort_asc = not st.session_state.sh_lvl2_hub_sort_asc
            else:
                st.session_state.sh_lvl2_hub_sort_col = col
                st.session_state.sh_lvl2_hub_sort_asc = False

        # --- POD LEVEL 2 & 3 SORTING STATES ---
        if "pod_lvl2_sort_col" not in st.session_state:
            st.session_state.pod_lvl2_sort_col = "Shipments"
        if "pod_lvl2_sort_asc" not in st.session_state:
            st.session_state.pod_lvl2_sort_asc = False
            
        def toggle_pod_lvl2_sort(col):
            if st.session_state.pod_lvl2_sort_col == col:
                st.session_state.pod_lvl2_sort_asc = not st.session_state.pod_lvl2_sort_asc
            else:
                st.session_state.pod_lvl2_sort_col = col
                st.session_state.pod_lvl2_sort_asc = False

        if "pod_lvl2_hub_sort_col" not in st.session_state:
            st.session_state.pod_lvl2_hub_sort_col = "Shipments"
        if "pod_lvl2_hub_sort_asc" not in st.session_state:
            st.session_state.pod_lvl2_hub_sort_asc = False
            
        def toggle_pod_lvl2_hub_sort(col):
            if st.session_state.pod_lvl2_hub_sort_col == col:
                st.session_state.pod_lvl2_hub_sort_asc = not st.session_state.pod_lvl2_hub_sort_asc
            else:
                st.session_state.pod_lvl2_hub_sort_col = col
                st.session_state.pod_lvl2_hub_sort_asc = False
        
        with st.container(border=True):
            # --- TABLE HEADER ---
            st.markdown("<div class='sticky-header-marker'></div>", unsafe_allow_html=True)
            head1, head2, head3, head4, head5, head6 = st.columns([2.0, 1.0, 0.8, 0.8, 0.8, 1.1])
            
            def sort_icon(col):
                return ""
    
            with head1:
                st.button(f"👤 Name / Level{sort_icon('State Head')}", on_click=toggle_sh_sort, args=('State Head',), key="sort_sh_name", type="tertiary")
            with head2:
                st.button(f"📦 Shipments{sort_icon('Shipments')}", on_click=toggle_sh_sort, args=('Shipments',), key="sort_sh_ship", type="tertiary")
            with head3:
                st.button(f" 0-2 Days{sort_icon('Ageing_0_2')}", on_click=toggle_sh_sort, args=('Ageing_0_2',), key="sort_sh_a02", type="tertiary")
            with head4:
                st.button(f"🟡 3-5 Days{sort_icon('Ageing_3_5')}", on_click=toggle_sh_sort, args=('Ageing_3_5',), key="sort_sh_a35", type="tertiary")
            with head5:
                st.button(f"🔴 5+ Days{sort_icon('Ageing_5_plus')}", on_click=toggle_sh_sort, args=('Ageing_5_plus',), key="sort_sh_a5p", type="tertiary")
            with head6:
                st.button(f"💸 5+ Debit{sort_icon('Debit_5_plus')}", on_click=toggle_sh_sort, args=('Debit_5_plus',), key="sort_sh_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            with st.container(height=600, border=False):
                # Group Level 1: State Head
                sh_groups = hier_df.groupby('State Head').agg(
                    Shipments=('State Head', 'count'),
                    Ageing_0_2=('Ageing_0_2', 'sum'),
                    Ageing_3_5=('Ageing_3_5', 'sum'),
                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                    Debit_5_plus=('Debit_5_plus', 'sum')
                ).reset_index()
            
                # Apply sorting based on session state
                sh_groups = sh_groups.sort_values(st.session_state.sh_sort_col, ascending=st.session_state.sh_sort_asc)
            
                for _, sh_row in sh_groups.iterrows():
                    sh_name = sh_row['State Head']
                    sh_ship = sh_row['Shipments']
                    sh_a02 = sh_row['Ageing_0_2']
                    sh_a35 = sh_row['Ageing_3_5']
                    sh_a5p = sh_row['Ageing_5_plus']
                    sh_d5p = sh_row['Debit_5_plus']
                
                    sh_expanded = st.session_state.get(f"sh_{sh_name}", False)
                    sh_icon = "▼" if sh_expanded else "▶"
                
                    # Custom Table Row: State Head
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.15, 1.85, 1.0, 0.8, 0.8, 0.8, 1.1])
                    expand_sh = c1.checkbox(f"{sh_icon}", key=f"sh_{sh_name}")
                    with c2:
                        if st.button(f"{sh_name}", key=f"btn_prev_sh_{sh_name}", type="tertiary"):
                            show_data_preview(f"State Head: {sh_name}", hier_df[hier_df['State Head'] == sh_name])
                    with c3:
                        st.button(get_sort_label(f"{sh_ship:,}", 'Shipments', st.session_state.sh_lvl2_sort_col, st.session_state.sh_lvl2_sort_asc), key=f"btn_sh_lvl2_ship_{sh_name}", type="tertiary", on_click=toggle_sh_lvl2_sort, args=('Shipments',))
                    with c4:
                        st.button(get_sort_label(f"{sh_a02:,}", 'Ageing_0_2', st.session_state.sh_lvl2_sort_col, st.session_state.sh_lvl2_sort_asc), key=f"btn_sh_lvl2_a02_{sh_name}", type="tertiary", on_click=toggle_sh_lvl2_sort, args=('Ageing_0_2',))
                    with c5:
                        st.button(get_sort_label(f"{sh_a35:,}", 'Ageing_3_5', st.session_state.sh_lvl2_sort_col, st.session_state.sh_lvl2_sort_asc), key=f"btn_sh_lvl2_a35_{sh_name}", type="tertiary", on_click=toggle_sh_lvl2_sort, args=('Ageing_3_5',))
                    with c6:
                        st.button(get_sort_label(f"{sh_a5p:,}", 'Ageing_5_plus', st.session_state.sh_lvl2_sort_col, st.session_state.sh_lvl2_sort_asc), key=f"btn_sh_lvl2_a5p_{sh_name}", type="tertiary", on_click=toggle_sh_lvl2_sort, args=('Ageing_5_plus',))
                    with c7:
                        st.button(get_sort_label(f"{format_indian_currency(sh_d5p)}", 'Debit_5_plus', st.session_state.sh_lvl2_sort_col, st.session_state.sh_lvl2_sort_asc), key=f"btn_sh_lvl2_d5p_{sh_name}", type="tertiary", on_click=toggle_sh_lvl2_sort, args=('Debit_5_plus',))
                
                    if expand_sh:
                        sh_df = hier_df[hier_df['State Head'] == sh_name]
                    
                        # Group Level 2: SZM
                        szm_groups = sh_df.groupby('SZM').agg(
                            Shipments=('SZM', 'count'),
                            Ageing_0_2=('Ageing_0_2', 'sum'),
                            Ageing_3_5=('Ageing_3_5', 'sum'),
                            Ageing_5_plus=('Ageing_5_plus', 'sum'),
                            Debit_5_plus=('Debit_5_plus', 'sum')
                        ).reset_index()
                        szm_groups = szm_groups.sort_values(st.session_state.sh_lvl2_sort_col, ascending=st.session_state.sh_lvl2_sort_asc)
                    
                        for _, szm_row in szm_groups.iterrows():
                            szm_name = szm_row['SZM']
                            szm_ship = szm_row['Shipments']
                            szm_a02 = szm_row['Ageing_0_2']
                            szm_a35 = szm_row['Ageing_3_5']
                            szm_a5p = szm_row['Ageing_5_plus']
                            szm_d5p = szm_row['Debit_5_plus']
                        
                            szm_expanded = st.session_state.get(f"szm_{sh_name}_{szm_name}", False)
                            szm_icon = "▼" if szm_expanded else "▶"
                        
                            # Custom Table Row: SZM (Indented visually)
                            sc_space, sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([0.1, 0.15, 1.75, 1.0, 0.8, 0.8, 0.8, 1.1])
                            expand_szm = sc1.checkbox(f"{szm_icon}", key=f"szm_{sh_name}_{szm_name}")
                            with sc2:
                                if st.button(f"{szm_name}", key=f"btn_prev_szm_{sh_name}_{szm_name}", type="tertiary"):
                                    show_data_preview(f"SZM: {szm_name}", sh_df[sh_df['SZM'] == szm_name])
                            with sc3:
                                st.button(get_sort_label(f"{szm_ship:,}", 'Shipments', st.session_state.sh_lvl2_hub_sort_col, st.session_state.sh_lvl2_hub_sort_asc), key=f"btn_szm_lvl3_ship_{sh_name}_{szm_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Shipments',))
                            with sc4:
                                st.button(get_sort_label(f"{szm_a02:,}", 'Ageing_0_2', st.session_state.sh_lvl2_hub_sort_col, st.session_state.sh_lvl2_hub_sort_asc), key=f"btn_szm_lvl3_a02_{sh_name}_{szm_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Ageing_0_2',))
                            with sc5:
                                st.button(get_sort_label(f"{szm_a35:,}", 'Ageing_3_5', st.session_state.sh_lvl2_hub_sort_col, st.session_state.sh_lvl2_hub_sort_asc), key=f"btn_szm_lvl3_a35_{sh_name}_{szm_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Ageing_3_5',))
                            with sc6:
                                st.button(get_sort_label(f"{szm_a5p:,}", 'Ageing_5_plus', st.session_state.sh_lvl2_hub_sort_col, st.session_state.sh_lvl2_hub_sort_asc), key=f"btn_szm_lvl3_a5p_{sh_name}_{szm_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Ageing_5_plus',))
                            with sc7:
                                st.button(get_sort_label(f"{format_indian_currency(szm_d5p)}", 'Debit_5_plus', st.session_state.sh_lvl2_hub_sort_col, st.session_state.sh_lvl2_hub_sort_asc), key=f"btn_szm_lvl3_d5p_{sh_name}_{szm_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Debit_5_plus',))
                        
                            if expand_szm:
                                szm_df = sh_df[sh_df['SZM'] == szm_name]
                            
                                # Group Level 3: Hub (Displayed as clickable text rows)
                                hub_groups = szm_df.groupby('current_hub').agg(
                                    Shipments=('current_hub', 'count'),
                                    Ageing_0_2=('Ageing_0_2', 'sum'),
                                    Ageing_3_5=('Ageing_3_5', 'sum'),
                                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                    Debit_5_plus=('Debit_5_plus', 'sum')
                                ).reset_index()
                                hub_groups = hub_groups.sort_values(st.session_state.sh_lvl2_hub_sort_col, ascending=st.session_state.sh_lvl2_hub_sort_asc)
                            
                                for _, hub_row in hub_groups.iterrows():
                                    hub_name = hub_row['current_hub']
                                    h_ship = hub_row['Shipments']
                                    h_a02 = hub_row['Ageing_0_2']
                                    h_a35 = hub_row['Ageing_3_5']
                                    h_a5p = hub_row['Ageing_5_plus']
                                    h_d5p = hub_row['Debit_5_plus']
                                
                                    hc_space, hc1, hc2, hc3, hc4, hc5, hc6 = st.columns([0.35, 1.65, 1.0, 0.8, 0.8, 0.8, 1.1])
                                    with hc1:
                                        if st.button(f"{hub_name}", key=f"btn_hub_{sh_name}_{szm_name}_{hub_name}", type="tertiary"):
                                            show_data_preview(f"{hub_name}", szm_df[szm_df['current_hub'] == hub_name])
                                
                                    with hc2:
                                        st.button(f"{h_ship:,}", key=f"btn_hub_lvl3_ship_val_{sh_name}_{szm_name}_{hub_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Shipments',))
                                    with hc3:
                                        st.button(f"{h_a02:,}", key=f"btn_hub_lvl3_a02_val_{sh_name}_{szm_name}_{hub_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Ageing_0_2',))
                                    with hc4:
                                        st.button(f"{h_a35:,}", key=f"btn_hub_lvl3_a35_val_{sh_name}_{szm_name}_{hub_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Ageing_3_5',))
                                    with hc5:
                                        st.button(f"{h_a5p:,}", key=f"btn_hub_lvl3_a5p_val_{sh_name}_{szm_name}_{hub_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Ageing_5_plus',))
                                    with hc6:
                                        st.button(f"{format_indian_currency(h_d5p)}", key=f"btn_hub_lvl3_d5p_val_{sh_name}_{szm_name}_{hub_name}", type="tertiary", on_click=toggle_sh_lvl2_hub_sort, args=('Debit_5_plus',))
                    st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("POD > LM State Head > Hub")
        
        with st.container(border=True):
            # --- POD TABLE HEADER ---
            st.markdown("<div class='sticky-header-marker'></div>", unsafe_allow_html=True)
            p_head1, p_head2, p_head3, p_head4, p_head5, p_head6 = st.columns([2.0, 1.0, 0.8, 0.8, 0.8, 1.1])
            
            def pod_sort_icon(col):
                return ""
    
            with p_head1:
                st.button(f"👤 Name / Level{pod_sort_icon('POD')}", on_click=toggle_pod_sort, args=('POD',), key="sort_pod_name", type="tertiary")
            with p_head2:
                st.button(f"📦 Shipments{pod_sort_icon('Shipments')}", on_click=toggle_pod_sort, args=('Shipments',), key="sort_pod_ship", type="tertiary")
            with p_head3:
                st.button(f"🟢 0-2 Days{pod_sort_icon('Ageing_0_2')}", on_click=toggle_pod_sort, args=('Ageing_0_2',), key="sort_pod_a02", type="tertiary")
            with p_head4:
                st.button(f"🟡 3-5 Days{pod_sort_icon('Ageing_3_5')}", on_click=toggle_pod_sort, args=('Ageing_3_5',), key="sort_pod_a35", type="tertiary")
            with p_head5:
                st.button(f"🔴 5+ Days{pod_sort_icon('Ageing_5_plus')}", on_click=toggle_pod_sort, args=('Ageing_5_plus',), key="sort_pod_a5p", type="tertiary")
            with p_head6:
                st.button(f"💸 5+ Debit{pod_sort_icon('Debit_5_plus')}", on_click=toggle_pod_sort, args=('Debit_5_plus',), key="sort_pod_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            with st.container(height=600, border=False):
                # Group Level 1: POD
                pod_groups = hier_df.groupby('POD Zone').agg(
                    Shipments=('POD Zone', 'count'),
                    Ageing_0_2=('Ageing_0_2', 'sum'),
                    Ageing_3_5=('Ageing_3_5', 'sum'),
                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                    Debit_5_plus=('Debit_5_plus', 'sum')
                ).reset_index()
            
                # Apply sorting based on session state
                pod_groups = pod_groups.sort_values('POD Zone' if st.session_state.pod_sort_col == 'POD' else st.session_state.pod_sort_col, ascending=st.session_state.pod_sort_asc)
            
                for _, pod_row in pod_groups.iterrows():
                    pod_name = pod_row['POD Zone']
                    pod_ship = pod_row['Shipments']
                    pod_a02 = pod_row['Ageing_0_2']
                    pod_a35 = pod_row['Ageing_3_5']
                    pod_a5p = pod_row['Ageing_5_plus']
                    pod_d5p = pod_row['Debit_5_plus']
                
                    pod_expanded = st.session_state.get(f"pod_{pod_name}", False)
                    pod_icon = "▼" if pod_expanded else "▶"
                
                    # Custom Table Row: POD
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.15, 1.85, 1.0, 0.8, 0.8, 0.8, 1.1])
                    expand_pod = c1.checkbox(f"{pod_icon}", key=f"pod_{pod_name}")
                    with c2:
                        if st.button(f"{pod_name}", key=f"btn_prev_pod_{pod_name}", type="tertiary"):
                            show_data_preview(f"POD: {pod_name}", hier_df[hier_df['POD Zone'] == pod_name])
                    with c3:
                        st.button(get_sort_label(f"{pod_ship:,}", 'Shipments', st.session_state.pod_lvl2_sort_col, st.session_state.pod_lvl2_sort_asc), key=f"btn_pod_lvl2_ship_{pod_name}", type="tertiary", on_click=toggle_pod_lvl2_sort, args=('Shipments',))
                    with c4:
                        st.button(get_sort_label(f"{pod_a02:,}", 'Ageing_0_2', st.session_state.pod_lvl2_sort_col, st.session_state.pod_lvl2_sort_asc), key=f"btn_pod_lvl2_a02_{pod_name}", type="tertiary", on_click=toggle_pod_lvl2_sort, args=('Ageing_0_2',))
                    with c5:
                        st.button(get_sort_label(f"{pod_a35:,}", 'Ageing_3_5', st.session_state.pod_lvl2_sort_col, st.session_state.pod_lvl2_sort_asc), key=f"btn_pod_lvl2_a35_{pod_name}", type="tertiary", on_click=toggle_pod_lvl2_sort, args=('Ageing_3_5',))
                    with c6:
                        st.button(get_sort_label(f"{pod_a5p:,}", 'Ageing_5_plus', st.session_state.pod_lvl2_sort_col, st.session_state.pod_lvl2_sort_asc), key=f"btn_pod_lvl2_a5p_{pod_name}", type="tertiary", on_click=toggle_pod_lvl2_sort, args=('Ageing_5_plus',))
                    with c7:
                        st.button(get_sort_label(f"{format_indian_currency(pod_d5p)}", 'Debit_5_plus', st.session_state.pod_lvl2_sort_col, st.session_state.pod_lvl2_sort_asc), key=f"btn_pod_lvl2_d5p_{pod_name}", type="tertiary", on_click=toggle_pod_lvl2_sort, args=('Debit_5_plus',))
                
                    if expand_pod:
                        pod_df = hier_df[hier_df['POD Zone'] == pod_name]
                    
                        # Group Level 2: LM State Head
                        state_groups = pod_df.groupby('LM State Head').agg(
                            Shipments=('LM State Head', 'count'),
                            Ageing_0_2=('Ageing_0_2', 'sum'),
                            Ageing_3_5=('Ageing_3_5', 'sum'),
                            Ageing_5_plus=('Ageing_5_plus', 'sum'),
                            Debit_5_plus=('Debit_5_plus', 'sum')
                        ).reset_index()
                        state_groups = state_groups.sort_values(st.session_state.pod_lvl2_sort_col, ascending=st.session_state.pod_lvl2_sort_asc)
                    
                        for _, state_row in state_groups.iterrows():
                            state_name = state_row['LM State Head']
                            state_ship = state_row['Shipments']
                            state_a02 = state_row['Ageing_0_2']
                            state_a35 = state_row['Ageing_3_5']
                            state_a5p = state_row['Ageing_5_plus']
                            state_d5p = state_row['Debit_5_plus']
                        
                            state_expanded = st.session_state.get(f"state_{pod_name}_{state_name}", False)
                            state_icon = "▼" if state_expanded else "▶"
                        
                            # Custom Table Row: LM State Head (Indented visually)
                            sc_space, sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([0.1, 0.15, 1.75, 1.0, 0.8, 0.8, 0.8, 1.1])
                            expand_state = sc1.checkbox(f"{state_icon}", key=f"state_{pod_name}_{state_name}")
                            with sc2:
                                if st.button(f"{state_name}", key=f"btn_prev_state_{pod_name}_{state_name}", type="tertiary"):
                                    show_data_preview(f"LM State Head: {state_name}", pod_df[pod_df['LM State Head'] == state_name])
                            with sc3:
                                st.button(get_sort_label(f"{state_ship:,}", 'Shipments', st.session_state.pod_lvl2_hub_sort_col, st.session_state.pod_lvl2_hub_sort_asc), key=f"btn_state_lvl3_ship_{pod_name}_{state_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Shipments',))
                            with sc4:
                                st.button(get_sort_label(f"{state_a02:,}", 'Ageing_0_2', st.session_state.pod_lvl2_hub_sort_col, st.session_state.pod_lvl2_hub_sort_asc), key=f"btn_state_lvl3_a02_{pod_name}_{state_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Ageing_0_2',))
                            with sc5:
                                st.button(get_sort_label(f"{state_a35:,}", 'Ageing_3_5', st.session_state.pod_lvl2_hub_sort_col, st.session_state.pod_lvl2_hub_sort_asc), key=f"btn_state_lvl3_a35_{pod_name}_{state_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Ageing_3_5',))
                            with sc6:
                                st.button(get_sort_label(f"{state_a5p:,}", 'Ageing_5_plus', st.session_state.pod_lvl2_hub_sort_col, st.session_state.pod_lvl2_hub_sort_asc), key=f"btn_state_lvl3_a5p_{pod_name}_{state_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Ageing_5_plus',))
                            with sc7:
                                st.button(get_sort_label(f"{format_indian_currency(state_d5p)}", 'Debit_5_plus', st.session_state.pod_lvl2_hub_sort_col, st.session_state.pod_lvl2_hub_sort_asc), key=f"btn_state_lvl3_d5p_{pod_name}_{state_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Debit_5_plus',))
                        
                            if expand_state:
                                state_df = pod_df[pod_df['LM State Head'] == state_name]
                            
                                # Group Level 3: Hub (Displayed as clickable text rows)
                                hub_groups = state_df.groupby('current_hub').agg(
                                    Shipments=('current_hub', 'count'),
                                    Ageing_0_2=('Ageing_0_2', 'sum'),
                                    Ageing_3_5=('Ageing_3_5', 'sum'),
                                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                    Debit_5_plus=('Debit_5_plus', 'sum')
                                ).reset_index()
                                hub_groups = hub_groups.sort_values(st.session_state.pod_lvl2_hub_sort_col, ascending=st.session_state.pod_lvl2_hub_sort_asc)
                            
                                for _, hub_row in hub_groups.iterrows():
                                    hub_name = hub_row['current_hub']
                                    h_ship = hub_row['Shipments']
                                    h_a02 = hub_row['Ageing_0_2']
                                    h_a35 = hub_row['Ageing_3_5']
                                    h_a5p = hub_row['Ageing_5_plus']
                                    h_d5p = hub_row['Debit_5_plus']
                                
                                    hc_space, hc1, hc2, hc3, hc4, hc5, hc6 = st.columns([0.35, 1.65, 1.0, 0.8, 0.8, 0.8, 1.1])
                                    with hc1:
                                        if st.button(f"{hub_name}", key=f"btn_hub_pod_{pod_name}_{state_name}_{hub_name}", type="tertiary"):
                                            show_data_preview(f"{hub_name}", state_df[state_df['current_hub'] == hub_name])
                                
                                    with hc2:
                                        st.button(f"{h_ship:,}", key=f"btn_state_lvl3_ship_val_{pod_name}_{state_name}_{hub_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Shipments',))
                                    with hc3:
                                        st.button(f"{h_a02:,}", key=f"btn_state_lvl3_a02_val_{pod_name}_{state_name}_{hub_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Ageing_0_2',))
                                    with hc4:
                                        st.button(f"{h_a35:,}", key=f"btn_state_lvl3_a35_val_{pod_name}_{state_name}_{hub_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Ageing_3_5',))
                                    with hc5:
                                        st.button(f"{h_a5p:,}", key=f"btn_state_lvl3_a5p_val_{pod_name}_{state_name}_{hub_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Ageing_5_plus',))
                                    with hc6:
                                        st.button(f"{format_indian_currency(h_d5p)}", key=f"btn_state_lvl3_d5p_val_{pod_name}_{state_name}_{hub_name}", type="tertiary", on_click=toggle_pod_lvl2_hub_sort, args=('Debit_5_plus',))
                    st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)

    with tab_hubs:
        st.subheader("Hub Level Summary")
        
        # --- HUB LEVEL SORTING STATE ---
        if "hub_flat_sort_col" not in st.session_state:
            st.session_state.hub_flat_sort_col = "Shipments"
        if "hub_flat_sort_asc" not in st.session_state:
            st.session_state.hub_flat_sort_asc = False
            
        def toggle_hub_flat_sort(col):
            if st.session_state.hub_flat_sort_col == col:
                st.session_state.hub_flat_sort_asc = not st.session_state.hub_flat_sort_asc
            else:
                st.session_state.hub_flat_sort_col = col
                st.session_state.hub_flat_sort_asc = False
                
        with st.container(border=True):
            st.markdown("<div class='sticky-header-marker'></div>", unsafe_allow_html=True)
            hf_head1, hf_head_szm, hf_head2, hf_head_tp, hf_head3, hf_head4, hf_head5, hf_head6 = st.columns([1.2, 0.8, 1.0, 0.8, 0.8, 0.8, 0.8, 1.1])
            
            with hf_head1:
                st.button(f"👤 Hub Name", key="sort_hub_flat_name", type="tertiary")
            with hf_head_szm:
                st.button("👤 SZM", key="sort_hub_flat_szm", type="tertiary")
            with hf_head2:
                st.button(f"📦 Shipments", on_click=toggle_hub_flat_sort, args=('Shipments',), key="sort_hub_flat_ship", type="tertiary")
            with hf_head_tp:
                st.button(f"👥 TP", on_click=toggle_hub_flat_sort, args=('TP',), key="sort_hub_flat_tp", type="tertiary")
            with hf_head3:
                st.button(f"🟢 0-2 Days", on_click=toggle_hub_flat_sort, args=('Ageing_0_2',), key="sort_hub_flat_a02", type="tertiary")
            with hf_head4:
                st.button(f"🟡 3-5 Days", on_click=toggle_hub_flat_sort, args=('Ageing_3_5',), key="sort_hub_flat_a35", type="tertiary")
            with hf_head5:
                st.button(f"🔴 5+ Days", on_click=toggle_hub_flat_sort, args=('Ageing_5_plus',), key="sort_hub_flat_a5p", type="tertiary")
            with hf_head6:
                st.button(f"💸 5+ Debit", on_click=toggle_hub_flat_sort, args=('Debit_5_plus',), key="sort_hub_flat_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            with st.container(height=600, border=False):
                flat_hub_groups = hier_df.groupby(['current_hub', 'SZM']).agg(
                    Shipments=('current_hub', 'count'),
                    TP=('seller_name', 'nunique'),
                    Ageing_0_2=('Ageing_0_2', 'sum'),
                    Ageing_3_5=('Ageing_3_5', 'sum'),
                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                    Debit_5_plus=('Debit_5_plus', 'sum')
                ).reset_index()
                
                flat_hub_groups = flat_hub_groups.sort_values(st.session_state.hub_flat_sort_col, ascending=st.session_state.hub_flat_sort_asc)
                
                display_hubs = flat_hub_groups.head(100)

                
                for _, fh_row in display_hubs.iterrows():
                    fh_hub = fh_row['current_hub']
                    fh_szm = fh_row['SZM']
                    fh_ship = fh_row['Shipments']
                    fh_tp = fh_row['TP']
                    fh_a02 = fh_row['Ageing_0_2']
                    fh_a35 = fh_row['Ageing_3_5']
                    fh_a5p = fh_row['Ageing_5_plus']
                    fh_d5p = fh_row['Debit_5_plus']
                    
                    fc1, fc2, fc3, fc_tp, fc4, fc5, fc6, fc7 = st.columns([1.2, 0.8, 1.0, 0.8, 0.8, 0.8, 0.8, 1.1])
                    with fc1:
                        if st.button(f"{fh_hub}", key=f"btn_hub_flat_{fh_hub}_{fh_szm}", type="tertiary"):
                            show_data_preview(f"{fh_hub}", hier_df[(hier_df['current_hub'] == fh_hub) & (hier_df['SZM'] == fh_szm)])
                    fc2.markdown(f"<p style='margin: 0; padding-top: 8px;'>{fh_szm}</p>", unsafe_allow_html=True)
                    with fc3:
                        st.button(f"{fh_ship:,}", key=f"btn_hub_flat_ship_{fh_hub}_{fh_szm}", type="tertiary")
                    with fc_tp:
                        st.button(f"{fh_tp:,}", key=f"btn_hub_flat_tp_{fh_hub}_{fh_szm}", type="tertiary")
                    with fc4:
                        st.button(f"{fh_a02:,}", key=f"btn_hub_flat_a02_{fh_hub}_{fh_szm}", type="tertiary")
                    with fc5:
                        st.button(f"{fh_a35:,}", key=f"btn_hub_flat_a35_{fh_hub}_{fh_szm}", type="tertiary")
                    with fc6:
                        st.button(f"{fh_a5p:,}", key=f"btn_hub_flat_a5p_{fh_hub}_{fh_szm}", type="tertiary")
                    with fc7:
                        st.button(f"{format_indian_currency(fh_d5p)}", key=f"btn_hub_flat_d5p_{fh_hub}_{fh_szm}", type="tertiary")

        st.subheader("Hub Type > Hub")
        
        # --- HUB SORTING STATE ---
        if "hub_sort_col" not in st.session_state:
            st.session_state.hub_sort_col = "Shipments"
        if "hub_sort_asc" not in st.session_state:
            st.session_state.hub_sort_asc = False
            
        def toggle_hub_sort(col):
            if st.session_state.hub_sort_col == col:
                st.session_state.hub_sort_asc = not st.session_state.hub_sort_asc
            else:
                st.session_state.hub_sort_col = col
                st.session_state.hub_sort_asc = False if col != 'Hub Type' else True

        # --- HUB LEVEL 2 SORTING STATES ---
        if "hub_lvl2_sort_col" not in st.session_state:
            st.session_state.hub_lvl2_sort_col = "Shipments"
        if "hub_lvl2_sort_asc" not in st.session_state:
            st.session_state.hub_lvl2_sort_asc = False
            
        def toggle_hub_lvl2_sort(col):
            if st.session_state.hub_lvl2_sort_col == col:
                st.session_state.hub_lvl2_sort_asc = not st.session_state.hub_lvl2_sort_asc
            else:
                st.session_state.hub_lvl2_sort_col = col
                st.session_state.hub_lvl2_sort_asc = False
        
        with st.container(border=True):
            # --- TABLE HEADER ---
            st.markdown("<div class='sticky-header-marker'></div>", unsafe_allow_html=True)
            h_head1, h_head_szm, h_head2, h_head_tp, h_head3, h_head4, h_head5, h_head6 = st.columns([1.2, 0.8, 1.0, 0.8, 0.8, 0.8, 0.8, 1.1])
            
            def hub_sort_icon(col):
                return ""
    
            with h_head1:
                st.button(f"👤 Hub Type / Name{hub_sort_icon('Hub Type')}", on_click=toggle_hub_sort, args=('Hub Type',), key="sort_hub_name", type="tertiary")
            with h_head_szm:
                st.button("👤 SZM", key="sort_hub_sh_header", type="tertiary")
            with h_head2:
                st.button(f"📦 Shipments{hub_sort_icon('Shipments')}", on_click=toggle_hub_sort, args=('Shipments',), key="sort_hub_ship", type="tertiary")
            with h_head_tp:
                st.button(f"👥 TP{hub_sort_icon('TP')}", on_click=toggle_hub_sort, args=('TP',), key="sort_hub_tp", type="tertiary")
            with h_head3:
                st.button(f"🟢 0-2 Days{hub_sort_icon('Ageing_0_2')}", on_click=toggle_hub_sort, args=('Ageing_0_2',), key="sort_hub_a02", type="tertiary")
            with h_head4:
                st.button(f"🟡 3-5 Days{hub_sort_icon('Ageing_3_5')}", on_click=toggle_hub_sort, args=('Ageing_3_5',), key="sort_hub_a35", type="tertiary")
            with h_head5:
                st.button(f"🔴 5+ Days{hub_sort_icon('Ageing_5_plus')}", on_click=toggle_hub_sort, args=('Ageing_5_plus',), key="sort_hub_a5p", type="tertiary")
            with h_head6:
                st.button(f"💸 5+ Debit{hub_sort_icon('Debit_5_plus')}", on_click=toggle_hub_sort, args=('Debit_5_plus',), key="sort_hub_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            with st.container(height=600, border=False):
                # Group Level 1: Hub Type
                hub_type_groups = hier_df.groupby('Hub Type').agg(
                    Shipments=('Hub Type', 'count'),
                    TP=('seller_name', 'nunique'),
                    Ageing_0_2=('Ageing_0_2', 'sum'),
                    Ageing_3_5=('Ageing_3_5', 'sum'),
                    Ageing_5_plus=('Ageing_5_plus', 'sum'),
                    Debit_5_plus=('Debit_5_plus', 'sum')
                ).reset_index()
            
                # Apply sorting based on session state
                hub_type_groups = hub_type_groups.sort_values('Hub Type' if st.session_state.hub_sort_col == 'Hub Type' else st.session_state.hub_sort_col, ascending=st.session_state.hub_sort_asc)
            
                for _, ht_row in hub_type_groups.iterrows():
                    ht_name = ht_row['Hub Type']
                    ht_ship = ht_row['Shipments']
                    ht_tp = ht_row['TP']
                    ht_a02 = ht_row['Ageing_0_2']
                    ht_a35 = ht_row['Ageing_3_5']
                    ht_a5p = ht_row['Ageing_5_plus']
                    ht_d5p = ht_row['Debit_5_plus']
                
                    ht_expanded = st.session_state.get(f"ht_{ht_name}", False)
                    ht_icon = "▼" if ht_expanded else "▶"
                
                    # Custom Table Row: Hub Type
                    c1, c2, c3, c_tp, c4, c5, c6, c7 = st.columns([0.15, 1.85, 1.0, 0.8, 0.8, 0.8, 0.8, 1.1])
                    expand_ht = c1.checkbox(f"{ht_icon}", key=f"ht_{ht_name}")
                    with c2:
                        if st.button(f"{ht_name}", key=f"btn_prev_ht_{ht_name}", type="tertiary"):
                            show_data_preview(f"{ht_name}", hier_df[hier_df['Hub Type'] == ht_name])
                    with c3:
                        st.button(get_sort_label(f"{ht_ship:,}", 'Shipments', st.session_state.hub_lvl2_sort_col, st.session_state.hub_lvl2_sort_asc), key=f"btn_hub_lvl2_ship_{ht_name}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Shipments',))
                    with c_tp:
                        st.button(get_sort_label(f"{ht_tp:,}", 'TP', st.session_state.hub_lvl2_sort_col, st.session_state.hub_lvl2_sort_asc), key=f"btn_hub_lvl2_tp_{ht_name}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('TP',))
                    with c4:
                        st.button(get_sort_label(f"{ht_a02:,}", 'Ageing_0_2', st.session_state.hub_lvl2_sort_col, st.session_state.hub_lvl2_sort_asc), key=f"btn_hub_lvl2_a02_{ht_name}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Ageing_0_2',))
                    with c5:
                        st.button(get_sort_label(f"{ht_a35:,}", 'Ageing_3_5', st.session_state.hub_lvl2_sort_col, st.session_state.hub_lvl2_sort_asc), key=f"btn_hub_lvl2_a35_{ht_name}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Ageing_3_5',))
                    with c6:
                        st.button(get_sort_label(f"{ht_a5p:,}", 'Ageing_5_plus', st.session_state.hub_lvl2_sort_col, st.session_state.hub_lvl2_sort_asc), key=f"btn_hub_lvl2_a5p_{ht_name}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Ageing_5_plus',))
                    with c7:
                        st.button(get_sort_label(f"{format_indian_currency(ht_d5p)}", 'Debit_5_plus', st.session_state.hub_lvl2_sort_col, st.session_state.hub_lvl2_sort_asc), key=f"btn_hub_lvl2_d5p_{ht_name}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Debit_5_plus',))
                
                    if expand_ht:
                        ht_df = hier_df[hier_df['Hub Type'] == ht_name]
                    
                        # Group Level 2: Hub & SZM
                        hub_sh_groups = ht_df.groupby(['current_hub', 'SZM']).agg(
                            Shipments=('current_hub', 'count'),
                            TP=('seller_name', 'nunique'),
                            Ageing_0_2=('Ageing_0_2', 'sum'),
                            Ageing_3_5=('Ageing_3_5', 'sum'),
                            Ageing_5_plus=('Ageing_5_plus', 'sum'),
                            Debit_5_plus=('Debit_5_plus', 'sum')
                        ).reset_index()
                        hub_sh_groups = hub_sh_groups.sort_values(st.session_state.hub_lvl2_sort_col, ascending=st.session_state.hub_lvl2_sort_asc)
                    
                        for _, hsh_row in hub_sh_groups.iterrows():
                            hsh_hub = hsh_row['current_hub']
                            hsh_sh = hsh_row['SZM']
                            hsh_ship = hsh_row['Shipments']
                            hsh_tp = hsh_row['TP']
                            hsh_a02 = hsh_row['Ageing_0_2']
                            hsh_a35 = hsh_row['Ageing_3_5']
                            hsh_a5p = hsh_row['Ageing_5_plus']
                            hsh_d5p = hsh_row['Debit_5_plus']
                        
                            # Custom Table Row: Hub Name & SZM (Indented visually)
                            hc_space, hc_hub, hc_am, hc2, hc_tp, hc3, hc4, hc5, hc6 = st.columns([0.15, 1.05, 0.8, 1.0, 0.8, 0.8, 0.8, 0.8, 1.1])
                            with hc_hub:
                                if st.button(f"{hsh_hub}", key=f"btn_hub_sh_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary"):
                                    show_data_preview(f"{hsh_hub}", ht_df[(ht_df['current_hub'] == hsh_hub) & (ht_df['SZM'] == hsh_sh)])
                        
                            hc_am.markdown(f"<p style='margin: 0; padding-top: 2px;'>{hsh_sh}</p>", unsafe_allow_html=True)
                        
                            with hc2:
                                st.button(f"{hsh_ship:,}", key=f"btn_hub_lvl2_ship_val_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Shipments',))
                            with hc_tp:
                                st.button(f"{hsh_tp:,}", key=f"btn_hub_lvl2_tp_val_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('TP',))
                            with hc3:
                                st.button(f"{hsh_a02:,}", key=f"btn_hub_lvl2_a02_val_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Ageing_0_2',))
                            with hc4:
                                st.button(f"{hsh_a35:,}", key=f"btn_hub_lvl2_a35_val_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Ageing_3_5',))
                            with hc5:
                                st.button(f"{hsh_a5p:,}", key=f"btn_hub_lvl2_a5p_val_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Ageing_5_plus',))
                            with hc6:
                                st.button(f"{format_indian_currency(hsh_d5p)}", key=f"btn_hub_lvl2_d5p_val_{ht_name}_{hsh_hub}_{hsh_sh}", type="tertiary", on_click=toggle_hub_lvl2_sort, args=('Debit_5_plus',))
                    st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
        