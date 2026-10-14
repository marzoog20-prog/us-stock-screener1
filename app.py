import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات صفحة الموقع
st.set_page_config(page_title="US Stock Screener", layout="wide")

st.title("📊 فاحص الأسهم الأمريكية الشامل (All US Stocks)")
st.write("ابحث وافحص أي سهم في السوق الأمريكي لحظياً بناءً على مؤشر RSI.")

# --- الشريط الجانبي للإعدادات والفلاتر ---
st.sidebar.header("⚙️ إبحث أو أدخل الرموز")

# طريقة مرنة تتيح لك كتابة أي رمز سهم تريده في السوق الأمريكي فوراً
user_tickers_input = st.sidebar.text_input(
    "أدخل رموز الأسهم مفصولة بفاصلة (مثال: AAPL, AMC, SNDL, TSLA, GME):",
    value="AAPL, MSFT, AMC, SNDL, GME, NIO, F, PLTR, PFE"
)

tickers = [t.strip().upper() for t in user_tickers_input.split(",") if t.strip()]

st.sidebar.header("📉 المؤشرات الفنية")
rsi_min = st.sidebar.number_input("الحد الأدنى لـ RSI (14)", value=0.0, step=1.0)
rsi_max = st.sidebar.number_input("الحد الأقصى لـ RSI (14)", value=70.0, step=1.0)

# الإطار الزمني
timeframe = st.sidebar.selectbox("الإطار الزمني", ["يومي (Daily)", "أسبوعي (Weekly)"], index=0)
interval_val = "1d" if "يومي" in timeframe else "1wk"

# زر بدء الفحص
if st.sidebar.button("بدء الفحص الشامل 🚀"):
    if not tickers:
        st.warning("الرجاء إدخال رمز سهم واحد على الأقل في القائمة الجانبية.")
    else:
        st.info("جاري فحص الأسهم المطلوبة من السوق الأمريكي مباشرة... يرجى الانتظار.")
        
        results = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="3mo", interval=interval_val)
                
                if len(df) < 14:
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
                        "السعر الحالي ($)": round(current_price, 4), # يدعم أسهم السنتات بدقة بأجزاء الـ سنت
                        "مؤشر RSI": round(current_rsi, 2),
                        "الحالة": "متاح ضمن الشروط 📊"
                    })
            except Exception as e:
                continue
                
        # عرض النتائج
        if results:
            res_df = pd.DataFrame(results)
            st.success(f"تم العثور على {len(res_df)} سهم مطابق:")
            st.dataframe(res_df, use_container_width=True)
        else:
            st.warning("لم يتم العثور على نتائج تطابق الشروط المدخلة لهذه الأسهم.")
