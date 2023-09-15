################################################################
#                       NER TAGGER                             #
#                                                              #
#     Builds on Presidio's Analyzer adding cutom recognizers   #
#     enhancers and NER models                                 #
#                                                              #
#                                                              #
################################################################

import sys
from typing import Any, Union
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import (UsBankRecognizer,
                                                      UsPassportRecognizer,
                                                      PhoneRecognizer,
                                                      EmailRecognizer,
                                                      IbanRecognizer,
                                                      IpRecognizer,
                                                      SpacyRecognizer
                                                     )
from canonym.recognizers import *
from canonym.enhancers import *
from canonym.text_item import TextItem
import confuse
from pathlib import Path
from importlib_resources import files
################################################################


class NerTagger:
    ''' 
    Object based on Presidio Analyzer, used to identified entities with the recognizers specified in the config file

            :param config_file: yaml config file to load instead of the default configuration stored in DEFAULT_NER_TAGGER_CONFIG_FILE 
    '''

    DEFAULT_NER_TAGGER_CONFIG_FILE = 'ner_config_default.yaml'

    def __init__(self, config_file: str=None):
        self.config = confuse.Configuration('Canonym', __name__)      
        self.load_config(file=config_file)
        print(f"NER Set-up is done! Available recognizers : {self.get_recognizers_names()}")

    def analyze(self, text_item: TextItem, score_threshold: float= 0, **kwargs) -> TextItem:
        '''
        Analyzing the text with the configured recognizers

                :param text_item: TextItem object, containing the input text 
                :param score_threshold: specific score threshold, ignoring any results with lower confidence 
                :return: TextItem with added ner_results
        '''
        score_threshold = score_threshold if score_threshold else self.SCORE_THRESHOLD  # Using the default threshold if nothing is provided
        text_item.ner_results = self.ner_analyzer.analyze(text=text_item.text,
                                                          language=text_item.language,
                                                          score_threshold=score_threshold,
                                                          **kwargs)
        return text_item

    def load_config(self, file: str = None ) -> None:
        ''' 
        Loading the config file, and updating the ner_analyzer with the new parameters

                :param file: .yaml config file to load
        '''
        if file is None:
            file = files('canonym.config').joinpath(self.DEFAULT_NER_TAGGER_CONFIG_FILE) # using defaults is no config file is provided
        #file = file if file else self.DEFAULT_NER_TAGGER_CONFIG_FILE 
        try:
            self.config.set_file(file)
            self._apply_config()
        except Exception as e:
            raise Exception(f'Failed to create NER Tagger from {file}') from e

    def set_config_value(self, config_key: str, config_value: Any) -> None:
        '''
        Setting a specific config key, and applying the new configuration

                :param config_key: name of the config key to set
                :param config_value: value to set
        '''
        self.config.set({config_key.strip(): config_value})
        self._apply_config()

    def print_config(self) -> None:
        '''
        Printing the NERTagger configuration with all active settings
        '''
        for item, value in self.config.items():
            print(f'{item} :\n    {value}\n')

    def export_config(self, file:str = 'config_export') -> None:
        '''
        Exporting the config to a yaml file

                :param file: export file name 
        '''
        file = Path(file).with_suffix('.yaml')
        with open(file, 'w') as f:
            f.write(self.config.dump())
        print(f'Successfully exported the NER config file at {str(file.absolute())}')

    def get_recognizers_names(self) -> list[str]:
        ''' 
        Sorted recognizers names

                :return: list of loaded recognizers
        '''
        return sorted([rec.name for rec in self.ner_analyzer.get_recognizers()])

    def add_recognizer(self, recognizer, *args, **kwargs) -> None:
        ''' 
        Allows the manual addition of a recognizer to the ner_analyzer registry

                :param recognizer: Presidio Recognizer to add to the registry
        '''
        recognizer_to_add = recognizer(*args, **kwargs)
        self.ner_analyzer.registry.add_recognizer(recognizer_to_add)

    def add_regex_recognizer(self,
                 name: str, 
                 regex: Union[list[str], str], 
                 context: list[str] = None, 
                 score: float = 0.4,
                 supported_language: str = 'en',
                 supported_entity: str = None) -> None:
        '''
        Wrapper to easily add a custom regex recognizer on the fly

                :param name: name of the new regex recognizer
                :param regex: regex pattern
                :param context: list of strings used by Presidio to enhance the score if close by the result
                :param score: default score if match
                :param supported_language: language of the recognizer, only one language can be used
                :param supported_entity: recognized entity_name, if not provided the name of the recognizer in upper caps will be used
        '''
        self.add_recognizer(recognizer=CustomRegexRecognizer,
                            name=name,
                            regex=regex,
                            context=context,
                            score=score,
                            supported_language=supported_language,
                            supported_entity=supported_entity
                           )

    @staticmethod
    def __str_to_class(classname) -> object:
        '''
        Returning the class object from a string, this is necessary because 
        the classes are returned as strings when reading from the yaml config 

                :param classname: name of the class to fetch
                :return: class object
        '''
        return getattr(sys.modules[__name__], classname)

    def _apply_config(self):
        ''' 
        Transfers the values of the config to class attributes and re-creates the recognizers and ner_analyzer
        '''
        for key, item in self.config.items():
            self.__dict__[key] = item.get()
        self.recognizers = list(map(self.__str_to_class, self.DEFAULT_RECOGNIZERS)) + self.__postprocessing_recognizer_classes()
        self.ner_analyzer = self.__create_NER_analyzer()

    def __create_NER_analyzer(self) -> AnalyzerEngine:
        ''' 
        Creates NLP analyzer based on the loaded config file

        Note: Because Presidio only allows one supported language per recognizer, 
              specific recognizers for each of the supported language in AVAILABLE_LANGS are necessary
              Unless a recognizer manually specifies the only languages it can work on , with the LANG variable

                  :return: Presidio Analyzer Engine
        '''
        nlp_engine = NlpEngineProvider(nlp_configuration=self.PRESIDIO_NLP_ENGINE_CONFIG).create_engine()
        final_recognizers = []

        # Specific settings for Spacy and Transformers
        for recognizer in self.recognizers:
            if recognizer.__name__ == 'SpacyRecognizer':
                # Limiting the entities of the Spacy recognizer 
                key_arguments = {'supported_entities': self.SPACY_ENTITIES}
            elif recognizer.__bases__[0].__name__ == 'TransformerRecogniser':
                # Limiting the entities of all the Transformer recognizers and loading the enhancers
                key_arguments = {'supported_entities': self.TRANSFORMER_MODELS_ENTITIES,
                                 'supported_enhancers': list(map(self.__str_to_class, self.TRANSFORMER_MODELS_ENHANCERS))}
            else:
                key_arguments = {}

            # Checking if the recognizer only support a specifc language LANG 
            # and if yes limiting to the intersection with the AVAILABLE_LANGS
            rec_lang = recognizer.__dict__.get('LANG')
            rec_lang = [rec_lang] if isinstance(rec_lang, str) else rec_lang
            languages = self.AVAILABLE_LANGS if rec_lang is None else set(rec_lang).intersection(self.AVAILABLE_LANGS)

            # Creating the language specific recognizers
            for lang in languages:
                rec = recognizer(supported_language=lang, **key_arguments)
                rec.name += '_'+lang.capitalize()
                final_recognizers.append(rec)

        registry = RecognizerRegistry(recognizers=final_recognizers)
        supported_languages = [lang for lang in nlp_engine.nlp]
        self.supported_entities = {ent for rec in final_recognizers  for ent in rec.supported_entities}
        return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=supported_languages, registry=registry)


    def __postprocessing_recognizer_classes(self) -> list[EntityTypePostProcessingRecognizer]:
        ''' 
        Dynamically creates the PostProcessing classes based on the self.POST_PROCESSING_ENTITIES dictionary
        creates a recognizer based on EntityTypePostProcessingRecognizer class for each supported_entity:enhancers pairs
        
                :return: list of Classes, subsetting EntityTypePostProcessingRecognizer
        '''

        postprocessing_recognizer_classes = []
        if self.POST_PROCESSING_ENTITIES:
            for pp_entity, pp_enhancers in self.POST_PROCESSING_ENTITIES.items():
                enhancer_classes = list(map(self.__str_to_class, pp_enhancers))
                class_name = ''.join([w.title() for w in pp_entity.split('_')]) + 'PostProcessing'
                new_class = type(class_name,
                                 (EntityTypePostProcessingRecognizer,),
                                 {'enhancers': enhancer_classes,
                                  'supported_entities': [pp_entity]}
                                )
                postprocessing_recognizer_classes.append(new_class)
        return postprocessing_recognizer_classes