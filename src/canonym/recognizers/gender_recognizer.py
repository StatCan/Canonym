################################################################
#                       Gender Recognizer                      #
#                                                              #
#       Identifies Gendered Pronouns in French and English     #
#                                                              #
################################################################

from presidio_analyzer import PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import Optional

################################################################


   
class GenderRecognizer(PatternRecognizer):
    ''' Recognizer for gendered pronouns'''
    
    SUPPORTED_ENTITY = 'GENDER'
    # English
    EN_PRONOUNS = {'she', 'her', 'hers', 'he', 'his', 'him', 'himself', 'herself', 'they', 'them', 'their', 'themselves'}
    EN_PRONOUNS.update({pr.title() for pr in EN_PRONOUNS})  # Deny list is case sensitive, adding title and upper case variants
    EN_PRONOUNS.update({pr.upper() for pr in EN_PRONOUNS})
    
    # French
    FR_PRONOUNS = {'il', 'lui', 'elle', 'eux', 'elles', 'ils', 'iel', 'iels'}
    FR_PRONOUNS.update({pr.title() for pr in FR_PRONOUNS})
    FR_PRONOUNS.update({pr.upper() for pr in FR_PRONOUNS})

    def __init__(self, supported_language: str = 'en', **kwargs):

        if supported_language == 'en':
            deny_list = self.EN_PRONOUNS.copy()
        elif supported_language == 'fr':
            deny_list = self.FR_PRONOUNS.copy()
        else:
            raise ValueError(f"Language : '{supported_language}' not supported by GenderRecognizer") 

        super().__init__(
            supported_entity= self.SUPPORTED_ENTITY,
            supported_language= supported_language,
            deny_list= deny_list,
            deny_list_score= 0.4,
            name= 'GenderRecognizer',
        )