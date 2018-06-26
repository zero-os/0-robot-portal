from JumpScale9Portal.portal import exceptions
def main(j, args, params, tags, tasklet):
    robot_name = args.requestContext.params.get('rname')
    service_guid = args.requestContext.params.get('guid')
    try:
        logs = j.apps.zrobot.client.getServiceLogs(robot_name, service_guid)
        args.doc.applyTemplate({'logs': logs})
    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params