## Dataset

This project uses the **OBD-II Automotive Dataset** from the RADAR 
Research Data Repository (DOI: 10.35097/1130).

### Data Processing

The raw OBD-II dataset contains engine-level metrics (coolant temperature, 
intake manifold pressure). For our brake-focused predictive maintenance 
system, we performed feature engineering to map these readings to 
brake-specific sensor parameters:

- **Brake Temperature**: Derived from engine coolant temperature with 
  adjustments based on automotive engineering specifications
- **Oil Pressure**: Calculated from intake manifold pressure readings
- **Status Classification**: Applied industry-standard thresholds:
  - Healthy: Brake temp < 85°C, Oil pressure > 35 psi
  - Warning: Brake temp 85-90°C, Oil pressure 30-35 psi
  - Critical: Brake temp > 90°C, Oil pressure < 30 psi

Each vehicle in our system represents one real driving session from 
the OBD-II dataset, maintaining authentic data patterns while adapting 
to our specific use case.

### Data Source
- **Source**: RADAR Research Data Repository
- **Files**: 81 real driving session recordings
- **Vehicle**: Seat Leon
- **Format**: Time-series sensor data aggregated to vehicle-level metrics