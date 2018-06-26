from JumpScale9Portal.portal import exceptions
def main(j, args, params, tags, tasklet):
    robot_name = args.requestContext.params.get('rname')
    service_guid = args.requestContext.params.get('sguid')
    task_guid = args.requestContext.params.get('tguid')
    try:
        task = j.apps.zrobot.client.getTask(robot_name, service_guid, task_guid)
        task['result'] = task['result'] or 'No result returned.'
        args.doc.applyTemplate({'task': task})
    except exceptions.BaseError as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params