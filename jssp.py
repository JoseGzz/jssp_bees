import networkx as nx
import random
import csv

dic = {'PUN':[], 'REST':[], 'ApVt':[], 'HyR': []}

class CPM(nx.DiGraph):
    def __init__(self):
        super().__init__()
        self._dirty = True
        self._makespan = -1
        self._criticalPath = None

    def add_node(self, *args, **kwargs):
        self._dirty = True
        super().add_node(*args, **kwargs)

    def add_nodes_from(self, *args, **kwargs):
        self._dirty = True
        super().add_nodes_from(*args, **kwargs)

    def add_edge(self, *args):  # , **kwargs):
        self._dirty = True
        super().add_edge(*args)  # , **kwargs)

    def add_edges_from(self, *args, **kwargs):
        self._dirty = True
        super().add_edges_from(*args, **kwargs)

    def remove_node(self, *args, **kwargs):
        self._dirty = True
        super().remove_node(*args, **kwargs)

    def remove_nodes_from(self, *args, **kwargs):
        self._dirty = True
        super().remove_nodes_from(*args, **kwargs)

    def remove_edge(self, *args):  # , **kwargs):
        self._dirty = True
        super().remove_edge(*args)  # , **kwargs)

    def remove_edges_from(self, *args, **kwargs):
        self._dirty = True
        super().remove_edges_from(*args, **kwargs)

    def _forward(self):
        for n in nx.topological_sort(self):
            S = max([self.node[j]['C']
                     for j in self.predecessors(n)], default=0)
            self.add_node(n, S=S, C=S + self.node[n]['p'])

    def _backward(self):
        for n in nx.topological_sort(self, reverse=True):
            Cp = min([self.node[j]['Sp']
                      for j in self.successors(n)], default=self._makespan)
            self.add_node(n, Sp=Cp - self.node[n]['p'], Cp=Cp)

    def _computeCriticalPath(self):
        G = set()
        for n in self:
            if self.node[n]['C'] == self.node[n]['Cp']:
                G.add(n)
        self._criticalPath = self.subgraph(G)

    @property
    def makespan(self):
        if self._dirty:
            self._update()
        return self._makespan

    @property
    def criticalPath(self):
        if self._dirty:
            self._update()
        return self._criticalPath

    def _update(self):
        self._forward()
        self._makespan = max(nx.get_node_attributes(self, 'C').values())
        self._backward()
        self._computeCriticalPath()
        self._dirty = False

def generate_nodes(processes):
    """genera un conjunto de nodos sin conexiones
    processes: lista de tuplas de la forma (id proceso, tiempo)"""
    graph_nodes = CPM() # creamos un nuevo objeto grafo
    for process in processes: # creamos los nodos con su id y tiempo
        graph_nodes.add_node(process[0], p=process[1])
    return graph_nodes

def generate_random_solution(graph_nodes, no_processes, no_requests):
    """generamos una solucion aleatoria agregando arcos a los nodos creados
    graph_nodes: grafo que contiene los nodos sin conexion
    no_processes: cantidad de procesos
    no_requests: cantidad de pedidos"""
    # obtenemos lista en orden de los nodos
    nodes = graph_nodes.nodes()
    # creamos lista de listas vacias para organizar el orden de los procesos en comun
    node_list = [[] for _ in range(no_processes)]
    # separamos los nodos de procesos que pertenecen a cada pedido 
    adjacency_list = [nodes[i:i + no_processes] for i in range(0, len(nodes), no_processes)]
    # creamos los arcos para unir los nodos en el orden establecido por el proceso
    for lst in adjacency_list:
        for i in range(len(lst)-1):
            graph_nodes.add_edges_from([(lst[i], lst[i+1])])
    # agrupamos los nodos que pertenecen a la misma operacion para asignarlas al azar
    nodes = graph_nodes.nodes()
    for i in range(len(node_list)):
        for j in range(i, len(nodes), no_processes):
            node_list[i].append(nodes[j])
    # asignar el orden de uso de cada estacion aleatoriamente
    for common_processes in node_list:
        random.shuffle(common_processes)
        for i in range(len(common_processes)-1):
            graph_nodes.add_edges_from([(common_processes[i], common_processes[i+1])])
    # regresamos el grafo con precedencias
    return graph_nodes, node_list

