import rpyc

from .utils import run, teardown_relays

class SchedulerService(rpyc.Service):
    def exposed_add_job(self, *args, **kwargs):
        return self.add_job(run, *args, **kwargs)

    def exposed_modify_job(self, job_id, jobstore=None, **changes):
        return self.modify_job(job_id, jobstore, **changes)

    def exposed_reschedule_job(self, job_id, jobstore=None, trigger=None, **trigger_args):
        return self.reschedule_job(job_id, jobstore, trigger, **trigger_args)

    def exposed_pause_job(self, job_id, jobstore=None):
        return self.pause_job(job_id, jobstore)

    def exposed_resume_job(self, job_id, jobstore=None):
        return self.resume_job(job_id, jobstore)

    def exposed_remove_job(self, job_id, relays_used, jobstore=None):
        teardown_relays(relays_used)
        self.remove_job(job_id, jobstore)

    def exposed_get_job(self, job_id):
        return self.get_job(job_id)

    def exposed_get_jobs(self, jobstore=None):
        return self.get_jobs(jobstore)
