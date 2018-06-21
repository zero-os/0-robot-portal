def main(j, args, params, tags, tasklet):
    robot_name = args.requestContext.params.get('rname')
    try:
        robot = j.apps.zrobot.client.get(robot_name)
        services = j.apps.zrobot.client.listRobotServices(robot_name)
        templates = j.apps.zrobot.client.listRobotTemplates(robot_name)
        args.doc.applyTemplate({'robot': robot, 
                                'services': services, 
                                'templates': templates})
    except Exception as e:
        args.doc.applyTemplate({'error': str(e)})

    params.result = (args.doc, args.doc)
    return params