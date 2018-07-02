import requests
from js9 import j
def init():
    portal_url = j.core.state.configGet('portal')['main']['public_url']
    if not j.core.state.configGetFromDict("myconfig", "path", '') or not portal_url:
        return
    res = j.portal.tools.models.system.User.objects(name='robot')
    if not res:
        j.portal.tools.server.active.auth.createUser('robot', 'robotRx', ['robot@tmp.com'], ['admin'])
        res = j.portal.tools.models.system.User.objects(name='robot')
    admin_user = res[0]
    authkeys = admin_user.authkeys.keys()
    for instance in j.clients.zrobot.list():
        if instance not in authkeys:
            authkey = j.portal.tools.server.active.auth.addAuthkey('robot', instance)
            zrobot = j.clients.zrobot.get(instance)
            try:
                zrobot.api.robot.AddWebHook({'url': '{0}/restmachine/zrobot/client/taskCallback?authkey={1}'.format(portal_url, authkey), 'kind': 'eco'})
            except (requests.exceptions.ConnectionError, ConnectionError):
                j.portal.tools.server.active.auth.deleteAuthkey('robot', instance)