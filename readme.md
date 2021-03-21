# Slack & Twitter Integration Bot (QM Exercise)

## Requirements

* python version >= 3.7.4
* see requirements.txt file that includes all necessary pip installations

## How to run? + install

* python3 -m pip install -r requirement.txt
* Fill the following keys at the slack and twitter configuration files that located in configurations folder:
  * TW:
    * access_token
    * access_token_secret
    * api_key
    * api_key_secret
    * personal_username
  * Slack:
    * bot_user_oauth_token
    * default_channel_id
* python3 client.py 2>qm_exercise.log

# Project Organization

    ├── requirements.txt   <- Requirements file (pip installations).
    │
    ├── client.py          <- Main file. This file executes the project.
    │
    |── wrappers           
    |   ├── requests_wrapper.py          <- wraps all project's requests.
    |   ├── slack_bot_wrapper.py         <- wraps all Slack api requests by using 'requests' lib.
    |   ├── twitter_wrapper.py           <- wraps all TW api requests by using tweepy (An external python lib).
    |   └── config_wrapper.py            <- loads the configurations files.
    └── configurations     
        ├── logging.yaml                 <- logging lib config
        ├── slack_configurations.yaml    <- slack configs
        └── twitter_configurations.yaml  <- tw configs

## Authors

* **Tony Schneider** - *Programming* - [TonySchneider](https://github.com/tonySchneider)
