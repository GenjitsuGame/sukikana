#!/bin/bash

yum update -y
yum install -y python36

# add boot script which loads environment variables
cat > /etc/profile.d/export_instance_tags.sh << 'EndOfMessage'
# fetch instance info
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
INSTANCE_AZ=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)
INSTANCE_REGION="`echo \"$INSTANCE_AZ\" | sed -e 's:\([0-9][0-9]*\)[a-z]*\$:\\1:'`"

# export instance tags
export_statement=$(aws ec2 describe-tags --region "$INSTANCE_REGION" --filters "Name=resource-id,Values=$INSTANCE_ID" --query 'Tags[?!contains(Key, `Name`) && !contains(Key, `:`)].[Key,Value]' --output text | sed -E 's/^([^\s\t]+)[\s\t]+([^\n]+)$/export \1="\2"/g')
eval $export_statement

# export instance info
export INSTANCE_ID
export INSTANCE_AZ
export INSTANCE_REGION

# add more env variables here if needed

git clone https://github.com/GenjitsuGame/sukikana.git

pip-3.6 install -r sukikana/tasks/requirements.txt
