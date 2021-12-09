class Node(object):
    def __init__(self, data, Next = None):
        self.data = data
        self.next = Next

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def getNext(self):
        return self.next

    def setNext(self, newNext):
        self.next = newNext
        if newNext is not None:
            self.data.nextRound = newNext
        


class LinkedList(object):
    def __init__(self):
        self.head = None

    def add(self, element):
        temp = Node(element)
        if self.head is not None:
            self.head.setNext(temp)
        self.head = temp

    def size(self):
        current = self.head
        count = 0
        while current != None:
            count = count + 1
            current = current.getNext()
        return count