################################################################
#                  CA Post Code  Recognizer                    #
#                                                              #
#     Canadian Post Code Recognizer, based on the Presidio     #
#     PatterRecognizer Class                                   #
#                                                              #
#                                                              #
################################################################

from presidio_analyzer import PatternRecognizer, Pattern
from typing import Union
################################################################

class CaPostCodeRecognizer(PatternRecognizer):
    ''' Recognizes Canadian post codes based on regex '''
    
    def __init__(self,
                 context: Union[list[str], str] = None,
                 score: float = 0.5,
                 supported_language: str = 'en',
                 **kwargs):
        
        supported_entity = "CA_POST_CODE"
        self.regex = r"(\b[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d\b)"   # Letter-Number-Letter Number-Letter-Number
        
        if context :
            context_list = context if isinstance(context, list) else [context]
        else :
        # If no context is provided, will provide a default list depending of the language 
            if supported_language == 'fr':
                context_list = ['code postal', 'codepostal', 'postcode', 'poste', 'cp']
            else: 
                # defaults to English
                context_list = ['post code', 'postal code', 'postcode', 'post']
            
        postcode_pattern = Pattern(name=supported_entity+"_pattern", regex=self.regex, score=score)
        super().__init__(supported_entity=supported_entity, 
                         patterns=[postcode_pattern], 
                         context=context_list,  
                         supported_language=supported_language)
        
