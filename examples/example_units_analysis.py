#!/usr/bin/env python3
"""
Example: Analyzing trainset units vs. car bodies

This example demonstrates how to work with the units (treinstellen) and
coaches (wagenkasten) data extracted from NDOVLoket.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ndov_train_composition import NDOVLoketParser
import json


def analyze_units_vs_coaches():
    """Collect and analyze the relationship between units and coaches"""
    print("=== Analyzing Trainset Units vs. Car Bodies ===\n")

    stats = {
        'single_unit_trains': 0,      # Trains with only 1 unit total
        'multi_unit_trains': 0,        # Trains with 2+ units
        'articulated_parts': 0,        # Parts with "X/Y" designation
        'unit_to_coach_ratios': {},    # Track common unit:coach ratios
    }

    compositions = []

    def analyze_composition(comp):
        """Analyze each composition"""
        compositions.append(comp.to_dict())

        # Count single vs multi-unit trains
        if comp.total_units == 1:
            stats['single_unit_trains'] += 1
        else:
            stats['multi_unit_trains'] += 1

        # Analyze each part
        for part in comp.composition_parts:
            # Track articulated trainsets (designation with slash)
            if '/' in part['designation']:
                stats['articulated_parts'] += 1

            # Track unit:coach ratios
            units = part['units']
            coaches = part['coaches']
            if units > 0 and coaches > 0:
                ratio = f"{units}:{coaches}"
                stats['unit_to_coach_ratios'][ratio] = stats['unit_to_coach_ratios'].get(ratio, 0) + 1

    parser = NDOVLoketParser()

    try:
        parser.connect()
        print("Collecting train composition data...\n")
        parser.receive_messages(callback=analyze_composition, max_messages=100)

        # Print statistics
        print("\n" + "=" * 60)
        print("ANALYSIS RESULTS")
        print("=" * 60 + "\n")

        total_trains = stats['single_unit_trains'] + stats['multi_unit_trains']

        if total_trains > 0:
            print(f"Total trains analyzed: {total_trains}")
            print(f"  Single-unit trains: {stats['single_unit_trains']} ({stats['single_unit_trains']/total_trains*100:.1f}%)")
            print(f"  Multi-unit trains: {stats['multi_unit_trains']} ({stats['multi_unit_trains']/total_trains*100:.1f}%)")
            print(f"\nArticulated trainset parts (X/Y format): {stats['articulated_parts']}")

            print("\nCommon unit:coach ratios:")
            for ratio, count in sorted(stats['unit_to_coach_ratios'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {ratio} - {count} occurrences")

            # Show some examples
            print("\n" + "=" * 60)
            print("EXAMPLE COMPOSITIONS")
            print("=" * 60 + "\n")

            # Find interesting examples
            single_unit_examples = [c for c in compositions if c['total_units'] == 1]
            multi_unit_examples = [c for c in compositions if c['total_units'] > 1]
            articulated_examples = [c for c in compositions if any('/' in p['designation'] for p in c['composition_parts'])]

            if single_unit_examples:
                comp = single_unit_examples[0]
                print("Single-unit train example:")
                print(f"  Train {comp['train_number']}: {comp['total_units']} unit, {comp['total_coaches']} coaches")
                for part in comp['composition_parts']:
                    print(f"    - {part['type']} {part['designation']}")
                print()

            if multi_unit_examples:
                comp = multi_unit_examples[0]
                print("Multi-unit train example:")
                print(f"  Train {comp['train_number']}: {comp['total_units']} units, {comp['total_coaches']} coaches")
                for part in comp['composition_parts']:
                    print(f"    - {part['type']} {part['designation']} ({part['units']} units, {part['coaches']} coaches)")
                print()

            if articulated_examples:
                comp = articulated_examples[0]
                print("Articulated trainset example:")
                print(f"  Train {comp['train_number']}: {comp['total_units']} units, {comp['total_coaches']} coaches")
                for part in comp['composition_parts']:
                    print(f"    - {part['type']} {part['designation']} ({part['units']} units, {part['coaches']} coaches)")
                print()

            # Save detailed results
            with open('output/units_analysis.json', 'w') as f:
                json.dump({
                    'statistics': stats,
                    'examples': {
                        'single_unit': single_unit_examples[:3],
                        'multi_unit': multi_unit_examples[:3],
                        'articulated': articulated_examples[:3]
                    }
                }, f, indent=2)

            print("Detailed analysis saved to units_analysis.json")

        else:
            print("No train compositions found in the collected messages.")
            print("Try running with --max-messages 200 or during peak hours.")

    finally:
        parser.disconnect()


if __name__ == "__main__":
    analyze_units_vs_coaches()
