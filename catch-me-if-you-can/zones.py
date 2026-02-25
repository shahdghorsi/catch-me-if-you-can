"""
Zone definitions for the Office Vibes Tracker - Paddington Edition
Each store/location has its own zone with a small radius to differentiate between them.
"""

# Paddington Office and nearby locations
DEFAULT_ZONES = [
    # === PADDINGTON OFFICE (Paddington Basin area) ===
    {
        "name": "Paddington Office - Ground",
        "type": "office",
        "latitude": 51.5170,
        "longitude": -0.1780,
        "radius": 40,
        "floor": 0,
        "icon": "🏢"
    },
    {
        "name": "Paddington Office - Floor 1",
        "type": "office",
        "latitude": 51.5170,
        "longitude": -0.1780,
        "radius": 40,
        "floor": 1,
        "icon": "🏢"
    },
    {
        "name": "Paddington Office - Floor 2",
        "type": "office",
        "latitude": 51.5170,
        "longitude": -0.1780,
        "radius": 40,
        "floor": 2,
        "icon": "🏢"
    },
    {
        "name": "Paddington Office - Floor 3",
        "type": "office",
        "latitude": 51.5170,
        "longitude": -0.1780,
        "radius": 40,
        "floor": 3,
        "icon": "🏢"
    },

    # === PUBS ===
    {
        "name": "Mad Bishop & Bear",
        "type": "pub",
        "latitude": 51.5167,
        "longitude": -0.1769,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Victoria",
        "type": "pub",
        "latitude": 51.5152,
        "longitude": -0.1743,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Cleveland Arms",
        "type": "pub",
        "latitude": 51.5178,
        "longitude": -0.1823,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Dickens Tavern",
        "type": "pub",
        "latitude": 51.5161,
        "longitude": -0.1795,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },

    # === CAFES ===
    {
        "name": "Costa - Praed Street",
        "type": "cafe",
        "latitude": 51.5165,
        "longitude": -0.1735,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },
    {
        "name": "Caffe Nero - Paddington",
        "type": "cafe",
        "latitude": 51.5158,
        "longitude": -0.1752,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },
    {
        "name": "Le Pain Quotidien",
        "type": "cafe",
        "latitude": 51.5173,
        "longitude": -0.1792,
        "radius": 15,
        "floor": None,
        "icon": "🥐"
    },

    # === RESTAURANTS / LUNCH SPOTS ===
    {
        "name": "Pret A Manger - Station",
        "type": "restaurant",
        "latitude": 51.5160,
        "longitude": -0.1765,
        "radius": 15,
        "floor": None,
        "icon": "🥪"
    },
    {
        "name": "Pret A Manger - Praed St",
        "type": "restaurant",
        "latitude": 51.5168,
        "longitude": -0.1742,
        "radius": 15,
        "floor": None,
        "icon": "🥪"
    },
    {
        "name": "Wagamama - Paddington",
        "type": "restaurant",
        "latitude": 51.5175,
        "longitude": -0.1788,
        "radius": 20,
        "floor": None,
        "icon": "🍜"
    },
    {
        "name": "Leon - Paddington",
        "type": "restaurant",
        "latitude": 51.5162,
        "longitude": -0.1758,
        "radius": 15,
        "floor": None,
        "icon": "🥗"
    },
    {
        "name": "Pizza Express - Paddington",
        "type": "restaurant",
        "latitude": 51.5148,
        "longitude": -0.1775,
        "radius": 20,
        "floor": None,
        "icon": "🍕"
    },
    {
        "name": "Nando's - Paddington",
        "type": "restaurant",
        "latitude": 51.5145,
        "longitude": -0.1762,
        "radius": 20,
        "floor": None,
        "icon": "🍗"
    },
    {
        "name": "Tesco Express - Praed St",
        "type": "restaurant",
        "latitude": 51.5163,
        "longitude": -0.1748,
        "radius": 15,
        "floor": None,
        "icon": "🛒"
    },

    # === GYM ===
    {
        "name": "PureGym Paddington",
        "type": "gym",
        "latitude": 51.5182,
        "longitude": -0.1798,
        "radius": 25,
        "floor": None,
        "icon": "💪"
    },

    # === MORE PUBS ===
    {
        "name": "Heist Bank",
        "type": "pub",
        "latitude": 51.5183,
        "longitude": -0.1798,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Pride of Paddington",
        "type": "pub",
        "latitude": 51.5171,
        "longitude": -0.1755,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Mitre - Lancaster Gate",
        "type": "pub",
        "latitude": 51.5118,
        "longitude": -0.1755,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Monkey Puzzle",
        "type": "pub",
        "latitude": 51.5186,
        "longitude": -0.1812,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Frontline Club",
        "type": "pub",
        "latitude": 51.5178,
        "longitude": -0.1802,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },
    {
        "name": "The Prince of Wales",
        "type": "pub",
        "latitude": 51.5142,
        "longitude": -0.1788,
        "radius": 20,
        "floor": None,
        "icon": "🍺"
    },

    # === MORE CAFES ===
    {
        "name": "Frequency Coffee",
        "type": "cafe",
        "latitude": 51.5185,
        "longitude": -0.1795,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },
    {
        "name": "Gail's Bakery - Paddington",
        "type": "cafe",
        "latitude": 51.5176,
        "longitude": -0.1785,
        "radius": 15,
        "floor": None,
        "icon": "🥐"
    },
    {
        "name": "Black Sheep Coffee",
        "type": "cafe",
        "latitude": 51.5169,
        "longitude": -0.1771,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },
    {
        "name": "Notes Coffee - Paddington",
        "type": "cafe",
        "latitude": 51.5164,
        "longitude": -0.1778,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },
    {
        "name": "EAT. - Paddington Station",
        "type": "cafe",
        "latitude": 51.5157,
        "longitude": -0.1763,
        "radius": 15,
        "floor": None,
        "icon": "🥪"
    },
    {
        "name": "Beany Green - Paddington",
        "type": "cafe",
        "latitude": 51.5179,
        "longitude": -0.1795,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },

    # === MORE RESTAURANTS ===
    {
        "name": "Honest Burgers - Paddington",
        "type": "restaurant",
        "latitude": 51.5172,
        "longitude": -0.1794,
        "radius": 20,
        "floor": None,
        "icon": "🍔"
    },
    {
        "name": "Itsu - Paddington",
        "type": "restaurant",
        "latitude": 51.5166,
        "longitude": -0.1768,
        "radius": 15,
        "floor": None,
        "icon": "🍣"
    },
    {
        "name": "Chipotle - Paddington",
        "type": "restaurant",
        "latitude": 51.5159,
        "longitude": -0.1745,
        "radius": 15,
        "floor": None,
        "icon": "🌯"
    },
    {
        "name": "Byron - Paddington",
        "type": "restaurant",
        "latitude": 51.5168,
        "longitude": -0.1782,
        "radius": 20,
        "floor": None,
        "icon": "🍔"
    },
    {
        "name": "The Grazing Goat",
        "type": "restaurant",
        "latitude": 51.5185,
        "longitude": -0.1565,
        "radius": 25,
        "floor": None,
        "icon": "🍽️"
    },
    {
        "name": "Pearl Liang - Chinese",
        "type": "restaurant",
        "latitude": 51.5181,
        "longitude": -0.1808,
        "radius": 20,
        "floor": None,
        "icon": "🥡"
    },
    {
        "name": "Satay House - Malaysian",
        "type": "restaurant",
        "latitude": 51.5172,
        "longitude": -0.1765,
        "radius": 20,
        "floor": None,
        "icon": "🍢"
    },
    {
        "name": "Lockhouse - Paddington Basin",
        "type": "restaurant",
        "latitude": 51.5177,
        "longitude": -0.1800,
        "radius": 25,
        "floor": None,
        "icon": "🍽️"
    },
    {
        "name": "Coppa Club - Paddington",
        "type": "restaurant",
        "latitude": 51.5174,
        "longitude": -0.1789,
        "radius": 20,
        "floor": None,
        "icon": "🍝"
    },
    {
        "name": "Darcie & May Green",
        "type": "restaurant",
        "latitude": 51.5180,
        "longitude": -0.1803,
        "radius": 20,
        "floor": None,
        "icon": "🥗"
    },
    {
        "name": "Hereford Road",
        "type": "restaurant",
        "latitude": 51.5155,
        "longitude": -0.1925,
        "radius": 20,
        "floor": None,
        "icon": "🍖"
    },
    {
        "name": "The Summerhouse",
        "type": "restaurant",
        "latitude": 51.5195,
        "longitude": -0.1835,
        "radius": 25,
        "floor": None,
        "icon": "🍽️"
    },
    {
        "name": "M&S Food - Paddington",
        "type": "restaurant",
        "latitude": 51.5161,
        "longitude": -0.1757,
        "radius": 20,
        "floor": None,
        "icon": "🛒"
    },
    {
        "name": "Canal Food Market",
        "type": "restaurant",
        "latitude": 51.5184,
        "longitude": -0.1792,
        "radius": 25,
        "floor": None,
        "icon": "🍴"
    },
    {
        "name": "Sainsbury's Local",
        "type": "restaurant",
        "latitude": 51.5167,
        "longitude": -0.1738,
        "radius": 15,
        "floor": None,
        "icon": "🛒"
    }
]


def init_zones(db, Zone):
    """Initialize the database with default zones if empty."""
    if Zone.query.count() == 0:
        for zone_data in DEFAULT_ZONES:
            zone = Zone(
                name=zone_data['name'],
                type=zone_data['type'],
                latitude=zone_data['latitude'],
                longitude=zone_data['longitude'],
                radius=zone_data['radius'],
                floor=zone_data.get('floor'),
                icon=zone_data.get('icon')
            )
            db.session.add(zone)
        db.session.commit()
        print(f"Initialized {len(DEFAULT_ZONES)} default zones")
