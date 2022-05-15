import sys
import os

import numpy as np
import json
from threading import Thread

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

sys.path.append("..")
from models.stat.lc import LC
from models.ml.snn import SNN

app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

complete = 0.0
error = None
file_path = ''
userFileName = ''
lc = None
snn = SNN()


def process_zip(content, ext):
    global complete, error, file_path

    try:
        with open('input.' + ext, 'wb') as outfile:
            outfile.write(content)
    except Exception:
        error = 'Unable to Save file'
        return

    complete = 0.8

    file_path = 'input.' + ext
    print(file_path)
    complete = 1.0


@ app.post('/upload')
async def upload(file: UploadFile = File(...)):
    global complete, file_path, error, lc, userFileName

    goodExts = ['lc', 'csv', 'ascii', 'hdf5']
    complete = 0.0
    file_path = ''
    userFileName = ''
    error = None
    lc = None
    os.system('rm -rf input*')
    os.system('rm -rf ../frontend/src/assets/*.jpg')

    userFileName = file.filename
    ext = userFileName.split('.')[-1]
    if ext not in goodExts:
        return {'status': 422,
                'error': 'File Format not supported. Must be {}.'.format('/'.join(goodExts))}
    content = await file.read()

    thread = Thread(target=process_zip, args=(content, ext))
    thread.start()

    complete = 0.3

    return {'status': 200}


@ app.get('/progress')
def progress():
    global complete, error, lc

    if error is not None:
        return {'status': 422, 'error': error}

    return {'status': 200, 'complete': complete}


@ app.get('/flares')
def bursts(bin_size: int = 100):
    global snn, file_path, lc

    print(file_path)
    lc = LC(file_path, bin_size)

    flares = lc.get_flares()
    conf_list = snn.get_conf(lc.get_ml_data())

    for i in range(len(flares)):
        flares[i]['ml_conf'] = round(100.0 * conf_list[i])

    return {'status': 200, 'flares': flares, 'total': {**lc.get_lc(), 'file_name': userFileName}}


@ app.post('/train')
def train(content: str = Form(...)):
    global snn, lc

    content = json.loads(content)
    labels = np.array(content['labels'])

    snn.train(lc.get_ml_data(), labels, epochs=10)
    snn.save_chkpt()

    return {'status': 200}
