import uuid
from IPython.display import HTML, Javascript, display


def load_resources():
    display(Javascript("""require.config({
    paths: {
        'd3': '//cdnjs.cloudflare.com/ajax/libs/d3/3.5.16/d3.min',
        'crossfilter': '//cdnjs.cloudflare.com/ajax/libs/crossfilter/1.3.12/crossfilter.min',
        'dc': '//cdnjs.cloudflare.com/ajax/libs/dc/1.7.5/dc.min',
        'underscore': '//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore-min',
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


def crossfilter_dataframe(df):
    guid = uuid.uuid4()
    return Javascript("""require(['d3', 'crossfilter', 'dc', 'underscore'], function(d3, crossfilter, dc, _) {
    var pluck = function(prop) {
        return function(d) { return d[prop]; };
    }

    var crossfilterData = {json};

    var cf = crossfilter(crossfilterData);
    var all = cf.groupAll();

    element.append('<div id="dc-{uuid}-count"><strong class="filter-count">?</strong> selected ' +
                   'out of <strong class="total-count">?</strong> records</div>' +
                   '<div style="clear: both;"></div>');
    var count = dc.dataCount("#dc-{uuid}-count");
    count.dimension(cf).group(all);

    _.each(_.keys(crossfilterData[0]), function(prop) {
        var propId = prop.replace(".", "_");
        element.append('<div style="float: left;" id="dc-{uuid}-chart-' + propId + '"><strong>' + prop + '</strong>' +
                       '<div style="clear: both;"></div></div>');
        var dim = cf.dimension(pluck(prop));
        var group = dim.group().reduceCount();
        var min = dim.bottom(1)[0][prop];
        var max = dim.top(1)[0][prop];
        var chart = dc.barChart("#dc-{uuid}-chart-" + propId);
        chart.dimension(dim).group(group)
            .x(d3.scale.linear().domain([min, max]))
            .width(450).height(250);
    });

    dc.renderAll();
    dc.redrawAll();
});""".replace('{json}', df.to_json(orient='records')).replace('{uuid}', str(guid)))


# TODO:
#
# - support multiple types of graphs
# - add data table
# - make graphs configurable
# - handle text columns
# - "reset filters" link
