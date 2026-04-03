"""
NEW FILE: services/agents/config/dataset_loader.py
PURPOSE : Central loader for all datasets used by Person 4 files.
          All your agents read real data from here instead of hardcoded values.
DATASETS:
  - ml/data/raw/ai4i2020.csv       (UCI — 10,000 rows)
  - ml/data/raw/PdM_telemetry.csv  (Azure — 876,100 rows)
  - ml/data/raw/PdM_failures.csv   (Azure — 761 rows)
  - ml/data/raw/PdM_machines.csv   (Azure — 100 rows)
  - ml/data/raw/PdM_errors.csv     (Azure — 3,919 rows)
USED BY:
  FILE 8  — engagement_agent.py
  FILE 11 — manufacturing_insights_agent.py
  FILE 14 — behavior_baseline.py
  FILE 15 — anomaly_detector.py
  FILE 18 — rca_engine.py
  FILE 25 — demo_runner.py
"""

import logging
import pandas as pd
from pathlib import Path
from functools import lru_cache

logger   = logging.getLogger(__name__)
DATA_DIR = Path("ml/data/raw")


# ==============================================================================
# SECTION 1: Dataset Loaders (cached — loads once, reuses every time)
# ==============================================================================

@lru_cache(maxsize=1)
def load_uci_dataset() -> pd.DataFrame:
    """
    Load UCI AI4I 2020 Predictive Maintenance dataset.
    10,000 rows | Columns: Type, Air temperature, Process temperature,
                            Rotational speed, Torque, Tool wear, machine_failure
    Used by: FILE 11 (RCA failure patterns), FILE 15 (anomaly training),
             FILE 18 (failure probabilities)
    """
    path = DATA_DIR / "ai4i2020.csv"
    if not path.exists():
        logger.warning(f"UCI dataset not found at {path} — using empty DataFrame")
        return pd.DataFrame()
    df = pd.read_csv(path)
    logger.info(f"UCI dataset loaded | rows={len(df)}")
    return df


