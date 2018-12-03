#!/usr/bin/env python

"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys, os, pwd, grp, signal, time
from resource_management import *
from subprocess import call
from common import *

def setup_hue():
  import params
  import status_params
  Logger.info("Configure Hue Service")
  # create the pid and log dir
  Directory([params.hue_log_dir, params.hue_pid_dir],
        mode=0755,
        cd_access='a',
        owner=params.hue_user,
        group=params.hue_group,
        create_parents=True
  )
  File([params.hue_log_file, params.hue_server_pid_file],
    mode=0644,
    owner=params.hue_user,
    group=params.hue_group,
    content=''
  )
  ## Delete from HDP3.0 && HUE4.3.0 
  #Logger.info("Creating symlinks /usr/hdp/current/hadoop-client/lib/hue-plugins-4.3.0-SNAPSHOT.jar")
  #Link("{0}/desktop/libs/hadoop/java-lib/*".format(params.hue_dir),to = "/usr/hdp/current/hadoop-client/lib")
  Execute('find {0} -iname "*.sh" | xargs chmod +x'.format(params.service_packagedir))
  # Create a home directory for solr user on HDFS
  params.HdfsResource(params.hue_hdfs_home_dir,
                type="directory",
                action="create_on_execute",
                owner=params.hue_user,
                mode=0755,
                recursive_chmod=True
  )
  Logger.info(format("Creating {hue_conf_dir}/log.conf file"))
  File(format("{hue_conf_dir}/log.conf"), 
    content = InlineTemplate(params.hue_log_content), 
    owner = params.hue_user
  )
  Logger.info(format("Creating {hue_conf_dir}/pseudo-distributed.ini config file"))
  File(format("{hue_conf_dir}/pseudo-distributed.ini"), 
    content = InlineTemplate(params.hue_pseudodistributed_content), 
    owner = params.hue_user
  )
  Logger.info(format("Run the script file to add configurations"))
  if params.hue_hdfs_module_enabled == 'Yes':
    add_hdfs_configuration(params.has_ranger_admin, params.security_enabled)
  if params.hue_hbase_module_enabled == 'Yes':
    add_hbase_configuration(params.has_ranger_admin, params.security_enabled)
  if params.hue_hive_module_enabled == 'Yes':
    add_hive_configuration(params.has_ranger_admin, params.security_enabled)
  if params.hue_oozie_module_enabled == 'Yes':
    add_oozie_configuration(params.has_ranger_admin, params.security_enabled)
  if params.hue_spark_module_enabled == 'Yes':
    add_spark_configuration(params.has_ranger_admin, params.security_enabled)

    
    	

