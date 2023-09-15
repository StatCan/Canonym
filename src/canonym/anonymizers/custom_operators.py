################################################################
#                  Custom Operators                            #
#                                                              #
#        Allows different types of entity masking              #
#                                                              #
#                                                              #
################################################################

import random
import string
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
################################################################


class BasicOperator:
    ''' Defines different types of entity masking using Presidio operators
        
            :param supported_entities: list of entity types identified by NER tagger
            :param config_dict: pair of strategy and entity types to be anonymized in dictionary format
    '''

    def __init__(self, supported_entities: list[str]=None, config_dict: dict={}):

        self.config_dict = config_dict
        self.supported_entities = supported_entities
        self.ACTIONS_DICT = {
            'replace': self.replaceOperator,
            'redact': self.redactOperator,
            'hash': self.hashOperator,
            'mask': self.maskOperator,
            'scramble': self.scrambleOperator,
            'randomize': self.randomizeOperator,
            'faker': self.fakerOperator,
            'replace_val': self.replacevalueOperator
        }
        self.operator_dict = {}
        self.fake = Faker(locale=['en_CA'])

    def _create_operator(self):
        ''' 
            Creates operators for each entity type based on config_dict

        '''
        
        if self.config_dict:
            for key, value in self.config_dict.items():
                func = self.ACTIONS_DICT.get(value)
                # If function name is not recognized, fall back on default option
                if func is None:
                    func = self.ACTIONS_DICT.get('replace')
                    print(f'Technique selected not recognized. Anonymizing with default technique _replace_')

                self.operator_dict.update({key: func(key)})
        else:
            for item in self.supported_entities:
                self.operator_dict.update({item: self.replaceOperator()})

        return self.operator_dict

    def get_operator(self):
        ''' 
            Method used to invoke _create_operator() call 

        '''
        
        self.operator_dict = self._create_operator()
        return self.operator_dict

    def replaceOperator(self, entity_name: str=None):
        ''' 
            Presidio Operator to replace the PII text with entity name tag 
            Example: "John Doe" replaced with <PERSON> 
            
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        return OperatorConfig(operator_name='replace')

    def redactOperator(self, entity_name: str=None):
        ''' 
            Presidio Operator to remove PII text completely from input 
        
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        return OperatorConfig(operator_name='redact')

    def hashOperator(self, entity_name: str=None):
        ''' 
            Presidio Operator to hash PII text with default hash type sha256 
        
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        return OperatorConfig(operator_name='hash', params={'hash_type': 'md5'})

    def maskOperator(self, entity_name: str=None):
        ''' 
            Presidio Operator to replace each character in PII text with a given character *
            chars_to_mask = 100 means maximum 100 characters will be masked in a single entity
            Assuming no PII text will have more than 100 characters
        
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        return OperatorConfig(operator_name='mask', params={'chars_to_mask': 100, 
                                                            'masking_char': '*',
                                                            'from_end': True})

    def scrambleOperator(self, entity_name: str=None):
        ''' 
            Presidio Custom Operator to return PII text with characters scrambled 
                
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        return OperatorConfig(operator_name='custom', params={"lambda": lambda x: ''.join(random.sample(x, len(x)))})

    def randomizeOperator(self, entity_name: str=None):
        ''' 
            Presidio Custom Operator to return digits-based PII text with random number of same length
        
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        return OperatorConfig(operator_name='custom', params={"lambda": lambda x: ''.join(random.choices(string.digits, k=len(x)))})

    def fakerOperator(self, entity_name: str=None):
        ''' 
            Presidio Custom Operator to return synthetic data specific to entity type using faker library
        
                :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        LAMBDA_DICT ={"PERSON": (lambda x: self.fake.name()),
                      "PHONE_NUMBER": (lambda x: self.fake.phone_number()),
                      "EMAIL_ADDRESS": (lambda x: self.fake.email()),
                      "FULL_ADDRESS": (lambda x: self.fake.address()),
                      "CA_SIN": (lambda x: self.fake.ssn()),
                      "COUNTRY": (lambda x: self.fake.country()),
                      "PROVINCE": (lambda x: self.fake.province()),
                      "CA_POST_CODE": (lambda x: self.fake.postalcode()),
                      "CA_PASSPORT": (lambda x: ''.join(random.choices(string.ascii_uppercase, k=2)) + ''.join(random.choices(string.digits, k=6))),
                     }
        lambda_func =  LAMBDA_DICT.get(entity_name, None)
        
        if lambda_func is None:
            return self.scrambleOperator()
        else:
            return OperatorConfig(operator_name="custom", params={"lambda": lambda_func})
        

    def replacevalueOperator(self, entity_name: str=None):
        ''' 
            Presidio Operator to replace the PII text with new string; 
            Individual entity text replaced with fixed string.
            
                    :param entity_name: entity type in string format. Example: 'PERSON'
        '''
        
        REPLACE_VAL_DICT = {"PERSON": "John Doe",
                          "PHONE_NUMBER": "123-456-7890",
                          "EMAIL_ADDRESS": "johndoe@mail.com",
                          "FULL_ADDRESS": "150 Tunney's Pasture Driveway, Ottawa, ON K1A 0T6",
                          "CA_SIN": "123 123 123",
                          "COUNTRY": "Canada",
                          "PROVINCE": "Ontario",
                          "CA_POST_CODE": "K1A 0T6",
                          "CA_PASSPORT": "11-0000-0000",
                         }
        replace_with =  REPLACE_VAL_DICT.get(entity_name, None)
        
        if replace_with is None:
            
            return self.replaceOperator()
        else:
            return OperatorConfig(operator_name="replace", params={"new_value": replace_with}) 
        