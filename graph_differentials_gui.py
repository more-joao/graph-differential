import numpy as np
from itertools import combinations
from tkinter import mainloop, Tk, ttk, IntVar, Listbox, END, Toplevel
from tkinter.scrolledtext import ScrolledText
from threading import Thread
from math import factorial
import datetime

def determine_vertices(matrix):
    vertices = []
    for i,r in enumerate(matrix):
        vertices.append(f'v{i}')
    return vertices


def determine_edges(matrix, vertices):
    # assuming it's an undirected graph -> checks lower triangular matrix for existing edges
    edges = []
    for i,row in enumerate(matrix):
        for j,col in enumerate(row):
            if j>i:
                break
            else:
                if matrix[i][j] != 0:
                    edges.append([vertices[i], vertices[j]])
    return edges


def determine_neighbourhood(edges, vertices, target_vertices=[]):
    neighbourhood = []

    for v in target_vertices:
        for e in edges:
            if v in e:
                adjacent_vertex = vertices[vertices.index(e[(e.index(v)+1)%2])]
                if adjacent_vertex not in target_vertices and adjacent_vertex not in neighbourhood:
                    neighbourhood.append(adjacent_vertex)

    return neighbourhood


def calculate_all_subsets(vertices):
    subsets = []
    for n in range(1,len(vertices)+1):
        for c in combinations(vertices, n):
            subsets.append(c)
    return subsets


def calculate_differentials(matrix):
    vertices = determine_vertices(matrix)
    edges = determine_edges(matrix, vertices)
    graph_differential = None
    subsets = calculate_all_subsets(vertices)
    differential_groups = {}

    for s in subsets:
        this_neighbourhood = len(determine_neighbourhood(edges, vertices, s))
        this_differential = this_neighbourhood-len(s)

        if this_differential not in differential_groups:
            differential_groups[this_differential] = [s]
        else:
            if differential_groups != {}:
                differential_groups[this_differential].append(s)

        if graph_differential == None or graph_differential < this_differential:
            graph_differential = this_differential

    return (vertices, edges, differential_groups, graph_differential)

# GUI functions

def clear_text(entry):
    entry.delete('1.0', END)


def draw_square():
    global draw_square_matrix_entry, adj_matrix_entry
    clear_text(adj_matrix_entry)
    n = int(draw_square_matrix_entry.get())
    line = f'{", ".join(["0" for i in range(n)])}'
    for x in range(1,n+1):
        if x!=n:
            adj_matrix_entry.insert(END, line+';\n')
        elif x==n:
            adj_matrix_entry.insert(END, line)

        
def update_labels(table, labels=['g_info', 'dif_info', 'group_list']):
    labels[0].configure(text=f'No. of Vertices: {len(vertices)}\n\nNo. of Edges: {len(edges)}\n\nDifferential of G: {graph_differential}\n\nNo. of Differential Groups: {len(differential_groups)}\n\nTotal Possible Subsets: {total_subsets}')
    labels[1].configure(text=f'Differential Group in View:\n\nNo. of Subsets for Group ({labels[2].get()}): {len(differential_groups[int(labels[2].get())])}\n\nPeak Differential Groups are ({peak[0]}) with {(peak[1])} subsets.')

    table.delete(*table.get_children())

    for s in differential_groups[int(labels[2].get())]:
        this_neighbourhood = determine_neighbourhood(edges, vertices, list(s))
        table.insert('', index='end', values=(len(s), int(labels[2].get()), f'{list(s)}', f'{this_neighbourhood}'))


