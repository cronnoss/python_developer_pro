# python
import os
import gzip
import sys
import glob
import logging
import collections
from optparse import OptionParser
from threading import Thread
from multiprocessing import Pool, cpu_count
import memcache

import appsinstalled_pb2

NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple(
    "AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"]
)


def dot_rename(path):
    head, fn = os.path.split(path)
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(memc, appsinstalled_list, dry_run=False):
    items = {}
    readable = {}
    for appsinstalled in appsinstalled_list:
        ua = appsinstalled_pb2.UserApps()
        ua.lat = appsinstalled.lat
        ua.lon = appsinstalled.lon
        key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
        ua.apps.extend(appsinstalled.apps)
        packed = ua.SerializeToString()
        items[key] = packed
        readable[key] = str(ua).replace("\n", " ")

    try:
        server_repr = None
        if hasattr(memc, "servers") and memc.servers:
            server_repr = memc.servers[0]
        else:
            server_repr = memc

        if dry_run:
            for key, ua_str in readable.items():
                logging.debug("%s - %s -> %s" % (server_repr, key, ua_str))
        else:
            memc.set_multi(items)
    except Exception as exp:
        server_repr = server_repr if server_repr is not None else memc
        logging.exception("Cannot write to memc %s: %s" % (server_repr, exp))
        return False
    return True


def parse_appsinstalled(line):
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.strip().isdigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def process_line(line, device_memc, dry_run):
    appsinstalled = parse_appsinstalled(line)
    if not appsinstalled:
        return None
    memc_addr = device_memc.get(appsinstalled.dev_type)
    if not memc_addr:
        logging.error("Unknown device type: %s" % appsinstalled.dev_type)
        return None
    return appsinstalled


def process_file(fn, device_memc, dry_run):
    errors = 0
    logging.info("Processing %s" % fn)

    # Create memcache clients for each device type
    memc_idfa = memcache.Client([device_memc["idfa"]])
    memc_gaid = memcache.Client([device_memc["gaid"]])
    memc_adid = memcache.Client([device_memc["adid"]])
    memc_dvid = memcache.Client([device_memc["dvid"]])

    with gzip.open(fn, "rt") as fd:
        lines = fd.readlines()
        appsinstalled_list = []
        for line in lines:
            appsinstalled = process_line(line, device_memc, dry_run)
            if appsinstalled:
                appsinstalled_list.append(appsinstalled)

        # Group by device type
        per_dev = {"idfa": [], "gaid": [], "adid": [], "dvid": []}
        for ai in appsinstalled_list:
            if ai.dev_type in per_dev:
                per_dev[ai.dev_type].append(ai)
            else:
                logging.error("Unknown device type while grouping: %s" % ai.dev_type)
                errors += 1

        memc = {
            "idfa": memc_idfa,
            "gaid": memc_gaid,
            "adid": memc_adid,
            "dvid": memc_dvid,
        }
        succeeded = 0

        # Use insert_appsinstalled per device type so dry-run logs are consistent
        for dev_type, apps_list in per_dev.items():
            if not apps_list:
                continue
            ok = insert_appsinstalled(memc[dev_type], apps_list, dry_run)
            if ok:
                succeeded += len(apps_list)
            else:
                errors += len(apps_list)

        processed = len(appsinstalled_list)

    if not processed:
        dot_rename(fn)
        return

    err_rate = float(errors) / processed
    if err_rate < NORMAL_ERR_RATE:
        logging.info("Acceptable error rate (%s). Successful load" % err_rate)
    else:
        logging.error(
            "High error rate (%s > %s). Failed load" % (err_rate, NORMAL_ERR_RATE)
        )
    dot_rename(fn)


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }
    threads = []
    for fn in glob.iglob(options.pattern):
        thread = Thread(target=process_file, args=(fn, device_memc, options.dry))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO if not opts.dry else logging.DEBUG,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
