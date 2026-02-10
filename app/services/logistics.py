"""
Logistics service for calculating travel times and distances between POIs.
"""

import math
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class TravelInfo:
    """Travel information between two points."""

    distance_km: float
    duration_minutes: int
    mode: str


class LogisticsService:
    """Service for calculating travel logistics between POIs."""

    # Average speeds by transport mode (km/h)
    SPEEDS = {
        "walk": 4.5,
        "transit": 20.0,
        "drive": 30.0,
        "bike": 15.0,
    }

    # Threshold distances for mode selection (km)
    WALK_THRESHOLD = 1.5
    TRANSIT_THRESHOLD = 5.0

    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).

        Returns distance in kilometers.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of Earth in kilometers
        r = 6371

        return c * r

    def calculate_travel_time(
        self,
        from_coords: Tuple[float, float],
        to_coords: Tuple[float, float],
        mode: Optional[str] = None,
    ) -> TravelInfo:
        """
        Calculate travel time between two coordinates.

        Args:
            from_coords: (latitude, longitude) of starting point
            to_coords: (latitude, longitude) of destination
            mode: Transport mode (walk, transit, drive). Auto-selected if None.

        Returns:
            TravelInfo with distance, duration, and mode.
        """
        lat1, lon1 = from_coords
        lat2, lon2 = to_coords

        # Calculate straight-line distance
        distance = self.haversine_distance(lat1, lon1, lat2, lon2)

        # Add a factor for actual travel distance (roads aren't straight)
        actual_distance = distance * 1.3  # 30% increase for road routing

        # Auto-select mode if not specified
        if mode is None:
            if actual_distance <= self.WALK_THRESHOLD:
                mode = "walk"
            elif actual_distance <= self.TRANSIT_THRESHOLD:
                mode = "transit"
            else:
                mode = "drive"

        # Calculate duration
        speed = self.SPEEDS.get(mode, self.SPEEDS["transit"])
        duration_hours = actual_distance / speed
        duration_minutes = int(duration_hours * 60)

        # Add buffer time for mode-specific factors
        if mode == "transit":
            duration_minutes += 10  # Waiting for transit
        elif mode == "walk":
            duration_minutes += 2  # Getting oriented

        return TravelInfo(
            distance_km=round(actual_distance, 2),
            duration_minutes=max(5, duration_minutes),  # Minimum 5 minutes
            mode=mode,
        )

    def estimate_walking_time(
        self,
        distance_km: float,
    ) -> int:
        """Estimate walking time for a given distance."""
        duration_hours = distance_km / self.SPEEDS["walk"]
        return max(5, int(duration_hours * 60))

    def is_walkable(self, lat1: float, lon1: float, lat2: float, lon2: float) -> bool:
        """Check if the distance between two points is walkable."""
        distance = self.haversine_distance(lat1, lon1, lat2, lon2)
        return distance <= self.WALK_THRESHOLD

    def optimize_route(
        self,
        poi_coords: list[Tuple[float, float]],
    ) -> list[int]:
        """
        Simple nearest-neighbor algorithm to optimize visit order.

        Returns list of indices representing optimized order.

        Note: This is a simple greedy algorithm. For production,
        consider using more sophisticated routing algorithms.
        """
        if len(poi_coords) <= 2:
            return list(range(len(poi_coords)))

        visited = [False] * len(poi_coords)
        order = [0]  # Start with first POI
        visited[0] = True

        for _ in range(len(poi_coords) - 1):
            current = order[-1]
            current_coords = poi_coords[current]

            # Find nearest unvisited POI
            min_distance = float("inf")
            nearest = -1

            for i, coords in enumerate(poi_coords):
                if not visited[i]:
                    dist = self.haversine_distance(
                        current_coords[0],
                        current_coords[1],
                        coords[0],
                        coords[1],
                    )
                    if dist < min_distance:
                        min_distance = dist
                        nearest = i

            if nearest >= 0:
                order.append(nearest)
                visited[nearest] = True

        return order
