from js9 import j
from JumpScale9Portal.portal import exceptions
from JumpScale9Portal.portal.auth import auth
from zerorobot.task import TaskNotFoundError
import time

class zrobot_client(j.tools.code.classGetBase()):
    def __init__(self):
        super(zrobot_client, self).__init__()

    def _check_zrobot(self, name):
        if name not in j.clients.zrobot.list():
            raise exceptions.NotFound("Couldn't find robot instance: {}".format(name))

    @auth(['admin'])
    def add(self, url, name, **kwargs):
        if name in j.clients.zrobot.list():
            raise exceptions.Conflict('robot instance: {} already in the portal'.format(name))

        j.clients.zrobot.new(name, data={'url': url})
        return True

    def _zrobot_data(self, name, all_data=False):
        zrobot = j.clients.zrobot.get(name)
        data = zrobot.config.data
        result = {'url': data['url'], 'name': zrobot.instance}
        if all_data:
            metrics, _ = zrobot.api.robot.GetMetrics()
            metrics = metrics.as_dict()
            memory_metrics = metrics['memory']

            for mem, val in memory_metrics.items():
                memory_metrics[mem] = int(j.data_units.sizes.toSize(val, output='M'))

            robot_info, _ = zrobot.api.robot.GetRobotInfo()
            extra = {
                'info': robot_info.as_dict(),
                'metrics': metrics,
                'jwt': data['jwt_'],
                'secrets': data['secrets_']
            }
            result.update(extra)
        return result

    @auth(['admin'])
    def list(self, **kwargs):
        results = []
        for instance in j.clients.zrobot.list():
            results.append(self._zrobot_data(instance))
        return results

    @auth(['admin'])
    def get(self, name, **kwargs):
        self._check_zrobot(name)
        return self._zrobot_data(name, True)

    @auth(['admin'])
    def listRobotServices(self, name, **kwargs):
        self._check_zrobot(name)
        zrobot_api = j.clients.zrobot.robots[name]
        results = []
        for service in zrobot_api.services.find():
            res = {
                'name': service.name,
                'guid': service.guid,
                'template': str(service.template_uid)
            }
            results.append(res)
        return results

    @auth(['admin'])
    def getService(self, robotName, guid,**kwargs):
        self._check_zrobot(robotName)
        robot_url = self._zrobot_data(robotName)['url']
        zrobot_api = j.clients.zrobot.robots[robotName]
        if guid not in zrobot_api.services.guids:
            raise exceptions.NotFound("Couldn't find service with guid: {}".format(guid))
        service = zrobot_api.services.guids[guid]
        task_list = service.task_list
        tasks_data = []
        for task in task_list.list_tasks(all=True):
            task_data = {
                'actionName': task.action_name,
                'guid': task.guid,
                'createdTime': j.data.time.epoch2HRDateTime(task.created),
                'state': task.state
            }
            tasks_data.append(task_data)

        result = {
            'name': service.name,
            'guid': service.guid,
            'template': str(service.template_uid),
            'tasks': tasks_data,
            'states': service.state.categories,
            'robotAddress': robot_url
        }
        
        return result

    def taskCallback(self, eco, **kwargs):
        lasttime = eco['lasttime'] or time.time()
        ecoobj = j.portal.tools.models.system.Errorcondition.objects(uniquekey=eco['uniquekey']).first()
        if ecoobj:
            ecoobj.update(inc__occurrences=1, errormessage=eco['errormessage'], lasttime=lasttime)
        else:
            j.portal.tools.models.system.Errorcondition(
                pid=eco['pid'],
                uniquekey=eco['uniquekey'],
                jid=eco['jid'],
                masterjid=eco['masterjid'],
                appname=eco['appname'],
                level=eco['level'],
                type=eco['type'],
                state=eco['state'],
                errormessage=eco['errormessage'],
                errormessagePub=eco['errormessagePub'],
                category=eco['category'],
                tags=eco['tags'],
                code=eco['code'],
                funcname=eco['funcname'],
                funcfilename=eco['funcfilename'],
                funclinenr=eco['funclinenr'],
                backtrace=eco['_traceback'],
                lasttime=lasttime,
                closetime=eco['closetime'],
                occurrences=eco['occurrences']
            ).save()

    @auth(['admin'])
    def getTask(self, robotName, serviceGuid, taskGuid, **kwargs):
        self._check_zrobot(robotName)
        zrobot_api = j.clients.zrobot.robots[robotName]
        if serviceGuid not in zrobot_api.services.guids:
            raise exceptions.NotFound("Couldn't find service with guid: {}".format(serviceGuid))
        service = zrobot_api.services.guids[serviceGuid]
        try:
            task = service.task_list.get_task_by_guid(taskGuid)
        except TaskNotFoundError:
            raise exceptions.NotFound("Couldn't find task with guid: {}".format(taskGuid))

        ecoid = ''
        if task.eco.uniquekey:
            eco = j.portal.tools.models.system.Errorcondition.find({'uniquekey': task.eco.uniquekey})[0]
            ecoid = str(eco.pk)
        data = {
            'actionName': task.action_name,
            'guid': task.guid,
            'createdTime': j.data.time.epoch2HRDateTime(task.created),
            'state': task.state,
            'duration': "{0:.8f}".format(task.duration),
            'result': task.result or '',
            'ecoid': ecoid
            }
        return data

    @auth(['admin'])
    def listRobotTemplates(self, name, **kwargs):
        self._check_zrobot(name)
        zrobot_api = j.clients.zrobot.robots[name]
        templates = zrobot_api.templates.uids
        results = []
        for template in templates.values():
            res = {
                'uid': template.uid,
                'name': template.name
            }
            results.append(res)

        return results
