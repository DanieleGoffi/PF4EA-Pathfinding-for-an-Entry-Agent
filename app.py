import tracemalloc
from tkinter import *
from matplotlib.colors import ListedColormap

from Core import solver

from Domain.grid import  *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Domain.agent import  *
from Core.problem import *

from tkinter.messagebox import showerror, showinfo
from tkinter import filedialog
from memory_profiler import profile
import timeout_decorator

def print_error(message:str):
    showerror("Error", message)
    raise Exception(message)

class App(Tk):
    def __init__(self):
        super().__init__()
        self.configure(background='white')

        self.grid = None
        self.traversables = []
        self.rows_var = IntVar(value=10)
        self.col_var = IntVar(value=10)
        self.perc_avail_cells_var = DoubleVar(value=0.8)
        self.agg_factor_var = IntVar(value=10)
        self.agents_var = IntVar(value=3)
        self.length_var = IntVar(value=10)
        self.max_var = IntVar(value = self.length_var.get() + 5)
        self.agents = []

        self.init_row = IntVar()
        self.init_col = IntVar()
        self.goal_row = IntVar()
        self.goal_col = IntVar(value=5)

        self.counter = 0

        self.problem = None
        self.solution_path = []
        self.cost = None
        self.count_open = None
        self.count_closed = None
        self.num_wait = None
        self.algo_time=0
        self.grid_time=0
        self.agents_time=0
        self.problem_time=0
        self.recap_base = "No elaboration performed \n"
        self.recap_alternative = "No elaboration performed \n"

        self.title("PF4EA")
        self.geometry("1000x1200")
        self.page = Page1(self)

    def go_to_page_2(self):
        if self.grid is None:
            print_error("No grid generated.")

        if len(self.traversables) == 0:
            print_error("A grid with no traversable cells can not be used.")

        self.page.destroy()
        self.canvas_widget.destroy()
        self.page = Page2(self)
        self.visualize_grid(self.grid.get_matrix())


    def generate_grid(self):
        # Controlli
        try:
            if self.rows_var.get() < 2:
                print_error("The number of rows must be at least 2.")
        except TclError:
            print_error("The number of rows must be an integer not smaller than 2.")

        try:
            if self.col_var.get() < 2:
                print_error("The number of columns must be at least 2.")
        except TclError:
            print_error("The number of columns must be an integer not smaller than 2.")

        try:
            if self.perc_avail_cells_var.get() < 0 or self.perc_avail_cells_var.get() > 1:
                print_error("The percentage of available cells must be between 0 and 1.")
        except TclError:
            print_error("The percentage of available cells must be a number between 0 and 1.")

        try:
            if self.agg_factor_var.get() < 1:
                print_error("The agglomeration factor must be at least 1.")
        except TclError:
            print_error("The agglomeration factor must be an integer greater than 0.")

        try:
            if self.agg_factor_var.get() > self.rows_var.get() * self.col_var.get():
                print_error("The agglomeration factor can not exceed the total number of cells.")
        except TclError:
            print_error("The agglomeration factor must be an integer smaller than or equal to the total number of cells.")

        rows = self.rows_var.get()
        col = self.col_var.get()
        perc_avail_cells = self.perc_avail_cells_var.get()
        aggregate_factor = self.agg_factor_var.get()

        try:
            start_time = time.perf_counter()
            self.grid = Grid(rows, col, perc_avail_cells, aggregate_factor)
            end_time = time.perf_counter()

            self.grid_time = end_time - start_time
        except timeout_decorator.timeout_decorator.TimeoutError:
            print_error("Time limit exceeded (300s)")


        self.traversables = self.grid.get_traversables()
        self.visualize_grid(self.grid.get_matrix())

    def visualize_grid(self, matrix):
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.pack_forget()
        # Colori per 0, 1
        base_colors = ['white', 'black']
        if np.max(matrix)>1:
             # Colori per 0, 1, 2, 3 + color map
            cmap = ListedColormap(base_colors + ['green', 'red'] + plt.cm.tab10(np.linspace(0, 1, np.max(matrix)-2)).tolist())
        else:
            cmap = ListedColormap(base_colors)

        plt.clf()
        plt.figure(figsize=(100, 100))
        plt.pcolormesh(matrix, edgecolors='k', linewidth=0.5, cmap=cmap)
        ax = plt.gca()
        ax.set_aspect('equal')
        ax.invert_yaxis()
        plt.axis('off')
        num_rows, num_cols = matrix.shape
        for i in range(num_rows):
            for j in range(num_cols):
                ax.text(j + 0.5, i + 0.5, f'({i},{j})', color='black', ha='center', va='center', fontsize=7)

        fig = plt.gcf()
        plt.close()

        canvas = FigureCanvasTkAgg(fig, self)
        widget = canvas.get_tk_widget()
        widget.pack()

        self.canvas_widget = widget

    def add_agents(self):
        # Controlli
        try:
            if self.init_row.get() < 0 or self.init_row.get() > self.rows_var.get()-1:
                print_error("The initial row must be between 0 and number of rows - 1.")
        except TclError:
            print_error("The initial row must be an integer between 0 and number of rows - 1.")

        try:
            if self.init_col.get() < 0 or self.init_col.get() > self.col_var.get()-1:
                print_error("The initial col must be between 0 and number of columns - 1.")
        except TclError:
            print_error("The initial col must be an integer between 0 and number of columns - 1.")

        try:
            if self.goal_row.get() < 0 or self.goal_row.get() > self.rows_var.get()-1:
                print_error("The goal row must be between 0 and number of rows - 1.")
        except TclError:
            print_error("The goal row must be an integer between 0 and number of rows - 1.")

        try:
            if self.goal_col.get() < 0 or self.goal_col.get() > self.col_var.get()-1:
                print_error("The goal col must be between 0 and number of columns - 1.")
        except TclError:
            print_error("The goal col must be an integer between 0 and number of columns - 1.")

        try:
            if self.agents_var.get() < 0:
                print_error("The number of agents can not be negative.")
        except TclError:
            print_error("The number of agents must be a positive integer.")

        try:
            if self.length_var.get() < 0:
                print_error("The max length of an agent can not be negative.")
        except TclError:
            print_error("The max length of an agent must be a positive integer.")

        try:
            if self.max_var.get() < 0:
                print_error("MAX can not be negative.")
        except TclError:
            print_error("MAX must be a positive integer.")

        if self.agents_var.get() > 0 and self.length_var.get() == 0:
            print_error("If the number of agents is at least 1, length_var can not be 0.")

        if self.agents_var.get() > len(self.traversables)-1  :
            print_error("The number of agents must be lower than available cells - 1.")

        init = Cell(self.init_row.get(), self.init_col.get())
        goal = Cell(self.goal_row.get(), self.goal_col.get())

        # Creazione agenti
        self.agents = []
        try:
            if self.agents_var.get() > 0:
                lengths=[]
                for i in range(self.agents_var.get()-1):
                    lengths.append(random.randint(1, self.length_var.get()))
                lengths.append(self.length_var.get())

                lengths.sort()

                start_time = time.perf_counter()
                for length_agent in lengths:
                    self.agents.append(Agent(self.grid, length_agent, self.agents))
                end_time = time.perf_counter()
                self.agents_time = end_time - start_time

        except timeout_decorator.timeout_decorator.TimeoutError:
            print_error("Time limit exceeded (100s per agent)")
        except:
            print_error("Conflicts occurred while generating random agents, retry (maybe with less agents).")


        if init.is_obstacle(self.grid.get_matrix()) or goal.is_obstacle(self.grid.get_matrix()):
            print_error("Init and goal can not be obstacles.")

        for agent in self.agents:
            if agent.start == init:
                print_error("Init can not be a starting cell of another agent.")
            if agent.end == goal:
                print_error("Goal can not be an ending cell of another agent.")

        if len(self.agents) > 0:
            if self.max_var.get() < self.length_var.get():
                print_error("Max length of agents can not be greater than time horizon max.")
        else:
            self.length_var.set(0)

        if self.max_var.get() > self.length_var.get() + len(self.traversables):
            print_error("Time horizon max can not exceed the sum of the length of the longest agent and the number of traversable cells.")

        start_time = time.perf_counter()
        self.problem = PF4EA(self.grid, self.agents, init, goal, self.max_var.get())
        end_time = time.perf_counter()
        self.problem_time = end_time - start_time

        self.problem_time += self.grid_time + self.agents_time
        matrix_with_agents = self.problem.matrix_with_agents()

        self.visualize_grid(matrix_with_agents)

    def call_reach_goal(self, alternative):
        time_exceeded = False

        if self.problem is None:
            print_error("No problem instance defined.")

        self.page.destroy()
        self.canvas_widget.destroy()
        self.page = Page3(self)
        self.visualize_grid(self.grid.get_matrix())

        self.counter = 0

        sol = solver.Solver()

        try:
            start_time = time.perf_counter()
            self.solution_path, self.count_open, self.count_closed = sol.reach_goal(self.problem, alternative)
            end_time = time.perf_counter()
            self.algo_time = end_time - start_time
        except timeout_decorator.timeout_decorator.TimeoutError:
            time_exceeded = True

        if alternative:
            self.page.label_algo.config(text='Alternative Reach Goal')
        else:
            self.page.label_algo.config(text='Base Reach Goal')

        path_length = ""
        if time_exceeded:  # timeout raggiunto
            self.page.button1.destroy()
            self.page.button2.destroy()
            self.page.label.config(text='TIME EXCEEDED', font=('calibre', 10, 'bold'))
            self.cost = "/"
            self.num_wait = "/"
            path_length = "/"

        elif not self.solution_path:  # nessuna souzione trovata
            self.page.button1.destroy()
            self.page.button2.destroy()
            self.page.label.config(text='SEARCH FAILED', font=('calibre', 10, 'bold'))
            self.cost = "/"
            self.num_wait = "/"
            path_length = "/"

        else:  # soluzione trovata
            self.cost = solver.compute_path_weight(self.grid.graph, self.solution_path)
            self.num_wait = solver.count_wait_moves(self.solution_path)
            path_length = str(len(self.solution_path))

        self.page.label_info1.config(
            text='Init: (' + str(self.problem.init.get_row()) + ', ' + str(self.problem.init.get_col()) + ')'
                 '  Goal: (' + str(self.problem.goal.get_row()) + ', ' + str(self.problem.goal.get_col()) + ')'
                 '  Cost: ' + str(self.cost) +
                 '  Length: ' + path_length)

        self.page.label_info2.config(
            text='Exec time: ' + str(self.algo_time) +
                 '  Count open: ' + str(self.count_open) +
                 '  Count closed: ' + str(self.count_closed) +
                 '  Wait moves: ' + str(self.num_wait))

        recap="Using relaxed path heuristic "
        if time_exceeded:
            recap += "\nTime Exceeded"
        elif not self.solution_path:
            recap += "\nSearch Failed"
        else:
            i = 0
            for cell in self.solution_path:
                recap += "\n(" + str(cell.get_row()) + ", " + str(cell.get_col()) +") at " + str(i)
                i += 1

        recap += ('\nCost: ' + str(self.cost) + "\n" +
                  'Length: ' + path_length + "\n" +
                  'Exec time: ' + str(self.algo_time) + "\n"+
                  'Count open: ' + str(self.count_open) + "\n" +
                  'Count closed: ' + str(self.count_closed) + "\n" +
                  'Wait moves: ' + str(self.num_wait))

        if alternative:
            self.recap_alternative = recap
        else:
            self.recap_base = recap

    def next_step(self):
        t = self.counter
        if t < len(self.solution_path):
            mat = self.problem.matrix_at_time(t, self.solution_path)
            self.visualize_grid(mat)
            self.page.label.config(text="Time = " + str(t))
            self.counter += 1
        else:
            mat = self.problem.matrix_with_sol(self.solution_path)
            self.visualize_grid(mat)
            self.page.label.config(text="Final Situation")

            showinfo("Finished", "The path is done")

    def last_step(self):
        self.page.label.config(text="Final Situation")
        mat = self.problem.matrix_with_sol(self.solution_path)
        self.visualize_grid(mat)

    def generate_random_init_goal(self):
        cell_init = np.random.choice(self.traversables)
        self.init_row.set(cell_init.row)
        self.init_col.set(cell_init.col)

        cell_goal = np.random.choice(self.traversables)
        self.goal_row.set(cell_goal.row)
        self.goal_col.set(cell_goal.col)

    def load_instance_from_file(self):
        try:
            filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                    filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
            if filename:
                problem = PF4EA()
                problem.read_instance_from_file(filename)
                self.problem = problem
                self.grid = self.problem.grid
                self.agents = self.problem.agents
                self.init_row.set(self.problem.init.get_row())
                self.init_col.set(self.problem.init.get_col())
                self.goal_row.set(self.problem.goal.get_row())
                self.goal_col.set(self.problem.goal.get_col())
                self.max_var.set(self.problem.max)
                matrix_with_agents = self.problem.matrix_with_agents()

                self.page.destroy()
                if hasattr(self, 'canvas_widget'):
                    self.canvas_widget.pack_forget()
                self.page = Page2(self)
                self.visualize_grid(matrix_with_agents)
        except:
            print_error("Impossible to use the selected file.")

    def save_instance(self):
        if self.problem is None:
            print_error("No problem instance defined.")

        filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        if filename:
            self.problem.save_instance_to_file(filename)

    def save_solution_to_file(self):
        filename = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        if filename:
            with open(filename, 'w') as f:
                f.write("Grid size: " + str(self.rows_var.get()) + "x" + str(self.col_var.get()) + "\n")
                f.write("Number of traversable cells: " + str(len(self.traversables)) + ", with percentage set at: " + str(self.perc_avail_cells_var.get()) + "\n")
                f.write("Agglomeration factor: " + str(self.agg_factor_var.get()) + "\n")
                f.write("Number of agents: " + str(self.agents_var.get()) + "\n")
                f.write("Paths generated in pseudorandom way\n")
                f.write("Lengths of paths: ")
                for a in self.agents[:-1]:
                    f.write(str(a.length) + ", ")
                f.write(str(self.agents[-1].length) + "\n")
                f.write("Max length of agents: " + str(self.length_var.get()) + "\n")
                f.write("Time horizon max: " + str(self.max_var.get()) + "\n")
                f.write("Init: (" + str(self.problem.init.get_row()) + ", " + str(self.problem.init.get_col()) + ")\n")
                f.write("Goal: (" + str(self.problem.goal.get_row()) + ", " + str(self.problem.goal.get_col()) + ")\n")
                f.write("Grid generation time: " + str(self.grid_time) + "\n")
                f.write("Agents generation time: " + str(self.agents_time) + "\n")
                f.write("Total time to create PF4EA instance: " + str(self.problem_time) + "\n")
                f.write("\n")
                f.write("Reach Goal Base" + "\n")
                f.write(self.recap_base)
                f.write("\n\nReach Goal Alternative" + "\n")
                f.write(self.recap_alternative)


    def restart_app(self):
        self.destroy()
        app = App()
        app.mainloop()

