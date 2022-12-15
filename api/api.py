from fileinput import filename
import os, io, time, sys, base64
from flask import Flask, flash, request, make_response,redirect, url_for, session,jsonify, send_file, Response
from werkzeug.utils import secure_filename
from logging.config import dictConfig
from flask.logging import default_handler
import logging

import torch
from torch import nn
from torchvision import transforms
from torchvision.io import write_jpeg
from collections import OrderedDict
import pickle
from ColorNet import ColorResNet

from PIL import Image

UPLOAD_FOLDER = '/root/file-upload/public/uploaded_images'
CORRECTED_FOLDER = '/root/file-upload/public/corrected_images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'])

# normalization constants
SCALE_MEAN = torch.tensor([0.485, 0.456, 0.406])
SCALE_STD = torch.tensor([0.229, 0.224, 0.225])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TODO probably too small for video content, will need to update
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

#Simple, no nonsense file logging. includes print's and tracebacks
logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('access.log')
logger.addHandler(handler)

# Also add the handler to Flask's logger for cases
#  where Werkzeug isn't used as the underlying WSGI server.
app.logger.addHandler(handler)

app.secret_key = '\xf1!g\xcbT\x17\x1dF\xb8\xbc\xdf\xe5;=K\x04\x94\x85\xb1\xa8\x19\xb9\x98'

# net = torch.load('/root/file-upload/api/Models/ColorResNet_0_1_3.pt', map_location=torch.device('cpu')).float().eval()
global processingQueue
processingQueue = []

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

# function which establishes a new file name for the images, simple now
#   but may need to become more complex once other users are utilizing service
def correctedName(fileName):
    # current implementation just prepends "corrected_" on the front of the image
    # since we don't really use shifted, I'm just going to leave that be
    newName = "corrected_" + fileName
    return newName


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

def recolorImageNET(fileName):
    # this setting controls the intensity of corrections to purple/orange
    # this could be passed through the API
    
    # Previously only 0.4
    intensity = 0.8

    # load pil immage
    # img = Image.open('hotdog.jpg')
    img = Image.open(UPLOAD_FOLDER + "/" + fileName)

    # transform to prep for model
    tfms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=SCALE_MEAN,
            std=SCALE_STD
        )
    ])
    img_tensor = tfms(img)

    # prepare the model
    #OLD ATTEMPT
    # can also use ColorResNet_0_2_3.pt
    # net = torch.load('/root/file-upload/api/Models/ColorResNet_0_1_3.pt', map_location=torch.device('cpu')).float().eval()
    # net = ColorResNet().eval()

    name = 'Models/ColorResNet_0_2_3.pt'
    # name = 'Models/ColorResNet_0_1_3.pt'

    net = ColorResNet(0, 2, 3)
    # net = ColorResNet(0, 1, 3)
    new_state_dict = torch.load(name.split('.')[0]+'_state_dict.pt')
    net.load_state_dict(new_state_dict)

    # use the network to compute image shift
    with torch.no_grad():
        # need to prepend a dummy index to the img tensor
        shift = net(img_tensor[None]).squeeze()

    # shift the original image and rescale
    max_pos_shift = 0.5
    scaled_shift = (shift - 0.5)
    scaling_factor = scaled_shift.max() / max_pos_shift
    scaled_shift = scaled_shift / scaling_factor
    output_tensor = img_tensor + intensity * scaled_shift
    # output_tensor = img_tensor + intensity * shift
    output_tensor = output_tensor * SCALE_STD[:, None, None] + SCALE_MEAN[:, None, None]
    output_tensor = torch.clip(output_tensor, 0, 1)

    # save as corrected iamge
    output_img = (output_tensor * 255).type(torch.uint8)
    newName = "corrected_" + fileName 
    newPath = CORRECTED_FOLDER + "/" + newName
    #write_jpeg(output_img, 'hotdog_corr.jpg')
    write_jpeg(output_img, newPath)
    
    # write_jpeg(output_img, 'hotdog_corr.jpg')

    # for diagnostic purposes can save the shift image as well
    shift_img = ((shift - shift.min())/(shift.max() - shift.min()) * 255).type(torch.uint8)
    shiftedName = "shifted_" + fileName 
    shiftedPath = CORRECTED_FOLDER + "/" + shiftedName
    # write_jpeg(shift_img, 'hotdog_shift.jpg')
    write_jpeg(shift_img, shiftedPath)

    return newName

