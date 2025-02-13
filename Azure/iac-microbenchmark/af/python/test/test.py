import json
import base64
import sys
import os
from azure.identity import DefaultAzureCredential 
import azure.functions as func 
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
@app.route(route="httptriggerbench")
def httptriggerbench(req: func.HttpRequest) -> func.HttpResponse:

    body = req.get_json()

    if not body:
        return func.HttpResponse(f"ERROR: HTTP request for PROJECTHERE is missing body.", status_code=400)



    # main code here
    try:
        print("")


    except Exception as e:
        return func.HttpResponse(f"ERROR: HTTP request for an error for operation PROJECTHERE {e} .", status_code=500)




    return func.HttpResponse(f"Hello. This HTTP triggered function executed successfully.")

