"""
Itinerary planner endpoint — returns activities in the exact shape
the React Native frontend (edt-ui/itinerary-planner) expects.
"""
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.sample_itinerary_data import CITY_ACTIVITIES, _build_generic_templates

router = APIRouter()


# ── Request / Response schemas ──────────────────────────────────────

class CityInput(BaseModel):
    name: str
    days: int


class GenerateRequest(BaseModel):
    country: str
    cities: List[CityInput]
    group_type: Optional[str] = None
    vibes: Optional[List[str]] = None
    budget_level: Optional[str] = None
    pacing: Optional[str] = None
    start_date: Optional[date] = None


class TransitInfo(BaseModel):
    mode: str
    duration: str
    note: Optional[str] = None


class ActivityDataOut(BaseModel):
    type: str
    # hotel uses 'name', others use 'title'
    name: Optional[str] = None
    title: Optional[str] = None
    time: str
    description: Optional[str] = None
    image: Optional[str] = None


class ActivityEntryOut(BaseModel):
    id: str
    data: ActivityDataOut
    status: Optional[str] = None
    transit: Optional[TransitInfo] = None
    tips: Optional[List[str]] = None
    checklist: Optional[List[str]] = None
    notes: Optional[str] = None


class DayItineraryOut(BaseModel):
    dayNumber: int
    date: str
    cityName: str
    title: str
    subtitle: Optional[str] = None
    activities: List[ActivityEntryOut]
    heroImage: Optional[str] = None


class GenerateResponse(BaseModel):
    days: List[str]
    day_itineraries: List[DayItineraryOut]


# ── Helpers ─────────────────────────────────────────────────────────

def _to_12h(time_24: str) -> str:
    """Convert '08:00' or '13:30' to '08:00 AM' / '01:30 PM'."""
    try:
        parts = time_24.split(":")
        h, m = int(parts[0]), int(parts[1])
        suffix = "AM" if h < 12 else "PM"
        if h == 0:
            h = 12
        elif h > 12:
            h -= 12
        return f"{h:02d}:{m:02d} {suffix}"
    except Exception:
        return time_24


# ── Image mappings ─────────────────────────────────────────────────

