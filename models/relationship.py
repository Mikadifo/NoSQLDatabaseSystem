class Relationship:
    def __init__(self, source, metaedge, target):
        self.source = source
        self.metaedge = metaedge
        self.target = target

    def mongo_transform(self):
        return {
                "source": self.source,
                "metaedge": self.metaedge,
                "target": self.target
        }
