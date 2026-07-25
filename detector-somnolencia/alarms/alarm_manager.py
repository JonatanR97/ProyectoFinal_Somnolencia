from alarms.sound_alarm import SoundAlarm


class AlarmManager:
    def __init__(self) -> None:
        self.alarm = SoundAlarm()
        self.is_active = False

    def update(self, alert_active: bool) -> None:
        if alert_active and not self.is_active:
            self.alarm.start()
            self.is_active = True

        elif not alert_active and self.is_active:
            self.alarm.stop()
            self.is_active = False

    def stop(self) -> None:
        self.alarm.stop()
        self.is_active = False