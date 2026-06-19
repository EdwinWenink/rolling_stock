"""
Pytest tests for NDOVLoket train composition parser
"""

import pytest
import gzip
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ndov_train_composition import parse_materieel_aanduiding


class TestTrainComposition:
    """Tests for TrainComposition class"""

    def test_composition_attributes(self, sample_composition):
        """Test that composition has correct attributes"""
        assert sample_composition.train_number == "1234"
        assert sample_composition.timestamp == "2026-06-19T12:00:00.000Z"
        assert sample_composition.total_units == 2
        assert sample_composition.total_coaches == 10
        assert sample_composition.total_length_cm == 12500

    def test_composition_parts(self, sample_composition):
        """Test that composition parts are stored correctly"""
        assert len(sample_composition.composition_parts) == 2

        part1 = sample_composition.composition_parts[0]
        assert part1['type'] == 'SLT'
        assert part1['designation'] == '6'
        assert part1['units'] == 1
        assert part1['coaches'] == 6
        assert part1['length_cm'] == 7500

    def test_composition_to_dict(self, sample_composition):
        """Test conversion to dictionary"""
        result = sample_composition.to_dict()

        assert result['train_number'] == "1234"
        assert result['total_units'] == 2
        assert result['total_coaches'] == 10
        assert result['total_length_cm'] == 12500
        assert 'composition_parts' in result
        assert 'vehicle_types' in result
        assert 'SLT' in result['vehicle_types']

    def test_composition_str(self, sample_composition):
        """Test string representation"""
        result = str(sample_composition)

        assert "Train 1234" in result
        assert "2 units" in result
        assert "10 coaches" in result
        assert "125.0m" in result
        assert "SLT 6" in result
        assert "SLT 4" in result


class TestMaterieelAanduidingParsing:
    """Tests for parsing MaterieelAanduiding format"""

    def test_aanduiding_parsing(self, aanduiding_test_cases):
        """Test parsing of various aanduiding formats"""
        for aanduiding, expected_units, expected_coaches in aanduiding_test_cases:
            units, coaches = parse_materieel_aanduiding(aanduiding)
            assert units == expected_units, f"Failed for {aanduiding}: units"
            assert coaches == expected_coaches, f"Failed for {aanduiding}: coaches"

    @pytest.mark.parametrize("aanduiding,expected_units,expected_coaches", [
        ("6", 1, 6),
        ("4", 1, 4),
        ("2/6", 2, 6),
        ("2/8", 2, 8),
        ("3/12", 3, 12),
    ])
    def test_aanduiding_parametrized(self, aanduiding, expected_units, expected_coaches):
        """Parametrized test for aanduiding parsing"""
        units, coaches = parse_materieel_aanduiding(aanduiding)
        assert units == expected_units
        assert coaches == expected_coaches

    def test_empty_aanduiding(self):
        """Test parsing empty aanduiding"""
        units, coaches = parse_materieel_aanduiding("")
        assert units == 0
        assert coaches == 0

    def test_none_aanduiding(self):
        """Test parsing None aanduiding"""
        units, coaches = parse_materieel_aanduiding(None)
        assert units == 0
        assert coaches == 0


class TestDVSParsing:
    """Tests for DVS (DynamischeVertrekStaat) XML parsing"""

    def test_parse_dvs_sample(self, parser, dvs_sample_xml):
        """Test parsing DVS sample XML"""
        comp = parser.parse_materieelsamenstelling(dvs_sample_xml)

        assert comp is not None
        assert comp.train_number == "1234"
        assert comp.timestamp == "2026-06-19T12:30:45.123Z"
        assert comp.total_units == 2
        assert comp.total_coaches == 10
        assert comp.total_length_cm == 12500

    def test_dvs_composition_parts(self, parser, dvs_sample_xml):
        """Test that DVS composition parts are parsed correctly"""
        comp = parser.parse_materieelsamenstelling(dvs_sample_xml)

        assert len(comp.composition_parts) == 2

        # Check first part
        part1 = comp.composition_parts[0]
        assert part1['type'] == 'SLT'
        assert part1['designation'] == '6'
        assert part1['units'] == 1
        assert part1['coaches'] == 6
        assert part1['length_cm'] == 7500

        # Check second part
        part2 = comp.composition_parts[1]
        assert part2['type'] == 'SLT'
        assert part2['designation'] == '4'
        assert part2['units'] == 1
        assert part2['coaches'] == 4
        assert part2['length_cm'] == 5000


