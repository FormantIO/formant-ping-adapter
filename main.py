#!/usr/bin/env python3

import os
import time
import json
import jsonschema

from formant.sdk.agent.v1 import Client as FormantAgentClient


class PingAdapter:
    """
    Formant Ping Adapter
    """

    def __init__(self):
        print("INFO: Ping Adapter has started")

        # Set up the config object
        self.config = {}
        self.config_schema = {}

        # Set up the adapter
        self.fclient = FormantAgentClient(ignore_throttled=True, ignore_unavailable=True)
        self.fclient.register_config_update_callback(self.update_adapter_configuration)

    def update_adapter_configuration(self):
        # TODO: stop the ping process

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
        except Exception as e:
            print("WARNING: Validation failed:", e)
            self.fclient.create_event(
                "ROS2 Adapter configuration failed validation",
                notify=False,
                severity="warning", 
            )
            return

        # Set the config object to the validated configuration
        if "ping_adapter_configuration" in config_blob:
            self.config = config_blob["ping_adapter_configuration"]
        else:
            self.config = {}


        # TODO: Create a thread to ping the host

        
        self.fclient.post_json("adapter.configuration", json.dumps(self.config))
        self.fclient.create_event(
            "Ping Adapter started",
            notify=False,
            severity="info", 
        )
        print("INFO: Posted update event and config")


if __name__ == "__main__":
    PingAdapter()