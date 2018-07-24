import json
import shlex
import logging
import os
import socket
import subprocess
import psycopg2
import uuid

FNAME=os.path.basename(__file__)
PID=os.getpid()
HOST=socket.gethostname()

# set up logging
log_filename='trainer_{}.log'.format(os.getpid())
log_format = '%(levelname)s %(asctime)s {pid} {filename} %(lineno)d %(message)s'.format(
        pid=PID, filename=FNAME)
logging.basicConfig(format=log_format,
    filename='/var/log/trainerlogs/{}'.format(log_filename),
    datefmt='%Y-%m-%dT%H:%M:%S%z',
    level=logging.INFO)
logger = logging.getLogger('trainer')

try:
    JOB_ID = os.environ['JOB_ID']
    DB_NAME = os.environ.get('DB_NAME', 'nlp')
    DB_PASSWORD = os.environ.get('DB_PASS', '')
    DB_USER = os.environ.get('DB_USER', DB_NAME)
    JM_USER = os.environ['JM_USER']
    JM_PASS = os.environ['JM_PASS']
except KeyError as e:
    logger.info('critical environment variables were not set. exiting')
    raise e


def cast_spell():
    inline_pip_args = ""
    with open('spell/requirements.txt') as f:
        for dep in f:
            inline_pip_args += '--pip {} '.format(dep.replace('\n', ''))

    #v100 is the rocket ship, k80 is a volvo
    spell_script = 'spell run {pipargs} --env SECRET={secret} --env JOB_ID={job_id} \
            --env JM_USER={JM_USER} \
            --env JM_PASS={JM_PASS} \
            --force \
            --framework \
            tensorflow==1.8.0 --env API_URL={api_url} --python3 \
            -t k80 "python spell/train.py"'.format(
            secret="TODO", job_id=JOB_ID, api_url="http://206.81.5.140",
            pipargs=inline_pip_args, JM_USER=JM_USER, JM_PASS=JM_PASS)
    subprocess.call(shlex.split(spell_script))
    logger.info('Avada kedavra!!')

if __name__ == '__main__':
    cast_spell()