def compute(entry, labels=['g_info', 'dif_info', 'group_list']):
    global vertices, edges, differential_groups, graph_differential, diff_table, adj_matrix_entry
    global total_subsets, peak, entry_csv

    text = entry.get('1.0', END)
    for c in text:
        if c == ' ' or c=='\n':
            text = text.replace(c, '')
    
    text = text.split(';')
    if '' in text:
        text.remove('')
    
    adjacency_matrix = np.zeros((len(text), len(text)), dtype=int)

    for i,r in enumerate(text): # checks only the lower triangular matrix, since graph is undirected
        for j,c in enumerate(r.split(',')):
            if c != '0':
                adjacency_matrix[i][j] = 1
                adjacency_matrix[j][i] = 1
    
    clear_text(adj_matrix_entry)
    for i,x in enumerate(adjacency_matrix, start=1):
        line = f'{", ".join([c for c in np.array_str(x).strip("[").strip("]") if c!=" "])}'
        if i!=np.size(x):
            adj_matrix_entry.insert(END, line+';\n')
        elif i==np.size(x):
            adj_matrix_entry.insert(END, line)
    
    vertices, edges, differential_groups, graph_differential = calculate_differentials(adjacency_matrix)
    labels[2].configure(values=[x for x in differential_groups])
    labels[2].current(0)

    peak = [[0], 0]
    for x in differential_groups:
        this = len(differential_groups[x])
        if this > peak[1]:
            peak = [[x], this]
        elif this == peak[1]:
            peak[0].append(x)


    total_subsets = 0
    n = len(vertices)
    for x in range(1, len(vertices)+1):
        total_subsets = int(total_subsets + factorial(n)/(factorial(x)*factorial(n-x)))

    entry_csv.delete(0, END)
    entry_csv.insert(END, f'{len(vertices)}, {len(edges)}, {graph_differential}, {len(differential_groups)}, {len(differential_groups[graph_differential])}, {total_subsets}, [{"; ".join([str(x) for x in peak[0]])}], {peak[1]}')

    update_labels(diff_table, labels)


def load_group(labels=['g_info', 'dif_info', 'group_list']):
    global diff_table
    update_labels(diff_table, labels)


def diff_vertices_info():
    global group_choice, vertices, differential_groups, edges

    window = Toplevel()
    window.geometry('400x400')
    window.resizable(width=False, height=False)
    window.title('differential vertices info')

    vertices_table = ttk.Treeview(window)
    vertices_table['columns'] = ('vertex', 'degree', 'occurrence')

    verscrlbar = ttk.Scrollbar(window, orient ="vertical", command=vertices_table.yview)
    verscrlbar.place(x=385, y=2, height=224)

    vertices_table.configure(yscrollcommand=verscrlbar.set)

    vertices_table.column('#0', width=0, minwidth=0, anchor='center')
    vertices_table.column('vertex', width=100, minwidth=10)
    vertices_table.column('degree', width=100, minwidth=10)
    vertices_table.column('occurrence', width=200, minwidth=10)

    vertices_table.heading('#0', text='')
    vertices_table.heading('vertex', text='Vertex')
    vertices_table.heading('degree', text='Degree')
    vertices_table.heading('occurrence', text='Occurrence')

    vertices_table.place(x=0, y=0)

    vertices_table.delete(*vertices_table.get_children())

    additional_info = ttk.Label(window, text='The values above refer to the unique vertices among all\nsubsets of the selected differential group.')
    additional_info.config(foreground='#0000ff')
    additional_info.place(x=10, y=350)

    unique_vertices = []
    group = differential_groups[int(group_choice.get())]
    
    for s in group:
        for v in s:
            if v not in [x[0] for x in unique_vertices if x[0]==v]:
                occurrence = len([x for x in group if v in x])
                degree = len([x for x in edges if v in x])
                unique_vertices.append((v, degree, occurrence))

    for v in unique_vertices:
        vertices_table.insert('', index='end', values=(v[0], v[1], v[2]))


root = Tk()
root.title('graph differential')
root.geometry('1300x450')
root.resizable(width=False, height=False)

global vertices, edges, differential_groups, graph_differential
vertices, edges, differential_groups, graph_differential, total_subsets = [], [], {}, int(), int()

frame1 = ttk.Frame(root, width=530, height=400, relief='groove')
frame1.place(x=30, y=10)

frame2 = ttk.Frame(root, width=650, height=400, relief='groove')
frame2.place(x=620, y=10)

