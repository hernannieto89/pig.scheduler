import rpyc

from datetime import datetime

from .utils import run, teardown_relays


class SchedulerService(rpyc.Service):

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def exposed_add_job(self, *args, **kwargs):
        return self.scheduler.add_job(run, *args, next_run_time=datetime.now(), **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return self.scheduler.modify_job(job_id, jobstore, **changes)

    def exposed_reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args):
        return self.scheduler.reschedule_job(job_id, jobstore, trigger, **trigger_args)

    def exposed_pause_job(self, job_id, relays_used, jobstore=None):
        self.scheduler.pause_job(job_id, jobstore)
        teardown_relays(relays_used)

    def exposed_resume_job(self, job_id, jobstore=None):
        return self.scheduler.resume_job(job_id, jobstore)

    def exposed_remove_job(self, job_id, jobstore=None):
        return self.scheduler.remove_job(job_id, jobstore)

    def exposed_get_job(self, job_id):
        return self.scheduler.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return self.scheduler.get_jobs(jobstore)
