# maze_gui.py
# Copyright 2020 David Kopec
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
from enum import Enum
from typing import List, NamedTuple, Callable, Optional, TypeVar
import random
from math import sqrt
from time import sleep
from generic_search import Stack, Queue, node_to_path, astar, Node
from tkinter import *
from tkinter.ttk import *

T = TypeVar('T')


class Cell(str, Enum):
    EMPTY = " "
    BLOCKED = "X"
    START = "S"
    GOAL = "G"
    EXPLORED = "E"
    CURRENT = "C"
    FRONTIER = "F"
    PATH = "*"


class MazeLocation(NamedTuple):
    row: int
    column: int

    def __str__(self):
        return f"({self.row}, {self.column})"


class MazeGUI:
    def __init__(self, rows: int = 10, columns: int = 10, sparseness: float = 0.2,
                 start: MazeLocation = MazeLocation(0, 0), goal: MazeLocation = MazeLocation(9, 9)) -> None:
        # initialize basic instance variables
        self._rows: int = rows
        self._columns: int = columns
        self.start: MazeLocation = start
        self.goal: MazeLocation = goal
        # fill the grid with empty cells
        self._grid: List[List[Cell]] = [[Cell.EMPTY for c in range(columns)] for r in range(rows)]
        # populate the grid with blocked cells
        self._randomly_fill(rows, columns, sparseness)
        # fill the start and goal locations in
        self._grid[start.row][start.column] = Cell.START
        self._grid[goal.row][goal.column] = Cell.GOAL
        self._setup_GUI()

    def _setup_GUI(self):
        # start the GUI
        self.root: Tk = Tk()
        self.root.title("Maze Solving")
        Grid.rowconfigure(self.root, 0, weight=1)
        Grid.columnconfigure(self.root, 0, weight=1)
        # main window
        frame: Frame = Frame(self.root)
        frame.grid(row=0, column=0, sticky=N + S + E + W)
        # style for widgets
        style: Style = Style()
        style.theme_use('classic')
        style.configure("BG.TLabel", foreground="black", font=('Helvetica', 26))
        style.configure("BG.TButton", foreground="black", font=('Helvetica', 26))
        style.configure("BG.TListbox", foreground="black", font=('Helvetica', 26))
        style.configure("BG.TCombobox", foreground="black", font=('Helvetica', 26))
        style.configure(" ", foreground="black", background="white")
        style.configure(Cell.EMPTY.value + ".TLabel", foreground="black", background="white", font=('Helvetica', 26))
        style.configure(Cell.BLOCKED.value + ".TLabel", foreground="white", background="black", font=('Helvetica', 26))
        style.configure(Cell.START.value + ".TLabel", foreground="black", background="green", font=('Helvetica', 26))
        style.configure(Cell.GOAL.value + ".TLabel", foreground="black", background="red", font=('Helvetica', 26))
        style.configure(Cell.PATH.value + ".TLabel", foreground="black", background="cyan", font=('Helvetica', 26))
        style.configure(Cell.EXPLORED.value + ".TLabel", foreground="black", background="yellow",
                        font=('Helvetica', 26))
        style.configure(Cell.CURRENT.value + ".TLabel", foreground="black", background="blue", font=('Helvetica', 26))
        style.configure(Cell.FRONTIER.value + ".TLabel", foreground="black", background="orange",
                        font=('Helvetica', 26))
        # put labels on the side
        for row in range(self._rows):
            Grid.rowconfigure(frame, row, weight=1)
            row_label: Label = Label(frame, text=str(row), style="BG.TLabel", anchor="center")
            row_label.grid(row=row, column=0, sticky=N + S + E + W)
            Grid.rowconfigure(frame, row, weight=1)
            Grid.grid_columnconfigure(frame, 0, weight=1)
        # put labels on the bottom
        for column in range(self._columns):
            Grid.columnconfigure(frame, column, weight=1)
            column_label: Label = Label(frame, text=str(column), style="BG.TLabel", anchor="center")
            column_label.grid(row=self._rows, column=column + 1, sticky=N + S + E + W)
            Grid.rowconfigure(frame, self._rows, weight=1)
            Grid.columnconfigure(frame, column + 1, weight=1)
        # setup grid display
        self._cell_labels: List[List[Label]] = [[Label(frame, anchor="center") for c in range(self._columns)] for r in
                                                range(self._rows)]
        for row in range(self._rows):
            for column in range(self._columns):
                cell_label: Label = self._cell_labels[row][column]
                Grid.columnconfigure(frame, column + 1, weight=1)
                Grid.rowconfigure(frame, row, weight=1)
                cell_label.grid(row=row, column=column + 1, sticky=N + S + E + W)
        self._display_grid()
        # setup buttons
        dfs_button: Button = Button(frame, style="BG.TButton", text="Run DFS", command=self.dfs)
        dfs_button.grid(row=self._rows + 2, column=0, columnspan=6, sticky=N + S + E + W)
        bfs_button: Button = Button(frame, style="BG.TButton", text="Run BFS", command=self.bfs)
        bfs_button.grid(row=self._rows + 2, column=6, columnspan=6, sticky=N + S + E + W)
        Grid.rowconfigure(frame, self._rows + 2, weight=1)
        # setup data structure displays
        frontier_label: Label = Label(frame, text="Frontier", style="BG.TLabel", anchor="center")
        frontier_label.grid(row=0, column=self._columns + 2, columnspan=3, sticky=N + S + E + W)
        explored_label: Label = Label(frame, text="Explored", style="BG.TLabel", anchor="center")
        explored_label.grid(row=self._rows // 2, column=self._columns + 2, columnspan=3, sticky=N + S + E + W)
        Grid.columnconfigure(frame, self._columns + 2, weight=1)
        Grid.columnconfigure(frame, self._columns + 3, weight=1)
        Grid.columnconfigure(frame, self._columns + 4, weight=1)
        self._frontier_listbox: Listbox = Listbox(frame, font=("Helvetica", 14))
        self._frontier_listbox.grid(row=1, column=self._columns + 2, columnspan=3, rowspan=self._rows // 2 - 1,
                                    sticky=N + S + E + W)
        # self._frontier_listbox.pack( side = LEFT, fill = BOTH )
        # frscrollbar = Scrollbar(frame, orient=VERTICAL)
        # frscrollbar.grid(row = 1, column = 2)
        # frscrollbar.pack(side=RIGHT, fill=BOTH)
        # self._frontier_listbox.config(yscrollcommand=frscrollbar.set)
        # frscrollbar.config(command=self._frontier_listbox.yview)
        self._explored_listbox: Listbox = Listbox(frame, font=("Helvetica", 14))
        self._explored_listbox.grid(row=self._rows // 2 + 1, column=self._columns + 2, columnspan=3,
                                    rowspan=self._rows // 2 - 1,
                                    sticky=N + S + E + W)
        # exscrollbar = Scrollbar(frame, orient=VERTICAL)
        # exscrollbar.pack(side=RIGHT, fill=BOTH)
        # self._explored_listbox.config(yscrollcommand=exscrollbar.set)
        # exscrollbar.config(command=self._explored_listbox.yview)
        # spinbox for interval
        interval_label: Label = Label(frame, text="Interval", style="BG.TLabel", anchor="center")
        interval_label.grid(row=self._rows + 1, column=self._columns + 2, columnspan=3, sticky=N + S + E + W)
        self._interval_box: Combobox = Combobox(frame, state="readonly", values=[1, 2, 3, 4, 5], justify="center",
                                                style="BG.TCombobox")
        self._interval_box.set(2)
        self._interval_box.grid(row=self._rows + 2, column=self._columns + 2, columnspan=3, sticky=N + S + E + W)
        # pack and go
        frame.pack(fill="both", expand=True)
        self.root.mainloop()

    def _randomly_fill(self, rows: int, columns: int, sparseness: float):
        for row in range(rows):
            for column in range(columns):
                if random.uniform(0, 1.0) < sparseness:
                    self._grid[row][column] = Cell.BLOCKED

    def _display_grid(self):
        self._grid[self.start.row][self.start.column] = Cell.START
        self._grid[self.goal.row][self.goal.column] = Cell.GOAL
        for row in range(self._rows):
            for column in range(self._columns):
                cell: Cell = self._grid[row][column]
                cell_label: Label = self._cell_labels[row][column]
                cell_label.configure(style=cell.value + ".TLabel")

    def step(self, frontier, explored, last_node):
        if not frontier.empty:
            current_node: Node[T] = frontier.pop()
            current_state: T = current_node.state
            if isinstance(frontier, Stack):
                self._frontier_listbox.delete(END, END)
            elif isinstance(frontier, Queue):
                self._frontier_listbox.delete(0, 0)
            self._grid[current_state.row][current_state.column] = Cell.CURRENT
            if last_node is not None:
                self._grid[last_node.state.row][last_node.state.column] = Cell.EXPLORED
            # if we found the goal, we're done
            if self.goal_test(current_state):
                path = node_to_path(current_node)
                self.mark(path)
                self._display_grid()
                return
            # check where we can go next and haven't explored
            for child in self.successors(current_state):
                if child in explored:  # skip children we already explored
                    continue
                explored.add(child)

                frontier.push(Node(child, current_node))
                # update GUI
                self._grid[child.row][child.column] = Cell.FRONTIER
                self._explored_listbox.insert(END, str(child))
                self._frontier_listbox.insert(END, str(child))
                self._explored_listbox.select_set(END)
                self._explored_listbox.yview(END)
                self._frontier_listbox.select_set(END)
                self._frontier_listbox.yview(END)
            self._display_grid()
            num_delay = int(self._interval_box.get()) * 1000
            self.root.after(num_delay, self.step, frontier, explored, current_node)

    def dfs(self):
        self.clear()
        self._display_grid()
        # frontier is where we've yet to go
        frontier: Stack[Node[T]] = Stack()
        frontier.push(Node(self.start, None))
        # explored is where we've been
        explored: Set[T] = {self.start}
        self.step(frontier, explored, None)

    def bfs(self):
        self.clear()
        self._display_grid()
        # frontier is where we've yet to go
        frontier: Queue[Node[T]] = Queue()
        frontier.push(Node(self.start, None))
        # explored is where we've been
        explored: Set[T] = {self.start}
        self.step(frontier, explored, None)

    # return a nicely formatted version of the maze for printing
    def __str__(self) -> str:
        output: str = ""
        for row in self._grid:
            output += "".join([c.value for c in row]) + "\n"
        return output

    def goal_test(self, ml: MazeLocation) -> bool:
        return ml == self.goal

    def successors(self, ml: MazeLocation) -> List[MazeLocation]:
        locations: List[MazeLocation] = []
        if ml.row + 1 < self._rows and self._grid[ml.row + 1][ml.column] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row + 1, ml.column))
        if ml.row - 1 >= 0 and self._grid[ml.row - 1][ml.column] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row - 1, ml.column))
        if ml.column + 1 < self._columns and self._grid[ml.row][ml.column + 1] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row, ml.column + 1))
        if ml.column - 1 >= 0 and self._grid[ml.row][ml.column - 1] != Cell.BLOCKED:
            locations.append(MazeLocation(ml.row, ml.column - 1))
        return locations

    def mark(self, path: List[MazeLocation]):
        for maze_location in path:
            self._grid[maze_location.row][maze_location.column] = Cell.PATH
        self._grid[self.start.row][self.start.column] = Cell.START
        self._grid[self.goal.row][self.goal.column] = Cell.GOAL

    def clear(self):
        self._frontier_listbox.delete(0, END)
        self._explored_listbox.delete(0, END)
        for row in range(self._rows):
            for column in range(self._columns):
                if self._grid[row][column] != Cell.BLOCKED:
                    self._grid[row][column] = Cell.EMPTY
        self._grid[self.start.row][self.start.column] = Cell.START
        self._grid[self.goal.row][self.goal.column] = Cell.GOAL


