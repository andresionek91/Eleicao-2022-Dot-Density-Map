from dataclasses import dataclass


@dataclass
class Config:
    """Configurations"""

    hosted_zone_type: str = "internal"
    is_private: bool = True
