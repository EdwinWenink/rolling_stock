#!/usr/bin/env python3
"""
Example usage of the NDOVLoket Train Composition Parser

This script demonstrates different ways to use the parser programmatically.
"""

from ndov_train_composition import NDOVLoketParser, TrainComposition
import json


def example_1_basic_usage():
    """Basic usage: connect and print compositions"""
    print("=== Example 1: Basic Usage ===\n")

    parser = NDOVLoketParser()

    try:
        parser.connect()
        print("Receiving 10 messages...\n")
        parser.receive_messages(max_messages=10)
    finally:
        parser.disconnect()


def example_2_custom_callback():
    """Custom callback to process compositions"""
    print("\n=== Example 2: Custom Callback ===\n")

    compositions_by_type = {}

    def analyze_composition(composition: TrainComposition):
        """Analyze and categorize compositions by vehicle type"""
        for vtype in composition.vehicle_types:
            if vtype not in compositions_by_type:
                compositions_by_type[vtype] = []
            compositions_by_type[vtype].append(composition.to_dict())

        print(f"Processed train {composition.train_number}: {', '.join(composition.vehicle_types)}")

    parser = NDOVLoketParser()

    try:
        parser.connect(topics=["/RIG/InfoPlusRITInterface2"])
        parser.receive_messages(callback=analyze_composition, max_messages=20)

        print("\n--- Summary by Vehicle Type ---")
        for vtype, comps in compositions_by_type.items():
            print(f"{vtype}: {len(comps)} trains")

    finally:
        parser.disconnect()


def example_3_filter_by_coaches():
    """Filter trains by number of coaches"""
    print("\n=== Example 3: Filter by Coach Count ===\n")

    long_trains = []

    def filter_long_trains(composition: TrainComposition):
        """Only save trains with 8 or more coaches"""
        if composition.total_coaches >= 8:
            long_trains.append(composition.to_dict())
            print(f"Long train found: {composition}")

    parser = NDOVLoketParser()

    try:
        parser.connect()
        print("Looking for trains with 8+ coaches...\n")
        parser.receive_messages(callback=filter_long_trains, max_messages=50)

        print(f"\nFound {len(long_trains)} long trains")

        with open('long_trains.json', 'w') as f:
            json.dump(long_trains, f, indent=2)
            print(f"Saved to long_trains.json")

    finally:
        parser.disconnect()


def example_4_statistics():
    """Collect statistics about train compositions"""
    print("\n=== Example 4: Composition Statistics ===\n")

    stats = {
        'total_trains': 0,
        'total_coaches': 0,
        'vehicle_type_counts': {},
        'trains_by_coach_count': {}
    }

    def collect_stats(composition: TrainComposition):
        """Collect various statistics"""
        stats['total_trains'] += 1
        stats['total_coaches'] += composition.total_coaches

        for vtype in composition.vehicle_types:
            stats['vehicle_type_counts'][vtype] = stats['vehicle_type_counts'].get(vtype, 0) + 1

        coach_count = composition.total_coaches
        stats['trains_by_coach_count'][coach_count] = stats['trains_by_coach_count'].get(coach_count, 0) + 1

    parser = NDOVLoketParser()

    try:
        parser.connect()
        print("Collecting statistics from 100 messages...\n")
        parser.receive_messages(callback=collect_stats, max_messages=100)

        print("\n--- Statistics ---")
        print(f"Total trains: {stats['total_trains']}")
        print(f"Total coaches: {stats['total_coaches']}")

        if stats['total_trains'] > 0:
            avg_coaches = stats['total_coaches'] / stats['total_trains']
            print(f"Average coaches per train: {avg_coaches:.1f}")

        print("\nVehicle types:")
        for vtype, count in sorted(stats['vehicle_type_counts'].items()):
            print(f"  {vtype}: {count}")

        print("\nTrains by coach count:")
        for coaches, count in sorted(stats['trains_by_coach_count'].items()):
            print(f"  {coaches} coaches: {count} trains")

        with open('train_statistics.json', 'w') as f:
            json.dump(stats, f, indent=2)
            print(f"\nStatistics saved to train_statistics.json")

    finally:
        parser.disconnect()


def example_5_specific_train_type():
    """Monitor for a specific train type"""
    print("\n=== Example 5: Monitor Specific Train Type ===\n")

    target_type = "VIRM"  # Change this to any type you're interested in
    matching_trains = []

    def find_specific_type(composition: TrainComposition):
        """Find trains with specific vehicle type"""
        if target_type in composition.vehicle_types:
            matching_trains.append(composition.to_dict())
            print(f"Found {target_type}: {composition}")

    parser = NDOVLoketParser()

    try:
        parser.connect()
        print(f"Looking for trains with {target_type} rolling stock...\n")
        parser.receive_messages(callback=find_specific_type, max_messages=100)

        print(f"\nFound {len(matching_trains)} trains with {target_type}")

        if matching_trains:
            filename = f'{target_type.lower()}_trains.json'
            with open(filename, 'w') as f:
                json.dump(matching_trains, f, indent=2)
                print(f"Saved to {filename}")

    finally:
        parser.disconnect()


if __name__ == "__main__":
    import sys

    examples = {
        '1': ('Basic usage', example_1_basic_usage),
        '2': ('Custom callback', example_2_custom_callback),
        '3': ('Filter by coach count', example_3_filter_by_coaches),
        '4': ('Statistics collection', example_4_statistics),
        '5': ('Monitor specific train type', example_5_specific_train_type),
    }

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num in examples:
            examples[example_num][1]()
        else:
            print(f"Unknown example: {example_num}")
            print(f"Available examples: {', '.join(examples.keys())}")
    else:
        print("Available examples:")
        for num, (desc, _) in examples.items():
            print(f"  {num}: {desc}")
        print(f"\nUsage: python {sys.argv[0]} <example_number>")
        print(f"Example: python {sys.argv[0]} 1")
