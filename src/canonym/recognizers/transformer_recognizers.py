##############################################################
#                   Transformer Recognizers                  #
#                                                            #
#                                                            #
##############################################################
from importlib_resources import files
from typing import Optional
from presidio_analyzer import EntityRecognizer, RecognizerResult,  AnalysisExplanation
from presidio_analyzer.nlp_engine import NlpArtifacts
from canonym.enhancers import ResultEnhancer, WordExtenderEnhancer, ContiguousEntitiesEnhancer
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import pathlib

#############################################################


class TransformerRecogniser(EntityRecognizer):
    ''' This is a subclass of Presidio EntityRecognizer class, that works with any model form the Huggingface library'''

    # Mapping entities from conll-2003 Ner dataset to one of the 3 entity types
    MODEL_ENTITIES = {
     'B-LOC': 'LOCATION',
     'I-LOC': 'LOCATION',
     'LOC': 'LOCATION',
     'B-PER': 'PERSON',
     'I-PER': 'PERSON',
     'PER': 'PERSON',
     'B-ORG': 'ORGANISATION',
     'I-ORG': 'ORGANISATION',
     'ORG': 'ORGANISATION'
    }

    DEFAULT_ENTITIES = {
        'LOCATION',
        'PERSON',
        'ORGANISATION'
    }

    DEFAULT_ENHANCERS = {
        WordExtenderEnhancer,
        ContiguousEntitiesEnhancer
    }

    DEFAULT_EXPLANATION = "Identified as {} by {} Transformer Named Entity Recognition"

    def __init__(self,
                 model : str,
                 supported_entities: list[str] = None,
                 supported_enhancers: list[ResultEnhancer] = None,
                 **kwargs): 
        
        self.model_path = model # pathlib.Path(model)  # Tries first to load the model locally, if not will pass as a string to load directly from the hub
        self.model_name = str(self.model_path).split('/')[-1].split('\\')[-1]
        self.name = 'TransformerRecogniser_'+self.model_name
        self.supported_entities = self.DEFAULT_ENTITIES if supported_entities is None else supported_entities
        self.supported_enhancers = self.DEFAULT_ENHANCERS if supported_enhancers is None else supported_enhancers
        super().__init__(name=self.name, supported_entities=self.supported_entities, **kwargs)

    def load(self):
        ''' Loads the Transformers model and creates a NER pipeline'''
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, truncation=True, padding=False)
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_path)
        self.pipeline = pipeline(task='ner', model=self.model, tokenizer=self.tokenizer, aggregation_strategy='simple')
        self.max_model_input = list(self.tokenizer.max_model_input_sizes.values())[0]

    def analyze(self,
                text: str,
                entities: list[str] = DEFAULT_ENTITIES,
                nlp_artifacts: NlpArtifacts = None
               ) -> list[RecognizerResult]:

        results = []

        # Should get the other Presidio NER
        ner_entities = nlp_artifacts.entities if nlp_artifacts else None
 
        pipe_input, chunk_lengths = self._preprocess_text(text)  # Deals with text that is longer than what the transformers model can handle

        pipe_results = self.pipeline(pipe_input)  # Transformers Pipeline
 
        if chunk_lengths:   # Fltattens the list and reindexes the tags if the text was too long and needed to be processed in chunks 
            out=[]
            add_length=0
            for i,pipe_result in enumerate(pipe_results):
                if i>0:
                    add_length += chunk_lengths[i-1]
                for ner_tag in pipe_result:
                    ner_tag['start']+=add_length   # Reindexing the start and end
                    ner_tag['end']+=add_length
                out.extend(pipe_result)
            pipe_results = out

        for pipe_result in pipe_results:
            entity_name = self.MODEL_ENTITIES.get(pipe_result['entity_group'])  # Converts the entity name to Presidio entity
            if entity_name not in entities:
                continue
            score = round(pipe_result['score'], 2)
            result = RecognizerResult(
                    entity_type=entity_name,
                    start=pipe_result['start'],
                    end=pipe_result['end'],
                    score=score,
                    analysis_explanation=self.transformers_explanation(entity_name, score),
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name
                    },
                )
            results.append(result)
        return results
 
    def _preprocess_text(self, text: str, max_length: int=None):
        ''' The goal is to divide long text inputs into chunks that the model can handle'''
        if not max_length:
            max_length = self.max_model_input -2   # Adding a margin of 2 tokens for start and end of sequence  
 
        if len(text)<=max_length:  # If the text is already smaller than the max number of tokens, bypass and return the text 
            return text, None
 
        tokenized_dict = self.tokenizer(text, max_length=None, add_special_tokens=False, return_offsets_mapping=True)
        tokenized = tokenized_dict['input_ids']
        offset_mapping = tokenized_dict['offset_mapping']
        positioned_tokens = list(zip(tokenized, offset_mapping))
        num_tokens = len(tokenized)
 
        if num_tokens<=max_length:  # If the tokenized text is smaller than the max number of tokens, bypass and return the text 
            return text, None
        else:
            output = []
            start_of_chunk = 0
 
            while positioned_tokens:
                work_chunk, positioned_tokens = positioned_tokens[:max_length], positioned_tokens[max_length:]  # Take a first chunk of the text of max_length
                resized_chunk, overflow = self._look_for_eos(work_chunk) if positioned_tokens else (work_chunk, [])   # Resized chunk, to the closest punctuation mark 
                end_of_chunk = resized_chunk[-1][1][1] if positioned_tokens else None  # Finding the real end position in the offset mapping
                output.append(text[start_of_chunk:end_of_chunk])  # Adding the first chunk to be read by the pipeline 
 
                start_of_chunk = end_of_chunk
                positioned_tokens = overflow + positioned_tokens 
            return output, [len(chunk) for chunk in output]
 
    def _look_for_eos(self, tokens: list[int], max_search: int=25):
        ''' Looks to split a text so that the first half end either with a punctuation sign 
            or if exceeding the search limit wil not cut a word'''
        last_token = ''
        for i,token in enumerate(reversed(tokens)):
            decoded_token = self.tokenizer.decode(token[0])
            # Conditions needed to split the text chunk
            split_conditions = ( 
                                (decoded_token in '.!?')  # A punctuation signifying an end of sentence
                                or ((i>=max_search) and ('##' not in last_token)) # Exceeded the max search and not a split word
                                )
            if split_conditions:
                return tokens[:-i], tokens[-i:] if i>0 else tokens, [] # split tokens or return tokens and an empty list if i==0 , resolving issue #1 IndexError: list index out of range

            last_token = decoded_token

        return tokens, []

    def transformers_explanation(self, entity_name, score):

        text_explanation = self.DEFAULT_EXPLANATION.format(entity_name, self.model_name) 
        explanation = AnalysisExplanation(
                recognizer=self.__class__.__name__,
                original_score=score,
                textual_explanation=text_explanation,
            )
        return explanation

    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Enhance confidence score using context of the entity.
        Is performed after all othe recognizers performed the analyze method"""
        
        # Loading the enhancers and performing the enhancments 
        for enhancer_class in self.DEFAULT_ENHANCERS:
            enhancer = enhancer_class(text, raw_recognizer_results, other_raw_recognizer_results, nlp_artifacts, context)
            raw_recognizer_results = enhancer.enhance()

        return raw_recognizer_results


class MobileBertNer(TransformerRecogniser):
    ''' Lightweight English NER Model from :
    https://huggingface.co/mrm8488/mobilebert-finetuned-ner/tree/main'''

    MODEL_PATH = 'mrm8488/mobilebert-finetuned-ner' 
    LANG = 'en'

    def __init__(self, **kwargs):
        kwargs.pop('supported_language', None)  # Forcing only English
        super().__init__(model=self.MODEL_PATH, supported_language = self.LANG, **kwargs)


class DistilCamembertNer(TransformerRecogniser):
    ''' Lightweight French NER Model from :
   https://huggingface.co/cmarkea/distilcamembert-base-ner'''

    MODEL_PATH = 'cmarkea/distilcamembert-base-ner' 
    LANG = 'fr'

    def __init__(self, **kwargs):
        kwargs.pop('supported_language', None)  # Forcing only French
        super().__init__(model=self.MODEL_PATH, supported_language = self.LANG, **kwargs)
