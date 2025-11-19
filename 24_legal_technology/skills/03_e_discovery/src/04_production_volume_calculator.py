"""
E-Discovery Production Volume and Cost Calculator

Calculates production volumes, estimates costs, and provides pricing analysis
for e-discovery productions.

Usage:
    python 04_production_volume_calculator.py --documents 100000 --avg-pages 2.5
"""

import argparse


def calculate_production_volumes(documents: int, avg_pages_per_doc: float = 2.5) -> dict:
    """Calculate production page volumes."""
    total_pages = int(documents * avg_pages_per_doc)

    return {
        'documents': documents,
        'avg_pages_per_doc': avg_pages_per_doc,
        'total_pages': total_pages
    }


def estimate_production_costs(volumes: dict, format_type: str = 'tiff') -> dict:
    """Estimate production costs."""
    pages = volumes['total_pages']

    # Cost per page by format (industry averages)
    costs = {
        'tiff': {
            'processing': 0.05,
            'imaging': 0.10,
            'qc': 0.02,
            'media': 0.01
        },
        'pdf': {
            'processing': 0.04,
            'conversion': 0.06,
            'qc': 0.02,
            'media': 0.01
        },
        'native': {
            'processing': 0.02,
            'organization': 0.01,
            'qc': 0.01,
            'media': 0.01
        }
    }

    format_costs = costs.get(format_type, costs['tiff'])
    total_cost = sum(format_costs.values()) * pages

    return {
        'format': format_type,
        'cost_per_page': sum(format_costs.values()),
        'total_cost': total_cost,
        'breakdown': {k: v * pages for k, v in format_costs.items()}
    }


def main():
    parser = argparse.ArgumentParser(description='E-Discovery Production Calculator')
    parser.add_argument('--documents', type=int, required=True, help='Number of documents')
    parser.add_argument('--avg-pages', type=float, default=2.5, help='Average pages per document')
    parser.add_argument('--format', choices=['tiff', 'pdf', 'native'], default='tiff', help='Production format')

    args = parser.parse_args()

    # Calculate volumes
    volumes = calculate_production_volumes(args.documents, args.avg_pages)

    # Estimate costs
    costs = estimate_production_costs(volumes, args.format)

    # Print results
    print("\n=== Production Volume Estimate ===")
    print(f"Documents: {volumes['documents']:,}")
    print(f"Average Pages/Doc: {volumes['avg_pages_per_doc']}")
    print(f"Total Pages: {volumes['total_pages']:,}")

    print(f"\n=== Production Cost Estimate ({costs['format'].upper()}) ===")
    print(f"Cost per Page: ${costs['cost_per_page']:.3f}")
    print(f"Total Cost: ${costs['total_cost']:,.2f}")
    print("\nBreakdown:")
    for component, cost in costs['breakdown'].items():
        print(f"  {component.title()}: ${cost:,.2f}")


if __name__ == '__main__':
    main()
