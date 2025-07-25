class Node:
    def __init__(self, Id, name, kind):
        self.Id = Id
        self.name = name
        self.kind = kind

    def mongo_transform(self):
        return {
            "_id": self.Id,
            "name": self.name,
            "kind": self.kind,
        }
