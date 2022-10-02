# Formant Ping Adapter

This adapter pings a remote host and then posts the result to a Formant stream to keep track of the robot's ping over time.

Note that the recorded ping is to an internet site, and will not necessarily reflect the ping to a remote operator.

## Configuration

The adapter requires the following configuration:

`hostname` - The hostname or IP address to ping.

`frequency` - The frequency at which to ping the host, in Hz.

`timeout` - The timeout for the ping, in seconds.

`stream` - The name of the stream to post the ping to.