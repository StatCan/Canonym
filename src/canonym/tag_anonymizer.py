################################################################
#                         TagAnonymizer                        #
#                                                              #
#     Anonymizing tagged entities                              #
#                                                              #
#                                                              #
#                                                              #
################################################################
import sys
import confuse
from typing import Any
from pathlib import Path
from canonym.text_item import TextItem
from importlib_resources import files
from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig

from canonym.anonymizers import *
################################################################


class TagAnonymizer:
    ''' 
    Object based on Presidio Anonymizer, used to anonymize identified entities with the strategy specified in the config file

            :param config_file: yaml config file to load instead of the default configuration stored in DEFAULT_AN_TAGGER_CONFIG_FILE 
            :param supported_entities: list of entities tagged by NER tagger, used by default when entities for anonymization strategy is not provided in config file 
    '''
    
    DEFAULT_AN_TAGGER_CONFIG_FILE = 'anonymizer_config_default.yaml'

    def __init__(self, config_file: str=None, supported_entities: list[str]=None):
        self.config = confuse.Configuration('Canonym', __name__)
        self.load_config(file=config_file)
        self.anonymizer = AnonymizerEngine() # initializing the Presidio anonymizer
        self.supported_entities = supported_entities

    def load_config(self, file: str=None ) -> None:
        ''' 
        Loading the config file

                :param file: .yaml config file to load
        '''
        #file = file if file else self.DEFAULT_AN_TAGGER_CONFIG_FILE # using defaults if no config file is provided
        if file is None:
            file = files('canonym.config').joinpath(self.DEFAULT_AN_TAGGER_CONFIG_FILE) # using defaults if no config file is provided
        try:
            self.config.set_file(file)
            self._apply_config()
        except Exception as e:
            raise Exception(f'Failed to get anonymizer entities from {file}') from e

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
        Printing the configuration with all active settings
        '''
        for item, value in self.config.items():
            print(f'{item} :\n    {value}\n')

    def export_config(self, file: str='config_export') -> None:
        '''
        Exporting the config to a yaml file

                :param file: export file name 
        '''
        file = Path(file).with_suffix('.yaml')
        with open(file, 'w') as f:
            f.write(self.config.dump())
        print(f'Sucesfully exported the Tag Anonymizer config file at {str(file.absolute())}')

    def _apply_config(self):
        '''
        Transfers the values of the config to operator attributes
        '''
        for key, item in self.config.items():
            self.__dict__[key] = item.get()

    def _custom_operators(self, strategy: str) -> dict:
        pii_operators = {}
        if self.ALL_ANONYMIZER_STRATEGIES:
            for item in self.ALL_ANONYMIZER_STRATEGIES:
                for strategy_name_in_config_file, strat in item.items():
                    if strategy_name_in_config_file == strategy:
                        for op_name, entity_group in strat.items():
                            if isinstance(entity_group, str):
                                # If entity group name is used like "NUMERIC_ENTITIES"
                                entity_list = eval('self.{0}'.format(entity_group))
                            elif isinstance(entity_group, list):
                                # If list of entity names are used
                                entity_list = entity_group
                            pii_operators.update(dict.fromkeys(entity_list, op_name))

        operator_dict = BasicOperator(supported_entities=self.supported_entities, config_dict=pii_operators).get_operator()
        return operator_dict

    def anonymize(self, text_item: TextItem, strategy: str='replace_all_with_tag') -> TextItem:
        '''
        Replaces/redacts/masks PII text based on strategy and entities listed in config file and results of NER tagger.
        
                Default functionality: replace all entities with entity name tag in format <ENTITY>
        
                :param text_item: TextItem object with ner tagger results
                :param strategy: string name of strategy as it appears in config file under ALL_ANONYMIZER_STRATEGIES
        '''
        
        # Create new RecognizerResult list to match provided entity types
        analyzer_result_modified = []
        pii_operators = self._custom_operators(strategy)
        if pii_operators:
            entity_list = list(pii_operators.keys())
        else:
            entity_list = self.supported_entities
        # Copy select entities and their results to a new list to be provided to Anonymizer
        for ner_result in text_item._ner_results:
            if ner_result.entity_type in entity_list:
                analyzer_result_modified.append(ner_result)
        
        text_item.anonymized_text = self.anonymizer.anonymize(text=text_item.text,
                                                              analyzer_results=analyzer_result_modified,
                                                              operators=pii_operators).text

        return text_item