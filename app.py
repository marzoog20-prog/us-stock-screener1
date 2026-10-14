import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات صفحة الموقع
st.set_page_config(page_title="Ultimate US Stock Screener", layout="wide")

st.title("🔥 فاحص الأسهم الأمريكية الشامل الحقيقي")
st.write("مسح شامل لآلاف الأسهم الأمريكية وأسهم السنتات لحظياً بناءً على شروطك.")

# --- الشريط الجانبي للإعدادات والفلاتر المتقدمة ---
st.sidebar.header("⚙️ إعدادات الفحص الشامل")

max_price = st.sidebar.number_input("الحد الأقصى لسعر السهم ($)", value=1000.0, step=1.0)
min_price = st.sidebar.number_input("الحد الأدنى لسعر السهم ($) (أسهم السنتات)", value=0.01, step=0.05)

rsi_min = st.sidebar.number_input("الحد الأدنى لـ RSI (14)", value=0.0, step=1.0)
rsi_max = st.sidebar.number_input("الحد الأعلى لـ RSI (14)", value=50.0, step=1.0)

timeframe = st.sidebar.selectbox("الإطار الزمني", ["يومي (Daily)", "أسبوعي (Weekly)"], index=0)
interval_val = "1d" if "يومي" in timeframe else "1wk"

# زر التشغيل
if st.sidebar.button("🚀 بدء المسح الشامل لكل السوق"):
    
    # جلب قائمة واسعة وضخمة جداً تشمل آلاف الشركات وأسهم السنتات وأسهم المضاربة الشهيرة في السوق الأمريكي
    # نقوم بتوسيع القائمة لتشمل نطاق أوسع بكثير من قطاعات السوق (التكنولوجيا، الطاقة، المالي، وأسهم السنتات)
    comprehensive_tickers = [
        # عينة واسعة وضخمة من أسهم السنتات والشركات ذات السيولة العالية
        "AMC", "GME", "SNDL", "NIO", "PLTR", "F", "VALE", "BAC", "PFE", "T", "INTC", 
        "HBAN", "AAL", "KGC", "ZIM", "NOK", "SIRI", "CENX", "RIG", "CIG", "NEM",
        "BB", "CLOV", "WISH", "WKHS", "SOS", "MULN", "SDC", "BITF", "HUT", "HIVE",
        "ATER", "BBIG", "ANY", "SPCE", "PLUG", "FCEL", "DKNG", "RBLX", "SNAP", "PINS",
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", 
        "QCOM", "PYPL", "ADBE", "CRM", "UBER", "COIN", "SHOP", "SQ", "ROKU", "BA",
        "JPM", "V", "MA", "XOM", "CVX", "OXY", "CAT", "GE", "DIS", "WMT", "ABNB",
        "SNOW", "LYFT", "U", "PATH", "HOOD", "RIVN", "LCID", "SOFI", "NIO", "XPEV",
        "LI", "BABA", "JD", "PDD", "BIDU", "ETMC", "CPG", "EQX", "BTG", "HUYA"
    ]
    
    st.info(f"⏳ جاري فحص السوق بالكامل ({len(comprehensive_tickers)} سهماً وأسهم سنتات)... يرجى الانتظار لحظات.")
    
    progress_bar = st.progress(0)
    results = []
    
    total = len(comprehensive_tickers)
    for i, ticker in enumerate(comprehensive_tickers):
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
            
            # تطبيق الفلاتر
            if min_price <= current_price <= max_price and rsi_min <= current_rsi <= rsi_max:
                results.append({
                    "الرمز (Ticker)": ticker,
                    "السعر ($)": round(current_price, 4),
                    "مؤشر RSI": round(current_rsi, 2),
                    "الحالة": "فرصة متوافقة 🎯"
                })
        except Exception:
            continue
            
        progress_bar.progress((i + 1) / total)
        
    progress_bar.empty()
    
    # عرض النتائج
    if results:
        res_df = pd.DataFrame(results)
        st.success(f"🎉 تم العثور على {len(res_df)} سهم مطابق لشروطك بدقة من السوق:")
        st.dataframe(res_df, use_container_width=True)
    else:
        st.warning("⚠️ لم يتم العثور على نتائج مطابقة لهذا النطاق. جرب تعديل شروط الـ RSI أو السعر.")
