"""Comparable Sales Analyzer"""
import numpy as np
from geopy.distance import geodesic

class CompAnalyzer:
    def __init__(self, subject_property):
        self.subject = subject_property
        
    def find_comps(self, sales, max_distance=1.0, max_sales_age=180):
        """Find comparable sales"""
        comps = []
        
        for sale in sales:
            # Check distance
            distance = geodesic(
                (self.subject['lat'], self.subject['lon']),
                (sale['lat'], sale['lon'])
            ).miles
            
            if distance > max_distance:
                continue
                
            # Check property type
            if sale['property_type'] != self.subject['property_type']:
                continue
                
            # Check size similarity (within 25%)
            size_diff = abs(sale['sqft'] - self.subject['sqft']) / self.subject['sqft']
            if size_diff > 0.25:
                continue
                
            # Calculate similarity score
            similarity = self.calculate_similarity(sale, distance)
            
            comps.append({
                'sale': sale,
                'distance': distance,
                'similarity': similarity
            })
            
        # Sort by similarity
        comps.sort(key=lambda x: x['similarity'], reverse=True)
        return comps[:6]
        
    def calculate_similarity(self, comp, distance):
        """Calculate similarity score (0-1)"""
        score = 1.0
        
        # Distance penalty
        score *= max(0, 1 - distance / 2)
        
        # Size similarity
        size_diff = abs(comp['sqft'] - self.subject['sqft']) / self.subject['sqft']
        score *= (1 - size_diff)
        
        # Age similarity
        age_diff = abs(comp['year_built'] - self.subject['year_built']) / 50
        score *= max(0, 1 - age_diff)
        
        return score
        
    def adjust_comp_price(self, comp):
        """Adjust comp price for differences"""
        adjusted = comp['sale_price']
        
        # Size adjustment
        sqft_diff = self.subject['sqft'] - comp['sqft']
        adjusted += sqft_diff * (comp['sale_price'] / comp['sqft'])
        
        # Bedroom adjustment
        bed_diff = self.subject['bedrooms'] - comp['bedrooms']
        adjusted += bed_diff * 15000
        
        # Bathroom adjustment
        bath_diff = self.subject['bathrooms'] - comp['bathrooms']
        adjusted += bath_diff * 8000
        
        return int(adjusted)
        
    def estimate_value(self, comps):
        """Estimate value using comps"""
        adjusted_prices = []
        weights = []
        
        for comp_data in comps:
            comp = comp_data['sale']
            adjusted = self.adjust_comp_price(comp)
            adjusted_prices.append(adjusted)
            weights.append(comp_data['similarity'])
            
        # Weighted average
        weights = np.array(weights) / sum(weights)
        estimated = np.average(adjusted_prices, weights=weights)
        
        return int(estimated)
