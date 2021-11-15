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

        ax.pie(data, labels=labels, autopct=lambda p: VisualizationMethods._get_pie_label(p, full_len), shadow=True, startangle=45)
        ax.axis('equal')
        ax.set_title(title)    
        ax.grid()
        