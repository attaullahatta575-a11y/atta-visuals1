from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class ProductAnalysis:
    product_type: str = ""
    target_customer: str = ""
    purpose: str = ""
    visible_features: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    selling_points: List[str] = field(default_factory=list)
    design_style: str = ""
    color_palette: List[str] = field(default_factory=list)
    typography: str = ""
    verified_specs: List[str] = field(default_factory=list)


@dataclass
class ImagePlan:
    number: int
    name: str
    purpose: str
    headline: str
    supporting_copy: str
    features: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    specs: List[str] = field(default_factory=list)
    layout: str = ""
    background: str = ""
    palette: List[str] = field(default_factory=list)


@dataclass
class ListingPlan:
    product: ProductAnalysis
    images: List[ImagePlan] = field(default_factory=list)
