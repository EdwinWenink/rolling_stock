# NDOVLoket Train Composition Parser

A Python parser for extracting train composition (rolling stock) data from the NDOVLoket open data feed for Dutch trains.

## Quick Start

```bash
# Install dependencies
make install

# Run tests
make test

# Run the parser
make run

# Or use uv directly
uv run src/ndov_train_composition.py --max-messages 50
```

## Project Structure

```
materieelinfo/
├── src/                          # Source code
│   └── ndov_train_composition.py # Main parser
├── examples/                     # Example scripts
│   ├── example_usage.py          # 5 usage examples
│   └── example_units_analysis.py # Analyze units vs coaches
├── tests/                        # Unit tests
│   └── test_parser.py            # Parser tests
├── docs/                         # Documentation
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # Quick start guide
│   └── XML_FORMAT.md             # Technical XML reference
├── output/                       # Generated output (gitignored)
│   └── *.json                    # Train composition data
├── data/                         # Data files (gitignored)
└── pyproject.toml                # Project configuration
```

## Features

- ✅ Connects to NDOVLoket's ZeroMQ real-time data feed
- ✅ Parses train composition information (materieelsamenstelling)
- ✅ Extracts rolling stock types, units (treinstellen), and coaches (wagenkasten)
- ✅ Records full timestamps with millisecond precision
- ✅ Captures train part lengths in centimeters
- ✅ Handles gzip-compressed messages
- ✅ Supports DVS (departures), RIT (services), and DAS (arrivals) formats
- ✅ Saves data to JSON format for further analysis

## Documentation

- **[Full Documentation](docs/FULL_DOCUMENTATION.md)** - Complete technical documentation
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started quickly
- **[XML Format Reference](docs/XML_FORMAT.md)** - Technical XML specification

## Usage

### Basic Usage

```bash
uv run src/ndov_train_composition.py --max-messages 100 --output output/trains.json
```

### Run Examples

```bash
# List available examples
make examples

# Run specific examples
make example-4      # Statistics collection
make example-units  # Units analysis

# Or use uv directly
uv run examples/example_usage.py 4
```

### Run Tests

```bash
# Run all tests
make test

# Or use pytest directly
uv run pytest tests/ -v
```

## Output

Train compositions are saved as JSON in the `output/` directory:

```json
{
  "train_number": "32278",
  "timestamp": "2022-07-16T19:50:56.392Z",
  "total_units": 4,
  "total_coaches": 14,
  "total_length_cm": 9700,
  "composition_parts": [
    {
      "type": "GTW-D-ARR",
      "designation": "2/6",
      "units": 2,
      "coaches": 6,
      "length_cm": 4100
    }
  ],
  "vehicle_types": ["GTW-D-ARR"]
}
```

## License

This project is provided as-is for educational and research purposes.

## References

- [NDOVLoket/GOVI](https://ndovloket.nl/)
- [OpenOV](https://openov.nl/)
- [Rijden de Treinen](https://www.rijdendetreinen.nl/en/open-data)
- [GoTrain - Reference Implementation](https://github.com/rijdendetreinen/gotrain)
