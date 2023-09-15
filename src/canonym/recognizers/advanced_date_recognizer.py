##############################################################
#                 Advanced Date Recogniser                   #
#                                                            #
#             Adding extra patterns to deal with             #
#             full months spelling and suffixes              #
#                  in English and French                     #
##############################################################

from presidio_analyzer.predefined_recognizers import DateRecognizer
from presidio_analyzer import Pattern

###############################################################


class AdvancedDateRecognizer(DateRecognizer):
    '''Adding extra patterns to the default DateRecognizer class to  deal with  
       full months spelling, suffixes and French spelling'''
    
    PATTERNS = DateRecognizer.PATTERNS
    
    # Full and abbreviated spelling of the months
    _ENGLISH_MONTHS = (r'January|February|March|April|May|June|July|August|September|October|November|December|'
                       r'JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC')
    
    _FRENCH_MONTHS = (r'Janvier|Février|Mars|Avril|Mai|Juin|Juillet|Août|Septembre|Octobre|Novembre|Décembre|'
                      r'Fevrier|Aout|Decembre|'      # Spelling variation without accents
                      r'JAN|FEV|MAR|AVR|MAI|JUN|JUL|AOU|SEP|OCT|NOV|DEC|'
                      r'FÉV|AOÛ|DÉC')                # Abbreviated months with accents
    
    # Adding new patterns to the default Presidio Date Patterns
    PATTERNS += [
        Pattern(
            " Date with English Months and various separators ",
            (r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])"  # 1 to 31 : 1
             r"(th|nd|st|rd)?"                       # English suffixes : 0 or 1
             r"(-| |\.|/|,)*"                        # Separators : 0 or more
             fr"({_ENGLISH_MONTHS})"                 # Months : exactly 1
             r"(-| |\.|/|,)*"                        # Separators : 0 or more
             r"(\d{4}|\d{2})?)\b"),                  # Year : YY or YYYY  : 1 or None
            0.6,
        ),
        Pattern(
            " Date with English Months and various separators , Month first",
            (fr"({_ENGLISH_MONTHS})"                 # Months : exactly 1
             r"(-| |\.|/|,)*"                        # Separators : 0 or more
             r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])"  # 1 to 31 : 1
             r"(th|nd|st|rd)?"                       # English suffixes : 0 or 1
             r"(-| |\.|/|,)*"                        # Separators : 0 or more
             r"(\d{4}|\d{2})?)\b"),                  # Year : YY or YYYY  : 1 or None
            0.6,
        ),
        Pattern(
            " Date with French Months and various separators ",
            (r"\b(([1-9]|0[1-9]|[1-2][0-9]|3[0-1])"  # 1 to 31 : 1
             r"(er)?"                                # French suffix : 0 or 1
             r"(-| |\.|/|,)*"                        # Separators : 0 or more
             fr"({_FRENCH_MONTHS})"                  # Months : exactly 1
             r"(-| |\.|/|,)*"                        # Separators : 0 or more
             r"(\d{4}|\d{2})?)\b"),                  # Year : YY or YYYY  : 1 or None
            0.6,
        )
    ]
    
   
    