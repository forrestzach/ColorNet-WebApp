ColorNet Webapp Documentation
Forrest Zach

Basics:
The current ColorNet Web Application tech stack utilizes React for the frontend and Flask (Python) for the backend/API. Nginx is used as the web server hosting service while Gunicorn is the web server gateway interface (WSGI) which provides an interface for the backend. All of this code is stored and runs on our current IBM Watson Machine where the webapp is actively developed and deployed on.
The primary directory for this project is “/root/file-upload”.

Frontend:
React is the frontend javascript library utilized in this application. There are not many other packages utilized beyond the basic React installation, at this time. 

The code in development and which can be modified is under “/root/file-upload/src” with the most important component being “/root/file-upload/src/components/FileUpload.js” specifically. FileUpload.js is where nearly all of the frontend javascript code lives, with “/root/file-upload/src/App.js” being the one which pulls in that component and displays it to the user.

When changes have been made to the webapp it must be compiled (built)deployed in order to view the changes in visuals/functionality. When built, the compiled and optimized javascript files are stored in the directory “/root/file-upload/build”. More details on this idea/process are in the “Deployment” section of this document.

Currently, the webapp must be deployed to production and be live to users on the internet in order to test its functionality between the frontend and backend. This is primarily due to the complication of developing in a remote environment (and the lack of the lead developer’s knowledge on how to get it working easily otherwise).

Troubleshooting: Compile errors will show up when you attempt to deploy/build the webapp, those should be displayed in the output of whatever terminal you are running the deployment script in. To read output from the frontend such as variables and such I utilize “console.log(“Text to display”)” and it will be displayed in the console of your web browser.
For errors with troubleshooting endpoint calls on the frontend side, I recommend using your browser’s “Developer Tools”. Chrome has a good built-in suite that is helpful.

Backend:
Python (3.9.13) is the language utilized for the backend, with a significant portion being focused on utilizing the Flask web framework and PyTorch libraries. The Flask API runs in the background as a locally hosted service on the host machine, on 127.0.0.1:5000 specifically. Gunicorn, the WSGI service mentioned earlier, is what keeps the backend running in the background in a production environment.

The code in development and which can be modified is under “/root/file-upload/api” with the actual API code itself existing in “/root/file-upload/api/api.py”. In api.py, you can find the code for the endpoints along with some helper functions, and even the functions which call/run the ColorNet algorithm. The classes used in the ColorNet algorithm can be found in “/root/file-upload/api/ColorNet.py” with the models living in “/root/file-upload/api/Models”. 

In order to install/add new packages to the miniconda environment simply use “source activate myenv” in order to access the environment which the api.py file uses. 
Warning: There is still the basic venv environment “venv” in the code base, be careful to use the miniconda environment as that is what the pytorch libraries are installed under.

Troubleshooting: When you need to read what error messages the python code is outputting, or if you want some text/variables printed for troubleshooting then simply look at “/root/file-upload/api/access.log”. This is where the error messages will be printed out and where data can be printed out from the backend, so long as “app.logger.error(“Text to print”)” is utilized. The app.logger.error() functions the same way as the typical python print() function so variables or anything can be thrown in there and displayed.

If you are racking your brain trying to figure out why nothing is outputting/working on the backend, double check that you are in fact using app.logger.error() instead of the usual print().

Note: On a rare occasion, the backend may enter an error state when trying to deploy and will not be responding properly. I believe this comes from trying to restart it when it is already in the compilation process. Simply rerunning the deploy command or restarting the whole machine should resolve this irregularity.

Deployment:
As mentioned previously, the webapp must be deployed into a production environment in order for the frontend and backend to communicate properly with each other. This process is simplified by a simple script I have created which can be accessed at “/root/file-upload/deploy.sh”. I will copy it here and explain each step thoroughly.

#!/bin/sh
bld='npm run build'
$bld
echo BUILD COMPLETED
 
reloadNGX='sudo systemctl reload nginx'
$reloadNGX
echo RELOADING NGINX COMPLETED
 
reloadFLSK='sudo systemctl restart flask-react-app.service'
$reloadFLSK
echo RESTARTING FLASK API COMPLETED

Here, you can see that deploying the application is a simple three step process, which only takes 5-6 seconds to complete. 

The way this bash script works is that each variable receives the string of a given command, “reloadNGX=’sudo systemctl reload nginx’” for example, and then runs that string as if it were a command typed out in the terminal with “$reloadNGX”.

The first is building the frontend, this compiles and optimizes the React code into web browser ready files. This is when any compile/syntax errors will show up for the frontend. 
The second is the command to reload the Nginx web server process. It is only reloading because nothing changes for Nginx in this step, it is simply looking at a certain directory (the React build directory at “/root/file-upload/build”)
The third is restarting the API backend which is the step where the python code is compiled and then established as a live service. To view compile/runtime errors, check the notes on the backend troubleshooting content.

You can easily check the status of whether the backend is currently running or not by running “sudo systemctl status flask-react-app.service” which will show what is currently happening with that process.

Upon the IBM machine restarting, or starting up after being shutdown, the services mentioned are setup to run upon restart/boot up so the webapp should function normally once the IBM machine is back online.

API:
	The API endpoint docs will be elaborated upon and fleshed out as the project matures and the basic endpoints are finalized.

/api/upload
	POST method. Receives a single image from the frontend.
	Returns a response containing the initial filename and the new corrected file’s name.
/api/uploadMultiple
	POST method. Receives multiple images in the response from the frontend.
	Returns a simple text response, this endpoint is under active development.
/api/getImage?image=<image name>
	GET method. Requests for a single image as a query parameter.
	Returns the binary (base64 encoded) content of the requested image, if it is found in the file system.
	Example request for an image “corrected_football.jpg”
	/api/getImage?image=corrected_football.jpg
/api/time
	GET method. 
	Returns the current Unix time.
	This endpoint primarily serves as a heart-beat for the backend that is visible on the frontend. When the text on the webpage displays “0” instead of the Unix time, it is an immediate clue that the API is not fulfilling requests.
/api/downloadImage?image=<image name>
	GET method. Requests for a single image as a query parameter
	Returns a downloadable version of the requested file, which will download automatically from the browser.

Uploaded/Processed Images:
	All files which are uploaded and corrected will end up in one of two directories, “/root/file-upload/public/uploaded_images” and “/root/file-upload/public/corrected_images”. The backend is what interacts with this file system, they are simply stored on disk on the IBM server. It should be a relatively simple process to switch to an actual database or change where the images are placed as these locations are simply constants set in the api.py file.
Having the files specifically in the /public directory should make them be able to be accessed directly by the frontend, but the use case ended up needing an API endpoint to fetch the files and send them to the frontend.

The bash script “/root/file-upload/clearImages.sh” is a simple script which permanently removes all files from the /uploaded_images and /corrected_images directories. Modifying this script should be simple if the upload location changes for instance, but please proceed with caution as the “rm *” command can be very dangerous if not handled carefully. It is encouraged to back up the entire codebase when testing new scripts of that nature.
