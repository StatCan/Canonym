##############################################################
#               Contiguous Entities Enhancer                 #
#                                                            #
#        to be called inside the Transformers recognizers    #
#        merges entities that are of the same type           #
##############################################################

from .result_enhancer import ResultEnhancer
###############################################################

class ContiguousEntitiesEnhancer(ResultEnhancer):
    ''' The goal of this enhancer is to merge together results of the same entity type
        that are separated by punctuation or white spaces '''
    
    DEFAULT_SEPARATORS = [' ', '.', '-', ',', ':']
    
    def enhance(self, separators=None):
        self.separators = self.DEFAULT_SEPARATORS if separators is None else separators
        results=[]
        sorted_results = sorted(self.raw_recognizer_results, key= lambda x: x.end)
        
        for i,sr1 in enumerate(sorted_results):
            if results and results[-1].end >= sr1.end:
                continue
            result = sr1
            for sr2 in sorted_results[i+1:]:
                result, flag = self.merge_result(self.text, result, sr2) 
                if flag:
                    break
            results.append(result)
        return results       
      
    def merge_result(self, text, result, next_result):
        if result.entity_type != next_result.entity_type:
            return result, True
        text_between = text[result.end:next_result.start]
        if len(set(text_between).difference(self.separators)) != 0:
            return result, True
        result.end = next_result.end
        return result, False
