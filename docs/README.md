# NDOVLoket Train Composition Parser

A Python script to parse train composition (rolling stock) data from the NDOVLoket open data feed for Dutch trains.

## Features

- Connects to NDOVLoket's ZeroMQ real-time data feed
- Parses train composition information (materieelsamenstelling)
- Extracts rolling stock types, designations, and coach counts
- Saves data to JSON format for further analysis
- Supports multiple data stream topics (RIT, DVS, DAS)

## Installation

```bash
uv sync
```

## Usage

### Basic Usage

Run the script to start receiving train composition data:

```bash
uv run ndov_train_composition.py
```

This will connect to the NDOVLoket feed and display train compositions as they arrive.

### Command Line Options

```bash
# Limit to 100 messages
uv run ndov_train_composition.py --max-messages 100

# Specify custom output file
uv run ndov_train_composition.py --output my_compositions.json

# Subscribe to specific topics only
uv run ndov_train_composition.py --topics /RIG/InfoPlusRITInterface2

# Use custom ZeroMQ endpoint
uv run ndov_train_composition.py --endpoint tcp://custom.server:7664
```

### Arguments

- `--endpoint`: ZeroMQ endpoint URL (default: `tcp://pubsub.besteffort.ndovloket.nl:7664`)
- `--max-messages`: Maximum number of messages to process (default: unlimited)
- `--output`: Output JSON file path (default: `train_compositions.json`)
- `--topics`: Specific ZeroMQ topics to subscribe to (default: all RIG topics)

## Data Sources

The script subscribes to the following NDOVLoket data streams:

1. **InfoPlusRITInterface2** - Train service information with composition data
2. **InfoPlusDVSInterface4** - Departure information
3. **InfoPlusDASInterface4** - Arrival information

## Output Format

Train compositions are saved as JSON with the following structure:

```json
[
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
        "number": null,
        "units": 2,
        "coaches": 6,
        "length_cm": 4100
      },
      {
        "type": "GTW-D-ARR",
        "designation": "2/8",
        "number": null,
        "units": 2,
        "coaches": 8,
        "length_cm": 5600
      }
    ],
    "vehicle_types": ["GTW-D-ARR"]
  }
]
```

## Data Fields

- **train_number**: The train service number
- **timestamp**: Full ISO 8601 timestamp with milliseconds (e.g., "2022-07-16T19:50:56.392Z")
- **total_units**: Total number of trainset units (treinstellen)
- **total_coaches**: Total number of car bodies (wagenkasten)
- **total_length_cm**: Total train length in centimeters (divide by 100 for meters)
- **composition_parts**: Array of rolling stock units
  - **type**: Rolling stock type (e.g., "SLT", "ICM", "VIRM", "GTW-D-ARR")
  - **designation**: MaterieelAanduiding (e.g., "6", "2/6", "2/8")
  - **number**: Specific unit number (if available)
  - **units**: Number of trainset units in this part (treinstellen)
  - **coaches**: Number of car bodies in this part (wagenkasten)
  - **length_cm**: Length of this part in centimeters (if available)
- **vehicle_types**: Unique list of all vehicle types in the composition

### Understanding Units vs. Coaches

The `designation` field uses the format `units/coaches` or just `coaches`:

- **"6"** = Single trainset with 6 coaches (1 unit, 6 coaches)
- **"2/6"** = Two coupled trainsets with 6 total car bodies (2 units, 6 coaches)
- **"2/8"** = Two coupled trainsets with 8 total car bodies (2 units, 8 coaches)

For articulated trainsets (like GTW), the "units" are semi-permanently coupled powered trainsets, while "coaches" refers to the individual car bodies that provide passenger space.

## Common Dutch Rolling Stock Types

- **SLT** - Sprinter Lighttrain (new)
- **VIRM** - Verlengd InterRegio Materieel
- **ICM** - InterCity Materieel
- **DDZ** - DubbelDeks Treinstellen
- **ICRm** - InterCity Rijtuig (modernized)
- **FLIRT** - Fast Light Innovative Regional Train
- **GTW-D-ARR** - Arriva GTW (Gelenktriebwagen) diesel trainset

