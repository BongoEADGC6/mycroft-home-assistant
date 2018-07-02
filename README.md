
# Home Assistant Skill for Mycroft

Due to my lack of time, this project has been taken up by https://github.com/btotharye/mycroft-homeassistant and is now the upstream repo. 

This is a skill to add [Home Assistant](https://home-assistant.io) support to
[Mycroft](https://mycroft.ai). Currently is supports turning on and off several
entity types (`light`, `switch`, `scene` and `input_boolean`).

## Installation

Clone the repository into your `~/.mycroft/skills` directory. Then install the
dependencies inside your mycroft virtual environment:

```
cd ~/.mycroft/skills
git clone https://gitlab.com/robconnolly/mycroft-home-assistant.git HomeAssistantSkill
workon mycroft
cd HomeAssistantSkill
pip install -r requirements.txt
```

## Configuration

Add a block to your `~/.mycroft/mycroft.conf` file like this:

```
  "HomeAssistantSkill": {
    "host": "hass.mylan.net",
    "password": "mysupersecrethasspass",
    "ssl": true|false
  }
```

NOTE: SSL support is currently insecure as it does not verify the cert. This means it will
work with a self signed cert, but shouldn't be used accross the internet.

You will then need to restart mycroft.

## Usage

Say something like "Hey Mycroft, turn on living room lights". Currently available commands
are "turn on" and "turn off". Matching to Home Assistant entity names is done by scanning
the HA API and looking for the closest matching friendly name. The matching is fuzzy (thanks
to the `fuzzywuzzy` module) so it should find the right entity most of the time, even if Mycroft
didn't quite get what you said.

## TODO

 * Implement SSL certificate verification
 * New intent for scene activation, e.g. "Mycroft, activate scene..."
 * New intent for opening/closing cover entities
 * New intent for locking/unlocking lock entities (with added security?)
 * ...

## Contributing

All contributions welcome:

 * Fork
 * Write code
 * Submit merge request

## Licence

See [`LICENCE`](https://gitlab.com/robconnolly/mycroft-home-assistant/blob/master/LICENSE).