# Could pass in corrected filenames as a parameter for this function so that there's 
#   no potential confusion on what the names are to the system
def recolorImageNETList(files):
        # this setting controls the intensity of corrections to purple/orange
    # this could be passed through the API
    for file in files:
        fileName = file
        # Previously only 0.4
        intensity = 0.8

        # load pil immage
        # img = Image.open('hotdog.jpg')
        img = Image.open(UPLOAD_FOLDER + "/" + fileName)

        # transform to prep for model
        tfms = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=SCALE_MEAN,
                std=SCALE_STD
            )
        ])
        img_tensor = tfms(img)

        # prepare the model
        #OLD ATTEMPT
        # can also use ColorResNet_0_2_3.pt
        # net = torch.load('/root/file-upload/api/Models/ColorResNet_0_1_3.pt', map_location=torch.device('cpu')).float().eval()
        # net = ColorResNet().eval()

        name = 'Models/ColorResNet_0_2_3.pt'
        # name = 'Models/ColorResNet_0_1_3.pt'

        net = ColorResNet(0, 2, 3)
        # net = ColorResNet(0, 1, 3)
        new_state_dict = torch.load(name.split('.')[0]+'_state_dict.pt')
        net.load_state_dict(new_state_dict)

        # use the network to compute image shift
        with torch.no_grad():
            # need to prepend a dummy index to the img tensor
            shift = net(img_tensor[None]).squeeze()

        # shift the original image and rescale
        max_pos_shift = 0.5
        scaled_shift = (shift - 0.5)
        scaling_factor = scaled_shift.max() / max_pos_shift
        scaled_shift = scaled_shift / scaling_factor
        output_tensor = img_tensor + intensity * scaled_shift
        # output_tensor = img_tensor + intensity * shift
        output_tensor = output_tensor * SCALE_STD[:, None, None] + SCALE_MEAN[:, None, None]
        output_tensor = torch.clip(output_tensor, 0, 1)

        # save as corrected iamge
        output_img = (output_tensor * 255).type(torch.uint8)
        newName = "corrected_" + fileName 
        newPath = CORRECTED_FOLDER + "/" + newName
        #write_jpeg(output_img, 'hotdog_corr.jpg')
        write_jpeg(output_img, newPath)
        
        # write_jpeg(output_img, 'hotdog_corr.jpg')

        # for diagnostic purposes can save the shift image as well
        shift_img = ((shift - shift.min())/(shift.max() - shift.min()) * 255).type(torch.uint8)
        shiftedName = "shifted_" + fileName 
        shiftedPath = CORRECTED_FOLDER + "/" + shiftedName
        # write_jpeg(shift_img, 'hotdog_shift.jpg')
        write_jpeg(shift_img, shiftedPath)

@app.route('/api/upload', methods=['POST'])
def fileUpload():
    print("upload function called")
    print("ColorNet func  call", file=sys.stderr)
    app.logger.error("Made it into endpoint")
    #target=os.path.join(UPLOAD_FOLDER,'test_docs')
    #if not os.path.isdir(target):
    #    os.mkdir(target)
    target = UPLOAD_FOLDER
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    session['uploadFilePath']=destination
    print("DEBUG: filename attempted with " + filename)
    # correctedName = recolorImage(filename)
    correctedName = recolorImageNET(filename)
    correctedPath = CORRECTED_FOLDER + "/" + correctedName
    response = {
        "FileName" : filename,
        "CorrectedFileName" : correctedName
    }
    return jsonify(response),{'Content-Type': 'img/*'}

# gracefully handles empty submissions, could be easy to 
#   include a shortcircuit return that says "empty" or whatever
@app.route('/api/uploadMultiple', methods=['POST'])
def fileUploadMultiple():
    app.logger.error("multiple upload endpoint called")
    app.logger.error(request.values)
    app.logger.error(request.files)
    numFiles = int(request.values['numImages'])

    fileList = []

    for i in range(numFiles):
        target = UPLOAD_FOLDER

        currentFileKey = "image" + str(i)
        file = request.files[currentFileKey] 
        filename = secure_filename(file.filename)
        destination="/".join([target, filename])
        file.save(destination)
        session['uploadFilePath']=destination
        
        fileList.append(filename)
        app.logger.error(fileList)

    # app.logger.error(processingQueue[0])

    recolorImageNETList(fileList)

    response = {
        "FileName" : "dummy response"
    }
    return jsonify(response)

# Does not work
# @app.route('/api/uploadMultiple', methods=['POST'])
# def fileUploadMultiple():
#     # print("upload function called")
#     # print("ColorNet func  call", file=sys.stderr)
#     # app.logger.error("Made it into endpoint")
#     #target=os.path.join(UPLOAD_FOLDER,'test_docs')
#     #if not os.path.isdir(target):
#     #    os.mkdir(target)
#     target = UPLOAD_FOLDER
#     for file in request.files['file']:
#         file = request.files['file'] 
#         filename = secure_filename(file.filename)
#         destination="/".join([target, filename])
#         file.save(destination)
#         session['uploadFilePath']=destination
#         print("DEBUG: filename attempted with " + filename)
#         correctedName = recolorImageNET(filename)
#         correctedPath = CORRECTED_FOLDER + "/" + correctedName
#     # correctedName = recolorImage(filename)
#     # correctedName = recolorImageNET(filename)
#     # correctedPath = CORRECTED_FOLDER + "/" + correctedName
#     response = {
#         "FileName" : filename,
#         "CorrectedFileName" : correctedName
#     }
#     return jsonify(response)

# Example URL /api/getImage?image=hotdog_corr.jpg
@app.route('/api/getImage', methods=['GET'])
def getImage():
    # print("image endpoint called")
    app.logger.error("Made it into endpoint")
    desiredImage = request.args.get('image')
    app.logger.error("requested image name is " + desiredImage)

    # image_binary = Image.open((CORRECTED_FOLDER + "/" + desiredImage))
    # data = base64.b64encode(image_binary)
    # TODO LOOK AT OPEN FLAG R or RB!! TODO
    image = open((CORRECTED_FOLDER + "/" + desiredImage), "rb")
    image_b64 = base64.b64encode(image.read())
    image_b64 = image_b64.decode()

    response = {
        "msg": "success!",
        "format": "gobbleygook",
        "img": image_b64
    }
    return jsonify(response)

@app.route('/api/downloadImage', methods=['GET'])
def downloadImage():
    desiredImage = request.args.get('image')
    imagePath = CORRECTED_FOLDER + "/" + desiredImage
    return send_file(imagePath, as_attachment=True)

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

#@app.route('/api/getImage', methods=['GET'])
#def get_uncorrected_image():


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True,host="0.0.0.0",use_reloader=False)

