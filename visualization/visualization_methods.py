def _get_label_with_abs_and_perc(p, total):
    absolute = '{:.0f}'.format(p * total / 100)
    percentage = '{0:.0%}'.format(p/100.0)

    return '{} ({})'.format(absolute, percentage)


class VisualizationMethods:
    
    @staticmethod
    def _get_pie_label(p, total):
        absolute = '{:.0f}'.format(p * total / 100)
        percentage = '{0:.0%}'.format(p/100.0)

        return '{} ({})'.format(absolute, percentage)


    @staticmethod
    def set_boxplot_by_ax(ax, data, title, use_log_scale=False, invert_scale=False):
        ax.boxplot(data, flierprops=dict(markerfacecolor='g', marker='D'), vert=(not invert_scale))
        ax.set_title(title)
        
        if use_log_scale and invert_scale:
            ax.set_xscale('log')
        elif use_log_scale and not invert_scale:
            ax.set_yscale('log')
            
        ax.grid()


    @staticmethod
    def set_pie_by_ax(ax, data, labels, title):
        full_len = 0

        for val in data:
            full_len = full_len + val

        ax.pie(data, labels=labels, autopct=lambda p: _get_label_with_abs_and_perc(p, full_len), shadow=True, startangle=45)
        ax.axis('equal')
        ax.set_title(title)    
        ax.grid()
        

    @staticmethod
    def show_bar_chart_by_dict(dict, xlabel, ylabel, title, color=None):
        import matplotlib.pyplot as plt

        keys = list(dict.keys())
        values = list(dict.values())
        
        _ = plt.figure(figsize = (24, 8))
        
        if color:
            plt.bar(keys, values, color=color, width=0.4)
        else:
            plt.bar(keys, values, width=0.4)
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        plt.title(title)
        plt.grid()
        plt.tight_layout()
        plt.show()


    @staticmethod
    def show_bar_chart_by_dict_and_ax(ax, dict, xlabel, ylabel, title, color=None):
        keys = list(dict.keys())
        values = list(dict.values())
        
        if color:
            ax.bar(keys, values, color=color, width=0.4)
        else:
            ax.bar(keys, values, width=0.4)
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xticklabels(keys, rotation=45, ha='right')
        ax.set_title(title)
        ax.grid()
