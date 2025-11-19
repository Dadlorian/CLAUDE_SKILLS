"""Market Analysis Tools"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketAnalyzer:
    def __init__(self, sales_data):
        self.sales = pd.DataFrame(sales_data)
        
    def get_metrics(self, period='month'):
        """Calculate market metrics"""
        return {
            'median_price': self.sales['price'].median(),
            'mean_price': self.sales['price'].mean(),
            'total_sales': len(self.sales),
            'avg_dom': self.sales['days_on_market'].mean(),
            'price_per_sqft': (self.sales['price'] / self.sales['sqft']).median()
        }
        
    def calculate_yoy_change(self, current_period, prior_year_period):
        """Year-over-year price change"""
        current_price = current_period['median_price']
        prior_price = prior_year_period['median_price']
        return ((current_price - prior_price) / prior_price) * 100
        
    def get_price_distribution(self, bins=10):
        """Price distribution histogram"""
        return pd.cut(self.sales['price'], bins=bins).value_counts()
        
    def market_temperature(self, active_listings):
        """Determine if market is hot/balanced/cold"""
        sales_per_month = len(self.sales) / 12
        months_inventory = active_listings / sales_per_month
        
        if months_inventory < 3:
            return 'hot'
        elif months_inventory < 6:
            return 'balanced'
        else:
            return 'cold'
