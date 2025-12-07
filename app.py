import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="US Stock Analysis App", layout="wide")

# ========================================
# Password Authentication
# ========================================
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["passwords"]["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show input for password
    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 US Stock Analysis App")
        st.markdown("### Please enter the password to access the application")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("💡 To change the password, edit the `.streamlit/secrets.toml` file")
        return False
    # Password not correct, show input + error
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 US Stock Analysis App")
        st.markdown("### Please enter the password to access the application")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect. Please try again.")
        st.info("💡 To change the password, edit the `.streamlit/secrets.toml` file")
        return False
    else:
        # Password correct
        return True

# Check password before showing the app
if not check_password():
    st.stop()  # Do not continue if check_password is not True

# ========================================
# Main Application (Only shown after authentication)
# ========================================

# Sidebar
st.sidebar.header("🔍 Stock Search")

# Mode Selection
search_mode = st.sidebar.radio("Search Mode", ["Single Stock Analysis", "Stock Screener"])

if search_mode == "Single Stock Analysis":
    ticker_symbol = st.sidebar.text_input("Ticker Symbol", value="AAPL").upper()
    period = st.sidebar.selectbox("Period", ("1mo", "3mo", "6mo", "1y", "2y", "5y"), index=3)
else:
    st.sidebar.subheader("📊 Filter Parameters")
    
    # Ticker Selection
    st.sidebar.write("**📋 Ticker Selection**")
    ticker_source = st.sidebar.radio(
        "Ticker Source",
        ["Default List", "Upload Custom List"],
        help="Choose to use default tickers or upload your own list"
    )
    
    if ticker_source == "Upload Custom List":
        uploaded_file = st.sidebar.file_uploader(
            "Upload ticker list (txt file, one ticker per line)",
            type=['txt'],
            help="Upload a text file with one ticker symbol per line"
        )
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                custom_tickers = [line.strip().upper() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
                st.sidebar.success(f"✅ Loaded {len(custom_tickers)} tickers from file")
                tickers_to_screen = custom_tickers
            except Exception as e:
                st.sidebar.error(f"❌ Error reading file: {str(e)}")
                tickers_to_screen = load_tickers_from_file()
        else:
            st.sidebar.info("👆 Please upload a ticker list file")
            tickers_to_screen = load_tickers_from_file()
    else:
        tickers_to_screen = load_tickers_from_file()
        st.sidebar.info(f"📊 Using {len(tickers_to_screen)} default tickers")
    
    st.sidebar.markdown("---")
    
    # Filter Selection
    filter_options = ["PER", "PBR", "ROE", "RSI", "MACD", "Market Cap", "Sector"]
    default_filters = ["PER", "PBR", "ROE", "RSI"]
    selected_filters = st.sidebar.multiselect("Select Active Filters", filter_options, default=default_filters)
    
    filters = {}
    
    # PER (Price to Earnings Ratio) Filter
    if "PER" in selected_filters:
        st.sidebar.write("**PER (Price to Earnings Ratio)**")
        filters["PER"] = st.sidebar.slider("PER Range", 0.0, 100.0, (0.0, 50.0), 1.0)
    
    # PBR (Price to Book Ratio) Filter
    if "PBR" in selected_filters:
        st.sidebar.write("**PBR (Price to Book Ratio)**")
        filters["PBR"] = st.sidebar.slider("PBR Range", 0.0, 20.0, (0.0, 10.0), 0.5)
    
    # ROE (Return on Equity) Filter
    if "ROE" in selected_filters:
        st.sidebar.write("**ROE (Return on Equity %)**")
        filters["ROE"] = st.sidebar.slider("ROE Range (%)", -50.0, 100.0, (0.0, 50.0), 5.0)
    
    # RSI Filter
    if "RSI" in selected_filters:
        st.sidebar.write("**RSI (Relative Strength Index)**")
        filters["RSI"] = st.sidebar.slider("RSI Range", 0.0, 100.0, (30.0, 70.0), 5.0)
        
    # MACD Filter
    if "MACD" in selected_filters:
        st.sidebar.write("**MACD Histogram (Momentum)**")
        filters["MACD"] = st.sidebar.slider("MACD Histogram Range", -10.0, 10.0, (-2.0, 2.0), 0.5)
    
    # Market Cap Filter
    if "Market Cap" in selected_filters:
        st.sidebar.write("**Market Cap**")
        market_cap_options = {
            "All": (0, float('inf')),
            "Mega Cap (>200B)": (200e9, float('inf')),
            "Large Cap (10B-200B)": (10e9, 200e9),
            "Mid Cap (2B-10B)": (2e9, 10e9),
            "Small Cap (<2B)": (0, 2e9)
        }
        market_cap_selection = st.sidebar.selectbox("Market Cap", list(market_cap_options.keys()))
        filters["Market Cap"] = market_cap_options[market_cap_selection]
    
    # Sector Filter
    if "Sector" in selected_filters:
        st.sidebar.write("**Sector**")
        sectors = ["All", "Technology", "Healthcare", "Financial Services", "Consumer Cyclical", 
                   "Communication Services", "Industrials", "Consumer Defensive", "Energy", 
                   "Utilities", "Real Estate", "Basic Materials"]
        sector_selection = st.sidebar.selectbox("Sector", sectors)
        filters["Sector"] = sector_selection
    
    # Search Button
    search_button = st.sidebar.button("🔍 Search Stocks", type="primary")
    
    period = "1y"  # Default period for screener

# Helper function to load tickers from file
@st.cache_data
def load_tickers_from_file(file_path="tickers.txt"):
    """Load ticker symbols from a text file."""
    try:
        with open(file_path, 'r') as f:
            tickers = [line.strip().upper() for line in f if line.strip() and not line.strip().startswith('#')]
        return tickers
    except FileNotFoundError:
        st.warning(f"⚠️ Ticker file '{file_path}' not found. Using default tickers.")
        # Fallback to default tickers
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "V", "JNJ",
            "WMT", "JPM", "MA", "PG", "UNH", "HD", "DIS", "BAC", "ADBE", "CRM",
            "NFLX", "CSCO", "PFE", "KO", "PEP", "INTC", "CMCSA", "VZ", "T", "MRK",
            "ABT", "NKE", "TMO", "COST", "AVGO", "ACN", "DHR", "TXN", "NEE", "LIN",
            "AMD", "QCOM", "UPS", "PM", "HON", "UNP", "RTX", "SBUX", "LOW", "IBM"
        ]
    except Exception as e:
        st.error(f"❌ Error loading ticker file: {str(e)}")
        return []

# Stock Screener Function with improved error handling
@st.cache_data
def screen_stocks(filters, tickers_list):
    """
    Screen stocks based on filters.
    
    Args:
        filters (dict): Dictionary of filter criteria
        tickers_list (list): List of ticker symbols to screen
    
    Returns:
        pd.DataFrame: DataFrame containing filtered stock data
    """
    results = []
    errors = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    error_container = st.empty()
    
    for idx, ticker in enumerate(tickers_list):
        try:
            status_text.text(f"Screening {ticker}... ({idx+1}/{len(tickers_list)})")
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="6mo") # Need enough data for MACD (26+9 days)
            
            if hist.empty:
                errors.append(f"{ticker}: No historical data available")
                continue
            
            # Get metrics
            per = info.get('trailingPE')
            pbr = info.get('priceToBook')
            roe = info.get('returnOnEquity')
            market_cap = info.get('marketCap')
            sector = info.get('sector', '')
            current_price = info.get('currentPrice', hist['Close'].iloc[-1] if not hist.empty else None)
            
            if current_price is None:
                errors.append(f"{ticker}: Unable to fetch current price")
                continue
            
            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            rsi = rsi_series.iloc[-1] if not rsi_series.empty else None
            
            # Calculate MACD
            exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
            macd_line = exp12 - exp26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist = macd_line - signal_line
            current_macd_hist = macd_hist.iloc[-1] if not macd_hist.empty else None

            # Apply filters
            
            # PER filter
            if "PER" in filters:
                if per is None or not (filters["PER"][0] <= per <= filters["PER"][1]):
                    continue
            
            # PBR filter
            if "PBR" in filters:
                if pbr is None or not (filters["PBR"][0] <= pbr <= filters["PBR"][1]):
                    continue
            
            # ROE filter
            if "ROE" in filters:
                if roe is None: continue
                roe_percent = roe * 100
                if not (filters["ROE"][0] <= roe_percent <= filters["ROE"][1]):
                    continue
            
            # RSI filter
            if "RSI" in filters:
                if rsi is None or not (filters["RSI"][0] <= rsi <= filters["RSI"][1]):
                    continue
            
            # MACD filter
            if "MACD" in filters:
                if current_macd_hist is None or not (filters["MACD"][0] <= current_macd_hist <= filters["MACD"][1]):
                    continue
            
            # Market Cap filter
            if "Market Cap" in filters:
                if market_cap is None or not (filters["Market Cap"][0] <= market_cap <= filters["Market Cap"][1]):
                    continue
            
            # Sector filter
            if "Sector" in filters:
                if filters["Sector"] != "All" and sector != filters["Sector"]:
                    continue
            
            # Add to results
            results.append({
                "Ticker": ticker,
                "Price": f"${current_price:.2f}",
                "PER": f"{per:.2f}" if per else "N/A",
                "PBR": f"{pbr:.2f}" if pbr else "N/A",
                "ROE": f"{roe*100:.2f}%" if roe else "N/A",
                "RSI": f"{rsi:.2f}" if rsi else "N/A",
                "MACD Hist": f"{current_macd_hist:.2f}" if current_macd_hist else "N/A",
                "Market Cap": f"${market_cap/1e9:.2f}B" if market_cap else "N/A",
                "Sector": sector
            })
            
        except KeyError as e:
            errors.append(f"{ticker}: Missing data field - {str(e)}")
        except ValueError as e:
            errors.append(f"{ticker}: Invalid data value - {str(e)}")
        except Exception as e:
            errors.append(f"{ticker}: {type(e).__name__} - {str(e)}")
        
        progress_bar.progress((idx + 1) / len(tickers_list))
    
    progress_bar.empty()
    status_text.empty()
    
    # Display errors if any
    if errors:
        with error_container.expander(f"⚠️ {len(errors)} errors occurred during screening", expanded=False):
            for error in errors[:10]:  # Show first 10 errors
                st.text(error)
            if len(errors) > 10:
                st.text(f"... and {len(errors) - 10} more errors")
    
    return pd.DataFrame(results)

