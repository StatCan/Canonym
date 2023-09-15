##############################################################
#             DateTimeDaySuffixEnhancer Enhancer             #
#                                                            #
#        Takes care of dates not recognized because          #
#        of the suffix                                       #
##############################################################

from .result_enhancer import ResultEnhancer
from presidio_analyzer import RecognizerResult 
###############################################################

class DateTimeDaySuffixEnhancer(ResultEnhancer):
    ''' The goal of this enhancer is to extend dates if the day was not captured because of the suffix like st or th  '''
    
    ENTITY_TYPE = 'DATE_TIME'
    SUFFIXES = ['th', 'st', 'rd', 'nd'] 
    
    def enhance(self):
        output=[]
        
        for result in self.raw_recognizer_results:
            # Skipping over other entity types
            if result.entity_type != self.ENTITY_TYPE:
                output.append(result)
                continue
                
            # If DATE_TIME checking the amount of digits in the matched text
            matched_text = self.text[result.start:result.end]
            previous_word = self.text[:result.start].strip().rsplit(' ', maxsplit=1)[-1]  # Previous word matching
            if any(suffix in previous_word for suffix in self.SUFFIXES):
                if any(c.isdigit() for c in previous_word):
                    result.start = self.text[:result.start].rfind(previous_word)
            output.append(result)
            
        return output