class Page1(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(pady=5)

        # Righe
        self.label_row = Label(self, text='Rows', font=('calibre', 10, 'bold'))
        self.entry_row = Entry(self, textvariable=parent.rows_var, font=('calibre', 10, 'normal'))
        # Colonne
        self.label_col = Label(self, text='Columns', font=('calibre', 10, 'bold'))
        self.entry_col = Entry(self, textvariable=parent.col_var, font=('calibre', 10, 'normal'))
        # Percentage of available cells
        self.label_perc = Label(self, text='Percentage of available cells', font=('calibre', 10, 'bold'))
        self.entry_perc = Entry(self, textvariable=parent.perc_avail_cells_var, font=('calibre', 10, 'normal'))
        # Agglomeration factor
        self.label_agg = Label(self, text='Agglomeration factor', font=('calibre', 10, 'bold'))
        self.entry_agg = Entry(self, textvariable=parent.agg_factor_var, font=('calibre', 10, 'normal'))

        self.label_row.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.entry_row.grid(row=0, column=1,sticky='w', padx=5, pady=5)

        self.label_col.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.entry_col.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        self.label_perc.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.entry_perc.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        self.label_agg.grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.entry_agg.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        # Main action buttons
        self.button_1 = Button(self, text='Generate Grid', command=parent.generate_grid)
        self.button_2 = Button(self, text='Use this grid and continue', command=parent.go_to_page_2)
        self.button_3 = Button(self, text='Load instance of PF4EA from file', command=parent.load_instance_from_file)

        self.button_1.grid(row=7, column=0, columnspan=2,pady=10)
        self.button_2.grid(row=8, column=0, columnspan=2, pady=10)
        self.button_3.grid(row=9, column=0, columnspan=2, pady=10)

class Page2(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(pady=5)

        self.num_attr = Label(self, text='Number of traversable cells: ' + str(len(parent.traversables)), font=('calibre', 10, 'italic'))

        self.label_agents = Label(self, text='Number of Agents', font=('calibre', 10, 'bold'))
        self.entry_agents = Entry(self, textvariable=parent.agents_var, font=('calibre', 10, 'normal'))

        self.label_length = Label(self, text='Max Length of Agents', font=('calibre', 10, 'bold'))
        self.entry_length = Entry(self, textvariable=parent.length_var, font=('calibre', 10, 'normal'))

        self.label_init_row = Label(self, text='Init Row', font=('calibre', 10, 'bold'))
        self.entry_init_row = Entry(self, textvariable=parent.init_row, font=('calibre', 10, 'normal'))

        self.label_init_col = Label(self, text='Init Col', font=('calibre', 10, 'bold'))
        self.entry_init_col = Entry(self, textvariable=parent.init_col, font=('calibre', 10, 'normal'))

        self.label_goal_row = Label(self, text='Goal Row', font=('calibre', 10, 'bold'))
        self.entry_goal_row = Entry(self, textvariable=parent.goal_row, font=('calibre', 10, 'normal'))

        self.label_goal_col = Label(self, text='Goal Col', font=('calibre', 10, 'bold'))
        self.entry_goal_col = Entry(self, textvariable=parent.goal_col, font=('calibre', 10, 'normal'))

        self.label_max = Label(self, text='Time horizon Max', font=('calibre', 10, 'bold'))
        self.entry_max = Entry(self, textvariable=parent.max_var, font=('calibre', 10, 'normal'))

        self.label_agents.grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.entry_agents.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        self.label_length.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.entry_length.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        self.label_init_row.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.entry_init_row.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        self.label_init_col.grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.entry_init_col.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        self.label_goal_row.grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.entry_goal_row.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        self.label_goal_col.grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.entry_goal_col.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        self.label_max.grid(row=6, column=0, sticky='e', padx=5, pady=5)
        self.entry_max.grid(row=6, column=1, sticky='w', padx=5, pady=5)

        self.num_attr.grid(row=7, column=0, columnspan=2, pady=10)

        self.button1 = Button(self, text='Add Agents Paths to Grid', command=parent.add_agents)
        self.button1.grid(row=8, column=0, columnspan=2, pady=10)

        self.button2 = Button(self, text='Generate random init - goal cells', command=parent.generate_random_init_goal)
        self.button2.grid(row=9, column=0, columnspan=2, pady=10)

        self.button3 = Button(self, text='Reach Goal', command=lambda: parent.call_reach_goal(False))
        self.button3.grid(row=10, column=0, columnspan=2, pady=10)

        self.button4 = Button(self, text='Alternative Reach Goal', command= lambda: parent.call_reach_goal(True))
        self.button4.grid(row=11, column=0, columnspan=2, pady=10)

        self.button5 = Button(self, text='Save this instance to file', command=parent.save_instance)
        self.button5.grid(row=13, column=0, columnspan=3, pady=10)

class Page3(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(pady=5)

        self.label_algo = Label(self, text="", font=('calibre', 10, 'bold'))
        self.label_algo.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        self.label = Label(self, text="Starting grid", font=('calibre', 10))
        self.label.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        self.button1 = Button(self, text='Next Step', command=parent.next_step)
        self.button1.grid(row=1, column=1, padx=5, pady=5)

        self.button2 = Button(self, text='Skip to End', command=parent.last_step)
        self.button2.grid(row=1, column=2, pady=5)

        self.label_info1 = Label(self, text="", font=('calibre', 10))
        self.label_info1.grid(row=2, column=0, sticky='w', padx=5, pady=5)

        self.label_info2 = Label(self, text="", font=('calibre', 10))
        self.label_info2.grid(row=3, column=0, sticky='w', padx=5, pady=5)

        self.button3 = Button(self, text='Reach Goal', command=lambda: parent.call_reach_goal(False))
        self.button3.grid(row=5, column=1, pady=10)

        self.button4 = Button(self, text='Reach Goal Alternative', command=lambda: parent.call_reach_goal(True))
        self.button4.grid(row=6, column=1, pady=10)

        self.button5 = Button(self, text='Save this instance to file', command=parent.save_instance)
        self.button5.grid(row=7, column=0, sticky='w', columnspan=1, pady=20)

        self.button6 = Button(self, text='Save results', command=parent.save_solution_to_file)
        self.button6.grid(row=7, column=1, sticky='W', columnspan=1, pady=20)

        self.button7 = Button(self, text="Restart app", command=parent.restart_app)
        self.button7.grid(row=7, column=2, sticky='e', columnspan=1, pady=20)



tracemalloc.start()
app = App()
app.mainloop()