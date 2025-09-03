from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel
from pydantic import BaseModel, Field, HttpUrl, EmailStr

class StrictBaseModel(PydanticBaseModel):
    model_config = {
        "str_strip_whitespace": True,
        "use_enum_values": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat(),
        },
        "validate_assignment": True,
        "extra": "forbid",
        "validate_by_name": True,
    }

# Publication metadata models
class Author(StrictBaseModel):
    name: str
    affiliation: Optional[str]

class Journal(StrictBaseModel):
    name: str
    issn: Optional[str]
    publisher: Optional[str]

class CitationMetadata(StrictBaseModel):
    title: str
    authors: List[Author]
    journal: Journal
    volume: Optional[str]
    issue: Optional[str]
    pages: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    pubmed_id: Optional[str]
    publication_date: Optional[str]
    year: Optional[int]
    abstract: Optional[str]
    keywords: List[str]
    subject_classifications: List[str]
    language: Optional[str]
    license: Optional[str]
    open_access: Optional[bool]
    funding: Optional[str]
    formatted_citation: Optional[str]


class MetadataExtractionResponse(StrictBaseModel):
    citation: CitationMetadata



  # General LTE and LTE dataset metadata models
class GeoCoverage(StrictBaseModel):
    """Location of the long-term field experiment, Geographic coverage following Schema.org Place object"""
    type: str = Field(default="Place", description="Schema.org type")
    lat1: float
    lon1: float
    lat2: Optional[float]
    lon2: Optional[float]

#class GeoShape(StrictBaseModel):
    #"""Geographic shape following GeoJSON-style bounding box"""
    #type: str = Field(default="GeoShape", description="Schema.org type")
    #box: str = Field(description="Bounding box coordinates as 'lat1 lon1 lat2 lon2'")

class Variable(StrictBaseModel):
    """Variables or research parameters measured in the LTE experiment, following Schema.org PropertyValue object"""
    type: str = Field(default="PropertyValue", alias="@type")
    name: str
    description: str
    unit: Optional[str]
    vocabulary: Optional[str] = "AGROVOC"
    
class DataDistribution(StrictBaseModel):
    """Information on LTE data availability if any is reprorted in the scientific publication text, Schema.org DataDownload object"""
    type: str = Field(default="DataDownload", alias="@type")
    contentUrl: HttpUrl
    encodingFormat: Optional[str] = "text/csv"


class LTEDataMetadata(StrictBaseModel):
    """Metadata about the agricultural long-term experiment (LTE) and dataset(s) collected in the LTE as described in the scientific publication, Schema.org Dataset object"""
    name: str
    description: Optional[str]
    geographic_coverage: Optional[GeoCoverage]
    #bounding_box: Optional[GeoShape]
    temporal_coverage: Optional[str]
    variables: List[Variable]
    dataset_doi: Optional[str]
    format: Optional[str]
    size: Optional[str]
    access_conditions: Optional[str]
    trial_status: Optional[str]
    experimental_setup: Optional[str]
    research_objectives: Optional[str]
    distribution: Optional[DataDistribution]
    license: Optional[str]
    supplementary_materials: Optional[str]


  