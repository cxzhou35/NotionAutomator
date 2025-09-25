import os
from .base_utils import DotDict
from .console_utils import *

def load_config(config_path: str):
    assert os.path.exists(config_path), f"config file not found: {config_path}"
    with open(config_path, "r") as f:
        cfg = yaml.load(f)

    def convert_to_dict(obj):
        if hasattr(obj, 'items'):
            return {k: convert_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_dict(item) for item in obj]
        else:
            return obj

    cfg_dict = convert_to_dict(cfg)
    return DotDict(cfg_dict)


def save_config(cfg: DotDict, output_path: str):
    with open(output_path, "w") as f:
        yaml.dump(cfg.todict(), f)