# Specific landmark images (title → URL)
_LANDMARK_IMAGES: dict[str, str] = {
    # Italy
    "Colosseum": "https://plus.unsplash.com/premium_photo-1661938399624-3495425e5027?w=400&h=300&fit=crop&auto=format",
    "Roman Forum & Palatine Hill": "https://plus.unsplash.com/premium_photo-1706464965798-336f113c677a?w=400&h=300&fit=crop&auto=format",
    "Piazza Navona": "https://plus.unsplash.com/premium_photo-1675972401142-a067427b2db5?w=400&h=300&fit=crop&auto=format",
    "Pantheon": "https://plus.unsplash.com/premium_photo-1694475508726-a959bbe226b8?w=400&h=300&fit=crop&auto=format",
    "Trevi Fountain": "https://plus.unsplash.com/premium_photo-1661962551246-49ffac5cff8a?w=400&h=300&fit=crop&auto=format",
    "Spanish Steps": "https://plus.unsplash.com/premium_photo-1676391702953-f6ef6316eb0a?w=400&h=300&fit=crop&auto=format",
    "Vatican Museums & Sistine Chapel": "https://images.unsplash.com/photo-1664214960903-d36374a66226?w=400&h=300&fit=crop&auto=format",
    "St. Peter's Basilica": "https://plus.unsplash.com/premium_photo-1694475430347-2db39ac3849c?w=400&h=300&fit=crop&auto=format",
    "Castel Sant'Angelo": "https://plus.unsplash.com/premium_photo-1764448752949-68ec255fae06?w=400&h=300&fit=crop&auto=format",
    "Trastevere Quarter": "https://plus.unsplash.com/premium_photo-1677619995531-ea6600535b18?w=400&h=300&fit=crop&auto=format",
    "Borghese Gallery": "https://images.unsplash.com/photo-1621410780263-552901f401f4?w=400&h=300&fit=crop&auto=format",
    "Villa Borghese Gardens": "https://plus.unsplash.com/premium_photo-1697730379810-6f3918f7c463?w=400&h=300&fit=crop&auto=format",
    "Cathedral of Santa Maria del Fiore": "https://plus.unsplash.com/premium_photo-1764348950318-4abd0bbd0efe?w=400&h=300&fit=crop&auto=format",
    "Uffizi Gallery": "https://plus.unsplash.com/premium_photo-1720420546717-e153f9ef179f?w=400&h=300&fit=crop&auto=format",
    "Ponte Vecchio": "https://plus.unsplash.com/premium_photo-1678118754486-fcf56fe5f5f6?w=400&h=300&fit=crop&auto=format",
    "Accademia Gallery": "https://images.unsplash.com/photo-1725434760903-05008bbd014e?w=400&h=300&fit=crop&auto=format",
    "Piazzale Michelangelo": "https://images.unsplash.com/photo-1689323768678-8e91ca96238b?w=400&h=300&fit=crop&auto=format",
    "Palazzo Pitti": "https://images.unsplash.com/photo-1588689317310-74e535ca37ef?w=400&h=300&fit=crop&auto=format",
    "Boboli Gardens": "https://plus.unsplash.com/premium_photo-1673141390230-8b4a3c3152b1?w=400&h=300&fit=crop&auto=format",
    "Basilica di Santa Croce": "https://plus.unsplash.com/premium_photo-1678118754991-d88dfd66b1f0?w=400&h=300&fit=crop&auto=format",
    "St. Mark's Basilica": "https://plus.unsplash.com/premium_photo-1677048147446-f4563f556c32?w=400&h=300&fit=crop&auto=format",
    "Doge's Palace": "https://plus.unsplash.com/premium_photo-1664283661769-eaa6feaf58c3?w=400&h=300&fit=crop&auto=format",
    "Rialto Market": "https://plus.unsplash.com/premium_photo-1664299077118-e310ce32096d?w=400&h=300&fit=crop&auto=format",
    "Murano Glass Factories": "https://images.unsplash.com/photo-1727001496055-ba712f0c7f82?w=400&h=300&fit=crop&auto=format",
    "Burano Island": "https://plus.unsplash.com/premium_photo-1677645995963-6052ac6ad06c?w=400&h=300&fit=crop&auto=format",
    "Milan Cathedral (Duomo)": "https://plus.unsplash.com/premium_photo-1715873662328-6c59909a35e3?w=400&h=300&fit=crop&auto=format",
    "Galleria Vittorio Emanuele II": "https://plus.unsplash.com/premium_photo-1715873752801-128e0a517933?w=400&h=300&fit=crop&auto=format",
    "The Last Supper (Santa Maria delle Grazie)": "https://images.unsplash.com/photo-1706797134942-c1d7972aad22?w=400&h=300&fit=crop&auto=format",
    "Navigli Canals": "https://images.unsplash.com/photo-1654869692655-2f5113e6353d?w=400&h=300&fit=crop&auto=format",
    "Pinacoteca di Brera": "https://images.unsplash.com/photo-1654869692655-2f5113e6353d?w=400&h=300&fit=crop&auto=format",
    "Naples Underground (Napoli Sotterranea)": "https://plus.unsplash.com/premium_photo-1697729585336-af43a681cc6a?w=400&h=300&fit=crop&auto=format",
    "Spaccanapoli": "https://images.unsplash.com/photo-1665406902101-1044757c7e2e?w=400&h=300&fit=crop&auto=format",
    "Naples National Archaeological Museum": "https://images.unsplash.com/photo-1665406902101-1044757c7e2e?w=400&h=300&fit=crop&auto=format",
    "Lungomare Seafront": "https://plus.unsplash.com/premium_photo-1697729585336-af43a681cc6a?w=400&h=300&fit=crop&auto=format",
    "Amalfi Cathedral": "https://images.unsplash.com/photo-1647167443660-a08d13ed0054?w=400&h=300&fit=crop&auto=format",
    "Villa Rufolo Gardens, Ravello": "https://plus.unsplash.com/premium_photo-1753979901415-035d50abd132?w=400&h=300&fit=crop&auto=format",
    "Positano Beach": "https://plus.unsplash.com/premium_photo-1722201172124-695e2a731ec4?w=400&h=300&fit=crop&auto=format",
    # France
    "Eiffel Tower": "https://plus.unsplash.com/premium_photo-1661919210043-fd847a58522d?w=400&h=300&fit=crop&auto=format",
    "Musée d'Orsay": "https://plus.unsplash.com/premium_photo-1717422935480-6a66474b88a9?w=400&h=300&fit=crop&auto=format",
    "Louvre Museum": "https://plus.unsplash.com/premium_photo-1696528052470-38fa85d93aa0?w=400&h=300&fit=crop&auto=format",
    "Sacré-Cœur Basilica": "https://plus.unsplash.com/premium_photo-1694475347672-560fa2f92fde?w=400&h=300&fit=crop&auto=format",
    "Montmartre & Place du Tertre": "https://plus.unsplash.com/premium_photo-1718285549233-42414e1c16f9?w=400&h=300&fit=crop&auto=format",
    "Notre-Dame (exterior)": "https://plus.unsplash.com/premium_photo-1719409843702-2cc417bc95fb?w=400&h=300&fit=crop&auto=format",
    "Palace of Versailles": "https://images.unsplash.com/photo-1692025469417-1fdaaf2557a2?w=400&h=300&fit=crop&auto=format",
    "Gardens of Versailles": "https://images.unsplash.com/photo-1692025469417-1fdaaf2557a2?w=400&h=300&fit=crop&auto=format",
    "Champs-Élysées & Arc de Triomphe": "https://plus.unsplash.com/premium_photo-1661916886713-7318e24b3def?w=400&h=300&fit=crop&auto=format",
    "Jardin des Tuileries": "https://plus.unsplash.com/premium_photo-1661916886713-7318e24b3def?w=400&h=300&fit=crop&auto=format",
    "Sainte-Chapelle": "https://plus.unsplash.com/premium_photo-1694475314521-8e02c303a8d6?w=400&h=300&fit=crop&auto=format",
    "Musée de l'Orangerie": "https://plus.unsplash.com/premium_photo-1717422935480-6a66474b88a9?w=400&h=300&fit=crop&auto=format",
    "Le Marais Quarter": "https://plus.unsplash.com/premium_photo-1718285549233-42414e1c16f9?w=400&h=300&fit=crop&auto=format",
    "Canal Saint-Martin": "https://plus.unsplash.com/premium_photo-1718285549233-42414e1c16f9?w=400&h=300&fit=crop&auto=format",
    "Promenade des Anglais": "https://plus.unsplash.com/premium_photo-1661962506417-f6056afac074?w=400&h=300&fit=crop&auto=format",
    "Vieux Nice (Old Town)": "https://images.unsplash.com/photo-1611886931912-fb7ab8b2a013?w=400&h=300&fit=crop&auto=format",
    "Castle Hill (Colline du Château)": "https://images.unsplash.com/photo-1611886931912-fb7ab8b2a013?w=400&h=300&fit=crop&auto=format",
    "Musée Matisse": "https://images.unsplash.com/photo-1611886931912-fb7ab8b2a013?w=400&h=300&fit=crop&auto=format",
    "Plage de Castel": "https://plus.unsplash.com/premium_photo-1661962506417-f6056afac074?w=400&h=300&fit=crop&auto=format",
    "Vieux Lyon & Traboules": "https://plus.unsplash.com/premium_photo-1742493609927-2083543dfebd?w=400&h=300&fit=crop&auto=format",
    "Basilica of Notre-Dame de Fourvière": "https://plus.unsplash.com/premium_photo-1742457723606-2f2906ea2fdf?w=400&h=300&fit=crop&auto=format",
    "Les Halles de Lyon Paul Bocuse": "https://plus.unsplash.com/premium_photo-1742493609927-2083543dfebd?w=400&h=300&fit=crop&auto=format",
    "Miroir d'Eau": "https://images.unsplash.com/photo-1645022581259-a2f88d7432ef?w=400&h=300&fit=crop&auto=format",
    "Cité du Vin": "https://images.unsplash.com/photo-1645022581259-a2f88d7432ef?w=400&h=300&fit=crop&auto=format",
    "Place de la Bourse": "https://images.unsplash.com/photo-1645022581259-a2f88d7432ef?w=400&h=300&fit=crop&auto=format",
    # Spain
    "Sagrada Familia": "https://plus.unsplash.com/premium_photo-1661885514351-ad93dcfb25f3?w=400&h=300&fit=crop&auto=format",
    "Park Güell": "https://plus.unsplash.com/premium_photo-1697730286026-467814876960?w=400&h=300&fit=crop&auto=format",
    "Gothic Quarter (Barri Gòtic)": "https://plus.unsplash.com/premium_photo-1697729414825-18882463d3a1?w=400&h=300&fit=crop&auto=format",
    "La Boqueria Market": "https://images.unsplash.com/photo-1752605158021-6ca2665f6acc?w=400&h=300&fit=crop&auto=format",
    "Barceloneta Beach": "https://images.unsplash.com/photo-1696941586183-84526dd38c29?w=400&h=300&fit=crop&auto=format",
    "Casa Batlló": "https://images.unsplash.com/photo-1593780242729-72b489db4d61?w=400&h=300&fit=crop&auto=format",
    "Casa Milà (La Pedrera)": "https://images.unsplash.com/photo-1593780242729-72b489db4d61?w=400&h=300&fit=crop&auto=format",
    "Montjuïc Castle & Gardens": "https://plus.unsplash.com/premium_photo-1697730076411-2b4602bf494f?w=400&h=300&fit=crop&auto=format",
    "Magic Fountain of Montjuïc": "https://plus.unsplash.com/premium_photo-1697730076411-2b4602bf494f?w=400&h=300&fit=crop&auto=format",
    "La Rambla": "https://plus.unsplash.com/premium_photo-1697729414825-18882463d3a1?w=400&h=300&fit=crop&auto=format",
    "Picasso Museum": "https://plus.unsplash.com/premium_photo-1697729414825-18882463d3a1?w=400&h=300&fit=crop&auto=format",
    "El Born Cultural Center": "https://plus.unsplash.com/premium_photo-1697729414825-18882463d3a1?w=400&h=300&fit=crop&auto=format",
    "Museo del Prado": "https://plus.unsplash.com/premium_photo-1697730402697-51e3757346d7?w=400&h=300&fit=crop&auto=format",
    "Retiro Park": "https://images.unsplash.com/photo-1576093536437-d9d60edb9b47?w=400&h=300&fit=crop&auto=format",
    "Royal Palace of Madrid": "https://plus.unsplash.com/premium_photo-1694475328725-64b77c08b4b9?w=400&h=300&fit=crop&auto=format",
    "Plaza Mayor": "https://plus.unsplash.com/premium_photo-1697729614354-16b191fb0861?w=400&h=300&fit=crop&auto=format",
    "Reina Sofía Museum": "https://plus.unsplash.com/premium_photo-1697730402697-51e3757346d7?w=400&h=300&fit=crop&auto=format",
    "Real Alcázar": "https://plus.unsplash.com/premium_photo-1697730300238-9f624454c3dd?w=400&h=300&fit=crop&auto=format",
    "Seville Cathedral & Giralda Tower": "https://plus.unsplash.com/premium_photo-1694475145659-3a6c1d825941?w=400&h=300&fit=crop&auto=format",
    "Plaza de España": "https://plus.unsplash.com/premium_photo-1694475224827-bbfced873eb8?w=400&h=300&fit=crop&auto=format",
    "Alhambra & Nasrid Palaces": "https://images.unsplash.com/photo-1528865972207-b47dfe0cac29?w=400&h=300&fit=crop&auto=format",
    "Generalife Gardens": "https://images.unsplash.com/photo-1528865972207-b47dfe0cac29?w=400&h=300&fit=crop&auto=format",
    "Albaicín Quarter": "https://images.unsplash.com/photo-1764268177381-ecc145c13787?w=400&h=300&fit=crop&auto=format",
    "Mirador de San Nicolás": "https://images.unsplash.com/photo-1764268177381-ecc145c13787?w=400&h=300&fit=crop&auto=format",
    # Japan
    "Meiji Shrine": "https://plus.unsplash.com/premium_photo-1664303893708-dfc70b56e9b0?w=400&h=300&fit=crop&auto=format",
    "Harajuku & Takeshita Street": "https://images.unsplash.com/photo-1664806462678-5df01513f7b9?w=400&h=300&fit=crop&auto=format",
    "Shibuya Crossing": "https://plus.unsplash.com/premium_photo-1715783495625-1da3a04fd8f6?w=400&h=300&fit=crop&auto=format",
    "Senso-ji Temple": "https://images.unsplash.com/photo-1667314432098-6fd47117aa7f?w=400&h=300&fit=crop&auto=format",
    "Sumida River Walk & Tokyo Skytree": "https://plus.unsplash.com/premium_photo-1722795256346-446f8f846b9e?w=400&h=300&fit=crop&auto=format",
    "Akihabara Electric Town": "https://plus.unsplash.com/premium_photo-1723983556109-7415d601c377?w=400&h=300&fit=crop&auto=format",
    "Shinjuku Gyoen National Garden": "https://plus.unsplash.com/premium_photo-1726579710883-7040d0e6d379?w=400&h=300&fit=crop&auto=format",
    "Tokyo Metropolitan Government Building": "https://plus.unsplash.com/premium_photo-1726579710883-7040d0e6d379?w=400&h=300&fit=crop&auto=format",
    "Tokyo Tower": "https://plus.unsplash.com/premium_photo-1697730244459-aafec2c71f64?w=400&h=300&fit=crop&auto=format",
    "teamLab Borderless": "https://images.unsplash.com/photo-1703437874711-d6d3de1e0013?w=400&h=300&fit=crop&auto=format",
    "Golden Gai, Shinjuku": "https://images.unsplash.com/photo-1676763118176-3ff8ffa7ddd4?w=400&h=300&fit=crop&auto=format",
    "Shimokitazawa": "https://images.unsplash.com/photo-1676763118176-3ff8ffa7ddd4?w=400&h=300&fit=crop&auto=format",
    "Fushimi Inari Shrine": "https://images.unsplash.com/photo-1693378173709-2197ce8c5af3?w=400&h=300&fit=crop&auto=format",
    "Arashiyama Bamboo Grove": "https://plus.unsplash.com/premium_photo-1749723953974-846df8821d16?w=400&h=300&fit=crop&auto=format",
    "Kinkaku-ji (Golden Pavilion)": "https://images.unsplash.com/photo-1676829940012-4d61ecd20e57?w=400&h=300&fit=crop&auto=format",
    "Nishiki Market": "https://plus.unsplash.com/premium_photo-1686538381765-da778cf88d9b?w=400&h=300&fit=crop&auto=format",
    "Philosopher's Path": "https://plus.unsplash.com/premium_photo-1749741021674-251461cada5a?w=400&h=300&fit=crop&auto=format",
    "Ginkaku-ji (Silver Pavilion)": "https://images.unsplash.com/photo-1712374949744-dcce9c289182?w=400&h=300&fit=crop&auto=format",
    "Nanzen-ji Temple": "https://images.unsplash.com/photo-1712374949744-dcce9c289182?w=400&h=300&fit=crop&auto=format",
    "Gion District & Geisha Spotting": "https://images.unsplash.com/photo-1597730763269-c49ab9f9db0f?w=400&h=300&fit=crop&auto=format",
    "Tea Ceremony Experience": "https://images.unsplash.com/photo-1597730763269-c49ab9f9db0f?w=400&h=300&fit=crop&auto=format",
    "Kiyomizu-dera Temple": "https://plus.unsplash.com/premium_photo-1673285286254-d0d0e465e0fd?w=400&h=300&fit=crop&auto=format",
    "Higashiyama Historic District": "https://plus.unsplash.com/premium_photo-1722593856044-e5176ca19a5f?w=400&h=300&fit=crop&auto=format",
    "Fushimi Sake District": "https://images.unsplash.com/photo-1693378173709-2197ce8c5af3?w=400&h=300&fit=crop&auto=format",
    "Osaka Castle": "https://plus.unsplash.com/premium_photo-1723983555971-8dafb9ae7265?w=400&h=300&fit=crop&auto=format",
    "Dotonbori": "https://plus.unsplash.com/premium_photo-1724593825200-39731dcdacf8?w=400&h=300&fit=crop&auto=format",
    "Shinsekai District": "https://plus.unsplash.com/premium_photo-1733342484519-556235e2fee7?w=400&h=300&fit=crop&auto=format",
    "Shinsaibashi Shopping Arcade": "https://plus.unsplash.com/premium_photo-1724593825200-39731dcdacf8?w=400&h=300&fit=crop&auto=format",
    "Hiroshima Peace Memorial Park": "https://images.unsplash.com/photo-1658167865945-7e9949fa4d69?w=400&h=300&fit=crop&auto=format",
    "Itsukushima Shrine & Floating Torii": "https://images.unsplash.com/photo-1620118933179-c9ba62e50c7c?w=400&h=300&fit=crop&auto=format",
    "Mt. Misen Ropeway": "https://images.unsplash.com/photo-1620118933179-c9ba62e50c7c?w=400&h=300&fit=crop&auto=format",
    "Ueno Park & Tokyo National Museum": "https://plus.unsplash.com/premium_photo-1726579710883-7040d0e6d379?w=400&h=300&fit=crop&auto=format",
    "Sumiyoshi Taisha": "https://plus.unsplash.com/premium_photo-1664303893708-dfc70b56e9b0?w=400&h=300&fit=crop&auto=format",
    "Tennoji & Abeno Harukas": "https://plus.unsplash.com/premium_photo-1723983555971-8dafb9ae7265?w=400&h=300&fit=crop&auto=format",
    # UK
    "Tower of London": "https://plus.unsplash.com/premium_photo-1680806491784-6d3d0d406562?w=400&h=300&fit=crop&auto=format",
    "Tower Bridge": "https://plus.unsplash.com/premium_photo-1661962726504-fa8f464a1bb8?w=400&h=300&fit=crop&auto=format",
    "Westminster Abbey": "https://plus.unsplash.com/premium_photo-1677656223956-b883f497d6f8?w=400&h=300&fit=crop&auto=format",
    "Big Ben & Houses of Parliament": "https://plus.unsplash.com/premium_photo-1672316288974-0c103e0c7a1e?w=400&h=300&fit=crop&auto=format",
    "London Eye": "https://plus.unsplash.com/premium_photo-1694475331421-40cf7f468690?w=400&h=300&fit=crop&auto=format",
    "British Museum": "https://plus.unsplash.com/premium_photo-1694475282880-4d02465afa55?w=400&h=300&fit=crop&auto=format",
    "Notting Hill & Portobello Road Market": "https://images.unsplash.com/photo-1685916096033-263dc3c8f4c2?w=400&h=300&fit=crop&auto=format",
    "Natural History Museum": "https://plus.unsplash.com/premium_photo-1667238837740-790e3ff6fe82?w=400&h=300&fit=crop&auto=format",
    "V&A Museum": "https://plus.unsplash.com/premium_photo-1667238837740-790e3ff6fe82?w=400&h=300&fit=crop&auto=format",
    "Camden Market": "https://images.unsplash.com/photo-1590497236370-a2136c967df2?w=400&h=300&fit=crop&auto=format",
    "Tate Modern": "https://plus.unsplash.com/premium_photo-1681425910045-5e7649d43cdd?w=400&h=300&fit=crop&auto=format",
    "Covent Garden": "https://images.unsplash.com/photo-1685916096033-263dc3c8f4c2?w=400&h=300&fit=crop&auto=format",
    "Hyde Park & Kensington Gardens": "https://plus.unsplash.com/premium_photo-1667238837740-790e3ff6fe82?w=400&h=300&fit=crop&auto=format",
    "Millennium Bridge & St Paul's Cathedral": "https://plus.unsplash.com/premium_photo-1681425910045-5e7649d43cdd?w=400&h=300&fit=crop&auto=format",
    "Greenwich & Cutty Sark": "https://plus.unsplash.com/premium_photo-1681425910045-5e7649d43cdd?w=400&h=300&fit=crop&auto=format",
    "Edinburgh Castle": "https://plus.unsplash.com/premium_photo-1732739049130-41cab10c7f75?w=400&h=300&fit=crop&auto=format",
    "Royal Mile": "https://plus.unsplash.com/premium_photo-1732481077925-83cddca9aa38?w=400&h=300&fit=crop&auto=format",
    "Holyrood Palace": "https://plus.unsplash.com/premium_photo-1732481077925-83cddca9aa38?w=400&h=300&fit=crop&auto=format",
    "Arthur's Seat": "https://plus.unsplash.com/premium_photo-1732481077925-83cddca9aa38?w=400&h=300&fit=crop&auto=format",
    "Scottish National Gallery": "https://plus.unsplash.com/premium_photo-1732739049130-41cab10c7f75?w=400&h=300&fit=crop&auto=format",
    "Calton Hill": "https://plus.unsplash.com/premium_photo-1732740526483-53f7016aac50?w=400&h=300&fit=crop&auto=format",
    "Royal Yacht Britannia": "https://images.unsplash.com/photo-1704632992940-6caf40070ddc?w=400&h=300&fit=crop&auto=format",
    "Scotch Whisky Experience": "https://plus.unsplash.com/premium_photo-1732739049130-41cab10c7f75?w=400&h=300&fit=crop&auto=format",
    "Dean Village": "https://plus.unsplash.com/premium_photo-1732481077925-83cddca9aa38?w=400&h=300&fit=crop&auto=format",
    "Greyfriars Kirkyard": "https://plus.unsplash.com/premium_photo-1732481077925-83cddca9aa38?w=400&h=300&fit=crop&auto=format",
    "Roman Baths": "https://images.unsplash.com/photo-1555084157-8424e8a945de?w=400&h=300&fit=crop&auto=format",
    "Bath Abbey": "https://images.unsplash.com/photo-1555084157-8424e8a945de?w=400&h=300&fit=crop&auto=format",
    "Royal Crescent & The Circus": "https://images.unsplash.com/photo-1615560468572-fcf50d0806c1?w=400&h=300&fit=crop&auto=format",
    "Pulteney Bridge & Weir": "https://images.unsplash.com/photo-1615560468572-fcf50d0806c1?w=400&h=300&fit=crop&auto=format",
    "Thermae Bath Spa": "https://images.unsplash.com/photo-1555084157-8424e8a945de?w=400&h=300&fit=crop&auto=format",
    "Bodleian Library": "https://plus.unsplash.com/premium_photo-1698084059435-a50ddfd69303?w=400&h=300&fit=crop&auto=format",
    "Radcliffe Camera": "https://plus.unsplash.com/premium_photo-1698084059435-a50ddfd69303?w=400&h=300&fit=crop&auto=format",
    "Christ Church College": "https://plus.unsplash.com/premium_photo-1661953304549-9a308ce47cff?w=400&h=300&fit=crop&auto=format",
    "Ashmolean Museum": "https://plus.unsplash.com/premium_photo-1698084059435-a50ddfd69303?w=400&h=300&fit=crop&auto=format",
    "Dorsoduro & Peggy Guggenheim Collection": "https://plus.unsplash.com/premium_photo-1664283661769-eaa6feaf58c3?w=400&h=300&fit=crop&auto=format",
    "Piazza della Signoria": "https://plus.unsplash.com/premium_photo-1720420546717-e153f9ef179f?w=400&h=300&fit=crop&auto=format",
    "Oltrarno & Santo Spirito": "https://plus.unsplash.com/premium_photo-1678118754486-fcf56fe5f5f6?w=400&h=300&fit=crop&auto=format",
    "Namba Parks": "https://plus.unsplash.com/premium_photo-1724593825200-39731dcdacf8?w=400&h=300&fit=crop&auto=format",
    "Mercado de San Miguel": "https://plus.unsplash.com/premium_photo-1697729614354-16b191fb0861?w=400&h=300&fit=crop&auto=format",
    "Barrio de las Letras": "https://plus.unsplash.com/premium_photo-1697729614354-16b191fb0861?w=400&h=300&fit=crop&auto=format",
    "Gran Vía": "https://plus.unsplash.com/premium_photo-1697729614354-16b191fb0861?w=400&h=300&fit=crop&auto=format",
    "Malasaña & Plaza del Dos de Mayo": "https://plus.unsplash.com/premium_photo-1697729614354-16b191fb0861?w=400&h=300&fit=crop&auto=format",
    "Triana Quarter": "https://plus.unsplash.com/premium_photo-1694475224827-bbfced873eb8?w=400&h=300&fit=crop&auto=format",
    "Cimiez Monastery & Gardens": "https://images.unsplash.com/photo-1611886931912-fb7ab8b2a013?w=400&h=300&fit=crop&auto=format",
    "Rue Sainte-Catherine": "https://images.unsplash.com/photo-1645022581259-a2f88d7432ef?w=400&h=300&fit=crop&auto=format",
}

