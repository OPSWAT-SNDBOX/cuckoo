# Copyright (C) 2010-2013 Claudio Guarnieri.
# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import ConfigParser
import os
import logging
import click

from cuckoo.common.exceptions import CuckooOperationalError
from cuckoo.common.objects import Dictionary
from cuckoo.misc import cwd

log = logging.getLogger(__name__)


class Type(object):
    """Base Class for Type Definitions"""

    def __init__(self):
        """Base constructor for Type Definition class"""
        pass

    def get(self, config, section, name):
        """Gets the Parameter value from the config file."""
        pass

    def check(self, value):
        """Checks the type of the value."""
        pass


class Int(Type):
    """Integer Type Definition class. """

    def __init__(self):
        """Constructor for Integer Type."""
        super(Int, self).__init__()
        return

    def get(self, config, section, name):
        """Gets the value of the parameter from the config file. """
        try:
            value = config.getint(section, name)
        except ValueError:
            value = config.get(section, name)
            if value is not "":
                log.error("Incorrect Integer %s", value)
        return value

    def check(self, value):
        """Checks if the value is of type Integer. """
        try:
            click.INT(value)
            return True
        except Exception as ex:
            return False


class String(Type):
    """ String Type Definition class. """

    def __init__(self):
        """Constructor for String Type."""
        super(String, self).__init__()
        return

    def get(self, config, section, name):
        """Gets the value of the parameter from the config file. """
        value = config.get(section, name)
        return value

    def check(self, value):
        """Checks if the value is of type String. """
        if isinstance(value, str):
            return True
        else:
            return False


class Path(String):
    """ Path Type Definition class. """

    def __init__(self, exists=False, writable=False, readable=False):
        """Constructor for Path Type."""
        super(Path, self).__init__()
        self.exists = exists
        self.writable = writable
        self.readable = readable
        return

    def get(self, config, section, name):
        """Gets the value of the parameter from the config file."""
        try:
            c = click.Path(exists=self.exists, writable=self.writable, readable=self.readable)
            value = c.convert(config.get(section, name), None, None)
        except Exception as ex:
            value = config.get(section, name)
            if value is not "":
                log.error("Incorrect Path : %s , Error : %s", value, ex)
        return value

    def check(self, value, exists=False, writable=False, readable=False):
        """Checks if the value is of type String. """
        try:
            c = click.Path(exists=exists, writable=writable, readable=readable)
            c.convert(value, None, None)
            return True
        except Exception as ex:
            return False


class Boolean(Type):
    """ Boolean Type Definition class. """

    def __init__(self):
        """Constructor for Boolean Type."""
        super(Boolean, self).__init__()
        return

    def get(self, config, section, name):
        """Gets the value of the parameter from the config file. """
        try:
            value = config.getboolean(section, name)
        except ValueError:
            value = config.get(section, name)
            if value is not "":
                log.error("Incorrect Boolean %s", value)
        return value

    def check(self, value):
        """Checks if the value is of type Boolean. """
        try:
            click.BOOL(value)
            return True
        except Exception as ex:
            return False


class UUID(Type):
    """ UUID Type Definition class. """

    def __init__(self):
        """Constructor for UUID Type."""
        super(UUID, self).__init__()
        return

    def get(self, config, section, name):
        """Gets the value of the parameter from the config file. """
        try:
            c = click.UUID(config.get(section, name))
            value = str(c)
        except Exception as ex:
            value = config.get(section, name)
            if value is not "":
                log.error("Incorrect UUID %s", value)
        return value

    def check(self, value):
        """Checks if the value is of type UUID. """
        try:
            click.UUID(value)
            return True
        except Exception as ex:
            return False


