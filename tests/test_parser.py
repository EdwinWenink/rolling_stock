#!/usr/bin/env python3
"""
Simple test to verify the parser works with sample XML data
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import gzip
from ndov_train_composition import TrainComposition, NDOVLoketParser, parse_materieel_aanduiding


def test_composition_class():
    """Test the TrainComposition class"""
    print("Testing TrainComposition class...")

    comp = TrainComposition()
    comp.train_number = "1234"
    comp.timestamp = "2026-06-19T12:00:00.000Z"
    comp.add_part("SLT", "6", "2345", units=1, coaches=6, length_cm=7500)
    comp.add_part("SLT", "4", "2346", units=1, coaches=4, length_cm=5000)
    comp.total_units = 2
    comp.total_coaches = 10
    comp.total_length_cm = 12500

    print(f"  {comp}")
    print(f"  Dict format: {comp.to_dict()}")
    print("  ✓ TrainComposition class works\n")


def test_aanduiding_parsing():
    """Test MaterieelAanduiding parsing"""
    print("Testing MaterieelAanduiding parsing...")

    test_cases = [
        ("6", 1, 6),
        ("4", 1, 4),
        ("2/6", 2, 6),
        ("2/8", 2, 8),
        ("3/12", 3, 12),
    ]

    all_passed = True
    for aanduiding, expected_units, expected_coaches in test_cases:
        units, coaches = parse_materieel_aanduiding(aanduiding)
        if units == expected_units and coaches == expected_coaches:
            print(f"  ✓ '{aanduiding}' -> {units} units, {coaches} coaches")
        else:
            print(f"  ✗ '{aanduiding}' -> got ({units}, {coaches}), expected ({expected_units}, {expected_coaches})")
            all_passed = False

    if all_passed:
        print("  ✓ MaterieelAanduiding parsing works\n")
    else:
        print("  ✗ Some aanduiding parsing tests failed\n")


def test_xml_parsing():
    """Test XML parsing with DVS format (DynamischeVertrekStaat)"""
    print("Testing DVS XML parsing...")

    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ns1:PutReisInformatieBoodschapIn xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
        xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4">
        <ns2:ReisInformatieProductDVS TimeStamp="2026-06-19T12:30:45.123Z">
            <ns2:DynamischeVertrekStaat>
                <ns2:Trein>
                    <ns2:TreinNummer>1234</ns2:TreinNummer>
                    <ns2:TreinVleugel>
                        <ns2:MaterieelDeelDVS>
                            <ns2:MaterieelSoort>SLT</ns2:MaterieelSoort>
                            <ns2:MaterieelAanduiding>6</ns2:MaterieelAanduiding>
                            <ns2:MaterieelLengte>7500</ns2:MaterieelLengte>
                        </ns2:MaterieelDeelDVS>
                        <ns2:MaterieelDeelDVS>
                            <ns2:MaterieelSoort>SLT</ns2:MaterieelSoort>
                            <ns2:MaterieelAanduiding>4</ns2:MaterieelAanduiding>
                            <ns2:MaterieelLengte>5000</ns2:MaterieelLengte>
                        </ns2:MaterieelDeelDVS>
                    </ns2:TreinVleugel>
                </ns2:Trein>
            </ns2:DynamischeVertrekStaat>
        </ns2:ReisInformatieProductDVS>
    </ns1:PutReisInformatieBoodschapIn>
    """

    parser = NDOVLoketParser()
    comp = parser.parse_materieelsamenstelling(sample_xml)

    if comp:
        print(f"  Parsed: {comp}")
        print(f"  Timestamp: {comp.timestamp}")
        print(f"  Total length: {comp.total_length_cm}cm ({comp.total_length_cm/100}m)")
        print("  ✓ DVS XML parsing works\n")
    else:
        print("  ✗ Failed to parse DVS sample XML\n")


