# Faucet SDN Intrusion Prevention System

## How does this work.
![img](https://raw.githubusercontent.com/panpoppular/Faucet-SDN-Intrusion-Prevention-System/master/Picture/Howitworks4.png)
The programs will read flow input from argus (make sure you have launch argus first!) every input will be queued and processed for
generating additional features, and send to prediction with model /src/keras_model , after got prediction results, if it's attack, the program will count for Consecutive attack, after 10 consecutive attacks from same ip (can be adjust by change FP_ELM_TH) the program will call yml.py for editing autoacl.yaml, which is faucet configuration files, and reload faucet service for apply new config.

** after program quitted (by user) the program will reset configuration file by calling resetyml.py and reload faucet service.

## Requirement (Controller)
1. Joblib, Tensorflow, scikit-learn
2. argus-server, argus-cilent

## Installation on controller (On VM)
1. Install required python packages `pip3 install joblib tensorflow`
2. Install argus `sudo apt install argus-server`
3. Install [faucet](https://docs.faucet.nz/en/latest/tutorials/first_time.html)
4. Clone this repo
5. Replace `/etc/faucet/faucet.yaml` with yaml file provided in Faucet_config directory 
6. Make sure you edited autoacl.yaml include path on faucet.yaml to absolute path of your working directory)
7. Disable password prompt for sudo command 

## Runing IDS

1. Run `sudo argus -i ens5 -m -Z -P 561` on terminal
2. On Seperate terminal, change directory to src and run `python3 Real_IDS_8F`  to start IDS.

## Attack testing

On attacker node, double click to open console, install nmap and hping3.
```
$ apt update
$ apt install hping3
$ apt install nmap (nmap is already installed)
```

The hping3 is DoS tools and Nmap is port scanning tools, you can test by these command.
```
$ nmap -p- <Target IP>
$ hping3 -S hping3 <Target IP> -s --flood -c 200000 
```

# Simulate on GNS3
Installing GNS3 is complex task to do (depended on OS) please consult the [Installation guide](https://docs.gns3.com/)

## Import portable project

1. Goto File > import portable project
2. Select portable project file (with .gns3project extension)
3. Wait until import complete, then right click on SDN_Controller node and select properties
![qemu1](https://raw.githubusercontent.com/panpoppular/Faucet-SDN-Intrusion-Prevention-System/master/Picture/QemuSel3.png)
4. Select HDD Tab, change hda image to provided qcow2 images (on 7z files)
![qemu2](https://raw.githubusercontent.com/panpoppular/Faucet-SDN-Intrusion-Prevention-System/master/Picture/Qemu-HDA.PNG)
5. The QEMU image Should work on Windows (with intel haxm accelerator)

## Simulating

1. Start all nodes
2. On controller, launch console and wait for deian loading
3. Login with this username/password
```
Username:test
Password:testtest
```
4. Launch argus on terminal ` sudo argus -i ens5 -m -Z -P 561 - ip and not icmp and not multicast`
5. cd to `sdnids/src`
6. launch our IDS `sudo python3 Real_IDS_8F.py` (Must be run with sudo)
7. The program will output stuff about tensorflow and numpy, you can ignore that.
8. launch attack by double click on attacker node (it will show console) then attack by provided command.
8. When program detect attack flows, it will show ip on screen and invoking yml.py
![attack](https://raw.githubusercontent.com/panpoppular/Faucet-SDN-Intrusion-Prevention-System/master/Picture/Capture.PNG)
9. After exit program (by ctrl+c) the acl files will be reseted (by invoking resetyml.py) and it will show statistics about predicte flows
(if provided correct attacking ip, this would be comfusion matrix)





## Import Project (Outdated)

## [Add component templates](https://docs.gns3.com/1_3RdgLWgfk4ylRr99htYZrGMoFlJcmKAAaUAc8x9Ph8/index.html)
1. Goto File > New template
2. Select Install an appliance from the GNS3 server then next.
3. We need Open vSwitch management Docker image, find on search bar, select and press install.
4. Press next to add components.
5. Repeat with webterm and ubuntu docker images.

## [Add VM templates](https://docs.gns3.com/1u_D9XSSA5PVFrOrTWSw1Vn8Utvimd6ksv76F7731N84/index.html)
1. Make sure you have VMWare/Virutalbox/QEMU images that installed requried software for controller.
2. Go to edit > Preferences
3. Follow instruction.
4. After finished configuration, start VM node and config IP fore each interfaces
```
1.e0 = Static IP (Same network as Controller IP) (This interface is for openflow controller)
2.e1 = link-local only (Mirrored interface)
3.e2 = dhcp (Internet interface) (Connect to nat node)
```
## Creating topology
(pic)

## Config node
1. On OpenvSwitchmanagement node, right click and click Configure.
2. On general settings tab, click Network configuration.
3. Normally, OpenvSwitchmanagement will use eth0 for management interface, config static ip by remove # and set ip
(pic)
4. On other docker nodes (webterms, ubuntu) you may config by use dhcp or static ip.
5. Start OpenvSwitchmanagement node and double click to access console
6. Normally, eth1-15 is under br0, you need to tell br0 to recognize controller by issuling this command.
```
$ ovs-vsctl set-controller br0 tcp:(Controller IP):6653
$ ovs-vsctl set controller br0 connection-mode=out-of-band
```