# Fallback images per activity type (rotate based on index)
_TYPE_IMAGES: dict[str, list[str]] = {
    "hotel": [
        "https://plus.unsplash.com/premium_photo-1661963239507-7bdf41a5e66b?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1661881436846-5a0f53025711?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1670360414882-4d4e261afb53?w=400&h=300&fit=crop&auto=format",
    ],
    "meal": [
        "https://plus.unsplash.com/premium_photo-1723478415102-952f63daf8c7?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1770559269035-b231d88090bf?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1687089577054-d5ea57d4ceeb?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1683121624323-0c5bf3ca6af2?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1671559021810-10b44c835652?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1694383419236-924d94a770df?w=400&h=300&fit=crop&auto=format",
        "https://images.unsplash.com/photo-1695910016906-99a1ae19802f?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1763758818746-a4d35a6679f3?w=400&h=300&fit=crop&auto=format",
    ],
    "transport": [
        "https://plus.unsplash.com/premium_photo-1683319786262-ceae1f8c70d6?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1677440437280-b410ab3ad976?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1726783211541-51f6069dc95a?w=400&h=300&fit=crop&auto=format",
    ],
    "shopping": [
        "https://plus.unsplash.com/premium_photo-1661299291077-e0a8a8d6d5e1?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1683140737936-7a4ae1e6b5a6?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1714347051060-f3a5bd84f7ea?w=400&h=300&fit=crop&auto=format",
    ],
    "sightseeing": [
        "https://plus.unsplash.com/premium_photo-1722201172124-695e2a731ec4?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1679690708509-a2c29b5726a4?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1694475105437-5e97dcc7e520?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1680667682187-52fd5e203efb?w=400&h=300&fit=crop&auto=format",
        "https://plus.unsplash.com/premium_photo-1693256457845-0585380de3c9?w=400&h=300&fit=crop&auto=format",
    ],
}

