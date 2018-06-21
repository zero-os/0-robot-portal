
def main(j, args, params, tags, tasklet):
    try:
        robots = j.apps.zrobot.client.list()
        args.doc.applyTemplate({'robots': robots})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params
