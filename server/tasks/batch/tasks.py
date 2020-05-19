import shutil

from server.tasks import ProgressTask, celery, logger


@celery.task(bind=True, base=ProgressTask)
def zip_files(
        self,
        output_filename: str,
        dir_name: str,
        update_url: str):

    # assigned id for this task
    # print(self.request.id)
    self.configure(update_url)

    logger.info("Started Zipping")
    progress = {'status': 'started', 'taskid': self.request.id}
    self.progress = progress

    shutil.make_archive(output_filename, 'zip', dir_name)
    progress['status'] = 'done'
    progress['filename'] = output_filename
    self.progress = progress