# Main Content
if search_mode == "Single Stock Analysis":
    st.title(f"📈 Stock Analysis: {ticker_symbol}")
else:
    st.title("🔍 Stock Screener Results")

# Fetch Data
@st.cache_data
def get_stock_data(ticker, period):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    info = stock.info
    return hist, info

if search_mode == "Stock Screener":
    # Initialize session state for screener results
    if 'screener_results' not in st.session_state:
        st.session_state.screener_results = None
    if 'selected_ticker_from_screener' not in st.session_state:
        st.session_state.selected_ticker_from_screener = None
    
    if search_button:
        st.subheader("Filtered Stocks")
        results_df = screen_stocks(filters, tickers_to_screen)
        st.session_state.screener_results = results_df
        st.session_state.selected_ticker_from_screener = None  # Reset selection on new search
        
        if results_df.empty:
            st.warning("No stocks found matching the selected criteria. Try adjusting the filter parameters.")
            st.stop()
        else:
            st.success(f"Found {len(results_df)} stocks matching your criteria")
            st.dataframe(results_df, use_container_width=True, hide_index=True)
    
    # Display results if they exist in session state
    if st.session_state.screener_results is not None and not st.session_state.screener_results.empty:
        if not search_button:  # Only show if not just searched (to avoid duplicate display)
            st.subheader("Filtered Stocks")
            st.success(f"Found {len(st.session_state.screener_results)} stocks matching your criteria")
            st.dataframe(st.session_state.screener_results, use_container_width=True, hide_index=True)
        
        # Allow user to select a stock for detailed analysis
        st.subheader("Select a stock for detailed analysis")
        selected_ticker = st.selectbox(
            "Choose a ticker", 
            st.session_state.screener_results["Ticker"].tolist(),
            key="ticker_selector"
        )
        
        if selected_ticker:
            st.session_state.selected_ticker_from_screener = selected_ticker
            ticker_symbol = selected_ticker
            st.markdown("---")
            st.subheader(f"Detailed Analysis: {ticker_symbol}")
        else:
            st.stop()
    elif not search_button:
        st.info("👈 Set your filter parameters in the sidebar and click 'Search Stocks' to begin screening.")
        st.stop()

