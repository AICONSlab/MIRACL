class AutoGenerateFlagMap:
    """
    Sentinel indicating flag_map should be auto-generated from MiraclObj.flow
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "AUTOGENERATE"


AUTOGENERATE = AutoGenerateFlagMap()
