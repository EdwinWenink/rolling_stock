#!/usr/bin/env python3
"""
NDOVLoket Train Composition Parser

This script connects to the NDOVLoket open data feed via ZeroMQ and parses
train composition (rolling stock) information from Dutch trains.

Data sources:
- InfoPlus RIT (Ritinformatie) - Train service information
- Train composition data includes materieelsoort, materieelaanduiding, and materieelnummer

ZeroMQ endpoint: tcp://pubsub.besteffort.ndovloket.nl:7664
Envelope topics:
- /RIG/InfoPlusRITInterface2 - Train services with composition data
- /RIG/InfoPlusDVSInterface4 - Departures
- /RIG/InfoPlusDASInterface4 - Arrivals

Note: Messages are gzip-compressed and automatically decompressed by this parser.
"""

import zmq
import gzip
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import json
import os
from pathlib import Path


class TrainComposition:
    """Represents a train composition (materieelsamenstelling)"""

    def __init__(self):
        self.train_number: Optional[str] = None
        self.timestamp: Optional[str] = None
        self.composition_parts: List[Dict[str, str]] = []
        self.total_coaches: int = 0
        self.total_units: int = 0
        self.total_length_cm: int = 0
        self.vehicle_types: List[str] = []

    def add_part(self, vehicle_type: str, designation: str, number: Optional[str] = None,
                 units: int = 1, coaches: int = 0, length_cm: Optional[int] = None):
        """
        Add a rolling stock part to the composition

        Args:
            vehicle_type: Type of rolling stock (e.g., "SLT", "VIRM")
            designation: MaterieelAanduiding (e.g., "6", "2/6")
            number: MaterieelNummer (optional unit number)
            units: Number of trainset units (treinstellen)
            coaches: Number of car bodies (wagenkasten)
            length_cm: Length in centimeters (MaterieelLengte or MaterieelDeelLengte)
        """
        part = {
            'type': vehicle_type,
            'designation': designation,
            'number': number,
            'units': units,
            'coaches': coaches,
            'length_cm': length_cm
        }
        self.composition_parts.append(part)
        self.vehicle_types.append(vehicle_type)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'train_number': self.train_number,
            'timestamp': self.timestamp,
            'total_coaches': self.total_coaches,
            'total_units': self.total_units,
            'total_length_cm': self.total_length_cm,
            'composition_parts': self.composition_parts,
            'vehicle_types': list(set(self.vehicle_types))
        }

    def __str__(self) -> str:
        parts_str = "; ".join([f"{p['type']} {p['designation']}" for p in self.composition_parts])
        length_m = self.total_length_cm / 100 if self.total_length_cm > 0 else 0
        return f"Train {self.train_number}: {parts_str} ({self.total_units} units, {self.total_coaches} coaches, {length_m:.1f}m)"


def parse_materieel_aanduiding(aanduiding: str) -> tuple[int, int]:
    """
    Parse MaterieelAanduiding to extract units and coaches.

    Format: "units/coaches" or just "coaches"
    Examples:
        "6" -> (1, 6)       # Single unit with 6 coaches
        "2/6" -> (2, 6)     # 2 units with 6 coaches total
        "2/8" -> (2, 8)     # 2 units with 8 coaches total

    Args:
        aanduiding: MaterieelAanduiding string

    Returns:
        Tuple of (units, coaches)
    """
    if not aanduiding:
        return (0, 0)

    try:
        if '/' in aanduiding:
            # Format: "2/6" = 2 units, 6 coaches
            parts = aanduiding.split('/')
            units = int(''.join(filter(str.isdigit, parts[0])))
            coaches = int(''.join(filter(str.isdigit, parts[1])))
            return (units, coaches)
        else:
            # Format: "6" = single unit with 6 coaches
            coaches = int(''.join(filter(str.isdigit, aanduiding)))
            return (1, coaches)
    except (ValueError, IndexError):
        return (0, 0)


