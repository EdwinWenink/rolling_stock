# Quick Start Guide

## Installation

This project uses UV for dependency management. If you don't have UV installed:

```bash
# Install UV (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then sync the dependencies:

```bash
uv sync
```

## Running the Parser

### 1. Basic Usage - Listen for Train Compositions

```bash
uv run ndov_train_composition.py
```

This will connect to the NDOVLoket feed and print train compositions as they arrive. Press Ctrl+C to stop.

### 2. Collect Limited Number of Messages

```bash
# Collect 50 messages and stop
uv run ndov_train_composition.py --max-messages 50
```

### 3. Save to Custom File

```bash
uv run ndov_train_composition.py --output my_trains.json --max-messages 100
```

### 4. Subscribe to Specific Topics Only

```bash
# Only RIT messages (train services)
uv run ndov_train_composition.py --topics /RIG/InfoPlusRITInterface2
```

## Running Examples

The `example_usage.py` script shows different ways to use the parser programmatically:

```bash
# See available examples
uv run example_usage.py

# Run example 1 (basic usage)
uv run example_usage.py 1

# Run example 4 (statistics collection)
uv run example_usage.py 4
```

### Available Examples:

1. **Basic usage** - Simple connection and message printing
2. **Custom callback** - Categorize trains by vehicle type
3. **Filter by coach count** - Only save long trains (8+ coaches)
4. **Statistics collection** - Gather stats about compositions
5. **Monitor specific train type** - Find trains with specific rolling stock (e.g., VIRM)

## Testing

Run the unit tests to verify everything works:

```bash
uv run test_parser.py
```

## Output Format

The parser saves train compositions as JSON:

```json
[
  {
    "train_number": "32278",
    "timestamp": "2022-07-16T19:50:56.392Z",
    "total_units": 2,
    "total_coaches": 14,
    "composition_parts": [
      {
        "type": "GTW-D-ARR",
        "designation": "2/6",
        "number": null,
        "units": 2,
        "coaches": 6
      },
      {
        "type": "GTW-D-ARR",
        "designation": "2/8",
        "number": null,
        "units": 2,
        "coaches": 8
      }
    ],
    "vehicle_types": ["GTW-D-ARR"]
  }
]
```

### Understanding the Data

- **total_units**: Total trainset units (treinstellen) - powered trainsets coupled together
- **total_coaches**: Total car bodies (wagenkasten) - passenger sections
- **designation**: Format is `units/coaches` or just `coaches`
  - `"6"` = 1 unit with 6 coaches
  - `"2/6"` = 2 units with 6 coaches total
  - `"2/8"` = 2 units with 8 coaches total

## Common Dutch Train Types

You'll see these abbreviations in the data:

- **SLT** - Sprinter Lighttrain (new electric trains)
- **VIRM** - Verlengd InterRegio Materieel (double-deck intercity)
- **ICM** - InterCity Materieel (intercity trains)
- **DDZ** - DubbelDeks Treinstellen (double-deck regional)
- **ICRm** - InterCity Rijtuig modernized (modernized intercity coaches)
- **FLIRT** - Fast Light Innovative Regional Train

## Understanding the Output

**Important:** Most messages from NDOVLoket do NOT contain composition data. This is normal!

When you run the parser, you'll see:
```
Message 1 on: /RIG/InfoPlusDVSInterface4
  - No composition data in this message
Message 2 on: /RIG/InfoPlusDVSInterface4
  ✓ Composition #1: Train 32278: GTW-D-ARR 2/6; GTW-D-ARR 2/8 (Total coaches: 14)
```

You may need to process 50-100 messages to find a few with composition information. This is expected because:
- Most messages are arrival/departure updates (platform, delays, etc.)
- Only a subset of messages include rolling stock details

**Tip:** For better results, collect more messages:
```bash
uv run ndov_train_composition.py --max-messages 200
```

Or subscribe to only RIT messages (which have more composition data):
```bash
uv run ndov_train_composition.py --topics /RIG/InfoPlusRITInterface2
```

## Troubleshooting

### Seeing "No composition data in this message"

This is **normal**. Not all messages contain rolling stock information. Solutions:
- Increase `--max-messages` to collect more data
- Use only RIT topic: `--topics /RIG/InfoPlusRITInterface2`
- Run during peak hours (6-9 AM, 4-7 PM) when more trains operate
- Use `--debug` to inspect raw XML and see what's in the messages

### Debug Mode - Inspect Raw Messages

```bash
uv run ndov_train_composition.py --debug --max-messages 10
```

This saves each message to `debug_message_N.xml` files for inspection.

### Connection Issues

If you can't connect to the NDOVLoket feed:
- Check your internet connection
- Verify the endpoint is accessible: `tcp://pubsub.besteffort.ndovloket.nl:7664`
- The feed may occasionally be down for maintenance

### Module Not Found

If you get import errors:
```bash
# Make sure dependencies are installed
uv sync
```

## Next Steps

- Modify `example_usage.py` to create your own analysis scripts
- Integrate the parser into your own projects by importing the classes
- Explore the full NDOVLoket API for additional data sources

## Documentation

- Full documentation: See [README.md](README.md)
- NDOVLoket: https://ndovloket.nl/
- OpenOV community: https://openov.nl/
