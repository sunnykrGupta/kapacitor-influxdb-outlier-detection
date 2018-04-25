
#### Resources used in this repository
- https://portal.influxdata.com/downloads#kapacitor
- https://hub.docker.com/_/kapacitor/
- https://docs.influxdata.com/kapacitor/v1.4/introduction/getting-started/
- https://docs.influxdata.com/kapacitor/v1.4/tick/expr/
- https://docs.influxdata.com/kapacitor/v1.4/nodes/alert_node/#slack

#### Setup kapacitor with Influxdb for demonstration

In this repository, we are using docker container for all our demostration. We are going to run all containers in same docker network for easy networking.
Docker's built-in service discovery capability. In order to do so, we'll first create a new network:
```
$ docker network create influxdb
```


Subscriptions is a feature available in InfluxDB that allow db to push data to Kapacitor for faster alerting instead of requiring Kapacitor to pull data from InfluxDB.

-------------------------------------------

#### Influxdb

InfluxDB is used as a data store for any use case involving large amounts of timestamped data, including DevOps monitoring, application metrics, IoT sensor data, and real-time analytics. Conserve space on your machine by configuring InfluxDB to keep data for a defined length of time, automatically expiring & deleting any unwanted data from the system. InfluxDB also offers a SQL-like query language for interacting with data.

we'll start our container named influxdb:

> If you want to run custom configuration for influxdb, a good reading is available.
> https://blog.laputa.io/try-influxdb-and-grafana-by-docker-6b4d50c6a446
> Generate the default configuration file:

```
$ docker run --rm influxdb influxd config > influxdb.conf
```
For running default InfluxDB container, skip above steps and run
```
$ docker run -d --name=influxdb \
        --net=influxdb \
        -p 8086:8086 \
        influxdb
```

#### Telegraf
It is part of the TICK stack and is a plugin-driven server agent for collecting and reporting metrics. Telegraf has plugins or integrations to source a variety of metrics directly from the system it’s running on, pull metrics from third-party APIs, or even listen for metrics via a StatsD and Kafka consumer services. It also has output plugins to send metrics to a variety of other datastores, services, and message queues, including InfluxDB, Graphite, OpenTSDB, Datadog, Librato, Kafka, MQTT, NSQ, and many others.

https://hub.docker.com/_/telegraf/

First, generate a sample configuration and save it as telegraf.conf on the host:
```
$ docker run --rm telegraf telegraf config > telegraf.conf
```
Activate telegraf for reading local system CPU and sending to influxDB
```
[agent]
  ## Default data collection interval for all inputs
  interval = "10s"

# Configuration for influxdb server to send metrics to
[[outputs.influxdb]]
  ## The full HTTP or UDP URL for your InfluxDB instance.
  ##
  ## Multiple urls can be specified as part of the same cluster,
  ## this means that only ONE of the urls will be written to each interval.

  # urls = ["udp://127.0.0.1:8089"] # UDP endpoint example
  urls = ["http://influxdb:8086"] # required

  ## The target database for metrics (telegraf will create it if not exists).
  database = "telegraf" # required
...
###############################################################################
#                            INPUT PLUGINS                                    #
###############################################################################

# Read metrics about cpu usage
[[inputs.cpu]]
  ## Whether to report per-cpu stats or not
  percpu = true
  ## Whether to report total system cpu stats or not
  totalcpu = true
  ## If true, collect raw CPU time metrics.
  collect_cpu_time = false
  ## If true, compute and report the sum of all non-idle CPU states.
  report_active = false
```

After modification of telegraf.conf file, run the telegraf docker

```
$ docker run -d --name=telegraf \
      --net=influxdb \
      -v $PWD/telegraf.conf:/etc/telegraf/telegraf.conf:ro \
      telegraf

Check logs to confirm runtime
$ docker logs -f telegraf
```

InfluxDB and Telegraf are now running and listening on localhost.

Wait about a minute for Telegraf to supply a small amount of system metric data to InfluxDB.
Then, confirm that InfluxDB has the data that Kapacitor will use.

