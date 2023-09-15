##############################################################
#                   Country Recognizer                       #
#                                                            #
#                                                            #
##############################################################
from pathlib import Path
from typing import Optional
from importlib_resources import files
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer import RecognizerResult, PatternRecognizer
#############################################################


class CountriesRecognizer(PatternRecognizer):

    COUNTRY_SHORT_TEXT_PATH = files('canonym.config').joinpath('countries_short.txt')
    COUNTRY_FULL_TEXT_PATH = files('canonym.config').joinpath('countries_full.txt')

    PREFERRED_ENTITIES = {'CANADA_POST_CODE', 'LOCATION', 'PROVINCE'}
    OVERLAP_ENTITY = {'LOCATION'}
    # Distance set for enhancing a result if a PREFERRED_ENTITIES is nearby
    DISTANCE = 5

    def __init__(self, **kwargs):
        self.COUNTRIES = self.load_countries(self.COUNTRY_SHORT_TEXT_PATH)
        self.COUNTRIES_FULL = self.load_countries(self.COUNTRY_FULL_TEXT_PATH)
        super().__init__(supported_entity='COUNTRY',
                         deny_list=self.COUNTRIES.union(self.COUNTRIES_FULL),
                         deny_list_score=0.1)
        self.name = 'PresidioCountries'
        self.score = 0.1
        self.supported_language = kwargs.pop('supported_language', 'en')

    def load_countries(self, file_path):
        country_path = Path(file_path)
        my_file = open(country_path, "r")
        data = my_file.read()
        country_list = data.split("\n")
        my_file.close()
        if len(country_list[0])>3:
            country_list.extend({country.lower() for country in country_list}) 
            country_list.extend({country.upper() for country in country_list})
#         elif len(country_list[0])<=3:
#             country_list.extend({country.lower() for country in country_list})
        return set(country_list)

    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Enhance confidence score by looking at the context"""
        # merging and sorting all results by start
        results = raw_recognizer_results + other_raw_recognizer_results
        results = sorted(results, key=lambda x: x.start)

        for i, result in enumerate(results):
            # Skipping if the result is not a COUNTRY - same routine as provinces for full address
            if result.entity_type != 'COUNTRY':
                continue 
            if text[result.start:result.end] in self.COUNTRIES_FULL:  #  Giving higher score if the country is fully spelled 
                result.score += 0.8
#             if text[result.start:result.end].isupper():  # Giving higher score if the country is in all caps
#                 result.score += 0.2

            distance_to_previous = result.start - results[i-1].end if i > 0 else 1000
            distance_to_next = results[i+1].start - result.end if i < len(results)-1 else 1000

            if i > 0 and (results[i-1].entity_type in self.PREFERRED_ENTITIES) and (distance_to_previous<self.DISTANCE):
                result.score += 0.2
            if i < len(results)-1 and (results[i+1].entity_type in self.PREFERRED_ENTITIES)  and (distance_to_next<self.DISTANCE):
                result.score += 0.2

            result.score = min(result.score, 1)
            result.recognition_metadata[RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY] = True
        return results