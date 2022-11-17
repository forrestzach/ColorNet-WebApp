from fileinput import filename
import os
import time
from flask import Flask, flash, request, make_response,redirect, url_for, session,jsonify, Response
from werkzeug.utils import secure_filename

import torch
from torch import nn
from torchvision import transforms
from torchvision.io import write_jpeg

from PIL import Image

UPLOAD_FOLDER = '/root/file-upload/public/uploaded_images'
CORRECTED_FOLDER = '/root/file-upload/public/corrected_images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = '\xf1!g\xcbT\x17\x1dF\xb8\xbc\xdf\xe5;=K\x04\x94\x85\xb1\xa8\x19\xb9\x98'



class Network(nn.Module):
    """
    docstring
    """

    def __init__(self):
        super(Network, self).__init__()

        self.network = nn.Sequential(
            nn.Conv2d(3, 10, 3, 1, 1),
            nn.ReLU(),
            nn.Conv2d(10, 3, 3, 1, 1),
            nn.Sigmoid()
        )

    def forward(self, img_tensor):
        output_tensor = self.network(img_tensor)
        return output_tensor


def recolorImage(fileName):
    # load pil immage
    img = Image.open(UPLOAD_FOLDER + "/" + fileName)

    # transform to prep for model
    tfms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize(512)
    ])
    img_tensor = tfms(img)
    print(img_tensor.shape)

    # get output image using model
    net = Network()
    with torch.no_grad():
        output_tensor = net(img_tensor)
    print(output_tensor)

    # save as corrected iamge
    output_img = (output_tensor*255).type(torch.uint8)
    print(output_img.min(), output_img.max(), output_img.dtype)
    newName = "corrected_" + fileName 
    newPath = CORRECTED_FOLDER + "/" + newName
    #write_jpeg(output_img, 'hotdog_corr.jpg')
    write_jpeg(output_img, newPath)
    return newName

@app.route('/api/upload', methods=['POST'])
def fileUpload():
    print("upload function called")
    #target=os.path.join(UPLOAD_FOLDER,'test_docs')
    #if not os.path.isdir(target):
    #    os.mkdir(target)
    target = UPLOAD_FOLDER
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    session['uploadFilePath']=destination

    correctedName = recolorImage(filename)
    correctedPath = CORRECTED_FOLDER + "/" + correctedName


    response = {
        "FileName" : filename,
        "CorrectedFileName" : correctedName
    }
    return jsonify(response),{'Content-Type': 'img/*'}


@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

#@app.route('/api/getImage', methods=['GET'])
#def get_uncorrected_image():


if __name__ == "__main__":
     app.secret_key = os.urandom(24)
     app.run(debug=True,host="0.0.0.0",use_reloader=False)