class TestRITParsing:
    """Tests for RIT (RitInformatie) XML parsing"""

    def test_parse_rit_sample(self, parser, rit_sample_xml):
        """Test parsing RIT sample XML"""
        comp = parser.parse_materieelsamenstelling(rit_sample_xml)

        assert comp is not None
        assert comp.train_number == "5678"
        assert comp.timestamp == "2026-06-19T13:15:22.456Z"
        assert comp.total_units == 2
        assert comp.total_coaches == 10
        assert comp.total_length_cm == 18100

    def test_rit_composition_parts(self, parser, rit_sample_xml):
        """Test that RIT composition parts are parsed correctly"""
        comp = parser.parse_materieelsamenstelling(rit_sample_xml)

        assert len(comp.composition_parts) == 2

        # Check vehicle types
        assert comp.vehicle_types == ['VIRM', 'VIRM']

        # Check first part has unit number
        part1 = comp.composition_parts[0]
        assert part1['number'] == '000000-09547-0'
        assert part1['length_cm'] == 10860


class TestArticulatedTrainsets:
    """Tests for articulated trainsets (X/Y format)"""

    def test_parse_gtw_articulated(self, parser, gtw_articulated_xml):
        """Test parsing GTW articulated trainset"""
        comp = parser.parse_materieelsamenstelling(gtw_articulated_xml)

        assert comp is not None
        assert comp.train_number == "32278"
        assert comp.total_units == 4  # 2 + 2
        assert comp.total_coaches == 14  # 6 + 8
        assert comp.total_length_cm == 9700  # 4100 + 5600

    def test_gtw_parts_have_slash_designation(self, parser, gtw_articulated_xml):
        """Test that GTW parts have slash format designation"""
        comp = parser.parse_materieelsamenstelling(gtw_articulated_xml)

        part1 = comp.composition_parts[0]
        assert part1['designation'] == '2/6'
        assert part1['units'] == 2
        assert part1['coaches'] == 6

        part2 = comp.composition_parts[1]
        assert part2['designation'] == '2/8'
        assert part2['units'] == 2
        assert part2['coaches'] == 8


class TestGzipDecompression:
    """Tests for gzip decompression of messages"""

    def test_decompress_dvs(self, parser, dvs_sample_xml):
        """Test parsing gzip-compressed DVS message"""
        # Compress the XML
        compressed = gzip.compress(dvs_sample_xml.encode('utf-8'))

        # Decompress and parse
        decompressed = gzip.decompress(compressed).decode('utf-8')
        comp = parser.parse_materieelsamenstelling(decompressed)

        assert comp is not None
        assert comp.train_number == "1234"
        assert comp.timestamp == "2026-06-19T12:30:45.123Z"

    def test_decompress_rit(self, parser, rit_sample_xml):
        """Test parsing gzip-compressed RIT message"""
        compressed = gzip.compress(rit_sample_xml.encode('utf-8'))
        decompressed = gzip.decompress(compressed).decode('utf-8')
        comp = parser.parse_materieelsamenstelling(decompressed)

        assert comp is not None
        assert comp.train_number == "5678"


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_empty_xml(self, parser):
        """Test parsing empty XML returns None"""
        result = parser.parse_materieelsamenstelling("")
        assert result is None

    def test_invalid_xml(self, parser):
        """Test parsing invalid XML returns None"""
        result = parser.parse_materieelsamenstelling("not xml")
        assert result is None

    def test_xml_without_composition(self, parser):
        """Test parsing XML without composition data returns None"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <ns1:PutReisInformatieBoodschapIn xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
            xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4">
            <ns2:ReisInformatieProductDVS TimeStamp="2026-06-19T12:00:00.000Z">
                <ns2:DynamischeVertrekStaat>
                    <ns2:Trein>
                        <ns2:TreinNummer>9999</ns2:TreinNummer>
                    </ns2:Trein>
                </ns2:DynamischeVertrekStaat>
            </ns2:ReisInformatieProductDVS>
        </ns1:PutReisInformatieBoodschapIn>
        """
        result = parser.parse_materieelsamenstelling(xml)
        assert result is None
