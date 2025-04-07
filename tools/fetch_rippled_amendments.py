"""
This script fetches the latest amendments from (the `develop` branch of) rippled and
adds them to the `rippled.cfg` file.
"""

import configparser
import os
import re

import requests

CONFIG_FILE = os.path.join(os.getcwd(), ".ci-config", "rippled.cfg")
FEATURES_SECTION = "features"
RIPPLED_FEATURES_FILE = "https://raw.githubusercontent.com/XRPLF/rippled/develop/include/xrpl/protocol/detail/features.macro"

config = configparser.ConfigParser(
    allow_no_value=True,
)
config.optionxform = str  # type: ignore
config.read(CONFIG_FILE)


def fetch_rippled_amendments():
    # Send a GET request
    response = requests.get(RIPPLED_FEATURES_FILE, timeout=30)  # 30 second timeout

    # Check for successful request
    if response.status_code == 200:
        features_contents = response.text
        feature_hits = re.findall(
            feature_hits = re.findall(
                r"^ *XRPL_FEATURE *\(([a-zA-Z0-9_]+), * Supported::yes, VoteBehavior::Default(Yes|No)",
                features_contents,
                re.MULTILINE,
            )

        fix_hits = re.findall(
            r"^ *XRPL_FIX *\(([a-zA-Z0-9_]+), * Supported::yes,",
            features_contents,
            re.MULTILINE,
        )

        all_supported_amendments = feature_hits + ["fix" + f for f in fix_hits]
        return all_supported_amendments
    else:
        print(f"Failed to fetch file. Status code: {response.status_code}")
        return []

if __name__ == "__main__":
    if FEATURES_SECTION in config:
        amendments_to_add = []
        existing_amendments = [v for v in config[FEATURES_SECTION] if v]
        new_rippled_amendments = fetch_rippled_amendments()

        for v in new_rippled_amendments:
            if v not in existing_amendments:
                amendments_to_add.append(v)

        if len(amendments_to_add) > 0:
            print(
                "INFO: The following amendments need to be inserted into the config file: "
                + ", ".join(amendments_to_add)
            )

            for v in amendments_to_add:
                config.set(FEATURES_SECTION, v, value=None)

            with open(CONFIG_FILE, "w", encoding="utf-8") as rippled_cfg_file:
                config.write(rippled_cfg_file)
        else:
            print(f"INFO: No new amendments to add into the {CONFIG_FILE} file.")
    else:
        print(f"ERROR: No features section found in the {CONFIG_FILE} file.")
