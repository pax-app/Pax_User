from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from project.api.utils.creation_utils import Utils


class Context():
    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def execute_sorting(self, provider_category_id) -> dict:
        providers_info = Utils().append_username_to_provider(provider_category_id)
        result = self._strategy.sort_providers(providers_info)
        return result


class Strategy(ABC):
    @abstractmethod
    def sort_providers(self, data: dict):
        pass


class ReviewStrategy(Strategy):
    def sort_providers(self, data: dict) -> dict:
        data = Utils().append_review_to_provider(data)
        providers_info = sorted(data, key=lambda element: element['reviews_average'])
        return sorted(data)


class PriceStrategy(Strategy):
    def sort_providers(self, data: dict) -> dict:
        providers_info = sorted(data, key=lambda element: element['minimum_price'])
        return providers_info


if __name__ == "__main__":
    # The client code picks a concrete strategy and passes it to the context.
    # The client should be aware of the differences between strategies in order
    # to make the right choice.

    context = Context(ConcreteStrategyA())
    print("Client: Strategy is set to normal sorting.")
    context.execute_sorting()
    print()

    print("Client: Strategy is set to reverse sorting.")
    context.strategy = ConcreteStrategyB()
    context.execute_sorting()
