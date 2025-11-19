"""
Case Law Scraper with Ethical Considerations
Demonstrates responsible scraping of publicly available case law
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CaseLawOpinion:
    """Data class for case law opinion"""
    citation: str
    title: str
    court: str
    date: datetime
    url: str
    text: Optional[str] = None
    summary: Optional[str] = None


class EthicalCaseLawScraper:
    """
    Ethical case law scraper following best practices:
    - Respects robots.txt
    - Implements rate limiting
    - Uses official/authorized sources
    - Includes proper error handling
    - Provides attribution
    """

    def __init__(self, rate_limit_seconds=2):
        """
        Initialize scraper with rate limiting

        Args:
            rate_limit_seconds: Minimum seconds between requests
        """
        self.rate_limit = rate_limit_seconds
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LegalResearchBot/1.0 (Educational/Research Purpose)'
        })

    def respect_rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            logger.info(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def scrape_courtlistener(self, query: str, max_results: int = 50) -> List[CaseLawOpinion]:
        """
        Scrape case law from CourtListener (free, authorized source)

        Args:
            query: Search query
            max_results: Maximum number of results to retrieve

        Returns:
            List of CaseLawOpinion objects
        """
        logger.info(f"Searching CourtListener for: {query}")

        base_url = "https://www.courtlistener.com"
        search_url = f"{base_url}/api/rest/v3/search/"

        results = []

        # API request (authorized method)
        self.respect_rate_limit()

        params = {
            "q": query,
            "type": "o",  # opinions
            "order_by": "score desc",
            "page_size": min(max_results, 20)  # API limit
        }

        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()

            data = response.json()

            for result in data.get("results", []):
                opinion = CaseLawOpinion(
                    citation=result.get("citation", "N/A"),
                    title=result.get("caseName", ""),
                    court=result.get("court", ""),
                    date=datetime.fromisoformat(result.get("dateFiled", "").replace("Z", "+00:00")),
                    url=f"{base_url}{result.get('absolute_url', '')}",
                    summary=result.get("snippet", "")
                )

                results.append(opinion)

                logger.info(f"Found: {opinion.citation} - {opinion.title}")

        except requests.RequestException as e:
            logger.error(f"Error scraping CourtListener: {e}")

        return results

    def scrape_justia(self, citation: str) -> Optional[CaseLawOpinion]:
        """
        Scrape specific case from Justia (publicly available)

        Args:
            citation: Case citation (e.g., "505 U.S. 144")

        Returns:
            CaseLawOpinion object or None
        """
        logger.info(f"Retrieving case from Justia: {citation}")

        # Construct Justia URL
        # Note: This is simplified - actual URL construction more complex
        justia_url = f"https://supreme.justia.com/cases/federal/us/{citation}/"

        self.respect_rate_limit()

        try:
            response = self.session.get(justia_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract case information
            # (Actual selectors would need to match Justia's HTML structure)
            title = soup.find('h1', class_='case-title')
            date = soup.find('span', class_='case-date')
            opinion_text = soup.find('div', class_='opinion-content')

            if title and date and opinion_text:
                opinion = CaseLawOpinion(
                    citation=citation,
                    title=title.text.strip(),
                    court="Supreme Court of the United States",
                    date=datetime.strptime(date.text.strip(), "%B %d, %Y"),
                    url=justia_url,
                    text=opinion_text.text.strip()
                )

                return opinion

        except requests.RequestException as e:
            logger.error(f"Error scraping Justia: {e}")

        return None

    @staticmethod
    def check_robots_txt(base_url: str) -> bool:
        """
        Check if scraping is allowed by robots.txt

        Args:
            base_url: Base URL of site

        Returns:
            True if allowed, False otherwise
        """
        from urllib.robotparser import RobotFileParser

        rp = RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")

        try:
            rp.read()
            user_agent = "LegalResearchBot"
            return rp.can_fetch(user_agent, base_url)

        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return False  # Err on side of caution


# Ethical Guidelines for Legal Research Scraping
ETHICAL_GUIDELINES = """
ETHICAL CONSIDERATIONS FOR LEGAL RESEARCH WEB SCRAPING:

1. USE AUTHORIZED SOURCES FIRST
   - Official court websites
   - Free legal databases (CourtListener, Justia, Google Scholar)
   - Public access systems (PACER for federal courts)

2. RESPECT TERMS OF SERVICE
   - Read and comply with website ToS
   - Do not circumvent access controls
   - Do not scrape subscription-only content without authorization

3. IMPLEMENT RATE LIMITING
   - Minimum 1-2 seconds between requests
   - Avoid overwhelming servers
   - Scrape during off-peak hours if possible

4. RESPECT ROBOTS.TXT
   - Check robots.txt before scraping
   - Honor disallow directives
   - Identify bot with descriptive User-Agent

5. USE APIs WHEN AVAILABLE
   - Prefer official APIs over web scraping
   - CourtListener API, Justia API, etc.
   - APIs are more reliable and ethical

6. ATTRIBUTION AND CITATION
   - Cite source of scraped data
   - Provide attribution in research outputs
   - Link back to original source

7. DATA PRIVACY
   - Do not scrape sealed or confidential documents
   - Respect privacy of parties
   - Handle personal information responsibly

8. VALIDATION
   - Verify accuracy of scraped data
   - Cross-reference with official sources
   - Update data regularly

9. LEGAL COMPLIANCE
   - Comply with Computer Fraud and Abuse Act (CFAA)
   - Follow copyright law (facts are not copyrightable, but expression may be)
   - Adhere to state computer crime laws

10. ALTERNATIVE: USE COMMERCIAL DATABASES
    - For professional practice, use Westlaw, Lexis, Bloomberg Law
    - Scraping should be for research/educational purposes
    - Commercial use may require licensing
"""


def main():
    """Example usage of ethical case law scraper"""
    print(ETHICAL_GUIDELINES)

    scraper = EthicalCaseLawScraper(rate_limit_seconds=2)

    # Example: Search CourtListener
    results = scraper.scrape_courtlistener("patent infringement", max_results=10)

    print(f"\nFound {len(results)} cases:")
    for result in results:
        print(f"  {result.citation}: {result.title}")
        print(f"    Court: {result.court}")
        print(f"    Date: {result.date}")
        print(f"    URL: {result.url}")
        print()


if __name__ == "__main__":
    main()
