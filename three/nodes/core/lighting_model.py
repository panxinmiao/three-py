class LightingModel:

    def __init__(self, direct = None, indirectDiffuse = None, indirectSpecular = None, ambientOcclusion = None) -> None:
        
        self.direct = direct
        self.indirectDiffuse = indirectDiffuse
        self.indirectSpecular = indirectSpecular
        self.ambientOcclusion = ambientOcclusion
