#!/usr/bin/env python3
"""
Google Places Impact Analysis Pipeline
Complete pipeline in a single file for simplicity

Handles:
1. Configuration & Constants
2. Google Places API Search
3. Impact Categorization (no duplicates)
4. Gap Analysis & Statistics
5. Pipeline Orchestration

Usage:
    from google_places_pipeline import GooglePlacesPipeline
    pipeline = GooglePlacesPipeline(config, reporter)
    results = pipeline.run(address, radius)

Author: Google Places Analysis Pipeline
Date: 2025-10-04
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from geopy.distance import geodesic

from pipeline_utils import PipelineConfig, ProgressReporter, PipelineError, DataProcessor, FileManager


# ============================================================================
# SECTION 1: CONFIGURATION & CONSTANTS
# ============================================================================

class PlacesConfig:
    """Configuration for Google Places searches"""

    # Search parameters
    DEFAULT_RADIUS = 1500  # meters (deprecated - use LEVEL_RADII)
    API_RATE_LIMIT = 0.1   # seconds between requests

    # Radius configuration per level (in meters)
    LEVEL_RADII = {
        "Level_1_Impacts": 3000,   # 3km
        "Level_2_Impacts": 600,    # 600m
        "Level_3_Impacts": 250,    # 250m
        "Level_4_Impacts": 100     # 100m
    }

    # Google's 91 officially supported place types (from official docs)
    GOOGLE_SUPPORTED_TYPES = {
        "accounting", "airport", "amusement_park", "aquarium", "art_gallery",
        "atm", "bakery", "bank", "bar", "beauty_salon", "bicycle_store",
        "book_store", "bowling_alley", "bus_station", "cafe", "campground",
        "car_dealer", "car_rental", "car_repair", "car_wash", "casino",
        "cemetery", "church", "city_hall", "clothing_store", "convenience_store",
        "courthouse", "dentist", "department_store", "doctor", "drugstore",
        "electrician", "electronics_store", "embassy", "fire_station", "florist",
        "funeral_home", "furniture_store", "gas_station", "gym", "hair_care",
        "hardware_store", "hindu_temple", "home_goods_store", "hospital",
        "insurance_agency", "jewelry_store", "laundry", "lawyer", "library",
        "light_rail_station", "liquor_store", "local_government_office",
        "locksmith", "lodging", "meal_delivery", "meal_takeaway", "mosque",
        "movie_rental", "movie_theater", "moving_company", "museum", "night_club",
        "painter", "park", "parking", "pet_store", "pharmacy", "physiotherapist",
        "plumber", "police", "post_office", "primary_school", "real_estate_agency",
        "restaurant", "roofing_contractor", "rv_park", "school", "secondary_school",
        "shoe_store", "shopping_mall", "spa", "stadium", "storage", "store",
        "subway_station", "supermarket", "synagogue", "taxi_stand",
        "tourist_attraction", "train_station", "transit_station", "travel_agency",
        "university", "veterinary_care", "zoo"
    }

    # Property impact categories (Level 1/Level 2/Level 3)
    PROPERTY_IMPACTS = {
        # Level 1 - Disruptive if within 3km
        "Level_1_Impacts": {
            "Major Disruption": [
                "airport"
            ],
        },
        "Level_2_Impacts": {
        # Level 2 - Significant, flag if within 600km
            "Industrial & Environmental": [
                "car_wash", "car_repair", "storage",
                "waste_management", "recycling_center", "hardware_store",
                "home_improvement_store", "auto_parts_store"
            ],
            "Retail Noise": [
                "night_club", "bar", "casino", "bowling_alley",
                "movie_theater", "stadium", "karaoke", "pub",
                "wine_bar", "bar_and_grill"
            ],
        },
        "Level_3_Impacts": {
        # Level 3 - Moderately significant, flag if within 250km
            "Fuel": [
                "fuel_station", "gas_station", "petrol_station", "petrol", "fuel"
            ],
            "Child Care & Early Education": [
                "child_care_agency", "preschool"
            ],
            "Rail": [
                "train_station", "railway_station",
            ],        
            "Institutional": [
                "cemetery", "funeral_home", "courthouse", "police",
                "fire_station", "hospital"
            ],
            "Other Transit": [
                "bus_station", "subway_station",
                "taxi_stand", "transit_station", "parking",
                "bus_stop"
            ],
            "Retail Volume": [
                "shopping_mall", "liquor_store", "food_court"
            ],
            "Accommodation": [
                "lodging", "hotel", "bed_and_breakfast", "motel",
                "cottage", "resort_hotel", "inn", "private_guest_room",
                "guest_house", "extended_stay_hotel", "hostel"
            ],
            "Events & Venues": [
                "event_venue", "wedding_venue", "banquet_hall"
            ],
            "Care Facilities": [
                "aged_care", "nursing_home", "retirement_home", "care_community"
            ],
            "Government & Public Services": [
                "government_office", "local_government_office", "city_hall",
                "post_office"
            ],
            "Education": [
                "school", "primary_school", "secondary_school",
                "university", "library"
            ]
        },
        "Level_4_Impacts": {
            # Level 4 - Somewhat significant, flag if within 100km
            "Personal Services": [
                "hair_salon", "hair_care", "beauty_salon", "nail_salon",
                "barber_shop", "spa", "massage", "laundry", "beautician",
                "body_art_service", "foot_care", "sauna", "public_bath",
                "tanning_studio", "makeup_artist"
            ],
            "Professional Services": [
                "accounting", "lawyer", "consultant", "real_estate_agency",
                "insurance_agency", "electrician", "plumber", "roofing_contractor",
                "general_contractor", "finance", "painter"
            ],
            "Healthcare": [
                "doctor", "dentist", "dental_clinic", "medical_lab",
                "pharmacy", "drugstore", "physiotherapist",
                "veterinary_care", "chiropractor", "wellness_center",
                "skin_care_clinic"
            ],
            "Food Retail": [
                "bakery", "food_store", "grocery_store", "supermarket",
                "asian_grocery_store", "butcher_shop", "market", "candy_store",
                "chocolate_shop", "confectionery", "dessert_shop", "ice_cream_shop"
            ],
            "Other Retail": [
                "clothing_store", "shoe_store", "jewelry_store",
                "electronics_store", "pet_store", "florist", "gift_shop",
                "book_store", "home_goods_store", "furniture_store",
                "sporting_goods_store", "bicycle_store", "department_store",
                "cell_phone_store"
            ],
            "Quick Dining": [
                "cafe", "coffee_shop", "meal_takeaway", "meal_delivery",
                "food_delivery", "sandwich_shop", "cafeteria", "donut_shop",
                "breakfast_restaurant", "hamburger_restaurant", "diner"
            ],
            "Restaurants": [
                "restaurant", "american_restaurant", "mexican_restaurant",
                "italian_restaurant", "pizza_restaurant", "barbecue_restaurant",
                "fine_dining_restaurant", "vegan_restaurant", "vegetarian_restaurant",
                "chinese_restaurant", "asian_restaurant", "korean_restaurant",
                "indian_restaurant", "middle_eastern_restaurant", "steak_house",
                "buffet_restaurant", "dessert_restaurant"
            ],
            "Alternative Services": [
                "astrologer", "psychic"
            ],
            "Entertainment & Catering": [
                "catering_service"
            ],
            "Logistics & Wholesale": [
                "wholesaler", "courier_service", "moving_company"
            ],
            "Parks & Gardens": [
                "park", "playground", "garden", "picnic_ground",
                "botanical_garden", "farm"
            ],
            "Sports & Fitness": [
                "sports_activity_location", "sports_complex", "fitness_center",
                "gym", "yoga_studio", "sports_club", "athletic_field",
                "sports_coaching", "golf_course", "bowling_alley", "swimming_pool"
            ],
            "Community & Culture": [
                "church", "place_of_worship", "community_center",
                "tourist_attraction", "art_gallery", "museum",
                "historical_landmark", "tour_agency"
            ],
            "Convenience Shopping": [
                "supermarket", "grocery_store", "convenience_store",
                "atm", "bank"
            ],
            "Travel Services": ["travel_agency"]
        }
    }

    @classmethod
    def extract_all_types(cls) -> set:
        """Extract all unique place types from PROPERTY_IMPACTS"""
        all_types = set()
        for impact_level in cls.PROPERTY_IMPACTS.values():
            for category in impact_level.values():
                all_types.update(category)
        return all_types

    @classmethod
    def get_search_method(cls, place_type: str) -> str:
        """Determine if type uses searchNearby or searchText"""
        return "searchNearby" if place_type in cls.GOOGLE_SUPPORTED_TYPES else "searchText"


# ============================================================================
# SECTION 2: GOOGLE PLACES SEARCH
# ============================================================================

class GooglePlacesSearcher:
    """Handles comprehensive Google Places API searches"""

    def __init__(self, api_key: str, reporter: ProgressReporter):
        self.api_key = api_key
        self.reporter = reporter
        self.property_coords = None

    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Convert address to coordinates using Google Geocoding API"""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": self.api_key}

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise PipelineError(f"Geocoding failed: HTTP {response.status_code}")

        data = response.json()
        if data['status'] != 'OK':
            raise PipelineError(f"Geocoding failed: {data['status']}")

        location = data['results'][0]['geometry']['location']
        return (location['lat'], location['lng'])

    def search_nearby_batch(self, place_types: List[str], coords: Tuple[float, float], radius: int) -> List[dict]:
        """Search using searchNearby API with multiple types (batched)"""
        url = "https://places.googleapis.com/v1/places:searchNearby"

        # Filter to only Google-supported types for searchNearby
        supported_types = [pt for pt in place_types if pt in PlacesConfig.GOOGLE_SUPPORTED_TYPES]

        if not supported_types:
            return []

        payload = {
            "includedTypes": supported_types,
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": coords[0], "longitude": coords[1]},
                    "radius": float(radius)
                }
            }
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.displayName,places.location,places.types,places.formattedAddress'
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            self.reporter.warning(f"searchNearby batch failed: HTTP {response.status_code}")
            return []

        data = response.json()
        return data.get('places', [])

    def search_text_batch(self, place_types: List[str], coords: Tuple[float, float], radius: int) -> List[dict]:
        """
        Search using searchText API for non-Google-supported types
        Note: searchText doesn't support multiple types in one call, so we combine with OR
        """
        url = "https://places.googleapis.com/v1/places:searchText"

        # Create a combined query with all types
        query_terms = [pt.replace("_", " ") for pt in place_types]
        combined_query = " OR ".join(query_terms)

        payload = {
            "textQuery": combined_query,
            "locationBias": {
                "circle": {
                    "center": {"latitude": coords[0], "longitude": coords[1]},
                    "radius": float(radius)
                }
            },
            "maxResultCount": 20
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.displayName,places.location,places.types,places.formattedAddress'
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            self.reporter.warning(f"searchText batch failed: HTTP {response.status_code}")
            return []

        data = response.json()
        return data.get('places', [])

    def is_within_radius(self, place_coords: Tuple[float, float], radius: int) -> bool:
        """Check if place is within specified radius using geodesic distance"""
        distance_m = geodesic(self.property_coords, place_coords).meters
        return distance_m <= radius

    def search_all_nearby_no_filter(self, coords: Tuple[float, float], radius: int) -> List[dict]:
        """
        Search for ALL places within radius (Level 4 logic)
        No type filtering - just paginate through all results
        """
        url = "https://places.googleapis.com/v1/places:searchNearby"
        all_places = []

        payload = {
            "maxResultCount": 20,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": coords[0], "longitude": coords[1]},
                    "radius": float(radius)
                }
            }
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.displayName,places.location,places.types,places.formattedAddress'
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            self.reporter.warning(f"searchNearby (no filter) failed: HTTP {response.status_code}")
            return []

        data = response.json()
        all_places.extend(data.get('places', []))

        # TODO: Handle pagination if nextPageToken is provided
        # For now, return first 20 results
        return all_places

    def search_by_level(self, address: str) -> dict:
        """
        Main method: Search place types by level with different radii
        - Levels 1-3: Search specific types within level-specific radius
        - Level 4: Search ALL places within 100m (no type filtering)
        Returns data organized by level
        """
        api_calls = 0

        # Geocode property address
        self.reporter.info(f"Geocoding address: {address}")
        self.property_coords = self.geocode_address(address)
        self.reporter.success(f"Property coordinates: {self.property_coords[0]:.6f}, {self.property_coords[1]:.6f}")

        # Results organized by level
        results_by_level = {}

        # Process Levels 1-3 (specific type searches - BATCHED)
        for level in ["Level_1_Impacts", "Level_2_Impacts", "Level_3_Impacts"]:
            level_radius = PlacesConfig.LEVEL_RADII[level]
            self.reporter.info(f"Searching {level} (radius: {level_radius}m)...")

            level_places = {}  # {name: place_data}
            categories = PlacesConfig.PROPERTY_IMPACTS[level]

            # Extract all types for this level
            level_types = set()
            for category_types in categories.values():
                level_types.update(category_types)

            level_types_list = sorted(level_types)

            # Separate into Google-supported and non-supported types
            supported_types = [pt for pt in level_types_list if pt in PlacesConfig.GOOGLE_SUPPORTED_TYPES]
            unsupported_types = [pt for pt in level_types_list if pt not in PlacesConfig.GOOGLE_SUPPORTED_TYPES]

            # BATCH 1: Search all Google-supported types in ONE call
            if supported_types:
                self.reporter.info(f"  Searching {len(supported_types)} Google-supported types...")
                results = self.search_nearby_batch(supported_types, self.property_coords, level_radius)
                api_calls += 1

                # Filter by actual distance and deduplicate
                for place in results:
                    place_coords = (place['location']['latitude'], place['location']['longitude'])
                    if self.is_within_radius(place_coords, level_radius):
                        name = place['displayName']['text']
                        if name not in level_places:
                            level_places[name] = place

                self.reporter.info(f"  Found {len(results)} places from supported types")

            # BATCH 2: Search all non-supported types in ONE call (if any)
            if unsupported_types:
                self.reporter.info(f"  Searching {len(unsupported_types)} non-supported types via text search...")
                results = self.search_text_batch(unsupported_types, self.property_coords, level_radius)
                api_calls += 1

                # Filter by actual distance and deduplicate
                for place in results:
                    place_coords = (place['location']['latitude'], place['location']['longitude'])
                    if self.is_within_radius(place_coords, level_radius):
                        name = place['displayName']['text']
                        if name not in level_places:
                            level_places[name] = place

                self.reporter.info(f"  Found {len(results)} places from text search")

            time.sleep(PlacesConfig.API_RATE_LIMIT)

            results_by_level[level] = {
                "radius_meters": level_radius,
                "types_searched": level_types_list,
                "unique_places": list(level_places.values()),
                "unique_places_count": len(level_places)
            }
            self.reporter.success(f"{level}: {len(level_places)} unique places within {level_radius}m (from {api_calls} API calls so far)")

        # Process Level 4 (ALL places within 100m - no type filtering)
        level_4_radius = PlacesConfig.LEVEL_RADII["Level_4_Impacts"]
        self.reporter.info(f"Searching Level_4_Impacts (radius: {level_4_radius}m, no type filter)...")

        level_4_results = self.search_all_nearby_no_filter(self.property_coords, level_4_radius)
        api_calls += 1

        # Filter by actual distance
        level_4_places = {}
        for place in level_4_results:
            place_coords = (place['location']['latitude'], place['location']['longitude'])
            if self.is_within_radius(place_coords, level_4_radius):
                name = place['displayName']['text']
                if name not in level_4_places:
                    level_4_places[name] = place

        results_by_level["Level_4_Impacts"] = {
            "radius_meters": level_4_radius,
            "types_searched": ["ALL_TYPES"],
            "unique_places": list(level_4_places.values()),
            "unique_places_count": len(level_4_places)
        }
        self.reporter.success(f"Level_4_Impacts: {len(level_4_places)} unique places within {level_4_radius}m")

        return {
            "property_address": address,
            "property_coordinates": {"latitude": self.property_coords[0], "longitude": self.property_coords[1]},
            "timestamp": datetime.now().isoformat(),
            "api_calls_made": api_calls,
            "search_strategy": {
                "approach": "Batched searches per level for efficiency",
                "Level_1_Impacts": f"Batched type search within {PlacesConfig.LEVEL_RADII['Level_1_Impacts']}m (1-2 API calls)",
                "Level_2_Impacts": f"Batched type search within {PlacesConfig.LEVEL_RADII['Level_2_Impacts']}m (1-2 API calls)",
                "Level_3_Impacts": f"Batched type search within {PlacesConfig.LEVEL_RADII['Level_3_Impacts']}m (1-2 API calls)",
                "Level_4_Impacts": f"All places within {PlacesConfig.LEVEL_RADII['Level_4_Impacts']}m, no type filter (1 API call)"
            },
            "results_by_level": results_by_level
        }


