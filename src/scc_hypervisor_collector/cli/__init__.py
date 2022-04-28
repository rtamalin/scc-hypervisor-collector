""""
SCC Hypervisor Collect CLI Implementation
"""
import argparse
import logging
from typing import (Optional, Sequence)
import yaml

from scc_hypervisor_collector import __version__ as cli_version
from scc_hypervisor_collector import (ConfigManager, CollectionScheduler)


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Implements CLI for the scc-hypervisor-gatherer."""
    parser = argparse.ArgumentParser(
        description="Collect configured hypervisor details and upload to "
                    "SUSE Customer Center (SCC)."
    )

    # General purpose options
    parser.add_argument('-V', '--version', action='version',
                        version="%(prog)s " + str(cli_version))

    # Output verbosity control
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-q', '--quiet', action='store_true',
                           help="Decrease output verbosity.")
    verbosity.add_argument('-v', '--verbose', action='store_true',
                           help="Increase output verbosity.")

    # Primary command line options
    parser.add_argument('-c', '--config', default='scchvc.yaml',
                        help="The YAML config file to use.")
    parser.add_argument('--config_dir', '--config-dir',
                        default='~/.config/scc-hypervisor-collector',
                        help="The config directory to check for YAML "
                             "config files.")
    parser.add_argument('-C', '--check', action='store_true',
                        help="Check the configuration data only, "
                             "reporting any errors.")

    args = parser.parse_args(argv)

    if args.quiet:
        log_level = logging.WARN
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level)

    cfg_mgr = ConfigManager(config_file=args.config,
                            config_dir=args.config_dir)

    logging.info("ConfigManager: config_data = %s", repr(cfg_mgr.config_data))

    if args.check:
        return

    scheduler = CollectionScheduler(cfg_mgr.config_data)

    logging.debug("Scheduler: scheduler = %s", repr(scheduler))

    scheduler.run()

    # TODO(rtamalin): Make reporting the results like this optional
    # once the SccUploader is implemented.
    for hv in scheduler.hypervisors:
        print(f"[{hv.backend.id}]")
        print(yaml.safe_dump(hv.details))


__all__ = ['main']
