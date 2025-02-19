#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

for PROJECT in "${PROJECTS[@]}"; do

    echo "Setting up project: $PROJECT"

    mvn archetype:generate -DarchetypeGroupId=com.microsoft.azure -DarchetypeArtifactId=azure-functions-archetype -DjavaVersion=21 -DgroupId=com.webb -DartifactId=java_${PROJECT} -Dversion=1.0-SNAPSHOT -DappName=java_${PROJECT} -DappRegion=eastus -DresourceGroup=benchmarkRG -Dtrigger=HttpTrigger -DinteractiveMode=false
    # go into new project
    cd java_"$PROJECT" || exit
    rm host.json
    rm pom.xml

    cat <<EOF > host.json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
EOF

# put first part of pom.xml config
cat <<EOF > pom.xml
<?xml version="1.0" encoding="UTF-8" ?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.webb</groupId>
    <artifactId>java_$PROJECT</artifactId>
    <version>1.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <name>Azure Java Functions</name>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <java.version>21</java.version>
        <azure.functions.maven.plugin.version>1.24.0</azure.functions.maven.plugin.version>
        <azure.functions.java.library.version>2.2.0</azure.functions.java.library.version>
        <functionAppName>java_$PROJECT</functionAppName>
    </properties>
EOF

second_pom_xml_part='
    <dependencies>
        <dependency>
            <groupId>com.microsoft.azure.functions</groupId>
            <artifactId>azure-functions-java-library</artifactId>
            <version>${azure.functions.java.library.version}</version>
        </dependency>
        <!-- Test -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.4.2</version>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>2.23.4</version>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-security-keyvault-keys</artifactId>
            <version>4.9.2</version>
        </dependency>

        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-identity</artifactId>
            <version>1.15.1</version>
        </dependency>

        <!-- Jackson for JSON serialization/deserialization -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.18.0</version>
        </dependency>
        <!-- https://mvnrepository.com/artifact/org.slf4j/slf4j-simple -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-nop</artifactId>
            <version>2.0.12</version>
        </dependency>

        <dependency>
            <groupId>com.azure.tools</groupId>
            <artifactId>azure-sdk-build-tool</artifactId>
            <version>1.0.0</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>${java.version}</source>
                    <target>${java.version}</target>
                    <encoding>${project.build.sourceEncoding}</encoding>
                </configuration>
            </plugin>
            <plugin>
                <groupId>com.microsoft.azure</groupId>
                <artifactId>azure-functions-maven-plugin</artifactId>
                <version>${azure.functions.maven.plugin.version}</version>
                <configuration>
                    <!-- function app name -->
                    <appName>${functionAppName}</appName>
                    <!-- function app resource group -->
                    <resourceGroup>benchmarkRG</resourceGroup>
                    <!-- function app service plan name -->
                    <appServicePlanName>java-functions-app-service-plan</appServicePlanName>
                    <!-- function app region-->
                    <!-- refers https://github.com/microsoft/azure-maven-plugins/wiki/Azure-Functions:-Configuration-Details#supported-regions for all valid values -->
                    <region>eastus</region>
                    <!-- function pricingTier, default to be consumption if not specified -->
                    <!-- refers https://github.com/microsoft/azure-maven-plugins/wiki/Azure-Functions:-Configuration-Details#supported-pricing-tiers for all valid values -->
                    <!-- <pricingTier></pricingTier> -->
                    <!-- Whether to disable application insights, default is false -->
                    <!-- refers https://github.com/microsoft/azure-maven-plugins/wiki/Azure-Functions:-Configuration-Details for all valid configurations for application insights-->
                    <!-- <disableAppInsights></disableAppInsights> -->
                    <runtime>
                        <!-- runtime os, could be windows, linux or docker-->
                        <os>linux</os>
                        <javaVersion>21</javaVersion>
                    </runtime>
                    <appSettings>
                        <property>
                            <name>FUNCTIONS_EXTENSION_VERSION</name>
                            <value>~4</value>
                        </property>
                    </appSettings>
                </configuration>
                <executions>
                    <execution>
                        <id>package-functions</id>
                        <goals>
                            <goal>package</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <!--Remove obj folder generated by .NET SDK in maven clean-->
            <plugin>
                <artifactId>maven-clean-plugin</artifactId>
                <version>3.1.0</version>
                <configuration>
                    <filesets>
                        <fileset>
                            <directory>obj</directory>
                        </fileset>
                    </filesets>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'

    echo "$second_pom_xml_part" >> pom.xml

    # Finished pom and host set up
    # Begin Main code setup
    #
    #
    cd src/main/java/com/webb/

    rm Function.java