def perturbate_solution(graph, node_list, patch_size):
    """creamos una configuracion similar a la actual
    graph: el bjeto que representa al grafo
    node_list: configuracion de la solucion; lista con el orden de los procesos
    path_size: 'cantidad' de variabilidad"""
    # aplicambios patch_size cantidad de cambios
    while patch_size > 0:
        # seleccionamos un proceso aleatorio para modificar su orden
        selected_process = random.randint(0, len(node_list)-1)
        # obtenemos los nodos involucrados en el proceso seleccionado
        nodes = node_list[selected_process]
        #print(node_list)
        # creamos una lista de tuplas con esos nodos para eliminar sus conexiones
        tup_list = []
        for i in range(len(nodes)-1):
            tup_list.append((nodes[i], nodes[i+1]))
        # eliminamos las conexiones entre esos nodos
        graph.remove_edges_from(tup_list)
        # generamos un nuevo orden aleatorio
        random.shuffle(nodes)
        # creamos las conexiones nuevas en base al nuevo orden aleatorio
        for i in range(len(nodes)-1):
            graph.add_edges_from([(nodes[i], nodes[i+1])])
        patch_size -= 1
        # reemplazamos el orden de una operacion anterior con la actual
        node_list[selected_process] = nodes
    return graph, node_list


def read():
    inp = input("Introduzca el nombre del archivo: ")
    with open(inp) as f:
        reader = csv.reader(f, delimiter="\t")
        firstline = True
        contPun = 0
        contRest = 0
        contApVt = 0
        contHyR = 0
        contID = 0
        lista = []
        for i in reader:
            if firstline:
                firstline = False
            else:
                a = i[0].split(";");
                if(a[0] == 'pedido'):
                    contID += 1
                    lista.append((contID,contPun))
                    dic['PUN'].append(contID)
                    contID += 1
                    lista.append((contID,contRest))
                    dic['REST'].append(contID)
                    contID += 1
                    lista.append((contID,contApVt))
                    dic['ApVt'].append(contID)
                    contID += 1
                    lista.append((contID,contHyR))
                    dic['HyR'].append(contID)
                    contPun = 0
                    contRest = 0
                    contApVt = 0
                    contHyR = 0
                else:
                    listaAux = []
                    listaAux.extend([int(a[3]),int(a[10]),int(a[13])])
                    maximum = max(listaAux)
                    contPun = contPun + (int(a[0]) * maximum)
                    listaAux = []
                    listaAux.extend([int(a[2]),int(a[4]),int(a[5]),int(a[9]),int(a[11]),int(a[12]),int(a[14])])
                    maximum = max(listaAux)
                    contRest = contRest + (int(a[0]) * maximum)
                    listaAux = []
                    listaAux.extend([int(a[6]),int(a[7])])
                    maximum = max(listaAux)
                    contApVt = contApVt + (int(a[0]) * maximum)
                    contHyR = contHyR + (int(a[0]) * int(a[8]))
    return lista

def write(lista_orden):
    counter = 0
    listaNUEVA = []
    listaPRUEBA = lista_orden
    listaPruebaPUN = listaPRUEBA[0]
    listaPruebaREST = listaPRUEBA[1]
    listaPruebaApVt = listaPRUEBA[2]
    listaPruebaHyR = listaPRUEBA[3]

    listaNuevaPUN = []
    listaNuevaPUN.append('PUN')
    for idCorr in listaPruebaPUN:
        counter = 0
        for id_proceso in dic['PUN']:
            if idCorr == id_proceso:
                desp = 'Pedido ' + str(counter+1)
                listaNuevaPUN.append(desp)
                break
            counter +=1

    listaNuevaREST = []
    listaNuevaREST.append('REST')
    for idCorr in listaPruebaREST:
        counter = 0
        for id_proceso in dic['REST']:
            if idCorr == id_proceso:
                desp = 'Pedido ' + str(counter+1)
                listaNuevaREST.append(desp)
                break
            counter +=1
    
    listaNuevaApVT = []
    listaNuevaApVT.append('ApVt')
    for idCorr in listaPruebaApVt:
        counter = 0
        for id_proceso in dic['ApVt']:
            if idCorr == id_proceso:
                desp = 'Pedido ' + str(counter+1)
                listaNuevaApVT.append(desp)
                break
            counter +=1

    listaNuevaHyR = []
    listaNuevaHyR.append('HyR')
    for idCorr in listaPruebaHyR:
        counter = 0
        for id_proceso in dic['HyR']:
            if idCorr == id_proceso:
                desp = 'Pedido ' + str(counter+1)
                listaNuevaHyR.append(desp)
                break
            counter +=1
        
    listaNUEVA.append(listaNuevaPUN)
    listaNUEVA.append(listaNuevaREST)
    listaNUEVA.append(listaNuevaApVT)
    listaNUEVA.append(listaNuevaHyR)
    cnt = 0
    for index in listaNUEVA:
        print(listaNUEVA[cnt])
        cnt += 1