class Config:
    """Configuration file parser."""

    # Config Parameters and their types
    ParamTypes = {
        ## cuckoo.conf parameters
        "cuckoo": {
            "cuckoo": {
                "version_check": Boolean(),
                "delete_original": Boolean(),
                "delete_bin_copy": Boolean(),
                "machinery": String(),
                "memory_dump": Boolean(),
                "terminate_processes": Boolean(),
                "reschedule": Boolean(),
                "process_results": Boolean(),
                "debug": Boolean(),
                "max_analysis_count": Int(),
                "max_machines_count": Int(),
                "max_vmstartup_count": Int(),
                "critical_timeout": Int(),
                "freespace": Int(),
                "tmppath": Path(exists=True, writable=True, readable=False),
                "rooter": Path(exists=False, writable=False, readable=True),
            },
            "resultserver": {
                "ip": String(),
                "port": Int(),
                "force_port": Boolean(),
                "upload_max_size": Int(),
            },
            "processing": {
                "analysis_size_limit": Int(),
                "resolve_dns": Boolean(),
                "sort_pcap": Boolean(),
            },
            "database": {
                "connection": String(),
                "timeout": Int(),
            },
            "timeouts": {
                "default": Int(),
                "critical": Int(),
                "vm_state": Int(),
            },
        },
        ## virtualbox.conf parameters
        "virtualbox": {
            "virtualbox": {
                "mode": String(),
                "path": Path(exists=True, writable=False, readable=True),
                "interface": String(),
                "machines": String(),
            },
            "*": {
                "label": String(),
                "platform": String(),
                "ip": String(),
                "snapshot": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
            },
            "honeyd": {
                "label": String(),
                "platform": String(),
                "ip": String(),
                "tags": String(),
                "options": String(),
            },
        },
        ## auxiliary.conf parameters
        "auxiliary": {
            "sniffer": {
                "enabled": Boolean(),
                "tcpdump": Path(exists=True, writable=False, readable=True),
                "bpf": String(),
            },
            "mitm": {
                "enabled": Boolean(),
                "mitmdump": Path(exists=True, writable=False, readable=True),
                "port_base": Int(),
                "script": Path(exists=True, writable=False, readable=True),
                "certificate": Path(exists=True, writable=False, readable=True),
            },
            "services": {
                "enabled": Boolean(),
                "services": String(),
                "timeout": Int(),
            },
            "reboot": {
                "enabled": Boolean(),
            },
        },
        ## avd.conf parameters
        "avd": {
            "avd": {
                "mode": String(),
                "emulator_path": Path(exists=True, writable=False, readable=True),
                "adb_path": Path(exists=True, writable=False, readable=True),
                "avd_path": Path(exists=True, writable=False, readable=True),
                "reference_machine": String(),
                "machines": String(),
            },
            "*": {
                "label": String(),
                "platform": String(),
                "ip": String(),
                "emulator_port": Int(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
            },
        },
        ## esx.conf parameters
        "esx": {
            "esx": {
                "dsn": String(),
                "username": String(),
                "password": String(),
                "machines": String(),
                "interface": String(),
            },
            "*": {
                "label": String(),
                "platform": String(),
                "ip": String(),
                "snapshot": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
            },
        },
        ## kvm.conf parameters
        "kvm": {
            "kvm": {
                "machines": String(),
                "interface": String(),
            },
            "*": {
                "label": String(),
                "platform": String(),
                "ip": String(),
                "snapshot": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
            },
        },
        ## memory.conf parameters
        "memory": {
            "basic": {
                "guest_profile": String(),
                "delete_memdump": String(),
                "filter": Boolean(),
            },
            "malfind": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "apihooks": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "pslist": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "psxview": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "callbacks": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "idt": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "timers": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "messagehooks": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "getsids": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "privs": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "dlllist": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "handles": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "ldrmodules": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "mutantscan": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "devicetree": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "svcscan": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "modscan": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "yarascan": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "ssdt": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "gdt": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "sockscan": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "netscan": {
                "enabled": Boolean(),
                "filter": Boolean(),
            },
            "mask": {
                "enabled": Boolean(),
                "pid_generic": String(),
            },
        },
        ## physical.conf parameters
        "physical": {
            "physical": {
                "machines": String(),
                "user": String(),
                "password": String(),
                "interface": String(),
            },
            "fog": {
                "hostname": String(),
                "username": String(),
                "password": String(),
            },
            "*": {
                "label": String(),
                "platform": String(),
                "ip": String(),
            },
        },
        ## processing.conf parameters
        "processing": {
            "analysisinfo": {
                "enabled": Boolean(),
            },
            "apkinfo": {
                "enabled": Boolean(),
                "decompilation_threshold": Int(),
            },
            "baseline": {
                "enabled": Boolean(),
            },
            "behavior": {
                "enabled": Boolean(),
            },
            "buffer": {
                "enabled": Boolean(),
            },
            "debug": {
                "enabled": Boolean(),
            },
            "droidmon": {
                "enabled": Boolean(),
            },
            "dropped": {
                "enabled": Boolean(),
            },
            "dumptls": {
                "enabled": Boolean(),
            },
            "googleplay": {
                "enabled": Boolean(),
                "android_id": String(),
                "google_login": String(),
                "google_password": String(),
            },
            "memory": {
                "enabled": Boolean(),
            },
            "misp": {
                "enabled": Boolean(),
                "url": String(),
                "apikey": String(),
                "maxioc": Int(),
            },
            "network": {
                "enabled": Boolean(),
            },
            "procmemory": {
                "enabled": Boolean(),
                "idapro": Boolean(),
                "extract_img": Boolean(),
                "dump_delete": Boolean(),
            },
            "procmon": {
                "enabled": Boolean(),
            },
            "screenshots": {
                "enabled": Boolean(),
                "tesseract": Boolean(),
            },
            "snort": {
                "enabled": Boolean(),
                "snort": Path(exists=False, writable=False, readable=True),
                "conf": Path(exists=False, writable=False, readable=True),
            },
            "static": {
                "enabled": Boolean(),
            },
            "String()s": {
                "enabled": Boolean(),
            },
            "suricata": {
                "enabled": Boolean(),
                "suricata": Path(exists=True, writable=False, readable=True),
                "eve_log": Path(exists=False, writable=True, readable=False),
                "files_log": Path(exists=False, writable=True, readable=False),
                "files_dir": Path(exists=False, writable=False, readable=True),
                "socket": Path(exists=True, writable=False, readable=True),
            },
            "targetinfo": {
                "enabled": Boolean(),
            },
            "virustotal": {
                "enabled": Boolean(),
                "timeout": Int(),
                "scan": Boolean(),
                "key": String(),
            },
            "irma": {
                "enabled": Boolean(),
                "force": Boolean(),
                "timeout": Int(),
                "scan": Boolean(),
                "url": String(),
            },
        },
        ## qemu.conf parameters
        "qemu": {
            "qemu": {
                "path": Path(exists=True, writable=False, readable=True),
                "interface": String(),
                "machines": String(),
            },
            "*": {
                "label": String(),
                "image": Path(exists=True, writable=False, readable=True),
                "arch": String(),
                "platform": String(),
                "ip": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
                "kernel_path": Path(exists=True, writable=False, readable=True),
            },
        },
        ## reporting.conf parameters
        "reporting": {
            "jsondump": {
                "enabled": Boolean(),
                "indent": Int(),
                "encoding": String(),
                "calls": Boolean(),
            },
            "reporthtml": {
                "enabled": Boolean(),
            },
            "misp": {
                "enabled": Boolean(),
                "url": String(),
                "apikey": String(),
                "mode": String(),
            },
            "mongodb": {
                "enabled": Boolean(),
                "host": String(),
                "port": Int(),
                "db": String(),
                "store_memdump": Boolean(),
                "paginate": Int(),
            },
            "elasticsearch": {
                "enabled": Boolean(),
                "hosts": String(),
                "calls": Boolean(),
                "index": String(),
                "index_time_pattern": String(),
            },
            "moloch": {
                "enabled": Boolean(),
                "host": String(),
                "moloch_capture": Path(exists=True, writable=False, readable=True),
                "conf": Path(exists=True, writable=False, readable=True),
                "instance": String(),
            },
            "notification": {
                "enabled": Boolean(),
                "url": String(),
                "identifier": String(),
            },
        },
        ## routing.conf parameters
        "routing": {
            "routing": {
                "route": String(),
                "internet": String(),
                "rt_table": String(),
                "auto_rt": Boolean(),
                "drop": Boolean(),
            },
            "inetsim": {
                "enabled": Boolean(),
                "server": String(),
            },
            "tor": {
                "enabled": Boolean(),
                "dnsport": Int(),
                "proxyport": Int(),
            },
            "vpn": {
                "enabled": Boolean(),
                "vpns": String(),
            },
            "*": {
                "name": String(),
                "description": String(),
                "interface": String(),
                "rt_table": String(),
            },
        },
        ## vmware.conf parameters
        "vmware": {
            "vmware": {
                "mode": String(),
                "path": Path(exists=True, writable=False, readable=True),
                "interface": String(),
                "machines": String(),
            },
            "*": {
                "vmx_path": Path(exists=True, writable=False, readable=True),
                "snapshot": String(),
                "platform": String(),
                "ip": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
            },
        },
        ## vsphere.conf parameters
        "vsphere": {
            "vsphere": {
                "host": String(),
                "port": Int(),
                "user": String(),
                "pwd": String(),
                "interface": String(),
                "machines": String(),
                "unverified_ssl": Boolean(),
            },
            "*": {
                "label": String(),
                "platform": String(),
                "ip": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
            },
        },
        ## xenserver.conf parameters
        "xenserver": {
            "xenserver": {
                "user": String(),
                "password": String(),
                "url": String(),
                "interface": String(),
                "machines": String(),
            },
            "*": {
                "uuid": UUID(),
                "snapshot": String(),
                "platform": String(),
                "ip": String(),
                "interface": String(),
                "resultserver_ip": String(),
                "resultserver_port": Int(),
                "tags": String(),
            },
        },
    }

    def __init__(self, file_name="cuckoo", cfg=None):
        """
        @param file_name: file name without extension.
        @param cfg: configuration file path.
        """
        env = {}
        for key, value in os.environ.items():
            if key.startswith("CUCKOO_"):
                env[key] = value

        config = ConfigParser.ConfigParser(env)

        if cfg:
            config.read(cfg)
        else:
            config.read(cwd("conf", "%s.conf" % file_name))

        if file_name not in self.ParamTypes:
            log.error("Unknown config file %s.conf" % (file_name))
            return
        for section in config.sections():
            if section in self.ParamTypes[file_name]:
                sectionTypes = self.ParamTypes[file_name][section]
            ## Hacky fix to get the type of unknown sections
            elif "*" in self.ParamTypes[file_name]:
                sectionTypes = self.ParamTypes[file_name]["*"]
            else:
                log.error("Config section %s NOT FOUND!!" % (section))
                continue
            setattr(self, section, Dictionary())
            for name, raw_value in config.items(section):
                if getattr(getattr(self, section), "enabled", None) in [True, None]:
                    if name in sectionTypes:
                        value = sectionTypes[name].get(config, section, name)
                    else:
                        log.error("Type of config parameter %s.%s NOT FOUND!!" % (section, name))
                        value = config.get(section, name)
                    setattr(getattr(self, section), name, value)

    def get(self, section):
        """Get option.
        @param section: section to fetch.
        @raise CuckooOperationalError: if section not found.
        @return: option value.
        """
        try:
            return getattr(self, section)
        except AttributeError as e:
            raise CuckooOperationalError("Option %s is not found in "
                                         "configuration, error: %s" %
                                         (section, e))


def parse_options(options):
    """Parse the analysis options field to a dictionary."""
    ret = {}
    for field in options.split(","):
        if "=" not in field:
            continue

        key, value = field.split("=", 1)
        ret[key.strip()] = value.strip()
    return ret


def emit_options(options):
    """Emit the analysis options from a dictionary to a string."""
    return ",".join("%s=%s" % (k, v) for k, v in options.items())