cat <<EOF > Function.java
package com.webb;

import com.microsoft.azure.functions.ExecutionContext;
import com.microsoft.azure.functions.HttpMethod;
import com.microsoft.azure.functions.HttpRequestMessage;
import com.microsoft.azure.functions.HttpResponseMessage;
import com.microsoft.azure.functions.HttpStatus;
import com.microsoft.azure.functions.annotation.AuthorizationLevel;
import com.microsoft.azure.functions.annotation.FunctionName;
import com.microsoft.azure.functions.annotation.HttpTrigger;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.security.SecureRandom;
import java.io.OutputStream;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.EncryptResult;
import com.azure.security.keyvault.keys.cryptography.models.EncryptionAlgorithm;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import java.util.Optional;

/**
 * Azure Functions with HTTP Trigger.
 */
public class Function {

    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String _KEY_NAME = System.getenv("_KEY_NAME");
    private static final ObjectMapper objectMapper = new ObjectMapper();

    
    @FunctionName("java_${PROJECT}")
    public HttpResponseMessage run(
            @HttpTrigger(
                name = "req",
                methods = {HttpMethod.POST},
                authLevel = AuthorizationLevel.ANONYMOUS)
                HttpRequestMessage<Optional<String>> request,
            final ExecutionContext context) {
                try  {
                    String requestBody = request.getBody().orElse(null);

                    if (requestBody == null) {
                        return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Please pass a request body").build();
                    }


                    ${PROJECT}RequestMessage ${PROJECT}request = objectMapper.readValue(requestBody, ${PROJECT}RequestMessage.class);


                    
                    DefaultAzureCredential creds = new DefaultAzureCredentialBuilder().build();

                    
                    KeyClient keyClient = new KeyClientBuilder().credential(creds).vaultUrl(KEY_VAULT_URL).buildClient();
                    
                    KeyVaultKey key = keyClient.getKey(_KEY_NAME);
                    CryptographyClient cryptoClient = new CryptographyClientBuilder()
        	                .keyIdentifier(key.getId())
        	                .credential(creds)
        	                .buildClient();


                    // Process the request and create response object
                    ${PROJECT}ResponseMessage responseObj = new ${PROJECT}ResponseMessage();

                    // Convert response object to JSON string
                    String jsonResponse = objectMapper.writeValueAsString(responseObj);

                    return request.createResponseBuilder(HttpStatus.OK).body(jsonResponse).build();
                } catch (Exception e) {
                    return request.createResponseBuilder(HttpStatus.BAD_REQUEST).body("Error: " + e.getMessage()).build();
                }
    }

    private static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                    + Character.digit(s.charAt(i + 1), 16));
        }
        return data;
    }

}
EOF




    cat <<EOL >> ${PROJECT}RequestMessage.java
package com.webb;

public class ${PROJECT}RequestMessage {


    // Default constructor (required for Jackson)
    public ${PROJECT}RequestMessage() {}


    // Getters and setters

}
EOL


    cat <<EOL >> ${PROJECT}ResponseMessage.java
package com.webb;

public class ${PROJECT}ResponseMessage {

    // Default constructor (required for Jackson)
    public ${PROJECT}ResponseMessage() {}


    // Getters and setters
}
EOL

    cd ../../../../../
    mvn install

    echo "Finished ${PROJECT}"
    cd ..

done

echo "Finished Preparing Java projects."
