#!/bin/sh
#this appears to be how it's done, little weird
bld='npm run build'
$bld

echo BUILD COMPLETED

reloadNGX='sudo systemctl reload nginx'
$reloadNGX
echo RELOADING NGINX COMPLETED

reloadFLSK='sudo systemctl restart flask-react-app.service'
$reloadFLSK
echo RESTARTING FLASK API COMPLETED
