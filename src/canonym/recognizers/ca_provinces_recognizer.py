################################################################
#                Canadian Provinces Recognizer                 #
#                                                              #
#        Canadian Provinces and Territories Recognizer         #
#                                                              #
#                                                              #
#                                                              #
################################################################

from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import Optional

################################################################


   
class CaProvincesRecognizer(PatternRecognizer):
    ''' Recognizer for Canadian Provinces and Territories'''
    
    PROVINCES_TERRITORIES = {'ON', 'QC', 'NS', 'NB', 'MB', 'BC', 'PE', 'SK', 'AB', 'NL', 'NT', 'YT', 'NU'}
    PROVINCES_TERRITORIES.update({prov.lower() for prov in PROVINCES_TERRITORIES })  # Adding lower cases 
    PROVINCES_TERRITORIES_FULL = {'Alberta',
                                  'British Columbia',
                                  'Manitoba',
                                  'New Brunswick',
                                  'Newfoundland and Labrador',
                                  'Northwest Territories',
                                  'Nova Scotia',
                                  'Nunavut',
                                  'Ontario',
                                  'Prince Edward Island',
                                  'Quebec',
                                  'Québec',
                                  'Saskatchewan',
                                  'Yukon'}
    
    # Adding lower and upper case variants
    PROVINCES_TERRITORIES_FULL.update({prov.lower() for prov in PROVINCES_TERRITORIES_FULL }) 
    PROVINCES_TERRITORIES_FULL.update({prov.upper() for prov in PROVINCES_TERRITORIES_FULL })
    
    PREFERRED_ENTITIES = {'CANADA_POST_CODE', 'LOCATION'}
    #Distance set for enhancing a result if a PREFERRED_ENTITIES is nearby
    DISTANCE = 5

    def __init__(self, supported_language: str = 'en', **kwargs):

        super().__init__(
                         supported_entity='PROVINCE',
                         deny_list = self.PROVINCES_TERRITORIES.union(self.PROVINCES_TERRITORIES_FULL),
                         deny_list_score=0.1,
                         supported_language=supported_language)
        self.score = 0.1


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
            # Skipping if the result is not a PROVINCE 
            if result.entity_type != 'PROVINCE':
                continue 
            if text[result.start:result.end] in self.PROVINCES_TERRITORIES_FULL:  #  Giving higher score if the province is fully spelled 
                result.score += 0.8
            if text[result.start:result.end].isupper():  # Giving higher score if the province is in all caps
                result.score += 0.2
            
            # Looking at the distance from the province to a preferred entity 
            distance_to_previous = result.start - results[i-1].end if i > 0 else 1000
            distance_to_next = results[i+1].start - result.end if i < len(results)-1 else 1000
            
            if i > 0 and (results[i-1].entity_type in self.PREFERRED_ENTITIES ) and (distance_to_previous<self.DISTANCE):
                result.score += 0.2
            if i < len(results)-1 and (results[i+1].entity_type in self.PREFERRED_ENTITIES)  and (distance_to_next<self.DISTANCE):
                result.score += 0.2
            result.score = min(result.score, 1)
            result.recognition_metadata[RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY] = True
        return results
