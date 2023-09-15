##############################################################
#             DateTimeMinDigitsEnhancer Enhancer             #
#                                                            #
#        Spacy tends to recognize vague DATE_TIME entities   #
#        if this enhancer will reduce their score            #
##############################################################

from .result_enhancer import ResultEnhancer
from presidio_analyzer import RecognizerResult 
###############################################################

class DateTimeMinDigitsEnhancer(ResultEnhancer):
    ''' The goal of this enhancer is to remove non-specific dates, meaning time periods 
        like "last year" or "a week" that get recognized as a DATE_TIME enitity by the Spacy models. 
        We wil reduce the score of DATE_TIME entities that dont have a minimum amount of digits '''

    ENTITY_TYPE = 'DATE_TIME'
    MINIMUM_DIGITS = 3 

    def enhance(self):
        output=[]

        for result in self.raw_recognizer_results:
            # Skipping over other entity types
            if result.entity_type != self.ENTITY_TYPE:
                output.append(result)
                continue

            # If DATE_TIME checking the amount of digits in the matched text
            matched_text = self.text[result.start:result.end]
            number_digits = sum([c.isdigit() for c in matched_text])
            if number_digits < self.MINIMUM_DIGITS:
                result.score = 0.1
                result.recognition_metadata[RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY] = True
            output.append(result)

        return output