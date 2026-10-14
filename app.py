import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات صفحة الموقع
st.set_page_config(page_title="US Stock Screener", layout="wide")

st.title("📊 استراتيجية فحص الأسهم الأمريكية (US Stocks)")
st.write("موقعك الخاص لفحص وفرز مئات الأسهم الأمريكية تلقائياً بناءً على المؤشرات الفنية.")

# --- الشريط الجانبي للإعدادات والفلاتر ---
st.sidebar.header("⚙️ إعدادات الفحص الأساسية")

# قائمة واسعة وشاملة لأشهر الأسهم الأمريكية تلقائياً لكي لا تحتاج لكتابتها
default_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", 
    "QCOM", "PYPL", "PEP", "COST", "ADBE", "JPM", "V", "MA", "UNH", "HD", 
    "PG", "JNJ", "XOM", "CVX", "BAC", "PFE", "ABBV", "KO", "DIS", "MRK", 
    "T", "VZ", "WMT", "NKE", "IBM", "ORCL", "CRM", "BA", "CAT", "GE"
]

st.sidebar.write(f"📈 جاري فحص قائمة تلقائية تضم {len(default_tickers)} شركة كبرى في السوق الأمريكي.")

st.sidebar.header("📉 المؤشرات الفنية")
rsi_min = st.sidebar.number_input("الحد الأدنى لـ RSI (14)", value=0.0, step=1.0)
rsi_max = st.sidebar.number_input("الحد الأقصى لـ RSI (14)", value=50.0, step=1.0)

# الإطار الزمني
timeframe = st.sidebar.selectbox("الإطار الزمني", ["يومي (Daily)", "أسبوعي (Weekly)"], index=0)
interval_val = "1d" if "يومي" in timeframe else "1wk"

# زر بدء الفحص
if st.sidebar.button("بدء الفحص التلقائي 🚀"):
    st.info("جاري سحب وفحص الأسهم الأمريكية تلقائياً... يرجى الانتظار قليلاً.")
    
    results = []
    
    for ticker in default_tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo", interval=interval_val)
            
            if len(df) < 20:
                continue
                
            # حساب مؤشر القوة النسبية RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            current_price = df['Close'].iloc[-1]
            current_rsi = df['RSI'].iloc[-1]
            
            # تطبيق الفلاتر
            if rsi_min <= current_rsi <= rsi_max:
                results.append({
                    "الرمز (Ticker)": ticker,
                    "السعر الحالي ($)": round(current_price, 2),
                    "مؤشر RSI": round(current_rsi, 2),
                    "الحالة": "جاهز للصعود 📈"
                })
        except Exception as e:
            continue
            
    # عرض النتائج
    if results:
        res_df = pd.DataFrame(results)
        st.success(f"تم العثور على {len(res_df)} سهم مطابق لشروطك من القائمة التلقائية:")
        st.dataframe(res_df, use_container_width=True)
    else:
        st.warning("لم يتم العثور على أسهم تطابق الشروط الحالية، جرب توسيع نطاق الـ RSI.")
