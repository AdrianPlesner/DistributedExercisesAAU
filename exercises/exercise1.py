from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub
import random
import time

class GossipMessage(MessageStub):

    def __init__(self, sender: int, destination: int, secrets):
        super().__init__(sender, destination)
        # we use a set to keep the "secrets" here
        self.secrets = secrets

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.secrets}'


class CallMessage(MessageStub):

    def __init__(self, sender: int, destination: int, nr: int):
        super().__init__(sender, destination)
        self.nr = nr

    def __str__(self):
        return f'{self.source} -> {self.destination} nr: {self.nr}'


class Gossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])

    def get_calle(self):
        res = self.index()
        while res == self.index():
            res = random.randint(0, self.number_of_devices()-1)
        return res

    def run(self):
        # the following is your termination condition, but where should it be placed?
        while True:
            ingoing = self.medium().receive()
            if ingoing is None:
                call_to = self.get_calle()
                self.medium().send(CallMessage(self.index(), call_to, 0))
                wait = time.time()
                rand_tim = random.random() * 1.5
                while time.time() - wait < rand_tim and (ingoing is None or ingoing.source is not call_to):
                    ingoing = self.medium().receive()
                if ingoing is not None and type(ingoing) is CallMessage and ingoing.nr is 1:
                    self.medium().send(GossipMessage(self.index(), call_to, self._secrets))
                    ingoing = self.medium().receive()
                    while ingoing is None or ingoing.source is not call_to:
                        ingoing = self.medium().receive()
                    if type(ingoing) is GossipMessage:
                        for sec in ingoing.secrets:
                            if sec not in self._secrets:
                                self._secrets.add(sec)
                else:
                    self.medium().send(CallMessage(self.index(), call_to, -1))
            elif type(ingoing) is CallMessage and ingoing.nr is 0:
                caller = ingoing.source
                self.medium().send(CallMessage(self.index(), caller, 1))
                ingoing = self.medium().receive()
                while ingoing is None or ingoing.source is not caller:
                    ingoing = self.medium().receive()
                if type(ingoing) is GossipMessage:
                    for sec in ingoing.secrets:
                        if sec not in self._secrets:
                            self._secrets.add(sec)
                    self.medium().send(GossipMessage(self.index(), caller, self._secrets))

            if len(self._secrets) == self.number_of_devices():
                return

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')

