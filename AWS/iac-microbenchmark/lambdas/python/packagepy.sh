#!/bin/bash

ARCH_DIR="x86"
#ARCH_DIR="arm"
# The location of the requirements for dependencies.
#REQTXTLOC="specific_requirements_for_lambda.txt"
REQTXTLOC="../../specific_requirements_for_lambda.txt"
#REQTXTLOC="../../../../../../requirements.txt"
# Loop through all .py files in the current directory
for py_file in *.py; do

  # Get the filename without the extension
  dir_name="${py_file%.py}"

  
  echo $dir_name

  # Create string for project dir
  PROJDIR="${ARCH_DIR}/${dir_name}"

  # Create the physical projcet dir
  mkdir -p "$PROJDIR"

  # Create a directory with the same name as the .py file (without the extension)
  # Optionally, move the .py file into the created directory
  cp "$py_file" "$PROJDIR/"

  # Move to the projdir
  cd "$PROJDIR/"

  # create the lib dir
  mkdir -p package

  # download and install the required libraries.
  pip install -r $REQTXTLOC --target=./package

  # move to the root of where the packages live
  #
  cd package
  # zip everything inside of it.
  zip -9 -r ../$dir_name.zip .
  cd ..

  # zip the py into it
  zip -9 $dir_name.zip $dir_name.py
  # remove the py inside the folder so the zip is the only thing in it.
  rm $dir_name.py

  rm -rf package

  # go back to the root dir where the script lives.
  cd ../..

done
