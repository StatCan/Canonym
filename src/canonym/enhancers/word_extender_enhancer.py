##############################################################
#                 WordExtender Enhancer                      #
#                                                            #
#        to be called inside the Transformers recognizers    #
#            extends entities to word boundaries             #
##############################################################

from .result_enhancer import ResultEnhancer
###############################################################

class WordExtenderEnhancer(ResultEnhancer):
    ''' The goal of this enhancer is to extend the tag over en entire word 
        usefull because Transformers work at token level so words could be only 
        partially tagged '''
    
       
    def enhance(self):
        results = []
        for result in self.raw_recognizer_results:
            entity_start, entity_end = self.find_word_boundaries(text=self.text, start=result.start, end=result.end)
            result.start, result.end = entity_start, entity_end 
            results.append(result)
        return results
    
    def find_word_boundaries(self, text:str, start:int, end:int) -> tuple[int, int]:
        word_start = self.find_word_boundary(text, start, 'left')
        word_end = self.find_word_boundary(text, end, 'right')
        return word_start, word_end
                    
            
    @staticmethod        
    def find_word_boundary(text:str,
                           start:int,
                           direction:str = 'right') -> int:
        word_boundaries = [' ', '.', '?', '!', '-', ',', '@', ':', ';']
        if direction == 'right':
            step = 1
            limit = len(text)
            padd = 0
        elif direction == 'left':
            step=-1
            limit = 0
            padd = 1 # padd needed for lef inclusive boundary
        else:
            raise ValueError('direction can either be left or right')
        i = start    
        while i != limit:     
            if text[i] in word_boundaries:
                break
            i += step
        return i + padd 
     