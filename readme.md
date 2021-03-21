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
    |   ├── requests_wrapper.py          <- requests class. wrappes all project's requests.
    |   ├── slack_bot_wrapper.py         <- 
    |   ├── twitter_wrapper.py           <- 
    |   └── config_wrapper.py            <- 
    └── configurations     
        ├── logging.yaml                 <- 
        ├── slack_configurations.yaml    <- 
        └── twitter_configurations.yaml  <- 

## Authors

* **Tony Schneider** - *Programming* - [TonySchneider](https://github.com/tonySchneider)
