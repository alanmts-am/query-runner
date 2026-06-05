class Result:
    def __init__(self, data: any, columns: list, collected: bool, error: str | None = None):
        self.data = data
        self.columns = columns
        self.collected = collected
        self.error = error
