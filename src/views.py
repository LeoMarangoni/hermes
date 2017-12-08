from flask.views import MethodView
from flask import jsonify, request
from model import (Accounts, AccountCredentials,
                   AccountInfo, Projects,
                   ProjectInfo, Queue)
import json


class ProjectsAPI(MethodView):
    def get(self, id=None):
        if (id is None):
            p = Projects.objects()
            envelop = "projects"
        else:
            p = Projects.objects(id=id).first()
            envelop = "project"
        p = json.loads(p.to_json())
        return jsonify({envelop: p})

    def post(self):
        data = request.get_json()
        p = Projects()
        self.updateProject(data, p)
        if 'accounts' in locals()['data']:
            for account in data['accounts']:
                p.accounts.create(**account)
        p.save()
        return (jsonify({"message": "Project created"}))

    def put(self, id):
        data = request.get_json()
        p = Projects.objects(id=id).first()
        self.updateProject(data, p)
        p.save()
        return (jsonify({"message": "Project updated"}))

    def delete(self, id):
        p = Projects.objects(id=id).first()
        p.delete()
        q = Queue.objects(projectId=id)
        if q:
            q.delete()
        return jsonify({"message": "project deleted"})

    def updateProject(self, data, p):
        # TODO Refact with a for loop in locals()[data]
        if 'info' in locals()['data']:
            info = p.info
            for key in data['info']:
                setattr(info, key, data['info'][key])
            setattr(p, "info", info)
        if 'configs' in locals()['data']:
            setattr(p, "configs", data['configs'])


class AccountsAPI(MethodView):
    def get(self, p_id, a_id=None):
        p = json.loads(Projects.objects(id=p_id).first().to_json())
        if (a_id is None):
            envelop = "accounts"
            print p
            a = p['accounts']
        else:
            envelop = "account"
            a = p['accounts'][a_id]
        return jsonify({envelop: a})

    def post(self, p_id):
        data = request.get_json()
        p = Projects.objects(id=p_id).first()
        p.accounts.create(**data)
        p.save()
        return jsonify({"message": "account added"})

    def put(self, p_id, a_id):
        data = request.get_json()
        a = Projects.objects(id=p_id).first().accounts[a_id]
        self.updateAccount(data, a)
        a.save()
        return jsonify({"message": "account updated"})

    def delete(self, p_id, a_id):
        # TODO: Remove account from queue
        p = Projects.objects(id=p_id).first()
        a = p.accounts[a_id]
        p.accounts.remove(a)
        p.save()
        return jsonify({"message": "account removed"})

    def updateAccount(self, data, a):
        # TODO Refact with a for loop in locals()[data]
        if 'info' in locals()['data']:
            info = a.info
            for key in data['info']:
                setattr(info, key, data['info'][key])
            setattr(a, "info", info)
        if 'credentials' in locals()['data']:
            cred = a.credentials
            for key in data['credentials']:
                setattr(cred, key, data['credentials'][key])
            setattr(a, "credentials", cred)
        return jsonify({"message": "account updated"})


class QueueAPI(MethodView):
    def get(self, p_id=None, a_id=None):
        if (p_id is None):
            q = Queue.objects()
        else:
            if (a_id is None):
                q = Queue.objects(projectId=p_id)
            else:
                q = Queue.objects(projectId=p_id, index=a_id)
        data = json.loads(q.to_json())
        return jsonify(data)

    def post(self, p_id, a_id=None, popstring=None):
        p = json.loads(Projects.objects(id=p_id).first().to_json())
        if (a_id is None):
            accounts = p['accounts']
        else:
            accounts = []
            accounts.append(p['accounts'][a_id])
        for account in accounts:
            command = self.param_parser(p['configs'], account['credentials'])
            index = p["accounts"].index(account)
            self.queue_add(index, p_id, command)
            print "%s, %s, %s" % (index, p_id, command)
        n = str(len(accounts))
        return jsonify({"message": n + " account(s) added to queue"})

    def put(self, p_id, a_id=None):
        pass

    def delete(self, p_id=None, a_id=None):
        if (a_id is None):
            if (p_id is None):
                q = Queue.objects()
            else:
                q = Queue.objects(projectId=p_id)
        else:
            q = Queue.objects(projectId=p_id, index=a_id)
        n = str(q.delete())
        return jsonify({"message": n + " account(s) removed from queue"})

    def param_parser(self, configs, credentials):
        command = ""
        parameters = []
        if (credentials is not list):
            credentials = [credentials]
        parameters.extend(configs)
        parameters.extend(credentials)
        for parameter in parameters:
            if type(parameter) is not dict:
                if (parameter != "" and parameter != " "):
                    command += "--%s " % (parameter)
            else:
                for key in parameter.keys():
                    command += "--%s %s " % (key, parameter[key])
        return (command)

    def queue_add(self, a_id, p_id, command, q=None):
        data = {"index": a_id,
                "command": command,
                "projectId": p_id}
        if (q is None):
            q = Queue()
        for key in data.keys():
            setattr(q, key, data[key])
        q.save()
