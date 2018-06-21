from js9 import j

class zrobot_client(j.tools.code.classGetBase()):
    """
    Actor for managing 0-robot clients
    """
    def __init__(self):
        pass
        
        self._te={}
        self.actorname="client"
        self.appname="zrobot"
        #zrobot_client_osis.__init__(self)


    def add(self, url, name, **kwargs):
        """
        Add a new 0-robot client
        param:url address of the 0-robot server
        param:name name to give to the client instance
        result bool,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method add")

    def get(self, name, **kwargs):
        """
        Returns client instance info using the name
        param:name name of the client instance
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method get")

    def getService(self, robotName, guid, **kwargs):
        """
        Returns service info
        param:robotName name of the client instance
        param:guid service guid
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getService")

    def getTask(self, robotName, serviceGuid, taskGuid, **kwargs):
        """
        Returns task info
        param:robotName name of the client instance
        param:serviceGuid service guid
        param:taskGuid task guid
        result dict,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method getTask")

    def list(self, **kwargs):
        """
        List all available clients
        result [],
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method list")

    def listRobotServices(self, name, **kwargs):
        """
        List all services in a 0-robot server
        param:name name of the client instance
        result [],
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listRobotServices")

    def listRobotTemplates(self, name, **kwargs):
        """
        List all templates in a 0-robot server
        param:name name of the client instance
        result [],
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method listRobotTemplates")