try:
    hist, info = get_stock_data(ticker_symbol, period)
    
    if hist.empty:
        st.error("No data found for this ticker. Please check the symbol.")
    else:
        # --- Header Info ---
        current_price = info.get('currentPrice', hist['Close'].iloc[-1])
        previous_close = info.get('previousClose', hist['Close'].iloc[-2])
        delta = current_price - previous_close
        delta_percent = (delta / previous_close) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${current_price:,.2f}", f"{delta:+.2f} ({delta_percent:+.2f}%)")
        col2.metric("Sector", info.get('sector', 'N/A'))
        col3.metric("Industry", info.get('industry', 'N/A'))

        # --- Fundamental Data ---
        st.subheader("Fundamental Indicators")
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        pe_ratio = info.get('trailingPE', 'N/A')
        pb_ratio = info.get('priceToBook', 'N/A')
        roe = info.get('returnOnEquity', 'N/A')
        if isinstance(roe, (int, float)):
            roe = f"{roe*100:.2f}%"
        
        f_col1.metric("PER (Trailing)", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio)
        f_col2.metric("PBR", f"{pb_ratio:.2f}" if isinstance(pb_ratio, (int, float)) else pb_ratio)
        f_col3.metric("ROE", roe)
        f_col4.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")

        # --- Technical Analysis ---
        st.subheader("Technical Analysis")
        
        # Calculate Indicators
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
        
        # RSI Calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))

        # Candlestick Chart with SMA
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index,
                        open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'],
                        name='Price'))
        
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], mode='lines', name='SMA 50', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_200'], mode='lines', name='SMA 200', line=dict(color='blue')))
        
        fig.update_layout(title=f"{ticker_symbol} Price Chart", yaxis_title="Price (USD)", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # RSI Chart
        st.write("### RSI (Relative Strength Index)")
        current_rsi = hist['RSI'].iloc[-1]
        rsi_status = "Neutral"
        if current_rsi >= 70: rsi_status = "Overbought (>70)"
        elif current_rsi <= 30: rsi_status = "Oversold (<30)"
        
        st.metric("Current RSI", f"{current_rsi:.2f}", rsi_status)
        
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], mode='lines', name='RSI', line=dict(color='purple')))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(yaxis_title="RSI", yaxis_range=[0, 100])
        st.plotly_chart(fig_rsi, use_container_width=True)

        # MACD Chart
        st.write("### MACD (Moving Average Convergence Divergence)")
        # Calculate MACD
        exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd_line = exp12 - exp26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line
        
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=hist.index, y=macd_line, mode='lines', name='MACD Line', line=dict(color='blue')))
        fig_macd.add_trace(go.Scatter(x=hist.index, y=signal_line, mode='lines', name='Signal Line', line=dict(color='orange')))
        fig_macd.add_trace(go.Bar(x=hist.index, y=macd_hist, name='Histogram', marker_color='gray'))
        fig_macd.update_layout(yaxis_title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")

