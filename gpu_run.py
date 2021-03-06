from flask import Flask, request
from flask_cors import CORS

from server.awsModule import *

import os
import sys

from gpuEngine import *
from gpuEngine.U2Net import u2net_test as u2test
from gpuEngine import U2Net
from gpuEngine import SuperResolution
import numpy as np
import asyncio
from PIL import Image
from ISR.models import RDN
from ISR.models import RRDN

from gpuEngine.U2Net.model import U2NET 
import torch


async def async_U2Net(outputName, net_model):
    u2test.main(outputName, net_model)

async def async_iconify(outputName):
    iconify.run(outputName)

app=Flask(__name__)
CORS(app)

#u2net model
model_name='u2net'
model_dir = os.path.join(os.getcwd(),'gpuEngine/U2Net/saved_models', model_name, model_name + '.pth')
print("...load U2NET---173.6 MB")
net = U2NET(3,1)
net.load_state_dict(torch.load(model_dir))
if torch.cuda.is_available():
    net.cuda()
net.eval()

#flask test
@app.route("/hello",methods=['GET'])
def hello():
    return "hihi"


@app.route("/backrmv",methods=['POST'])
def backrmv():
    inputName = request.form.to_dict()['fileName']
    outputName = 'backRmv_'+inputName.split('.')[0] + '.png'

    # 원래 사진 파일 s3에서 다운로드
    downloadFileFromS3('inputImage/backgroundRemoval/'+inputName,outputName)

    # background removal 하기
    #loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    print('new_event_loop()')
    asyncio.set_event_loop(loop)
    print('set_event_loop()')
    loop.run_until_complete(async_U2Net(outputName, net))
    print('run_until_complete(u2net)')
    loop.close()  
    print(loop.is_closed())

    # 후처리된 사진 파일 s3에 업로드 (+서버에선 파일 지움)
    uploadFileToS3(outputName, 'outputImage/backgroundRemoval/'+outputName)
    print('s3 upload')
    os.remove(outputName)
    print('remove')
    # 파일 다운로드 s3 링크 받아오기
    url = getUrlFromS3('outputImage/backgroundRemoval/'+outputName)

    # 클라이언트로 링크 전송
    return url

@app.route("/supresol",methods=['POST'])
def supresol():
    inputName = request.form.to_dict()['fileName']
    outputName = 'SR_'+inputName.split('.')[0] + '.jpg'

    # 원래 사진 파일 s3에서 다운로드
    downloadFileFromS3('inputImage/superResolution/'+inputName,outputName)

    # super resolution 하기
    # chanel 4 ->3
    lr_img = Image.open(outputName).convert("RGB")
    lr_img_np = np.array(lr_img)

    print("...load RRDN-GAN...")
    sr_model = RRDN(weights = 'gans')

    sr_img_gan = sr_model.predict(lr_img_np)
    sr_img_gan = Image.fromarray(sr_img_gan)
    sr_img_gan.save(outputName)    

    # 후처리된 사진 파일 s3에 업로드 (+서버에선 파일 지움)
    uploadFileToS3(outputName, 'outputImage/superResolution/'+outputName)
    os.remove(outputName)
    # 파일 다운로드 s3 링크 받아오기
    url = getUrlFromS3('outputImage/superResolution/'+outputName)

    # 클라이언트로 링크 전송
    return url

@app.route("/iconify",methods=['POST'])
def iconify():
    inputName = request.form.to_dict()['fileName']
    outputName = 'iconify_'+inputName

    # 원래 사진 파일 s3에서 다운로드
    downloadFileFromS3('inputImage/iconify/'+inputName,outputName)

    # iconify 하기
    #loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    print('new_event_loop()')
    asyncio.set_event_loop(loop)
    print('set_event_loop()')
    loop.run_until_complete(async_iconify(outputName))
    print('run_until_complete(iconify)')
    loop.close()  
    print(loop.is_closed())

    # 후처리된 사진 파일 s3에 업로드 (+서버에선 파일 지움)
    uploadFileToS3(outputName, 'outputImage/iconify/'+outputName)
    os.remove(outputName)

    # 파일 다운로드 s3 링크 받아오기
    url = getUrlFromS3('outputImage/iconify/'+outputName)

    # 클라이언트로 링크 전송
    return url


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6789, debug=True)