def test_alternative_xml_format():
    """Test XML parsing with RIT format (RitInformatie)"""
    print("Testing RIT XML format...")

    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ns1:PutReisInformatieBoodschapIn xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
        xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4">
        <ns2:ReisInformatieProductRitInfo TimeStamp="2026-06-19T13:15:22.456Z">
            <ns2:RitInfo>
                <ns2:RitId>5678</ns2:RitId>
                <ns2:LogischeRitDeel>
                    <ns2:LogischeRitDeelStation>
                        <ns2:MaterieelDeel>
                            <ns2:MaterieelDeelSoort>VIRM</ns2:MaterieelDeelSoort>
                            <ns2:MaterieelDeelAanduiding>6</ns2:MaterieelDeelAanduiding>
                            <ns2:MaterieelDeelLengte>10860</ns2:MaterieelDeelLengte>
                            <ns2:MaterieelNummer>000000-09547-0</ns2:MaterieelNummer>
                        </ns2:MaterieelDeel>
                        <ns2:MaterieelDeel>
                            <ns2:MaterieelDeelSoort>VIRM</ns2:MaterieelDeelSoort>
                            <ns2:MaterieelDeelAanduiding>4</ns2:MaterieelDeelAanduiding>
                            <ns2:MaterieelDeelLengte>7240</ns2:MaterieelDeelLengte>
                            <ns2:MaterieelNummer>000000-09548-0</ns2:MaterieelNummer>
                        </ns2:MaterieelDeel>
                    </ns2:LogischeRitDeelStation>
                </ns2:LogischeRitDeel>
            </ns2:RitInfo>
        </ns2:ReisInformatieProductRitInfo>
    </ns1:PutReisInformatieBoodschapIn>
    """

    parser = NDOVLoketParser()
    comp = parser.parse_materieelsamenstelling(sample_xml)

    if comp:
        print(f"  Parsed: {comp}")
        print(f"  Timestamp: {comp.timestamp}")
        print(f"  Total length: {comp.total_length_cm}cm ({comp.total_length_cm/100}m)")
        print("  ✓ RIT XML format works\n")
    else:
        print("  ✗ Failed to parse RIT XML format\n")


def test_gzip_decompression():
    """Test gzip decompression of messages"""
    print("Testing gzip decompression...")

    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <ns1:PutReisInformatieBoodschapIn xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
        xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4">
        <ns2:ReisInformatieProductDVS TimeStamp="2026-06-19T14:45:33.789Z">
            <ns2:DynamischeVertrekStaat>
                <ns2:Trein>
                    <ns2:TreinNummer>9999</ns2:TreinNummer>
                    <ns2:TreinVleugel>
                        <ns2:MaterieelDeelDVS>
                            <ns2:MaterieelSoort>ICM</ns2:MaterieelSoort>
                            <ns2:MaterieelAanduiding>3</ns2:MaterieelAanduiding>
                            <ns2:MaterieelLengte>6800</ns2:MaterieelLengte>
                        </ns2:MaterieelDeelDVS>
                        <ns2:MaterieelDeelDVS>
                            <ns2:MaterieelSoort>ICM</ns2:MaterieelSoort>
                            <ns2:MaterieelAanduiding>4</ns2:MaterieelAanduiding>
                            <ns2:MaterieelLengte>9100</ns2:MaterieelLengte>
                        </ns2:MaterieelDeelDVS>
                    </ns2:TreinVleugel>
                </ns2:Trein>
            </ns2:DynamischeVertrekStaat>
        </ns2:ReisInformatieProductDVS>
    </ns1:PutReisInformatieBoodschapIn>
    """

    # Compress the XML like NDOVLoket does
    compressed = gzip.compress(sample_xml.encode('utf-8'))

    # Decompress it
    decompressed = gzip.decompress(compressed).decode('utf-8')

    parser = NDOVLoketParser()
    comp = parser.parse_materieelsamenstelling(decompressed)

    if comp:
        print(f"  Parsed from compressed: {comp}")
        print(f"  Timestamp: {comp.timestamp}")
        print("  ✓ Gzip decompression works\n")
    else:
        print("  ✗ Failed to parse decompressed XML\n")


if __name__ == "__main__":
    print("=" * 60)
    print("NDOVLoket Train Composition Parser - Unit Tests")
    print("=" * 60 + "\n")

    test_composition_class()
    test_aanduiding_parsing()
    test_xml_parsing()
    test_alternative_xml_format()
    test_gzip_decompression()

    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)
