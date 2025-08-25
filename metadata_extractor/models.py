from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel

class StrictBaseModel(PydanticBaseModel):
    class Config:
        anystr_strip_whitespace = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        allow_population_by_field_name = True
        validate_assignment = True
        extra = "forbid"

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

class GeoCoverage(StrictBaseModel):
    lat1: float
    lon1: float
    lat2: Optional[float]
    lon2: Optional[float]

class Variable(StrictBaseModel):
    name: str
    description: str
    unit: Optional[str]
    vocabulary: Optional[str] = "AGROVOC"

class LTEDataMetadata(StrictBaseModel):
    name: str
    description: Optional[str]
    geographic_coverage: Optional[GeoCoverage]
    temporal_coverage: Optional[str]
    variables: List[Variable]
    dataset_doi: Optional[str]
    format: Optional[str]
    size: Optional[str]
    access_conditions: Optional[str]
    trial_status: Optional[str]
    experimental_setup: Optional[str]
    research_objectives: Optional[str]

class MetadataExtractionResponse(StrictBaseModel):
    citation: CitationMetadata
    datasets: List[LTEDataMetadata]
    reasoning: Optional[str]
