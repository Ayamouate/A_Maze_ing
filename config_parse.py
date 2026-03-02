from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Any


class MazeConfig(BaseModel):
    """Maze configuration validator using Pydantic."""
    width: int = Field(..., gt=2, lt=100)
    height: int = Field(..., gt=2, lt=100)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algo: Optional[str] = "DFS"

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, value: Any) -> tuple[int, int]:
        """Convert string 'x,y' to tuple of integers if needed."""
        if isinstance(value, str):
            try:
                parts = value.split(",")
                if len(parts) != 2:
                    raise ValueError("Coordinates must be in format 'x,y'")
                x, y = parts
                return int(x.strip()), int(y.strip())
            except ValueError:
                raise ValueError("Coordinates must be 'x,y' with integers")
        return value

    @model_validator(mode="after")
    def validate_positions(self) -> "MazeConfig":
        """Validate entry and exit are within maze bounds and different."""
        x1, y1 = self.entry
        x2, y2 = self.exit

        if not (0 <= x1 < self.width and 0 <= y1 < self.height):
            raise ValueError(f"Entry {self.entry} is out of bounds")
        if not (0 <= x2 < self.width and 0 <= y2 < self.height):
            raise ValueError(f"Exit {self.exit} is out of bounds")
        if self.entry == self.exit:
            raise ValueError("Entry and exit cannot be the same")

        # Validate entry is on border
        if not (x1 == 0 or x1 == self.width - 1
                or y1 == 0 or y1 == self.height - 1):
            raise ValueError(f"Entry {self.entry} must be on the maze border")
        # Validate exit is on border
        if not (x2 == 0 or x2 == self.width - 1
                or y2 == 0 or y2 == self.height - 1):
            raise ValueError(f"Exit {self.exit} must be on the maze border")

        return self

    def as_dict(self) -> dict[str, Any]:
        """Return configuration as dictionary."""
        return self.model_dump()


class ConfigReader:
    """Read and parse maze configuration from a file."""
    REQ_KEYS = {"width", "height", "entry", "exit", "output_file", "perfect"}
    OPT_KEYS = {"seed", "algo"}
    ALL_KEYS = REQ_KEYS | OPT_KEYS

    def __init__(self, path: str) -> None:
        """Store file path."""
        self.path = path

    def read(self) -> dict[str, Any]:
        """Parse the config file and return validated dictionary."""
        data: dict[str, Any] = {}

        try:
            with open(self.path) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if not line:
                        continue

                    if "=" not in line:
                        raise ValueError(f"Invalid line: '{line}' (need '=')")

                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    # Check for unknown keys
                    if key not in self.ALL_KEYS:
                        raise ValueError(f"Unknown key: '{key}'")

                    # Check for empty value
                    if not value:
                        raise ValueError(f"Empty value for key: '{key}'")

                    if key in data:
                        raise ValueError(f"Duplicate key: '{key}'")

                    data[key] = value
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {self.path}")

        # Check required keys
        missing = self.REQ_KEYS - data.keys()
        if missing:
            raise ValueError(f"Missing required keys: {missing}")

        # Convert width
        try:
            data["width"] = int(data["width"])
        except ValueError:
            raise ValueError(f"Invalid width: '{data['width']}' must be int")

        # Convert height
        try:
            data["height"] = int(data["height"])
        except ValueError:
            raise ValueError(f"Invalid height: '{data['height']}' must be int")

        # Convert perfect (must be "true" or "false")
        if data["perfect"].lower() not in ("true", "false"):
            raise ValueError(f"Invalid perfect:'{data['perfect']}' true/false")
        data["perfect"] = data["perfect"].lower() == "true"

        # Handle optional seed
        if "seed" in data and data["seed"]:
            try:
                data["seed"] = int(data["seed"])
            except ValueError:
                raise ValueError(f"Invalid seed: '{data['seed']}' must be int")
        else:
            data["seed"] = None

        # Handle optional algo
        if "algo" in data:
            if data["algo"].upper() not in ("DFS", "PRIM"):
                raise ValueError(f"Invalid algo: '{data['algo']}' ('DFS/PRIM)")
            data["algo"] = data["algo"].upper()
        return data


def load_config(path: str) -> MazeConfig:
    """Load and validate config from file."""
    reader = ConfigReader(path)
    data = reader.read()
    return MazeConfig(**data)


if __name__ == "__main__":
    try:
        config = load_config("config.txt")
        print(config.as_dict())
    except ValueError as e:
        print(f"Error: {e}")
