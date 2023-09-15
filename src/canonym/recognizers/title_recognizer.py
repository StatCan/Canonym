################################################################
#                        Title Recognizer                      #
#                                                              #
#       Identifies Gendered Titles   in French and English     #
#                                                              #
################################################################

from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import Optional

################################################################


   
class TitleRecognizer(PatternRecognizer):
    ''' Recognizer for gendered titles'''
    
    
    CONTEXTUAL_ENTITIES = 'PERSON'
    SCORE_THRESHOLD = 0.4
    SUPPORTED_ENTITY = 'TITLE'
    SPACING = 3
    
    # English
    EN_PRONOUNS = {'Mr', 'Ms', 'Miss', 'Mrs', 'Mister', 'Madam', 'Master'}
    EN_PRONOUNS.update({pr.title() for pr in EN_PRONOUNS})
    EN_PRONOUNS.update({pr.upper() for pr in EN_PRONOUNS})
    
    # French
    FR_PRONOUNS = {'M', 'Mme', 'Mr', 'Mmes', 'Ms', 'Mlle'}
    FR_PRONOUNS.update({pr.title() for pr in FR_PRONOUNS})
    FR_PRONOUNS.update({pr.upper() for pr in FR_PRONOUNS})

    def __init__(self, supported_language: str = 'en'):

        if supported_language == 'en':
            deny_list = self.EN_PRONOUNS.copy()
        elif supported_language == 'fr':
            deny_list = self.FR_PRONOUNS.copy()
        else:
            raise ValueError(f"Language : '{supported_language}' not supported by TitleRecognizer") 

        super().__init__(
            supported_entity= self.SUPPORTED_ENTITY,
            supported_language= supported_language,
            deny_list= deny_list,
            deny_list_score= 0.1,
            name= 'TitleRecognizer',
        )

    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Enhance confidence score to show only titles close to a PERSON entity."""

        for result in raw_recognizer_results:
            for other_result in other_raw_recognizer_results:
                if other_result.entity_type not in self.CONTEXTUAL_ENTITIES: 
                    continue
                if other_result.score <= self.SCORE_THRESHOLD:
                    continue
                right_dif = other_result.start - result.end
                
                if right_dif >= 0 and right_dif <= self.SPACING:
                    result.score += 0.3
    
        return raw_recognizer_results