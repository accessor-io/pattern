from openbb_terminal.sdk import openbb
import pandas as pd

def analyze_plexiglass_market():
    # List of relevant tickers
    tickers = ['GLW', 'OLED', 'DAKT', 'TSE', 'ARKAY', 'MTLHY']
    
    print("OpenBB Plexiglass Market Analysis")
    print("=================================")
    
    for ticker in tickers:
        try:
            # Get company info
            info = openbb.stocks.fa.info(ticker)
            print(f"\nAnalyzing {ticker} - {info.get('longName', 'N/A')}")
            
            # Get analyst recommendations
            analyst = openbb.stocks.fa.analyst(ticker)
            if isinstance(analyst, pd.DataFrame):
                print("\nAnalyst Recommendations:")
                print(analyst.head())
            
            # Get recent news
            news = openbb.stocks.news(ticker, limit=3)
            if isinstance(news, pd.DataFrame):
                print("\nRecent News:")
                for _, row in news.iterrows():
                    print(f"- {row['title']}")
            
            # Get financial metrics
            metrics = openbb.stocks.fa.metrics(ticker)
            if isinstance(metrics, pd.DataFrame):
                print("\nKey Metrics:")
                print(metrics[['Market Cap', 'P/E', 'EPS']].head())
            
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {str(e)}")
            continue

if __name__ == "__main__":
    print("Starting OpenBB Analysis...")
    analyze_plexiglass_market() 