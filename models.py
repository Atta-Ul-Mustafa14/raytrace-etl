from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class RayRow(BaseModel):
    pixel_x: int = Field(ge=0)
    pixel_y: int = Field(ge=0)
    hit: bool
    surface: Literal["sky", "sphere_1", "sphere_2", "sphere_3", "floor"]
    distance: Optional[float] = Field(default=None, gt=0)
    brightness: float = Field(ge=0, le=1)
    nx: float
    ny: float
    nz: float

    @model_validator(mode="after")
    def check(self):
        if self.hit != (self.surface != "sky"):
            raise ValueError("hit flag disagrees with surface")
        if self.hit:
            if self.distance is None:
                raise ValueError("hit ray needs a distance")
            if abs((self.nx ** 2 + self.ny ** 2 + self.nz ** 2) ** 0.5 - 1) > 0.01:
                raise ValueError("normal is not unit length")
        return self
