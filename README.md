# awshelper

This module allows a user to establish a connection to AWS - for use with `awscli` - using MFA, simplifying the steps one would typically have to take.

Commands that are currently available for use are:

* setCreds - this will prompt for the AWS profile to use and set your `AWS_PROFILE` environment variable accordingly. It will also check to ensure the IAM user/creds are valid for use
* unsetCreds - this will unset all environment variables relating to AWS that have been set as part of these functions
* authMfa - this will prompt for a token - generated from either a hardware/virtual MFA appliance - and fetch a session token for use with AWS. This is then set as an environment variable for use with `awscli` 

## Getting Started

I've found it is best to configure a number of aliases as part of your `.bash_profile` (or similar) in order to utilise the script as easily as possible. These are as follows...

<pre>export PYTHONPATH=$PYTHONPATH:&lt&ltPATH TO DOWNLOADED FILE&gt&gt
alias awsSetCreds="python3 -c 'import awshelper; awshelper.setCreds()'; source $HOME/.aws/.awsenv 2>/dev/null; rm -f $HOME/.aws/.awsenv"
alias awsUnsetCreds="python3 -c 'import awshelper; awshelper.unsetCreds()'; source $HOME/.aws/.awsenv 2>/dev/null; rm -f $HOME/.aws/.awsenv"
alias awsAuthMfa="python3 -c 'import awshelper; awshelper.authMfa()'; source $HOME/.aws/.awsenv 2>/dev/null; rm -f $HOME/.aws/.awsenv"</pre>
