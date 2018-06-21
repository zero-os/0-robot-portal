def main(j, args, params, tags, tasklet):
    robot_name = args.requestContext.params.get('rname')
    guid = args.requestContext.params.get('guid')
    try:
        service = j.apps.zrobot.client.getService(robot_name, guid)
        args.doc.applyTemplate({'service': service})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params