from dataclasses import dataclass


@dataclass
class Theme:
    id: int | None
    title: str


@dataclass
class Question:
    id: int | None
    title: str
    theme_id: int | None
    answers: list['Answer']


@dataclass
class Answer:
    title: str
    is_correct: bool
