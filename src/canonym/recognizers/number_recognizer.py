################################################################
#                       Number Recognizer                      #
#                                                              #
#                   Generic Number Recognizer                  #
#                                                              #
#                                                              #
#                                                              #
################################################################
from typing import Optional
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer import RecognizerResult
from .custom_regex_recognizer import CustomRegexRecognizer

################################################################


class NumberRecognizer(CustomRegexRecognizer):
    ''' Generic number recognizer '''

    def __init__(self, supported_language: str = 'en'):
        regex = [r"\b\d{1,5}[ ,-]?\d{1,5}\b", r"\b\d+\b"]
        score = 0.4
        context = ['numero', 'nr', 'numéro', '#', 'No', 'addresse'] if supported_language == 'fr' else ['number', 'nr', 'nbr', '#', 'No', 'address']
        super().__init__(name="number", regex=regex, score=score, supported_language=supported_language, context=context)

        
    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Enhance confidence score to show only numbers that are not inside an other entity."""

        for result in raw_recognizer_results:
            for other_result in other_raw_recognizer_results:
                if result.contained_in(other_result) and other_result.score >= self.score:
                    result.score -= 0.1
                    break

        return raw_recognizer_results