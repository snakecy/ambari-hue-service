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
reload(sys)
sys.setdefaultencoding('utf8')
from resource_management import *
from subprocess import call
from setup_hue import setup_hue
from common import download_hue

class HueServer(Script):
  """
  Contains the interface definitions for methods like install, 
  start, stop, status, etc. for the Hue Server
  """
  def install(self, env):
    # Import properties defined in -config.xml file from params class
    import params
    env.set_params(params)
    self.install_packages(env)
    Logger.info(format("Downloading Hue Service"))
    download_hue()

  def configure(self, env):
    import params
    env.set_params(params)
    setup_hue()
    
  def start(self, env):
    import params
    self.stop(env)
    self.configure(env)
    Execute('chown -R -v hue:hue {hue_log_dir}')
    Execute('cd /user/local/hue && source ./build/env/bin/activate')
    Execute(format("nohup {hue_bin_dir}/supervisor >> {hue_log_file} 2>&1 &"),
          environment={'JAVA_HOME': params.java_home, 
                      'HADOOP_CONF_DIR': params.hadoop_conf_dir, 
                      'SPARK_HOME': '/usr/hdp/current/spark-client',
                      'PATH': '$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin'
          },
          user=params.hue_user
    )
    Execute ('ps -ef | grep hue | grep supervisor | grep -v grep | grep -v nohup | awk \'{print $2}\' > ' + params.hue_server_pid_file, user=params.hue_user)
#    Execute ('ps -ef | grep hue | grep runcherrypyserver | grep -v grep | grep -v nohup | awk \'{print $2}\' > ' + params.hue_server_pid_file, user=params.hue_user)

  def stop(self, env):
    import params
    env.set_params(params)
    # Kill the process of Hue
    Execute ('ps -ef | grep hue | grep -v grep | awk  \'{print $2}\' | xargs kill -9', user=params.hue_user, ignore_failures=True)
    File(params.hue_server_pid_file,
      action = "delete",
      owner = params.hue_user
    )

  def status(self, env):
    import status_params
    env.set_params(status_params)
    #use built-in method to check status using pidfile
    check_process_status(status_params.hue_server_pid_file)

  def usersync(self, env):
    import params
    env.set_params(params)
    if params.usersync_enabled:
      if params.usersync_source == 'unix':
        Execute ('{0}/hue useradmin_sync_with_unix --min-uid={1} --max-uid={2} --min-gid={3} --max-gid={4}'.format(params.hue_bin_dir, params.usersync_unix_minUserId, params.usersync_unix_maxUserId, params.usersync_unix_minGroupId, params.usersync_unix_maxGroupId), user=params.hue_user)
      else:
        Execute ('{0}/hue sync_ldap_users_and_groups'.format(params.hue_bin_dir), user=params.hue_user)
    else:
      Logger.info("Hue UserSync is disabled >> " + params.hue_log_file)

  def metastoresync(self, env):
    import params
    env.set_params(params)
    if params.metastore_db_flavor != 'sqlite3':
      Execute (format("{hue_bin_dir}/hue syncdb --noinput"), user=params.hue_user)
      Execute (format("{hue_bin_dir}/hue migrate"), user=params.hue_user)
    else:
      Logger.info("echo Hue Metastore is stored in $HUE/desktop/desktop.db >> " + params.hue_log_file)
  def restart(self, env):
    self.configure(env)
    print "restart HUE"
    self.stop(env)
    self.start(env)

if __name__ == "__main__":
  HueServer().execute()
