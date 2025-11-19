"""
Production Matchmaking Service with Skill-Based Rating and Party Support
Implements ELO-based matchmaking with region filtering and dynamic queue expansion
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import heapq


class GameMode(Enum):
    DUEL_1V1 = "1v1"
    TEAM_2V2 = "2v2"
    SQUAD_5V5 = "5v5"
    BATTLE_ROYALE = "battle_royale"


class Region(Enum):
    NA_WEST = "na-west"
    NA_EAST = "na-east"
    EU_WEST = "eu-west"
    EU_EAST = "eu-east"
    ASIA = "asia"
    OCEANIA = "oceania"


@dataclass
class Player:
    """Player matchmaking profile"""
    id: str
    username: str
    skill_rating: float  # ELO rating
    rating_uncertainty: float = 50.0  # Glicko-2 RD
    region: Region = Region.NA_WEST
    preferred_modes: List[GameMode] = field(default_factory=list)
    party_id: Optional[str] = None
    is_party_leader: bool = False
    queued_at: float = 0.0
    games_played: int = 0
    win_rate: float = 0.5


@dataclass
class Party:
    """Group of players queuing together"""
    id: str
    leader_id: str
    member_ids: List[str]
    avg_skill_rating: float
    created_at: float


@dataclass
class Match:
    """Created match ready to start"""
    id: str
    mode: GameMode
    teams: Dict[str, List[str]]  # team_name -> [player_ids]
    player_ids: List[str]
    avg_skill_rating: float
    skill_variance: float
    region: Region
    created_at: float
    server_id: Optional[str] = None


class MatchmakingQueue:
    """Priority queue for matchmaking with skill-based ordering"""

    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.parties: Dict[str, Party] = {}
        self.heap: List = []  # Priority queue ordered by wait time

    def add_player(self, player: Player):
        """Add player to queue"""
        self.players[player.id] = player
        player.queued_at = time.time()

        # Add to priority queue (priority = negative wait time for min heap)
        heapq.heappush(self.heap, (player.queued_at, player.id))

    def add_party(self, party: Party):
        """Add party to queue"""
        self.parties[party.id] = party

        # Add party leader to heap as representative
        if party.leader_id in self.players:
            leader = self.players[party.leader_id]
            heapq.heappush(self.heap, (leader.queued_at, party.id))

    def remove_players(self, player_ids: List[str]):
        """Remove players from queue"""
        for player_id in player_ids:
            if player_id in self.players:
                del self.players[player_id]

    def get_candidates(self, count: int) -> List[Player]:
        """Get top candidates by wait time"""
        candidates = []

        # Make a copy to iterate
        temp_heap = list(self.heap)
        heapq.heapify(temp_heap)

        while temp_heap and len(candidates) < count:
            _, player_id = heapq.heappop(temp_heap)

            if player_id in self.players:
                candidates.append(self.players[player_id])

        return candidates

    def size(self) -> int:
        return len(self.players)


class MatchmakingService:
    """Main matchmaking service"""

    def __init__(self, config: Dict):
        self.config = config
        self.queues: Dict[GameMode, MatchmakingQueue] = {}
        self.matches: List[Match] = []
        self.running = False

        # Initialize queues for each mode
        for mode in GameMode:
            self.queues[mode] = MatchmakingQueue()

        # ELO settings
        self.K_FACTOR = 32  # Rating change multiplier
        self.BASE_SKILL_RANGE = 100  # Base skill rating tolerance
        self.MAX_SKILL_RANGE = 500  # Maximum skill rating tolerance
        self.RANGE_EXPANSION_RATE = 50  # Expand by 50 per 10 seconds

    async def start(self):
        """Start matchmaking service"""
        self.running = True
        asyncio.create_task(self._matchmaking_loop())

    async def stop(self):
        """Stop matchmaking service"""
        self.running = False

    async def add_to_queue(self, player: Player, mode: GameMode) -> Optional[Match]:
        """Add player to matchmaking queue"""

        if mode not in self.queues:
            raise ValueError(f"Invalid game mode: {mode}")

        queue = self.queues[mode]

        # Check if player is in a party
        if player.party_id:
            party = await self._get_party(player.party_id)
            if party:
                # Add entire party
                queue.add_party(party)
                print(f"Party {party.id} joined {mode.value} queue")
            else:
                # Party not found, add as solo
                queue.add_player(player)
        else:
            # Solo player
            queue.add_player(player)

        print(f"Player {player.username} joined {mode.value} queue (rating: {player.skill_rating})")

        # Immediately try to find match
        match = await self._try_create_match(mode)

        return match

    async def _matchmaking_loop(self):
        """Main matchmaking loop"""

        while self.running:
            # Check each mode for potential matches
            for mode in GameMode:
                await self._try_create_match(mode)

            # Run every second
            await asyncio.sleep(1)

    async def _try_create_match(self, mode: GameMode) -> Optional[Match]:
        """Try to create a match for given mode"""

        queue = self.queues[mode]
        match_size = self._get_match_size(mode)

        if queue.size() < match_size:
            return None

        # Get candidates
        candidates = queue.get_candidates(match_size * 3)  # Get extra for filtering

        if len(candidates) < match_size:
            return None

        # Try to find balanced match
        match_players = self._find_balanced_group(candidates, match_size)

        if match_players:
            # Create match
            match = await self._create_match(mode, match_players)

            # Remove players from queue
            player_ids = [p.id for p in match_players]
            queue.remove_players(player_ids)

            print(f"Created match {match.id} for mode {mode.value}")
            return match

        return None

    def _find_balanced_group(self, candidates: List[Player], size: int) -> Optional[List[Player]]:
        """Find balanced group of players"""

        # Sort by skill rating
        sorted_candidates = sorted(candidates, key=lambda p: p.skill_rating)

        # Try to find group with minimal skill variance
        best_group = None
        best_variance = float('inf')

        for i in range(len(sorted_candidates) - size + 1):
            group = sorted_candidates[i:i + size]

            # Check constraints
            if not self._check_match_constraints(group):
                continue

            # Calculate variance
            ratings = [p.skill_rating for p in group]
            variance = max(ratings) - min(ratings)

            if variance < best_variance:
                best_variance = variance
                best_group = group

        return best_group

    def _check_match_constraints(self, players: List[Player]) -> bool:
        """Check if players meet matchmaking constraints"""

        # Get skill ratings
        ratings = [p.skill_rating for p in players]
        skill_range = max(ratings) - min(ratings)

        # Calculate dynamic tolerance based on wait time
        max_wait = max(time.time() - p.queued_at for p in players)
        tolerance = self._calculate_skill_tolerance(max_wait)

        if skill_range > tolerance:
            return False

        # Check region compatibility
        regions = set(p.region for p in players)
        if len(regions) > 2:  # Too many different regions
            return False

        # Check party constraints
        party_ids = set(p.party_id for p in players if p.party_id)
        if len(party_ids) > len(players) / 2:  # Too many parties
            return False

        return True

    def _calculate_skill_tolerance(self, wait_time: float) -> float:
        """Calculate skill rating tolerance based on wait time"""

        # Expand tolerance over time
        expansion = (wait_time / 10) * self.RANGE_EXPANSION_RATE

        tolerance = self.BASE_SKILL_RANGE + expansion

        # Cap at maximum
        return min(tolerance, self.MAX_SKILL_RANGE)

    async def _create_match(self, mode: GameMode, players: List[Player]) -> Match:
        """Create match from players"""

        match_id = self._generate_match_id()

        # Calculate match stats
        avg_rating = sum(p.skill_rating for p in players) / len(players)
        ratings = [p.skill_rating for p in players]
        skill_variance = max(ratings) - min(ratings)

        # Determine region (most common)
        region_counts = {}
        for p in players:
            region_counts[p.region] = region_counts.get(p.region, 0) + 1
        region = max(region_counts.items(), key=lambda x: x[1])[0]

        # Create teams
        teams = self._create_teams(mode, players)

        match = Match(
            id=match_id,
            mode=mode,
            teams=teams,
            player_ids=[p.id for p in players],
            avg_skill_rating=avg_rating,
            skill_variance=skill_variance,
            region=region,
            created_at=time.time()
        )

        # Assign server
        match.server_id = await self._assign_server(match)

        self.matches.append(match)

        # Notify players
        await self._notify_match_ready(match)

        return match

    def _create_teams(self, mode: GameMode, players: List[Player]) -> Dict[str, List[str]]:
        """Create balanced teams for match"""

        if mode == GameMode.DUEL_1V1:
            return {
                "player1": [players[0].id],
                "player2": [players[1].id]
            }

        elif mode in [GameMode.TEAM_2V2, GameMode.SQUAD_5V5]:
            # Balance teams by skill
            sorted_players = sorted(players, key=lambda p: p.skill_rating, reverse=True)

            team1 = []
            team2 = []

            # Snake draft
            for i, player in enumerate(sorted_players):
                if i % 2 == 0:
                    team1.append(player.id)
                else:
                    team2.append(player.id)

            return {
                "team1": team1,
                "team2": team2
            }

        elif mode == GameMode.BATTLE_ROYALE:
            # Free-for-all
            return {
                "players": [p.id for p in players]
            }

        return {}

    async def update_ratings(self, match_id: str, results: Dict[str, bool]):
        """Update player ratings after match"""

        match = next((m for m in self.matches if m.id == match_id), None)
        if not match:
            return

        # ELO calculation for each player
        for player_id, won in results.items():
            player = await self._get_player(player_id)
            if not player:
                continue

            # Calculate opponent average rating
            opponent_ids = [pid for pid in match.player_ids if pid != player_id]
            opponents = [await self._get_player(pid) for pid in opponent_ids]
            opponent_avg = sum(p.skill_rating for p in opponents if p) / len(opponents)

            # Expected score
            expected = 1 / (1 + 10 ** ((opponent_avg - player.skill_rating) / 400))

            # Actual score
            actual = 1.0 if won else 0.0

            # New rating
            new_rating = player.skill_rating + self.K_FACTOR * (actual - expected)

            # Update player
            await self._update_player_rating(player_id, new_rating)

            print(f"Updated {player.username} rating: {player.skill_rating:.1f} -> {new_rating:.1f}")

    def _get_match_size(self, mode: GameMode) -> int:
        """Get required number of players for mode"""
        sizes = {
            GameMode.DUEL_1V1: 2,
            GameMode.TEAM_2V2: 4,
            GameMode.SQUAD_5V5: 10,
            GameMode.BATTLE_ROYALE: 100
        }
        return sizes.get(mode, 2)

    def _generate_match_id(self) -> str:
        """Generate unique match ID"""
        timestamp = str(time.time())
        return f"match_{hashlib.md5(timestamp.encode()).hexdigest()[:16]}"

    async def _assign_server(self, match: Match) -> str:
        """Assign game server for match"""
        # In production: select server in player's region with capacity
        return f"server_{match.region.value}_1"

    async def _notify_match_ready(self, match: Match):
        """Notify players that match is ready"""
        # Send notifications to players
        for player_id in match.player_ids:
            print(f"Notifying player {player_id} - match {match.id} ready")

    async def _get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        # Mock implementation
        return None

    async def _get_party(self, party_id: str) -> Optional[Party]:
        """Get party by ID"""
        # Mock implementation
        return None

    async def _update_player_rating(self, player_id: str, new_rating: float):
        """Update player's skill rating"""
        # Mock implementation
        pass

    def get_queue_stats(self, mode: GameMode) -> Dict:
        """Get queue statistics"""
        queue = self.queues.get(mode)
        if not queue:
            return {}

        players = list(queue.players.values())

        if not players:
            return {
                "mode": mode.value,
                "players_in_queue": 0,
                "avg_wait_time": 0,
                "avg_skill_rating": 0
            }

        current_time = time.time()
        wait_times = [current_time - p.queued_at for p in players]

        return {
            "mode": mode.value,
            "players_in_queue": len(players),
            "avg_wait_time": sum(wait_times) / len(wait_times),
            "max_wait_time": max(wait_times),
            "avg_skill_rating": sum(p.skill_rating for p in players) / len(players),
            "skill_range": max(p.skill_rating for p in players) - min(p.skill_rating for p in players)
        }


# Example usage
async def main():
    config = {}
    service = MatchmakingService(config)
    await service.start()

    # Create test players
    players = [
        Player(id="p1", username="Player1", skill_rating=1500, region=Region.NA_WEST),
        Player(id="p2", username="Player2", skill_rating=1520, region=Region.NA_WEST),
        Player(id="p3", username="Player3", skill_rating=1480, region=Region.NA_WEST),
        Player(id="p4", username="Player4", skill_rating=1510, region=Region.NA_WEST),
    ]

    # Add to queue
    for player in players:
        await service.add_to_queue(player, GameMode.TEAM_2V2)

    # Check stats
    stats = service.get_queue_stats(GameMode.TEAM_2V2)
    print(f"Queue stats: {stats}")

    # Wait for matchmaking
    await asyncio.sleep(2)

    await service.stop()


if __name__ == "__main__":
    asyncio.run(main())
