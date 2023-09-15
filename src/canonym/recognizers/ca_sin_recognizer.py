################################################################
#                  Canadian SIN Recognizer                     #
#                                                              #
#     Canadian SIN Recognizer ( Social Insurance Number)       #
#                                                              #
#                                                              #
#                                                              #
################################################################

from .custom_regex_recognizer import CustomRegexRecognizer

################################################################

class CaSinRecognizer(CustomRegexRecognizer):
    ''' Canadian Social Insurance Number Recognizer'''
        
    def __init__(self, supported_language: str = 'en'):
        
        regex = r"\b\d{3}[ -]?\d{3}[ -]?\d{3}\b" 
        context_list = ['numéro d’assurance sociale', 'NAS'] if supported_language == 'fr' else ['sin', 'social insurance number']
        super().__init__(name="Ca_SIN", regex=regex, context=context_list, supported_language=supported_language)