This can be achieved with the following query:
```
$ curl -G 'http://localhost:8086/query?db=telegraf' --data-urlencode 'q=SELECT mean(usage_idle) FROM cpu'
```


#### Exploring influxdb

```
$ docker run --rm  -it --network=influxdb influxdb influx -host influxdb
Connected to http://influxdb:8086 version 1.5.2
InfluxDB shell version: 1.5.2

> show DATABASES;
name: databases
name
----
_internal
telegraf

> use telegraf;
Using database telegraf

> SHOW MEASUREMENTS;
name: measurements
name
----
cpu
disk
diskio
kernel
mem
processes
swap
system
> select * from cpu limit 10;
name: cpu
time                cpu       host         usage_guest usage_guest_nice usage_idle        usage_iowait        usage_irq usage_nice          usage_softirq       usage_steal usage_system       usage_user
----                ---       ----         ----------- ---------------- ----------        ------------        --------- ----------          -------------       ----------- ------------       ----------
1524062950000000000 cpu-total 79c75edd8367 0           0                95.60191002764282 0.12565971349580513 0         0                   0.05026388539832205 0           1.0429756220137538 3.179190751463584
1524062950000000000 cpu0      79c75edd8367 0           0                96.09218436889321 0                   0         0                   0.10020040080140688 0           0.9018036072149402 2.905811623233965
1524062950000000000 cpu1      79c75edd8367 0           0                93.07923771311687 0.10030090270802144 0         0                   0.2006018054160429  0           1.0030090270802143 5.6168505516492
1524062950000000000 cpu2      79c75edd8367 0           0                94.56740442658447 0.30181086519123707 0         0                   0.10060362173034088 0           2.0120724346068175 3.018108651905651
1524062950000000000 cpu3      79c75edd8367 0           0                96.67338709679268 0.30241935483848786 0         0                   0.1008064516131158  0           0.9072580645177557 2.016129032265754
1524062950000000000 cpu4      79c75edd8367 0           0                96.58291457282779 0.10050251256267857 0         0                   0                   0           1.0050251256267857 2.3115577889576033
1524062950000000000 cpu5      79c75edd8367 0           0                95.96774193543477 0                   0         0                   0                   0           0.9072580645170902 3.1249999999931237
1524062950000000000 cpu6      79c75edd8367 0           0                95.96774193550516 0.10080645161297254 0         0                   0                   0           0.7056451612920971 3.2258064516105374
1524062950000000000 cpu7      79c75edd8367 0           0                95.98393574299345 0                   0         0                   0                   0           0.8032128514049623 3.2128514056198494
1524062960000000000 cpu-total 79c75edd8367 0           0                90.12843112563401 0.35255603122645723 0         0.01259128682949588 0.20146058927193408 0           2.8456308234666414 6.459330143524802
```


