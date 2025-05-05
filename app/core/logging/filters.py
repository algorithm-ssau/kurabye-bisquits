from logging import Filter

class ColorFilter(Filter):
    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED",
    }

    def filter(self, record):
        record.color = ColorFilter.COLOR[record.levelname]
        return True


class SensitiveWordsFilter(Filter):

    SENSITIVE_WORDS: set[str] = {'phone', 'password', 'passport',}

    def filter(self, record):
        return not any(word.lower() in record.msg.lower() for word in SensitiveWordsFilter.SENSITIVE_WORDS)

