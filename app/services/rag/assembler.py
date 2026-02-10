from typing import List, Optional, Set
from datetime import date, time, timedelta
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from decimal import Decimal

from app.models.poi import POI
from app.models.itinerary import Itinerary, ItineraryDay, ItineraryItem
from app.schemas.itinerary import TripRequestCreate
from app.services.rag.scorer import ScoredPOI
from app.core.config import PACING_CONFIG, PERSONA_DURATION_MULTIPLIERS, BREAK_RULES


@dataclass
class TimeSlot:
    """A time slot in the day's schedule."""

    start_time: time
    end_time: time
    slot_type: str  # "anchor", "activity", "meal", "buffer"
    duration_minutes: int


@dataclass
class DayPlan:
    """A plan for a single day."""

    day_number: int
    date: date
    theme: str = ""
    items: List["PlannedItem"] = field(default_factory=list)
    estimated_cost: Decimal = Decimal("0.00")

    def add_item(self, item: "PlannedItem"):
        self.items.append(item)
        if item.poi.avg_cost_per_person:
            self.estimated_cost += item.poi.avg_cost_per_person


@dataclass
class PlannedItem:
    """A planned item in the itinerary."""

    poi: POI
    start_time: time
    end_time: time
    sequence_order: int
    selection_reason: str
    persona_match_score: float
    travel_time_from_previous: int = 0
    travel_mode: str = "walk"
    is_break: bool = False  # True for relaxation breaks
    break_type: str = None  # "coffee", "gelato", "rest", etc.


