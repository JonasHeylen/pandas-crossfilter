from IPython.display import Javascript


def load_js():
    return Javascript("""require.config({
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
});""")


def dataframe_as_js(df, name='crossfilterData'):
    return Javascript("window.{name} = {json};".format(name=name, json=df.to_json(orient='records')))


