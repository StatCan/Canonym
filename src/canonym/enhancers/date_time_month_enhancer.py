##############################################################
#             DateTimeMonthEnhancer Enhancer                 #
#                                                            #
#        Takes care of full Months not recognized            #
#                                                            #
##############################################################

from .result_enhancer import ResultEnhancer
from presidio_analyzer import RecognizerResult 
###############################################################

class DateTimeMonthEnhancer(ResultEnhancer):
    ''' The goal of this enhancer is to extend dates if the Month was not captured '''
    
    ENTITY_TYPE = 'DATE_TIME'
    MONTHS = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December',
              'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    def enhance(self):
        output=[]
        
        for result in self.raw_recognizer_results:
            # Skipping over other entity types
            if result.entity_type != self.ENTITY_TYPE:
                output.append(result)
                continue
                
            # If DATE_TIME checking the amount of digits in the matched text
            matched_text = self.text[result.start:result.end]
            previous_word = self.text[:result.start].strip().rsplit(' ', maxsplit=1)[-1]  # Matches the previous word
            if any(month in previous_word for month in self.MONTHS):
                    result.start = self.text[:result.start].rfind(previous_word)
            output.append(result)
            
        return output