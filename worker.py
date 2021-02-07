import threading
import queue
import tempfile
import requests
from urllib.parse import urlparse
import os
import zipfile
from app import app

job_queue = queue.Queue()


def start_workers(n):
    app.logger.info("Starting {} worker thread(s)".format(n))
    for _ in range(n):
        threading.Thread(target=worker, daemon=True).start()


def worker():
    while True:
        job = job_queue.get()
        app.logger.info("Started processing job: {}".format(job))
        try:
            handle_job(job)
            app.logger.info("Job finished successfully: {}".format(job))
        except Exception as e:
            job["failed_status"] = job["status"]
            job["status"] = "FAILED"
            job["error"] = repr(e)
            app.logger.error("Job failed: {}", job)
        finally:
            job_queue.task_done()


def handle_job(job):
    src_list = job["input"]["srcList"]
    dst_storage = job["input"]["dstStorage"]
    job_id = job["id"]

    with tempfile.TemporaryDirectory() as src_dir:
        job["status"] = "DOWNLOADING"
        download_src_list(src_list, src_dir)
        with tempfile.TemporaryDirectory() as zip_tmp_dir:
            zip_path = os.path.join(zip_tmp_dir, "{}.zip".format(job_id))
            job["status"] = "ZIPPING"
            zip_dir(src_dir, zip_path)
            job["status"] = "UPLOADING"
            output_dst = upload_file(zip_path, dst_storage)

    job["status"] = "FINISHED"
    job["output"] = {
        "src": output_dst
    }


def download_src_list(src_list, src_dir):
    for src in src_list:
        download_src(src, src_dir)


def download_src(src, src_dir):
    filename = os.path.basename(urlparse(src).path)
    src_path = os.path.join(src_dir, filename)
    with open(src_path, 'wb') as src_file:
        file_stream = requests.get(src, stream=True)
        for chunk in file_stream.iter_content(chunk_size=1024 * 1024):
            src_file.write(chunk)


def zip_dir(src_dir, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for filename in os.listdir(src_dir):
            zip_file.write(os.path.join(src_dir, filename), filename)


# TODO: just copies to ./{filename} for now, upload to storage instead
def upload_file(path, dst_storage):
    from shutil import copyfile
    filename = os.path.basename(path)
    out_path = './{}'.format(filename)
    copyfile(path, out_path)
    return out_path
