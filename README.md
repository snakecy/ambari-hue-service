## Ambari Service for Hue
Ambari service for easily installing and managing Hue(v4.3.0) on HDP3.0 cluster. thanks for the author [Kyle Joe's](https://github.com/EsharEditor) basic work.


## Authors
For further adding features, the author [snakecy](https://github.com/snakecy) will continue to develop! 

Thanks to star. 

## Version
   + Hue 4.3.0
   + Ambari 2.7+
   + HDP 3.0

## Required
   - Python=2.7
   - Django=1.11
   - pycrypto >= 2.6.1
   - setuptools >= 36.5.0

## Others installed with yum
   - Refer to the dir 'yumrepos'

## Addition
   + Add restart


## HDFS HA mode
   - manual to install hadoop-httpfs service 
       - configure hdfs-site.xml
       

```
# sudo yum install hadoop-httpfs
```

   - start HttpFs

```
# sudo service hadoop-httpfs start
（or /usr/hdp/current/hadoop-httpfs/etc/rc.d/init.d/hadoop-httpfs start）
```


## Setup

#### Deploy Hue on existing cluster

- (Optional) To see Hue metrics in Ambari, login to Ambari (admin/admin) and start Ambari Metrics service
 
    http://$AMBARI_HOST:8080

- To download the Hue service folder, run below
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/HUE  
sudo git clone https://github.com/snakecy/ambari-hue-service.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/HUE
```

- Restart Ambari

```
service ambari-server restart
```
- Then you can add hue service as like the way of the other ambari components.
- The hue location will be set '/usr/local/hue' by default or as you like.
- One benefit to wrapping the component in Ambari service is that you can now monitor/manage this service remotely via REST API


```
export SERVICE=HUE
export PASSWORD=admin
export AMBARI_HOST=localhost
export CLUSTER=snakecy

#get service status
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X GET http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#start service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Start $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#stop service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#restart service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Restart $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

```

#### Configuring Cluster and HUE
We’ll need to reconfigure our HDFS, Hive (WebHcatalog, this feature has been removed in HUE v4.3.0), and Oozie services to take advantage of HUE’s features.

[tutorials from Hue](http://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/?replytocom=50032)


#### Hue Service Action
- UserSync: synchronize users from the current system or Ldap server
- DatabaseSync: synchronize metastore from SQLite
  
  ```
  ## migrate database
    # cd /usr/local/hue/build/env/bin/
    # hue syncdb 
    # hue migrate
  ```

#### Use Hue
- The Hue webUI login page should come up at the below link: 
http://$HUE_HOSTNAME:8888
![Image](./screenshots/hue.png?raw=true)
![Image](./screenshots/hue_conf.png?raw=true)

#### Remove service

- To remove the Hue service: 
  - Stop and delete the service via Ambari
  - Other way, unregister the service by running below from Ambari node
  
```
export SERVICE=HUE
export PASSWORD=admin
export AMBARI_HOST=localhost

#detect name of cluster
output=`curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari'  http://$AMBARI_HOST:8080/api/v1/clusters`
CLUSTER=`echo $output | sed -n 's/.*"cluster_name" : "\([^\"]*\)".*/\1/p'`

#unregister service from ambari
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X DELETE http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#if above errors out, run below first to fully stop the service
#curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
```