# City hero images (for DayHeader)
_CITY_HERO_IMAGES: dict[str, str] = {
    "rome": "https://plus.unsplash.com/premium_photo-1661938399624-3495425e5027?w=800&h=400&fit=crop&auto=format",
    "florence": "https://plus.unsplash.com/premium_photo-1764348950318-4abd0bbd0efe?w=800&h=400&fit=crop&auto=format",
    "venice": "https://plus.unsplash.com/premium_photo-1677048147446-f4563f556c32?w=800&h=400&fit=crop&auto=format",
    "milan": "https://plus.unsplash.com/premium_photo-1715873662328-6c59909a35e3?w=800&h=400&fit=crop&auto=format",
    "naples": "https://plus.unsplash.com/premium_photo-1697729585336-af43a681cc6a?w=800&h=400&fit=crop&auto=format",
    "amalfi": "https://plus.unsplash.com/premium_photo-1722201172124-695e2a731ec4?w=800&h=400&fit=crop&auto=format",
    "paris": "https://plus.unsplash.com/premium_photo-1661919210043-fd847a58522d?w=800&h=400&fit=crop&auto=format",
    "nice": "https://plus.unsplash.com/premium_photo-1661962506417-f6056afac074?w=800&h=400&fit=crop&auto=format",
    "lyon": "https://plus.unsplash.com/premium_photo-1742493609927-2083543dfebd?w=800&h=400&fit=crop&auto=format",
    "bordeaux": "https://images.unsplash.com/photo-1645022581259-a2f88d7432ef?w=800&h=400&fit=crop&auto=format",
    "barcelona": "https://plus.unsplash.com/premium_photo-1661885514351-ad93dcfb25f3?w=800&h=400&fit=crop&auto=format",
    "madrid": "https://plus.unsplash.com/premium_photo-1694475328725-64b77c08b4b9?w=800&h=400&fit=crop&auto=format",
    "seville": "https://plus.unsplash.com/premium_photo-1694475224827-bbfced873eb8?w=800&h=400&fit=crop&auto=format",
    "granada": "https://images.unsplash.com/photo-1528865972207-b47dfe0cac29?w=800&h=400&fit=crop&auto=format",
    "tokyo": "https://plus.unsplash.com/premium_photo-1715783495625-1da3a04fd8f6?w=800&h=400&fit=crop&auto=format",
    "kyoto": "https://images.unsplash.com/photo-1693378173709-2197ce8c5af3?w=800&h=400&fit=crop&auto=format",
    "osaka": "https://plus.unsplash.com/premium_photo-1724593825200-39731dcdacf8?w=800&h=400&fit=crop&auto=format",
    "hiroshima": "https://images.unsplash.com/photo-1658167865945-7e9949fa4d69?w=800&h=400&fit=crop&auto=format",
    "london": "https://plus.unsplash.com/premium_photo-1661962726504-fa8f464a1bb8?w=800&h=400&fit=crop&auto=format",
    "edinburgh": "https://plus.unsplash.com/premium_photo-1732739049130-41cab10c7f75?w=800&h=400&fit=crop&auto=format",
    "bath": "https://images.unsplash.com/photo-1555084157-8424e8a945de?w=800&h=400&fit=crop&auto=format",
    "oxford": "https://plus.unsplash.com/premium_photo-1698084059435-a50ddfd69303?w=800&h=400&fit=crop&auto=format",
}


