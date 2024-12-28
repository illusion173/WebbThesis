#!/bin/bash

ARCH_DIR="x86"
#ARCH_DIR="arm"


for ts_file in *.ts; do
  dir_name="${ts_file%.ts}"

  # Create string for project dir loc name
  PROJDIR="${ARCH_DIR}/${dir_name}"

  # Create the physical project dir
  mkdir -p "$PROJDIR"

  # create src folder for .ts to live in
  SRCDIR="${PROJDIR}/src"

  mkdir -p "$SRCDIR"

  cp "$ts_file" "$SRCDIR/"

  cd "$PROJDIR/"

  touch package.json  
  touch tsconfig.json

  cat > package.json <<EOF
{
  "name": "BL-${dir_name}",
  "version": "1.0.0",
  "description": "typescript lambda function - operation ${dir_name}",
  "main": "dist/index.js",
  "scripts": {
    "clean": "rm -rf dist",
    "build": "npm run clean && tsc",
    "package": "zip -r ${dir_name}.zip dist/*",
    "deploy": "npm run clean && npm run build && npm run package"
  },
  "dependencies": {
  "@aws-sdk/client-kms": "^3.140.0", 
  "base64-js": "^1.5.1",
  "aws-sdk": "^2.1362.0" 
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/aws-lambda": "^8.10.110"
  },
  "author": "JeremiahWebb",
  "license": "MIT"
}
EOF


  cat > tsconfig.json <<EOF
{
  "compilerOptions": {
    "target": "ES6",
    "module": "CommonJS",
    "outDir": "./dist",  
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "noImplicitAny": false
  },
  "include": [
    "src/**/*.ts"
  ],
  "exclude": [
    "node_modules",
    "dist"
  ]
}
EOF

  npm run deploy
  cd ../..

done