# ============================================================================
# SECTION 3: IMPACT CATEGORIZATION (NO DUPLICATES)
# ============================================================================

class PlacesCategorizer:
    """Categorizes places into impact levels without duplication"""

    def __init__(self, reporter: ProgressReporter):
        self.reporter = reporter

    def categorize_places(self, search_results: dict) -> dict:
        """
        Categorize places by level and return ONLY the closest place per category
        Uses results from level-based search
        """
        prop_coords = (search_results['property_coordinates']['latitude'],
                      search_results['property_coordinates']['longitude'])

        categorized = {
            "Level_1_Impacts": {},
            "Level_2_Impacts": {},
            "Level_3_Impacts": {},
            "Level_4_Impacts": {}
        }

        total_categories = 0
        total_matches = 0

        # Process each level
        for level in ["Level_1_Impacts", "Level_2_Impacts", "Level_3_Impacts", "Level_4_Impacts"]:
            level_results = search_results['results_by_level'][level]
            all_places = level_results['unique_places']
            categories = PlacesConfig.PROPERTY_IMPACTS[level]

            # For each category, find the closest matching place
            for category_name, search_types in categories.items():
                matches = []

                for place in all_places:
                    place_types = place.get('types', [])

                    # Check if any of place's types match this category's search types
                    if any(ptype in search_types for ptype in place_types):
                        place_coords = (place['location']['latitude'], place['location']['longitude'])
                        distance = geodesic(prop_coords, place_coords).meters

                        matches.append({
                            'name': place['displayName']['text'],
                            'latitude': place_coords[0],
                            'longitude': place_coords[1],
                            'types': place_types,
                            'formatted_address': place.get('formattedAddress', 'Unknown'),
                            'distance_meters': round(distance, 1)
                        })

                # Sort by distance and keep ONLY the closest
                matches.sort(key=lambda x: x['distance_meters'])
                closest_place = matches[0] if matches else None

                categorized[level][category_name] = {
                    "searched_types": search_types,
                    "closest_place": closest_place,
                    "total_found": len(matches)
                }

                total_categories += 1
                if closest_place:
                    total_matches += 1

        self.reporter.success(f"Categorized {total_matches} categories with matches out of {total_categories} total categories")

        return {
            "property_address": search_results['property_address'],
            "property_coordinates": search_results['property_coordinates'],
            "timestamp": datetime.now().isoformat(),
            "level_radii": PlacesConfig.LEVEL_RADII,
            "impact_analysis": categorized,
            "summary": {
                "total_categories": total_categories,
                "categories_with_matches": total_matches,
                "categories_without_matches": total_categories - total_matches
            }
        }