class ItineraryAssembler:
    """Assembles the final itinerary from scored POIs."""

    # Default day schedule
    DAY_START = time(9, 0)  # 9 AM
    DAY_END = time(22, 0)  # 10 PM

    # Meal times
    LUNCH_START = time(12, 30)
    LUNCH_END = time(14, 0)
    DINNER_START = time(19, 30)
    DINNER_END = time(21, 0)

    def __init__(self, pacing: str = "moderate", group_type: str = None):
        self.pacing = pacing
        self.group_type = group_type
        self.config = PACING_CONFIG.get(pacing, PACING_CONFIG["moderate"])

    def _get_persona_duration(self, poi: POI) -> int:
        """Get duration adjusted for the traveler's persona/group type."""
        base_duration = poi.typical_duration_minutes or 60

        if not self.group_type:
            return base_duration

        multipliers = PERSONA_DURATION_MULTIPLIERS.get(self.group_type, {})
        subcategory = poi.subcategory or "default"

        # Get multiplier for subcategory, or default
        multiplier = multipliers.get(subcategory, multipliers.get("default", 1.0))

        return int(base_duration * multiplier)

    def _is_heavy_activity(self, poi: POI) -> bool:
        """Check if activity is 'heavy' and needs a break after."""
        subcategory = poi.subcategory or ""
        duration = poi.typical_duration_minutes or 0

        heavy_subcategories = BREAK_RULES.get("heavy_subcategories", ["museum", "historical"])
        heavy_min_duration = BREAK_RULES.get("heavy_min_duration", 90)

        return subcategory in heavy_subcategories and duration >= heavy_min_duration

    def _get_break_duration(self, poi: POI) -> int:
        """Get the appropriate break duration after an activity."""
        if self._is_heavy_activity(poi):
            return self.config.get("break_after_heavy_minutes", 45)
        elif poi.typical_duration_minutes and poi.typical_duration_minutes >= 60:
            return self.config.get("break_after_moderate_minutes", 15)
        return 0

    def build_itinerary(
        self,
        scored_pois: List[ScoredPOI],
        trip_request: TripRequestCreate,
        must_include_ids: Optional[List[UUID]] = None,
    ) -> Itinerary:
        """
        Build a complete itinerary from scored POIs.

        Phase 3 of the RAG pipeline: Assemble the day-by-day itinerary
        using a top-down progressive approach.
        """
        # Set group type for persona-based durations
        self.group_type = trip_request.group_type

        num_days = (trip_request.end_date - trip_request.start_date).days + 1
        used_poi_ids: Set[UUID] = set()

        # Separate POIs by type
        anchors = [s for s in scored_pois if self._is_anchor_worthy(s.poi)]
        restaurants = [s for s in scored_pois if s.poi.category == "restaurant"]
        activities = [s for s in scored_pois if s.poi.category in ["activity", "shopping", "attraction"]]

        # Handle must-include POIs
        must_include_scored = []
        if must_include_ids:
            for scored in scored_pois:
                if scored.poi.id in must_include_ids:
                    must_include_scored.append(scored)

        day_plans = []
        current_date = trip_request.start_date

        for day_num in range(1, num_days + 1):
            day_plan = self._build_day(
                day_number=day_num,
                date=current_date,
                anchors=anchors,
                restaurants=restaurants,
                activities=activities,
                used_poi_ids=used_poi_ids,
                must_include=must_include_scored if day_num == 1 else [],
            )
            day_plans.append(day_plan)
            current_date += timedelta(days=1)

        # Create itinerary model
        itinerary = self._create_itinerary_model(day_plans, trip_request)

        return itinerary

    def _build_day(
        self,
        day_number: int,
        date: date,
        anchors: List[ScoredPOI],
        restaurants: List[ScoredPOI],
        activities: List[ScoredPOI],
        used_poi_ids: Set[UUID],
        must_include: List[ScoredPOI] = None,
    ) -> DayPlan:
        """Build a single day's plan."""
        day_plan = DayPlan(day_number=day_number, date=date)
        sequence = 1

        # 1. Select anchor activities for the day
        num_anchors = self.config["anchors_per_day"]
        day_anchors = self._select_best_available(
            anchors, used_poi_ids, num_anchors, must_include or []
        )

        # 2. Assign morning anchor (if available)
        current_time = self.DAY_START
        if day_anchors:
            morning_anchor = day_anchors[0]
            # Use persona-adjusted duration
            duration = self._get_persona_duration(morning_anchor.poi)
            start = current_time
            end = self._add_minutes(start, duration)

            item = PlannedItem(
                poi=morning_anchor.poi,
                start_time=start,
                end_time=end,
                sequence_order=sequence,
                selection_reason=morning_anchor.selection_reason,
                persona_match_score=morning_anchor.final_score,
            )
            day_plan.add_item(item)
            used_poi_ids.add(morning_anchor.poi.id)
            sequence += 1
            current_time = end

            # Add break after heavy activity if configured
            if self.config.get("must_include_breaks", False):
                break_duration = self._get_break_duration(morning_anchor.poi)
                if break_duration > 0:
                    current_time = self._add_minutes(current_time, break_duration)

        # 3. Add lunch
        lunch = self._select_best_available(restaurants, used_poi_ids, 1)
        if lunch:
            lunch_poi = lunch[0]
            item = PlannedItem(
                poi=lunch_poi.poi,
                start_time=self.LUNCH_START,
                end_time=self.LUNCH_END,
                sequence_order=sequence,
                selection_reason=lunch_poi.selection_reason,
                persona_match_score=lunch_poi.final_score,
                travel_time_from_previous=15,
            )
            day_plan.add_item(item)
            used_poi_ids.add(lunch_poi.poi.id)
            sequence += 1

        # 4. Afternoon anchor (if we have a second one)
        afternoon_start = time(14, 30)
        if len(day_anchors) > 1:
            afternoon_anchor = day_anchors[1]
            # Use persona-adjusted duration
            duration = self._get_persona_duration(afternoon_anchor.poi)
            start = afternoon_start
            end = self._add_minutes(start, duration)

            item = PlannedItem(
                poi=afternoon_anchor.poi,
                start_time=start,
                end_time=end,
                sequence_order=sequence,
                selection_reason=afternoon_anchor.selection_reason,
                persona_match_score=afternoon_anchor.final_score,
                travel_time_from_previous=20,
            )
            day_plan.add_item(item)
            used_poi_ids.add(afternoon_anchor.poi.id)
            sequence += 1
            current_time = end

            # Add break after heavy activity if configured
            if self.config.get("must_include_breaks", False):
                break_duration = self._get_break_duration(afternoon_anchor.poi)
                if break_duration > 0:
                    current_time = self._add_minutes(current_time, break_duration)
        else:
            current_time = afternoon_start

        # 5. Fill remaining slots with activities based on pacing
        remaining_slots = self.config["max_activities"] - len(day_plan.items)
        if remaining_slots > 0:
            fillers = self._select_best_available(activities, used_poi_ids, remaining_slots)
            # Start from current_time (already set after afternoon anchor + break)
            if current_time < time(17, 0):
                current_time = time(17, 0)

            for filler in fillers:
                if current_time >= self.DINNER_START:
                    break

                # Use persona-adjusted duration
                duration = self._get_persona_duration(filler.poi)
                end = self._add_minutes(current_time, duration)

                item = PlannedItem(
                    poi=filler.poi,
                    start_time=current_time,
                    end_time=end,
                    sequence_order=sequence,
                    selection_reason=filler.selection_reason,
                    persona_match_score=filler.final_score,
                    travel_time_from_previous=15,
                )
                day_plan.add_item(item)
                used_poi_ids.add(filler.poi.id)
                sequence += 1

                # Add buffer (and extra break if heavy)
                buffer = self.config["min_buffer_minutes"]
                if self.config.get("must_include_breaks", False):
                    buffer += self._get_break_duration(filler.poi)
                current_time = self._add_minutes(end, buffer)

        # 6. Add dinner
        dinner = self._select_best_available(restaurants, used_poi_ids, 1)
        if dinner:
            dinner_poi = dinner[0]
            item = PlannedItem(
                poi=dinner_poi.poi,
                start_time=self.DINNER_START,
                end_time=self.DINNER_END,
                sequence_order=sequence,
                selection_reason=dinner_poi.selection_reason,
                persona_match_score=dinner_poi.final_score,
                travel_time_from_previous=15,
            )
            day_plan.add_item(item)
            used_poi_ids.add(dinner_poi.poi.id)

        # Generate day theme based on items
        day_plan.theme = self._generate_day_theme(day_plan)

        return day_plan

    def _select_best_available(
        self,
        scored_pois: List[ScoredPOI],
        used_ids: Set[UUID],
        count: int,
        priority: List[ScoredPOI] = None,
    ) -> List[ScoredPOI]:
        """Select the best available POIs that haven't been used."""
        selected = []

        # First, add priority items
        if priority:
            for p in priority:
                if p.poi.id not in used_ids and len(selected) < count:
                    selected.append(p)

        # Then fill with best available
        for scored in scored_pois:
            if len(selected) >= count:
                break
            if scored.poi.id not in used_ids and scored not in selected:
                selected.append(scored)

        return selected

    def _is_anchor_worthy(self, poi: POI) -> bool:
        """Determine if a POI should be considered an anchor activity."""
        # Anchors are typically major attractions or activities
        if poi.category in ["attraction", "activity"]:
            # Long duration suggests major activity
            if poi.typical_duration_minutes and poi.typical_duration_minutes >= 90:
                return True
            # Must-see attractions are anchors
            if poi.attributes and poi.attributes.is_must_see:
                return True
        return False

    def _add_minutes(self, t: time, minutes: int) -> time:
        """Add minutes to a time object."""
        total_minutes = t.hour * 60 + t.minute + minutes
        hours = (total_minutes // 60) % 24
        mins = total_minutes % 60
        return time(hours, mins)

    def _generate_day_theme(self, day_plan: DayPlan) -> str:
        """Generate a theme for the day based on its activities."""
        if not day_plan.items:
            return "Free Day"

        categories = [item.poi.category for item in day_plan.items if item.poi.category]
        subcategories = [item.poi.subcategory for item in day_plan.items if item.poi.subcategory]
        neighborhoods = [item.poi.neighborhood for item in day_plan.items if item.poi.neighborhood]

        # Determine theme based on dominant categories
        if "attraction" in categories:
            if any(s in subcategories for s in ["museum", "gallery"]):
                return "Art & Culture Day"
            if any(s in subcategories for s in ["historical", "ruins", "monument"]):
                return "History & Heritage Day"
            return "Sightseeing Day"

        if neighborhoods:
            main_neighborhood = max(set(neighborhoods), key=neighborhoods.count)
            return f"Exploring {main_neighborhood}"

        return "Discovery Day"

    def _create_itinerary_model(
        self,
        day_plans: List[DayPlan],
        trip_request: TripRequestCreate,
    ) -> Itinerary:
        """Create the SQLAlchemy itinerary model from day plans."""
        total_cost = sum(dp.estimated_cost for dp in day_plans)

        itinerary = Itinerary(
            id=uuid4(),
            total_estimated_cost=total_cost,
            generation_method="rag_v1",
        )

        for day_plan in day_plans:
            itinerary_day = ItineraryDay(
                id=uuid4(),
                day_number=day_plan.day_number,
                date=day_plan.date,
                theme=day_plan.theme,
                estimated_cost=day_plan.estimated_cost,
                pacing_score=Decimal(str(len(day_plan.items) / self.config["max_activities"])),
            )

            for planned_item in day_plan.items:
                item = ItineraryItem(
                    id=uuid4(),
                    poi_id=planned_item.poi.id,
                    sequence_order=planned_item.sequence_order,
                    start_time=planned_item.start_time,
                    end_time=planned_item.end_time,
                    selection_reason=planned_item.selection_reason,
                    persona_match_score=Decimal(str(round(planned_item.persona_match_score, 2))),
                    travel_time_from_previous=planned_item.travel_time_from_previous,
                    travel_mode=planned_item.travel_mode,
                )
                item.poi = planned_item.poi
                itinerary_day.items.append(item)

            itinerary.days.append(itinerary_day)

        return itinerary