# CLEVER ALGORITHM: Bees Algorithm
# Author: Santiago E. Conant-Pablos, October 6, 2015

def objective_function(graph):
    """returns value of function to optimize"""
    return graph.makespan

def create_random_bee(graph, no_processes, no_orders):
    """create a random bee position"""
    return generate_random_solution(graph, no_processes, no_orders)

def create_neigh_bee(graph, node_list, patch_size):
    """create a bee inside a neighborhood"""
    return perturbate_solution(graph, node_list, patch_size)

def search_neigh(parent, neigh_size, patch_size, node_list):
    """search inside the neighborhood of a site"""
    neigh = []
    for i in range(neigh_size):
        bee = list(create_neigh_bee(parent, node_list, patch_size))
        if len(bee) < 3: # si no se le ha asignado un fitness hay que hacerlo
            bee.append(objective_function(bee[0]))
        else: # de lo contrario solo hay que reemplazarlo
            bee[2] = objective_function(bee[0])
        neigh.append(bee)
    neigh.sort(key=lambda b: b[2])
    return neigh[0]

def create_scout_bees(requests, no_processes, no_orders, num_scouts):
    """creates scout bees for new sites"""
    return [create_random_bee(generate_nodes(requests), no_processes, no_orders) for i in range(num_scouts)]

def bees_algorithm(max_gens, requests, no_processes, num_bees, num_sites,
                   elite_sites, patch_size, patch_dec, e_bees, o_bees):
    """implements the Bees algorithm"""
    # el mejor encontrado
    best = None
    # creacion de una poblacion de soluciones aleatorias
    no_requests = int(len(requests)/no_processes)
    # pop[i] = (graph, solution, fitness); fitness se agrega en el for interno
    pop = [create_random_bee(generate_nodes(
        requests), no_processes, no_requests
    ) for i in range(num_bees)]
    # corre la optimizacion en terminos de generaciones
    for gen in range(max_gens):
        print_flag = False
        for bee in range(num_bees):
            pop[bee] = list(pop[bee])
            if len(pop[bee]) < 3:
                pop[bee].append(objective_function(pop[bee][0]))
            else:
                pop[bee][2] = objective_function(pop[bee][0])
        pop.sort(key = lambda b: b[2])
        if not best or pop[0][2] < best[2]:
            print_flag = True
            best = pop[0]
        next_gen = []
        for i, parent in enumerate(pop[:num_sites]):
            neigh_size = e_bees if i < elite_sites else o_bees
            next_gen.append(search_neigh(parent[0], neigh_size, patch_size, parent[1]))
        
        scouts = create_scout_bees(requests, no_processes, no_requests, num_bees - num_sites)
        pop = next_gen + scouts
        patch_size = patch_size * patch_dec
        if print_flag : print(" > it=%d, patch_size=%g, f=%g" % (gen+1,patch_size,best[2]))
    return best

# algorithm configuration
max_gens = 100 # maximun number of generations
num_bees = 45
num_sites = 3
elite_sites = 1
patch_size = 3.0
patch_dec = 0.95 # decrease of patch size in each generation
e_bees = 7    # number of elite bees
o_bees = 2    # number of other bees
no_jobs = 4 # cantidad de operaciones para ensamblaje (incluye varias en paralelo)
requests = read()#[(1,50),(2,3),(3,41),(4,94),(5,15),(6,13),(7,34),(8,29),(9,55),(10,73),(11,14),(12,91)]
best = bees_algorithm(max_gens, requests, no_jobs, num_bees, num_sites,
                      elite_sites, patch_size, patch_dec, e_bees, o_bees)
print("Done.\nBest Solution: f=%g" % (best[2]))
write(best[1])
