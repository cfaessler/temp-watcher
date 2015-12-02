import ConfigParser


class SettingsWrapper:
    def __init__(self):
        self.settings = ConfigParser.RawConfigParser()
        self.settings.read('../settings.cfg')
        self.update_settings()

    def update_settings(self):
        self.THRESHOLD = self.settings.getint('Global', 'THRESHOLD_DEGREES')
        self.HYSTERESIS = self.settings.getint('Global', 'HYSTERESIS')
        self.PUSHOVER_API_TOKEN = self.settings.get('Pushover', 'API_TOKEN')
        self.PUSHOVER_API_USER = self.settings.get('Pushover', 'API_USER')
        self.APP_KEY = self.settings.get('Global', 'SECRET_KEY')
