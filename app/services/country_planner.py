"""
Country-level multi-city trip planner.
Generates 2 distinct city allocation options and orchestrates per-city itinerary generation.
"""
import logging
from itertools import combinations
from typing import Dict, List, Optional, Tuple

from app.core.country_config import COUNTRY_DATABASE, get_travel_time

logger = logging.getLogger(__name__)


class CountryPlanner:
    """Orchestrates multi-city trip planning for a country."""

    def generate_allocation_options(
        self,
        country_id: str,
        total_days: int,
        group_type: str = "couple",
        vibes: Optional[List[str]] = None,
        pacing: str = "moderate",
        must_include_cities: Optional[List[str]] = None,
        exclude_cities: Optional[List[str]] = None,
        start_city: Optional[str] = None,
        end_city: Optional[str] = None,
    ) -> List[Dict]:
        """
        Generate exactly 2 distinct city allocation options.

        Option A (Classic): Based on popular routes, balanced allocation.
        Option B (Persona-Optimized): Prioritizes cities matching group_type + vibes.
        """
        vibes = vibes or []
        must_include_cities = must_include_cities or []
        exclude_cities = exclude_cities or []

        country = COUNTRY_DATABASE.get(country_id)
        if not country:
            raise ValueError(f"Country '{country_id}' not found.")

        available_cities = {
            k: v for k, v in country["cities"].items()
            if k not in exclude_cities
        }

        if not available_cities:
            raise ValueError("No cities available after applying exclusions.")

        # Generate Option A: Classic (popular route based)
        option_a = self._generate_classic_option(
            country_id, available_cities, total_days,
            must_include_cities, start_city, end_city,
        )

        # Generate Option B: Persona-optimized
        option_b = self._generate_persona_option(
            country_id, available_cities, total_days,
            group_type, vibes, must_include_cities,
            start_city, end_city,
        )

        # Ensure options are distinct
        if option_b and option_a:
            a_cities = set(c["city_id"] for c in option_a["allocation"])
            b_cities = set(c["city_id"] for c in option_b["allocation"])
            if a_cities == b_cities:
                # Try depth-vs-breadth variant
                option_b = self._generate_breadth_variant(
                    country_id, available_cities, total_days,
                    option_a, must_include_cities,
                )

        # Format final options
        options = []
        raw_options = [opt for opt in [option_a, option_b] if opt]

        for i, opt in enumerate(raw_options[:2]):
            cities_str = " + ".join(
                [f"{a['days']} days {a['city_name']}" for a in opt["allocation"]]
            )

            # Generate option name
            option_name = self._generate_option_name(opt, available_cities, i)

            # Pros and cons
            pros, cons = self._generate_pros_cons(opt, available_cities, total_days)

            # Compute match score based on vibes + group_type overlap
            match_score = self._compute_match_score(
                opt, available_cities, group_type, vibes
            )

            options.append({
                "option_id": i + 1,
                "option_name": option_name,
                "description": cities_str,
                "cities": opt["allocation"],
                "total_days": total_days,
                "total_travel_time_minutes": opt["total_travel_minutes"],
                "match_score": match_score,
                "pros": pros[:3],
                "cons": cons[:2],
            })

        # Mark recommended option (higher match score)
        if len(options) >= 2:
            recommended = 0 if options[0]["match_score"] >= options[1]["match_score"] else 1
        else:
            recommended = 0

        return options, recommended

    def _generate_classic_option(
        self,
        country_id: str,
        available_cities: Dict,
        total_days: int,
        must_include: List[str],
        start_city: Optional[str],
        end_city: Optional[str],
    ) -> Optional[Dict]:
        """Generate a classic option based on popular routes."""
        country = COUNTRY_DATABASE[country_id]
        popular_routes = country.get("popular_routes", [])

        best_route = None
        best_score = -1

        for route in popular_routes:
            # Check all cities in route are available
            if not all(c in available_cities for c in route):
                continue
            # Check must-include cities
            if not all(c in route for c in must_include):
                continue

            # Check total minimum days fit
            min_days = sum(available_cities[c]["min_days"] for c in route)
            if min_days > total_days:
                continue

            # Score: prefer routes that fit well within total_days
            ideal_days = sum(available_cities[c]["ideal_days"] for c in route)
            fit_score = 10 - abs(ideal_days - total_days)

            # Bonus for including high-priority cities
            priority_score = sum(6 - available_cities[c].get("priority", 5) for c in route)

            total_score = fit_score + priority_score
            if total_score > best_score:
                best_score = total_score
                best_route = route

        if not best_route:
            # Fallback: use top priority cities
            sorted_cities = sorted(
                available_cities.keys(),
                key=lambda x: available_cities[x].get("priority", 5)
            )
            best_route = []
            running_days = 0
            for city_id in sorted_cities:
                city = available_cities[city_id]
                if running_days + city["min_days"] <= total_days:
                    best_route.append(city_id)
                    running_days += city["min_days"]

            # Ensure must-include cities
            for city_id in must_include:
                if city_id not in best_route and city_id in available_cities:
                    best_route.append(city_id)

        allocation = self._allocate_days(country_id, best_route, total_days, available_cities)
        if not allocation:
            return None

        travel_time = self._compute_travel_time(country_id, allocation)
        return {
            "allocation": allocation,
            "total_travel_minutes": travel_time,
            "type": "classic",
        }

    def _generate_persona_option(
        self,
        country_id: str,
        available_cities: Dict,
        total_days: int,
        group_type: str,
        vibes: List[str],
        must_include: List[str],
        start_city: Optional[str],
        end_city: Optional[str],
    ) -> Optional[Dict]:
        """Generate persona-optimized option prioritizing vibe + group match."""
        # Score each city
        city_scores = {}
        for city_id, city_data in available_cities.items():
            city_vibes = set(city_data.get("vibes", []))
            city_best_for = set(city_data.get("best_for", []))

            vibe_overlap = len(set(vibes) & city_vibes) / max(len(vibes), 1)
            group_match = 1.0 if group_type in city_best_for else 0.3

            score = vibe_overlap * 0.6 + group_match * 0.4
            city_scores[city_id] = score

        # Sort cities by persona score
        sorted_cities = sorted(city_scores.keys(), key=lambda x: city_scores[x], reverse=True)

        # Build route: start with must-include, then add highest-scoring
        route = list(must_include)
        for city_id in sorted_cities:
            if city_id not in route:
                route.append(city_id)

        # Trim to fit total_days
        final_route = []
        running_days = 0
        for city_id in route:
            city = available_cities[city_id]
            if running_days + city["min_days"] <= total_days:
                final_route.append(city_id)
                running_days += city["min_days"]

        if not final_route:
            return None

        allocation = self._allocate_days(country_id, final_route, total_days, available_cities)
        if not allocation:
            return None

        travel_time = self._compute_travel_time(country_id, allocation)
        return {
            "allocation": allocation,
            "total_travel_minutes": travel_time,
            "type": "persona",
        }

    def _generate_breadth_variant(
        self,
        country_id: str,
        available_cities: Dict,
        total_days: int,
        existing_option: Dict,
        must_include: List[str],
    ) -> Optional[Dict]:
        """Generate a breadth variant (more cities, fewer days each) as fallback."""
        existing_city_ids = set(c["city_id"] for c in existing_option["allocation"])
        existing_count = len(existing_city_ids)

        # Try adding one more city
        all_cities = sorted(
            available_cities.keys(),
            key=lambda x: available_cities[x].get("priority", 5)
        )

        for city_id in all_cities:
            if city_id not in existing_city_ids:
                trial_route = list(existing_city_ids) + [city_id]
                min_days = sum(available_cities[c]["min_days"] for c in trial_route)
                if min_days <= total_days:
                    allocation = self._allocate_days(
                        country_id, trial_route, total_days, available_cities
                    )
                    if allocation:
                        travel_time = self._compute_travel_time(country_id, allocation)
                        return {
                            "allocation": allocation,
                            "total_travel_minutes": travel_time,
                            "type": "breadth",
                        }

        # If can't add more, try with fewer cities (depth variant)
        if existing_count > 2:
            depth_route = list(existing_city_ids)[:existing_count - 1]
            # Ensure must-includes
            for city_id in must_include:
                if city_id not in depth_route:
                    depth_route.append(city_id)

            allocation = self._allocate_days(
                country_id, depth_route, total_days, available_cities
            )
            if allocation:
                travel_time = self._compute_travel_time(country_id, allocation)
                return {
                    "allocation": allocation,
                    "total_travel_minutes": travel_time,
                    "type": "depth",
                }

        return None

    def _allocate_days(
        self,
        country_id: str,
        city_ids: List[str],
        total_days: int,
        cities_data: Dict,
    ) -> Optional[List[Dict]]:
        """Allocate days to cities based on priority and ideal duration."""
        sorted_cities = sorted(
            city_ids,
            key=lambda x: cities_data[x].get("priority", 5)
        )

        allocation = []
        remaining_days = total_days

        # First pass: assign minimum days
        for city_id in sorted_cities:
            city = cities_data[city_id]
            min_days = city.get("min_days", 1)

            if remaining_days < min_days:
                return None

            allocation.append({
                "city_id": city_id,
                "city_name": city["name"],
                "days": min_days,
                "highlights": city.get("highlights", [])[:3],
            })
            remaining_days -= min_days

        # Second pass: distribute remaining days by priority and ideal gap
        while remaining_days > 0:
            best_idx = None
            best_score = -1

            for i, alloc in enumerate(allocation):
                city_id = alloc["city_id"]
                city = cities_data[city_id]
                current_days = alloc["days"]
                max_days = city.get("max_days", 5)
                ideal_days = city.get("ideal_days", 2)
                priority = city.get("priority", 5)

                if current_days >= max_days:
                    continue

                score = (6 - priority) * 10
                if current_days < ideal_days:
                    score += 20

                if score > best_score:
                    best_score = score
                    best_idx = i

            if best_idx is None:
                break

            allocation[best_idx]["days"] += 1
            remaining_days -= 1

        # Add travel time from previous city
        for i in range(1, len(allocation)):
            prev_city = allocation[i - 1]["city_id"]
            curr_city = allocation[i]["city_id"]
            travel_min = get_travel_time(country_id, prev_city, curr_city)
            allocation[i]["arrival_from"] = allocation[i - 1]["city_name"]
            allocation[i]["travel_time_minutes"] = travel_min if travel_min < 999 else None

        return allocation

    def _compute_travel_time(self, country_id: str, allocation: List[Dict]) -> int:
        """Compute total inter-city travel time."""
        total = 0
        for i in range(1, len(allocation)):
            t = get_travel_time(
                country_id,
                allocation[i - 1]["city_id"],
                allocation[i]["city_id"],
            )
            if t < 999:
                total += t
        return total

    def _compute_match_score(
        self,
        option: Dict,
        available_cities: Dict,
        group_type: str,
        vibes: List[str],
    ) -> float:
        """Compute how well an option matches user preferences."""
        if not option["allocation"]:
            return 0.0

        total_score = 0.0
        total_weight = 0.0

        for alloc in option["allocation"]:
            city_id = alloc["city_id"]
            city = available_cities.get(city_id, {})
            days = alloc["days"]

            city_vibes = set(city.get("vibes", []))
            city_best_for = set(city.get("best_for", []))

            vibe_overlap = len(set(vibes) & city_vibes) / max(len(vibes), 1)
            group_match = 1.0 if group_type in city_best_for else 0.3

            city_score = vibe_overlap * 0.6 + group_match * 0.4
            total_score += city_score * days
            total_weight += days

        return min(total_score / max(total_weight, 1), 1.0)

    def _generate_option_name(self, option: Dict, available_cities: Dict, index: int) -> str:
        """Generate a descriptive name for an allocation option."""
        city_vibes = []
        for alloc in option["allocation"]:
            city = available_cities.get(alloc["city_id"], {})
            city_vibes.extend(city.get("vibes", []))

        if "romantic" in city_vibes and "beach" in city_vibes:
            return "Romance & Relaxation"
        elif "cultural" in city_vibes and "art" in city_vibes:
            return "Art & Culture Tour"
        elif "foodie" in city_vibes and "relaxation" in city_vibes:
            return "Culinary Journey"
        elif "adventure" in city_vibes:
            return "Adventure Trail"
        elif "historical" in city_vibes and "cultural" in city_vibes:
            return "History & Heritage"
        elif "modern" in city_vibes and "shopping" in city_vibes:
            return "City & Shopping"
        elif option.get("type") == "classic":
            return "Classic Route"
        elif option.get("type") == "persona":
            return "Personalized Pick"
        elif option.get("type") == "breadth":
            return "Explorer's Choice"
        elif option.get("type") == "depth":
            return "Deep Dive"
        else:
            return f"Option {index + 1}"

    def _generate_pros_cons(
        self, option: Dict, available_cities: Dict, total_days: int
    ) -> Tuple[List[str], List[str]]:
        """Generate pros and cons for an allocation option."""
        pros = []
        cons = []

        num_cities = len(option["allocation"])
        travel_min = option["total_travel_minutes"]

        if num_cities == 1:
            pros.append("Deep exploration of one city")
            cons.append("Less variety")
        elif num_cities >= 3:
            pros.append("Great variety of experiences")
            if travel_min > 300:
                cons.append(f"More travel time ({travel_min // 60}h total)")
        elif num_cities == 2:
            pros.append("Good balance of depth and variety")

        if travel_min < 180:
            pros.append("Minimal travel time between cities")

        for alloc in option["allocation"]:
            city = available_cities.get(alloc["city_id"], {})
            if alloc["days"] >= city.get("ideal_days", 2):
                pros.append(f"Enough time in {alloc['city_name']}")
                break  # Only add one of these

        for alloc in option["allocation"]:
            city = available_cities.get(alloc["city_id"], {})
            if alloc["days"] < city.get("ideal_days", 2):
                cons.append(f"Tight schedule in {alloc['city_name']}")
                break

        return pros, cons

    async def ensure_city_data(self, city_key: str, db_session, min_pois: int = 20) -> bool:
        """Check if city has enough POIs; trigger fetch if needed."""
        from sqlalchemy import select, func
        from app.models.poi import POI

        stmt = select(func.count()).where(POI.city == city_key.title())
        result = await db_session.execute(stmt)
        count = result.scalar() or 0

        if count >= min_pois:
            return True

        logger.info(f"City {city_key} has {count} POIs (need {min_pois}), triggering fetch...")
        try:
            from app.services.data_ingestion.overture_fetcher import (
                OvertureMapsFetcher,
                DatabaseSeeder,
            )

            fetcher = OvertureMapsFetcher()
            raw_pois = fetcher.fetch_pois(city_key, limit=200)
            scored_pois = fetcher.score_pois(raw_pois, city_key)

            seeder = DatabaseSeeder(db_session)
            inserted = await seeder.seed_pois(scored_pois, city_key)
            await db_session.commit()

            logger.info(f"Auto-seeded {inserted} POIs for {city_key}")
            return inserted > 0
        except Exception as e:
            logger.error(f"Failed to auto-seed POIs for {city_key}: {e}")
            return False