def _get_activity_image(title: str, act_type: str, index: int) -> str:
    """Get an image URL for an activity — specific landmark or type-based fallback."""
    if title in _LANDMARK_IMAGES:
        return _LANDMARK_IMAGES[title]
    pool = _TYPE_IMAGES.get(act_type, _TYPE_IMAGES["sightseeing"])
    return pool[index % len(pool)]


_TIPS = {
    "hotel": [
        "Confirm check-in time in advance",
        "Ask about luggage storage if arriving early",
    ],
    "meal": [
        "Reservations recommended for dinner",
        "Ask staff for local specialties",
    ],
    "sightseeing": [
        "Arrive early to avoid crowds",
        "Check opening hours before visiting",
    ],
    "transport": [
        "Buy tickets in advance when possible",
        "Keep a screenshot of your booking offline",
    ],
    "shopping": [
        "Compare prices before buying",
        "Ask about tax-free shopping for tourists",
    ],
}

_CHECKLISTS = {
    "hotel": ["Confirm reservation", "Pack essentials in day bag"],
    "meal": ["Check dietary options", "Bring cash for small venues"],
    "sightseeing": ["Charge phone for photos", "Wear comfortable shoes"],
    "transport": ["Have tickets ready", "Arrive 10 min early"],
    "shopping": ["Set a budget", "Bring a reusable bag"],
}


