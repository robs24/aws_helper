import boto3
import getpass
import os, sys
from pathlib import Path

def configureEnv():
  global awsEnvFile
  sys.tracebacklimit = 0
  awsEnvFile = Path('{}/.aws/.awsenv'.format(os.environ['HOME']))

def checkCreds(awsProfile):
  boto3.setup_default_session(
    profile_name=awsProfile
  )
  sts = boto3.client('sts')
  callerIdentity = sts.get_caller_identity()
  
  accountId = callerIdentity['Account']
  arn = callerIdentity['Arn']
  userId = callerIdentity['UserId']
  
  if accountId != None and arn != None and userId != None:
    print('''Credentials valid for the following account/user:
      AWS Profile: {}
      Account ID: {}
      ARN: {}
      User ID: {}'''.format(awsProfile, accountId, arn, userId))
    awsEnv = open(awsEnvFile, 'a')
    awsEnv.write('export AWS_PROFILE={};'.format(awsProfile))
    awsEnv.close()
    return
  else:
    raise Exception("Unhandled error with 'aws sts get-caller-identity'")

def unsetCreds():
  configureEnv()

  print('Unsetting all existing AWS_* credential-related environment variables')
  awsEnv = open(awsEnvFile, 'w+')
  awsEnv.write('''unset AWS_ACCESS_KEY_ID;
unset AWS_SECRET_ACCESS_KEY;
unset AWS_SESSION_TOKEN;
unset AWS_MFA_ACCESS_KEY_ID;
unset AWS_MFA_EXPIRY;
unset AWS_MFA_SECRET_ACCESS_KEY;
unset AWS_MFA_SESSION_TOKEN;
unset AWS_PROFILE;\n''')
  awsEnv.close()

def setCreds():
  configureEnv()

  if awsEnvFile.exists():
    os.remove(awsEnvFile)

  unsetCreds()
  awsProfile = input('Enter your AWS profile: ')
  checkCreds(awsProfile)

def authMfa():
  configureEnv()
  if os.environ.get('AWS_PROFILE'):
    awsProfile=os.environ.get('AWS_PROFILE')
    boto3.setup_default_session(
      profile_name=awsProfile
    )
    sts = boto3.client('sts')
    sts.get_caller_identity()

    if os.environ.get('AWS_SESSION_TOKEN'):
      raise Exception('ERROR: already using an STS token. You probably don\'t want to do MFA authentication at this stage - perhaps run \'aws_reset_creds\' to reset')
    else:
      iam = boto3.client('iam')
      mfaSerial = iam.list_mfa_devices()
      mfaToken = getpass.getpass('Enter the MFA token code for [{}]: '.format(awsProfile))
      
      sessionTokens = sts.get_session_token(
        DurationSeconds=28800,
        SerialNumber=mfaSerial['MFADevices'][0]['SerialNumber'],
        TokenCode=mfaToken
      )
      credentials = sessionTokens['Credentials']

      awsEnv = open(awsEnvFile, 'w+')
      awsEnv.write(f'''export AWS_ACCESS_KEY_ID="{credentials['AccessKeyId']}";
export AWS_SECRET_ACCESS_KEY="{credentials['SecretAccessKey']}";
export AWS_SESSION_TOKEN="{credentials['SessionToken']}";

export AWS_MFA_ACCESS_KEY_ID="{credentials['AccessKeyId']}";
export AWS_MFA_SECRET_ACCESS_KEY="{credentials['SecretAccessKey']}";
export AWS_MFA_SESSION_TOKEN="{credentials['SessionToken']}";
export AWS_MFA_EXPIRY="{credentials['Expiration']}";''')
      awsEnv.close()
      print('MFA succeeded. With great power comes great responsibility...')
  else:
    raise Exception('ERROR: current AWS credential configuration invalid. Did you forget to run \'awsSetCreds\'?')