#### Kapacitor
Kapacitor is a native data processing engine in the [TICK Stack](https://www.influxdata.com/time-series-platform/). It can process both stream and batch data from InfluxDB. It lets you plug in your own custom logic or user-defined functions to process alerts with dynamic thresholds, match metrics for patterns, compute statistical anomalies, and perform specific actions based on these alerts like dynamic load rebalancing. It also integrates with HipChat, OpsGenie, Alerta, Sensu, PagerDuty, Slack, and [more](https://www.influxdata.com/products/integrations/).

https://hub.docker.com/_/kapacitor/

Start the Kapacitor container with the container hostname matching the container name
so Kapacitor can automatically create subscriptions correctly and with the
KAPACITOR_INFLUXDB_0_URLS_0  value set to point at InfluxDB.
```
$ docker run -d -p 9092:9092 \
    --name=kapacitor \
    -h kapacitor \
    --net=influxdb \
    -e KAPACITOR_INFLUXDB_0_URLS_0=http://influxdb:8086 \
    -v $PWD/kapacitor.conf:/etc/kapacitor/kapacitor.conf:ro \
    kapacitor
```

The default Kapacitor configuration file is unpacked to /etc/kapacitor/kapacitor.conf.
A copy of the current configuration can be extracted from the Kapacitor daemon as follows:
```
$ docker run --rm  -it --network=influxdb kapacitor kapacitord config > kapacitor.conf
```
Kapacitor has an HTTP API with which all communication happens.
The kapacitor client application exposes the API over the command line.

Now use this CLI tool to define the task and the database—including retention policy—that it can access. Run another container linked to the kapacitor container for using the client and define tickscripts.

We have a script called `cpu_alert.tick` defined to fire alert events whenever conditions are met. To define tickScript run :

```
$ docker run --rm  -it --network=container:kapacitor \
        -v $PWD/cpu_alert.tick:/root/cpu_alert.tick:ro \
        kapacitor kapacitor define cpu_alert -tick /root/cpu_alert.tick

$  docker run --rm  -it --network=container:kapacitor kapacitor kapacitor list tasks
ID        Type      Status    Executing Databases and Retention Policies
cpu_alert stream    disabled  false     ["telegraf"."autogen"]


View details about the task using the show command.
$ docker run --rm  -it --network=container:kapacitor kapacitor kapacitor show cpu_alert

ID: cpu_alert
Error:
Template:
Type: stream
Status: disabled
Executing: false
Created: 18 Apr 18 18:05 UTC
Modified: 18 Apr 18 18:05 UTC
LastEnabled: 01 Jan 01 00:00 UTC
Databases Retention Policies: ["telegraf"."autogen"]
TICKscript:
dbrp "telegraf"."autogen"

stream
    // Select just the cpu measurement from our example database.
    |from()
        .measurement('cpu')
    |alert()
        .crit(lambda: int("usage_idle") < 95)
        // Whenever we get an alert write it to a file.
        .log('/tmp/alerts.log')

DOT:
digraph cpu_alert {
stream0 -> from1;
from1 -> alert2;
}
```
----------------------------------------
Kapacitor now knows how to trigger the alert. However, nothing is going to happen until the task has been enabled.
Before being enabled it should first be tested to ensure that it does not do spam the log files or communication channels with alerts. Record the current data stream for a bit so it can be used to test the new task:
```
#wait for 60s to record
$ kapacitor record stream -task cpu_alert -duration 60s

$ docker run --rm  -it --network=container:kapacitor kapacitor kapacitor record stream -task cpu_alert -duration 60s
> 9a3e9069-b7ee-48ea-a0be-75e720a4c2c0

#Save ID to run tickscript against the recorded events
$ rid=9a3e9069-b7ee-48ea-a0be-75e720a4c2c0
$ echo $rid

# Confirm that the recording captured some data. Run
$ kapacitor list recordings
$ kapacitor list recordings $rid

$ docker run --rm  -it --network=container:kapacitor kapacitor kapacitor list recordings $rid
ID                                   Type    Status    Size      Date
9a3e9069-b7ee-48ea-a0be-75e720a4c2c0 stream  finished  2.6 kB    18 Apr 18 18:15 UTC
```
With a snapshot of data recorded from the stream, that data can then be replayed to the new task. The replay action replays data only to a specific task. This way the task can be tested in complete isolation:
```
$ kapacitor replay -recording $rid -task cpu_alert

$ docker run --rm -it --network=container:kapacitor kapacitor kapacitor replay -recording $rid -task cpu_alert
c9dc56b1-64b3-4f84-918a-c0edb9520aec
```
Check the log using the command below. The file should contain lines of JSON, where each line represents one alert.
The JSON line contains the alert level and the data that triggered the alert.
```
$ cat /tmp/alerts.log

#Copy logs from docker to host for inspect
$ docker cp kapacitor:/tmp/alerts.log .

#Enable the task, so it can start processing the live data stream, with:
$ kapacitor enable cpu_alert
#Now alerts will be written to the log in real time.
```


####  Troubleshoot using continuous logs from Kapacitor container
```
docker logs -f kapacitor 2>&1 | grep "cpu_alert"
```
