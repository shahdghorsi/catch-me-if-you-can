import math
from typing import List, Dict, Optional, Tuple

# Earth's radius in meters
EARTH_RADIUS = 6371000

# Clustering distance in meters
CLUSTER_DISTANCE = 50


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    Returns distance in meters.
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS * c


def detect_zone(latitude: float, longitude: float, zones: List[Dict]) -> Optional[Dict]:
    """
    Detect which zone a user is in based on their coordinates.
    Returns the most specific (smallest radius) matching zone.
    """
    matching_zones = []

    for zone in zones:
        distance = haversine_distance(
            latitude, longitude,
            zone['latitude'], zone['longitude']
        )

        if distance <= zone['radius']:
            matching_zones.append({
                'zone': zone,
                'distance': distance,
                'radius': zone['radius']
            })

    if not matching_zones:
        return None

    # Return the zone with the smallest radius (most specific)
    matching_zones.sort(key=lambda x: x['radius'])
    return matching_zones[0]['zone']


def cluster_people(people: List[Dict]) -> List[Dict]:
    """
    Cluster people who are within CLUSTER_DISTANCE meters of each other.
    Returns list of clusters with people and center coordinates.
    """
    if not people:
        return []

    # Filter out people without location
    people_with_location = [
        p for p in people
        if p.get('latitude') is not None and p.get('longitude') is not None
    ]

    if not people_with_location:
        return []

    # Track which people have been assigned to clusters
    assigned = set()
    clusters = []

    for person in people_with_location:
        if person['id'] in assigned:
            continue

        # Start a new cluster with this person
        cluster_members = [person]
        assigned.add(person['id'])

        # Find all nearby people
        for other in people_with_location:
            if other['id'] in assigned:
                continue

            distance = haversine_distance(
                person['latitude'], person['longitude'],
                other['latitude'], other['longitude']
            )

            if distance <= CLUSTER_DISTANCE:
                cluster_members.append(other)
                assigned.add(other['id'])

        # Calculate cluster center
        avg_lat = sum(m['latitude'] for m in cluster_members) / len(cluster_members)
        avg_lon = sum(m['longitude'] for m in cluster_members) / len(cluster_members)

        # Determine cluster zone (use the zone of the first person who has one)
        cluster_zone = None
        for member in cluster_members:
            if member.get('current_zone'):
                cluster_zone = member['current_zone']
                break

        clusters.append({
            'id': f"cluster_{len(clusters)}",
            'members': cluster_members,
            'center': {'latitude': avg_lat, 'longitude': avg_lon},
            'zone': cluster_zone,
            'count': len(cluster_members)
        })

    return clusters


def group_by_zone(clusters: List[Dict], zones: List[Dict]) -> Dict:
    """
    Group clusters by their detected zone for display.
    Returns a dictionary with zone names as keys.
    """
    grouped = {
        'office': [],
        'pub': [],
        'restaurant': [],
        'cafe': [],
        'gym': [],
        'unknown': []
    }

    zone_lookup = {z['name']: z for z in zones}

    for cluster in clusters:
        zone_name = cluster.get('zone')

        if zone_name and zone_name in zone_lookup:
            zone_type = zone_lookup[zone_name]['type']
            grouped[zone_type].append(cluster)
        else:
            grouped['unknown'].append(cluster)

    return grouped


def get_zone_color(zone_type: str) -> str:
    """Get the color associated with a zone type."""
    colors = {
        'office': '#22c55e',      # Green
        'restaurant': '#f97316',  # Orange
        'pub': '#a855f7',         # Purple
        'cafe': '#3b82f6',        # Blue
        'gym': '#ef4444',         # Red
        'unknown': '#6b7280'      # Gray
    }
    return colors.get(zone_type, colors['unknown'])
