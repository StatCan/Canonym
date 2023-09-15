################################################################
#                 Alpha Numeric ID Recognizer                  #
#                                                              #
#                                                              #
#                                                              #
#                                                              #
#                                                              #
################################################################
from typing import Optional
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer import RecognizerResult
from .custom_regex_recognizer import CustomRegexRecognizer

################################################################


class AlphaNumericIDRecognizer(CustomRegexRecognizer):
    ''' AlphaNumericID '''
    
    MINIMUM_LENGTH = 5
    
    def __init__(self, supported_language:str = 'en'):
        regex = r"\b(?:[0-9]+[a-zA-Z]|[a-zA-Z]+[0-9])[a-zA-Z0-9]*\b"
        context_list = ['ID', 'numéro', '#', 'nr'] if supported_language == 'fr' else ['ID', 'number', 'nbr', '#']
        super().__init__(name="AlphaNumeric_ID", regex=regex, context=context_list, supported_language=supported_language)
        
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
            if (result.end-result.start) < self.MINIMUM_LENGTH:
                result.score = 0.3
                result.recognition_metadata[RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY] = True
            for other_result in other_raw_recognizer_results:
                if result.contained_in(other_result):
                    result.score = 0.3
                    result.recognition_metadata[RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY] = True
                    break

        return raw_recognizer_results