# ============================================================================
# SECTION 4: GAP ANALYSIS & STATISTICS
# ============================================================================

class PlacesAnalyzer:
    """Generates statistics for the categorized results"""

    def __init__(self, reporter: ProgressReporter):
        self.reporter = reporter

    def generate_statistics(self, search_results: dict, impact_data: dict) -> dict:
        """Generate summary statistics by level"""

        # Count categories with/without matches per level
        level_stats = {}
        for level in ["Level_1_Impacts", "Level_2_Impacts", "Level_3_Impacts", "Level_4_Impacts"]:
            categories = impact_data['impact_analysis'][level]
            with_matches = sum(1 for cat in categories.values() if cat['closest_place'] is not None)
            total_cats = len(categories)

            level_stats[level] = {
                "radius_meters": PlacesConfig.LEVEL_RADII[level],
                "total_categories": total_cats,
                "categories_with_matches": with_matches,
                "categories_without_matches": total_cats - with_matches,
                "total_places_searched": search_results['results_by_level'][level]['unique_places_count']
            }

        # Collect all closest places for distance analysis
        all_closest = []
        for level in impact_data['impact_analysis'].values():
            for category in level.values():
                if category['closest_place']:
                    all_closest.append(category['closest_place'])

        # Distance distribution of closest places
        distances = [p['distance_meters'] for p in all_closest]
        distances.sort()

        return {
            "summary": impact_data['summary'],
            "level_statistics": level_stats,
            "closest_places_distance_distribution": {
                "total_closest_places": len(all_closest),
                "closest_m": round(distances[0], 1) if distances else 0,
                "furthest_m": round(distances[-1], 1) if distances else 0,
                "median_m": round(distances[len(distances)//2], 1) if distances else 0,
                "within_100m": sum(1 for d in distances if d <= 100),
                "within_250m": sum(1 for d in distances if d <= 250),
                "within_600m": sum(1 for d in distances if d <= 600),
                "within_3000m": sum(1 for d in distances if d <= 3000)
            }
        }


# ============================================================================
# SECTION 5: PIPELINE ORCHESTRATION
# ============================================================================

class GooglePlacesPipeline:
    """Main orchestrator for Google Places impact analysis"""

    def __init__(self, config: PipelineConfig, reporter: ProgressReporter):
        self.config = config
        self.reporter = reporter
        self.output_dir = Path(config.get("output_dir", "data/places_analysis"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, address: str) -> dict:
        """
        Execute complete pipeline with level-based searches

        Steps:
        1. Search by level (different radii per level)
        2. Categorize places (return closest per category)
        3. Generate statistics
        4. Save all outputs

        Returns: dict with output file paths
        """
        self.reporter.print_header()

        try:
            # STEP 1: Level-based Search
            self.reporter.print_step(1, "Level-Based Place Search")
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise PipelineError("GOOGLE_API_KEY not found in environment")

            searcher = GooglePlacesSearcher(api_key, self.reporter)
            search_results = searcher.search_by_level(address)

            search_file = DataProcessor.save_json(
                search_results,
                self.output_dir / "search_results_by_level.json",
                verbose=False
            )
            self.reporter.success(f"API calls made: {search_results['api_calls_made']}")
            self.reporter.success(f"Saved to: {search_file}")

            # STEP 2: Impact Categorization (closest place per category)
            self.reporter.print_step(2, "Impact Categorization (Closest per Category)")
            categorizer = PlacesCategorizer(self.reporter)
            impact_data = categorizer.categorize_places(search_results)

            impact_file = DataProcessor.save_json(
                impact_data,
                self.output_dir / "property_impacts.json",
                verbose=False
            )
            self.reporter.success(f"Saved to: {impact_file}")

            # STEP 3: Statistics
            self.reporter.print_step(3, "Generate Statistics")
            analyzer = PlacesAnalyzer(self.reporter)
            stats = analyzer.generate_statistics(search_results, impact_data)

            stats_file = DataProcessor.save_json(stats, self.output_dir / "statistics.json", verbose=False)
            self.reporter.success(f"Statistics saved to: {stats_file}")

            # Print summary
            self._print_summary(stats, impact_data)

            return {
                "search_results": search_file,
                "impacts": impact_file,
                "statistics": stats_file
            }

        except Exception as e:
            self.reporter.error(f"Pipeline failed: {str(e)}")
            raise PipelineError(f"GooglePlacesPipeline failed: {str(e)}") from e

    def _print_summary(self, stats: dict, impact_data: dict):
        """Print summary statistics"""
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        summary = stats['summary']
        print(f"\n📊 Total categories: {summary['total_categories']}")
        print(f"✅ Categories with matches: {summary['categories_with_matches']}")
        print(f"❌ Categories without matches: {summary['categories_without_matches']}")

        print(f"\n📍 Level Statistics:")
        for level, level_stats in stats['level_statistics'].items():
            print(f"\n  {level} (radius: {level_stats['radius_meters']}m):")
            print(f"    Categories: {level_stats['total_categories']}")
            print(f"    With matches: {level_stats['categories_with_matches']}")
            print(f"    Places searched: {level_stats['total_places_searched']}")

        print(f"\n📏 Closest Places Distance Distribution:")
        dist = stats['closest_places_distance_distribution']
        print(f"   Total closest places: {dist['total_closest_places']}")
        print(f"   Closest: {dist['closest_m']}m")
        print(f"   Furthest: {dist['furthest_m']}m")
        print(f"   Median: {dist['median_m']}m")
        print(f"   Within 100m: {dist['within_100m']}")
        print(f"   Within 250m: {dist['within_250m']}")
        print(f"   Within 600m: {dist['within_600m']}")
        print(f"   Within 3000m: {dist['within_3000m']}")


if __name__ == "__main__":
    # Quick test if run directly
    print("Google Places Pipeline - Use scripts/run_places_analysis.py to execute")
