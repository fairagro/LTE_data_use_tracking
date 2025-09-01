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


# LTE dataset metadata models
class GeoCoverage(StrictBaseModel):
    lat1: float
    lon1: float
    lat2: Optional[float]
    lon2: Optional[float]

class GeoShape(StrictBaseModel):
    """Geographic shape following GeoJSON-style bounding box"""
    type: str = Field(default="GeoShape", description="Schema.org type")
    box: str = Field(description="Bounding box coordinates as 'lat1 lon1 lat2 lon2'")

class Variable(StrictBaseModel):
    name: str
    description: str
    unit: Optional[str]
    vocabulary: Optional[str] = "AGROVOC"
    
class DataDistribution(StrictBaseModel):
    """Schema.org DataDownload object"""
    type: str = Field(default="DataDownload", alias="@type")
    contentUrl: HttpUrl
    encodingFormat: Optional[str] = "text/csv"


class LTEDataMetadata(StrictBaseModel):
    name: str
    description: Optional[str]
    geographic_coverage: Optional[GeoCoverage]
    bounding_box: Optional[GeoShape]
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

class MetadataExtractionResponse(StrictBaseModel):
    citation: CitationMetadata
    datasets: List[LTEDataMetadata]
    reasoning: Optional[str]


# Metadata models for LTE Overview Map
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

class TrialDesign(StrictBaseModel):
    randomization: Optional[bool]
    replication: Optional[int]
    number_plots: Optional[int]
    size_plots: Optional[float]

class SoilInfo(StrictBaseModel):
    soil_group_wrb: Optional[str]
    soil_type_other: Optional[str]
    parental_material: Optional[str]
    texture: Optional[str]
    texture_sand: Optional[float]
    texture_silt: Optional[float]
    texture_clay: Optional[float]
    bulk_density: Optional[float]
    organic_carbon_prc: Optional[float]
    further_soil_info: Optional[str]

class ContactInfo(StrictBaseModel):
    contact_name: Optional[str]
    contact_email: Optional[EmailStr]
    doi: Optional[str]

class TrialTypes(StrictBaseModel): 
    tillage_trial: Optional[bool] # yes/no
    fertilization_trial: Optional[bool] # yes/no
    crop_rotation_trial: Optional[bool] # yes/no
    cover_crop_trial: Optional[bool] # yes/no
    irrigation_trial: Optional[bool] # yes/no
    pest_weed_trial: Optional[bool] # yes/no
    grazing_trial: Optional[bool] # yes/no
    other_trial: Optional[bool] # yes/no


class AGROVOCConcept(StrictBaseModel):
    label: str
    uri: Optional[str]

class CropSpecies(StrictBaseModel):
    name: AGROVOCConcept
    schema_org_type: Optional[str] = "Plant"


class LTEEntry(StrictBaseModel): #Addd schema.org where makes sense
    id: Optional[int] # make obligatory later
    index: Optional[int]
    name: Optional[str] # make obligatory later
    site: Optional[str] 
    country: Optional[str]
    start_date: Optional[int]
    status: Optional[str] # binary: on-going / finished
    trial_duration: Optional[int] # in years
    trial_status: Optional[str] # Ongoing / finished (with year it finished)
    trial_institution: Optional[str]
    landuse_type: Optional[str] # 
    research_theme: Optional[str] # free text
    trial_types: TrialTypes
    trial_category: Optional[str]
    holder_category: Optional[str]
    website: Optional[HttpUrl]
    #networks: Optional[List[str]]
    research_parameters: Optional[str] #  with units if applicable
    farming_category: Optional[str] 
    #position_exactness: Optional[str]
    size_hectares: Optional[float]
    longitude: Optional[float]
    latitude: Optional[float]
    experimental_setup: Optional[str]
    tillage_levels: Optional[str] 
    fertilization_levels: Optional[str]
    crop_rotation_levels: Optional[List[CropSpecies]]
    cover_crop_levels: Optional[List[CropSpecies]]
    irrigation_levels: Optional[str]
    pest_weed_levels: Optional[str] # Pest and weed management levels
    grazing_levels: Optional[str]
    other_levels: Optional[str]
    one_factorial_lte: Optional[bool]
    two_factorial_lte: Optional[bool]
    multifactorial_lte: Optional[bool]
    trial_design: TrialDesign
    soil_info: SoilInfo
    miscellaneous: Optional[str]
    #literature: Optional[str] # Citation of study at hand, taken form CitationMetadata
    #sources: Optional[str]
    agrovoc_keywords: Optional[str]
