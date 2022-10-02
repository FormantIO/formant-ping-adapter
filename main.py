#!/usr/bin/env python3

import os
import time
import json
import jsonschema

from formant.sdk.agent.v1 import Client as FormantAgentClient

"""
# Formant Ping Adapter

This adapter pings a remote host and then posts the result to a Formant stream to keep track of the robot's ping over time.

## Configuration

The adapter requires the following configuration:

`hostname` - The hostname or IP address to ping.

`interval` - The interval in seconds between pings.

`timeout` - The timeout for the ping, in seconds.

`formant_stream` - The name of the stream to post the ping to.

### Example Configuration

```json
{
    "hostname": "google.com",
    "interval": 60,
    "timeout": 5,
    "formant_stream": "ping"
}
```

### Configuration Schema

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://formant.io/formant_ping_adapter_configuration.schema.json",
    "title": "Formant Ping Adapter Configuration",
    "description": "Configuration for the ping adapter.",
    "type": "object",
    "properties": {
        "ping_adapter_configuration": {
            "description": "The top level wrapper for ping adapter configuration.",
            "type": "object",
            "properties": {
                "hostname": {
                    "description": "The host to ping.",
                    "type": "string",
                    "format": "hostname"
                },
                "interval": {
                    "description": "The interval in seconds between ping attempts.",
                    "type": "number",
                    "exclusiveMinimum": 0
                },
                "timeout": {
                    "description": "The timeout in seconds to wait for a response from the host.",
                    "type": "number",
                    "minimum": 0
                },
                "formant_stream": {
                    "description": "The Formant stream to send the ping results to.",
                    "type": "string"
                }
            },
            "required": ["hostname", "frequency", "timeout", "formant_stream"]
        }
    },
    "required": ["ros2_adapter_configuration"]
}
```

## Tags

Successful pings will be posted with a `success: true` tag, and failed pings will be posted with a `success: false` tag.

"""

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