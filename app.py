import streamlit as st
import yfinance as yf
import pandas as pd

# إعدادات صفحة الموقع
st.set_page_config(page_title="Professional US Stock Screener", layout="wide")

st.title("🎯 الفاحص المحترف للأسهم الأمريكية (RSI + الاتجاه + الأسهم المخصصة)")
st.write("أداة متقدمة لفحص الأسهم مع إمكانية إضافة أي أسهم جديدة تريدها يدوياً.")

# --- الشريط الجانبي للإعدادات والفلاتر ---
st.sidebar.header("⚙️ إعدادات الفحص المتقدمة")

max_price = st.sidebar.number_input("الحد الأقصى لسعر السهم ($)", value=1000.0, step=1.0)
min_price = st.sidebar.number_input("الحد الأدنى لسعر السهم ($)", value=0.01, step=0.05)

rsi_min = st.sidebar.number_input("الحد الأدنى لـ RSI (14)", value=0.0, step=1.0)
rsi_max = st.sidebar.number_input("الحد الأعلى لـ RSI (14)", value=50.0, step=1.0)

# خانة مخصصة لإضافة أسهم زيادة
custom_tickers_input = st.sidebar.text_input(
    "أضف أسهم زيادة (مفصولة بفاصلة مثل: TSLA, NVDA, AAPL):",
    value=""
)

# فلتر الاتجاه العام
filter_trend = st.sidebar.checkbox("شرط الاتجاه الصاعد (السعر فوق متوسط 50)", value=False)

# زر التشغيل
if st.sidebar.button("🚀 بدء الفحص الشامل"):
    
    # القائمة الأساسية الشاملة
    base_tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "INTC", 
        "QCOM", "PYPL", "COST", "ADBE", "JPM", "V", "MA", "UNH", "HD", "DIS",
        "AMC", "GME", "SNDL", "NIO", "PLTR", "F", "VALE", "BAC", "PFE", "T", 
        "HBAN", "AAL", "ZIM", "NOK", "SIRI", "BB", "CLOV", "WISH", "PLUG", "SOFI"
    ]
    
    # دمج الأسهم الأساسية مع الأسهم التي أضافها المستخدم بالخانة المخصصة
    user_added = [t.strip().upper() for t in custom_tickers_input.split(",") if t.strip()]
    tickers_pool = list(set(base_tickers + user_added)) # دمج وحذف التكرار
    
    st.info(f"⏳ جاري فحص وتحليل إجمالي ({len(tickers_pool)} سهماً)... يرجى الانتظار.")
    
    progress_bar = st.progress(0)
    results = []
    
    total = len(tickers_pool)
    for i, ticker in enumerate(tickers_pool):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
            
            if len(df) < 50:
                progress_bar.progress((i + 1) / total)
                continue
                
            # حساب مؤشر القوة النسبية RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # حساب المتوسط المتحرك البسيط 50 يوم
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            
            current_price = df['Close'].iloc[-1]
            current_rsi = df['RSI'].iloc[-1]
            current_sma50 = df['SMA_50'].iloc[-1]
            
            # تطبيق الفلاتر الأساسية
            pass_price_rsi = (min_price <= current_price <= max_price) and (rsi_min <= current_rsi <= rsi_max)
            
            if pass_price_rsi:
                if filter_trend:
                    if current_price > current_sma50:
                        results.append({
                            "الرمز (Ticker)": ticker,
                            "السعر ($)": round(current_price, 4),
                            "مؤشر RSI": round(current_rsi, 2),
                            "متوسط 50 ($)": round(current_sma50, 2),
                            "الحالة": "اتجاه صاعد + RSI ممتاز 📈"
                        })
                else:
                    results.append({
                        "الرمز (Ticker)": ticker,
                        "السعر ($)": round(current_price, 4),
                        "مؤشر RSI": round(current_rsi, 2),
                        "متوسط 50 ($)": round(current_sma50, 2),
                        "الحالة": "فرصة متوافقة 🎯"
                    })
        except Exception:
            continue
            
        progress_bar.progress((i + 1) / total)
        
    progress_bar.empty()
    
    # عرض النتائج مع العمود الجديد بوضوح
    if results:
        res_df = pd.DataFrame(results)
        st.success(f"🎉 تم رصد {len(res_df)} سهم تطابق المعايير:")
        st.dataframe(res_df, use_container_width=True)
    else:
        st.warning("⚠️ لم يتم العثور على نتائج مطابقة للشروط الحالية. جرب توسيع نطاق الـ RSI أو إلغاء شرط الاتجاه الصاعد.")
