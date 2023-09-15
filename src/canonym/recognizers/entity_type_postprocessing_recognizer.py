##############################################################
#           Entity Type postprocessign recognizer            #
#                                                            #
#    Recognizer that calls enhancers on a specific Entity    #
#                                                            #
##############################################################
from typing import Optional, Union 
from canonym.enhancers import ResultEnhancer
from presidio_analyzer import RecognizerResult, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
###############################################################


class EntityTypePostProcessingRecognizer(EntityRecognizer):
    ''' This recognizer works differently from the regular recognizers, no analysis is conducted.
        instead it will call the enhancers provided on the supported entities '''
    
    def __init__(self,
                 enhancers: Union[list[ResultEnhancer], ResultEnhancer] = None, # Enhancer(s) to be called on the supported entities 
                 **kwargs):
        supported_entities = kwargs.pop('supported_entities', type(self).supported_entities)
        super().__init__(supported_entities=supported_entities, **kwargs)
        
        self.enhancers = enhancers if enhancers else self.enhancers
        self.enhancers = self.enhancers if isinstance(self.enhancers, list) else [self.enhancers]
        
        
    def load(self) -> None:
        ''' No model to Load but abstract method of EntityRecognizer  has to be implemented'''
        pass

    def analyze(
        self, text: str, entities: list[str], nlp_artifacts: NlpArtifacts
    ) -> list[RecognizerResult]:
        ''' No direct analysis of the text but abstract method of EntityRecognizer has to be implemented'''
        return []
    
    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Will call enhancers from the list on the provided supported entities """
        
        # Filtering only the results of the right entity type       
        results_to_enhance = [result for result in other_raw_recognizer_results if result.entity_type in self.supported_entities]
        for enhancer_class in self.enhancers: 
            enhancer = enhancer_class(text, results_to_enhance, other_raw_recognizer_results, nlp_artifacts, context)
            results_to_enhance = enhancer.enhance()
            
        return results_to_enhance
    
