from js9 import j
from JumpScale9Portal.portal import exceptions
from JumpScale9Portal.portal.exceptions import catcherrors
from JumpScale9Portal.portal.auth import auth
from zerorobot.task import TaskNotFoundError
import requests


class zrobot_client(j.tools.code.classGetBase()):
    def __init__(self):
        super(zrobot_client, self).__init__()

    def _check_zrobot(self, name):
        if name not in j.clients.zrobot.list():
            raise exceptions.NotFound("Couldn't find robot instance: {}".format(name))

    @property
    def portal_url(self):
        return j.core.state.configGet('portal')['main']['public_url']

    @auth(['admin'])
    @catcherrors(msg='')
    def add(self, url, name, godToken=None, **kwargs):
        if not self.portal_url:
            raise exceptions.BadRequest('portal_url not configured in js9 portal config.')
        if name in j.clients.zrobot.list():
            raise exceptions.Conflict('robot instance: {} already in the portal'.format(name))

        zrobot = j.clients.zrobot.new(name, data={'url': url})
        if godToken:
            zrobot.god_token_set(godToken)
        ctx = kwargs['ctx']
        authkey = j.apps.system.usermanager.addAuthkey('robot', name, ctx=ctx)

        try:
            zrobot.api.robot.AddWebHook({'url': '{0}/restmachine/zrobot/client/taskCallback?authkey={1}'.format(self.portal_url, authkey), 'kind': 'eco'})
        except (requests.exceptions.ConnectionError, ConnectionError):
            j.apps.system.usermanager.deleteAuthkey('robot', name, ctx=ctx)
            j.clients.zrobot.delete(name)
            raise
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
    @catcherrors(msg='')
    def list(self, **kwargs):
        if not j.core.state.configGetFromDict("myconfig", "path", ''):
            raise exceptions.BadRequest("Please setup config manager before using the portal.")
        results = []
        for instance in j.clients.zrobot.list():
            results.append(self._zrobot_data(instance))
        return results

    @auth(['admin'])
    @catcherrors(msg='')
    def get(self, name, **kwargs):
        if not self.portal_url:
            raise exceptions.BadRequest('portal_url not configured in js9 portal config.')
        self._check_zrobot(name)
        return self._zrobot_data(name, True)

    @auth(['admin'])
    @catcherrors(msg='')
    def delete(self, name, **kwargs):
        j.apps.system.usermanager.deleteAuthkey('robot', name, ctx=kwargs['ctx'])
        j.clients.zrobot.delete(name)
        return True

    @auth(['admin'])
    @catcherrors(msg='')
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

    def _get_service(self, robotName, guid):
        self._check_zrobot(robotName)
        zrobot_api = j.clients.zrobot.robots[robotName]
        if guid not in zrobot_api.services.guids:
            raise exceptions.NotFound("Couldn't find service with guid: {}".format(guid))
        service = zrobot_api.services.guids[guid]
        return service

    @auth(['admin'])
    @catcherrors(msg='')
    def getService(self, robotName, guid,**kwargs):
        robot_url = self._zrobot_data(robotName)['url']
        service = self._get_service(robotName, guid)
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
            'data': service.data,
            'guid': service.guid,
            'template': str(service.template_uid),
            'tasks': tasks_data,
            'states': service.state.categories,
            'robotAddress': robot_url,
        }
        
        return result

    @auth(['admin'])
    @catcherrors(msg='')
    def getServiceLogs(self, robotName, guid, **kwargs):
        service = self._get_service(robotName, guid)
        try:
            service_logs = service.logs
        except RuntimeError as e:
            raise exceptions.Unauthorized(str(e))
        logs = {
            'data': service_logs
        }
        return logs

    def taskCallback(self, eco, service, **kwargs):
        lasttime = eco['time_last']
        uniquekey = j.data.hash.md5_string(eco['trace'])
        appname = 'Robot service:{}'.format(service)
        ecoobj = j.portal.tools.models.system.Errorcondition.objects(uniquekey=uniquekey).first()
        if ecoobj:
            ecoobj.update(inc__occurrences=1, errormessage=eco['message'], lasttime=lasttime)
        else:
            j.portal.tools.models.system.Errorcondition(
                pid=eco.get('pid', 0),
                uniquekey=uniquekey,
                jid=eco.get('jid', 0),
                masterjid=eco.get('masterjid', 0),
                appname=appname,
                level=eco.get('level', 1),
                type=eco['type', 'DEBUG'],
                state=eco['state', 'ERROR'],
                errormessage=eco['message'],
                errormessagePub=eco['message_pub'],
                category=eco['cat'],
                tags=eco.get('tags', ''),
                code=eco.get('code', ''),
                funcname=eco.get('funcname', ''),
                funcfilename=eco.get('funcfilename', ''),
                funclinenr=eco.get('funclinenr', ''),
                backtrace=eco['trace'],
                lasttime=lasttime,
                closetime=eco.get('closetime'),
                occurrences=eco.get('count')
            ).save()

    @auth(['admin'])
    @catcherrors(msg='')
    def getTask(self, robotName, serviceGuid, taskGuid, **kwargs):
        service = self._get_service(robotName, serviceGuid)
        try:
            task = service.task_list.get_task_by_guid(taskGuid)
        except TaskNotFoundError:
            raise exceptions.NotFound("Couldn't find task with guid: {}".format(taskGuid))

        ecoid = ''
        duration = "{0:.8f}".format(task.duration) if task.duration else 'Duration info not available yet.'
        if task.eco:
            eco = j.portal.tools.models.system.Errorcondition.find({'uniquekey': task.eco.uniquekey})[0]
            ecoid = str(eco.pk)
        data = {
            'actionName': task.action_name,
            'guid': task.guid,
            'createdTime': j.data.time.epoch2HRDateTime(task.created),
            'state': task.state,
            'duration': duration,
            'result': task.result or '',
            'ecoid': ecoid
            }
        return data

    @auth(['admin'])
    @catcherrors(msg='')
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
