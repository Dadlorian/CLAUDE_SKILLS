"""
Keyword Research Automation Tool for SEO/SEM

This comprehensive tool helps digital marketers conduct data-driven keyword research,
including difficulty analysis, search volume trends, SERP feature opportunities,
topic clustering, and automated content brief generation.

Features:
- Bulk keyword analysis with multiple data sources
- Keyword difficulty scoring
- Search intent classification
- Topic cluster generation
- Competitor keyword gap analysis
- Content brief automation

Usage:
    python keyword_research_tool.py --seed "digital marketing" --output keywords.csv
"""

import pandas as pd
import numpy as np
import requests
import json
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
import re
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class Keyword:
    """Data class for keyword information."""
    keyword: str
    search_volume: int
    difficulty: float
    cpc: float
    search_intent: str
    serp_features: List[str]
    trend: str
    opportunity_score: float


class KeywordResearchTool:
    """
    Comprehensive keyword research tool for SEO/SEM campaigns.

    Integrates with multiple data sources, performs analysis, and generates
    actionable insights for content strategy.
    """

    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize keyword research tool.

        Args:
            api_keys: Dictionary with API keys for various services
                     {'semrush': 'key', 'ahrefs': 'key', 'serp_api': 'key'}
        """
        self.api_keys = api_keys or {}
        self.keywords_data = []

    def generate_keyword_variations(self, seed_keyword: str) -> List[str]:
        """
        Generate keyword variations from a seed keyword.

        Args:
            seed_keyword: Starting keyword to expand

        Returns:
            List of keyword variations
        """
        variations = [seed_keyword]

        # Common modifiers
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        prepositions = ['for', 'with', 'in', 'on', 'to', 'from', 'by']
        qualifiers = ['best', 'top', 'free', 'cheap', 'affordable', 'professional']
        time_modifiers = ['2024', '2025', 'new', 'latest', 'updated']

        # Question variations
        for q_word in question_words:
            variations.append(f"{q_word} is {seed_keyword}")
            variations.append(f"{q_word} to {seed_keyword}")

        # Modifier variations
        for qualifier in qualifiers:
            variations.append(f"{qualifier} {seed_keyword}")
            variations.append(f"{seed_keyword} {qualifier}")

        # Prepositional variations
        for prep in prepositions:
            variations.append(f"{seed_keyword} {prep}")

        # Time-based variations
        for time_mod in time_modifiers:
            variations.append(f"{seed_keyword} {time_mod}")

        # Long-tail variations
        variations.extend([
            f"{seed_keyword} guide",
            f"{seed_keyword} tutorial",
            f"{seed_keyword} tips",
            f"{seed_keyword} examples",
            f"{seed_keyword} vs",
            f"{seed_keyword} tools",
            f"{seed_keyword} software",
            f"{seed_keyword} services",
            f"{seed_keyword} cost",
            f"{seed_keyword} pricing",
            f"{seed_keyword} reviews",
            f"{seed_keyword} comparison"
        ])

        return list(set(variations))  # Remove duplicates

    def classify_search_intent(self, keyword: str) -> str:
        """
        Classify the search intent of a keyword.

        Args:
            keyword: Keyword to classify

        Returns:
            Intent classification: 'informational', 'navigational', 'commercial', 'transactional'
        """
        keyword_lower = keyword.lower()

        # Transactional intent indicators
        transactional_words = ['buy', 'purchase', 'order', 'discount', 'deal', 'coupon',
                              'cheap', 'affordable', 'price', 'pricing', 'cost', 'shop']

        # Commercial intent indicators
        commercial_words = ['best', 'top', 'review', 'comparison', 'vs', 'versus',
                           'alternative', 'compare', 'tool', 'software', 'service']

        # Informational intent indicators
        informational_words = ['what', 'how', 'why', 'when', 'guide', 'tutorial',
                              'learn', 'tip', 'example', 'definition', 'meaning']

        # Navigational intent indicators
        navigational_words = ['login', 'sign in', 'official', 'website', 'portal', 'dashboard']

        # Check for intent patterns
        if any(word in keyword_lower for word in navigational_words):
            return 'navigational'
        elif any(word in keyword_lower for word in transactional_words):
            return 'transactional'
        elif any(word in keyword_lower for word in commercial_words):
            return 'commercial'
        elif any(word in keyword_lower for word in informational_words):
            return 'informational'
        else:
            # Default heuristics
            if '?' in keyword or keyword_lower.startswith(('how', 'what', 'why', 'when', 'where')):
                return 'informational'
            return 'informational'  # Default

    def calculate_keyword_difficulty(self, keyword: str, backlinks: int = None,
                                    domain_authority: float = None) -> float:
        """
        Calculate keyword difficulty score (0-100).

        Args:
            keyword: Keyword to analyze
            backlinks: Number of backlinks to top ranking pages
            domain_authority: Average DA of top 10 results

        Returns:
            Difficulty score between 0 and 100
        """
        # Simplified difficulty calculation (real version would use API data)

        # Word count factor (longer keywords generally easier)
        word_count = len(keyword.split())
        word_count_factor = max(0, (5 - word_count) * 10)

        # Generic term difficulty
        generic_terms = ['marketing', 'business', 'software', 'service', 'best']
        generic_factor = sum(20 for term in generic_terms if term in keyword.lower())

        # Base difficulty
        base_difficulty = 30

        # Backlinks factor (if provided)
        backlink_factor = 0
        if backlinks:
            backlink_factor = min(40, backlinks / 100)

        # Domain authority factor (if provided)
        da_factor = 0
        if domain_authority:
            da_factor = domain_authority / 2.5

        difficulty = base_difficulty + word_count_factor + generic_factor + backlink_factor + da_factor

        return min(100, max(0, difficulty))

    def calculate_opportunity_score(self, search_volume: int, difficulty: float,
                                    cpc: float) -> float:
        """
        Calculate opportunity score for a keyword.

        High opportunity = High volume + Low difficulty + High commercial value

        Args:
            search_volume: Monthly search volume
            difficulty: Keyword difficulty (0-100)
            cpc: Cost per click in dollars

        Returns:
            Opportunity score (0-100)
        """
        # Normalize search volume (log scale)
        volume_score = min(100, (np.log10(max(10, search_volume)) / 5) * 100)

        # Invert difficulty (easier = better)
        difficulty_score = 100 - difficulty

        # Commercial value score
        cpc_score = min(100, (cpc / 10) * 100)

        # Weighted average
        opportunity = (volume_score * 0.4 + difficulty_score * 0.4 + cpc_score * 0.2)

        return round(opportunity, 2)

    def analyze_keywords(self, keywords: List[str], use_simulation: bool = True) -> List[Keyword]:
        """
        Analyze a list of keywords with various metrics.

        Args:
            keywords: List of keywords to analyze
            use_simulation: If True, generate simulated data (for demo purposes)

        Returns:
            List of Keyword objects with analysis
        """
        analyzed_keywords = []

        for kw in keywords:
            if use_simulation:
                # Simulate data (replace with actual API calls in production)
                search_volume = self._simulate_search_volume(kw)
                difficulty = self.calculate_keyword_difficulty(kw)
                cpc = self._simulate_cpc(kw)
                serp_features = self._identify_serp_features(kw)
                trend = self._analyze_trend(kw)
            else:
                # Placeholder for actual API integration
                search_volume = 0
                difficulty = 50
                cpc = 0
                serp_features = []
                trend = 'stable'

            intent = self.classify_search_intent(kw)
            opportunity = self.calculate_opportunity_score(search_volume, difficulty, cpc)

            keyword_obj = Keyword(
                keyword=kw,
                search_volume=search_volume,
                difficulty=difficulty,
                cpc=cpc,
                search_intent=intent,
                serp_features=serp_features,
                trend=trend,
                opportunity_score=opportunity
            )

            analyzed_keywords.append(keyword_obj)

        return analyzed_keywords

    def _simulate_search_volume(self, keyword: str) -> int:
        """Simulate search volume based on keyword characteristics."""
        np.random.seed(hash(keyword) % 10000)

        # Base volume
        base = 1000

        # Word count factor (longer = lower volume)
        word_count = len(keyword.split())
        word_factor = 1 / (word_count ** 0.5)

        # Question keywords typically have lower volume
        if keyword.startswith(('what', 'how', 'why', 'when', 'where')):
            word_factor *= 0.5

        volume = int(base * word_factor * np.random.uniform(0.5, 3))
        return max(10, volume)

    def _simulate_cpc(self, keyword: str) -> float:
        """Simulate CPC based on keyword characteristics."""
        np.random.seed(hash(keyword) % 10000)

        # Commercial/transactional keywords have higher CPC
        intent = self.classify_search_intent(keyword)

        if intent == 'transactional':
            base_cpc = 5.0
        elif intent == 'commercial':
            base_cpc = 3.0
        elif intent == 'informational':
            base_cpc = 1.0
        else:
            base_cpc = 0.5

        cpc = base_cpc * np.random.uniform(0.7, 1.5)
        return round(cpc, 2)

    def _identify_serp_features(self, keyword: str) -> List[str]:
        """Identify potential SERP features for a keyword."""
        features = []

        keyword_lower = keyword.lower()

        # Featured snippet opportunities
        if any(word in keyword_lower for word in ['what', 'how', 'why', 'definition']):
            features.append('Featured Snippet')

        # People Also Ask
        if any(word in keyword_lower for word in ['what', 'how', 'why', 'can', 'should']):
            features.append('People Also Ask')

        # Video carousel
        if any(word in keyword_lower for word in ['how to', 'tutorial', 'guide']):
            features.append('Video Carousel')

        # Local pack
        if any(word in keyword_lower for word in ['near me', 'in', 'local']):
            features.append('Local Pack')

        # Shopping results
        if any(word in keyword_lower for word in ['buy', 'price', 'cheap', 'best', 'review']):
            features.append('Shopping Results')

        # Image pack
        if any(word in keyword_lower for word in ['design', 'template', 'example', 'ideas']):
            features.append('Image Pack')

        return features

    def _analyze_trend(self, keyword: str) -> str:
        """Analyze keyword trend (simplified simulation)."""
        # In production, use Google Trends API
        np.random.seed(hash(keyword) % 10000)
        trends = ['rising', 'stable', 'declining']
        weights = [0.3, 0.5, 0.2]
        return np.random.choice(trends, p=weights)

    def create_topic_clusters(self, keywords: List[Keyword],
                            num_clusters: int = 5) -> Dict[str, List[Keyword]]:
        """
        Group keywords into topic clusters.

        Args:
            keywords: List of analyzed keywords
            num_clusters: Number of clusters to create

        Returns:
            Dictionary mapping cluster names to keyword lists
        """
        # Simple clustering based on common words
        clusters = defaultdict(list)

        for kw_obj in keywords:
            words = set(kw_obj.keyword.lower().split())

            # Remove common stop words
            stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'for', 'to', 'of',
                         'in', 'on', 'at', 'by', 'with', 'what', 'how', 'why', 'when'}
            words = words - stop_words

            # Find best matching cluster
            best_cluster = None
            best_overlap = 0

            for cluster_name in clusters.keys():
                cluster_words = set(cluster_name.split())
                overlap = len(words & cluster_words)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_cluster = cluster_name

            if best_cluster and best_overlap > 0:
                clusters[best_cluster].append(kw_obj)
            else:
                # Create new cluster from most significant word
                significant_word = max(words, key=len) if words else kw_obj.keyword.split()[0]
                clusters[significant_word].append(kw_obj)

        # Sort clusters by total search volume
        sorted_clusters = {}
        for cluster_name, cluster_kws in sorted(
            clusters.items(),
            key=lambda x: sum(kw.search_volume for kw in x[1]),
            reverse=True
        ):
            sorted_clusters[cluster_name] = cluster_kws

        return dict(list(sorted_clusters.items())[:num_clusters])

    def generate_content_brief(self, cluster_name: str, keywords: List[Keyword]) -> str:
        """
        Generate a content brief for a topic cluster.

        Args:
            cluster_name: Name of the topic cluster
            keywords: Keywords in the cluster

        Returns:
            Formatted content brief
        """
        # Sort keywords by opportunity score
        sorted_kws = sorted(keywords, key=lambda x: x.opportunity_score, reverse=True)

        # Primary keyword (highest opportunity)
        primary_kw = sorted_kws[0]

        # Secondary keywords
        secondary_kws = sorted_kws[1:6]

        # Calculate aggregate metrics
        total_volume = sum(kw.search_volume for kw in keywords)
        avg_difficulty = np.mean([kw.difficulty for kw in keywords])

        # Identify common search intents
        intent_counts = Counter(kw.search_intent for kw in keywords)
        primary_intent = intent_counts.most_common(1)[0][0]

        # Generate brief
        brief = []
        brief.append("=" * 70)
        brief.append(f"CONTENT BRIEF: {cluster_name.title()}")
        brief.append("=" * 70)
        brief.append("")

        brief.append("PRIMARY KEYWORD")
        brief.append("-" * 70)
        brief.append(f"Keyword: {primary_kw.keyword}")
        brief.append(f"Search Volume: {primary_kw.search_volume:,}/month")
        brief.append(f"Difficulty: {primary_kw.difficulty:.1f}/100")
        brief.append(f"Search Intent: {primary_kw.search_intent.title()}")
        brief.append(f"Opportunity Score: {primary_kw.opportunity_score:.1f}/100")
        brief.append("")

        brief.append("SECONDARY KEYWORDS")
        brief.append("-" * 70)
        for kw in secondary_kws:
            brief.append(f"- {kw.keyword} ({kw.search_volume:,}/mo, difficulty: {kw.difficulty:.0f})")
        brief.append("")

        brief.append("CLUSTER OVERVIEW")
        brief.append("-" * 70)
        brief.append(f"Total Keywords: {len(keywords)}")
        brief.append(f"Total Search Volume: {total_volume:,}/month")
        brief.append(f"Average Difficulty: {avg_difficulty:.1f}/100")
        brief.append(f"Primary Intent: {primary_intent.title()}")
        brief.append("")

        brief.append("SERP FEATURES TO TARGET")
        brief.append("-" * 70)
        all_features = []
        for kw in keywords:
            all_features.extend(kw.serp_features)
        feature_counts = Counter(all_features)
        for feature, count in feature_counts.most_common(5):
            brief.append(f"- {feature} ({count} keywords)")
        brief.append("")

        brief.append("CONTENT RECOMMENDATIONS")
        brief.append("-" * 70)

        if primary_intent == 'informational':
            brief.append("Content Type: Comprehensive Guide / Tutorial")
            brief.append("Recommended Length: 2,000-3,000 words")
            brief.append("Structure: Introduction → Step-by-step sections → Examples → FAQ → Conclusion")
        elif primary_intent == 'commercial':
            brief.append("Content Type: Comparison / Review Article")
            brief.append("Recommended Length: 1,500-2,500 words")
            brief.append("Structure: Overview → Detailed comparisons → Pros/cons → Recommendations")
        elif primary_intent == 'transactional':
            brief.append("Content Type: Product/Service Landing Page")
            brief.append("Recommended Length: 800-1,500 words")
            brief.append("Structure: Value proposition → Features → Pricing → Social proof → CTA")
        else:
            brief.append("Content Type: Navigation / Resource Page")
            brief.append("Recommended Length: 500-1,000 words")

        brief.append("")
        brief.append("KEY SECTIONS TO INCLUDE")
        brief.append("-" * 70)
        brief.append("1. Introduction (include primary keyword in first 100 words)")
        brief.append("2. Main content sections (use H2/H3 with keyword variations)")
        brief.append("3. FAQ section (target PAA opportunities)")
        brief.append("4. Conclusion with clear CTA")
        brief.append("")

        brief.append("=" * 70)

        return "\n".join(brief)

    def export_to_csv(self, keywords: List[Keyword], filename: str):
        """
        Export keyword analysis to CSV.

        Args:
            keywords: List of analyzed keywords
            filename: Output CSV filename
        """
        data = []
        for kw in keywords:
            data.append({
                'Keyword': kw.keyword,
                'Search Volume': kw.search_volume,
                'Difficulty': kw.difficulty,
                'CPC': kw.cpc,
                'Intent': kw.search_intent,
                'SERP Features': ', '.join(kw.serp_features),
                'Trend': kw.trend,
                'Opportunity Score': kw.opportunity_score
            })

        df = pd.DataFrame(data)
        df = df.sort_values('Opportunity Score', ascending=False)
        df.to_csv(filename, index=False)
        print(f"Exported {len(keywords)} keywords to {filename}")


# Example usage
if __name__ == "__main__":
    print("Keyword Research Tool - SEO/SEM")
    print("=" * 70)
    print()

    # Initialize tool
    tool = KeywordResearchTool()

    # Example seed keyword
    seed_keyword = "digital marketing"
    print(f"Generating keyword variations for: '{seed_keyword}'")

    # Generate variations
    keyword_list = tool.generate_keyword_variations(seed_keyword)
    print(f"Generated {len(keyword_list)} keyword variations")
    print()

    # Analyze keywords
    print("Analyzing keywords...")
    analyzed_keywords = tool.analyze_keywords(keyword_list[:30])  # Analyze first 30
    print(f"Analyzed {len(analyzed_keywords)} keywords")
    print()

    # Display top opportunities
    print("TOP 10 KEYWORD OPPORTUNITIES")
    print("-" * 70)
    top_keywords = sorted(analyzed_keywords, key=lambda x: x.opportunity_score, reverse=True)[:10]
    for i, kw in enumerate(top_keywords, 1):
        print(f"{i}. {kw.keyword}")
        print(f"   Volume: {kw.search_volume:,}/mo | Difficulty: {kw.difficulty:.0f}/100 | "
              f"Opportunity: {kw.opportunity_score:.0f}/100")
        print(f"   Intent: {kw.search_intent} | CPC: ${kw.cpc}")
    print()

    # Create topic clusters
    print("Creating topic clusters...")
    clusters = tool.create_topic_clusters(analyzed_keywords, num_clusters=3)
    print(f"Created {len(clusters)} topic clusters")
    print()

    # Generate content briefs
    for cluster_name, cluster_kws in clusters.items():
        print(tool.generate_content_brief(cluster_name, cluster_kws))
        print("\n")

    # Export to CSV
    tool.export_to_csv(analyzed_keywords, 'keyword_research_results.csv')
    print("\nKeyword research complete!")