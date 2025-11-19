# Apache Superset Configuration Example

import os
from cachelib.redis import RedisCache

# ================================================
# DATABASE
# ================================================

# PostgreSQL metadata database
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://superset:superset@localhost/superset'

# ================================================
# CACHE
# ================================================

# Redis for caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 1 day
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1
}

# Cache for dashboard filter state
FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_filter_',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 2
}

# ================================================
# SECURITY
# ================================================

# Secret key for session encryption
SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE_THIS_SECRET_KEY'

# Enable CSRF protection
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# ================================================
# FEATURES
# ================================================

FEATURE_FLAGS = {
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_RBAC': True,
    'EMBEDDED_SUPERSET': True,
}

# ================================================
# PERFORMANCE
# ================================================

# Query timeout (seconds)
SUPERSET_WEBSERVER_TIMEOUT = 60

# SQL Lab query timeout
SQLLAB_TIMEOUT = 300
SQLLAB_ASYNC_TIME_LIMIT_SEC = 600

# Row limit for SQL Lab
SQL_MAX_ROW = 100000

# ================================================
# EMAIL ALERTS
# ================================================

SMTP_HOST = 'smtp.gmail.com'
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PORT = 587
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
SMTP_MAIL_FROM = 'superset@company.com'

# ================================================
# ROW-LEVEL SECURITY
# ================================================

# Custom function for dynamic RLS
def get_user_filter(table):
    from flask import g
    if g.user.is_anonymous:
        return None
    
    user_region = g.user.get_attribute('region')
    if user_region:
        return f"region = '{user_region}'"
    
    return None

# ================================================
# CUSTOM CSS/BRANDING
# ================================================

APP_NAME = "Company BI"
APP_ICON = "/static/assets/images/superset-logo.png"
APP_ICON_WIDTH = 126

# Custom CSS
EXTRA_CATEGORICAL_COLOR_SCHEMES = [
    {
        'id': 'company_colors',
        'label': 'Company Brand',
        'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    }
]