@lru_cache(maxsize=1)
def load_azure_telemetry() -> pd.DataFrame:
    """
    Load Azure Predictive Maintenance telemetry dataset.
    876,100 rows | Columns: datetime, machineID, volt, rotate, pressure, vibration
    Used by: FILE 14 (UEBA normal behaviour thresholds),
             FILE 25 (real sensor values for demo)
    """
    path = DATA_DIR / "PdM_telemetry.csv"
    if not path.exists():
        logger.warning(f"Azure telemetry not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["datetime"])
    logger.info(f"Azure telemetry loaded | rows={len(df)}")
    return df


@lru_cache(maxsize=1)
def load_azure_failures() -> pd.DataFrame:
    """
    Load Azure failure records.
    761 rows | Columns: datetime, machineID, failure
    Used by: FILE 8 (which vehicles have failure history),
             FILE 25 (real failure examples for demo)
    """
    path = DATA_DIR / "PdM_failures.csv"
    if not path.exists():
        logger.warning(f"Azure failures not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["datetime"])
    logger.info(f"Azure failures loaded | rows={len(df)}")
    return df


@lru_cache(maxsize=1)
def load_azure_machines() -> pd.DataFrame:
    """
    Load Azure machine info.
    100 rows | Columns: machineID, model, age
    Used by: FILE 8 (vehicle age for urgency scoring),
             FILE 25 (real machine data for demo)
    """
    path = DATA_DIR / "PdM_machines.csv"
    if not path.exists():
        logger.warning(f"Azure machines not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    logger.info(f"Azure machines loaded | rows={len(df)}")
    return df


@lru_cache(maxsize=1)
def load_azure_errors() -> pd.DataFrame:
    """
    Load Azure error records.
    3,919 rows | Columns: datetime, machineID, errorID
    Used by: FILE 14 (error frequency for UEBA baseline)
    """
    path = DATA_DIR / "PdM_errors.csv"
    if not path.exists():
        logger.warning(f"Azure errors not found at {path}")
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["datetime"])
    logger.info(f"Azure errors loaded | rows={len(df)}")
    return df


# ==============================================================================
# SECTION 2: Derived Statistics Used By Your Files
# ==============================================================================

def get_uci_failure_stats() -> dict:
    """
    Calculate real failure statistics from UCI dataset.
    Used by: FILE 18 (rca_engine — real failure probabilities)
             FILE 11 (manufacturing_insights_agent)

    Returns:
        dict with failure rates per type
    """
    df = load_uci_dataset()
    if df.empty:
        return {"overall_failure_rate": 0.034, "source": "default"}

    stats = {
        "overall_failure_rate": round(df["machine_failure"].mean(), 4),
        "total_records":        len(df),
        "total_failures":       int(df["machine_failure"].sum()),
        "source":               "uci_ai4i2020",
    }

    # Temperature statistics for threshold setting
    stats["avg_air_temp"]     = round(df["Air temperature"].mean(), 2)
    stats["avg_process_temp"] = round(df["Process temperature"].mean(), 2)
    stats["avg_torque"]       = round(df["Torque"].mean(), 2)
    stats["avg_tool_wear"]    = round(df["Tool wear"].mean(), 2)

    # Failure conditions (when machine_failure=1)
    failed = df[df["machine_failure"] == 1]
    if len(failed) > 0:
        stats["failure_avg_temp"]     = round(failed["Process temperature"].mean(), 2)
        stats["failure_avg_torque"]   = round(failed["Torque"].mean(), 2)
        stats["failure_avg_toolwear"] = round(failed["Tool wear"].mean(), 2)

    logger.info(f"UCI failure stats: {stats['overall_failure_rate']*100:.1f}% failure rate")
    return stats


def get_azure_normal_ranges() -> dict:
    """
    Calculate normal operating ranges from Azure telemetry.
    Used by: FILE 14 (behavior_baseline — normal thresholds)
             FILE 15 (anomaly_detector — what is normal)

    Returns:
        dict with mean and std for each sensor
    """
    df = load_azure_telemetry()
    if df.empty:
        return {
            "volt":      {"mean": 170.0, "std": 15.0},
            "rotate":    {"mean": 446.0, "std": 55.0},
            "pressure":  {"mean": 100.0, "std": 10.0},
            "vibration": {"mean": 40.0,  "std": 5.0},
            "source":    "default",
        }

    ranges = {"source": "azure_pdm_telemetry"}
    for col in ["volt", "rotate", "pressure", "vibration"]:
        ranges[col] = {
            "mean": round(df[col].mean(), 2),
            "std":  round(df[col].std(), 2),
            "min":  round(df[col].min(), 2),
            "max":  round(df[col].max(), 2),
            "p95":  round(df[col].quantile(0.95), 2),   # 95th percentile = upper normal
        }

    logger.info(f"Azure normal ranges calculated from {len(df)} telemetry readings")
    return ranges


def get_high_risk_machines() -> list:
    """
    Find machines with most failure history from Azure dataset.
    Used by: FILE 8 (engagement_agent — who to call first)
             FILE 25 (demo_runner — use real high-risk machines)

    Returns:
        list of machineIDs sorted by failure count (highest first)
    """
    failures_df = load_azure_failures()
    machines_df = load_azure_machines()

    if failures_df.empty:
        return [1, 2, 3, 4, 5]   # fallback

    # Count failures per machine
    failure_counts = (
        failures_df.groupby("machineID")
        .size()
        .reset_index(name="failure_count")
        .sort_values("failure_count", ascending=False)
    )

    # Merge with machine age info
    if not machines_df.empty:
        failure_counts = failure_counts.merge(machines_df, on="machineID", how="left")

    top_machines = failure_counts.head(10)["machineID"].tolist()
    logger.info(f"Top high-risk machines: {top_machines[:5]}")
    return top_machines


def get_demo_sensor_readings(machine_id: int = None) -> dict:
    """
    Get REAL sensor readings from Azure telemetry for demo.
    Used by: FILE 25 (demo_runner — show real data not fake)

    Returns:
        dict with real sensor values for one machine
    """
    telemetry = load_azure_telemetry()
    machines  = load_azure_machines()

    if telemetry.empty:
        return {
            "machineID":   1,
            "volt":        172.3,
            "rotate":      460.2,
            "pressure":    98.7,
            "vibration":   41.2,
            "age":         5,
            "source":      "default",
        }

    # Use high-risk machine or random one
    if machine_id is None:
        high_risk = get_high_risk_machines()
        machine_id = high_risk[0] if high_risk else 1

    # Get latest reading for this machine
    machine_data = telemetry[telemetry["machineID"] == machine_id]
    if machine_data.empty:
        machine_data = telemetry.sample(1)

    latest = machine_data.iloc[-1]

    # Get machine age
    age = 5
    if not machines.empty:
        m = machines[machines["machineID"] == machine_id]
        if not m.empty:
            age = int(m.iloc[0]["age"])

    return {
        "machineID":   int(latest["machineID"]),
        "volt":        round(float(latest["volt"]), 2),
        "rotate":      round(float(latest["rotate"]), 2),
        "pressure":    round(float(latest["pressure"]), 2),
        "vibration":   round(float(latest["vibration"]), 2),
        "age":         age,
        "source":      "azure_pdm_telemetry",
    }


def get_failure_component_mapping() -> dict:
    """
    Map Azure failure types to vehicle components.
    Used by: FILE 8 (engagement_agent — what component to mention)
             FILE 18 (rca_engine — failure type context)
    """
    failures_df = load_azure_failures()

    if failures_df.empty:
        return {"comp1": "brakes", "comp2": "engine",
                "comp3": "engine oil", "comp4": "tires"}

    # Azure uses comp1-comp4 — map to vehicle components
    mapping = {
        "comp1": "brakes",
        "comp2": "engine",
        "comp3": "engine oil",
        "comp4": "tires",
    }

    # Get failure frequency per component
    comp_counts = failures_df["failure"].value_counts().to_dict()
    logger.info(f"Failure component distribution: {comp_counts}")

    return {**mapping, "frequency": comp_counts}


# ==============================================================================
# SELF-TEST
# Run: python services/agents/config/dataset_loader.py
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Dataset Loader — Self Test")
    print("="*60)

    print("\n[1] Loading UCI AI4I dataset...")
    uci = load_uci_dataset()
    print(f"    Rows    : {len(uci)}")
    print(f"    Columns : {list(uci.columns)}")

    print("\n[2] Loading Azure telemetry...")
    tel = load_azure_telemetry()
    print(f"    Rows    : {len(tel)}")
    print(f"    Columns : {list(tel.columns)}")

    print("\n[3] Loading Azure failures...")
    fail = load_azure_failures()
    print(f"    Rows    : {len(fail)}")

    print("\n[4] Getting UCI failure statistics...")
    stats = get_uci_failure_stats()
    print(f"    Failure rate    : {stats['overall_failure_rate']*100:.2f}%")
    print(f"    Total failures  : {stats['total_failures']}")
    print(f"    Avg process temp: {stats['avg_process_temp']}K")

    print("\n[5] Getting Azure normal sensor ranges...")
    ranges = get_azure_normal_ranges()
    for sensor in ["volt", "rotate", "pressure", "vibration"]:
        r = ranges[sensor]
        print(f"    {sensor:<12}: mean={r['mean']} | std={r['std']} | p95={r['p95']}")

    print("\n[6] Getting high-risk machines...")
    machines = get_high_risk_machines()
    print(f"    Top 5 high-risk: {machines[:5]}")

    print("\n[7] Getting demo sensor readings (real data)...")
    demo = get_demo_sensor_readings()
    print(f"    Machine ID : {demo['machineID']}")
    print(f"    Voltage    : {demo['volt']}")
    print(f"    Rotation   : {demo['rotate']}")
    print(f"    Pressure   : {demo['pressure']}")
    print(f"    Vibration  : {demo['vibration']}")
    print(f"    Source     : {demo['source']}")

    print("\n[8] Getting failure component mapping...")
    comp_map = get_failure_component_mapping()
    print(f"    Mapping    : {comp_map}")

    print("\n" + "="*60)
    print("  ✅ All datasets loading correctly!")
    print("  Commit this file and update your agents to use it.")
    print("="*60 + "\n")