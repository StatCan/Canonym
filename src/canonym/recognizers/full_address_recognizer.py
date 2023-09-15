##############################################################
#                   Full Address Recognizer                  #
#                                                            #
#                                                            #
##############################################################
from typing import Optional
from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from canonym.enhancers import ResultEnhancer
#############################################################


class FullAddressRecognizer(EntityRecognizer):
    '''Recognizer using only other recognized entities to create a larger full-address entity
       It should be the last recognizer added to the list '''
    
    SUPPORTED_ENTITY = ['FULL_ADDRESS']
    FULL_ADDRESS_COMPONENTS = {'CA_POST_CODE', 'NUMBER', 'LOCATION', 'PROVINCE', 'STREET_TYPE', 'COUNTRY'}
    ALLOWED_SPACING = 5

    def __init__(self,
                 supported_enhancers: list[ResultEnhancer] = None,
                 **kwargs): 
        supported_language = kwargs.pop('supported_language', 'en')
        super().__init__(
            name='FullAddressRecogniser',
            supported_language=supported_language,
            supported_entities=self.SUPPORTED_ENTITY,
            **kwargs
        )
        self.score = 0.4

    def load(self) -> None:
        ''' No model to Load but abstract method has to be implemented'''
        pass

    def analyze(
        self, text: str, entities: list[str], nlp_artifacts: NlpArtifacts
    ) -> list[RecognizerResult]:
        ''' No direct analysis of the text but abstract method has to be implemented'''
        return []

    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: list[RecognizerResult],
        other_raw_recognizer_results: list[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[list[str]] = None,
    ) -> list[RecognizerResult]:
        """Using the context enhancement feature to add FULL_ADDRESS entities"""

        sorted_recognizer_results = sorted(other_raw_recognizer_results, key=lambda x: x.start)  # Sorting alll results by entity start
        filtered_recognizer_results = [result for result in sorted_recognizer_results if (result.score >= self.score) and (result.entity_type in self.FULL_ADDRESS_COMPONENTS)]
        # The code below is necessary because of nested entities
        # if an entity is nested will take into account the parent's end to compute the spacing
        for result in filtered_recognizer_results:
            result.parent_end = result.end
            filtered_recognizer_results_subset = filtered_recognizer_results.copy()
            filtered_recognizer_results_subset.remove(result)
            for result_2 in filtered_recognizer_results_subset:
                if result.contained_in(result_2) and result.parent_end < result_2.end:
                    result.parent_end = result_2.end
        results = []
        full_addresses = []
        full_address_candidate = []
        for result in filtered_recognizer_results:
            spacing = 0
            if full_address_candidate:
                # Looking at the distance from the last candidate to evaluate if they should be merged
                text_to_previous = text[full_address_candidate[-1].parent_end:result.start]
                text_to_previous = ''.join(text_to_previous.split()) # Eliminates any whitespace characters 
                spacing = len(text_to_previous)
                
            if spacing < self.ALLOWED_SPACING:  # If spacing is correct append to address_candidate
                full_address_candidate.append(result)
            elif spacing >= self.ALLOWED_SPACING:  # If spacing is too large, add current candidate, create new address_candidate
                full_addresses.append(full_address_candidate)
                full_address_candidate = []
                full_address_candidate.append(result)

        # Case where the address ends the text 
        if full_address_candidate:
            full_addresses.append(full_address_candidate)
            full_address_candidate = []

        # Post processing, we ignore some false positives
        for address in full_addresses:
            address_start = min([entity.start for entity in address])
            address_end = max([entity.end for entity in address])
            all_entity_types = {entity.entity_type for entity in address}
            # A full address must have a location
            if 'LOCATION' not in all_entity_types:
                continue
            # Needs at least two entities to be considered an address
            if len(address)<2:
                continue
            # A full address must be composed of 3 words or more
            if list(text[address_start:address_end].strip()).count(' ') < 3:
                continue
            results.append(RecognizerResult(entity_type = self.SUPPORTED_ENTITY[0],
                                           start = address_start,
                                           end = address_end,
                                           score = self.score))
        return results
