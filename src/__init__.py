"""
NDOVLoket Train Composition Parser

A Python parser for extracting train composition (rolling stock) data
from the NDOVLoket open data feed for Dutch trains.
"""

from .ndov_train_composition import (
    TrainComposition,
    NDOVLoketParser,
    parse_materieel_aanduiding,
    save_to_json,
)

__version__ = "0.1.0"
__all__ = [
    "TrainComposition",
    "NDOVLoketParser",
    "parse_materieel_aanduiding",
    "save_to_json",
]
