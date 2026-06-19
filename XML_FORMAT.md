# NDOVLoket XML Format Reference

This document describes the XML structure used by NDOVLoket for train composition data.

## Namespaces

```xml
xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4"
```

## Message Types

### 1. DVS (DynamischeVertrekStaat) - Departure Information

**Topic:** `/RIG/InfoPlusDVSInterface4`

**Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ns1:PutReisInformatieBoodschapIn xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
    xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4">
    <ns2:ReisInformatieProductDVS TimeStamp="2022-07-16T19:50:56.392Z" Versie="6.2">
        <ns2:RIPAdministratie>
            <ns2:ReisInformatieProductID>2197032278644005</ns2:ReisInformatieProductID>
        </ns2:RIPAdministratie>
        <ns2:DynamischeVertrekStaat>
            <ns2:RitId>32278</ns2:RitId>
            <ns2:RitDatum>2022-07-16</ns2:RitDatum>
            <ns2:Trein>
                <ns2:TreinNummer>32278</ns2:TreinNummer>
                <ns2:TreinSoort Code="ST">Stoptrein</ns2:TreinSoort>
                <ns2:Vervoerder>Arriva</ns2:Vervoerder>
                
                <!-- Train composition in TreinVleugel -->
                <ns2:TreinVleugel>
                    <ns2:MaterieelDeelDVS>
                        <ns2:MaterieelSoort>GTW-D-ARR</ns2:MaterieelSoort>
                        <ns2:MaterieelAanduiding>2/6</ns2:MaterieelAanduiding>
                        <ns2:MaterieelNummer>12345</ns2:MaterieelNummer>
                        <ns2:MaterieelLengte>4100</ns2:MaterieelLengte>
                        <ns2:MaterieelDeelVolgordeVertrek>1</ns2:MaterieelDeelVolgordeVertrek>
                    </ns2:MaterieelDeelDVS>
                    <ns2:MaterieelDeelDVS>
                        <ns2:MaterieelSoort>GTW-D-ARR</ns2:MaterieelSoort>
                        <ns2:MaterieelAanduiding>2/8</ns2:MaterieelAanduiding>
                        <ns2:MaterieelNummer>12346</ns2:MaterieelNummer>
                        <ns2:MaterieelLengte>5600</ns2:MaterieelLengte>
                        <ns2:MaterieelDeelVolgordeVertrek>2</ns2:MaterieelDeelVolgordeVertrek>
                    </ns2:MaterieelDeelDVS>
                </ns2:TreinVleugel>
            </ns2:Trein>
        </ns2:DynamischeVertrekStaat>
    </ns2:ReisInformatieProductDVS>
