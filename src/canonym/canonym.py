################################################################
#                          CANONYM                             #
#                                                              #
#                  Anonymizing textual data                    #
#                                                              #
#                                                              #
#                                                              #
################################################################

from canonym import NerTagger, TextItem
from .tag_anonymizer import TagAnonymizer
from lingua import LanguageDetectorBuilder, IsoCode639_1
import pandas as pd
from pandas import Series, DataFrame
from presidio_analyzer import RecognizerResult
from typing import Any, Union
from tqdm.auto import tqdm
import warnings
################################################################


class Canonym:
    '''
    Canonym aims to improve on the dafault models and techniques provided by Presidio,
    to achieve better NER tagging and anonymization results.
    Especially on Canadian data, which requires bilingual capabilities and special recognizers

         :param ner_config_file: config file to replace the default parameters of the NER tagger
         :param anonymizer_config_file: config file to replace the default parameters of the anonymizer
    '''

    def __init__(self, ner_config_file: str=None, anonymizer_config_file: str=None):
        self.ner_tagger = NerTagger(config_file=ner_config_file)
        self.supported_entities = self.ner_tagger.supported_entities
        self.tag_anonymizer = TagAnonymizer(config_file=anonymizer_config_file, supported_entities=self.supported_entities)
        self.ACTIONS_DICT = {
            'str': self.anonymize_text,
            'TextItem': self.anonymize_text,
            'list': self.anonymize_list,
            'DataFrame': self.anonymize_dataframe,
            'Series': self.anonymize_pd_series
        }
        self.language_detector=LanguageDetectorBuilder.from_iso_codes_639_1(*[IsoCode639_1[code.upper()] for code in self.ner_tagger.AVAILABLE_LANGS]).build()

    def ner_tagging(self, text_item: Union[TextItem, str],  index_value: Any = None, language: str='en', **kwargs) -> TextItem:
        '''
        First step of the pipeline, identifying the entities we want to anonymize
        transforming the input into a TextItem object if needed. 
        Expects a string or a TextItem object as input, will return a TextItem with the NER results

                :param text_item: text input where we want to identify NER entities
                :param index_value: optional index, used to keep track of the text_items if anonymizing a Series or DataFrame
                :param language: language of the text, default to english, if None or auto are provided a search will be conducted
                :return: TextItem object
        '''
        # Converting strings into TextItems
        text_item = TextItem(text_item, index=index_value, language=language) if isinstance(text_item, str) else text_item
        if not isinstance(text_item, TextItem):
            raise TypeError(f'The input provided was of type {type(text_item)}, the method only accepts str and TextItem objects')

        # Detecting the language of the string if auto or None 
        if text_item.language == 'auto' or text_item.language is None:
            text_item.language = self.__detect_lang(text_item.text)

        return self.ner_tagger.analyze(text_item, **kwargs)

    def anonymize(self, input_object: Any, **kwargs) -> Any:
        '''
        Convenience method, as defined in self.ACTIONS_DICT,  will call any of the following depending of the input type :
                    - anonymize_text(self, text_item: TextItem | str, index_value: Any = None, language: str ='en')
                    - anonymize_list(self, list_of_items: list[TextItem], index: list = None, language: str ='en')
                    - anonymize_pd_series(self, text_series:Series, language:str = 'en')
                    - anonymize_dataframe(self, data_frame:DataFrame, columns_to_anonymize:list[str] = None, language:str | dict = 'en') 

                    :param input_object: input which type will be matched with the keys of ACTIONS_DICT calling the appropriate anonymizing function
        '''
        self.input_type = str(type(input_object).__name__) # Gets input type
        func = self.ACTIONS_DICT.get(self.input_type) # Gets the associated anonymizing function

        if func is None:
            raise TypeError(f"Incorrect input type : {self.input_type} provided, should be one of the following: {list(self.ACTIONS_DICT.keys())}")
        return func(input_object, **kwargs)

    def anonymize_text(self, text_item: Union[TextItem, str], index_value: Any = None, language: str ='en', output_type: str = None, strategy: str='replace_all_with_tag') -> Union[TextItem, str]:
        '''
        Main pipeline: first tags the relevant entities on the text_item, then applies the specified anonymization technique
        By default returns the anonymized text, can return the full TextItem object if output_type==TextItem 

                :param text_item: Text input we want to anonymize
                :param index_value: Optional index, used to keep track of the text_items if anonymizing a Series or DataFrame
                :param language: Language of the text, defaults to english, if None or auto are provided a search will be conducted
                :param output_type: By default will provide the anonymized text in string format, specify TextItem to recieve the full TextItem object
                :return: Anonymized text or TextItem object
        '''
        text_item = self.ner_tagging(text_item=text_item, index_value=index_value, language=language)
        text_item = self.tag_anonymizer.anonymize(text_item=text_item, strategy=strategy)

        return text_item if output_type == 'TextItem' else text_item.anonymized_text

    def anonymize_list(self, list_of_items: list[TextItem], index: list=None, language: str='en', output_type: str=None, strategy: str='replace_all_with_tag') -> Union[list[TextItem], list[str]]:
        '''
        Applies the anonymize_text method to each element of the list 

                :param list_of_items: List of text items to anonymize
                :param index: list of indices used to keep track of the text_items if anonymizing a Series or DataFrame
                :param language: Language of the text, defaults to english, if None or auto are provided a search will be conducted
                :param output_type: By default will provide a list of anonymized text in string format, specify TextItem to recieve a list of TextItem objects
                :return: List of anonymized texts or lisr of TextItem objects
        '''
        if index and (len(index) == len(list_of_items)):
            return [self.anonymize_text(item, index_value=indx, language=language, output_type=output_type, strategy=strategy) for item,indx in tqdm(zip(list_of_items, index))]
        else:
            return [self.anonymize_text(item, language=language, output_type=output_type, strategy=strategy) for item in tqdm(list_of_items)]

    def anonymize_pd_series(self, text_series: Series, language: str='en', strategy: str='replace_all_with_tag', **kwargs) -> Series:
        '''
        Transforms a Pandas Series into a list of strings, then anonymises it. 
        Returns a series with the same name, index as the original but with an anonymized text

                :param text_series: Pandas Series containg text data to anonymize
                :param language: Language of the text, defaults to english, if None or auto are provided a search will be conducted
                :return: Pandas series with anonymized text
        '''
        allowed_types = ['string', 'object']

        if text_series.dtype.name not in allowed_types:
            warnings.warn(f"Warning: Series {text_series.index[0]} is of dtype {text_series.dtype.name} instead of {allowed_types}, no anonymization is possible")
            return text_series
        else:
            series_as_list = text_series.to_list()
            series_index = text_series.index.to_list()
            series_name = text_series.name if text_series.name else text_series.index[0]
            series_as_list = self.anonymize_list(list_of_items=series_as_list, index=series_index, language=language, output_type='TextItem', strategy=strategy)
            return Series(data=[item.anonymized_text for item in series_as_list], index=[item.index for item in series_as_list], name=series_name)

    def anonymize_dataframe(self, data_frame: DataFrame, columns_to_anonymize: list[str]=None, language: str='en', strategy: str='replace_all_with_tag', **kwargs) -> DataFrame:
        '''
        By default will anonymize each column containing text, but specific columns can be provided in columns_to_anonymize.
        The language of each column can be provided as a dict of the format {column_name:language, },
        a single language or the "auto" option can also be provided.
        Will then call anonymize_pd_series on each of the columns to be treated, and return an anonymized data_frame with the same index and columns

                :param data_frame: Pandas DataFrame containg text data to anonymize
                :param columns_to_anonymize: List of column names to anonymize, if not provided all text columns will be processed
                :param language: Language of the text, defaults to english, if None or auto are provided a search will be conducted. 
                                 Also accepts a dict of format {column_name:language or auto, }
                :return: New Pandas DataFrame with anonymized text columns
        '''
        data_frame = data_frame.copy()  # Works on a copy of the original df

        if columns_to_anonymize is None:
            # Returns only the data_frame columns that contain text
            columns_to_anonymize = [k for k, v in data_frame.dtypes.to_dict().items() if v.name in  ['string', 'object']]
        print(f"The following {len(columns_to_anonymize)} columns will be processed by the anonymizer: {columns_to_anonymize}")

        for column in tqdm(columns_to_anonymize):
            # If the language is a dict of column_names:language pairs will set it as the language, if not will pass the argument
            lang = language.get(column, 'en') if isinstance(language, dict) else language
            if lang is not None and lang != 'auto' :
                print(f'The column "{column}" wil be considered to contain data in {lang}') 
            else:
                print(f'The language of the text in column "{column}" will be automatically detected')
            data_frame[column] = self.anonymize_pd_series(data_frame[column], language=lang, strategy=strategy)

        return data_frame

    def __detect_lang(self, text: str) -> str:
        '''
        Detecting the language of a piece of text, returning in iso 639_1 format
        if the detector fails to identify and gives None, will return "en" for English by default

                :param text: text input to be fed to the language_detector for identification
                :return: iso_639_1 string id to identify a language
        '''
        detected_language = self.language_detector.detect_language_of(text)
        if detected_language:
            return detected_language.iso_code_639_1.name.lower()
        else:
            return 'en'