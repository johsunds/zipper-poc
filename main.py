from flask import request, jsonify, abort, make_response
import uuid
import os
from worker import start_workers, job_queue
from boundeddict import BoundedDict
from app import app

jobs = BoundedDict(max_size=1000)

start_workers(os.environ.get("ZIPPER_THREADS", 3))

'''
 Example:
    POST /zip
    {
        "srcList": ["http://localhost:8080/myfile1", "http://localhost:8080/myfile2"],
        "dstStorage": "VX-1"
    }
'''


@app.route('/zip', methods=['POST'])
def start_job():
    try:
        job_id = str(uuid.uuid4())
        job_input = request.json
        jobs[job_id] = {
            "status": "QUEUED",
            "input": job_input,
            "id": job_id,
        }
        job_queue.put(jobs[job_id])
        return jsonify({"id": job_id})
    except Exception as e:
        abort(make_response(jsonify(message="Failed to start job", error=repr(e)), 400))


@app.route('/zip', methods=['GET'])
def list_jobs():
    return jsonify(jobs)


@app.route('/zip/<job_id>', methods=['GET'])
def get_job(job_id):
    try:
        return jsonify(jobs[job_id])
    except Exception as e:
        abort(make_response(jsonify(message="Job not found", error=repr(e)), 404))
