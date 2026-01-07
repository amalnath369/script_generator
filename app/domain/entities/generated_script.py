from dataclasses import dataclass   



@dataclass(frozen=True, kw_only= True)
class GeneratedScript:

    id: str
    script_id: str
    script: str
    model_name: str


