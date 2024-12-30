# WebbThesis
Code and Data Repository for thesis: \
Comparative Performance Analysis of Cryptographic Workloads Across Cloud Providers: \
A Multi-Language Study on FaaS and IaaS Platforms by Jeremiah Webb @ Embry-Riddle Aeronautical University 

# Chosen benchmark configurations
(In MB)
AWS Lambda: 128, 512, 1024, 1769, 3008 \
(Currently set quota, seehttps://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)
Azure Functions: Not available, dynamic

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


