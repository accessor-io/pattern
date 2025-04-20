import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import tabulate
import pytz

# List of companies involved in plexiglass/acrylic products
companies = {
    # Emerging Tech & Innovation Leaders
    'C3 Nano': 'CNNO',                      # Advanced transparent conductive films
    'View Inc': 'VIEW',                      # Smart glass and dynamic display technology
    'Lucid Display Technology': 'LCID',      # Next-gen display solutions
    'Corning Inc': 'GLW',                    # Advanced glass and display technology
    'Universal Display Corp': 'OLED',        # Display technology innovation
    'Kolon Industries': 'KOLIF',             # Advanced materials and displays
    
    # Sustainable & Smart Materials Startups
    'Nano Magic Holdings': 'NMGX',           # Smart surface and coating technology
    'Meta Materials Inc': 'MMAT',            # Advanced materials and nanotech
    'Crown Electrokinetics': 'CRKN',         # Smart glass technology
    'Research Frontiers': 'REFR',            # SPD-Smart light control technology
    
    # Innovative Display Solutions
    'Daktronics': 'DAKT',                   # Digital display solutions
    'Planar Systems': 'PLNR',               # Professional display solutions
    'Visionox Technology': 'VIONF',         # OLED display technology
    'E Ink Holdings': 'EINK',               # Electronic paper display tech
    
    # Retail Tech Integration
    'Cooler Screens': 'COOL',               # Digital retail display innovation
    'Standard Fiber': 'STFI',               # Advanced material solutions
    'Vycom Corp': 'VYCM',                   # Innovative plastic solutions
    'Piedmont Plastics': 'PDMT',            # Custom plastic solutions
    
    # Traditional Leaders with Innovation Focus
    'Mitsubishi Chemical Holdings': 'MTLHY', # Major PMMA manufacturer
    'Trinseo S.A.': 'TSE',                  # Produces acrylic products
    'Arkema': 'ARKAY',                      # Altuglas® brand
    'Covestro AG': 'COVTY',                 # Specialty materials for retail displays
    
    # Emerging International Players
    'Schweiter Technologies': 'SCWTF',      # Display and architectural materials
    'Chimei Corporation': 'CMEXF',          # Advanced materials manufacturer
    'JSR Corporation': 'JSCPY',             # Specialty materials innovation
    'AGC Inc': 'ASGLY',                     # Glass and display innovation
}

# Time periods to analyze
periods = {
    '3Y': 1095,
    '1Y': 365,
    '6M': 180,
    '3M': 90,
    '1M': 30,
    '2W': 14,
    '1W': 7
}

def get_historical_prices(ticker):
    stock = yf.Ticker(ticker)
    end_date = datetime.now(pytz.timezone('America/New_York'))
    max_days = max(periods.values())
    start_date = end_date - timedelta(days=max_days)
    
    hist = stock.history(start=start_date, end=end_date)
    
    if hist.empty:
        return None
    
    prices = {}
    volume = {}
    for period_name, days in periods.items():
        date = end_date - timedelta(days=days)
        mask = hist.index <= date
        if not mask.any():
            prices[period_name] = None
            volume[period_name] = None
            continue
        closest_date = hist.index[mask][-1]
        prices[period_name] = hist.loc[closest_date, 'Close']
        if 'Volume' in hist.columns:
            volume[period_name] = hist.loc[closest_date:, 'Volume'].mean()
    
    return prices, volume

print("\nEmerging Companies in Acrylic/Display Technology")
print("==============================================")
print("Focus: Innovation | Contract Potential | Market Disruption")
print("Note: Some companies may be in early stages or recently public")
print("==============================================")

results = []
for company, ticker in companies.items():
    try:
        prices, volume = get_historical_prices(ticker)
        if prices:
            row = [company, ticker]
            row.extend([f"${prices[period]:.2f}" if prices[period] is not None else "N/A" 
                       for period in periods.keys()])
            
            # Calculate growth metrics
            if prices['1M'] and prices['1W']:
                weekly_growth = ((prices['1W'] - prices['1M']) / prices['1M']) * 100
                row.append(f"{weekly_growth:.1f}%")
            else:
                row.append("N/A")
            
            # Add average daily volume for liquidity indication
            if volume['1M']:
                row.append(f"{volume['1M']:,.0f}")
            else:
                row.append("N/A")
            
            results.append(row)
        else:
            print(f"Note: {company} ({ticker}) - Limited trading data or pre-IPO")
    except Exception as e:
        print(f"Note: {company} ({ticker}) - {str(e)}")

headers = ['Company', 'Ticker'] + list(periods.keys()) + ['Monthly Growth', 'Avg Volume']
print(tabulate.tabulate(results, headers=headers, tablefmt='grid'))

print("\nPromising Indicators:")
print("1. Companies with high volume growth indicate increasing market interest")
print("2. Recent price momentum may suggest new contract announcements")
print("3. Look for companies with strong patents and innovative technology")
print("4. Consider those with recent retail partnership announcements")
print("\nStartup Success Factors:")
print("1. Proprietary Technology: Patents and unique solutions")
print("2. Strategic Partnerships: Especially with major retailers")
print("3. Sustainable Practices: Focus on eco-friendly materials")
print("4. Market Timing: Rising demand for smart display solutions") 