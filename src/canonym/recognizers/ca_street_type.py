#####################################################################################################################
#                                     Canadian Street types Recognizer                                              #
#                                                                                                                   #
#                                                                                                                   #
#                                      Info scrapped from Canada Post                                               #
#  https://www.canadapost-postescanada.ca/scp/fr/soutien/sujet/directives-adressage/symboles-et-abreviations.page   #
#                                                                                                                   #
#####################################################################################################################

from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import Optional
import csv
from importlib_resources import files
from  pathlib import Path
################################################################

class CaStreetTypeRecognizer(PatternRecognizer):
    ''' Matches street types'''
    
    SUPPORTED_ENTITY = 'STREET_TYPE'
    CA_STREET_TYPES_CSV_PATH = files('canonym.config').joinpath('CA_Street_types.csv')
    CONTEXTUAL_ENTITIES = {'CANADA_POST_CODE', 'NUMBER', 'LOCATION'}
    SPACING = 7
    SCORE_THRESHOLD = 0.4

    def __init__(self, supported_language:str = 'en'):
        street_types = list(self.load_street_types())
        super().__init__(supported_entity=self.SUPPORTED_ENTITY,
                         supported_language = supported_language,
                         deny_list=street_types,
                         deny_list_score=0.1)
        self.score = 0.1

    def load_street_types(self):
        street_types_path = Path(self.CA_STREET_TYPES_CSV_PATH)
        with open(street_types_path, newline='') as f:
            reader = csv.reader(f)
            street_types = list([street[0] for street in reader][1:])  # Picking only the first columns [0] and dropping the header [1:]
        street_types += [st.upper() for st in street_types]
        street_types += [st.lower() for st in street_types]
        street_types += [st.title() for st in street_types]
        street_types.sort()
        return set(street_types)

    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Enhance confidence score to show only IDs len >5 and that are not inside an other entity."""

        for result in raw_recognizer_results:
            for other_result in other_raw_recognizer_results:
                if other_result.entity_type not in self.CONTEXTUAL_ENTITIES: 
                    continue
                if other_result.score <= self.SCORE_THRESHOLD:
                    continue
                right_dif = other_result.start - result.end
                left_dif = result.start - other_result.end 
                if right_dif >= 0 and right_dif <= self.SPACING:
                    result.score += 0.3
                if left_dif >= 0 and left_dif <= self.SPACING:
                    result.score += 0.3

        return raw_recognizer_results
 