</ns1:PutReisInformatieBoodschapIn>
```

**Key Fields:**
- `TimeStamp` (attribute) - Full ISO 8601 timestamp at product level (e.g., "2022-07-16T19:50:56.392Z")
- `TreinNummer` - Train service number
- `MaterieelSoort` - Rolling stock type (e.g., "GTW-D-ARR", "SLT", "VIRM")
- `MaterieelAanduiding` - Coach count or designation (e.g., "6", "2/6", "4")
- `MaterieelLengte` - Length in centimeters (e.g., 4100 = 41 meters)
- `MaterieelNummer` - Specific unit number (optional)
- `MaterieelDeelVolgordeVertrek` - Order in the train composition

### 2. RIT (RitInformatie) - Service/Trip Information

**Topic:** `/RIG/InfoPlusRITInterface2`

**Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ns1:PutReisInformatieBoodschapIn xmlns:ns1="urn:ndov:cdm:trein:reisinformatie:messages:5"
    xmlns:ns2="urn:ndov:cdm:trein:reisinformatie:data:4">
    <ns2:ReisInformatieProductRitInfo TimeStamp="2022-07-16T19:50:56.392Z" Versie="6.2">
        <ns2:RitInfo>
            <ns2:RitId>5678</ns2:RitId>
            <ns2:RitDatum>2022-07-16</ns2:RitDatum>
            <ns2:LogischeRitDeel>
                <ns2:LogischeRitDeelStation>
                    <ns2:StationCode>UT</ns2:StationCode>
                    
                    <!-- Train composition -->
                    <ns2:MaterieelDeel>
                        <ns2:MaterieelDeelID>AD6</ns2:MaterieelDeelID>
                        <ns2:MaterieelDeelSoort>VIRM</ns2:MaterieelDeelSoort>
                        <ns2:MaterieelDeelAanduiding>4</ns2:MaterieelDeelAanduiding>
                        <ns2:MaterieelDeelLengte>10860</ns2:MaterieelDeelLengte>
                        <ns2:MaterieelNummer>000000-09547-0</ns2:MaterieelNummer>
                        <ns2:MaterieelDeelToegankelijk>N</ns2:MaterieelDeelToegankelijk>
                        <ns2:AchterBlijvenMaterieelDeel>N</ns2:AchterBlijvenMaterieelDeel>
                    </ns2:MaterieelDeel>
                    <ns2:MaterieelDeel>
                        <ns2:MaterieelDeelID>AD7</ns2:MaterieelDeelID>
                        <ns2:MaterieelDeelSoort>VIRM</ns2:MaterieelDeelSoort>
                        <ns2:MaterieelDeelAanduiding>6</ns2:MaterieelDeelAanduiding>
                        <ns2:MaterieelNummer>000000-09548-0</ns2:MaterieelNummer>
                    </ns2:MaterieelDeel>
                </ns2:LogischeRitDeelStation>
            </ns2:LogischeRitDeel>
        </ns2:RitInfo>
    </ns2:ReisInformatieProductRitInfo>
</ns1:PutReisInformatieBoodschapIn>
```

**Key Fields:**
- `TimeStamp` (attribute) - Full ISO 8601 timestamp at product level
- `RitId` - Trip/service ID
- `MaterieelDeelSoort` - Rolling stock type
- `MaterieelDeelAanduiding` - Coach count or designation
- `MaterieelDeelLengte` - Length in centimeters
- `MaterieelNummer` - Specific unit number
- `MaterieelDeelToegankelijk` - Accessibility (N/Y)
- `AchterBlijvenMaterieelDeel` - Whether this unit stays behind (N/Y)

### 3. DAS (DynamischeAankomstStaat) - Arrival Information

**Topic:** `/RIG/InfoPlusDASInterface4`

Similar structure to DVS but for arrivals. May contain composition data in some cases.

## Parser Implementation

The parser in `ndov_train_composition.py` extracts composition data by:

1. Registering the `ns2` namespace
2. Finding all `MaterieelDeelDVS` elements (DVS messages)
3. Finding all `MaterieelDeel` elements (RIT messages)
4. Extracting:
   - `MaterieelSoort` or `MaterieelDeelSoort` → vehicle type
   - `MaterieelAanduiding` or `MaterieelDeelAanduiding` → designation
   - `MaterieelNummer` → unit number (optional)
5. Calculating total coaches from designation field

## Common Rolling Stock Codes

| Code | Description | Typical Coaches |
|------|-------------|----------------|
| SLT | Sprinter Lighttrain | 4, 6 |
| VIRM | Verlengd InterRegio Materieel | 4, 6 |
| ICM | InterCity Materieel | 3, 4 |
| DDZ | DubbelDeks Treinstellen | 4, 6 |
| ICRm | InterCity Rijtuig modernized | Varies |
| GTW-D-ARR | Arriva GTW diesel | 2/6, 2/8 |
| FLIRT | Fast Light Regional Train | 3, 4 |

## MaterieelAanduiding Format (Coach Designation)

The `MaterieelAanduiding` field indicates the train composition and can have different formats:

### Format: `number_of_units / number_of_car_bodies`

**Examples:**

