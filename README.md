# FixrAppBuilderFarm

## What is this GitHub Project?

Its our Full-Stack Cloud Service for the Fixr App Builder script. Before the technical blah blah blahs, lets 
take a look at a diagram that describes what it is:

<img src="build_farm.png" width="720" height="490">

This prototype system is our current attempt to scale up our Android app building operations. It is currently
a grease monkey jerry-rigged monstrosity, but hopefully in time, it will be polished and robust enough to be
extended to encompose other critical operations of the Fixr pipeline. But before we drift off to paradise, with
the magic unicorn, lets return to reality and the status quo: here's a brief lo-down on the Fixr App Builder Farm
pipeline:

* Batch/Incremental Jobs: The pipeline starts with a list of jobs, each representing a specific commit of a Android
application in a GitHub repository that we wish to be built. Jobs are uniquely identified by the triplet, user name
repository name and commit hash. Currently, the only way we invoke the pipeline, is by pushing the list of commit history
extracted from our Muse tool (https://github.com/kenbod/muse). Particularly, the latest and greatest copy of the
history.json file. Included in this project, is a simple Python script (details below) that converts entries of the
history.json file into jobs recognized by our Fixr App Builders. In future, we intend to feed incremental jobs from
active focused crawl data extracted from GitHub on a daily basis, but thats a story for another time.

* Redis Job Queue: Jobs for the App Builders are stored in Redis (http://redis.io/). It provide us semi-persistent
storage of job data and the ability to manage the scheduling of jobs to the app builder array. Current means to 
manipulate the job queue is basic (simple scripts to redis shell command line), but future plans will include implementing
an interactive job queue manager.

* Fixr App Buider Array: The main workhorses of this pipeline. This comprises of a cluster of computing nodes (currently 
OpenStack VMs) that does the actual building of Android apps. The key features of this pipeline is centralized storage of
build output, meta-data and logging information (Current deployment has no redundancies and fault tolerence, but can be
scaled up thanks to the technologies we are using). Build output (.jars, .classes and .apks) are stored in a file-system. 
It is shown as GFS in the diagram, but currently it is loaded in a local Cinder volume (due to OpenStack/GFS instability).
Meta-data of the build (build outcome, paths, apps, etc..) are stored in MongoDB, while build logs are stored in GrayLog
centralized logger, which has Elastic search as a backend.

* Builder Web Services: There is currently one main web service that is provide, the Fixr Build Query API service. It
provides a query interface intended for other Fixr tools to extract build information. In conjunction, we intend to 
implement a simple FTP service to allow Fixr tools to retrieve build outputs (Currently not deployed, but can easily
be done when need arises). 

For more details on this project, check out the slides at https://docs.google.com/presentation/d/1OaQXd3CWOb_4roxCP8z6_rJf45uhoOs8ehTfB9-hy-s/edit?usp=sharing

## Current Deployment Layout

The current deployoment layout is... well, bad. In an ideal world, each box (as well as cylinder) in the above diagram 
would correspond to an OpenStack VM. But due to limited resources and compounded by the instability of our OpenStack
cluster, the Fixr App Builder is currently deployed as follows on the following VMs:

* Fixr-App-Buider-Beta (192.12.242.242) in Muse Project: Running Redis Job Queue, MongoDB with build meta-data,
  attached with Cinder volume containing build outputs and running build query service. Also has x2 builder threads
  running.

* Loggermon-Alpha (192.12.242.231) in PL Project: Running the GrayLog centralized logger and x2 builder threads

* fixr_clustering_new (192.12.243.136) in PL Project: Running x2 builder threads

## Querying the Farm

More documentation for querying the farm will be added soon. But for now, try the following URL to poke at the query interface.

To retrieve a summary of the overall build results:

> http://192.12.242.242:8080/count/all/

To retrieve a pagination of passed (stats=ps) builds, starting from page 0 with 20 entries a page:

> http://192.12.242.242:8080/repo/?stats=ps&page=0&per_page=20

We need everyone's feedback on what kind of query interfaces are required for app building integration with your 
respective Fixr tools. Please feel free to submit requests/demands to edmund.lam@colorado.edu ! 

## Dependencies and Install/Deployment instructions

Deployment of the Fixr App Builder Farm is currently a rather involved process. Why shouldn't it be? Since it
comprises of several sub-components that are designed to span across multiple VMs. So before we have the time to upgrade this
with fancy Docker containers and elastic cloud integration, we've got this readme file and you, a capable and young(ish) Fixr 
human subject, to drive this wonderful process. We list the dependencies and deployment instructions organsized by
logical sub-components of this tool-chain. This project is mainly developed in Python, so the only stuff you'll
need to install are libraries. Note that with default port settings, it is possible to run this entire tool chain on a single 
VM/PC.

### Before you start

Get you favorite package management and auxiliary dev/support tools (e.g., apt-get, easy_install, pip, wget, make). 
This project was tested and deployed on Ubuntu 14.04 and 16.04, so if you have not noticed, instructions here
will be obviously Ubuntu-centric. But you are a capable and adaptable young person, you'll easily figure out
the equivalent tools on your favorite OS. This GitHub repository has a sub-module! So remember to recursively
clone it when you clone this repository, i.e.,

> git clone --recursive https://github.com/cuplv/FixrAppBuilderFarm.git

Also, note that in the following, we will report the default network ports in which the subcomponent uses. This can
of course be modified, but most importantly for web access of these sub-systems, the VM's security group must include
open ingres rules for these network ports. 

### Build Job Queue

Dependencies: Redis 3.2.3, Python 2.7, redis-py 2.10.5

- Install Redis as instructed at http://redis.io/download 
- apt-get Python 2.7 and easy_install (or pip) redis-py

At this point, you should be able to start a redis server and interact with it through Python shell.
See http://redis.io/documentation and https://pypi.python.org/pypi/redis for instructions on how to
use Redis and its Python bindings.

You should start Redis with basic password authentication, run the following in a screen:

> redis-server --requirepass (password)

The alternative is to create a Redis configuration file with this password requirement, and/or run redis server as an OS service.
Note that Redis' default port used is 6379.

### MongoDB Build Meta-Data Store

Dependencies: MongoDB 3.0.4, PyMongo 3.3.0

- apt-get mongodb and easy_install/pip pymongo .

You should configure MongoDB to (1) store its data in an appropriate volume and (2) Require authorized access.
To do this, modify the conf file, normally found in /etc/mongod.conf and restart the mongoDB server. You will
also need to create a MongoDB user which the Fixr App Builders can authenticate as (See https://docs.mongodb.com/manual/).
Default network port for MongoDB is 27017.

### GrayLog Central Logging Service

Dependencies: GrayLog 2.1.0, Java (>=8), MongoDB (>=2.4), ElasticSearch (>=2.x)

- Install the appropriate versions of Java, MongoDB and ElasticSearch (See http://docs.graylog.org/en/2.1/pages/installation/os/ubuntu.html)
- apt-get graylog-server (See http://docs.graylog.org/en/2.1/pages/installation/operating_system_packages.html)

Following the instructions in the GrayLog website, they are pretty complete. Once you have setup the server, you should be
able to enter the console, if you have expose the appropriate ports on your VM (default 9000).

### Fixr Build Query Service

Dependencies: Flask 0.11, MongoDB 3.0.4, PyMongo 3.3.0, Redis 3.2.3, Python 2.7, redis-py 2.10.5

- Install Redis and MongoDB dependencies, including Python libraries.
- Install Python Flask (See http://flask.pocoo.org/)
- Install Python modules pytz and graypy

At this point, you should be able to start the app builder query service. But before that, make sure your configuration file 
app_builder.ini is configured correctly (See .ini configurations below). Once configurations are done, run the following Python 
Flask script in the flaskService folder:

> python query_service.py

You can do this either on bare-metal on a screen (if you are ok getting hacked eventually), or behing your favorite web server (Apache, Ngix, etc..)
Default port is 8080.

### Fixr App Builder Service

Dependencies: MongoDB 3.0.4, PyMongo 3.3.0, Redis 3.2.3, Python 2.7, redis-py 2.10.5, Java (>=8), GitHub Repo Commandline tool and Search API Library,
Android SDKs/NDK (platform tools/tools and ALL sdks), Gradle (primary 2.14.1, plus ALL other versions)

- Install Redis and MongoDB dependencies, including Python libraries.
- Install latest Gradle (https://gradle.org/gradle-download/)

Remember to export the variable GRADLE_HOME pointing to the root of your Gradle path and add $GRADLE_HOME/bin to your PATH variable.

The above are the easy bits. There's still a number of things you'll need to do, particularly the following:

- Create symbolic link in flaskService folder to appbuilder folder in submodule FixrAppBuilder 
- Get and update Android SDKs and Android NDK
- Get GitHub commandline tool and search API library
- Get all versions of Gradle
- Setup some environment variables

Yes, that's a lot of things. One possibility is to follow the cookie crumbles found in this docker file (https://github.com/cuplv/FixrAppBuilder/blob/master/Dockerfile).
It contains most of these steps, but you'll need to mod it a little to work as raw shell bashing (not just blind cut and paste, you lazy brat.. =P). Alternatively,
try following the rest of the instructions.

Create a symbolic link in flaskService folder to appbuilder folder in submodule FixrAppBuilder. Simple, from flaskService, run the command:

> ln -s ../FixrAppBuilder/appbuilder appbuilder

Should work, but if you get the exception that ../FixAppBuilder/appbuilder does not exist, you probably did not download the FixrAppBuilder
submodule by adding the '--recursive' flag while cloning this GitHub repository. Please do this, and try again with the submodule. 
Next, you'll need the GitHub command line tools and search API libraries. apt-get the command line tool:

> sudo apt-get install git

Next, you'll need the GitHub search API library and Python bindings:

> wget https://github.com/libgit2/libgit2/archive/v0.24.0.tar.gz 
> tar xzf v0.24.0.tar.gz
> cd libgit2-0.24.0
> cmake .
> make 
> sudo make install
> pip install pygit2

Wonderful, that's it for GitHub. Now lets deal with the Android stuff. Get Android SDK and NDK by doing the following:

> wget http://dl.google.com/android/android-sdk_r24.4-linux.tgz
> tar -xvzf android-sdk_r24.4-linux.tgz

> wget https://dl.google.com/android/ndk/android-ndk-r9d-linux-x86_64.tar.bz2
> tar -xvjf android-ndk-r9d-linux-x86_64.tar.bz2

Take note of the root paths where you extracted these libraries to. You'll now need to export environment variables
ANDROID_HOME and ANDROID_SDK_HOME to the SDKs path, and ANDROID_NDK_HOME to the NDK path. Additionally, add
$ANDROID_SDK_HOME/tools , $ANDROID_SDK_HOME/platform-tools and $ANDROID_NDK_HOME to your PATH variable.

Once this is done, you are almost there.. but not yet. You need to update your Android SDK now, particularly install all
versions of the Android SDK and supporting libraries. Run the following commands:

> android update sdk -u -a -t 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52
> android update sdk -u -a -t 119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141
> android update sdk -u -a -t 153,154,155,156,157,158,159,160,161,162,163,164,165,166

One last step: you need to setup what's called the 'Local Gradle Farm'. Its our local repository of all
gradle versions and essentially a local implementation of the Gradle wrapper.. why do we need this? Long
story short, GitHub users are gits (http://www.merriam-webster.com/dictionary/git) and many don't even check in their gradle wrappers, so to build their
apps, we must implement the functionality of the Gradle wrapper. To set this up, first export variable
GRADLE_FARM_HOME pointing to a designated path to hold all Gradle binary libraries. Next run the bash script
'setup_gradle_farm.sh' found in this GitHub repo. This will download and copy all Gradle versions into the designated folder.
You won't need to export $GRADLE_FARM_HOME to your PATH variable, but you'll need it for configuring
app_builder.ini (see below).

You probably now have the necessary libraries to run the app builder service. However, before you do, you need to
check the configurations in app_builder.ini . Particularly, you need to point 'archivehost' and 'archivedir' to the
right destination, where build outputs should be uploaded to. You'll need to ensure that your VM can 'scp' files
to 'archivehost' (e.g., setup authorized key access). You will also need to set 'gradlefarmpath' to the folder
designated to contain all gradle versions (i.e., GRADLE_FARM_HOME above). Additional to all these, be sure that
redisOptions and dbOptions are set correctly: pointing to right instances of Redis and MongoDB, with the correct
authentication data. To run an app builder instance, use the following command in a screen:

> python builder_service.py -n (name_of_worker) -w (name_of_work_dir)

Flags -n and -w are optional and will override inputs for 'name' and 'workdir' in category buildOptions of the app_builder.ini
initialization file.

### .ini Configurations

Our Python server scripts in this project fetches configuration parameters from a default .ini file, app_builder.ini . The two main
Python server scripts are builder_services.py and query_services.py, both found in the folder flaskService.
These configurations are divided into several categories:

* dbOptions: MongoDB options. Here, we indicate the host name (host) and network port (port) of the MongoDB server storing 
Build Meta-data, as well as the appropriate username (user) and password (pwd). You should also indicate the name of the
MongoDB database (name).

* qServeOptions: Fixr App Builder Query service options. Here, we indicate the host name (host) and network port (port) that
the query service should use. Also include an optional name parameter as a name identifier for the centralized logs.

* redisOptions: Redis server options. Here, we indicate the host name (host) and network port (port) of the Redis
server that runs the Build Job Queue. We should also indicate the password to be used (pwd) and two entry points of
the Redis: 'jobs' indicates the name of the main job queue, while 'failed' indicates the name of the queue containing failed
jobs.

* buildOptions: Fixr App Builder service options. Here, we indicate the main working folder of the builder (workdir) and
whether or not its contains are to be removed after processing (removework). We also indicate the name of the builder (name)
and two other important configuration parameters: 'archivehost' and 'archivedir' indicates the host name and local path of
where build outputs are stored, while 'gradlefarmpath' indicates the local path where local gradle binaries (various versions) 
are stored.

* logOptions: Logging option to be used. 'logtype' indicate the type of logging to use. Currently supports graylog (default)
and filelog. For Graylog, you must specify the host name and port of the GrayLog service used, while standard file log
requires the 'filename'.


