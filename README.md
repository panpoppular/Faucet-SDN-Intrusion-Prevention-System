# Faucet SDN Intrusion Prevention System

## Requirement (Controller)
1. Joblib, Tensorflow, scikit-learn
2. argus-server, argus-cilent

## Installation on controller
1. Install required python packages `pip3 install joblib tensorflow`
2. Install argus `sudo apt install argus-server`
3. Install [faucet](https://docs.faucet.nz/en/latest/tutorials/first_time.html)
4. Clone this repo
5. Replace `/etc/faucet/faucet.yaml` with yaml file provided in Faucet_config directory 
6. Make sure you edited autoacl.yaml include path on faucet.yaml to absolute path of your working directory)
7. Run `sudo argus -i <monitoring interface> -m -Z -P 561 on terminal
8. On Seperate terminal, run Real_IDS_8F.py on src directory to start IDS.

# Simulate on GNS3
Installing GNS3 is complex task to do (depended on OS) please consult the [Installation guide](https://docs.gns3.com/)