class NDOVLoketParser:
    """Parser for NDOVLoket train composition data"""

    def __init__(self, endpoint: str = "tcp://pubsub.besteffort.ndovloket.nl:7664"):
        self.endpoint = endpoint
        self.context = None
        self.socket = None

    def connect(self, topics: List[str] = None):
        """Connect to ZeroMQ endpoint and subscribe to topics"""
        if topics is None:
            topics = [
                "/RIG/InfoPlusRITInterface2",  # Train services
                "/RIG/InfoPlusDVSInterface4",  # Departures
                "/RIG/InfoPlusDASInterface4"   # Arrivals
            ]

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.endpoint)

        for topic in topics:
            print(f"Subscribing to: {topic}")
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

        print(f"Connected to {self.endpoint}")

    def disconnect(self):
        """Close ZeroMQ connection"""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()

    def parse_materieelsamenstelling(self, xml_string: str, debug=False) -> Optional[TrainComposition]:
        """
        Parse materieelsamenstelling from XML message

        Expected format examples:
        - "SLT 6;SLT 4" (two parts: SLT 6-coach and SLT 4-coach)
        - "ICM-3;ICM-4"
        """
        try:
            root = ET.fromstring(xml_string)
            composition = TrainComposition()

            # Define namespace (InfoPlus uses namespaces)
            ns = {'ns2': 'urn:ndov:cdm:trein:reisinformatie:data:4'}

            # Parse train number (TreinNummer or RitId)
            train_number = root.find('.//ns2:TreinNummer', ns) or root.find('.//ns2:RitId', ns)
            if train_number is not None and train_number.text:
                composition.train_number = train_number.text

            # Parse timestamp - TimeStamp is at the product level (ReisInformatieProductDVS/@TimeStamp)
            # First try the attribute on the product element
            product_dvs = root.find('.//ns2:ReisInformatieProductDVS', ns)
            product_rit = root.find('.//ns2:ReisInformatieProductRitInfo', ns)
            product_das = root.find('.//ns2:ReisInformatieProductDAS', ns)

            if product_dvs is not None and product_dvs.get('TimeStamp'):
                composition.timestamp = product_dvs.get('TimeStamp')
            elif product_rit is not None and product_rit.get('TimeStamp'):
                composition.timestamp = product_rit.get('TimeStamp')
            elif product_das is not None and product_das.get('TimeStamp'):
                composition.timestamp = product_das.get('TimeStamp')
            else:
                # Fallback: try to find TimeStamp or RitDatum element
                timestamp = root.find('.//ns2:TimeStamp', ns) or root.find('.//ns2:RitDatum', ns)
                if timestamp is not None and timestamp.text:
                    composition.timestamp = timestamp.text

            # Parse materieelsamenstelling from DVS messages (DynamischeVertrekStaat)
            # DVS: MaterieelDeelDVS with MaterieelSoort and MaterieelAanduiding
            for materieel_deel in root.findall('.//ns2:MaterieelDeelDVS', ns):
                materieel_soort = materieel_deel.find('ns2:MaterieelSoort', ns)
                materieel_aanduiding = materieel_deel.find('ns2:MaterieelAanduiding', ns)
                materieel_nummer = materieel_deel.find('ns2:MaterieelNummer', ns)
                materieel_lengte = materieel_deel.find('ns2:MaterieelLengte', ns)

                if materieel_soort is not None and materieel_soort.text:
                    aanduiding_text = materieel_aanduiding.text if materieel_aanduiding is not None else ""
                    units, coaches = parse_materieel_aanduiding(aanduiding_text)

                    # Parse length in centimeters
                    length_cm = None
                    if materieel_lengte is not None and materieel_lengte.text:
                        try:
                            length_cm = int(materieel_lengte.text)
                        except ValueError:
                            pass

                    composition.add_part(
                        vehicle_type=materieel_soort.text,
                        designation=aanduiding_text,
                        number=materieel_nummer.text if materieel_nummer is not None else None,
                        units=units,
                        coaches=coaches,
                        length_cm=length_cm
                    )

                    composition.total_units += units
                    composition.total_coaches += coaches
                    if length_cm:
                        composition.total_length_cm += length_cm

            # Parse materieelsamenstelling from RIT messages (Service/RitInfo)
            # RIT: MaterieelDeel with MaterieelDeelSoort and MaterieelDeelAanduiding
            for materieel_deel in root.findall('.//ns2:MaterieelDeel', ns):
                materieel_soort = materieel_deel.find('ns2:MaterieelDeelSoort', ns)
                materieel_aanduiding = materieel_deel.find('ns2:MaterieelDeelAanduiding', ns)
                materieel_nummer = materieel_deel.find('ns2:MaterieelNummer', ns)
                materieel_lengte = materieel_deel.find('ns2:MaterieelDeelLengte', ns)

                if materieel_soort is not None and materieel_soort.text:
                    aanduiding_text = materieel_aanduiding.text if materieel_aanduiding is not None else ""
                    units, coaches = parse_materieel_aanduiding(aanduiding_text)

                    # Parse length in centimeters
                    length_cm = None
                    if materieel_lengte is not None and materieel_lengte.text:
                        try:
                            length_cm = int(materieel_lengte.text)
                        except ValueError:
                            pass

                    composition.add_part(
                        vehicle_type=materieel_soort.text,
                        designation=aanduiding_text,
                        number=materieel_nummer.text if materieel_nummer is not None else None,
                        units=units,
                        coaches=coaches,
                        length_cm=length_cm
                    )

                    composition.total_units += units
                    composition.total_coaches += coaches
                    if length_cm:
                        composition.total_length_cm += length_cm

            if composition.composition_parts:
                return composition
            return None

        except ET.ParseError as e:
            if debug:
                print(f"  XML Parse Error: {e}")
            return None
        except Exception as e:
            if debug:
                print(f"  Error parsing composition: {e}")
            return None

    def receive_messages(self, callback=None, max_messages: Optional[int] = None, debug=False):
        """
        Receive and process messages from ZeroMQ feed

        Args:
            callback: Optional function to call with each parsed TrainComposition
            max_messages: Maximum number of messages to process (None = infinite)
            debug: If True, save raw XML messages for debugging
        """
        count = 0
        composition_count = 0

        try:
            while max_messages is None or count < max_messages:
                multipart = self.socket.recv_multipart()

                if len(multipart) >= 2:
                    envelope = multipart[0].decode('utf-8')

                    # Decompress gzip-compressed message
                    try:
                        xml_message = gzip.decompress(multipart[1]).decode('utf-8')
                    except gzip.BadGzipFile:
                        # Try without decompression (some messages might not be compressed)
                        xml_message = multipart[1].decode('utf-8')

                    print(f"\n[{datetime.now()}] Message {count + 1} on: {envelope}")

                    if debug:
                        # Save raw XML for debugging to data directory
                        os.makedirs('data', exist_ok=True)
                        debug_file = f"data/debug_message_{count + 1}.xml"
                        with open(debug_file, 'w') as f:
                            f.write(xml_message)
                        print(f"  Saved to {debug_file}")

                    composition = self.parse_materieelsamenstelling(xml_message, debug=debug)

                    if composition:
                        composition_count += 1
                        print(f"  ✓ Composition #{composition_count}: {composition}")

                        if callback:
                            callback(composition)
                    else:
                        print(f"  - No composition data in this message")

                    count += 1

            print(f"\nProcessed {count} messages, found {composition_count} with composition data")

        except KeyboardInterrupt:
            print("\nStopped by user")
        except Exception as e:
            print(f"Error receiving messages: {e}")


