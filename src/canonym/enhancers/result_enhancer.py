##############################################################
#                      Results Enhancer                      #
#                                                            #
#            to be called inside recognizers                 #
#            within the enhance using context method         #
##############################################################
from typing import Optional
from abc import ABC, abstractmethod
from presidio_analyzer import RecognizerResult 
from presidio_analyzer.nlp_engine import NlpArtifacts
###############################################################

class ResultEnhancer(ABC):
    ''' Abstract class of an enhancer that is to be called after the first NER results are obtained
    
        Info - Presidio has the following work flow :
            1 - individual NER recognizers
            2 - specific ResultEnhancers called for each recognizer using their enhance_using_context() method
            3 - general context aware enhancer (spacy LemmaContextAwareEnhancer by default)
            
        for more details see : Presidio/AnalyzerEngine._enhance_using_context() 
        
        '''
    
    def __init__(self,
                 text: str,
                 raw_recognizer_results: list[RecognizerResult],
                 other_raw_recognizer_results: list[RecognizerResult],
                 nlp_artifacts: NlpArtifacts = None,
                 context: Optional[list[str]] = None,
                ):
        
        self.text = text
        self.raw_recognizer_results = raw_recognizer_results
        self.other_raw_recognizer_results = other_raw_recognizer_results
        self.context = context
        
        
    @abstractmethod
    def enhance(self) -> list[RecognizerResult]:
        pass
