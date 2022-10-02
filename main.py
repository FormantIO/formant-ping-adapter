#!/usr/bin/env python3

import os
import time
import json
import subprocess
import jsonschema

from formant.sdk.agent.v1 import Client as FormantAgentClient

DEFAULT_HOSTNAME = "formant.io"
DEFAULT_INTERVAL = 10
DEFAULT_TIMEOUT = 5
DEFAULT_FORMANT_STREAM = "ping"


class PingAdapter:
    """
    Formant Ping Adapter
    """

    def __init__(self):
        print("INFO: Ping Adapter has started")

        # Set up the config object
        self.config = {}
        self.config_schema = {}

        # Set up the default config params
        self.hostname = DEFAULT_HOSTNAME
        self.interval = DEFAULT_INTERVAL
        self.timeout = DEFAULT_TIMEOUT
        self.formant_stream = DEFAULT_FORMANT_STREAM

        # Set up the adapter
        self.fclient = FormantAgentClient(ignore_throttled=True, ignore_unavailable=True)
        self.fclient.register_config_update_callback(self.update_adapter_configuration)

        # Start the ping process
        while True:
            self.ping_host()
            time.sleep(self.interval)

    def update_adapter_configuration(self):
        # Load config from either the agent's json blob or the config.json file
        try:
            config_blob = json.loads(self.fclient.get_config_blob_data())
            print("INFO: Loaded config from agent")
        except:
            # Otherwise, load from the config.json file shipped with the adapter
            current_directory = os.path.dirname(os.path.realpath(__file__))
            with open(f"{current_directory}/config.json") as f:
                config_blob = json.loads(f.read())

            print("INFO: Loaded config from config.json file")
            
        # Validate configuration based on schema
        with open("config_schema.json") as f:
            try:
                self.config_schema = json.load(f)
                print("INFO: Loaded config schema from config_schema.json file")
            except:
                print("ERROR: Could not load config schema. Is the file valid json?")
                return

        print("INFO: Validating config...")

        # Runt the validation check    
        try:
            jsonschema.validate(config_blob, self.config_schema)
            print("INFO: Validation succeeded")

            # Set the config object to the validated configuration
            if "ping_adapter_configuration" in config_blob:
                self.config = config_blob["ping_adapter_configuration"]
            else:
                self.config = {}

        except Exception as e:
            print("WARNING: Validation failed:", e)
            self.fclient.create_event(
                "ROS2 Adapter configuration failed validation",
                notify=False,
                severity="warning", 
            )

            # If the config is invalid, the default will be used
            self.config = {}

        # Set the config params
        self.hostname = self.config.get("hostname", DEFAULT_HOSTNAME)
        self.interval = self.config.get("interval", DEFAULT_INTERVAL)
        self.timeout = self.config.get("timeout", DEFAULT_TIMEOUT)
        self.formant_stream = self.config.get("formant_stream", DEFAULT_FORMANT_STREAM)

        # Post the startup event
        self.fclient.post_json("adapter.configuration", json.dumps(self.config))
        self.fclient.create_event(
            "Ping Adapter started",
            notify=False,
            severity="info", 
        )
        print("INFO: Posted update event and config")

    def ping_host(self):
        """
        Ping the host and post the results to the Formant stream
        """

        # Ping the host
        try:
            response = subprocess.run(
                ["ping", "-c", "1", "-W", str(self.timeout), self.hostname],
                capture_output=True,
                text=True,
            )
        except Exception as e:
            print("ERROR: Ping failed:", e)
            return

        # Parse the ping response
        if response.returncode == 0:
            # Successful ping
            success = True
            ping_time = float(response.stdout.split("time=")[1].split(" ms")[0])
        else:
            # Failed ping
            success = False
            ping_time = None

        # Post the ping result to the Formant stream
        self.fclient.post_numeric(
            self.formant_stream,
            ping_time,
            tags={
                "success": str(success),
                "hostname": str(self.hostname),
            }
        )


if __name__ == "__main__":
    PingAdapter()