## Technical Details

### XML Format and Namespaces

NDOVLoket uses the InfoPlus XML format with namespaces defined by the Dutch railway standard. The parser handles:

**Namespace:**
- `ns2: urn:ndov:cdm:trein:reisinformatie:data:4`

**Message Types:**

1. **DVS (DynamischeVertrekStaat)** - Departure information
   - Root: `ReisInformatieProductDVS`
   - Train composition tags:
     - `MaterieelDeelDVS` - Individual rolling stock unit
     - `MaterieelSoort` - Vehicle type (e.g., "SLT", "VIRM", "GTW-D-ARR")
     - `MaterieelAanduiding` - Designation/coach count (e.g., "6", "2/6")
     - `MaterieelNummer` - Unit number (optional)

2. **RIT (RitInformatie)** - Service/trip information
   - Root: `ReisInformatieProductRitInfo`
   - Train composition tags:
     - `MaterieelDeel` - Individual rolling stock unit
     - `MaterieelDeelSoort` - Vehicle type
     - `MaterieelDeelAanduiding` - Designation/coach count
     - `MaterieelNummer` - Unit number (optional)

3. **DAS (DynamischeAankomstStaat)** - Arrival information
   - Similar structure to DVS

### Example XML Structure

DVS message with composition data:
```xml
<ns2:ReisInformatieProductDVS>
  <ns2:DynamischeVertrekStaat>
    <ns2:Trein>
      <ns2:TreinNummer>1234</ns2:TreinNummer>
      <ns2:TreinVleugel>
        <ns2:MaterieelDeelDVS>
          <ns2:MaterieelSoort>SLT</ns2:MaterieelSoort>
          <ns2:MaterieelAanduiding>6</ns2:MaterieelAanduiding>
        </ns2:MaterieelDeelDVS>
      </ns2:TreinVleugel>
    </ns2:Trein>
  </ns2:DynamischeVertrekStaat>
</ns2:ReisInformatieProductDVS>
```

## Notes

- The script requires an active internet connection to connect to the NDOVLoket feed
- Messages from NDOVLoket are **gzip-compressed**; the parser automatically decompresses them
- Data availability depends on NS (Nederlandse Spoorwegen) and other operators publishing composition information
- **Not all messages contain composition data** - only a subset of DVS and RIT messages include `MaterieelDeel` information
- The parser uses XML namespace-aware parsing to correctly extract data from InfoPlus messages
- The script increments the message counter for all received messages, but only saves those with composition data

## Troubleshooting

### Why am I seeing many messages but few compositions?

Most messages from NDOVLoket are arrival/departure updates without composition data. This is normal behavior:
- DVS/DAS messages contain platform, delay, and route information
- Only some DVS messages and most RIT messages include `MaterieelDeel` data
- You may need to process 50-100 messages to find a few with composition information

**Solutions:**
- Use `--max-messages 200` to collect more data
- Subscribe to only RIT messages: `--topics /RIG/InfoPlusRITInterface2`
- Use `--debug` flag to save raw XML and inspect message contents
- Run during peak hours when more trains are operating

### Debug Mode

To inspect raw XML messages and understand what data is available:

```bash
uv run ndov_train_composition.py --debug --max-messages 10
```

This saves each message as `debug_message_N.xml` so you can examine the structure.

## References

- [NDOVLoket/GOVI](https://ndovloket.nl/)
- [OpenOV](https://openov.nl/)
- [Rijden de Treinen](https://www.rijdendetreinen.nl/en/open-data)
- [GoTrain - Reference Implementation](https://github.com/rijdendetreinen/gotrain)

## Sources

- [GitHub - rijdendetreinen/gotrain](https://github.com/rijdendetreinen/gotrain)
- [NS Train Positions Documentation](https://data.ndovloket.nl/docs/infoplus/TreinLocatie/Publicatiedocument_NDOV_NS-Treinposities-161202.pdf)
- [NDOV Loket Examples](https://github.com/onderweg/ndovloket-ppv-vi-examples)
- [OpenOV](https://openov.nl/)
- [Rijdendetreinen Open Data](https://www.rijdendetreinen.nl/en/open-data)
