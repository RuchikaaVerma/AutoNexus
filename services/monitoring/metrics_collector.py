"""
PURPOSE: Collects Prometheus metrics for Grafana dashboard.
CONNECTS TO: All agent files, FILE 1 (config)
"""
import logging, time
from services.agents.config.hf_model_config import PROMETHEUS_PORT, ENABLE_METRICS
logger = logging.getLogger(__name__)

# Lazy import — only load prometheus if metrics enabled
_counters = {}
_gauges   = {}
_started  = False


def _init_metrics():
    global _started
    if _started or not ENABLE_METRICS:
        return
    try:
        from prometheus_client import Counter, Gauge, start_http_server
        _counters["calls_total"]     = Counter("autonexus_calls_total",     "Total calls made", ["outcome"])
        _counters["sms_total"]       = Counter("autonexus_sms_total",       "Total SMS sent",   ["status"])
        _counters["emails_total"]    = Counter("autonexus_emails_total",    "Total emails sent",["status"])
        _counters["ueba_alerts"]     = Counter("autonexus_ueba_alerts",     "UEBA alerts",      ["level"])
        _gauges["active_agents"]     = Gauge(  "autonexus_active_agents",   "Active agents count")
        _gauges["booking_rate"]      = Gauge(  "autonexus_booking_rate",    "Booking conversion rate")
        _gauges["last_anomaly_score"]= Gauge(  "autonexus_last_anomaly_score","Last UEBA anomaly score")
        start_http_server(PROMETHEUS_PORT)
        _started = True
        logger.info(f"Prometheus metrics server started on port {PROMETHEUS_PORT}")
    except Exception as e:
        logger.warning(f"Prometheus init skipped: {e}")


def record_call(outcome: str):
    _init_metrics()
    if "calls_total" in _counters:
        _counters["calls_total"].labels(outcome=outcome).inc()


def record_sms(status: str):
    _init_metrics()
    if "sms_total" in _counters:
        _counters["sms_total"].labels(status=status).inc()


def record_email(status: str):
    _init_metrics()
    if "emails_total" in _counters:
        _counters["emails_total"].labels(status=status).inc()


def record_ueba_alert(level: str, score: int):
    _init_metrics()
    if "ueba_alerts" in _counters:
        _counters["ueba_alerts"].labels(level=level).inc()
    if "last_anomaly_score" in _gauges:
        _gauges["last_anomaly_score"].set(score)


def set_active_agents(count: int):
    _init_metrics()
    if "active_agents" in _gauges:
        _gauges["active_agents"].set(count)


def set_booking_rate(rate: float):
    _init_metrics()
    if "booking_rate" in _gauges:
        _gauges["booking_rate"].set(rate)


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  FILE 21: Metrics Collector — Self Test")
    print("="*55)
    _init_metrics()
    record_call("appointment_booked")
    record_call("appointment_declined")
    record_sms("success")
    record_email("success")
    record_ueba_alert("HIGH", 75)
    set_active_agents(4)
    set_booking_rate(0.68)
    print(f"\n  Metrics recorded ✅")
    print(f"  Prometheus port : {PROMETHEUS_PORT}")
    print(f"  Metrics enabled : {ENABLE_METRICS}")
    print("  FILE 21 complete!\n")