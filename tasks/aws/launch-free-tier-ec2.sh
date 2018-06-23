#!/bin/bash

aws ec2 run-instances --launch-template LaunchTemplateId=lt-087a4eaca7411cf7b --tag-specifications "ResourceType=instance,Tags=[{Key=label,Value='$1'}]"


