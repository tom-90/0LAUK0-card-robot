from __future__ import annotations
from game.input import GameInput
from game.cards import Card
from pesten.types import PestenInputType
from pesten.state import PestenGameState
import threading
from ultralytics.yolo.v8 import detect
import os
from webcam import WebcamSource
import numpy as np
from enum import Enum

suit_map = {
    "r": 1, # Diamonds/ruiten
    "h": 2, # Hearts/harten
    "s": 3, # Spades/schoppen
    "k": 4  # Clubs/klaveren
}

rank_map = {
    "a": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "b": 11,
    "v": 12,
    "h": 13
}

class ClassType(Enum):
    H10 = "h10"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    H6 = "h6"
    H7 = "h7"
    H8 = "h8"
    H9 = "h9"
    HA = "ha"
    HB = "hb"
    HH = "hh"
    HV = "hv"
    J = "j"
    K10 = "k10"
    K2 = "k2"
    K3 = "k3"
    K4 = "k4"
    K5 = "k5"
    K6 = "k6"
    K7 = "k7"
    K8 = "k8"
    K9 = "k9"
    KA = "ka"
    KB = "kb"
    KH = "kh"
    KV = "kv"
    R10 = "r10"
    R2 = "r2"
    R3 = "r3"
    R4 = "r4"
    R5 = "r5"
    R6 = "r6"
    R7 = "r7"
    R8 = "r8"
    R9 = "r9"
    RA = "ra"
    RB = "rb"
    RH = "rh"
    RV = "rv"
    S10 = "s10"
    S2 = "s2"
    S3 = "s3"
    S4 = "s4"
    S5 = "s5"
    S6 = "s6"
    S7 = "s7"
    S8 = "s8"
    S9 = "s9"
    SA = "sa"
    SB = "sb"
    SH = "sh"
    SV = "sv"
    PILE_FACE_DOWN = "pile-face-down"
    PILE_FACE_UP = "pile-face-up"

    def is_card(self):
        return self != ClassType.PILE_FACE_DOWN and self != ClassType.PILE_FACE_UP

    def to_card(self):
        assert self.is_card(), "Cannot convert non-card type to card"

        if self == ClassType.J:
            return Card(0, 0)

        for rank in rank_map:
            for suit in suit_map:
                if self.value == suit + rank:
                    return Card(rank_map[rank], suit_map[suit])

        raise Exception("Invalid card type")
        

class Box():
    ROLLING_AVERAGE_LENGTH = 20
    DISTANCE_THRESHOLD = 100
    CONFIDENCE_THRESHOLD = 0.7
    REMOVAL_THRESHOLD = 0.4
    SIGNIFICANT_CONFIDENCE_CHANGE = 0.1

    confs: list[float]
    type: ClassType

    def __init__(self, conf: float, type: ClassType, xyxy: np.ndarray):
        self.confs = []
        self.type = type
        self.update(conf, xyxy)
    
    def update(self, conf: float, xyxy: np.ndarray = None):
        if xyxy is not None:
            self.p1 = xyxy[0, 0:2]
            self.p2 = xyxy[0, 2:4]

        old_confidence = self.confidence

        self.confs.append(conf)
        if len(self.confs) > Box.ROLLING_AVERAGE_LENGTH:
            self.confs.pop(0)

        return abs(self.confidence - old_confidence) > Box.SIGNIFICANT_CONFIDENCE_CHANGE

    def should_remove(self):
        return len(self.confs) >= Box.ROLLING_AVERAGE_LENGTH and self.confidence < Box.REMOVAL_THRESHOLD

    def should_include(self):
        return self.confidence > Box.CONFIDENCE_THRESHOLD

    def is_same(self, xyxy: np.ndarray, type: ClassType):
        # Check if the provided xyxy is close enough to the stored p1 and p2 points and types match
        return self.type == type and np.linalg.norm(self.p1 - xyxy[0, 0:2]) < Box.DISTANCE_THRESHOLD and np.linalg.norm(self.p2 - xyxy[0, 2:4]) < Box.DISTANCE_THRESHOLD

    @property
    def confidence(self):
        return sum(self.confs) / Box.ROLLING_AVERAGE_LENGTH

