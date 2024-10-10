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

# AWS Lambda dependencies including Jackson for JSON parsing
lambda_dependencies='

    <!-- https://mvnrepository.com/artifact/software.amazon.awssdk/lambda -->
    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>lambda</artifactId>
        <version>2.28.16</version>
    </dependency>

    <!-- https://mvnrepository.com/artifact/com.amazonaws/aws-lambda-java-core -->
    <dependency>
        <groupId>com.amazonaws</groupId>
        <artifactId>aws-lambda-java-core</artifactId>
        <version>1.2.3</version>
    </dependency>

    <!-- https://mvnrepository.com/artifact/com.amazonaws/aws-lambda-java-events -->
    <dependency>
        <groupId>com.amazonaws</groupId>
        <artifactId>aws-lambda-java-events</artifactId>
        <version>3.14.0</version>
    </dependency>

    <dependency>
        <groupId>software.amazon.awssdk</groupId>
        <artifactId>kms</artifactId>
        <version>2.28.16</version>
    </dependency>

    <!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-databind -->
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.18.0</version>
    </dependency>
'

# Maven shade plugin build section
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
    awk -v deps="$lambda_dependencies" '/<\/dependencies>/ { print deps } 1' "$temp_file" > pom.xml

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
    cat <<EOL > src/main/java/com/webb/LambdaHandler.java
package com.webb;

import java.util.Map;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyRequestEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayProxyResponseEvent;
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
        cat <<EOL >> src/main/java/com/webb/LambdaHandler.java
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
    cat <<EOL >> src/main/java/com/webb/LambdaHandler.java
public class LambdaHandler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    // Create an instance of ObjectMapper for JSON parsing and serialization
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private KmsClient kmsClient;

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent request, Context context) {
        context.getLogger().log("Received event: " + request);

          // Create a response object
          APIGatewayProxyResponseEvent response = new APIGatewayProxyResponseEvent();
          HashMap<String,String> rspHeaders = new HashMap<>();
          rspHeaders.put("Access-Control-Allow-Origin", "*");
          rspHeaders.put("Content-Type", "application/json");
          response.setHeaders(rspHeaders);

        try {
        	
            // Get KMS key ARN from environment variables
            String ${project_name}KmsKeyId = System.getenv("_KMS_KEY_ARN");
        	
            // Get the JSON string from the request body
            String body = request.getBody();
                    
            // Deserialize the request body into Sha256RequestMessage object

            //
          ${project_name}RequestMessage requestMessage = objectMapper.readValue(body, ${project_name}RequestMessage.class);


            String message = requestMessage.getMessage();
            
            // convert message to bytes
            SdkBytes messageBytes = SdkBytes.fromByteArray(message.getBytes(StandardCharsets.UTF_8));
                // Create a ResponseMessage object
                ${project_name}ResponseMessage responseMessage = new ${project_name}ResponseMessage(
                		"responseMessage"
                );
                String responseBody = objectMapper.writeValueAsString(responseMessage);

                // Set success response
                response.setStatusCode(200);
                response.setBody(responseBody);
                
                
                return response;


            } catch (Exception e) {
        	
        	
            // Handle any errors
            context.getLogger().log("Error parsing request: " + e.getMessage());
            
        	HashMap<String,String> rspErrorBody = new HashMap<>();
        	rspErrorBody.put("Error", "Error while parsing request body: " + e.getMessage());

            // Set error response
            response.setStatusCode(500);
            response.setBody(rspErrorBody.toString());
            return response;
        }
    }
}
EOL

    # Create the src/main/java/com/webb/${project_name}RequestMessage.java with request message structure
    cat <<EOL > src/main/java/com/webb/${project_name}RequestMessage.java
package com.webb;

public class ${project_name}RequestMessage {
    private String message;
    private String sender;

    // Default constructor (required for Jackson)
    public ${project_name}RequestMessage() {}

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }
}
EOL

    # Create the src/main/java/com/webb/${project_name}ResponseMessage.java with response message structure
    cat <<EOL > src/main/java/com/webb/${project_name}ResponseMessage.java
package com.webb;

public class ${project_name}ResponseMessage {
    private String message;
    private String sender;
    private String status;

    // Default constructor (required for Jackson)
    public ${project_name}ResponseMessage() {}

    public ${project_name}ResponseMessage(String message, String sender, String status) {
        this.message = message;
        this.sender = sender;
        this.status = status;
    }

    // Getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSender() {
        return sender;
    }

    public void setSender(String sender) {
        this.sender = sender;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
EOL

    # Navigate back to the parent directory before processing the next project
    cd ..
done

echo "All projects created successfully!"
