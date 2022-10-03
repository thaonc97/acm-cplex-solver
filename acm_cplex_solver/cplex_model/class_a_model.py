from dataclasses import astuple, dataclass, field

from toml import TomlArraySeparatorEncoder

@dataclass
class ClassAModel:
    r: float
    ratio: float
    total_b_c_network: float
    total_b_c_domain: float
    x_a: float
