from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class BruteForceConfig:
    failure_threshold: int = 5
    window_seconds: int = 60
    critical_multiplier: int = 3


@dataclass(slots=True)
class SuspiciousIPConfig:
    request_rate_threshold: int = 120
    request_rate_window_seconds: int = 60
    error_ratio_threshold: float = 0.5
    error_ratio_min_requests: int = 10
    sensitive_paths: set[str] = field(
        default_factory=lambda: {
            "/.env",
            "/.git/config",
            "/wp-admin",
            "/wp-login.php",
            "/phpmyadmin",
            "/admin",
            "/backup",
            "/config.php",
            "/xmlrpc.php",
        }
    )


@dataclass(slots=True)
class PipelineConfig:
    brute_force: BruteForceConfig = field(default_factory=BruteForceConfig)
    suspicious_ip: SuspiciousIPConfig = field(default_factory=SuspiciousIPConfig)
    rules_file: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[3] / "rules" / "default_rules.yml"
    )
    anomaly_window_seconds: int = 60
    anomaly_baseline_windows: int = 5
    anomaly_min_events: int = 12
    anomaly_spike_multiplier: float = 3.0
