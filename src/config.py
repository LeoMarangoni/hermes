apiconfig = {
    "host": "127.0.0.1",
     "port": 5500,
     "debug": False,
     "threaded": True
}
dbconfig = {
    "db": "hermesdb",
#    "host": "localhost",
#    "port": 27017,
#    "username": "hermesadmin",
#    "password": "hermespasswd"
}
plugins = {
    "imap": {
        "image": "marangoni/imapsync",
        "logdir": "/tmp/var/LOG_imapsync",
        "entrypoint": "/usr/bin/imapsync"
    },
    "zimbra": {
        "image": "marangoni/zmzsync",
        "logdir": "/LOG_zmzsync",
        "entrypoint": "/usr/bin/zmzsync"
    }
}
