from rpyc.utils.server import ThreadedServer

from apscheduler.schedulers.background import BackgroundScheduler

from scheduler import SchedulerService

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.start()
    protocol_config = {'allow_public_attrs': True}
    server = ThreadedServer(SchedulerService, port=12345, protocol_config=protocol_config)
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
