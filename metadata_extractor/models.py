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
    """Author of the scientific publication information is extracted from, Schema.org Person object"""
    name: str
    affiliation: Optional[str]

class Journal(StrictBaseModel):
    """Journal information of the scientific publication information is extracted from, Schema.org Periodical object"""
    name: str
    issn: Optional[str]
    publisher: Optional[str]

class CitationMetadata(StrictBaseModel):
    """Metadata about the scientific publication the information is extracted from, Schema.org ScholarlyArticle object"""
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




# Metadata models for LTE Overview Map
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

class TrialDesign(StrictBaseModel):
    """Detailed information about the experimental design of the LTE."""
    randomization: Optional[bool]
    replication: Optional[int]
    number_plots: Optional[int]
    size_plots: Optional[float]

class SoilInfo(StrictBaseModel):
    """Detailed information about the soil at the LTE site."""
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
    """Contact information for the LTE dataset or experiment."""
    contact_name: Optional[str]
    contact_email: Optional[EmailStr]
    doi: Optional[str]

class TrialTypes(StrictBaseModel): 
    """Types of trials conducted in the LTE."""
    tillage_trial: Optional[bool] # yes/no
    fertilization_trial: Optional[bool] # yes/no
    crop_rotation_trial: Optional[bool] # yes/no
    cover_crop_trial: Optional[bool] # yes/no
    irrigation_trial: Optional[bool] # yes/no
    pest_weed_trial: Optional[bool] # yes/no
    grazing_trial: Optional[bool] # yes/no
    other_trial: Optional[bool] # yes/no


class AGROVOCConcept(StrictBaseModel):
    """AGROVOC concept for crop species, following Schema.org DefinedTerm object"""
    type: str = Field(default="DefinedTerm", alias="@type")
    inDefinedTermSet: str = Field(default="https://www.fao.org/agrovoc/en/", alias="inDefinedTermSet")
    label: str
    uri: Optional[str]

class CropSpecies(StrictBaseModel):
    """Crop species grown in the LTE, represented as AGROVOC concept."""
    type: str = Field(default="CropSpecies", alias="@type")
    name: AGROVOCConcept
    schema_org_type: Optional[str] = "Plant"

class Variable(StrictBaseModel):
    """Variables or research parameters measured in the LTE experiment, following Schema.org PropertyValue object"""
    type: str = Field(default="PropertyValue", alias="@type")
    name: str
    description: str
    unit: Optional[str]
    vocabulary: Optional[str] = "AGROVOC"

class LTEEntry(StrictBaseModel): 
    """Metadata model for the LTE overview map, containing detailed information about the LTE itself, not necessarily reported in the publication text. If not reported in the text, the attribute should be set to null."""
    #id: Optional[int] #
    #index: Optional[int]
    name: Optional[str] # 
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
    #holder_category: Optional[str]
    website: Optional[HttpUrl]
    #networks: Optional[List[str]]
    research_parameters: List[Variable] #  with units if applicable
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
    sources: ContactInfo
    #agrovoc_keywords: Optional[str]


class MetadataExtractionResponse(StrictBaseModel):
    citation: CitationMetadata
    #LTE_metadata: LTEDataMetadata
    LTE_metadata_OverviewMap: LTEEntry 
    #reasoning: Optional[str]