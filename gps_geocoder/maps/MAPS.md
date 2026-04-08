# Available Maps

gps-geocoder uses a pluggable map system. Each regional map is an optional module that can be installed independently.

## Currently available

| ID | Region | Data source | Approx. size |
|----|--------|-------------|-------------|
| `tw` | Taiwan (台灣) | OpenStreetMap / Geofabrik | ~52 MB |

## Coming soon

Regional maps will be added over time based on community demand. Planned:

- `jp` — Japan (日本)
- `kr` — South Korea (韓國)

## Install only what you need

Maps can be large. Install only the regions you actually need:

```bash
pip install gps-geocoder[tw]       # Taiwan only
pip install gps-geocoder[tw,jp]    # Taiwan + Japan
pip install gps-geocoder[all]      # All available maps
```

Then build the database:

```bash
gps-geocoder init tw
```

## Without any maps

Even without installing any maps, you can still:
- Import personal places from Google Takeout
- Search and query your saved places
- Get raw coordinates from gps-bridge

Maps add street-level address resolution for their region.
