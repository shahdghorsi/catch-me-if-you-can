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
        "name": "Starbucks - Paddington Station",
        "type": "cafe",
        "latitude": 51.5155,
        "longitude": -0.1760,
        "radius": 15,
        "floor": None,
        "icon": "☕"
    },
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
