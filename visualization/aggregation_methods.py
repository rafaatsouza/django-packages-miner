def _is_unwanted(str, unwanteds=None, unwanteds_regex=None):
    import re

    if unwanteds and str in unwanteds:
        return True
    
    if unwanteds_regex:
        for unw_reg in unwanteds_regex:
            if re.match(unw_reg, str):
                return True

    return False

class AggregationMethods:
    
    @staticmethod
    def get_concate_and_freqs(df, value_column, used_column, unwanteds=None, unwanteds_regex=None):
        concate = ''
        freq = {}
        freq_by = {}

        for index, row in df[~df[value_column].isnull()].iterrows():
            used_by_count = row[used_column] or 0
            values = (row[value_column] or '').split(',')
            for part in values:
                if _is_unwanted(part, unwanteds, unwanteds_regex):
                    continue

                if part in freq_by:
                    freq_by[part] = freq_by[part] + used_by_count
                else:
                    freq_by[part] = used_by_count

                if part in freq:
                    freq[part] = freq[part] + 1
                else:
                    freq[part] = 1

                if concate == '':
                    concate = part
                else:
                    concate = '{},{}'.format(concate, part)

        return concate, freq, freq_by


    @staticmethod
    def get_concate_and_freq(values, unwanteds=None, unwanteds_regex=None):
        concate = ''
        freq = {}

        for grid in values:
            parts = grid.split(',')
            for part in parts:
                if _is_unwanted(part, unwanteds, unwanteds_regex):
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