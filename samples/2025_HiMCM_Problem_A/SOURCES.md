# Data Sources — 2025 HiMCM Problem A

## Parameter Data

### building_basic.json
- **Source**: Self-designed based on Problem Figure 1 schematic
- **Description**: Single-story office building with 6 rooms, central hallway, 2 exits
- **Room dimensions**: Assumed 4m × 5m = 20 m² per office (typical office standard)
- **Hallway**: Assumed 30m × 1.8m (standard corridor width per IBC)
- **Status**: Simulated data — parameters are reasonable estimates based on building codes

### building_scenario_B.json
- **Source**: Self-designed per Requirement 3
- **Description**: 2-story office + chemistry lab, 11 rooms, 1 staircase
- **Room dimensions**: Offices 4m×5m=20m², Lab 8m×5m=40m²
- **Floor height**: 3.5m per floor
- **Status**: Simulated data

### building_scenario_C.json
- **Source**: Self-designed per Requirement 3
- **Description**: 3-story mixed-use (daycare + open office + warehouse), 16 rooms, 2 staircases
- **Room dimensions**: Daycare 30m², Open office 40m²×2, Warehouse aisles 40m²×6
- **Status**: Simulated data

### room_type_params.csv
- **Source**: Literature-based estimates
- **References**:
  - Office sweep time: NFPA 101 Life Safety Code, typical fire drill observations
  - Daycare sweep time: Adjusted from office baseline ×3.0 (children hiding behavior)
  - Lab sweep time: OSHA laboratory safety guidelines
  - Warehouse sweep time: Based on Lambert et al. (2021), crawling speed ~15-21 m²/min
  - Kitchen sweep time: NFPA 96 commercial kitchen safety standards
- **Key reference**: Lambert et al. (2021) "Search & Rescue Operations during Interior Firefighting: A Study into Crawling Speeds", *Fire Safety Journal*, 121:103269
- **Status**: Literature-derived estimates — annotated with uncertainty ranges

## Model Parameters (Hard-coded in utils.py)

| Parameter | Value | Source |
|-----------|-------|--------|
| Normal walking speed | 1.35 m/s | ISO/TR 16738:2009 Fire-safety engineering |
| Walking speed with gear | 1.0 m/s | NFPA firefighter equipment studies |
| Walking speed in smoke | 0.5 m/s | Lambert et al. (2021) crawling experiment |
| Stair ascent speed | 0.4 m/s | ISO/TR 16738:2009 |
| Stair descent speed | 0.6 m/s | ISO/TR 16738:2009 |
| Communication delay | Lognormal(μ=2s, σ=0.5) | Reasonable estimate for radio communication |
| Smoke diffusion coefficient | 0.01 m²/s | Typical indoor air diffusion |
| Fire spread rate | 0.5 m/min (initial) | Engineering estimate based on FDS benchmarks |

## References (BibTeX)
See: `paper/refs.bib` — 14 references covering graph optimization, MAPF, fire simulation, firefighter behavior, and smart building technologies.
