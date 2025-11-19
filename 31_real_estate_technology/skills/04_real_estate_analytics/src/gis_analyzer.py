"""GIS Analysis for Real Estate"""
import geopandas as gpd
from shapely.geometry import Point

class GISAnalyzer:
    def __init__(self, properties_df):
        self.gdf = gpd.GeoDataFrame(
            properties_df,
            geometry=[Point(xy) for xy in zip(properties_df.lon, properties_df.lat)]
        )
        
    def find_within_radius(self, center_lat, center_lon, radius_miles):
        """Find properties within radius"""
        center = Point(center_lon, center_lat)
        
        # Convert miles to degrees (approximate)
        radius_deg = radius_miles / 69.0
        
        buffer = center.buffer(radius_deg)
        return self.gdf[self.gdf.geometry.within(buffer)]
        
    def nearest_neighbors(self, target_lat, target_lon, n=5):
        """Find N nearest properties"""
        target = Point(target_lon, target_lat)
        self.gdf['distance'] = self.gdf.geometry.distance(target)
        return self.gdf.nsmallest(n, 'distance')
