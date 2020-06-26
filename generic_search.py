# generic_search.py
# From Classic Computer Science Problems in Python Chapter 2
# Copyright 2018 David Kopec
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations
from typing import TypeVar, Generic, List, Callable, Set, Deque, Dict, Optional
from heapq import heappush, heappop

T = TypeVar('T')


class Stack(Generic[T]):
    def __init__(self) -> None:
        self.container: List[T] = []

    @property
    def empty(self) -> bool:
        return not self.container  # not is true for empty container

    def push(self, item: T) -> None:
        self.container.append(item)

    def pop(self) -> T:
        return self.container.pop()  # LIFO

    def __repr__(self) -> str:
        return repr(self.container)


class Node(Generic[T]):
    def __init__(self, state: T, parent: Optional[Node], cost: float = 0.0, heuristic: float = 0.0) -> None:
        self.state: T = state
        self.parent: Optional[Node] = parent
        self.cost: float = cost
        self.heuristic: float = heuristic

    def __lt__(self, other: Node) -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


def node_to_path(node: Node[T]) -> List[T]:
    path: List[T] = [node.state]
    # work backwards from end to front
    while node.parent is not None:
        node = node.parent
        path.append(node.state)
    path.reverse()
    return path


class Queue(Generic[T]):
    def __init__(self) -> None:
        self.container: Deque[T] = Deque()

    @property
    def empty(self) -> bool:
        return not self.container  # not is true for empty container

    def push(self, item: T) -> None:
        self.container.append(item)

    def pop(self) -> T:
        return self.container.popleft()  # FIFO

    def __repr__(self) -> str:
        return repr(self.container)


class PriorityQueue(Generic[T]):
    def __init__(self) -> None:
        self._container: List[T] = []

    @property
    def empty(self) -> bool:
        return not self._container  # not is true for empty container

    def push(self, item: T) -> None:
        heappush(self._container, item)  # in by priority

    def pop(self) -> T:
        return heappop(self._container)  # out by priority

    def __repr__(self) -> str:
        return repr(self._container)


def astar(initial: T, goal_test: Callable[[T], bool], successors: Callable[[T], List[T]], heuristic: Callable[[T], float]) -> Optional[Node[T]]:
    # frontier is where we've yet to go
    frontier: PriorityQueue[Node[T]] = PriorityQueue()
    frontier.push(Node(initial, None, 0.0, heuristic(initial)))
    # explored is where we've been
    explored: Dict[T, float] = {initial: 0.0}

    # keep going while there is more to explore
    while not frontier.empty:
        current_node: Node[T] = frontier.pop()
        current_state: T = current_node.state
        # if we found the goal, we're done
        if goal_test(current_state):
            return current_node
        # check where we can go next and haven't explored
        for child in successors(current_state):
            new_cost: float = current_node.cost + 1  # 1 assumes a grid, need a cost function for more sophisticated apps

            if child not in explored or explored[child] > new_cost:
                explored[child] = new_cost
                frontier.push(Node(child, current_node, new_cost, heuristic(child)))
    return None  # went through everything and never found goal


if __name__ == "__main__":
    print(linear_contains([1, 5, 15, 15, 15, 15, 20], 5))  # True
    print(binary_contains(["a", "d", "e", "f", "z"], "f"))  # True
    print(binary_contains(["john", "mark", "ronald", "sarah"], "sheila"))  # False