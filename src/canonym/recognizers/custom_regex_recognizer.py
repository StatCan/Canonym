################################################################
#                  Custom Regex Recognizer                     #
#                                                              #
#     Allows the creation of a custom recognizer based on      #
#     the provided regex pattern                               #
#                                                              #
#                                                              #
################################################################

from presidio_analyzer import PatternRecognizer, Pattern
from typing import Union
################################################################

class CustomRegexRecognizer(PatternRecognizer):
    ''' Allows the creation of a custom regex recognizer'''

    def __init__(self,
                 name: str, 
                 regex: Union[list[str], str], 
                 context: list[str] = None, 
                 score: float = 0.4,
                 supported_language: str = 'en',
                 supported_entity: str = None
                ):
        
        supported_entity=name.upper() if supported_entity is None else supported_entity.upper()
        self.regex = regex if isinstance(regex,list) else [regex]
        self.score = score
        context_list= [cont.lower() for cont in context] if isinstance(context, list) else context
        self.patterns = [Pattern(name=name+"_pattern_"+str(i), regex=reg, score=self.score) for i,reg in enumerate(self.regex)]
        super().__init__(name=name, 
                         supported_entity=supported_entity,
                         patterns = self.patterns,
                         context=context_list,
                         supported_language=supported_language)
    
    def __str__(self):
        return fr"{self.name.title()} Regex recognizer : {self.regex} "
    
    def __repr__(self):
        return fr"CustomRegexRecognizer(name={self.name}, regex={self.regex}, context={self.context}, score={self.score}), supported_language={self.supported_language})"