################################################################
#                        Text Item                             #
#                                                              #
#     Basic text object Analyzer adding cutom recognizers      #
#     enhancers and NER models                                 #
#                                                              #
#                                                              #
################################################################
from presidio_analyzer import RecognizerResult
from dataclasses import dataclass, field


@dataclass
class TextItem:
    ''' 
    Basic text object, is first passed to the NERTagger then to the TagAnonymizer 
    
            :param text: original text input 
            :param anonymized_text: anonymized text provided by the TagAnonymizer
            :param index: optional index, used to keep track of the text_items if anonymizing a Series or DataFrame
            :param language: language of the text, defaults to english
            :param ner_results: list of NER entities provided by the NERTagger
    '''

    text: str
    anonymized_text: str = None     # Final output after anonymization 
    index: int = None     # To keep track of the DataFrame index if it exists
    language: str = 'en'     # For the recognizers to work properly a language should be provided, defaults to English
    _ner_results: list[RecognizerResult] = field(default_factory=list)     # Creates an empty list if nothing is provided      
    
    @property    
    def ner_results(self):
        return self._ner_results      
    
    @ner_results.setter
    def ner_results(self, new_results: list[RecognizerResult]):
        self._ner_results = new_results
        self._ner_results.sort(key = lambda x: (x.entity_type, x.start))
        self.ner_entities_types = sorted({result.entity_type for result in self._ner_results})

    def print_ner_results(self) -> None:
        ''' Printing the results, sorted by entity type'''     
        for entity in self.ner_entities_types:
            print(f'{entity} :')
            for filtered_result in [result for result in self.ner_results if result.entity_type == entity]:
                print(f'    - {self.text[filtered_result.start:filtered_result.end]}  | score : {filtered_result.score}')
            print('\r')
            
    def __len__(self):
        return len(self.text)
    
    def number_tags(self):
        return len(self.ner_results)
    
    def __str__(self):
        return self.anonymized_text or self.text
    
    



