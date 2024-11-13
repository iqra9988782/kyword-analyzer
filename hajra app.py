# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join(text.split())
    return text

def get_keyword_suggestions(keyword):
    modifiers = {
        'commercial': ["buy", "price", "cheap", "best", "top", "online", "shop", "store"],
        'informational': ["how to", "what is", "guide", "tutorial", "tips", "vs", "review"],
        'local': ["near me", "in city", "local", "shipping", "delivery"],
        'specific': ["for sale", "professional", "services", "cost"]
    }
    
    suggestions = []
    clean_keyword = clean_text(keyword)
    
    for category, words in modifiers.items():
        for word in words:
            suggestions.append({
                'keyword': f"{clean_keyword} {word}",
                'type': category
            })
    
    return suggestions

def calculate_keyword_metrics(keyword):
    import random
    seed = sum(ord(c) for c in keyword)
    random.seed(seed)
    
    base_volume = random.randint(1000, 50000)
    word_count = len(keyword.split())
    
    return {
        "monthly_volume": int(base_volume / (word_count ** 0.5)),
        "competition": round(random.uniform(0.1, 1.0), 2),
        "difficulty": round(random.uniform(1, 100), 1),
        "cpc": round(random.uniform(0.5, 5.0), 2)
    }

def main():
    st.set_page_config(page_title="Advanced Keyword Analyzer", layout="wide")
    
    st.markdown("""
        <style>
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🔍 Advanced Keyword Analyzer")
    
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    with st.sidebar:
        st.header("📋 Search History")
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.success("History cleared!")
        
        for idx, item in enumerate(reversed(st.session_state.history[-10:])):
            st.text(f"{len(st.session_state.history) - idx}. {item}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("Enter your keyword:", key="keyword_input", 
                              placeholder="Type your keyword here...")
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary")
    
    if analyze_button and keyword:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        if keyword not in st.session_state.history:
            st.session_state.history.append(f"{keyword} ({timestamp})")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        import time
        for i in range(100):
            progress_bar.progress(i + 1)
            if i == 30:
                status_text.text("Analyzing keyword metrics...")
            elif i == 60:
                status_text.text("Generating suggestions...")
            elif i == 90:
                status_text.text("Preparing results...")
            time.sleep(0.01)
        
        status_text.empty()
        progress_bar.empty()
        
        st.subheader("📊 Keyword Metrics")
        metrics = calculate_keyword_metrics(keyword)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Monthly Volume", f"{metrics['monthly_volume']:,}")
        col2.metric("Competition", f"{metrics['competition']:.2f}")
        col3.metric("Difficulty", f"{metrics['difficulty']:.1f}")
        col4.metric("CPC", f"${metrics['cpc']}")
        
        st.subheader("💡 Keyword Suggestions")
        suggestions = get_keyword_suggestions(keyword)
        
        suggestions_data = []
        for sugg in suggestions:
            metrics = calculate_keyword_metrics(sugg['keyword'])
            suggestions_data.append({
                "Keyword": sugg['keyword'],
                "Type": sugg['type'].capitalize(),
                "Monthly Volume": metrics["monthly_volume"],
                "Competition": metrics["competition"],
                "Difficulty": metrics["difficulty"],
                "CPC": metrics["cpc"]
            })
        
        df_suggestions = pd.DataFrame(suggestions_data)
        
        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.multiselect(
                "Filter by Type:",
                options=df_suggestions["Type"].unique(),
                default=df_suggestions["Type"].unique()
            )
        
        with col2:
            volume_filter = st.slider(
                "Minimum Monthly Volume:",
                min_value=0,
                max_value=int(df_suggestions["Monthly Volume"].max()),
                value=0
            )
        
        filtered_df = df_suggestions[
            (df_suggestions["Type"].isin(type_filter)) &
            (df_suggestions["Monthly Volume"] >= volume_filter)
        ]
        
        st.dataframe(
            filtered_df.style.background_gradient(subset=["Monthly Volume"], cmap="Blues"),
            use_container_width=True
        )
        
        st.subheader("📈 Volume vs Competition Analysis")
        fig = px.scatter(
            filtered_df,
            x="Competition",
            y="Monthly Volume",
            size="CPC",
            color="Type",
            hover_data=["Keyword"],
            title="Keyword Analysis Matrix"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.download_button(
            label="📥 Download Analysis (CSV)",
            data=filtered_df.to_csv(index=False),
            file_name=f"keyword_analysis_{keyword}_{timestamp.replace(':', '-')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