class CameraInput(GameInput):
    state: PestenGameState
    boxes: list[Box]
    change_event: threading.Event

    def __init__(self, state):
        super().__init__(state)

        self.boxes = []
        self.change_event = threading.Event()

        self.register(PestenInputType.READ_TOP_CARD, self.get_top_card)
        self.register(PestenInputType.READ_DRAWN_CARD, self.get_drawn_card)
        self.register(PestenInputType.WAIT_FOR_SHUFFLE, self.wait_for_shuffle)
        self.register(PestenInputType.WAIT_FOR_TOP_CARD, self.wait_for_top_card)
        self.register(PestenInputType.WAIT_FOR_PLAY_OR_DRAW, self.wait_for_play_or_draw)

        self.thread = threading.Thread(target=self.run_predictor)
        self.thread.daemon = True # Stop thread when main thread stops
        self.thread.start()

    def run_predictor(self):
        predictor = detect.DetectionPredictor(overrides={
            'show': True,
            'save': False,
            'verbose': False,
            'model': os.path.abspath(os.path.join(os.path.realpath(__file__), '../../../../model/best_weights.pt'))
        })
        print(os.path.abspath(os.path.join(os.path.realpath(__file__), '../../../../model/best_weights.pt')))

        # The predictor function will keep predicting and returning values as we go
        for data in predictor(WebcamSource(os.getenv('WEBCAM_SOURCE'), os.getenv('WEBCAM_RESOLUTION'), predictor), stream=True):
            # data contains all predictions made in the current frame/image from the webcam

            data = data.to("cpu") # Move data to CPU

            changed = False
            boxes: list[Box] = []

            if data.boxes:
                # Print the bounding boxes and their classes
                for box in data.boxes:
                    xyxy = box.xyxy.numpy()
                    type = None
                    conf = None
                    for predIndex, cls in enumerate(box.cls):
                        clsName = data.names[int(cls)]
                        if conf == None or box.conf[predIndex] > conf:
                            type = clsName
                            conf = box.conf[predIndex]

                    if type != None:
                        type = ClassType(type)
                        match = False
                        for box in self.boxes:
                            if box.is_same(xyxy, type):
                                changed = changed or box.update(conf, xyxy)
                                if not box.should_remove():
                                    boxes.append(box)
                                else:
                                    changed = True
                                match = True
                                break

                        if not match:
                            changed = True
                            boxes.append(Box(conf, type, xyxy))

            for box in self.boxes:
                if box not in boxes:
                    changed = changed or box.update(0)
                    if not box.should_remove():
                        boxes.append(box)
                    else:
                        changed = True

            self.boxes = boxes

            if changed:
                self.change_event.set()

    def get_top_card(self):
        while True:
            self.change_event.wait()
            self.change_event.clear()

            cards = self.get_visible_cards()
            if len(cards) == 1:
                return cards[0]

    def get_drawn_card(self):
        print("Waiting for drawn card...")
        while True:
            self.change_event.wait()
            self.change_event.clear()

            cards = self.get_visible_cards()
            hand = self.state.get_current_player().hand
            top_card = self.state.get_top_card()

            for card in cards:
                if card != top_card and card not in hand:
                    print(f"Drawn card: {card}.")
                    print(f"Waiting for card to disappear from view...")
                    while True:
                        self.change_event.wait()
                        self.change_event.clear()

                        cards = self.get_visible_cards()
                        if card not in cards:
                            return card

    def wait_for_shuffle(self):
        input("Please shuffle the deck and press enter when you are ready to continue.")

    def wait_for_top_card(self, card: Card):
        print(f"Waiting for top card to be {card}...")
        while True:
            self.change_event.wait()
            self.change_event.clear()

            cards = self.get_visible_cards()
            if card in cards:

                return
    
    def wait_for_play_or_draw(self):
        if self.state.pestkaarten_sum > 0:
            print(f"You need to throw a 'pestkaart' or you will be forced to draw {self.state.pestkaarten_sum} new cards.")

        orig_draw_pile_conf = self.get_draw_pile_confidence()
        while True:
            self.change_event.wait()
            self.change_event.clear()

            if orig_draw_pile_conf - self.get_draw_pile_confidence() > 0.1:
                return None

            cards = self.get_visible_cards()
            top_card = self.state.get_top_card()
            for card in cards:
                if card != top_card:
                    return card

    def get_visible_cards(self) -> list[Card]:
        types: set[ClassType] = set()
        for box in self.boxes:
            if box.should_include() and box.type.is_card():
                types.add(box.type)

        return [type.to_card() for type in types]

    def get_draw_pile_confidence(self) -> float:
        pile_box = None
        for box in self.boxes:
            if box.type == ClassType.PILE_FACE_DOWN and (pile_box == None or box.confidence > pile_box.confidence):
                pile_box = box

        if pile_box == None:
            return 0
        else:
            return pile_box.confidence

    def __deepcopy__(self, obj):
        return None