| Format | Meaning | Description |
|--------|---------|-------------|
| `6` | Single 6-coach unit | Simple number = one trainset with 6 coaches |
| `4` | Single 4-coach unit | Simple number = one trainset with 4 coaches |
| `2/6` | 2 units, 6 car bodies | Two coupled trainsets with 6 car bodies total |
| `2/8` | 2 units, 8 car bodies | Two coupled trainsets with 8 car bodies total |

### Detailed Explanation

The **slash format** (`2/6`) is used for articulated trainsets:

- **First number (2)**: Number of **treinstellen** (trainset units) coupled together
  - Each unit is a self-contained, powered trainset
  - Units are semi-permanently coupled for a service
  
- **Second number (6)**: Total number of **wagenkasten** (car bodies/coach sections)
  - Represents the total passenger capacity
  - Car bodies in articulated trains share bogies (wheel assemblies)

**Example: GTW-D-ARR 2/6**
- Type: Arriva Gelenktriebwagen (articulated diesel trainset)
- 2 trainset units coupled together
- 6 car bodies total providing passenger space
- Cannot be easily separated (articulated design)

**Example: VIRM 4**
- Type: Verlengd InterRegio Materieel
- Single trainset unit (no slash = single unit)
- 4 coaches

### Why This Matters

Understanding the unit vs. car body distinction is important because:

1. **Capacity**: Car bodies determine passenger capacity
2. **Flexibility**: Number of units shows if the train is a single set or multiple coupled sets
3. **Operations**: Articulated trainsets (with slash notation) can't be easily split
4. **Platform length**: Total length depends on both units and car bodies

### Parser Behavior

The parser uses the `parse_materieel_aanduiding()` function to extract both values from each `MaterieelAanduiding`:

```python
parse_materieel_aanduiding("6")    # Returns: (1, 6)  - 1 unit, 6 coaches
parse_materieel_aanduiding("2/6")  # Returns: (2, 6)  - 2 units, 6 coaches
parse_materieel_aanduiding("2/8")  # Returns: (2, 8)  - 2 units, 8 coaches
```

Each composition part stores:
- `units`: Number of trainset units (treinstellen) in this part
- `coaches`: Number of car bodies (wagenkasten) in this part

The totals are summed across all parts:
- `total_units`: Sum of all units in the train
- `total_coaches`: Sum of all coaches in the train

### Real-World Example

A train with composition **GTW-D-ARR 2/6 + GTW-D-ARR 2/8** would be parsed as:

```json
{
  "total_units": 4,
  "total_coaches": 14,
  "composition_parts": [
    {
      "type": "GTW-D-ARR",
      "designation": "2/6",
      "units": 2,
      "coaches": 6
    },
    {
      "type": "GTW-D-ARR",
      "designation": "2/8",
      "units": 2,
      "coaches": 8
    }
  ]
}
```

This represents:
- 4 total GTW trainset units coupled together
- 14 total car bodies providing passenger space
- Two groups: a 2-unit/6-coach formation + a 2-unit/8-coach formation

## Length Field

Train part lengths are specified in **centimeters** (not millimeters or meters):

**DVS messages:** `MaterieelLengte` (element)  
**RIT messages:** `MaterieelDeelLengte` (element)

**Examples:**
- `4100` = 41 meters (GTW 2/6)
- `5600` = 56 meters (GTW 2/8)
- `10860` = 108.6 meters (VIRM 6)
- `7240` = 72.4 meters (VIRM 4)

The parser:
- Stores individual part lengths as `length_cm` in each composition part
- Sums them to calculate `total_length_cm` for the entire train
- Displays length in meters in the string representation (dividing by 100)

## Compression

All messages from NDOVLoket are **gzip-compressed**. The parser automatically:
1. Receives the compressed binary data
2. Decompresses using `gzip.decompress()`
3. Decodes to UTF-8 string
4. Parses the XML

## References

- [NDOVLoket InfoPlus Specification](https://data.ndovloket.nl/)
- [GoTrain Parser Implementation](https://github.com/rijdendetreinen/gotrain/tree/master/parsers)
- Sample XML files: `/tmp/gotrain/parsers/testdata/` (if cloned)
