willie_modules
==============

Modules for willie (our IRC bot)

Installing
----------

  1. Clone the repository
  2. Put the path to the repository in willie's `default.cfg` (usually stored in `~/.willie/default.cfg` in the `[core]` section:
     
     Like so:
     ```
     extra = /home/sam/dev/willie/willie_modules
     ```
  3. Install the dependencies: `pip install -r requirements.txt`
  4. Configure the modules (their configurationm will go in `default.cfg`


logger
------

Logger will log everything to a log server.

**Config section:** `[logger]`

**Config Variables**

  * `channels` - a list of the channels to log. This is a subset of `[core]`.`channels` and if not defind will default to all channels willie is currently in.
  * `base_url` - the url where these logs will go - *REQUIRED*
  * `api_key` - the api key for connecting to the log server - *REQUIRED*