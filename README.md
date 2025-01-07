# WebbThesis
Code and Data Repository for thesis: \
Comparative Performance Analysis of Cryptographic Workloads Across Cloud Providers: \
A Multi-Language Study on FaaS and IaaS Platforms by Jeremiah Webb @ Embry-Riddle Aeronautical University 

# Chosen benchmark configurations
## Languages Tested
- Python3.11
- Rust 1.83.0
- Go 1.23.0
- tsc 5.7.2 (Node 23.4.0)
- Dotnet v8


## Cryptographic Workloads: 
- SHA256 Hash Generation
- SHA384 Hash generation
- AES256 Encrypt
- AES256 Decrypt
- ECC (256, 384) Sign
- ECc (256, 384) Verify
- RSA (2048, 3072, 4096) Encrypt
- RSA (2048, 3072, 4096) Decrypt

## Function-as-a-Service (FaaS) configurations

(In MB)

AWS Lambda: 128, 512, 1024, 1769, 3008 \

(Currently set quota, see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)

Azure Functions: Not available, dynamic

All in x86 and Arm64 bit

## Infrastruction-as-a-Service (IaaS) configurations
All OS - Ubuntu 22.04 LTS
(All Burstable machines)

## x86
### AWS EC2:
- t2.medium (2 vcpu, 4Gb mem)
- t2.xlarge (4 vcpu, 16Gb mem)
- t2.2xlarge (8 vcpu, 32Gb mem)

### Azure Virtual Machines:
- B2s (2 vcpu, 4Gb mem)
- B4ms (4 vcpu, 16Gb mem)
- B8ms (8 vcpu, 32Gb mem)

## Arm 64 bit
### AWS EC2:
- t4g.medium (2 vcpu, 4Gb mem)
- t4g.xlarge (4 vcpu, 16Gb mem)
- t4g.2xlarge (8 vcpu, 32Gb mem)

### Azure Virtual Machines:
- B2pls_v2 (2 vcpu, 4Gb mem)
- B4ps_v2 (4 vcpu, 16Gb mem)
- B8ps_v2 (8 vcpu, 32Gb mem)