# frame 1

adj_matrix_label = ttk.Label(frame1, text='Adjacency Matrix of G (undirected)')
adj_matrix_label.place(x=10, y=10)

adj_matrix_entry = ScrolledText(frame1)
adj_matrix_entry.configure(height=15, width=60, relief='solid', font=('arial', 11), )
adj_matrix_entry.place(x=10, y=40)

compute_btn = ttk.Button(frame1, text='Compute', command=lambda: Thread(target=compute(adj_matrix_entry, [graph_info, differential_info, group_choice]), daemon=True).start())
compute_btn.place(x=10, y=320)

clear_btn = ttk.Button(frame1, text='Clear', command=lambda: clear_text(adj_matrix_entry))
clear_btn.place(x=100, y=320)

draw_square_matrix_label = ttk.Label(frame1, text='Draw Zero Matrix (NxN):')
draw_square_matrix_label.place(x=260, y=320)

draw_square_matrix_entry = ttk.Entry(frame1, width=5)
draw_square_matrix_entry.place(x=400, y=320)

draw_square_matrix_btn = ttk.Button(frame1, text='Draw', width=6, command=draw_square)
draw_square_matrix_btn.place(x=450, y=318)

note_label = ttk.Label(frame1, text='Note: adjacency matrix input should be as a series of elements separated by commas.\nEach row is determined by a semicolon. Use the draw function to get an example.')
note_label.config(font=('Arial', 8), foreground='#0000ff')
note_label.place(x=10, y=350)

# frame 2

diff_table = ttk.Treeview(frame2)
diff_table['columns'] = ('length', 'sdiff', 'subset', 'neib')

verscrlbar = ttk.Scrollbar(frame2, orient ="vertical", command=diff_table.yview)
verscrlbar.place(x=631, y=2, height=224)

diff_table.configure(yscrollcommand=verscrlbar.set)

diff_table.column('#0', width=0, minwidth=0, anchor='center')
diff_table.column('subset', width=185, minwidth=10)
diff_table.column('sdiff', width=100, minwidth=10)
diff_table.column('length', width=80, minwidth=10)
diff_table.column('neib', width=281, minwidth=10)

diff_table.heading('#0', text='')
diff_table.heading('subset', text='Subset S')
diff_table.heading('sdiff', text='Diff(S)')
diff_table.heading('length', text='Card(S)')
diff_table.heading('neib', text='N[S]-\S')

diff_table.place(x=0, y=0)

graph_info = ttk.Label(frame2, text='No. of Vertices: None\n\nNo. of Edges: None\n\nDifferential of Graph G: None\n\nNo. of Differential Groups: None\n\nTotal Possible Subsets: None')
graph_info.place(x=10, y=240)

differential_info = ttk.Label(frame2, text='Differential Group in View:\n\nNo. of Subsets for Group: None\n\nPeak Differential Groups are (None) with 0 subsets.')
differential_info.place(x=300, y=240)

group_choice = ttk.Combobox(frame2, height=5, width=5)
group_choice.place(x=445, y=240)

load_group_btn = ttk.Button(frame2, text='Load Group', command=lambda: Thread(target=load_group([graph_info, differential_info, group_choice]), daemon=True).start())
load_group_btn.place(x=500, y=238)

see_group_vertices_btn = ttk.Button(frame2, text='Differential Vertices', command=diff_vertices_info)
see_group_vertices_btn.place(x=500, y=268)

csv_label = ttk.Label(frame2, text='Copy as CSV:')
csv_label.place(x=300, y=325)

entry_csv = ttk.Entry(frame2, width=30)
entry_csv.place(x=390, y=325)

help_label = ttk.Label(frame2, foreground='#0000ff', text='V(G), E(G), Diff(G), total_differential_groups, total_subsets_Diff(G),\ntotal_subsets, peak_differential_groups, total_subsets_for_peak')
help_label.configure(font=('Arial', 8))
help_label.place(x=300, y=350)

root.mainloop()
