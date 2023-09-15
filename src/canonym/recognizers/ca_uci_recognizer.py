################################################################
#                  Canadian UCI Recognizer                     #
#                                                              #
#     Canadian UCI Recognizer ( Unique client identifier)      #
#                                                              #
#                                                              #
#                                                              #
################################################################

from .custom_regex_recognizer import CustomRegexRecognizer

################################################################

class CaUciRecognizer(CustomRegexRecognizer):
    ''' Canadian Unique Client Identifier Recognizer'''

    def __init__(self, supported_language: str = 'en'):
        
        regex = [r"\b\d{4}[ -]?\d{4}\b",  # 8 digits with an optional space or dash in the middle
                      r"\b11[ -]?\d{4}[ -]?\d{4}\b"]   # 11 followed by 8 digits with an optional space or dash in the middle
        
        if supported_language == 'fr': 
            context_list = ['UCI', 'IUC', 'identificateur unique de client', 'identificateur de client', "#", 'id'] 
        else :
            # Context defaults to English
            context_list = ['UCI', 'unique client identifier', 'id', "#"]
            
        super().__init__(name="Ca_Uci", regex=regex, context=context_list, supported_language=supported_language)