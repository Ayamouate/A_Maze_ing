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
    seed : Optional[int] = None

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, value: Any) -> tuple[int, int]:
        """Convert string 'x,y' to tuple of integers if needed."""
        if isinstance(value, str):
            try:
                x, y = value.split(",")
                return int(x.strip()), int(y.strip())
            except ValueError:
                raise ValueError("Coordinates must be in format 'x,y'")
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
        return self

    def as_dict(self) -> dict[str, Any]:
        """Return configuration as dictionary."""
        return self.model_dump()


class ConfigReader:
    """Read and parse maze configuration from a file."""
    REQUIRED_KEYS = {"width", "height", "entry", "exit", "output_file", "perfect"}
    OPTIONAL_KEYS = {"seed"}

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
                        raise ValueError(f"Invalid line: '{line}' (missing '=')")

                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key in data:
                        raise ValueError(f"Duplicate key: {key}")

                    data[key] = value
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {self.path}")

        # Check required keys
        missing = self.REQUIRED_KEYS - data.keys()
        if missing:
            raise ValueError(f"Missing required keys: {missing}")

        # Convert types
        data["width"] = int(data["width"])
        data["height"] = int(data["height"])
        data["perfect"] = data["perfect"].lower() == "true"

        # Handle optional seed
        if "seed" in data and data["seed"]:
            data["seed"] = int(data["seed"])
        else:
            data["seed"] = None

        return data


def load_config(path: str) -> MazeConfig:
    """Load and validate config from file."""
    reader = ConfigReader(path)
    data = reader.read()
    return MazeConfig(**data)


if __name__ == "__main__":
    config = load_config("config.txt")
    print(config.as_dict())
