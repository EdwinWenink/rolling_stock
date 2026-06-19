"""
Pytest configuration and fixtures for NDOVLoket parser tests
"""

import pytest
import gzip
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ndov_train_composition import NDOVLoketParser, TrainComposition


@pytest.fixture
def parser():
    """Create a fresh NDOVLoketParser instance"""
    return NDOVLoketParser()


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory"""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def dvs_sample_xml(fixtures_dir):
    """Load DVS sample XML"""
    return (fixtures_dir / 'dvs_sample.xml').read_text()


@pytest.fixture
def rit_sample_xml(fixtures_dir):
    """Load RIT sample XML"""
    return (fixtures_dir / 'rit_sample.xml').read_text()


@pytest.fixture
def gtw_articulated_xml(fixtures_dir):
    """Load GTW articulated trainset XML"""
    return (fixtures_dir / 'gtw_articulated.xml').read_text()


@pytest.fixture
def sample_composition():
    """Create a sample TrainComposition for testing"""
    comp = TrainComposition()
    comp.train_number = "1234"
    comp.timestamp = "2026-06-19T12:00:00.000Z"
    comp.add_part("SLT", "6", "2345", units=1, coaches=6, length_cm=7500)
    comp.add_part("SLT", "4", "2346", units=1, coaches=4, length_cm=5000)
    comp.total_units = 2
    comp.total_coaches = 10
    comp.total_length_cm = 12500
    return comp


@pytest.fixture
def aanduiding_test_cases():
    """Test cases for MaterieelAanduiding parsing"""
    return [
        ("6", 1, 6),
        ("4", 1, 4),
        ("2/6", 2, 6),
        ("2/8", 2, 8),
        ("3/12", 3, 12),
    ]
