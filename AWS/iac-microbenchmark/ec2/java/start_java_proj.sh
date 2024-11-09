#!/bin/bash

# Array of project directory names
projects=(
    "rsa2048_decrypt"
    "rsa2048_encrypt"
    "rsa3072_decrypt"
    "rsa3072_encrypt"
    "rsa4096_decrypt"
    "rsa4096_encrypt"
    "sha256"
    "sha384"
    "aes256_decrypt"
    "aes256_encrypt"
    "ecc256_sign"
    "ecc256_verify"
    "ecc384_sign"
    "ecc384_verify"
)

dependencies='
        <!-- AWS SDK for Java (KMS) -->
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>kms</artifactId>
            <version>2.28.16</version>
        </dependency>

        <!-- Jackson for JSON serialization/deserialization -->
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>2.18.0</version>
        </dependency>
'

maven_shade_plugin='
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-shade-plugin</artifactId>
            <version>3.2.2</version>
            <configuration>
                <createDependencyReducedPom>false</createDependencyReducedPom>
            </configuration>
            <executions>
                <execution>
                    <phase>package</phase>
                    <goals>
                        <goal>shade</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
'

# Loop through each project and create Maven project structure
for project in "${projects[@]}"; do
    echo "Creating project: $project"
    
    # Create Maven project using the archetype:generate command
    mvn archetype:generate -DgroupId=com.webb -DartifactId="$project" -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false

    # Navigate to the project directory
    cd "$project" || exit

    # Remove App.java file
    rm -f src/main/java/com/webb/App.java
    echo "Removed App.java from $project"

    # Add the necessary dependencies to the pom.xml
    echo "Adding AWS Lambda, KMS, and Jackson dependencies to $project/pom.xml"

    # Create a temporary file to hold the modified pom.xml
    temp_file=$(mktemp)

    # Append the existing content of pom.xml to the temp file
    cat pom.xml > "$temp_file"

    # Use awk to add the lambda dependencies just before the closing </dependencies> tag
    awk -v deps="$dependencies" '/<\/dependencies>/ { print deps } 1' "$temp_file" > pom.xml

    # Add the build section (after </dependencies> and before the end of </project>)
    awk -v build="$maven_shade_plugin" '/<\/dependencies>/ { print $0 "\n" build; next }1' pom.xml > "$temp_file" && mv "$temp_file" pom.xml

    # Modify the Java version in pom.xml (escape < and > with \)
    sed -i '/<\/properties>/i \
        <maven.compiler.source>21<\/maven.compiler.source>\n\
        <maven.compiler.target>21<\/maven.compiler.target>' pom.xml

    # Extract project name in camel case format
    project_name=$(echo "$project" | sed -E 's/lambda-project-//; s/(^|_)([a-z])/\U\2/g; s/_//g')

    # Create the src/main/java/com/webb/LambdaHandler.java with skeleton code
    mkdir -p src/main/java/com/webb

    cat <<EOL > src/main/java/com/webb/${project_name}Program.java
package com.webb;

import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.util.HashMap;
import java.nio.charset.StandardCharsets;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.regions.Region;

EOL

    # Add AES and RSA imports if the project is related to AES or RSA
    if [[ "$project" == *"aes256"* || "$project" == *"rsa"* ]]; then
        cat <<EOL >> src/main/java/com/webb/${project_name}Program.java
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;
EOL
    fi
    # Continue with the rest of the LambdaHandler class
    cat <<EOL >> src/main/java/com/webb/${project_name}Program.java
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.*;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class ${project_name}Program {
    private static final String KMS_KEY_ARN = System.getenv("KMS_KEY_ARN");
    private KmsClient kmsClient;
    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        // Read from stdin
        InputStream input = System.in;
        ${project_name}RequestMessage request = mapper.readValue(input, ${project_name}RequestMessage.class);

        // Create KMS Client
        try (KmsClient kmsClient = KmsClient.create()) {
            // Encrypt the message using AWS KMS
            EncryptRequest encryptRequest = EncryptRequest.builder()
                    .keyId(KMS_KEY_ARN)
                    .plaintext(java.nio.ByteBuffer.wrap(request.getMessage().getBytes(StandardCharsets.UTF_8)))
                    .build();
            EncryptResponse encryptResponse = kmsClient.encrypt(encryptRequest);

            // Prepare response message
            String encryptedMessage = java.util.Base64.getEncoder().encodeToString(encryptResponse.ciphertextBlob().asByteArray());
            ${project_name}ResponseMessage response = new ${project_name}ResponseMessage(encryptedMessage, request.getSender(), "Success");

            // Write to stdout
            OutputStream output = System.out;
            mapper.writeValue(output, response);
        } catch (KmsException e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
EOL
    # Copy the Request and Response Messages
    #cp ../../../lambdas/java/${project}/src/main/java/webb/${project_name}ResponseMessage.java src/main/java/com/webb/${project_name}ResponseMessage.java

    cp ../../../lambdas/java/${project}/src/main/java/com/webb/${project_name}RequestMessage.java src/main/java/com/webb/${project_name}RequestMessage.java

    cp ../../../lambdas/java/${project}/src/main/java/com/webb/${project_name}ResponseMessage.java src/main/java/com/webb/${project_name}ResponseMessage.java


    # Navigate back to the parent directory before processing the next project
    #
    cd ..
done

echo "All projects created successfully!"
