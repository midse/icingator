#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy.snmp import SNMPException
from bottle import route, run, template, request, static_file

from collections import OrderedDict
import subprocess
import glob
import re
import time

from config import config, IF_TYPE_VALUES, LOCATIONS

p_block = re.compile(r'<ICINGATOR_BEGIN>.*?(object Host.*?)</ICINGATOR_END>', re.DOTALL)
p_sysname = re.compile(r'object Host "(.*?)" {')
p_address = re.compile(r'address.*?=.*?"(.*?)"')
p_display_name = re.compile(r'display_name.*?=.*?"(.*?)"')
p_os = re.compile(r'vars\.os.*?=.*?"(.*?)"')
p_oids = re.compile(r'vars\.oids\[".+?"\].*?=.*?"(\d+)"')

cisco_mib_path = config['SNMP_CISCO']['mib_path']
forti_mib_path = config['SNMP_FORTINET']['mib_path']

load("{}".format(cisco_mib_path))


def get_interfaces(host, device_type):
    section = 'SNMP_' + device_type

    m = M(version=3, host=host, secname=config[section]['secname'],
          authprotocol=config[section]["authprotocol"], authpassword=config[section]["authpassword"],
          privprotocol=config[section]["privprotocol"], privpassword=config[section]["privpassword"])

    interfaces = OrderedDict()
    for id in m.ifName:
        interfaces[id] = [m.ifName[id], m.ifAlias[id], m.ifOperStatus[id], IF_TYPE_VALUES[int(m.ifType[id])]]

    return interfaces


def get_sysname(host, device_type):
    section = 'SNMP_' + device_type

    m = M(version=3, host=host, secname=config[section]["secname"],
          authprotocol=config[section]["authprotocol"], authpassword=config[section]["authpassword"],
          privprotocol=config[section]["privprotocol"], privpassword=config[section]["privpassword"])

    return m.sysName.split('.')[0]


def get_existing_files():
    return glob.glob(config['ICINGA']['conf_folder'] + '/conf.d/icingator_hst-*.conf')


def get_all_existing_sysnames():
    existing_devices = []

    for conf_file in get_existing_files():
        with open(conf_file, 'r') as data:
            data = data.read()
            existing_devices.extend(re.findall(p_display_name, data))

    return existing_devices


def get_full_conf_path(filename):
    prefix = ''
    suffix = ''

    if filename.startswith(config['ICINGA']['conf_folder']):
        return filename

    if not filename.startswith('icingator_'):
        prefix = 'icingator_'

    if not filename.endswith('.conf'):
        suffix = '.conf'

    return '{}/conf.d/{}{}{}'.format(config['ICINGA']['conf_folder'], prefix, filename, suffix)


def parse_conf_file(filename):
    devices = []

    with open(get_full_conf_path(filename), 'r') as opened_conf_file:
        data = opened_conf_file.read()
        all_blocks = re.findall(p_block, data)

        for block in all_blocks:
            conf = {}

            conf['sysname'] = re.findall(p_sysname, block)[0]
            conf['host'] = re.findall(p_address, block)[0]
            conf['device_type'] = re.findall(p_os, block)[0]

            # We are parsing the oids to be able to show already monitored interfaces
            conf['oids'] = re.findall(p_oids, block)

            devices.append(conf)

    return devices


def get_location(sysname):
    # LOCATIONS are defined in config.py file
    if sysname[:2] in LOCATIONS:  # Check the first 2 chars
        return LOCATIONS[sysname[:2]]
    elif sysname[len(sysname) - 2:] in LOCATIONS:  # Check the last 2 chars
        return LOCATIONS[sysname[len(sysname) - 2:]]
    else:
        split = sysname.split('-')

        reduced_name = split[len(split) - 2][len(split[len(split) - 2]) - 2:]  # Check this kind of hostname --> XXXDA-1 (where DA is the location)
        if reduced_name in LOCATIONS:
            return LOCATIONS[reduced_name]

    return 'UNKNOWN'


