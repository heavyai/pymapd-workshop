SETUP KINESIS PRODUCER
======================
- Launch the Amazon Linux2 AMI which has the AWS CLI packages preinstalled.
- Services -> IAM -> Policies -> 
  select AmazonKinesisFullAccess 
  select CloudWatchFullAccess
  Service = EC2
  Actions = All EC2 actions

Create Policy -> JSON -> cut paste the json file -> Review Policy
 Name & Description
 Create Policy

Create Role -> EC2 -> Permissions -> Filter Policies 
  Specify the Policy name in Filter Policies
  select the policy you created
  Next: Tags
  Key=name Value=Kinesis_WS_Test
  Select Next

  Role Name = Kinesis_WS_Role_test1
  Create Role

  Instance -> Instance Settings -> Attach/Replace IAM Role -> select Role -> Apply

- Setup AWS configuration with access and secret key credentials
  aws configure
- Test if the AWS credentials are setup correctly by listing the user's S3 storage
  aws s3 ls

- Create a Kinesis Stream called bike-status with a single shard
  aws kinesis create-stream --stream-name bike-status --shard-count 1
  aws kinesis list-streams
  aws kinesis describe-stream --stream-name bike-status

- Install Kinesis Agent to create a producer
  sudo yum install –y https://s3.amazonaws.com/streaming-data-agent/aws-kinesis-agent-latest.amzn1.noarch.rpm

- Setup Kinesis Producer configuration file /etc/aws-kinesis/agent.json
  sudo vi /etc/aws-kinesis/agent.json
{ 
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "", 
  "firehose.endpoint": "",
  "flows": [
    { 
      "filePattern": "/tmp/kinesis/bike-status*",
      "kinesisStream": "bike-status",
      "partitionKeyOption": "RANDOM"
    }
  ]
}

- Start the Kinesis Agent and configure it to start at bootup
  sudo service aws-kinesis-agent start
  sudo service aws-kinesis-agent status
  sudo chkconfig aws-kinesis-agent on

- Monitor the Kinesis agent at /var/log/aws-kinesis-agent/aws-kinesis-agent.log
  
SETUP KINESIS CONSUMER
======================
- Setup the Kinesis Consumer on the same server or spin up another Amazon Linux2 instance.
- For the workshop we will spin up a single Linux instance for running both the producer and consumer.
- Use Anaconda distribution to setup python and install boto3 library for kinesis 
  consumer support and pymapd library for OmniSci API access.
  
- Install Anaconda
  wget https://repo.anaconda.com/archive/Anaconda3-2019.07-Linux-x86_64.sh
  chmod 755 Anaconda3-2019.07-Linux-x86_64.sh
  ./Anaconda3-2019.07-Linux-x86_64.sh
  conda install boto3
  conda install -c conda-forge pymapd

TEST STREAMING
==============
- Copy the list of bike status endpoints from S3.
  https://mapd-veda.s3-us-west-1.amazonaws.com/gbfs_endpoints.csv

- Start the python program to feed the Kinesis Producer with bike status data stream.
  python bikestream.py 

  The bikestream program will get the bike status from the various endpoints and write it to a CSV file
  /tmp/kinesis/bike-status-N.csv. Note that the producer configuration (json) is looking for data input 
  to files that match the /tmp/kinesis/bike-status* pattern.

- Start the python Kinesis consumer program that will read the data from the producer and create a Pandas 
  dataframe for 100 records at a time and write to the table bike-status on OmniSci.
  python streamconsumer.py

- Confirm that the Kinesis workflow is working using OmniSci Immerse data manager.

