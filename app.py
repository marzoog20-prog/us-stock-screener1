import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات صفحة الموقع الاحترافية
st.set_page_config(page_title="Ultimate US Stock Screener", layout="wide")

st.title("🔥 فاحص الأسهم الأمريكية الشامل (السوق الكامل وأسهم السنتات)")
st.write("أداتك الاحترافية لمسح مئات الأسهم الأمريكية وأسهم السنتات لحظياً.")

# --- الشريط الجانبي للإعدادات والفلاتر المتقدمة ---
st.sidebar.header("⚙️ إعدادات الفحص المتقدمة")

st.sidebar.header("📉 الفلاتر الفنية والمالية")
max_price = st.sidebar.number_input("الحد الأقصى لسعر السهم ($)", value=1000.0, step=1.0)
min_price = st.sidebar.number_input("الحد الأدنى لسعر السهم ($) (لأسهم السنتات)", value=0.01, step=0.05)

rsi_min = st.sidebar.number_input("الحد الأدنى لـ RSI (14)", value=0.0, step=1.0)
rsi_max = st.sidebar.number_input("الحد الأقصى لـ RSI (14)", value=50.0, step=1.0)

timeframe = st.sidebar.selectbox("الإطار الزمني", ["يومي (Daily)", "أسبوعي (Weekly)"], index=0)
interval_val = "1d" if "يومي" in timeframe else "1wk"

# زر التشغيل
if st.sidebar.button("🚀 بدء المسح الشامل لكل السوق"):
    
    # قائمة واسعة وضخمة تضم مئات الأسهم القيادية وأسهم السنتات والشركات المتقلبة
    large_universe = [
        # أسهم السنتات والمضاربة الشهيرة
        "AMC", "GME", "SNDL", "NIO", "PLTR", "F", "VALE", "BAC", "PFE", "T", "INTC", 
        "HBAN", "AAL", "KGC", "ZIM", "NOK", "SIRI", "CENX", "RIG", "CIG", "NEM",
        "BB", "CLOV", "WISH", "WKHS", "SBE", "SOS", "NTEC", "CIDM", "CEI", "PROG",
        "MULN", "SDC", "BITF", "HUT", "HIVE", "ATER", "BBIG", "ANY", "IRNT", "SPCE",
        # الأسهم الكبرى والتقنية والنمو
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", 
        "QCOM", "PYPL", "ADBE", "CRM", "UBER", "COIN", "SHOP", "SQ", "ROKU", "SNAP",
        "JPM", "V", "MA", "XOM", "CVX", "OXY", "BA", "CAT", "GE", "DIS", "WMT",
        "ABNB", "SNOW", "PLDD", "PINS", "TWTR", "LYFT", "DKNG", "RBLX", "U", "PATH"
    ]
    
    st.info(f"⏳ جاري مسح وتحليل {len(large_universe)} سهماً في السوق الأمريكي وتطبيق الشروط...")
    
    progress_bar = st.progress(0)
    results = []
    
    total = len(large_universe)
    for i, ticker in enumerate(large_universe):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="3mo", interval=interval_val)
            
            if len(df) < 14:
                progress_bar.progress((i + 1) / total)
                continue
                
            # حساب مؤشر القوة النسبية RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            current_price = df['Close'].iloc[-1]
            current_rsi = df['RSI'].iloc[-1]
            
            # تطبيق شروط السعر والفلاتر الفنية
            if min_price <= current_price <= max_price and rsi_min <= current_rsi <= rsi_max:
                results.append({
                    "الرمز (Ticker)": ticker,
                    "السعر الحالي ($)": round(current_price, 4),
                    "مؤشر RSI": round(current_rsi, 2),
                    "الحالة الفنية": "فرصة محتملة 🎯"
                })
        except Exception:
            continue
            
        progress_bar.progress((i + 1) / total)
        
    progress_bar.empty()
    
    # عرض النتائج
    if results:
        res_df = pd.DataFrame(results)
        st.success(f"🎉 تم بنجاح رصد {len(res_df)} سهم مطابق لمعاييرك الدقيقة:")
        st.dataframe(res_df, use_container_width=True)
    else:
        st.warning("⚠️ لم يتم العثور على أسهم تطابق الشروط الحالية. جرب توسيع نطاق الـ RSI أو نطاق الأسعار.")