def save_to_json(composition: TrainComposition, filename: str = "output/train_compositions.json"):
    """Save train composition to JSON file"""
    try:
        # Ensure output directory exists
        output_dir = Path(filename).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append(composition.to_dict())

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(f"Error saving to JSON: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse train composition data from NDOVLoket'
    )
    parser.add_argument(
        '--endpoint',
        default='tcp://pubsub.besteffort.ndovloket.nl:7664',
        help='ZeroMQ endpoint (default: tcp://pubsub.besteffort.ndovloket.nl:7664)'
    )
    parser.add_argument(
        '--max-messages',
        type=int,
        default=None,
        help='Maximum number of messages to process (default: unlimited)'
    )
    parser.add_argument(
        '--output',
        default='output/train_compositions.json',
        help='Output JSON file (default: output/train_compositions.json)'
    )
    parser.add_argument(
        '--topics',
        nargs='+',
        default=None,
        help='ZeroMQ topics to subscribe to (default: all RIG topics)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Save raw XML messages for debugging'
    )

    args = parser.parse_args()

    ndov = NDOVLoketParser(endpoint=args.endpoint)

    try:
        ndov.connect(topics=args.topics)

        # Callback to save each composition to JSON
        callback = lambda comp: save_to_json(comp, args.output)

        print(f"\nListening for train composition data...")
        print(f"Output will be saved to: {args.output}")
        if args.debug:
            print(f"Debug mode: Raw XML will be saved to debug_message_*.xml files")
        print(f"Press Ctrl+C to stop\n")

        ndov.receive_messages(callback=callback, max_messages=args.max_messages, debug=args.debug)

    finally:
        ndov.disconnect()
        print("\nConnection closed")


if __name__ == "__main__":
    main()
