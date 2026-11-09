#!/usr/bin/env python3
"""Sanity checks for the Zabbix template YAML (no Zabbix server needed)."""
import re
import sys
import glob
import yaml

errors = []
files = glob.glob("template/*.yaml")
if not files:
    sys.exit("no template found")

for f in files:
    doc = yaml.safe_load(open(f))["zabbix_export"]
    tpl = doc["templates"][0]
    name = tpl["template"]
    macros = {m["macro"] for m in tpl["macros"]}
    uuids = []
    def walk(o):
        if isinstance(o, dict):
            if "uuid" in o:
                uuids.append(o["uuid"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    for x in uuids:
        if not re.fullmatch(r"[0-9a-f]{32}", x) or x[12] != "4" or x[16] not in "89ab":
            errors.append(f"{f}: invalid uuid v4: {x}")
    if len(uuids) != len(set(uuids)):
        errors.append(f"{f}: duplicated uuids")
    rule = tpl["discovery_rules"][0]
    keys = {i["key"].split("[")[0] for i in rule["item_prototypes"]}
    for t in rule["trigger_prototypes"]:
        for m in re.findall(r"\{\$[A-Z0-9_.]+\}", t["expression"] + t["name"]):
            if m not in macros:
                errors.append(f"{f}: undefined macro {m} in trigger '{t['name']}'")
        for k in re.findall(r"/([^/]+)/([a-z.]+)\[", t["expression"]):
            if k[0] != name:
                errors.append(f"{f}: trigger refers to wrong host '{k[0]}'")
            if k[1] not in keys:
                errors.append(f"{f}: trigger uses unknown item key {k[1]}")
        if "{#SNMPINDEX}" not in t["name"]:
            errors.append(f"{f}: trigger name lacks LLD macro: {t['name']}")
    vm = {v["name"] for v in tpl.get("valuemaps", [])}
    for i in rule["item_prototypes"]:
        if "valuemap" in i and i["valuemap"]["name"] not in vm:
            errors.append(f"{f}: missing value map {i['valuemap']['name']}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK")