def euclidean_distance(goal: MazeLocation) -> Callable[[MazeLocation], float]:
    def distance(ml: MazeLocation) -> float:
        xdist: int = ml.column - goal.column
        ydist: int = ml.row - goal.row
        return sqrt((xdist * xdist) + (ydist * ydist))

    return distance


def manhattan_distance(goal: MazeLocation) -> Callable[[MazeLocation], float]:
    def distance(ml: MazeLocation) -> float:
        xdist: int = abs(ml.column - goal.column)
        ydist: int = abs(ml.row - goal.row)
        return (xdist + ydist)

    return distance


if __name__ == "__main__":
    # Test DFS
    m: MazeGUI = MazeGUI()
    # print(m)
    # solution1: Optional[Node[MazeLocation]] = dfs(m.start, m.goal_test, m.successors)
    # if solution1 is None:
    #     print("No solution found using depth-first search!")
    # else:
    #     path1: List[MazeLocation] = node_to_path(solution1)
    #     m.mark(path1)
    #     print(m)
    #     m.clear(path1)
    # # Test BFS
    # solution2: Optional[Node[MazeLocation]] = bfs(m.start, m.goal_test, m.successors)
    # if solution2 is None:
    #     print("No solution found using breadth-first search!")
    # else:
    #     path2: List[MazeLocation] = node_to_path(solution2)
    #     m.mark(path2)
    #     print(m)
    #     m.clear(path2)
    # # Test A*
    # distance: Callable[[MazeLocation], float] = manhattan_distance(m.goal)
    # solution3: Optional[Node[MazeLocation]] = astar(m.start, m.goal_test, m.successors, distance)
    # if solution3 is None:
    #     print("No solution found using A*!")
    # else:
    #     path3: List[MazeLocation] = node_to_path(solution3)
    #     m.mark(path3)
    #     print(m)
