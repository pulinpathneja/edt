from fastapi import APIRouter

from app.api.routes import pois, personas, itinerary, recommendations, cities, landmarks, travel, country_itinerary, pipeline, itinerary_planner, query

api_router = APIRouter()

api_router.include_router(cities.router, prefix="/cities", tags=["Cities"])
api_router.include_router(landmarks.router, prefix="/landmarks", tags=["Landmarks"])
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])
api_router.include_router(personas.router, prefix="/personas", tags=["Personas"])
api_router.include_router(itinerary.router, prefix="/itinerary", tags=["Itinerary"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(travel.router, prefix="/travel", tags=["Travel"])
api_router.include_router(country_itinerary.router, prefix="/country-itinerary", tags=["Country Itinerary"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(itinerary_planner.router, prefix="/itinerary-planner", tags=["Itinerary Planner"])
api_router.include_router(query.router, prefix="/query", tags=["Query"])
