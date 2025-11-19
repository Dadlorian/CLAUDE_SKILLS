#!/usr/bin/env python3
"""
CDN Cache Purge Automation Script
Purges CDN cache when content is updated
Supports: Cloudflare, AWS CloudFront, Fastly

Usage:
    python cdn_purge_script.py --provider cloudflare --urls https://example.com/page.html
    python cdn_purge_script.py --provider cloudflare --tags blog,featured
    python cdn_purge_script.py --provider cloudfront --distribution E123ABC --paths /blog/*
"""

import argparse
import json
import logging
from typing import List, Optional
import requests
import boto3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CloudflarePurge:
    """Cloudflare cache purge client"""

    def __init__(self, zone_id: str, api_token: str):
        self.zone_id = zone_id
        self.api_token = api_token
        self.api_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def purge_by_urls(self, urls: List[str]) -> bool:
        """Purge cache by URL"""
        logger.info(f"Purging {len(urls)} URLs from Cloudflare cache...")

        payload = {"files": urls}

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Successfully purged {len(urls)} URLs")
                    return True
                else:
                    logger.error(f"Purge failed: {result.get('errors')}")
                    return False
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return False

    def purge_by_tags(self, tags: List[str]) -> bool:
        """Purge cache by tags"""
        logger.info(f"Purging {len(tags)} tags from Cloudflare cache...")

        payload = {"tags": tags}

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"Successfully purged tags: {', '.join(tags)}")
                    return True
                else:
                    logger.error(f"Purge failed: {result.get('errors')}")
                    return False
            else:
                logger.error(f"API request failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return False

    def purge_all(self) -> bool:
        """Purge entire cache"""
        logger.warning("Purging entire Cloudflare cache...")

        payload = {"purge_everything": True}

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info("Successfully purged entire cache")
                    return True
                else:
                    logger.error(f"Purge failed: {result.get('errors')}")
                    return False
            else:
                logger.error(f"API request failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return False


class CloudFrontPurge:
    """AWS CloudFront cache invalidation client"""

    def __init__(self, distribution_id: str, region: str = "us-east-1"):
        self.distribution_id = distribution_id
        self.client = boto3.client("cloudfront", region_name=region)

    def invalidate(self, paths: List[str]) -> bool:
        """Create CloudFront invalidation"""
        logger.info(f"Invalidating {len(paths)} paths in CloudFront...")

        try:
            response = self.client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    "Paths": {
                        "Quantity": len(paths),
                        "Items": paths
                    },
                    "CallerReference": str(datetime.now().timestamp())
                }
            )

            invalidation_id = response["Invalidation"]["Id"]
            logger.info(f"Successfully created invalidation: {invalidation_id}")
            return True

        except Exception as e:
            logger.error(f"Invalidation failed: {e}")
            return False


class FastlyPurge:
    """Fastly cache purge client"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.fastly.com/purge"
        self.headers = {
            "Fastly-Key": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def purge_by_urls(self, urls: List[str], soft: bool = False) -> bool:
        """Purge cache by URL"""
        logger.info(f"Purging {len(urls)} URLs from Fastly cache...")

        success_count = 0

        for url in urls:
            try:
                # Soft purge optional header
                headers = self.headers.copy()
                if soft:
                    headers["Soft-Purge"] = "1"

                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data={"url": url},
                    timeout=10
                )

                if response.status_code == 200:
                    success_count += 1
                    logger.debug(f"Purged: {url}")
                else:
                    logger.warning(f"Failed to purge {url}: {response.status_code}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")

        logger.info(f"Successfully purged {success_count}/{len(urls)} URLs")
        return success_count == len(urls)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="CDN cache purge automation script"
    )

    parser.add_argument(
        "--provider",
        choices=["cloudflare", "cloudfront", "fastly"],
        required=True,
        help="CDN provider"
    )

    parser.add_argument(
        "--urls",
        nargs="+",
        help="URLs to purge (Cloudflare, Fastly)"
    )

    parser.add_argument(
        "--tags",
        nargs="+",
        help="Cache tags to purge (Cloudflare)"
    )

    parser.add_argument(
        "--paths",
        nargs="+",
        help="Paths to invalidate (CloudFront)"
    )

    parser.add_argument(
        "--zone-id",
        help="Cloudflare zone ID"
    )

    parser.add_argument(
        "--api-token",
        help="Cloudflare API token"
    )

    parser.add_argument(
        "--api-key",
        help="Fastly API key"
    )

    parser.add_argument(
        "--distribution-id",
        help="CloudFront distribution ID"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Purge entire cache"
    )

    parser.add_argument(
        "--soft",
        action="store_true",
        help="Soft purge (Fastly: serve stale, fetch fresh)"
    )

    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()

    success = False

    try:
        if args.provider == "cloudflare":
            if not args.zone_id or not args.api_token:
                logger.error("Cloudflare requires --zone-id and --api-token")
                return 1

            cf = CloudflarePurge(args.zone_id, args.api_token)

            if args.all:
                success = cf.purge_all()
            elif args.tags:
                success = cf.purge_by_tags(args.tags)
            elif args.urls:
                success = cf.purge_by_urls(args.urls)
            else:
                logger.error("Provide --urls, --tags, or --all")
                return 1

        elif args.provider == "cloudfront":
            if not args.distribution_id:
                logger.error("CloudFront requires --distribution-id")
                return 1

            if not args.paths:
                logger.error("CloudFront requires --paths")
                return 1

            cf = CloudFrontPurge(args.distribution_id)
            success = cf.invalidate(args.paths)

        elif args.provider == "fastly":
            if not args.api_key:
                logger.error("Fastly requires --api-key")
                return 1

            if not args.urls:
                logger.error("Fastly requires --urls")
                return 1

            fastly = FastlyPurge(args.api_key)
            success = fastly.purge_by_urls(args.urls, soft=args.soft)

        return 0 if success else 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
