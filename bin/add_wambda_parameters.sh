#!/bin/bash

set -e

REGION="ap-northeast-1"
PROFILE="shogi"

put_param() {
  aws ssm put-parameter --name "$1" --value "$2" --type String --region $REGION --profile $PROFILE --overwrite
}

put_param "/wambda/debug" "true"
put_param "/wambda/use_mock" "false"
put_param "/wambda/no_auth" "false"
put_param "/wambda/deny_signup" "false"
put_param "/wambda/deny_login" "false"
put_param "/wambda/log_level" "INFO"