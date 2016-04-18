import uuid
from IPython.display import HTML, Javascript, display


def load_resources():
    display(Javascript("""require.config({
    paths: {
        'd3': '//cdnjs.cloudflare.com/ajax/libs/d3/3.5.16/d3.min',
        'crossfilter': '//cdnjs.cloudflare.com/ajax/libs/crossfilter/1.3.12/crossfilter.min',
        'dc': '//cdnjs.cloudflare.com/ajax/libs/dc/1.7.5/dc.min',
    },
    shim: {
        'crossfilter': {
            deps: [],
            exports: 'crossfilter'
        }
    }
});"""), HTML('<link href="https://cdnjs.cloudflare.com/ajax/libs/dc/1.7.5/dc.min.css" rel="stylesheet" type="text/css">'))


def dataframe_as_js(df, name='crossfilterData'):
    return Javascript("window.{name} = {json};".format(name=name, json=df.to_json(orient='records')))


class Crossfilter:
    def __init__(self, df, graphs=None, width=450, height=250):
        self.df = df
        self.graphs = graphs
        if not self.graphs:
            self.graphs = [self.default_graph(col_name) for col_name in self.df.columns]
        self.width = width
        self.height = height

    def default_graph(self, col_name):
        #import pdb; pdb.set_trace()
        cat_columns = self.df.select_dtypes(include=['category']).columns
        if col_name in cat_columns:
            return RowChart(col_name)
        else:
            return BarChart(col_name)


    def _repr_javascript_(self):
        guid = uuid.uuid4()
        df = self.df.copy()
        # convert category columns back to string before calling to_json
        # https://github.com/pydata/pandas/pull/10321
        for i, s in df.loc[:, df.select_dtypes(include=['category']).columns].iteritems():
            df.loc[:, i] = s.astype('str')
        js = """
    require(['d3', 'crossfilter', 'dc'], function(d3, crossfilter, dc) {
        var pluck = function(prop) {
            return function(d) { return d[prop]; };
        }
        var crossfilterData = {json};
        var cf = crossfilter(crossfilterData);"""
        js += Summary()._repr_javascript_()
        for graph in self.graphs:
            js += graph._repr_javascript_()
        js += """
        dc.renderAll();
        dc.redrawAll();
    });"""
        return js.replace('{json}', df.to_json(orient='records')).replace('{uuid}', str(guid)) \
                          .replace('{width}', str(self.width)).replace('{height}', str(self.height))


class Chart:
    def __init__(self, crossfilter_name='cf'):
        self.crossfilter_name = crossfilter_name

    def _repr_javascript_(self):
        pass


class Summary(Chart):
    def _repr_javascript_(self):
        return """
        var all = {cf}.groupAll();
        element.append('<div id="dc-{uuid}-count"><strong class="filter-count">?</strong> selected ' +
                       'out of <strong class="total-count">?</strong> records</div>' +
                       '<div style="clear: both;"></div>');
        var count = dc.dataCount("#dc-{uuid}-count");
        count.dimension({cf}).group(all);""".replace('{cf}', self.crossfilter_name)


class ProperyChart(Chart):
    def __init__(self, property, crossfilter_name='cf'):
        super().__init__(crossfilter_name)
        self.property = property


class BarChart(ProperyChart):
    def _repr_javascript_(self):
        return """
        var prop = "{prop}";
        var propId = prop.replace(".", "_");
        var chartId = "dc-{uuid}-chart-" + propId;
        element.append('<div style="float: left;" id="' + chartId + '"><strong>' + prop + '</strong>' +
                       '<div style="clear: both;"></div></div>');
        var dim = {cf}.dimension(pluck(prop));
        var group = dim.group().reduceCount();
        var min = dim.bottom(1)[0][prop];
        var max = dim.top(1)[0][prop] + 1;
        var chart = dc.barChart("#" + chartId);
        chart.dimension(dim).group(group)
            .x(d3.scale.linear().domain([min, max]))
            .xUnits(dc.units.integers)
            .elasticY(true)
            .width({width}).height({height});
        """.replace('{cf}', self.crossfilter_name).replace("{prop}", self.property)


class RowChart(ProperyChart):
    def _repr_javascript_(self):
        return """
        var prop = "{prop}";
        var propId = prop.replace(".", "_");
        var chartId = "dc-{uuid}-chart-" + propId;
        element.append('<div style="float: left;" id="' + chartId + '"><strong>' + prop + '</strong>' +
                       '<div style="clear: both;"></div></div>');
        var dim = {cf}.dimension(pluck(prop));
        var group = dim.group().reduceCount();
        var min = dim.bottom(1)[0][prop];
        var max = dim.top(1)[0][prop] + 1;
        var chart = dc.rowChart("#" + chartId);
        chart.dimension(dim).group(group).width({width}).height({height});
        """.replace('{cf}', self.crossfilter_name).replace("{prop}", self.property)


# TODO:
#
# - support multiple types of graphs
# - add data table
# - make graphs configurable
# - handle text columns
# - "reset filters" link