def _build_activity_entry(
    city_id: str, day_idx: int, act_idx: int, act: dict
) -> ActivityEntryOut:
    """Transform a raw activity dict into the frontend-shaped ActivityEntryOut."""
    act_type = act["type"]
    time_12 = _to_12h(act["time"])
    title = act["title"]

    data: dict = {"type": act_type, "time": time_12}
    if act_type == "hotel":
        data["name"] = title
    else:
        data["title"] = title

    if "description" in act:
        data["description"] = act["description"]

    data["image"] = _get_activity_image(title, act_type, act_idx)

    entry: dict = {
        "id": f"{city_id}-d{day_idx + 1}-{act_idx}",
        "data": ActivityDataOut(**data),
        "status": "upcoming",
    }

    if "transit" in act:
        t = act["transit"]
        entry["transit"] = TransitInfo(
            mode=t["mode"], duration=t["duration"], note=t.get("note")
        )

    entry["tips"] = _TIPS.get(act_type, [])
    entry["checklist"] = _CHECKLISTS.get(act_type, [])

    if act_type == "hotel":
        entry["notes"] = f"Your accommodation in the city. {act.get('description', '')}"
    elif "description" in act:
        entry["notes"] = act["description"]

    return ActivityEntryOut(**entry)


# ── Endpoint ────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateResponse)
async def generate_itinerary(request: GenerateRequest):
    """
    Generate a full itinerary shaped for the React Native frontend.

    Accepts city names + day counts, returns ActivityEntry[] per day
    with 12-hour times, tips, checklists, and notes.
    """
    start = request.start_date or date.today()
    all_days: list[str] = []
    all_day_itineraries: list[DayItineraryOut] = []
    global_day = 0

    for city_input in request.cities:
        city_name = city_input.name
        city_id = city_name.lower().replace(" ", "_")
        num_days = city_input.days

        templates = CITY_ACTIVITIES.get(city_id, [])
        if not templates:
            templates = _build_generic_templates(city_name, num_days)

        for d in range(num_days):
            current_date = start + timedelta(days=global_day)
            template = templates[d % len(templates)]

            # Format date label like "14 Mar"
            day_label = current_date.strftime("%-d %b")
            all_days.append(day_label)

            activities: list[ActivityEntryOut] = []
            for idx, act in enumerate(template["activities"]):
                entry = _build_activity_entry(city_id, global_day, idx, act)
                activities.append(entry)

            # Mark first activity of first day as 'current'
            if global_day == 0 and activities:
                activities[0].status = "current"

            all_day_itineraries.append(DayItineraryOut(
                dayNumber=global_day + 1,
                date=current_date.isoformat(),
                cityName=city_name,
                title=template["title"],
                subtitle=request.country.title(),
                activities=activities,
                heroImage=_CITY_HERO_IMAGES.get(city_id),
            ))
            global_day += 1

    return GenerateResponse(days=all_days, day_itineraries=all_day_itineraries)
