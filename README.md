# Arista Lab Tools

Python scripts to manage/generate EOS configuration for labs.
Based on [Nornir](https://nornir.tech/) and [NAPALM](https://napalm.readthedocs.io/), integrates well with [containerlab](https://containerlab.srlinux.dev/) for cEOS labs but can also be used for vEOS or physical labs.

```
Usage: lab [OPTIONS] COMMAND [ARGS]...

Options:
  -n, --nornir PATH        Nornir configuration in YAML format.
  -t, --topology FILENAME  Containerlab topology file.
  --help                   Show this message and exit.

Commands:
  apply       Apply configuration templates
  backup      Create or delete device configuration backups to flash
  init-ceos   Configure cEOS serial number and system MAC address
  interfaces  Configure point-to-point interfaces
  load        Load configuration from a folder
  onboard     Onboard to CloudVision
  peering     Configure peering devices
  restore     Restore configuration backups from flash
  save        Save configuration to a folder
  start       Start containers
  stop        Stop containers
```

## Installation

Requires poetry to build the wheel.
You can use the make target `make all` that uses poetry to build the package with `poetry build` and installs the package with `pip`.

## Usage

### How to backup lab configuration ?

The command `lab backup` will backup all device running-configuration to flash. You can restore it anytime with `lab restore`.
The command `lab load --folder configs/lsl3-fabric` will load a L3LS fabric configuration initially generated with CloudVision Studios.
Some commands like `lab load` or `lab onboard` will automatically save configuration to flash, respectively before and after running the command.

> Once the backup configuration is present in flash, it won't be overriden unless you run `lab backup --delete`

### How to configure the serial number and system MAC ?

cEOS does not support modifying the serial number or system MAC after the first startup. It needs to be configured before dpeloying the lab with containerlab.
Configure the [Nornir inventory](project/inventory/hosts.yaml) and run the following commands:
```
lab init-ceos
containerlab deploy
```

### How to onboard the lab to CloudVision ?

Onboard to CloudVision
You can destroy a lab and re-onboard it in Cloudvision but you will need to configure the same correct serial number and system MAC address for each node so CloudVision will recognize the devices as already provisioned.

To correctly re-onboard a lab previously saved to CloudVision, you need to run:
```
lab init-ceos
containerlab deploy
```

> Ensure that the TerminAttr configuration and adequate username ares part of the startup config. Below is an example of minimal startup config:
```
username admin privilege 15 role network-admin secret arista
username cvpadmin privilege 15 role network-admin secret arista
!
aaa authorization exec default local
!
service routing protocols model multi-agent
!
platform tfa personality arfa
!
management api http-commands
   no shutdown
!
daemon TerminAttr
   exec /usr/bin/TerminAttr -cvcompression=gzip -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -cvaddr=192.168.100.100:9910 -cvauth=token,/tmp/token -cvvrf=default -taillogs
   no shutdown
!
```

Then go to your CloudVision instance, `Devices -> Device Registration -> Device Onboarding -> Onboard Provisioned EOS Devices` to re-onboard the devices by provisioning the certificates.

> It is a good idea (but not mandatory) to have fixed management IP addresses defined in the `topology.clab.yml` file.

### How to onboard the lab to CloudVision-as-a-service ?

Create a file with a generated secure token. Use the command `lab onboard --token cv-onboarding-token` to configure the lab and start to stream to CloudVision.
You can destroy a lab and re-onboard it in Cloudvision but you will need to configure the same correct serial number and system MAC address for each node so CloudVision will recognize the devices as already provisioned.

To correctly re-onboard a lab previously saved to CloudVision, you need to run:
```
lab init-ceos
containerlab deploy
lab onboard --token cv-onboarding-token
```

### How to configure point-to-point links ?

Use the `lab interfaces` command. The command takes a YAML file as input that defines the point-to-point IP subnet and eventually the IGP metrics and instance name.
Below is the YAML file structure. Refer to project example below for more details.

``` yaml
links:
  - endpoints: ["bas:et1", "ban:et1"]
    ipv4_subnet: 10.186.59.0/31
    ipv6_subnet: fc00:10:186:59::/127
    isis:
      instance: ISIS
      metric: 1
```

## Project skeleton

The structure below provides an example on how to structure a lab project:
```
.
├── clab-evpn-vxlan-fabric (containerlab topology directory - contains binds to device flash)
│   ├── ansible-inventory.yml
│   ├── leaf1
│   │   └── flash
│   ├── leaf2
│   │   └── flash
│   ├── leaf3
│   │   └── flash
│   ├── leaf4
│   │   └── flash
│   ├── spine1
│   │   └── flash
│   └── spine2
│       └── flash
├── Makefile (contains useful targets)
├── configs (arbitrary folder used to store configurations)
│   └── evpn-vxlan-fabric
│       ├── leaf1.cfg
│       ├── leaf2.cfg
│       ├── leaf3.cfg
│       ├── leaf4.cfg
│       ├── spine1.cfg
│       └── spine2.cfg
├── cv-onboarding-token (optional CVaaS token to onboard the devices)
├── inventory (contains Nornir inventory data)
│   ├── defaults.yaml
│   ├── groups.yaml
│   └── hosts.yaml
├── nornir.yaml (default Nornir configuration)
├── links.yaml (point-to-point links definition for the 'lab interfaces' command)
├── startup (arbitrary folder used to store startup configurations)
│   ├── leaf1.cfg
│   ├── leaf2.cfg
│   ├── leaf3.cfg
│   ├── leaf4.cfg
│   ├── spine1.cfg
│   └── spine2.cfg
└── topology.clab.yml (containerlab topology file)
```
> Default values are defined for the `nornir.yaml` and `topology.clab.yml` files but you can specify custom file names with the `--nornir`and `--topology` options.

### Project examples

- EVPN-VXLAN Fabric: TODO
- ISIS-BGP IP Backbone: TODO