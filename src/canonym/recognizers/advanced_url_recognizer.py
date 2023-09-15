################################################################
#                 Advanced URL Recognizer                      #
#                                                              #
#       Modification of the Presidio URL recognizer            #
#       to fix false positives  recognition                    #
################################################################
from presidio_analyzer.predefined_recognizers import UrlRecognizer
from presidio_analyzer import Pattern
################################################################

class AdvancedUrlRecognizer(UrlRecognizer):
    ''' Fix of the default Presidio Recognizer '''
    
    # Adding word boundaries to the original regex to fix false positives recognition
    BASE_URL_REGEX = r"(\b"+UrlRecognizer.BASE_URL_REGEX[1:-1]+r"\b)" 
    
    PATTERNS = [
        Pattern("Standard Url", "(?i)(?:https?://)" + BASE_URL_REGEX, 0.6),
        Pattern("Non schema URL", "(?i)" + BASE_URL_REGEX, 0.5),
    ]
