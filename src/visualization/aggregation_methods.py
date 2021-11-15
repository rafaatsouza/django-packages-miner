class AggregationMethods:
    
    #TODO: Set unwanted by regex
    @staticmethod
    def get_concate_and_freq(values, unwanted=None):
        concate = ''
        freq = {}

        for grid in values:
            parts = grid.split(',')
            for part in parts:
                if unwanted and part in unwanted:
                    continue

                if part in freq:
                    freq[part] = freq[part] + 1
                else:
                    freq[part] = 1

                if concate == '':
                    concate = part
                else:
                    concate = '{},{}'.format(concate, part)

        return concate, freq