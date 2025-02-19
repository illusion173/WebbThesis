#!/bin/bash



PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")
LANGAUGES=("java")
#LANGAUGES=("dotnet" "python" "java" "typescript")
RESOURCEGROUP="benchmarkWebbRG"

for LANGUAGE in "${LANGAUGES[@]}"; do


  # We will first cd to the parent language dir.
  if [[ "$LANGUAGE" == "dotnet" ]]; then
      cd af/c#
  else
      cd af/${LANGUAGE}
  fi


  for PROJECT in "${PROJECTS[@]}"; do
    cleaned_proj_op="${PROJECT//_/}"

    echo "Attempting to publish ${LANGUAGE} - ${PROJECT}."
    if [[ "$LANGUAGE" == "java" ]]; then
        cd java_${PROJECT}
        mvn clean package -DskipTests
        mvn azure-functions:deploy
        cd ..
        continue
    fi

    # Special cases for dotnet
    if [[ "$LANGUAGE" == "dotnet" ]]; then
        cd dotnet_${PROJECT}
        
        dotnet publish -c Release -r linux-x64 -p:PublishReadyToRun=true
        func azure functionapp publish ${LANGUAGE}${cleaned_proj_op}benchmarkappwebbeecserau 

        cd ..
        continue
    fi

    cd ${PROJECT}
    ls
    func azure functionapp publish ${LANGUAGE}${cleaned_proj_op}benchmarkappwebbeecserau  --${LANGUAGE}

    cd ..

    echo "Deployed ${LANGUAGE} - ${PROJECT}."
  done

  echo "Done Deploying all of ${LANGUAGE} Deployment."
  cd ../..
done

echo "Done deploying all azure functions."