@route('/<filename:re:.*\.css>', method="GET")
def stylesheets(filename):
    return static_file(filename, root='static/css/')


@route('/<filename:re:.*\.js>', method="GET")
def javascript(filename):
    return static_file(filename, root='static/js/')


@route('/<filename:re:.*\.(jpg|png|gif|ico)>', method="GET")
def images(filename):
    return static_file(filename, root='static/img/')


@route('/')
def index():
    device_types = sorted(config['ICINGATOR']['device_types'].split(','))
    existing_devices = sorted(get_all_existing_sysnames())

    # Template file --> views/index.tpl
    return template('index', device_types=device_types, conf_files=existing_devices)


@route('/device', method='POST')
def do_device():
        host = request.forms.get('host')
        device_type = request.forms.get('device_type')

        try:
            sysname = get_sysname(host, device_type)
            interfaces = get_interfaces(host, device_type)
        except SNMPException as error:
            return template('<br><br><br><br><span class="pure-button button-error">SNMP error : {{error}}</span>', error=error)

        oids = []

        conf_file = get_full_conf_path('hst-' + device_type)
        # If device already has a conf file, we parse it to load monitored interfaces
        if conf_file in get_existing_files():
            oids = parse_conf_file(conf_file)[0]['oids']
            print(parse_conf_file(conf_file))

        # Template file --> views/my_device.tpl
        return template('my_device',
                        nb_interfaces=len(interfaces),
                        host=host,
                        sysname=sysname,
                        device_type=device_type,
                        interfaces=sorted(interfaces.items(), key=lambda tuple: tuple[1][0]),
                        oids=oids)


@route('/conf', method='POST')
def do_conf():
        sysname = request.forms.get('conf_file')

        conf = {}

        for conf_file in get_existing_files():
            devices = parse_conf_file(conf_file)

            for device in devices:
                if device['sysname'] == sysname:
                    conf = device
                    break
            if conf:
                break

        try:
            interfaces = get_interfaces(conf['host'], conf['device_type'])
        except SNMPException as error:
            return template('<br><br><br><br><span class="pure-button button-error">We got an SNMP error : {{error}}</span>', error=error)

        # Template file --> views/my_device.tpl
        return template('my_device',
                        nb_interfaces=len(interfaces),
                        host=conf['host'],
                        sysname=conf['sysname'],
                        device_type=conf['device_type'],
                        interfaces=sorted(interfaces.items(), key=lambda tuple: tuple[1][0]),
                        oids=conf['oids'])


@route('/icinga', method='POST')
def do_icinga():
        interfaces = request.forms.getall('interfaces')
        host = request.forms.get('host')
        device_type = request.forms.get('device_type')

        try:
            sysname = get_sysname(host, device_type)
        except SNMPException as error:
            return template('<br><br><br><br><span class="pure-button button-error">We got an SNMP error : {{error}}</span>', error=error)

        location = get_location(sysname)

        output = template('icinga_host', sysname=sysname, device_type=device_type, interfaces=interfaces, host=host, location=location, dateandtime=time.strftime("%c"))

        with open(get_full_conf_path('hst-' + device_type), "a+") as conf_file:
                conf_file.write(output)

        disclaimer = "We didn't reload Icinga because 'reload_after_generate' option is disabled!"
        if config.getboolean("ICINGA", "reload_after_generate"):
            p = subprocess.Popen(config['ICINGA']['reload_command'], stdout=subprocess.PIPE, shell=True)

            (_, err) = p.communicate()

            disclaimer = "Something went wrong... We weren't able to reload Icinga. Check with your administrator"
            if not err:
                disclaimer = "Icinga was successfully reloaded!"

            p.wait()

        return template('<br><br><strong>{{disclaimer}}</strong><br><br><textarea cols="80" rows="20">{{output}}</textarea><br><br>', output=output, disclaimer=disclaimer)

run(host=config['BOTTLE']['host'], port=int(config['BOTTLE']['port']))
