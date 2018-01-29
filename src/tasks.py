"""This Module handle all asynchronous tasks on API."""
import docker
import requests
import time
import threading
import json
from config import plugins
from model import Projects, Queue

class tasks():
    """Migration Tasks Manager.

    This class checks if there are any projects created and if they have
    accounts in the migration queue.
    Construct it in the main program to start his execution.
    """

    def __init__(self, interval=10):
        """Constructor.

        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.cli = docker.from_env()
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        """Run until the main program's death."""
        while True:
            print "Quering for finished migrations..."
            containers = self.cli.containers.list(all=True,
                                                  filters={"name":
                                                           "hermesapi",
                                                           "status":
                                                           "exited"})
            if type(containers) == list:
                for container in containers:
                    name = container.name.split("__")
                    if container.wait() == 0:
                        status = "success"
                    else:
                        status = "failure"
                    account = Projects.objects(id=name[1]).first()['accounts'][int(name[2])]
                    setattr(account.info, "status", status)
                    account.save()
                    print account.to_json()
                    container.remove()
            print "Quering for projects..."
            projects = json.loads(Projects.objects().to_json())
            for project in projects:
                threads = project['info']['threads']
                print project['info']
                protocol = project['info']['protocol']
                project = project['_id']['$oid']
                running = len(self.cli.containers.list(filters={'name':
                                                                project}))
                if running < threads:
                    threads = threads - running
                    threads = range(0, threads)
                    for thread in threads:
                        next_account = Queue.objects(projectId=project).first()
                        if next_account:
                            index = next_account['index']
                            cmd = next_account['command']
                            next_account.delete()
                            self.cli.containers.run(
                                plugins[protocol]['image'],
                                cmd,
                                detach=True,
                                name="hermesapi__%s__%s"
                                % (project, index),
                                entrypoint=plugins[protocol]['entrypoint'],
                                volumes={
                                    "/var/log/hermes/migrations": {
                                        'bind': plugins[protocol]['logdir'],
                                        'mode': 'rw'
                                    }
                                }
                            )
                            account = Projects.objects(id=project).first()['accounts'][index]
                            setattr(account.info, "status", "running")
                            account.save()
                        else:
                            print (
                                "No accounts in queue for project %s"
                                % (project)
                            )
                else:
                    print (
                        "thread limit reached, looking for next project"
                    )

            print "Done! Sleeping for %s seconds" % (self.interval)
            time.sleep(self.interval)
