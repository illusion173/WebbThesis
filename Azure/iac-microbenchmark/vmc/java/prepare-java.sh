#!/bin/bash

# Define project names
PROJECTS=("ecc256_verify" "ecc384_verify" "rsa2048_decrypt" "rsa3072_decrypt" "rsa4096_decrypt" "ecc256_sign" "ecc384_sign" "rsa2048_encrypt" "rsa3072_encrypt" "rsa4096_encrypt")

dependencies='
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
            <artifactId>slf4j-simple</artifactId>
            <version>2.0.12</version>
        </dependency>
'

# Create projects and install dependencies
for PROJECT in "${PROJECTS[@]}"; do
    echo "Setting up project: $PROJECT"

    # camel case
    project_name=$(echo "$PROJECT" | sed -E 's/(^|_)([a-z])/\U\2/g; s/_//g')

    # Maven Shade plugin configuration
    maven_shade_plugin="
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
                    <configuration>
                    <transformers>
                        <transformer implementation=\"org.apache.maven.plugins.shade.resource.ManifestResourceTransformer\">
                            <mainClass>com.webb.${project_name}Program</mainClass>
                        </transformer>
                    </transformers>
                </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
    "

    mvn_java_version="
    <properties>
        <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
    </properties>
    "

    mvn archetype:generate -DgroupId=com.webb -DartifactId="$PROJECT" -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false

    # Navigate to the project directory
    cd "$PROJECT" || exit

    # Remove App.java file
    rm -f src/main/java/com/webb/App.java
    echo "Removed App.java from $PROJECT"

    echo "INSERT DEPENDENCIES"

    # Create a temporary file to hold the modified pom.xml
    temp_file=$(mktemp)

    # Append the existing content of pom.xml to the temp file
    cat pom.xml > "$temp_file"

    # Use awk to add the lambda dependencies just before the closing </dependencies> tag
    awk -v deps="$dependencies" '/<\/dependencies>/ { print deps } 1' "$temp_file" > pom.xml

    # Add the build section (after </dependencies> and before the end of </project>)
    awk -v build="$maven_shade_plugin" '/<\/dependencies>/ { print $0 "\n" build; next }1' pom.xml > "$temp_file" && mv "$temp_file" pom.xml


    awk -v build="$mvn_java_version" '/<\/url>/ { print $0 "\n" build; next }1' pom.xml > "$temp_file" && mv "$temp_file" pom.xml

    # Create the src/main/java/com/webb/ directory
    mkdir -p src/main/java/com/webb

    # Generate the Java program file
    cat <<EOL > src/main/java/com/webb/${project_name}Program.java
package com.webb;

import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Base64;
import java.nio.charset.StandardCharsets;
import java.io.InputStream;
import java.io.OutputStream;
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.cryptography.*;
import com.azure.security.keyvault.keys.models.KeyVaultKey;
import com.azure.security.keyvault.keys.cryptography.models.SignResult;
import com.azure.security.keyvault.keys.cryptography.models.SignatureAlgorithm;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class ${project_name}Program {
    private static final String KEY_VAULT_URL = System.getenv("AZURE_KEY_VAULT_URL");
    private static final String KEY_NAME = System.getenv("KEY_NAME");

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper();

        try  {

            if (args.length != 1) {
                System.err.println("Usage: java ${project_name} <message>");
                System.exit(1);
            }

        String requestJsonString = args[0];  // Get the message from the command line argument

        ${project_name}RequestMessage request = mapper.readValue(requestJsonString, ${project_name}RequestMessage.class);

            
        ${project_name}ResponseMessage response = new ${project_name}ResponseMessage(encryptedMessage, request.getSender(), "Success");
        // Write to stdout
        OutputStream output = System.out;
        mapper.writeValue(output, response);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}


EOL

    cat <<EOL >> src/main/java/com/webb/${project_name}RequestMessage.java
package com.webb;

public class ${project_name}RequestMessage {


    // Default constructor (required for Jackson)
    public ${project_name}RequestMessage() {}

    public ${project_name}RequestMessage() {}

    // Getters and setters

}
EOL


    cat <<EOL >> src/main/java/com/webb/${project_name}ResponseMessage.java
package com.webb;

public class ${project_name}ResponseMessage {
    private boolean verified;

    // Default constructor (required for Jackson)
    public ${project_name}ResponseMessage() {}

    public ${project_name}ResponseMessage() {}

    // Getters and setters

}
EOL

    cd ..
done

echo "Setup completed!"
