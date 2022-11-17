#!/bin/sh
#this appears to be how it's done, little weird
clearCor='rm /root/file-upload/public/corrected_images/*'
$clearCor
clearUnc='rm /root/file-upload/public/uploaded_images/*'
$clearUnc

echo IMAGES CLEARED