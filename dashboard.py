import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import altair as alt
import gdown

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

st.title("📦 RTS Pendency Dashboard")

with st.sidebar:
    # Safely get the Cloud URL
    try:
        REPORT_DOWNLOAD_URL = st.secrets["REPORT_DOWNLOAD_URL"]
    except (FileNotFoundError, KeyError):
        REPORT_DOWNLOAD_URL = None

    st.header("📊 Report Data")
    st.markdown("Download the latest processed report file.")
    
    file_path = "Final_ZOHO_Report.xlsx"
    if os.path.exists(file_path):
        with open(file_path, "rb") as fp:
            st.download_button(
                label="Download Report File",
                data=fp,
                file_name="Final_ZOHO_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    elif REPORT_DOWNLOAD_URL:
        st.link_button("Download Latest Report", REPORT_DOWNLOAD_URL, help="Download from Cloud Storage")

@st.cache_data(ttl=900) # Cache expires every 15 minutes (900 seconds) to fetch fresh cloud data
def load_data(file_source, mtime=None):
    """Loads the processed data and caches it for performance."""
    try:
        # If the source is a URL (like Google Drive)
        if isinstance(file_source, str) and file_source.startswith("http"):
            temp_file = "temp_cloud_report.xlsx"
            # gdown automatically bypasses the Google Drive large file virus warning
            gdown.download(file_source, temp_file, quiet=True)
            df = pd.read_excel(temp_file, sheet_name="Processed Data")
        else:
            # Explicitly read the 'Processed Data' tab where the script writes the output
            df = pd.read_excel(file_source, sheet_name="Processed Data")
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
        universal_search = st.text_input("🔍 Universal Search", placeholder="Search for any value across all columns...", label_visibility="collapsed")
        if universal_search:
            mask = df.astype(str).apply(lambda col: col.str.contains(universal_search, case=False, na=False, regex=False)).any(axis=1)
            df = df[mask]
            
        filter_configs = [
            ("Hub Name", "current_hub"),
            ("Hub Type", "Hub Type"),
            ("AM", "AM"),
            ("SL", "SL"),
            ("CT", "CT"),
            ("POD", "POD Zone"),
            ("Picked Month", "picked_month"),
            ("HOV", "HOV")
        ]
        
        # Distribute the 8 filters cleanly across 8 columns (side by side)
        cols = st.columns(8)
        
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
    else:
        ofd_d0_count = 0
        ofd_d0_df = df.iloc[0:0]

    @st.dialog("Data Preview", width="large")
    def show_data_preview(title, data_subset):
        st.write(f"Showing all {len(data_subset):,} records for: **{title}**")
        st.dataframe(data_subset, use_container_width=True, hide_index=True)

    # Prepare the dataset for hierarchy (Safely handle missing columns)
    hier_df = df.copy()
    hier_df['AM'] = hier_df.get('AM', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['SL'] = hier_df.get('SL', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['current_hub'] = hier_df.get('current_hub', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['Hub Type'] = hier_df.get('Hub Type', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    
    # Fallback if POD Zone is missing but POD Mapping exists
    if 'POD Zone' not in hier_df.columns and 'POD Mapping' in hier_df.columns:
        hier_df['POD Zone'] = hier_df['POD Mapping']
    hier_df['POD Zone'] = hier_df.get('POD Zone', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
    hier_df['State Head'] = hier_df.get('State Head', pd.Series(['Unknown'] * len(hier_df))).fillna('Unknown')
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
    
    # --- TABS ---
    tab_overview, tab_amslpod, tab_hubs = st.tabs(["Overview", "AM/SL/POD", "Hubs"])
    
    with tab_overview:
        # 2. Display as Broad Pills in 6 Columns
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>Total Shipments</p>", unsafe_allow_html=True)
                if st.button(f"{total_shipments:,}", key="btn_total", help="Click to view Total Shipments data", type="primary", use_container_width=True):
                    show_data_preview("Total Shipments", df)
                
        with col2:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>Debit Value</p>", unsafe_allow_html=True)
                if st.button(f"{format_indian_currency(total_debit)}", key="btn_debit", help="Click to view Debit Value data", type="primary", use_container_width=True):
                    show_data_preview("Debit Value", df)
                
        with col3:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>Overall HOV (1k+)</p>", unsafe_allow_html=True)
                if st.button(f"{hov_count:,}", key="btn_hov", help="Click to view Overall HOV (1k+) data", type="primary", use_container_width=True):
                    show_data_preview("Overall HOV (1k+)", df[debit_series >= 1000])
                
        with col4:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>5+ Ageing</p>", unsafe_allow_html=True)
                if st.button(f"{ageing_5_plus:,}", key="btn_ageing", help="Click to view 5+ Ageing data", type="primary", use_container_width=True):
                    show_data_preview("5+ Ageing", df[ageing_series > 5])
                
        with col5:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>5+ Ageing HOV (1k+)</p>", unsafe_allow_html=True)
                if st.button(f"{ageing_hov_count:,}", key="btn_ageing_hov", help="Click to view 5+ Ageing HOV (1k+) data", type="primary", use_container_width=True):
                    show_data_preview("5+ Ageing HOV (1k+)", df[(ageing_series > 5) & (debit_series >= 1000)])
                    
        with col6:
            with st.container(border=True):
                st.markdown("<p class='metric-label'>OFD (D0+)</p>", unsafe_allow_html=True)
                if st.button(f"{ofd_d0_count:,}", key="btn_ofd_d0", help="Click to view OFD (D0+) data", type="primary", use_container_width=True):
                    show_data_preview("OFD (D0+)", ofd_d0_df)
    
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
        st.markdown("<p style='font-size: 13px; color: gray;'><em>Note: Expand the rows below to drill down into Buckets and specific Order Statuses.</em></p>", unsafe_allow_html=True)
        
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
                if st.session_state.flag_sort_col == col:
                    return " ↑" if st.session_state.flag_sort_asc else " ↓"
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

    with tab_amslpod:
        st.subheader("AM > SL > Hub")
        st.markdown("<p style='font-size: 13px; color: gray;'><em>Note: Native Streamlit tables do not support collapsible rows. Below is a custom-built grid layout simulating an expandable table.</em></p>", unsafe_allow_html=True)
        
        # --- SORTING STATE ---
        if "am_sort_col" not in st.session_state:
            st.session_state.am_sort_col = "Shipments"
        if "am_sort_asc" not in st.session_state:
            st.session_state.am_sort_asc = False
            
        def toggle_sort(col):
            if st.session_state.am_sort_col == col:
                st.session_state.am_sort_asc = not st.session_state.am_sort_asc
            else:
                st.session_state.am_sort_col = col
                st.session_state.am_sort_asc = False if col != 'AM' else True
        
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
        
        with st.container(border=True):
            # --- TABLE HEADER ---
            head1, head2, head3, head4, head5, head6 = st.columns([2.0, 1.0, 0.8, 0.8, 0.8, 1.1])
            
            def sort_icon(col):
                if st.session_state.am_sort_col == col:
                    return " ↑" if st.session_state.am_sort_asc else " ↓"
                return ""
    
            with head1:
                st.button(f"👤 Name / Level{sort_icon('AM')}", on_click=toggle_sort, args=('AM',), key="sort_am_name", type="tertiary")
            with head2:
                st.button(f"📦 Shipments{sort_icon('Shipments')}", on_click=toggle_sort, args=('Shipments',), key="sort_am_ship", type="tertiary")
            with head3:
                st.button(f" 0-2 Days{sort_icon('Ageing_0_2')}", on_click=toggle_sort, args=('Ageing_0_2',), key="sort_am_a02", type="tertiary")
            with head4:
                st.button(f"🟡 3-5 Days{sort_icon('Ageing_3_5')}", on_click=toggle_sort, args=('Ageing_3_5',), key="sort_am_a35", type="tertiary")
            with head5:
                st.button(f"🔴 5+ Days{sort_icon('Ageing_5_plus')}", on_click=toggle_sort, args=('Ageing_5_plus',), key="sort_am_a5p", type="tertiary")
            with head6:
                st.button(f"💸 5+ Debit{sort_icon('Debit_5_plus')}", on_click=toggle_sort, args=('Debit_5_plus',), key="sort_am_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            # Group Level 1: AM
            am_groups = hier_df.groupby('AM').agg(
                Shipments=('AM', 'count'),
                Ageing_0_2=('Ageing_0_2', 'sum'),
                Ageing_3_5=('Ageing_3_5', 'sum'),
                Ageing_5_plus=('Ageing_5_plus', 'sum'),
                Debit_5_plus=('Debit_5_plus', 'sum')
            ).reset_index()
            
            # Apply sorting based on session state
            am_groups = am_groups.sort_values(st.session_state.am_sort_col, ascending=st.session_state.am_sort_asc)
            
            for _, am_row in am_groups.iterrows():
                am_name = am_row['AM']
                am_ship = am_row['Shipments']
                am_a02 = am_row['Ageing_0_2']
                am_a35 = am_row['Ageing_3_5']
                am_a5p = am_row['Ageing_5_plus']
                am_d5p = am_row['Debit_5_plus']
                
                am_expanded = st.session_state.get(f"am_{am_name}", False)
                am_icon = "▼" if am_expanded else "▶"
                
                # Custom Table Row: AM
                c1, c2, c3, c4, c5, c6, c7 = st.columns([0.15, 1.85, 1.0, 0.8, 0.8, 0.8, 1.1])
                expand_am = c1.checkbox(f"{am_icon}", key=f"am_{am_name}")
                with c2:
                    if st.button(f"AM: {am_name}", key=f"btn_prev_am_{am_name}", type="tertiary"):
                        show_data_preview(f"AM: {am_name}", hier_df[hier_df['AM'] == am_name])
                c3.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{am_ship:,}</b></p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{am_a02:,}</b></p>", unsafe_allow_html=True)
                c5.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{am_a35:,}</b></p>", unsafe_allow_html=True)
                c6.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{am_a5p:,}</b></p>", unsafe_allow_html=True)
                c7.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{format_indian_currency(am_d5p)}</b></p>", unsafe_allow_html=True)
                
                if expand_am:
                    am_df = hier_df[hier_df['AM'] == am_name]
                    
                    # Group Level 2: SL
                    sl_groups = am_df.groupby('SL').agg(
                        Shipments=('SL', 'count'),
                        Ageing_0_2=('Ageing_0_2', 'sum'),
                        Ageing_3_5=('Ageing_3_5', 'sum'),
                        Ageing_5_plus=('Ageing_5_plus', 'sum'),
                        Debit_5_plus=('Debit_5_plus', 'sum')
                    ).reset_index()
                    sl_groups = sl_groups.sort_values('Shipments', ascending=False)
                    
                    for _, sl_row in sl_groups.iterrows():
                        sl_name = sl_row['SL']
                        sl_ship = sl_row['Shipments']
                        sl_a02 = sl_row['Ageing_0_2']
                        sl_a35 = sl_row['Ageing_3_5']
                        sl_a5p = sl_row['Ageing_5_plus']
                        sl_d5p = sl_row['Debit_5_plus']
                        
                        sl_expanded = st.session_state.get(f"sl_{am_name}_{sl_name}", False)
                        sl_icon = "▼" if sl_expanded else "▶"
                        
                        # Custom Table Row: SL (Indented visually)
                        sc_space, sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([0.1, 0.15, 1.75, 1.0, 0.8, 0.8, 0.8, 1.1])
                        expand_sl = sc1.checkbox(f"{sl_icon}", key=f"sl_{am_name}_{sl_name}")
                        with sc2:
                            if st.button(f"SL: {sl_name}", key=f"btn_prev_sl_{am_name}_{sl_name}", type="tertiary"):
                                show_data_preview(f"SL: {sl_name}", am_df[am_df['SL'] == sl_name])
                        sc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{sl_ship:,}</p>", unsafe_allow_html=True)
                        sc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{sl_a02:,}</p>", unsafe_allow_html=True)
                        sc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{sl_a35:,}</p>", unsafe_allow_html=True)
                        sc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{sl_a5p:,}</p>", unsafe_allow_html=True)
                        sc7.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(sl_d5p)}</p>", unsafe_allow_html=True)
                        
                        if expand_sl:
                            sl_df = am_df[am_df['SL'] == sl_name]
                            
                            # Group Level 3: Hub (Displayed as clickable text rows)
                            hub_groups = sl_df.groupby('current_hub').agg(
                                Shipments=('current_hub', 'count'),
                                Ageing_0_2=('Ageing_0_2', 'sum'),
                                Ageing_3_5=('Ageing_3_5', 'sum'),
                                Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                Debit_5_plus=('Debit_5_plus', 'sum')
                            ).reset_index()
                            hub_groups = hub_groups.sort_values('Shipments', ascending=False)
                            
                            for _, hub_row in hub_groups.iterrows():
                                hub_name = hub_row['current_hub']
                                h_ship = hub_row['Shipments']
                                h_a02 = hub_row['Ageing_0_2']
                                h_a35 = hub_row['Ageing_3_5']
                                h_a5p = hub_row['Ageing_5_plus']
                                h_d5p = hub_row['Debit_5_plus']
                                
                                hc_space, hc1, hc2, hc3, hc4, hc5, hc6 = st.columns([0.35, 1.65, 1.0, 0.8, 0.8, 0.8, 1.1])
                                with hc1:
                                    if st.button(f"{hub_name}", key=f"btn_hub_{am_name}_{sl_name}_{hub_name}", type="tertiary"):
                                        show_data_preview(f"{hub_name}", sl_df[sl_df['current_hub'] == hub_name])
                                
                                hc2.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_ship:,}</p>", unsafe_allow_html=True)
                                hc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_a02:,}</p>", unsafe_allow_html=True)
                                hc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_a35:,}</p>", unsafe_allow_html=True)
                                hc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_a5p:,}</p>", unsafe_allow_html=True)
                                hc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(h_d5p)}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("POD > State Head > Hub")
        
        with st.container(height=520, border=True):
            # --- POD TABLE HEADER ---
            p_head1, p_head2, p_head3, p_head4, p_head5, p_head6 = st.columns([2.0, 1.0, 0.8, 0.8, 0.8, 1.1])
            
            def pod_sort_icon(col):
                if st.session_state.pod_sort_col == col:
                    return " ↑" if st.session_state.pod_sort_asc else " ↓"
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
                    if st.button(f"POD: {pod_name}", key=f"btn_prev_pod_{pod_name}", type="tertiary"):
                        show_data_preview(f"POD: {pod_name}", hier_df[hier_df['POD Zone'] == pod_name])
                c3.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{pod_ship:,}</b></p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{pod_a02:,}</b></p>", unsafe_allow_html=True)
                c5.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{pod_a35:,}</b></p>", unsafe_allow_html=True)
                c6.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{pod_a5p:,}</b></p>", unsafe_allow_html=True)
                c7.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{format_indian_currency(pod_d5p)}</b></p>", unsafe_allow_html=True)
                
                if expand_pod:
                    pod_df = hier_df[hier_df['POD Zone'] == pod_name]
                    
                    # Group Level 2: State Head
                    state_groups = pod_df.groupby('State Head').agg(
                        Shipments=('State Head', 'count'),
                        Ageing_0_2=('Ageing_0_2', 'sum'),
                        Ageing_3_5=('Ageing_3_5', 'sum'),
                        Ageing_5_plus=('Ageing_5_plus', 'sum'),
                        Debit_5_plus=('Debit_5_plus', 'sum')
                    ).reset_index()
                    state_groups = state_groups.sort_values('Shipments', ascending=False)
                    
                    for _, state_row in state_groups.iterrows():
                        state_name = state_row['State Head']
                        state_ship = state_row['Shipments']
                        state_a02 = state_row['Ageing_0_2']
                        state_a35 = state_row['Ageing_3_5']
                        state_a5p = state_row['Ageing_5_plus']
                        state_d5p = state_row['Debit_5_plus']
                        
                        state_expanded = st.session_state.get(f"state_{pod_name}_{state_name}", False)
                        state_icon = "▼" if state_expanded else "▶"
                        
                        # Custom Table Row: State Head (Indented visually)
                        sc_space, sc1, sc2, sc3, sc4, sc5, sc6, sc7 = st.columns([0.1, 0.15, 1.75, 1.0, 0.8, 0.8, 0.8, 1.1])
                        expand_state = sc1.checkbox(f"{state_icon}", key=f"state_{pod_name}_{state_name}")
                        with sc2:
                            if st.button(f"State Head: {state_name}", key=f"btn_prev_state_{pod_name}_{state_name}", type="tertiary"):
                                show_data_preview(f"State Head: {state_name}", pod_df[pod_df['State Head'] == state_name])
                        sc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{state_ship:,}</p>", unsafe_allow_html=True)
                        sc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{state_a02:,}</p>", unsafe_allow_html=True)
                        sc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{state_a35:,}</p>", unsafe_allow_html=True)
                        sc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{state_a5p:,}</p>", unsafe_allow_html=True)
                        sc7.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(state_d5p)}</p>", unsafe_allow_html=True)
                        
                        if expand_state:
                            state_df = pod_df[pod_df['State Head'] == state_name]
                            
                            # Group Level 3: Hub (Displayed as clickable text rows)
                            hub_groups = state_df.groupby('current_hub').agg(
                                Shipments=('current_hub', 'count'),
                                Ageing_0_2=('Ageing_0_2', 'sum'),
                                Ageing_3_5=('Ageing_3_5', 'sum'),
                                Ageing_5_plus=('Ageing_5_plus', 'sum'),
                                Debit_5_plus=('Debit_5_plus', 'sum')
                            ).reset_index()
                            hub_groups = hub_groups.sort_values('Shipments', ascending=False)
                            
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
                                
                                hc2.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_ship:,}</p>", unsafe_allow_html=True)
                                hc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_a02:,}</p>", unsafe_allow_html=True)
                                hc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_a35:,}</p>", unsafe_allow_html=True)
                                hc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{h_a5p:,}</p>", unsafe_allow_html=True)
                                hc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(h_d5p)}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)

    with tab_hubs:
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
        
        with st.container(border=True):
            # --- TABLE HEADER ---
            h_head1, h_head_am, h_head2, h_head3, h_head4, h_head5, h_head6 = st.columns([1.2, 0.8, 1.0, 0.8, 0.8, 0.8, 1.1])
            
            def hub_sort_icon(col):
                if st.session_state.hub_sort_col == col:
                    return " ↑" if st.session_state.hub_sort_asc else " ↓"
                return ""
    
            with h_head1:
                st.button(f"👤 Hub Type / Name{hub_sort_icon('Hub Type')}", on_click=toggle_hub_sort, args=('Hub Type',), key="sort_hub_name", type="tertiary")
            with h_head_am:
                st.button("👤 AM", key="sort_hub_am_header", type="tertiary")
            with h_head2:
                st.button(f"📦 Shipments{hub_sort_icon('Shipments')}", on_click=toggle_hub_sort, args=('Shipments',), key="sort_hub_ship", type="tertiary")
            with h_head3:
                st.button(f"🟢 0-2 Days{hub_sort_icon('Ageing_0_2')}", on_click=toggle_hub_sort, args=('Ageing_0_2',), key="sort_hub_a02", type="tertiary")
            with h_head4:
                st.button(f"🟡 3-5 Days{hub_sort_icon('Ageing_3_5')}", on_click=toggle_hub_sort, args=('Ageing_3_5',), key="sort_hub_a35", type="tertiary")
            with h_head5:
                st.button(f"🔴 5+ Days{hub_sort_icon('Ageing_5_plus')}", on_click=toggle_hub_sort, args=('Ageing_5_plus',), key="sort_hub_a5p", type="tertiary")
            with h_head6:
                st.button(f"💸 5+ Debit{hub_sort_icon('Debit_5_plus')}", on_click=toggle_hub_sort, args=('Debit_5_plus',), key="sort_hub_d5p", type="tertiary")
            st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
            
            # Group Level 1: Hub Type
            hub_type_groups = hier_df.groupby('Hub Type').agg(
                Shipments=('Hub Type', 'count'),
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
                ht_a02 = ht_row['Ageing_0_2']
                ht_a35 = ht_row['Ageing_3_5']
                ht_a5p = ht_row['Ageing_5_plus']
                ht_d5p = ht_row['Debit_5_plus']
                
                ht_expanded = st.session_state.get(f"ht_{ht_name}", False)
                ht_icon = "▼" if ht_expanded else "▶"
                
                # Custom Table Row: Hub Type
                c1, c2, c3, c4, c5, c6, c7 = st.columns([0.15, 1.85, 1.0, 0.8, 0.8, 0.8, 1.1])
                expand_ht = c1.checkbox(f"{ht_icon}", key=f"ht_{ht_name}")
                with c2:
                    if st.button(f"{ht_name}", key=f"btn_prev_ht_{ht_name}", type="tertiary"):
                        show_data_preview(f"{ht_name}", hier_df[hier_df['Hub Type'] == ht_name])
                c3.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{ht_ship:,}</b></p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{ht_a02:,}</b></p>", unsafe_allow_html=True)
                c5.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{ht_a35:,}</b></p>", unsafe_allow_html=True)
                c6.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{ht_a5p:,}</b></p>", unsafe_allow_html=True)
                c7.markdown(f"<p style='margin: 0; padding-top: 2px;'><b>{format_indian_currency(ht_d5p)}</b></p>", unsafe_allow_html=True)
                
                if expand_ht:
                    ht_df = hier_df[hier_df['Hub Type'] == ht_name]
                    
                    # Group Level 2: Hub & AM
                    hub_am_groups = ht_df.groupby(['current_hub', 'AM']).agg(
                        Shipments=('current_hub', 'count'),
                        Ageing_0_2=('Ageing_0_2', 'sum'),
                        Ageing_3_5=('Ageing_3_5', 'sum'),
                        Ageing_5_plus=('Ageing_5_plus', 'sum'),
                        Debit_5_plus=('Debit_5_plus', 'sum')
                    ).reset_index()
                    hub_am_groups = hub_am_groups.sort_values('Shipments', ascending=False)
                    
                    for _, ham_row in hub_am_groups.iterrows():
                        ham_hub = ham_row['current_hub']
                        ham_am = ham_row['AM']
                        ham_ship = ham_row['Shipments']
                        ham_a02 = ham_row['Ageing_0_2']
                        ham_a35 = ham_row['Ageing_3_5']
                        ham_a5p = ham_row['Ageing_5_plus']
                        ham_d5p = ham_row['Debit_5_plus']
                        
                        # Custom Table Row: Hub Name & AM (Indented visually)
                        hc_space, hc_hub, hc_am, hc2, hc3, hc4, hc5, hc6 = st.columns([0.15, 1.05, 0.8, 1.0, 0.8, 0.8, 0.8, 1.1])
                        with hc_hub:
                            if st.button(f"{ham_hub}", key=f"btn_hub_am_{ht_name}_{ham_hub}_{ham_am}", type="tertiary"):
                                show_data_preview(f"{ham_hub}", ht_df[(ht_df['current_hub'] == ham_hub) & (ht_df['AM'] == ham_am)])
                        
                        hc_am.markdown(f"<p style='margin: 0; padding-top: 2px;'>{ham_am}</p>", unsafe_allow_html=True)
                        
                        hc2.markdown(f"<p style='margin: 0; padding-top: 2px;'>{ham_ship:,}</p>", unsafe_allow_html=True)
                        hc3.markdown(f"<p style='margin: 0; padding-top: 2px;'>{ham_a02:,}</p>", unsafe_allow_html=True)
                        hc4.markdown(f"<p style='margin: 0; padding-top: 2px;'>{ham_a35:,}</p>", unsafe_allow_html=True)
                        hc5.markdown(f"<p style='margin: 0; padding-top: 2px;'>{ham_a5p:,}</p>", unsafe_allow_html=True)
                        hc6.markdown(f"<p style='margin: 0; padding-top: 2px;'>{format_indian_currency(ham_d5p)}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
        