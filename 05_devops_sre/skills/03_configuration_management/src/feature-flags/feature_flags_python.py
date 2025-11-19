"""
Feature Flags Implementation in Python
Demonstrates production-ready feature flag patterns for gradual rollouts,
A/B testing, and decoupling deployment from feature releases.
"""

import os
import hashlib
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import redis
from datetime import datetime


class RolloutStrategy(Enum):
    """Different rollout strategies for feature flags"""
    ALL = "all"  # Enable for all users
    NONE = "none"  # Disable for all users
    PERCENTAGE = "percentage"  # Enable for percentage of users
    USER_LIST = "user_list"  # Enable for specific users
    USER_ATTRIBUTE = "user_attribute"  # Enable based on user attributes
    GRADUAL = "gradual"  # Gradual rollout over time


@dataclass
class User:
    """User context for feature flag evaluation"""
    user_id: str
    email: str
    attributes: Dict[str, Any]

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)


@dataclass
class FeatureFlag:
    """Feature flag definition"""
    key: str
    name: str
    description: str
    enabled: bool
    strategy: RolloutStrategy
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class FeatureFlagClient:
    """
    Feature flag client with multiple backends (LaunchDarkly, Unleash, or custom)
    Supports caching, fallbacks, and analytics.
    """

    def __init__(self, backend: str = "redis", redis_url: Optional[str] = None):
        self.backend = backend
        self.redis_client = None
        self.cache: Dict[str, FeatureFlag] = {}

        if backend == "redis" and redis_url:
            self.redis_client = redis.from_url(redis_url)

    def is_enabled(self, flag_key: str, user: User, default: bool = False) -> bool:
        """
        Check if a feature flag is enabled for a user.

        Args:
            flag_key: Feature flag identifier
            user: User context
            default: Default value if flag not found

        Returns:
            True if feature is enabled, False otherwise
        """
        try:
            flag = self._get_flag(flag_key)

            if not flag or not flag.enabled:
                return default

            # Track analytics
            self._track_evaluation(flag_key, user, "evaluated")

            # Evaluate based on strategy
            result = self._evaluate_strategy(flag, user)

            # Track result
            self._track_evaluation(flag_key, user, "enabled" if result else "disabled")

            return result

        except Exception as e:
            print(f"Error evaluating flag {flag_key}: {e}")
            return default

    def get_variant(self, flag_key: str, user: User, default: str = "control") -> str:
        """
        Get variant for A/B testing.

        Args:
            flag_key: Feature flag identifier
            user: User context
            default: Default variant name

        Returns:
            Variant name (e.g., "control", "treatment", "variant-a")
        """
        try:
            flag = self._get_flag(flag_key)

            if not flag or not flag.enabled:
                return default

            variants = flag.config.get("variants", {})
            if not variants:
                return default

            # Use consistent hashing for stable variant assignment
            user_hash = self._hash_user(user.user_id, flag_key)
            total_weight = sum(v.get("weight", 0) for v in variants.values())

            if total_weight == 0:
                return default

            # Determine variant based on hash and weights
            threshold = (user_hash % 100) / 100.0 * total_weight
            cumulative_weight = 0

            for variant_name, variant_config in variants.items():
                cumulative_weight += variant_config.get("weight", 0)
                if threshold < cumulative_weight:
                    self._track_evaluation(flag_key, user, f"variant:{variant_name}")
                    return variant_name

            return default

        except Exception as e:
            print(f"Error getting variant for {flag_key}: {e}")
            return default

    def get_config(self, flag_key: str, user: User) -> Dict[str, Any]:
        """
        Get configuration object for a feature flag.
        Useful for feature flags that control behavior (not just on/off).

        Args:
            flag_key: Feature flag identifier
            user: User context

        Returns:
            Configuration dictionary
        """
        try:
            flag = self._get_flag(flag_key)

            if not flag or not self.is_enabled(flag_key, user):
                return {}

            return flag.config

        except Exception as e:
            print(f"Error getting config for {flag_key}: {e}")
            return {}

    def _get_flag(self, flag_key: str) -> Optional[FeatureFlag]:
        """Retrieve flag from cache or backend"""
        # Check cache first
        if flag_key in self.cache:
            return self.cache[flag_key]

        # Fetch from backend
        if self.backend == "redis" and self.redis_client:
            flag_data = self.redis_client.get(f"flag:{flag_key}")
            if flag_data:
                flag = self._deserialize_flag(flag_data)
                self.cache[flag_key] = flag
                return flag

        return None

    def _evaluate_strategy(self, flag: FeatureFlag, user: User) -> bool:
        """Evaluate feature flag based on strategy"""

        if flag.strategy == RolloutStrategy.ALL:
            return True

        elif flag.strategy == RolloutStrategy.NONE:
            return False

        elif flag.strategy == RolloutStrategy.PERCENTAGE:
            percentage = flag.config.get("percentage", 0)
            user_hash = self._hash_user(user.user_id, flag.key)
            return (user_hash % 100) < percentage

        elif flag.strategy == RolloutStrategy.USER_LIST:
            allowed_users = flag.config.get("users", [])
            return user.user_id in allowed_users or user.email in allowed_users

        elif flag.strategy == RolloutStrategy.USER_ATTRIBUTE:
            attribute_rules = flag.config.get("rules", [])
            return self._evaluate_attribute_rules(attribute_rules, user)

        elif flag.strategy == RolloutStrategy.GRADUAL:
            # Gradual rollout based on time
            start_percentage = flag.config.get("start_percentage", 0)
            end_percentage = flag.config.get("end_percentage", 100)
            start_time = flag.config.get("start_time")
            end_time = flag.config.get("end_time")

            if not start_time or not end_time:
                return False

            now = datetime.now()
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)

            if now < start:
                current_percentage = start_percentage
            elif now > end:
                current_percentage = end_percentage
            else:
                # Linear interpolation
                progress = (now - start).total_seconds() / (end - start).total_seconds()
                current_percentage = start_percentage + (end_percentage - start_percentage) * progress

            user_hash = self._hash_user(user.user_id, flag.key)
            return (user_hash % 100) < current_percentage

        return False

    def _evaluate_attribute_rules(self, rules: list, user: User) -> bool:
        """Evaluate user attribute rules"""
        for rule in rules:
            attribute = rule.get("attribute")
            operator = rule.get("operator")
            value = rule.get("value")

            user_value = user.get_attribute(attribute)

            if operator == "equals":
                if user_value == value:
                    return True
            elif operator == "not_equals":
                if user_value != value:
                    return True
            elif operator == "in":
                if user_value in value:
                    return True
            elif operator == "greater_than":
                if user_value > value:
                    return True
            elif operator == "less_than":
                if user_value < value:
                    return True

        return False

    def _hash_user(self, user_id: str, flag_key: str) -> int:
        """Create consistent hash for user and flag combination"""
        hash_input = f"{user_id}:{flag_key}"
        hash_value = hashlib.md5(hash_input.encode()).hexdigest()
        return int(hash_value[:8], 16)

    def _track_evaluation(self, flag_key: str, user: User, event: str):
        """Track feature flag evaluation for analytics"""
        if self.redis_client:
            analytics_key = f"analytics:flag:{flag_key}:{event}"
            self.redis_client.incr(analytics_key)

            # Store user-specific event
            user_event = {
                "flag": flag_key,
                "user_id": user.user_id,
                "event": event,
                "timestamp": datetime.now().isoformat()
            }
            self.redis_client.lpush(f"analytics:events:{flag_key}", json.dumps(user_event))

    def _deserialize_flag(self, flag_data: bytes) -> FeatureFlag:
        """Deserialize flag from storage"""
        data = json.loads(flag_data)
        return FeatureFlag(
            key=data["key"],
            name=data["name"],
            description=data["description"],
            enabled=data["enabled"],
            strategy=RolloutStrategy(data["strategy"]),
            config=data["config"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


# Example usage
def main():
    # Initialize client
    client = FeatureFlagClient(
        backend="redis",
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379")
    )

    # Create user context
    user = User(
        user_id="user123",
        email="user@example.com",
        attributes={
            "plan": "premium",
            "signup_date": "2024-01-15",
            "country": "US"
        }
    )

    # Check if feature is enabled
    if client.is_enabled("new-checkout-flow", user, default=False):
        print("Using new checkout flow")
        # New checkout logic
    else:
        print("Using legacy checkout flow")
        # Legacy checkout logic

    # A/B testing
    variant = client.get_variant("homepage-redesign", user, default="control")
    if variant == "treatment":
        print("Showing redesigned homepage")
    else:
        print("Showing original homepage")

    # Get feature configuration
    config = client.get_config("search-algorithm", user)
    max_results = config.get("max_results", 10)
    use_ml_ranking = config.get("ml_ranking", False)

    print(f"Search config: max_results={max_results}, ml_ranking={use_ml_ranking}")


if __name__ == "__main__":
    main()
