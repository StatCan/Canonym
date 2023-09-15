################################################################
#                Canadian Passport Recognizer                  #
#                                                              #
#            Canadian Passport Number Recognizer               #
#                                                              #
#                                                              #
#                                                              #
################################################################

from .custom_regex_recognizer import CustomRegexRecognizer

################################################################

class CaPassportRecognizer(CustomRegexRecognizer):
    ''' Canadian Passport Number Recognizer'''
    
    def __init__(self, supported_language: str = 'en'):
        regex = r"\b[a-zA-Z]{2}[ -]?\d{6}\b"  # 2 letters - 6 Numbers
        context_list = ['passeport', 'numéro de passeport'] if supported_language == 'fr' else ['passport', 'passport number', 'passportnumber']
        super().__init__(name="CA_Passport", regex=regex, context=context_list, supported_language=supported_language)
   