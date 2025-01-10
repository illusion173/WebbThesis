#!/bin/bash

#ARCH_DIR="x86"
ARCH_DIR="arm"


for ts_file in *.ts; do
  dir_name="${ts_file%.ts}"

  # Create string for project dir loc name
  PROJDIR="${ARCH_DIR}/${dir_name}"

  # Create the physical project dir
  mkdir -p "$PROJDIR"

  # move ts file to root of projectdir
  cp "$ts_file" "$PROJDIR/"


  cd "$PROJDIR/"

  # Create NPM back for building 
  touch package.json

cat > package.json <<EOF
{
  "name": "BL-${dir_name}",
  "version": "1.0.0",
  "description": "typescript lambda function - operation ${dir_name}",
  "type": "commonjs",
  "main": "${dir_name}.js",
  "scripts": {
    "prebuild": "rm -rf dist",
    "build": "esbuild ${dir_name}.ts --bundle --minify --sourcemap --platform=node --target=es2020 --outfile=dist/${dir_name}.js",
    "postbuild": "cd dist && zip -r ${dir_name}.zip ${dir_name}.js*",
    "test": "TEST"
  },
  "devDependencies": {
    "@types/aws-lambda": "^8.10.147",
    "esbuild": "^0.24.2",
    "@aws-sdk/client-kms": "^3.140.0",
    "base64-js": "^1.5.1",
    "aws-sdk": "^2.1362.0",
    "typescript": "^5.0.0"
  },
  "author": "JeremiahWebb",
  "license": "MIT"
}
EOF
  npm install -D @types/aws-lambda esbuild
  npm run build

  mv dist/${dir_name}.zip .

  cd ../..
done

