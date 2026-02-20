"""
Sample itinerary data for demo purposes.
Returns realistic day-by-day activities for supported cities.
"""
from datetime import date, timedelta
from typing import List, Optional

# Each city has a list of day templates. Each template has activities for one day.
# Activities follow the shape expected by the React Native frontend:
#   { id, data: { type, title, time, description }, status, transit? }

CITY_ACTIVITIES = {
    # ==================== ITALY ====================
    "rome": [
        {
            "title": "Ancient Rome & the Colosseum",
            "activities": [
                {"type": "hotel", "title": "Hotel Artemide", "time": "08:00", "description": "Boutique hotel on Via Nazionale"},
                {"type": "meal", "title": "Antico Caffe Greco", "time": "08:30", "description": "Historic cafe since 1760 — cappuccino & cornetto", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Colosseum", "time": "10:00", "description": "Iconic Roman amphitheater, skip-the-line entry", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Roman Forum & Palatine Hill", "time": "12:00", "description": "Ruins of ancient Rome's political center", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Trattoria Luzzi", "time": "13:30", "description": "Classic Roman pasta — cacio e pepe, amatriciana", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Piazza Navona", "time": "15:30", "description": "Baroque masterpiece with Bernini's Fountain of the Four Rivers", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Pantheon", "time": "17:00", "description": "Best-preserved ancient Roman building, free entry", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Roscioli", "time": "19:30", "description": "Wine bar & restaurant — Roman-Jewish cuisine", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
        {
            "title": "Vatican City & Trastevere",
            "activities": [
                {"type": "hotel", "title": "Hotel Artemide", "time": "07:30", "description": "Early start for the Vatican"},
                {"type": "meal", "title": "Bar del Fico", "time": "08:00", "description": "Quick espresso & pastry before the museums", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Vatican Museums & Sistine Chapel", "time": "09:00", "description": "Michelangelo's ceiling — book 8 AM entry to beat crowds", "transit": {"mode": "bus", "duration": "20 min"}},
                {"type": "sightseeing", "title": "St. Peter's Basilica", "time": "11:30", "description": "Climb the dome for panoramic views of Rome", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Pizzeria La Montecarlo", "time": "13:00", "description": "Thin-crust Roman pizza near the Vatican", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Castel Sant'Angelo", "time": "14:30", "description": "Hadrian's mausoleum with rooftop terrace views", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Trastevere Quarter", "time": "16:30", "description": "Cobblestone streets, street art, and local life", "transit": {"mode": "walk", "duration": "20 min"}},
                {"type": "meal", "title": "Da Enzo al 29", "time": "19:30", "description": "Legendary Trastevere trattoria — carbonara to die for", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
        {
            "title": "Borghese, Fountains & Spanish Steps",
            "activities": [
                {"type": "hotel", "title": "Hotel Artemide", "time": "08:00"},
                {"type": "meal", "title": "Pasticceria Regoli", "time": "08:30", "description": "Famous maritozzo cream buns", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Borghese Gallery", "time": "10:00", "description": "Bernini & Caravaggio masterpieces — reservation required", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Villa Borghese Gardens", "time": "12:00", "description": "Stroll through Rome's central park, rent a rowboat", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "Il Chianti", "time": "13:00", "description": "Tuscan-Roman cuisine in a cozy setting", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Trevi Fountain", "time": "15:00", "description": "Toss a coin — visit in the afternoon for fewer crowds", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Spanish Steps", "time": "16:30", "description": "Iconic stairway connecting Piazza di Spagna to Trinita dei Monti", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "meal", "title": "Armando al Pantheon", "time": "19:30", "description": "Family-run gem — traditional Roman dishes since 1961", "transit": {"mode": "walk", "duration": "15 min"}},
            ],
        },
    ],
    "florence": [
        {
            "title": "Duomo, Uffizi & Renaissance Heart",
            "activities": [
                {"type": "hotel", "title": "Hotel Lungarno", "time": "08:00", "description": "Arno riverfront boutique hotel"},
                {"type": "meal", "title": "Ditta Artigianale", "time": "08:30", "description": "Specialty coffee & pastries in a hip setting", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Cathedral of Santa Maria del Fiore", "time": "10:00", "description": "Brunelleschi's dome — climb 463 steps for city views", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Uffizi Gallery", "time": "12:00", "description": "Botticelli's Birth of Venus & Primavera", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "meal", "title": "Trattoria Mario", "time": "13:30", "description": "Shared tables, hearty Tuscan lunch since 1953", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Ponte Vecchio", "time": "15:30", "description": "Medieval bridge lined with gold and jewelry shops", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "shopping", "title": "San Lorenzo Leather Market", "time": "17:00", "description": "Haggle for handmade leather goods", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Il Latini", "time": "19:30", "description": "Bustling Florentine steakhouse — bistecca alla fiorentina", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
        {
            "title": "Accademia, Oltrarno & Tuscan Flavors",
            "activities": [
                {"type": "hotel", "title": "Hotel Lungarno", "time": "08:00"},
                {"type": "meal", "title": "Caffe Rivoire", "time": "08:30", "description": "Hot chocolate & pastries in Piazza della Signoria", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Accademia Gallery", "time": "09:30", "description": "Michelangelo's David — book early slot", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Piazza della Signoria", "time": "11:30", "description": "Open-air sculpture gallery with Palazzo Vecchio", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "All'Antico Vinaio", "time": "12:30", "description": "World-famous schiacciata sandwiches — expect a line", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Oltrarno & Santo Spirito", "time": "14:30", "description": "Artisan workshops, quieter piazzas, bohemian charm", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Piazzale Michelangelo", "time": "17:00", "description": "Panoramic viewpoint — best sunset in Florence", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "meal", "title": "Buca Mario", "time": "19:30", "description": "Underground cellar restaurant — Tuscan classics since 1886", "transit": {"mode": "bus", "duration": "15 min"}},
            ],
        },
        {
            "title": "Boboli Gardens & Artisan Florence",
            "activities": [
                {"type": "hotel", "title": "Hotel Lungarno", "time": "08:00"},
                {"type": "meal", "title": "S.Forno", "time": "08:30", "description": "Artisan bakery in Oltrarno", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Palazzo Pitti", "time": "10:00", "description": "Grand Medici palace with world-class art collection", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Boboli Gardens", "time": "12:00", "description": "Renaissance gardens with grottoes and fountains", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Mercato Centrale", "time": "13:30", "description": "Upstairs food hall — lampredotto, truffle pasta, gelato", "transit": {"mode": "bus", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Basilica di Santa Croce", "time": "15:30", "description": "Tombs of Michelangelo, Galileo & Machiavelli", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "meal", "title": "Osteria dell'Enoteca", "time": "19:00", "description": "Wine-paired Tuscan dinner", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
    ],
    "venice": [
        {
            "title": "Grand Canal, St. Mark's & Rialto",
            "activities": [
                {"type": "hotel", "title": "Hotel Danieli", "time": "08:00", "description": "Historic hotel near St. Mark's Square"},
                {"type": "meal", "title": "Pasticceria Tonolo", "time": "08:30", "description": "Legendary Venetian pastry shop", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "transport", "title": "Vaporetto Grand Canal", "time": "09:30", "description": "Water bus ride along the Grand Canal — line 1 for the full experience", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "St. Mark's Basilica", "time": "10:30", "description": "Byzantine mosaics and golden altarpiece", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Doge's Palace", "time": "12:00", "description": "Gothic masterpiece — cross the Bridge of Sighs", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Osteria Bancogiro", "time": "13:30", "description": "Cicchetti and prosecco by the Rialto Bridge", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Rialto Market", "time": "15:00", "description": "Fresh seafood market operating since the 11th century", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "Antiche Carampane", "time": "19:30", "description": "Hidden gem for authentic Venetian seafood", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
        {
            "title": "Murano, Burano & Venetian Islands",
            "activities": [
                {"type": "hotel", "title": "Hotel Danieli", "time": "08:00"},
                {"type": "meal", "title": "Rosa Salva", "time": "08:15", "description": "Quick cornetto & caffe before the ferry", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "transport", "title": "Vaporetto to Murano", "time": "09:00", "description": "Ferry ride to the glass-making island", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Murano Glass Factories", "time": "10:00", "description": "Watch master glassblowers create works of art"},
                {"type": "transport", "title": "Ferry to Burano", "time": "11:30", "description": "30-minute ferry to the colorful fishing village", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Burano Island", "time": "12:15", "description": "Rainbow-colored houses and lace-making tradition"},
                {"type": "meal", "title": "Trattoria da Romano", "time": "13:00", "description": "Famous for risotto de go (goby fish risotto)", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "sightseeing", "title": "Dorsoduro & Peggy Guggenheim Collection", "time": "15:30", "description": "Modern art in a Grand Canal palazzo", "transit": {"mode": "walk", "duration": "10 min", "note": "Ferry back to Venice main island"}},
                {"type": "meal", "title": "Al Covo", "time": "19:30", "description": "Refined Venetian cuisine with lagoon views", "transit": {"mode": "walk", "duration": "15 min"}},
            ],
        },
    ],
    "milan": [
        {
            "title": "Duomo, Last Supper & Fashion District",
            "activities": [
                {"type": "hotel", "title": "Rosa Grand Milano", "time": "08:00", "description": "Central hotel steps from the Duomo"},
                {"type": "meal", "title": "Pavé", "time": "08:30", "description": "Artisan bakery & specialty coffee", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Milan Cathedral (Duomo)", "time": "10:00", "description": "Gothic marvel — rooftop terraces with Alps views", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Galleria Vittorio Emanuele II", "time": "11:30", "description": "Stunning 19th-century shopping arcade", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Luini Panzerotti", "time": "12:30", "description": "Legendary fried calzones — cash only, expect a queue", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "sightseeing", "title": "The Last Supper (Santa Maria delle Grazie)", "time": "14:00", "description": "Leonardo da Vinci's masterpiece — timed 15-min slots", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "shopping", "title": "Quadrilatero della Moda", "time": "16:00", "description": "Fashion district — Via Montenapoleone & Via della Spiga", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Ratanà", "time": "19:30", "description": "Modern Milanese cuisine in a converted railway station", "transit": {"mode": "walk", "duration": "15 min"}},
            ],
        },
        {
            "title": "Navigli, Brera & Milanese Culture",
            "activities": [
                {"type": "hotel", "title": "Rosa Grand Milano", "time": "08:00"},
                {"type": "meal", "title": "Princi", "time": "08:30", "description": "Milanese bakery chain — freshly baked focaccia", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Pinacoteca di Brera", "time": "10:00", "description": "Milan's finest art gallery — Raphael, Caravaggio", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Brera District", "time": "12:00", "description": "Bohemian neighborhood with galleries and boutiques", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Pescaria", "time": "13:00", "description": "Seafood street food in trendy Brera", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Navigli Canals", "time": "15:00", "description": "Milan's canal district — galleries, vintage shops, aperitivo bars", "transit": {"mode": "train", "duration": "12 min"}},
                {"type": "meal", "title": "Langosteria", "time": "19:30", "description": "Upscale seafood with canal views", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
    ],
    "naples": [
        {
            "title": "Historic Naples & Underground City",
            "activities": [
                {"type": "hotel", "title": "Grand Hotel Vesuvio", "time": "08:00", "description": "Seafront luxury on Via Partenope"},
                {"type": "meal", "title": "Gran Caffe Gambrinus", "time": "08:30", "description": "Naples' most famous cafe — sfogliatella & espresso", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Naples Underground (Napoli Sotterranea)", "time": "10:00", "description": "Ancient Greek-Roman tunnels 40m below the city", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Spaccanapoli", "time": "12:00", "description": "The straight street that splits old Naples in half", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "L'Antica Pizzeria da Michele", "time": "12:30", "description": "The birthplace of Neapolitan pizza — only margherita & marinara", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Naples National Archaeological Museum", "time": "14:30", "description": "Pompeii artifacts & Farnese collection", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Lungomare Seafront", "time": "17:00", "description": "Sunset walk along the bay with Vesuvius views", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "meal", "title": "Tandem Ragù", "time": "19:30", "description": "Slow-cooked Neapolitan ragù — a local institution", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
    ],
    "amalfi": [
        {
            "title": "Amalfi Coast Drive & Ravello",
            "activities": [
                {"type": "hotel", "title": "Hotel Santa Caterina", "time": "08:00", "description": "Cliffside hotel overlooking the Mediterranean"},
                {"type": "meal", "title": "Bar Francese", "time": "08:30", "description": "Lemon pastries on the piazza", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Amalfi Cathedral", "time": "09:30", "description": "9th-century cathedral with Arab-Norman architecture", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "transport", "title": "Coastal Drive to Ravello", "time": "10:30", "description": "Scenic 30-minute drive up the cliffside road", "transit": {"mode": "car", "duration": "30 min"}},
                {"type": "sightseeing", "title": "Villa Rufolo Gardens, Ravello", "time": "11:30", "description": "Terraced gardens with infinity views of the coast"},
                {"type": "meal", "title": "Cumpa' Cosimo", "time": "13:00", "description": "Home-style Amalfitan cooking in Ravello", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Positano Beach", "time": "15:30", "description": "Colorful cliffside town — swim & explore boutiques", "transit": {"mode": "car", "duration": "40 min"}},
                {"type": "meal", "title": "Lo Guarracino", "time": "19:30", "description": "Seafood terrace perched above the sea in Positano", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
    ],
    # ==================== FRANCE ====================
    "paris": [
        {
            "title": "Eiffel Tower, Louvre & Left Bank",
            "activities": [
                {"type": "hotel", "title": "Hotel Le Marais", "time": "08:00", "description": "Charming hotel in the historic Marais district"},
                {"type": "meal", "title": "Du Pain et des Idées", "time": "08:30", "description": "Legendary bakery — pain des amis & escargot pastry", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Eiffel Tower", "time": "10:00", "description": "Summit access for 360° Paris panorama", "transit": {"mode": "train", "duration": "20 min"}},
                {"type": "sightseeing", "title": "Musée d'Orsay", "time": "12:30", "description": "Impressionist masterpieces in a former railway station", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Bouillon Racine", "time": "13:30", "description": "Art Nouveau gem — classic French brasserie fare", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Louvre Museum", "time": "15:00", "description": "Mona Lisa, Venus de Milo — focus on key wings", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Jardin des Tuileries", "time": "17:30", "description": "Formal gardens between the Louvre and Place de la Concorde", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Le Comptoir du Panthéon", "time": "19:30", "description": "Terrace dining in the Latin Quarter", "transit": {"mode": "walk", "duration": "15 min"}},
            ],
        },
        {
            "title": "Montmartre, Sacré-Cœur & Le Marais",
            "activities": [
                {"type": "hotel", "title": "Hotel Le Marais", "time": "08:00"},
                {"type": "meal", "title": "Café de Flore", "time": "08:30", "description": "Iconic Left Bank cafe — croque monsieur & café crème", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Sacré-Cœur Basilica", "time": "10:00", "description": "White-domed hilltop basilica with city views", "transit": {"mode": "train", "duration": "20 min"}},
                {"type": "sightseeing", "title": "Montmartre & Place du Tertre", "time": "11:30", "description": "Artists' square, winding lanes, Amélie vibes", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Le Bouillon Chartier", "time": "13:00", "description": "Belle Époque workers' canteen — incredible value", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Le Marais Quarter", "time": "15:00", "description": "Medieval streets, galleries, boutiques & falafel on Rue des Rosiers", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Notre-Dame (exterior)", "time": "17:00", "description": "View the restoration progress of the legendary cathedral", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Chez Janou", "time": "19:30", "description": "Provençal cuisine — famous for the chocolate mousse bowl", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
        {
            "title": "Versailles & Champs-Élysées",
            "activities": [
                {"type": "hotel", "title": "Hotel Le Marais", "time": "07:30"},
                {"type": "meal", "title": "Boulangerie Poilâne", "time": "08:00", "description": "Famous sourdough bakery — tartine for breakfast", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "transport", "title": "RER C to Versailles", "time": "08:45", "description": "45-minute train to the Palace of Versailles", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Palace of Versailles", "time": "10:00", "description": "Hall of Mirrors, royal apartments & Marie Antoinette's estate"},
                {"type": "sightseeing", "title": "Gardens of Versailles", "time": "12:00", "description": "800 hectares of formal gardens & fountains", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "La Petite Venise", "time": "13:00", "description": "Italian restaurant in the Grand Canal wing of Versailles", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Champs-Élysées & Arc de Triomphe", "time": "16:00", "description": "Iconic avenue — climb the Arc for sunset views", "transit": {"mode": "train", "duration": "45 min"}},
                {"type": "meal", "title": "Le Relais de l'Entrecôte", "time": "19:30", "description": "No menu — just steak-frites with secret sauce", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
        {
            "title": "Seine Cruise & Hidden Paris",
            "activities": [
                {"type": "hotel", "title": "Hotel Le Marais", "time": "08:30"},
                {"type": "meal", "title": "Claus", "time": "09:00", "description": "Brunch paradise — granola bowls & fresh juice", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Musée de l'Orangerie", "time": "10:30", "description": "Monet's Water Lilies in two oval rooms", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Sainte-Chapelle", "time": "12:00", "description": "Stunning 13th-century stained glass windows", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Breizh Café", "time": "13:00", "description": "Best Breton crêpes & galettes in Paris", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "transport", "title": "Seine River Cruise", "time": "15:00", "description": "1-hour boat cruise past major landmarks", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "sightseeing", "title": "Canal Saint-Martin", "time": "17:00", "description": "Trendy waterside neighborhood — wine bars & boutiques", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Le Bouillon Pigalle", "time": "19:30", "description": "Modern bistro classics at honest prices", "transit": {"mode": "walk", "duration": "15 min"}},
            ],
        },
    ],
    "nice": [
        {
            "title": "Promenade, Old Town & Castle Hill",
            "activities": [
                {"type": "hotel", "title": "Hotel Negresco", "time": "08:00", "description": "Belle Époque landmark on the Promenade des Anglais"},
                {"type": "meal", "title": "Chez Pipo", "time": "08:30", "description": "Socca (chickpea flatbread) — a Nice specialty", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Promenade des Anglais", "time": "09:30", "description": "Morning walk along the legendary seaside boulevard", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Vieux Nice (Old Town)", "time": "10:30", "description": "Baroque architecture, flower market on Cours Saleya", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "La Merenda", "time": "12:30", "description": "Tiny restaurant, no phone — Niçoise cuisine at its best", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Castle Hill (Colline du Château)", "time": "14:30", "description": "Panoramic views of the Baie des Anges", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Musée Matisse", "time": "16:30", "description": "Comprehensive collection in a 17th-century villa", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "meal", "title": "Le Safari", "time": "19:30", "description": "Classic French Riviera dining on Cours Saleya", "transit": {"mode": "bus", "duration": "15 min"}},
            ],
        },
        {
            "title": "Beach Day & Côte d'Azur Vibes",
            "activities": [
                {"type": "hotel", "title": "Hotel Negresco", "time": "08:30"},
                {"type": "meal", "title": "Café de Turin", "time": "09:00", "description": "Seafood platters on Place Garibaldi", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Plage de Castel", "time": "10:30", "description": "Public beach with turquoise water below Castle Hill", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "meal", "title": "Olive et Artichaut", "time": "13:00", "description": "Mediterranean fusion in a charming old town setting", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Cimiez Monastery & Gardens", "time": "15:00", "description": "Franciscan monastery with Nice's best rose garden", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "meal", "title": "Chez René Socca", "time": "19:00", "description": "Street food dinner — socca, farcis, pissaladière", "transit": {"mode": "bus", "duration": "12 min"}},
            ],
        },
    ],
    "lyon": [
        {
            "title": "Gastronomy Capital & Old Lyon",
            "activities": [
                {"type": "hotel", "title": "Cour des Loges", "time": "08:00", "description": "Renaissance palace hotel in Vieux Lyon"},
                {"type": "meal", "title": "Boulangerie du Palais", "time": "08:30", "description": "Fresh croissants & pain au chocolat", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Vieux Lyon & Traboules", "time": "10:00", "description": "Renaissance quarter — explore secret covered passageways", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Basilica of Notre-Dame de Fourvière", "time": "11:30", "description": "Hilltop basilica with panoramic city views", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Bouchon Daniel et Denise", "time": "13:00", "description": "Authentic Lyonnaise bouchon — quenelles & andouillette", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Les Halles de Lyon Paul Bocuse", "time": "15:00", "description": "Gourmet food hall — cheese, charcuterie, wine tastings", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Café Comptoir Abel", "time": "19:30", "description": "Lyon's oldest bouchon since 1928", "transit": {"mode": "walk", "duration": "12 min"}},
            ],
        },
    ],
    "bordeaux": [
        {
            "title": "Wine Capital & Miroir d'Eau",
            "activities": [
                {"type": "hotel", "title": "InterContinental Bordeaux", "time": "08:00", "description": "Grand hotel on the Place de la Comédie"},
                {"type": "meal", "title": "Café Français", "time": "08:30", "description": "Breakfast on Place Pey Berland", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Miroir d'Eau", "time": "10:00", "description": "World's largest reflecting pool — stunning photo spot", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Place de la Bourse", "time": "10:30", "description": "Iconic 18th-century square facing the Garonne river", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Le Petit Commerce", "time": "12:30", "description": "Fresh oysters & Atlantic seafood", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Cité du Vin", "time": "14:30", "description": "Interactive wine museum — tasting included", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Rue Sainte-Catherine", "time": "17:00", "description": "Europe's longest pedestrian shopping street", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Le Chapon Fin", "time": "19:30", "description": "Historic restaurant — Bordelaise cuisine paired with local wines", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
    ],
    # ==================== SPAIN ====================
    "barcelona": [
        {
            "title": "Gaudí Masterpieces & Gothic Quarter",
            "activities": [
                {"type": "hotel", "title": "Hotel Casa Bonay", "time": "08:00", "description": "Design hotel in the Eixample district"},
                {"type": "meal", "title": "Federal Café", "time": "08:30", "description": "Brunch & specialty coffee in the Gothic Quarter", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Sagrada Familia", "time": "10:00", "description": "Gaudí's unfinished masterpiece — tower access for city views", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Park Güell", "time": "12:30", "description": "Gaudí's colorful mosaic-covered park on a hilltop", "transit": {"mode": "bus", "duration": "20 min"}},
                {"type": "meal", "title": "Bar Cañete", "time": "14:00", "description": "Upscale tapas bar on La Rambla", "transit": {"mode": "train", "duration": "20 min"}},
                {"type": "sightseeing", "title": "Gothic Quarter (Barri Gòtic)", "time": "16:00", "description": "Medieval streets, cathedral & hidden plazas", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "La Rambla", "time": "17:30", "description": "Famous tree-lined pedestrian boulevard", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Cal Pep", "time": "20:00", "description": "Legendary counter-service seafood tapas", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
        {
            "title": "Barceloneta Beach & El Born",
            "activities": [
                {"type": "hotel", "title": "Hotel Casa Bonay", "time": "08:30"},
                {"type": "meal", "title": "Flax & Kale", "time": "09:00", "description": "Healthy brunch spot with creative dishes", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "La Boqueria Market", "time": "10:00", "description": "Famous food market — fresh juices, jamón, seafood", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Picasso Museum", "time": "11:30", "description": "Comprehensive collection of Picasso's early works", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "meal", "title": "La Cova Fumada", "time": "13:00", "description": "No-frills locals' spot — inventor of the bomba (potato croquette)", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Barceloneta Beach", "time": "15:00", "description": "Mediterranean beach with promenade & chiringuitos", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "El Born Cultural Center", "time": "17:00", "description": "Ruins of 18th-century Barcelona under a glass market hall", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "meal", "title": "Tickets", "time": "20:30", "description": "Ferran Adrià's playful tapas bar — book weeks ahead", "transit": {"mode": "train", "duration": "15 min"}},
            ],
        },
        {
            "title": "Montjuïc & Modernisme Trail",
            "activities": [
                {"type": "hotel", "title": "Hotel Casa Bonay", "time": "08:00"},
                {"type": "meal", "title": "Betlem Brunch", "time": "08:30", "description": "Avocado toast & cold-pressed juices", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Casa Batlló", "time": "10:00", "description": "Gaudí's dragon-inspired apartment building", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Casa Milà (La Pedrera)", "time": "11:30", "description": "Gaudí's undulating stone facade & rooftop warriors", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Cervecería Catalana", "time": "13:00", "description": "Bustling tapas institution on Carrer de Mallorca", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "sightseeing", "title": "Montjuïc Castle & Gardens", "time": "15:00", "description": "Hilltop fortress with harbor panoramas — take the cable car", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Magic Fountain of Montjuïc", "time": "18:00", "description": "Evening light and music show (check schedule)", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Bodega 1900", "time": "20:30", "description": "Adrià brothers' vermouth bar with creative conservas", "transit": {"mode": "walk", "duration": "15 min"}},
            ],
        },
    ],
    "madrid": [
        {
            "title": "Prado, Retiro & Tapas Trail",
            "activities": [
                {"type": "hotel", "title": "Only YOU Boutique Hotel", "time": "08:00", "description": "Trendy hotel in the Barrio de las Letras"},
                {"type": "meal", "title": "Café del Círculo de Bellas Artes", "time": "08:30", "description": "Rooftop breakfast with Madrid skyline views", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Museo del Prado", "time": "10:00", "description": "Velázquez, Goya, El Greco — one of the world's greatest museums", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Retiro Park", "time": "12:30", "description": "Crystal Palace, rowboats on the lake, rose gardens", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Mercado de San Miguel", "time": "13:30", "description": "Gourmet market — tapas grazing from stall to stall", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Royal Palace of Madrid", "time": "15:30", "description": "Largest royal palace in Western Europe — lavish state rooms", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Plaza Mayor", "time": "17:30", "description": "Grand central square — churros con chocolate at San Ginés", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "meal", "title": "Sobrino de Botín", "time": "20:00", "description": "World's oldest restaurant (since 1725) — roast suckling pig", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
        {
            "title": "Reina Sofía, Gran Vía & Malasaña",
            "activities": [
                {"type": "hotel", "title": "Only YOU Boutique Hotel", "time": "08:30"},
                {"type": "meal", "title": "La Rollerie", "time": "09:00", "description": "French-inspired brunch in a stylish space", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Reina Sofía Museum", "time": "10:00", "description": "Picasso's Guernica and Spanish modern art", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Barrio de las Letras", "time": "12:00", "description": "Literary quarter — quotes embedded in the cobblestones", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Casa Labra", "time": "13:00", "description": "Standing-room tapas since 1860 — cod croquettes", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Gran Vía", "time": "14:30", "description": "Madrid's Broadway — architecture, theaters, shopping", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Malasaña & Plaza del Dos de Mayo", "time": "16:30", "description": "Hipster neighborhood — vintage shops, street art, craft bars", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "La Barraca", "time": "20:00", "description": "Best paella in Madrid — Valencian-style rice dishes", "transit": {"mode": "walk", "duration": "12 min"}},
            ],
        },
    ],
    "seville": [
        {
            "title": "Alcázar, Flamenco & Triana",
            "activities": [
                {"type": "hotel", "title": "Hotel Alfonso XIII", "time": "08:00", "description": "Grand Mudéjar-style palace hotel"},
                {"type": "meal", "title": "Confitería La Campana", "time": "08:30", "description": "Seville's oldest pastry shop — churros & tortas", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Real Alcázar", "time": "09:30", "description": "Stunning Mudéjar palace — Game of Thrones filming location", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Seville Cathedral & Giralda Tower", "time": "11:30", "description": "World's largest Gothic cathedral — climb the ramp to the top", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "El Rinconcillo", "time": "13:30", "description": "Seville's oldest bar (since 1670) — spinach & chickpea tapas", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Plaza de España", "time": "15:30", "description": "Magnificent semicircular plaza with tiled alcoves for each province", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Triana Quarter", "time": "17:30", "description": "Cross the river — ceramic workshops, tapas bars, riverside walks", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Casa Anselma", "time": "21:00", "description": "Spontaneous flamenco in a Triana tavern — no sign outside", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
    ],
    "granada": [
        {
            "title": "Alhambra & Albaicín",
            "activities": [
                {"type": "hotel", "title": "Parador de Granada", "time": "08:00", "description": "Stay inside the Alhambra complex itself"},
                {"type": "meal", "title": "Café 4 Gatos", "time": "08:30", "description": "Cozy breakfast spot near Plaza Nueva", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Alhambra & Nasrid Palaces", "time": "09:00", "description": "Islamic architecture masterpiece — book months ahead", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Generalife Gardens", "time": "12:00", "description": "Summer palace gardens with fountains and courtyards", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Los Diamantes", "time": "13:30", "description": "Free tapas with every drink — fried fish is legendary", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Albaicín Quarter", "time": "15:30", "description": "UNESCO white-walled Moorish quarter with tea houses", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Mirador de San Nicolás", "time": "17:30", "description": "Best sunset viewpoint — Alhambra against the Sierra Nevada", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "meal", "title": "Bodegas Castañeda", "time": "20:00", "description": "Historic bar — free generous tapas with every round", "transit": {"mode": "walk", "duration": "12 min"}},
            ],
        },
    ],
    # ==================== JAPAN ====================
    "tokyo": [
        {
            "title": "Shibuya, Harajuku & Meiji Shrine",
            "activities": [
                {"type": "hotel", "title": "Park Hyatt Tokyo", "time": "08:00", "description": "Shinjuku skyscraper hotel — Lost in Translation vibes"},
                {"type": "meal", "title": "Tsukiji Outer Market", "time": "08:30", "description": "Fresh sushi breakfast & tamagoyaki at the market", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Meiji Shrine", "time": "10:00", "description": "Serene Shinto shrine surrounded by ancient forest", "transit": {"mode": "train", "duration": "20 min"}},
                {"type": "sightseeing", "title": "Harajuku & Takeshita Street", "time": "11:30", "description": "Teen fashion capital — kawaii culture & crepe shops", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Afuri Ramen", "time": "12:30", "description": "Yuzu shio ramen — light, citrusy, and addictive", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Shibuya Crossing", "time": "14:00", "description": "World's busiest pedestrian crossing — view from Shibuya Sky", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "shopping", "title": "Shibuya 109 & Center-gai", "time": "15:30", "description": "Shopping and street culture in Shibuya's core", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "Omoide Yokocho (Memory Lane)", "time": "19:00", "description": "Tiny yakitori alleys in Shinjuku — smoke-filled nostalgia", "transit": {"mode": "train", "duration": "10 min"}},
            ],
        },
        {
            "title": "Asakusa, Akihabara & Ueno",
            "activities": [
                {"type": "hotel", "title": "Park Hyatt Tokyo", "time": "08:00"},
                {"type": "meal", "title": "Kayaba Coffee", "time": "08:30", "description": "Retro kissaten (coffee house) in Yanaka — egg sandwiches", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Senso-ji Temple", "time": "10:00", "description": "Tokyo's oldest temple — thunder gate & Nakamise shopping street", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Sumida River Walk & Tokyo Skytree", "time": "11:30", "description": "River crossing with 634m tower views", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Asakusa Gyukatsu", "time": "12:30", "description": "Deep-fried beef cutlet grilled on a hot stone", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Ueno Park & Tokyo National Museum", "time": "14:00", "description": "Japan's most visited museum — samurai armor & ukiyo-e prints", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Akihabara Electric Town", "time": "16:30", "description": "Anime, manga, arcades & electronics heaven", "transit": {"mode": "train", "duration": "5 min"}},
                {"type": "meal", "title": "Gonpachi Nishi-Azabu", "time": "19:00", "description": "Kill Bill restaurant — soba & robata grill", "transit": {"mode": "train", "duration": "20 min"}},
            ],
        },
        {
            "title": "Shinjuku, Ginza & Tokyo Tower",
            "activities": [
                {"type": "hotel", "title": "Park Hyatt Tokyo", "time": "08:00"},
                {"type": "meal", "title": "Bills Omotesando", "time": "08:30", "description": "World's best ricotta pancakes", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Shinjuku Gyoen National Garden", "time": "10:00", "description": "Japanese, English & French gardens in central Tokyo", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Tokyo Metropolitan Government Building", "time": "12:00", "description": "Free observation deck on the 45th floor", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "meal", "title": "Fuunji Ramen", "time": "12:30", "description": "Legendary tsukemen (dipping ramen) — always a queue", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "shopping", "title": "Ginza District", "time": "14:30", "description": "Luxury shopping — department stores, galleries, and flagship brands", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Tokyo Tower", "time": "17:00", "description": "333m red-and-white tower — main deck at sunset", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Roppongi Yokocho", "time": "19:00", "description": "Indoor food court with 18 regional Japanese restaurants", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
        {
            "title": "Teamlab, Odaiba & Shimokitazawa",
            "activities": [
                {"type": "hotel", "title": "Park Hyatt Tokyo", "time": "08:30"},
                {"type": "meal", "title": "Morimoto Morning Market", "time": "09:00", "description": "Fresh onigiri & miso soup breakfast", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "teamLab Borderless", "time": "10:00", "description": "Immersive digital art museum — wear white for best effect", "transit": {"mode": "train", "duration": "25 min"}},
                {"type": "meal", "title": "Odaiba Takoyaki Museum", "time": "12:30", "description": "Sample takoyaki from the best shops across Japan", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Shimokitazawa", "time": "14:30", "description": "Bohemian neighborhood — thrift shops, live music, tiny bars", "transit": {"mode": "train", "duration": "30 min"}},
                {"type": "sightseeing", "title": "Golden Gai, Shinjuku", "time": "17:00", "description": "Six narrow alleys of over 200 micro-bars", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Uobei Sushi", "time": "19:00", "description": "High-speed conveyor sushi — order via tablet, ¥100/plate", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
    ],
    "kyoto": [
        {
            "title": "Fushimi Inari, Bamboo Grove & Temples",
            "activities": [
                {"type": "hotel", "title": "Hoshinoya Kyoto", "time": "07:30", "description": "Riverside ryokan accessible only by boat"},
                {"type": "meal", "title": "Inoda Coffee Honten", "time": "08:00", "description": "Kyoto's beloved retro kissaten since 1947", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Fushimi Inari Shrine", "time": "09:00", "description": "Thousands of vermilion torii gates up Mt. Inari — go early to beat crowds", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Arashiyama Bamboo Grove", "time": "11:30", "description": "Towering bamboo forest — magical morning light", "transit": {"mode": "train", "duration": "25 min"}},
                {"type": "meal", "title": "Yoshimura Soba", "time": "12:30", "description": "Handmade soba overlooking the river in Arashiyama", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Kinkaku-ji (Golden Pavilion)", "time": "14:30", "description": "Gold-leaf covered Zen temple reflected in a mirror pond", "transit": {"mode": "bus", "duration": "20 min"}},
                {"type": "sightseeing", "title": "Nishiki Market", "time": "16:30", "description": "Kyoto's kitchen — 130 shops of local delicacies", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "meal", "title": "Gion Karyo", "time": "19:00", "description": "Kaiseki dinner in Gion — multi-course Japanese haute cuisine", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
        {
            "title": "Gion, Philosopher's Path & Tea Ceremony",
            "activities": [
                {"type": "hotel", "title": "Hoshinoya Kyoto", "time": "08:00"},
                {"type": "meal", "title": "Saryo Suisen", "time": "08:30", "description": "Matcha and wagashi (traditional sweets) breakfast", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Philosopher's Path", "time": "09:30", "description": "2km canal-side stone path lined with cherry trees", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Ginkaku-ji (Silver Pavilion)", "time": "10:30", "description": "Zen temple with immaculate sand garden", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Nanzen-ji Temple", "time": "12:00", "description": "Massive temple gate & Roman-style brick aqueduct", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Omen Nanzenji", "time": "12:30", "description": "Famous udon noodles near Nanzen-ji", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "sightseeing", "title": "Gion District & Geisha Spotting", "time": "15:00", "description": "Historic geisha quarter — wooden machiya houses", "transit": {"mode": "bus", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Tea Ceremony Experience", "time": "16:30", "description": "Participate in a traditional Japanese tea ceremony", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Pontocho Alley", "time": "19:00", "description": "Narrow lantern-lit alley — pick any riverside restaurant", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
        {
            "title": "Kiyomizu-dera, Higashiyama & Sake",
            "activities": [
                {"type": "hotel", "title": "Hoshinoya Kyoto", "time": "07:30"},
                {"type": "meal", "title": "Weekenders Coffee", "time": "08:00", "description": "Specialty coffee in a minimalist Kyoto-style space", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Kiyomizu-dera Temple", "time": "09:00", "description": "Hilltop temple with a wooden stage jutting over the valley", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Higashiyama Historic District", "time": "10:30", "description": "Preserved Edo-period streets — ceramics, incense, pickles", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Hirano-ya", "time": "12:00", "description": "Tofu cuisine in a 300-year-old restaurant", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Fushimi Sake District", "time": "14:30", "description": "Sake breweries — tastings at Gekkeikan and Kizakura", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "meal", "title": "Tofuya Ukai", "time": "18:30", "description": "Exquisite tofu kaiseki in a garden setting", "transit": {"mode": "train", "duration": "15 min"}},
            ],
        },
    ],
    "osaka": [
        {
            "title": "Dotonbori, Street Food & Castle",
            "activities": [
                {"type": "hotel", "title": "Conrad Osaka", "time": "08:00", "description": "Luxury hotel with river views in Nakanoshima"},
                {"type": "meal", "title": "Rikuro's Cheesecake", "time": "08:30", "description": "Famously jiggly Japanese cheesecake — watch it being made", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Osaka Castle", "time": "10:00", "description": "Iconic castle surrounded by moats and cherry trees", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Shinsekai District", "time": "12:00", "description": "Retro neighborhood around Tsutenkaku Tower", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Daruma Kushikatsu", "time": "12:30", "description": "Osaka's king of kushikatsu — deep-fried skewers on a stick", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "sightseeing", "title": "Dotonbori", "time": "14:30", "description": "Neon-lit canal — the Glico Man, giant crab, and takoyaki", "transit": {"mode": "train", "duration": "8 min"}},
                {"type": "meal", "title": "Takoyaki Wanaka", "time": "15:30", "description": "Crispy-outside creamy-inside octopus balls", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "sightseeing", "title": "Shinsaibashi Shopping Arcade", "time": "16:30", "description": "600m covered shopping street — fashion, souvenirs, snacks", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "Mizuno Okonomiyaki", "time": "19:00", "description": "Osaka's soul food — savory pancake cooked on a griddle", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
        {
            "title": "Kuromon Market & Osaka Nightlife",
            "activities": [
                {"type": "hotel", "title": "Conrad Osaka", "time": "08:00"},
                {"type": "meal", "title": "Kuromon Market", "time": "08:30", "description": "Osaka's kitchen — sashimi, grilled scallops, fresh uni", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Sumiyoshi Taisha", "time": "10:30", "description": "One of Japan's oldest shrines with unique architectural style", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Tennoji & Abeno Harukas", "time": "12:00", "description": "Japan's tallest building — observation deck at 300m", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Ajinoya", "time": "13:00", "description": "Premium okonomiyaki with wagyu beef", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Namba Parks", "time": "15:00", "description": "Shopping complex with rooftop canyon garden", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Hozenji Yokocho", "time": "19:00", "description": "Atmospheric lantern-lit alley — intimate izakayas", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
    ],
    "hiroshima": [
        {
            "title": "Peace Memorial & Miyajima Island",
            "activities": [
                {"type": "hotel", "title": "Sheraton Grand Hiroshima", "time": "08:00", "description": "Central hotel near the Peace Memorial"},
                {"type": "meal", "title": "Musubi Musashi", "time": "08:30", "description": "Hiroshima-style onigiri at the station", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Hiroshima Peace Memorial Park", "time": "09:30", "description": "A-Bomb Dome, Memorial Museum — deeply moving experience", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "transport", "title": "Ferry to Miyajima Island", "time": "12:00", "description": "JR ferry to the sacred island — 10-minute ride", "transit": {"mode": "train", "duration": "30 min"}},
                {"type": "meal", "title": "Kakiya Oyster Bar", "time": "12:45", "description": "Grilled Miyajima oysters — the island's specialty", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Itsukushima Shrine & Floating Torii", "time": "14:00", "description": "Iconic vermilion gate appearing to float on the sea", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Mt. Misen Ropeway", "time": "15:30", "description": "Cable car to the island's summit — wild deer & panoramas", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Nagata-ya", "time": "19:00", "description": "Hiroshima-style okonomiyaki — layered with noodles & cabbage", "transit": {"mode": "train", "duration": "40 min", "note": "Ferry back + tram to city center"}},
            ],
        },
    ],
    # ==================== UK ====================
    "london": [
        {
            "title": "Westminster, Tower & South Bank",
            "activities": [
                {"type": "hotel", "title": "The Ned London", "time": "08:00", "description": "Members' club hotel in a former Midland Bank"},
                {"type": "meal", "title": "Dishoom King's Cross", "time": "08:30", "description": "Bombay-style cafe — bacon naan roll & chai", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Tower of London", "time": "10:00", "description": "Crown Jewels, Beefeaters & 1000 years of history", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Tower Bridge", "time": "12:00", "description": "Walk the glass floor high-level walkways", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Borough Market", "time": "12:30", "description": "London's finest food market — toasties, pies, pastries", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Westminster Abbey", "time": "14:30", "description": "Gothic masterpiece — coronation church since 1066", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Big Ben & Houses of Parliament", "time": "16:00", "description": "Iconic clock tower on the Thames", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "London Eye", "time": "17:00", "description": "30-minute rotation for panoramic Thames views", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Padella", "time": "19:30", "description": "Fresh handmade pasta — pici cacio e pepe is legendary", "transit": {"mode": "train", "duration": "10 min"}},
            ],
        },
        {
            "title": "British Museum, Notting Hill & West End",
            "activities": [
                {"type": "hotel", "title": "The Ned London", "time": "08:00"},
                {"type": "meal", "title": "The Wolseley", "time": "08:30", "description": "Grand European cafe-restaurant on Piccadilly", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "British Museum", "time": "10:00", "description": "Rosetta Stone, Elgin Marbles, Egyptian mummies — free entry", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Covent Garden", "time": "12:00", "description": "Street performers, boutiques & the Royal Opera House piazza", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Bao Soho", "time": "12:30", "description": "Taiwanese steamed buns — expect a queue, worth it", "transit": {"mode": "walk", "duration": "8 min"}},
                {"type": "sightseeing", "title": "Notting Hill & Portobello Road Market", "time": "14:30", "description": "Pastel houses, antiques & vintage finds", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "shopping", "title": "Oxford Street & Carnaby Street", "time": "16:30", "description": "Flagship stores and indie boutiques", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "meal", "title": "Hawksmoor Seven Dials", "time": "19:30", "description": "Best steak in London — dry-aged British beef", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
        {
            "title": "South Kensington, Hyde Park & Camden",
            "activities": [
                {"type": "hotel", "title": "The Ned London", "time": "08:00"},
                {"type": "meal", "title": "Granger & Co", "time": "08:30", "description": "Australian-style brunch in Notting Hill", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Natural History Museum", "time": "10:00", "description": "Blue whale skeleton, dinosaurs & gems — free entry", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "V&A Museum", "time": "12:00", "description": "World's largest museum of decorative arts", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "meal", "title": "Kensington Creperie", "time": "13:00", "description": "French crêpes near the museum quarter", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Hyde Park & Kensington Gardens", "time": "14:30", "description": "Serpentine Gallery, Peter Pan statue, Italian Gardens", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Camden Market", "time": "16:30", "description": "Eclectic market — street food, vintage clothing, canal views", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "meal", "title": "Dishoom Shoreditch", "time": "19:30", "description": "Bombay cafe — black daal that's been simmering for 24 hours", "transit": {"mode": "train", "duration": "15 min"}},
            ],
        },
        {
            "title": "Greenwich, Tate Modern & Theatre",
            "activities": [
                {"type": "hotel", "title": "The Ned London", "time": "08:30"},
                {"type": "meal", "title": "E Pellicci", "time": "09:00", "description": "Art Deco Italian greasy spoon in Bethnal Green — since 1900", "transit": {"mode": "train", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Greenwich & Cutty Sark", "time": "10:00", "description": "Maritime heritage, Prime Meridian line, Royal Observatory", "transit": {"mode": "train", "duration": "20 min"}},
                {"type": "meal", "title": "Goddards at Greenwich", "time": "12:30", "description": "Traditional pie & mash — proper East End grub", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Tate Modern", "time": "14:30", "description": "Contemporary art in a former power station — free entry", "transit": {"mode": "train", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Millennium Bridge & St Paul's Cathedral", "time": "16:30", "description": "Cross the bridge to Wren's masterpiece dome", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Flat Iron Soho", "time": "19:00", "description": "No-fuss flat iron steak dinner — £12 including salad", "transit": {"mode": "train", "duration": "10 min"}},
            ],
        },
    ],
    "edinburgh": [
        {
            "title": "Castle, Royal Mile & Arthur's Seat",
            "activities": [
                {"type": "hotel", "title": "The Balmoral", "time": "08:00", "description": "Iconic clock tower hotel on Princes Street"},
                {"type": "meal", "title": "The Pantry", "time": "08:30", "description": "Stockbridge brunch spot — Scottish eggs Benedict", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Edinburgh Castle", "time": "10:00", "description": "Hilltop fortress overlooking the city — Stone of Destiny", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Royal Mile", "time": "12:00", "description": "Medieval spine of Old Town — closes, wynds & street performers", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "The Outsider", "time": "13:00", "description": "Modern Scottish cuisine with castle views", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Holyrood Palace", "time": "14:30", "description": "Official Scottish residence of the King — Mary Queen of Scots' chambers", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Arthur's Seat", "time": "16:00", "description": "Extinct volcano hike — 360° views of Edinburgh, Firth of Forth", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "The Witchery by the Castle", "time": "19:30", "description": "Gothic dining at the castle gates — theatrical setting", "transit": {"mode": "walk", "duration": "20 min"}},
            ],
        },
        {
            "title": "New Town, Leith & Whisky",
            "activities": [
                {"type": "hotel", "title": "The Balmoral", "time": "08:00"},
                {"type": "meal", "title": "Loudons Cafe", "time": "08:30", "description": "Specialty coffee & sourdough toast", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Scottish National Gallery", "time": "10:00", "description": "Scottish & European masters — free entry", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Calton Hill", "time": "11:30", "description": "National Monument & Nelson Monument — iconic city panorama", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Fishers in Leith", "time": "12:30", "description": "Fresh seafood at the historic port district", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Royal Yacht Britannia", "time": "14:30", "description": "Tour the Queen's former floating palace in Leith", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Scotch Whisky Experience", "time": "16:30", "description": "Barrel ride through whisky-making — guided tasting", "transit": {"mode": "bus", "duration": "15 min"}},
                {"type": "meal", "title": "Timberyard", "time": "19:30", "description": "Farm-to-table tasting menu in a converted warehouse", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
        {
            "title": "Dean Village, Stockbridge & Ghost Tour",
            "activities": [
                {"type": "hotel", "title": "The Balmoral", "time": "08:00"},
                {"type": "meal", "title": "Milk Bar", "time": "08:30", "description": "Tiny brunch spot — shakshuka & banana bread", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Dean Village", "time": "10:00", "description": "Fairy-tale village hidden in a river gorge in the city center", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "sightseeing", "title": "Scottish National Gallery of Modern Art", "time": "11:30", "description": "Sculpture garden & modern art in a neoclassical building", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "Scran & Scallie", "time": "13:00", "description": "Tom Kitchin's gastropub — haggis, neeps & tatties", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Stockbridge Market (Sundays)", "time": "14:30", "description": "Artisan food & craft market in a village-like neighborhood", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Greyfriars Kirkyard", "time": "16:30", "description": "Atmospheric cemetery — Greyfriars Bobby & Harry Potter inspiration", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Ondine", "time": "19:30", "description": "Sustainable Scottish seafood near the Royal Mile", "transit": {"mode": "walk", "duration": "5 min"}},
            ],
        },
    ],
    "bath": [
        {
            "title": "Roman Baths, Royal Crescent & Thermal Spa",
            "activities": [
                {"type": "hotel", "title": "The Gainsborough Bath Spa", "time": "08:00", "description": "Only hotel with direct access to Bath's thermal waters"},
                {"type": "meal", "title": "The Pump Room", "time": "08:30", "description": "Georgian breakfast above the Roman Baths — live music", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Roman Baths", "time": "10:00", "description": "2000-year-old bathing complex — remarkably preserved", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "sightseeing", "title": "Bath Abbey", "time": "11:30", "description": "Perpendicular Gothic church with fan-vaulted ceiling", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "meal", "title": "Sally Lunn's", "time": "12:30", "description": "Oldest house in Bath — famous Sally Lunn bun since 1680", "transit": {"mode": "walk", "duration": "3 min"}},
                {"type": "sightseeing", "title": "Royal Crescent & The Circus", "time": "14:00", "description": "Georgian architectural masterpieces — sweeping crescents", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Pulteney Bridge & Weir", "time": "15:30", "description": "Palladian bridge lined with shops — one of only a few in the world", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": "Thermae Bath Spa", "time": "16:30", "description": "Rooftop thermal pool with views of Bath Abbey", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "The Scallop Shell", "time": "19:30", "description": "Sustainable fish & chips — best in Bath", "transit": {"mode": "walk", "duration": "8 min"}},
            ],
        },
    ],
    "oxford": [
        {
            "title": "Dreaming Spires & College Tour",
            "activities": [
                {"type": "hotel", "title": "The Randolph Hotel", "time": "08:00", "description": "Gothic Revival hotel opposite the Ashmolean Museum"},
                {"type": "meal", "title": "The Grand Cafe", "time": "08:30", "description": "Breakfast at the site of England's first coffee house (1650)", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Bodleian Library", "time": "10:00", "description": "One of Europe's oldest libraries — Divinity School used in Harry Potter", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Radcliffe Camera", "time": "11:00", "description": "Iconic circular reading room — exterior only (but stunning)", "transit": {"mode": "walk", "duration": "2 min"}},
                {"type": "sightseeing", "title": "Christ Church College", "time": "11:30", "description": "Harry Potter's Great Hall, Lewis Carroll's Alice in Wonderland", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "meal", "title": "Covered Market", "time": "13:00", "description": "Indoor market since 1774 — pies, sandwiches & Ben's Cookies", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Ashmolean Museum", "time": "14:30", "description": "World's first public museum — free entry, remarkable collection", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": "Punting on the Cherwell", "time": "16:30", "description": "Punt along the river past University Parks", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "meal", "title": "The Eagle and Child", "time": "19:00", "description": "Tolkien & C.S. Lewis's favorite pub — the Inklings met here", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        },
    ],
}


def build_sample_day_itineraries(
    city_id: str,
    city_name: str,
    num_days: int,
    start_date: date,
) -> list[dict]:
    """
    Build sample day-by-day itinerary data for a city.

    Returns a list of DayItinerary dicts matching the frontend's expected shape:
    {
        dayNumber, date, cityName, title,
        activities: [{ id, data: { type, title, time, description }, status, transit? }]
    }
    """
    templates = CITY_ACTIVITIES.get(city_id, [])

    if not templates:
        # Fallback: generate generic activities for unknown cities
        templates = _build_generic_templates(city_name, num_days)

    result = []
    for d in range(num_days):
        current_date = start_date + timedelta(days=d)
        template = templates[d % len(templates)]

        activities = []
        for idx, act in enumerate(template["activities"]):
            entry: dict = {
                "id": f"{city_id}-d{d+1}-{idx}",
                "data": {
                    "type": act["type"],
                    "title": act["title"],
                    "time": act["time"],
                },
                "status": "upcoming",
            }
            if "description" in act:
                entry["data"]["description"] = act["description"]
            if "transit" in act:
                entry["transit"] = act["transit"]

            activities.append(entry)

        # Mark first activity as 'current' on day 1
        if d == 0 and activities:
            activities[0]["status"] = "current"

        result.append({
            "dayNumber": d + 1,
            "date": current_date.isoformat(),
            "cityName": city_name,
            "title": template["title"] if d < len(templates) else f"Day {d + 1} in {city_name}",
            "activities": activities,
        })

    return result


def _build_generic_templates(city_name: str, num_days: int) -> list[dict]:
    """Fallback templates for cities not in our database."""
    templates = []
    for d in range(num_days):
        templates.append({
            "title": f"Exploring {city_name}" if d == 0 else f"Day {d + 1} in {city_name}",
            "activities": [
                {"type": "hotel", "title": f"Hotel in {city_name}", "time": "08:00"},
                {"type": "meal", "title": "Local Breakfast", "time": "08:30", "description": f"Traditional breakfast spot in {city_name}", "transit": {"mode": "walk", "duration": "5 min"}},
                {"type": "sightseeing", "title": f"{city_name} Top Attraction", "time": "10:00", "description": "Must-see landmark", "transit": {"mode": "walk", "duration": "15 min"}},
                {"type": "meal", "title": "Local Lunch", "time": "13:00", "description": "Traditional local cuisine", "transit": {"mode": "walk", "duration": "10 min"}},
                {"type": "sightseeing", "title": f"{city_name} Cultural Site", "time": "15:00", "description": "Historical or cultural highlight", "transit": {"mode": "walk", "duration": "12 min"}},
                {"type": "meal", "title": "Dinner", "time": "19:30", "description": "Evening dining experience", "transit": {"mode": "walk", "duration": "10 min"}},
            ],
        })
    return templates
