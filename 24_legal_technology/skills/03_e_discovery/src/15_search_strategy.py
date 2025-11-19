"""
Search Strategy and Keyword Management Example
Demonstrates developing and executing search strategies
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict

class KeywordStrategy:
    """Develops comprehensive keyword search strategies"""

    def __init__(self):
        """Initialize keyword strategy builder"""
        self.keywords = defaultdict(list)
        self.topic_maps = {}

    def add_topic_keywords(self, topic: str, keywords: List[str]) -> None:
        """
        Add keywords for specific legal topic

        Args:
            topic: Legal issue or topic name
            keywords: List of related keywords
        """
        self.keywords[topic] = keywords

    def build_search_string(self, topic: str, use_or: bool = False) -> str:
        """
        Build search string for topic

        Args:
            topic: Topic name
            use_or: Use OR operator (default uses AND)

        Returns:
            Search string
        """
        keywords = self.keywords.get(topic, [])
        if not keywords:
            return ""

        operator = " OR " if use_or else " AND "
        # Add quotes for exact phrase matching
        quoted = [f'"{kw}"' for kw in keywords]
        return operator.join(quoted)

    def get_search_strategy(self) -> Dict:
        """
        Get complete search strategy

        Returns:
            Dictionary mapping topics to search strings
        """
        strategy = {}

        for topic, keywords in self.keywords.items():
            strategy[topic] = {
                "keywords": keywords,
                "search_string": self.build_search_string(topic),
                "keyword_count": len(keywords)
            }

        return strategy

    @staticmethod
    def develop_query_hierarchy(keywords: List[str]) -> Dict:
        """
        Develop hierarchical query from keywords

        Args:
            keywords: List of keywords

        Returns:
            Hierarchical query structure
        """
        # Primary keywords (most important)
        primary = keywords[:len(keywords)//3] if len(keywords) > 3 else keywords

        # Secondary keywords (supporting)
        secondary = keywords[len(keywords)//3:2*len(keywords)//3] if len(keywords) > 3 else []

        # Tertiary keywords (contextual)
        tertiary = keywords[2*len(keywords)//3:] if len(keywords) > 3 else []

        return {
            "primary_keywords": primary,
            "secondary_keywords": secondary,
            "tertiary_keywords": tertiary,
            "combined_query": " OR ".join([f'"{kw}"' for kw in primary]) +
            (" AND (" + " OR ".join([f'"{kw}"' for kw in secondary]) + ")" if secondary else "")
        }


class SearchExecutor:
    """Executes searches and analyzes results"""

    @staticmethod
    def execute_keyword_search(documents: List[Dict],
                              search_terms: List[str],
                              search_fields: List[str] = None) -> Dict:
        """
        Execute keyword search across documents

        Args:
            documents: Documents to search
            search_terms: Keywords to search for
            search_fields: Fields to search (default: all)

        Returns:
            Search results
        """
        if search_fields is None:
            search_fields = ['Subject', 'Body', 'Author']

        results = {
            "search_terms": search_terms,
            "total_documents_searched": len(documents),
            "hits_by_term": defaultdict(int),
            "unique_documents_hit": set(),
            "search_results": []
        }

        for term in search_terms:
            term_lower = term.lower()

            for doc in documents:
                # Search in specified fields
                found = False
                for field in search_fields:
                    field_value = str(doc.get(field, '')).lower()
                    if term_lower in field_value:
                        found = True
                        break

                if found:
                    results["hits_by_term"][term] += 1
                    doc_id = doc.get('DocumentID')
                    results["unique_documents_hit"].add(doc_id)

                    results["search_results"].append({
                        "document_id": doc_id,
                        "term": term,
                        "hit_field": field,
                        "relevance": "high" if field == "Subject" else "medium" if field == "Body" else "low"
                    })

        return {
            "search_terms": search_terms,
            "total_searched": len(documents),
            "total_hits": len(results["search_results"]),
            "unique_documents_hit": len(results["unique_documents_hit"]),
            "hit_percentage": round(len(results["unique_documents_hit"]) / len(documents) * 100, 1),
            "hits_per_term": dict(results["hits_by_term"]),
            "sample_results": results["search_results"][:10]
        }

    @staticmethod
    def refine_search(initial_results: Dict,
                     refining_terms: List[str]) -> Dict:
        """
        Refine search results with additional terms

        Args:
            initial_results: Results from initial search
            refining_terms: Additional terms to apply

        Returns:
            Refined search results
        """
        refined = []

        for result in initial_results.get("search_results", []):
            doc_id = result["document_id"]
            match_all = True

            for term in refining_terms:
                if term.lower() not in doc_id.lower():
                    match_all = False
                    break

            if match_all:
                refined.append(result)

        return {
            "original_hits": len(initial_results.get("search_results", [])),
            "refined_hits": len(refined),
            "refinement_terms": refining_terms,
            "reduction_percentage": round(
                (1 - len(refined) / max(len(initial_results.get("search_results", [])), 1)) * 100, 1
            ),
            "refined_results": refined
        }


class BooleanSearchBuilder:
    """Builds complex Boolean search queries"""

    @staticmethod
    def build_and_query(terms: List[str]) -> str:
        """Build AND query"""
        return " AND ".join([f'"{term}"' for term in terms])

    @staticmethod
    def build_or_query(terms: List[str]) -> str:
        """Build OR query"""
        return " OR ".join([f'"{term}"' for term in terms])

    @staticmethod
    def build_not_query(include_terms: List[str],
                       exclude_terms: List[str]) -> str:
        """
        Build query with exclusions

        Args:
            include_terms: Terms to include
            exclude_terms: Terms to exclude

        Returns:
            NOT query string
        """
        include = " AND ".join([f'"{term}"' for term in include_terms])
        exclude = " AND NOT ".join([f'"{term}"' for term in exclude_terms])
        return f"({include}) AND NOT ({exclude})"

    @staticmethod
    def build_proximity_query(terms: List[str],
                             distance: int = 5) -> str:
        """
        Build proximity query (terms within distance)

        Args:
            terms: Terms that should be near each other
            distance: Maximum distance between terms

        Returns:
            Proximity query string
        """
        # Simplified proximity query format
        return f'({" ".join(terms)}) NEAR/{distance}'

    @staticmethod
    def build_wildcard_query(term_pattern: str) -> str:
        """
        Build wildcard query

        Args:
            term_pattern: Term with wildcards (* or ?)

        Returns:
            Wildcard query
        """
        return f'"{term_pattern}"'


class SearchAnalytics:
    """Analyzes search performance and effectiveness"""

    @staticmethod
    def analyze_search_precision(search_results: Dict,
                                relevant_document_count: int) -> Dict:
        """
        Analyze search precision and recall

        Args:
            search_results: Search results from execution
            relevant_document_count: Known relevant documents in universe

        Returns:
            Precision/recall metrics
        """
        retrieved = search_results.get("unique_documents_hit", 0)
        relevant = relevant_document_count
        relevant_retrieved = retrieved  # Simplified assumption

        precision = relevant_retrieved / retrieved if retrieved > 0 else 0
        recall = relevant_retrieved / relevant if relevant > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1_score, 3),
            "interpretation": "good" if f1_score > 0.7 else "acceptable" if f1_score > 0.5 else "needs_refinement"
        }

    @staticmethod
    def identify_search_gaps(search_results: Dict,
                            all_documents: List[Dict],
                            relevant_keywords: List[str]) -> Dict:
        """
        Identify documents that should have been found

        Args:
            search_results: Results from search
            all_documents: All available documents
            relevant_keywords: Keywords that indicate relevance

        Returns:
            Gap analysis
        """
        found_doc_ids = search_results.get("unique_documents_hit", set())
        missed = []

        for doc in all_documents:
            doc_id = doc.get('DocumentID')
            if doc_id not in found_doc_ids:
                # Check if document contains any relevant keywords
                content = " ".join([str(v).lower() for v in doc.values()])
                for keyword in relevant_keywords:
                    if keyword.lower() in content:
                        missed.append({
                            "document_id": doc_id,
                            "missed_keyword": keyword
                        })
                        break

        return {
            "documents_found": len(found_doc_ids),
            "documents_missed": len(missed),
            "missed_details": missed[:20]
        }


# Example usage
if __name__ == "__main__":
    keywords = ["contract", "agreement", "terms", "conditions"]

    builder = BooleanSearchBuilder()
    and_query = builder.build_and_query(keywords[:2])
    or_query = builder.build_or_query(keywords)

    print(f"AND Query: {and_query}")
    print(f"OR Query: {or_query}")

    # Execute search
    docs = [
        {"DocumentID": 1, "Subject": "Contract Agreement", "Body": "terms and conditions"},
        {"DocumentID": 2, "Subject": "Meeting Notes", "Body": "discussed plans"}
    ]

    executor = SearchExecutor()
    results = executor.execute_keyword_search(docs, ["contract", "agreement"])
    print(f"Search Results: {results['unique_documents_hit']} documents found")
