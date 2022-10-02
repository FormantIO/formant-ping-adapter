# Formant Ping Adapter

This adapter pings a remote host and then posts the result to a Formant stream to keep track of the robot's ping over time.

Note that the recorded ping is to an internet site, and will not necessarily reflect the ping to a remote operator.

## Configuration

The adapter uses the following configuration:

| Parameter      | Description                                | Default    |
| -------------- | ------------------------------------------ | ---------- |
| hostname       | The hostname or IP address to ping         | formant.io |
| interval       | The interval in seconds between pings      | 5          |
| timeout        | The timeout for the ping, in seconds       | 5          |
| formant_stream | The name of the stream to post the ping to | ping       |

## Tags

Successful pings will be posted with a `success: true` tag, and failed pings will be posted with a `success: false` tag. The hostname will also be tagged to each ping.

## Usage

To use the adapter, pull down this repository and create a zip file:
```
zip -r ping-adapter.zip ping-adapter
```

Then, upload the zip file Formant's adapters management page and set the start script to `./start.sh`. This adapter can then be selected in device configuration.
