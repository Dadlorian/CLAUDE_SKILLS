#!/usr/bin/env python3
"""Jinja2 Template Engine for Document Generation"""

from jinja2 import Template, Environment, FileSystemLoader
from datetime import datetime

# Simple template example
template_string = """
EMPLOYMENT AGREEMENT

This Agreement made on {{ effective_date }} between {{ employer_name }} ("Employer")
and {{ employee_name }} ("Employee").

1. POSITION
Employee shall serve as {{ job_title }}.

2. COMPENSATION
Base Salary: ${{ "{:,}".format(salary) }} per year
{% if bonus_eligible %}
Bonus: Up to {{ bonus_percentage }}% of base salary
{% endif %}

3. BENEFITS
{% for benefit in benefits %}
- {{ benefit }}
{% endfor %}

{% if stock_options > 0 %}
4. STOCK OPTIONS
Employee shall receive {{ "{:,}".format(stock_options) }} stock options.
{% endif %}
"""

def generate_employment_agreement(data):
    template = Template(template_string)
    output = template.render(**data)
    filename = f"Employment_{data['employee_name'].replace(' ', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(output)
    print(f'Created: {filename}')
    return filename

if __name__ == '__main__':
    data = {
        'effective_date': 'November 19, 2025',
        'employer_name': 'Tech Startup Inc',
        'employee_name': 'John Smith',
        'job_title': 'Senior Software Engineer',
        'salary': 150000,
        'bonus_eligible': True,
        'bonus_percentage': 15,
        'benefits': ['Health Insurance', '401(k) Match', 'Unlimited PTO'],
        'stock_options': 10000
    }
    generate_employment_agreement(data)
