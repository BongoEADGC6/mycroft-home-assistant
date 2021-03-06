from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from os.path import dirname, join
from requests import get, post
from fuzzywuzzy import fuzz
import json

__author__ = 'robconnolly'
LOGGER = getLogger(__name__)


class HomeAssistantClient(object):
    def __init__(self, host, password, port=8123, ssl=False):
        self.ssl = ssl
        if self.ssl:
            self.url = "https://%s:%d" % (host, port)
        else:
            self.url = "http://%s:%d" % (host, port)
        self.headers = {
            'x-ha-access': password,
            'Content-Type': 'application/json'
        }

    def find_entity(self, entity, types):
        if self.ssl:
            req = get("%s/api/states" % self.url, headers=self.headers, verify=False)
        else:
            req = get("%s/api/states" % self.url, headers=self.headers)

        if req.status_code == 200:
            best_score = 0
            best_entity = None
            for state in req.json():
                try:
                    if state['entity_id'].split(".")[0] in types:
                        LOGGER.debug("Entity Data: %s" % state)
                        score = fuzz.ratio(entity, state['attributes']['friendly_name'].lower())
                        if score > best_score:
                            best_score = score
                            best_entity = { "id": state['entity_id'],
                                            "dev_name": state['attributes']['friendly_name'],
                                            "state": state['state'] }
                except KeyError:
                    pass
            return best_entity

        return None

    def execute_service(self, domain, service, data):
        if self.ssl:
            post("%s/api/services/%s/%s" % (self.url, domain, service), headers=self.headers, data=json.dumps(data), verify=False)
        else:
            post("%s/api/services/%s/%s" % (self.url, domain, service), headers=self.headers, data=json.dumps(data))

# TODO - Localization
class HomeAssistantSkill(MycroftSkill):
    def __init__(self):
        super(HomeAssistantSkill, self).__init__(name="HomeAssistantSkill")
        self.ha = HomeAssistantClient(self.config.get('host'),
            self.config.get('password'), ssl=self.config.get('ssl', False))

    def initialize(self):
        self.load_vocab_files(join(dirname(__file__), 'vocab', self.lang))
        self.load_regex_files(join(dirname(__file__), 'regex', self.lang))
        self.__build_lighting_intent()

    def __build_lighting_intent(self):
        intent = IntentBuilder("LightingIntent").require("LightActionKeyword").require("Action").require("Entity").build()
        # TODO - Locks, Temperature, Identity location
        self.register_intent(intent, self.handle_lighting_intent)

    def handle_lighting_intent(self, message):
        entity = message.data["Entity"]
        action = message.data["Action"]
        LOGGER.debug("Entity: %s" % entity)
        LOGGER.debug("Action: %s" % action)
        ha_entity = self.ha.find_entity(entity, ['light', 'switch', 'scene', 'input_boolean'])
        if ha_entity is None:
            #self.speak("Sorry, I can't find the Home Assistant entity %s" % entity)
            self.speak_dialog('homeassistant.device.unknown', data={"dev_name": ha_entity['dev_name']})
            return
        ha_data = {'entity_id': ha_entity['id']}

        if action == "on":
            if ha_entity['state'] == action:
                self.speak_dialog('homeassistant.device.already',\
                        data={ "dev_name": ha_entity['dev_name'], 'action': action })
            else:
                self.speak_dialog('homeassistant.device.on', data=ha_entity)
                self.ha.execute_service("homeassistant", "turn_on", ha_data)
        elif action == "off":
            if ha_entity['state'] == action:
                self.speak_dialog('homeassistant.device.already',\
                        data={"dev_name": ha_entity['dev_name'], 'action': action })
            else:
                self.speak_dialog('homeassistant.device.off', data=ha_entity)
                self.ha.execute_service("homeassistant", "turn_off", ha_data)
        elif action == "dim":
            if ha_entity['state'] == "off":
                self.speak_dialog('homeassistant.device.off', data={"dev_name": ha_entity['dev_name']})
                self.speak("Can not dim %s. It is off." % ha_entity['dev_name'])
            else:
                #self.speak_dialog('homeassistant.device.off', data=ha_entity)
                self.speak("Dimmed the %s" % ha_entity['dev_name'])
                #self.ha.execute_service("homeassistant", "turn_off", ha_data)
        elif action == "brighten":
            if ha_entity['state'] == "off":
                self.speak_dialog('homeassistant.device.off', data={"dev_name": ha_entity['dev_name']})
                self.speak("Can not brighten %s. It is off." % ha_entity['dev_name'])
            else:
                #self.speak_dialog('homeassistant.device.off', data=ha_entity)
                self.speak("Increased brightness of %s" % ha_entity['dev_name'])
                #self.ha.execute_service("homeassistant", "turn_off", ha_data)
        else:
            ##self.speak("I don't know what you want me to do.")
            self.speak_dialog('homeassistant.error.sorry')

    def stop(self):
        pass


def create_skill():
    return HomeAssistantSkill()
