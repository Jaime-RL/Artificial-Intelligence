import math
import matplotlib.pyplot as plt
import random

# Lee el archivo .tsp y extrae las coordenadas de cada ciudad
def parse_cities(filename):
    cities = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            parts = line.split()
            node_id, x, y = int(parts[0]), float(parts[1]), float(parts[2])
            cities.append(City(node_id, x, y)) # Crea y guarda el objeto City
            
    return cities

# Representación básica de una ciudad
class City:
    def __init__(self, node_id, x_coord, y_coord):
        self.node_id = node_id
        self.x_coord = x_coord
        self.y_coord = y_coord
    
    def __repr__(self):
        return f"City(id={self.node_id}, x={self.x_coord}, y={self.y_coord})"

# Calcula la distancia euclidiana (línea recta) entre dos ciudades
def calculate_distance(city1, city2):
    return math.sqrt((city1.x_coord - city2.x_coord)**2 + (city1.y_coord - city2.y_coord)**2)



# ==========================================
# PARTE 1: ALGORITMO GENÉTICO (GA)
# ==========================================
class GeneticAlgorithmTSP:
    def __init__(self, cities, pop_size=100, crossover_rate=0.8, mutation_rate=0.05, max_evals=250000):
        # Fija la primera ciudad como inicio/fin y el resto como ciudades a ordenar
        self.start_city = next(c for c in cities if c.node_id == 1)
        self.evolving_cities = [c for c in cities if c.node_id != 1]
        
        # Parámetros del algoritmo
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.max_evals = max_evals
        self.eval_count = 0
        
        self.best_fitness_history = []
        self.best_distance_history = []


    # Genera la primera generación de rutas aleatorias
    def create_initial_population(self):
        population = []
        for _ in range(self.pop_size):
            route = self.evolving_cities.copy()
            random.shuffle(route)
            population.append(route)
        return population


    # Calcula la distancia de la ruta y asigna un puntaje (a menor distancia, mayor fitness)
    def evaluate_fitness(self, route):
        self.eval_count += 1
        full_route = [self.start_city] + route + [self.start_city]
        
        total_dist = 0.0
        for i in range(len(full_route) - 1):
            total_dist += calculate_distance(full_route[i], full_route[i+1])
            
        fitness_score = 10000.0 / total_dist
        return fitness_score, total_dist


    # Elige aleatoriamente 'k' rutas y se queda con la de mejor fitness
    def tournament_selection(self, population, fitness_scores, k=3):
        selected_indices = random.sample(range(len(population)), k)
        best_idx = selected_indices[0]
        best_score = fitness_scores[best_idx]

        for idx in selected_indices[1:]:
            current_score = fitness_scores[idx]
            if current_score > best_score:
                best_idx = idx
                best_score = current_score

        selected_route = population[best_idx]
        return selected_route


    # Combina dos rutas padres para crear una hija (Order Crossover) sin repetir ciudades
    def order_crossover(self, parent1, parent2):
        if random.random() > self.crossover_rate:
            return parent1.copy()

        size = len(parent1)
        child = [None] * size
        
        # Copia un segmento aleatorio del padre 1
        start, end = sorted(random.sample(range(size), 2))
        child[start:end] = parent1[start:end]
        
        # Rellena los huecos con el orden del padre 2
        p2_filtered = [city for city in parent2 if city not in child]
        fill_idx = 0
        for i in range(size):
            if child[i] is None:
                child[i] = p2_filtered[fill_idx]
                fill_idx += 1
                
        return child


    # Invierte un segmento aleatorio de la ruta para introducir variedad
    def order_mutation(self, route):
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(len(route)), 2)
            if idx1 > idx2:
                idx1, idx2 = idx2, idx1

            segment_to_reverse = route[idx1:idx2 + 1]
            reversed_segment = list(reversed(segment_to_reverse))
            route[idx1:idx2 + 1] = reversed_segment
            
        return route
    
    
    # Bucle principal de evolución
    def run(self):
      
        population = self.create_initial_population()
        best_overall_route = None
        best_overall_dist = float('inf')
        generation = 0
        
        while self.eval_count < self.max_evals:
            # Evalúa toda la población actual
            evaluations = [self.evaluate_fitness(ind) for ind in population]
            fitness_scores = [eval[0] for eval in evaluations]
            distances = [eval[1] for eval in evaluations]
            
            gen_best_fitness = max(fitness_scores)
            gen_best_dist = min(distances)
            best_idx = distances.index(gen_best_dist)
            
            self.best_fitness_history.append(gen_best_fitness)
            self.best_distance_history.append(gen_best_dist)
            
            # Guarda la mejor ruta global encontrada hasta el momento
            if gen_best_dist < best_overall_dist:
                best_overall_dist = gen_best_dist
                best_overall_route = population[best_idx]
                print(f"GA -> Generación {generation} | Mejor Distancia: {best_overall_dist:.2f}")

            # Crea la nueva generación (elitismo: guarda al mejor)
            new_population = []
            new_population.append(population[best_idx])
            
            # Llena el resto de la población con cruces y mutaciones
            while len(new_population) < self.pop_size:
                p1 = self.tournament_selection(population, fitness_scores)
                p2 = self.tournament_selection(population, fitness_scores)
                
                child = self.order_crossover(p1, p2)
                child = self.order_mutation(child)
                new_population.append(child)
                
            population = new_population
            generation += 1

        return best_overall_route, best_overall_dist



# ==========================================
# PARTE 2: ANT COLONY OPTIMIZATION (ACO)
# ==========================================
class AntColonyTSP:
    def __init__(self, ciudades, num_hormigas=40, num_iteraciones=200, alpha=1.0, beta=5.0, evaporation=0.5):
        self.ciudades = ciudades
        self.num_hormigas = num_hormigas
        self.num_iteraciones = num_iteraciones
        
        self.alpha = alpha       # Importancia de las feromonas
        self.beta = beta         # Importancia de la distancia (visibilidad)
        self.evaporation = evaporation # Tasa de evaporación
        
        self.n = len(ciudades)
        
        # Matrices para guardar distancias, visibilidad (eta) y feromonas (tau)
        self.dist = [[0.0 for _ in range(self.n)] for _ in range(self.n)]
        self.eta = [[0.0 for _ in range(self.n)] for _ in range(self.n)]
        self.tau = [[10.0 for _ in range(self.n)] for _ in range(self.n)] # Feromona inicial
        
        # Pre-calcula distancias y visibilidad entre todas las ciudades
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    d = calculate_distance(self.ciudades[i], self.ciudades[j])
                    self.dist[i][j] = d
                    self.eta[i][j] = 1.0 / d if d > 0 else 0.0 # Más cerca = más visible
                    
        self.history_best_distances = []
        
    def ejecutar(self):     
        mejor_distancia_global = float('inf')
        mejor_ruta_global = None
        
        # Bucle principal de iteraciones
        for iteracion in range(self.num_iteraciones):
            rutas_iteracion = []
            
            # Cada hormiga construye una ruta
            for ant in range(self.num_hormigas):
                ruta = [0]
                visitado = {0}
                ciudad_actual = 0
                
                # Construye la ruta paso a paso hasta visitar todas las ciudades
                while len(visitado) < self.n:
                    suma_pesos = 0.0
                    options = []
                    
                    # Evalúa opciones basadas en feromonas y distancia
                    for j in range(self.n): 
                        if j not in visitado:
                            peso = (self.tau[ciudad_actual][j] ** self.alpha) * (self.eta[ciudad_actual][j] ** self.beta)
                            suma_pesos += peso
                            options.append((j, peso))    
                    
                    # Selección probabilística de la siguiente ciudad (Ruleta)
                    valor_aleatorio = random.uniform(0, suma_pesos)
                    acumulado = 0.0
                    for option in options:
                        index, peso = option
                        acumulado += peso
                        if acumulado >= valor_aleatorio:
                            siguiente_ciudad = index
                            break
                    
                    ruta.append(siguiente_ciudad)
                    visitado.add(siguiente_ciudad)
                    ciudad_actual = siguiente_ciudad
                    
                ruta.append(0) # Regresa a la ciudad de origen
                rutas_iteracion.append(ruta)
            
            # --- EVALUACIÓN DE LAS RUTAS DE ESTA ITERACIÓN ---
            mejor_distancia_iteracion = float('inf') 
            distancias_iteracion = [] 
            
            for ruta in rutas_iteracion:
                distancia_ruta = 0.0 
                for i in range(len(ruta) - 1):
                    distancia_ruta += self.dist[ruta[i]][ruta[i+1]]
                distancias_iteracion.append(distancia_ruta)
                    
                if distancia_ruta < mejor_distancia_iteracion:
                    mejor_distancia_iteracion = distancia_ruta
                if distancia_ruta < mejor_distancia_global:
                    mejor_distancia_global = distancia_ruta
                    mejor_ruta_global = ruta 
                    
            self.history_best_distances.append(mejor_distancia_global)
            
            if (iteracion + 1) % 10 == 0 or iteracion == 0:
                print(f"ACO -> Iteración {iteracion+1} | Mejor global: {mejor_distancia_global:.2f}")

            # --- ACTUALIZACIÓN DE FEROMONAS ---
            # 1. Evaporación: disminuye el rastro en todos los caminos
            for i in range(self.n):
                for j in range(self.n):
                    self.tau[i][j] *= (1.0 - self.evaporation)
                    
            # 2. Aporte: las hormigas dejan más feromonas en las rutas más cortas
            for idx, ruta in enumerate(rutas_iteracion):
                distancia_ruta = distancias_iteracion[idx] 
                aporte_pheromones = 1.0 / distancia_ruta
                
                for i in range(len(ruta) - 1):
                    origen = ruta[i]
                    destino = ruta[i+1]
                    self.tau[origen][destino] += aporte_pheromones
                    self.tau[destino][origen] += aporte_pheromones 
                    
        print("\n¡Evolución ACO completada!")
        return mejor_ruta_global, mejor_distancia_global                



# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    cities = parse_cities('berlin52.tsp') # Carga los datos
    
    # Ejecuta el Algoritmo Genético
    print("="*40)
    print(" EJECUTANDO ALGORITMO GENÉTICO (GA) ")
    print("="*40)
    ga = GeneticAlgorithmTSP(cities, pop_size=300, crossover_rate=0.90, mutation_rate=0.15)
    best_route_ga, best_dist_ga = ga.run()
    
    # Ejecuta la Optimización de Colonia de Hormigas
    print("\n" + "="*40)
    print(" EJECUTANDO ANT COLONY OPTIMIZATION (ACO) ")
    print("="*40)
    aco = AntColonyTSP(cities, num_hormigas=40, num_iteraciones=200, alpha=1.0, beta=5.0, evaporation=0.5)
    best_route_aco, best_dist_aco = aco.ejecutar()
    
    # GRAFICAR LOS RESULTADOS DE AMBOS ALGORITMOS
    plt.figure(figsize=(12, 5))
    
    # Gráfica de convergencia para GA
    plt.subplot(1, 2, 1)
    plt.plot(ga.best_distance_history, color='blue')
    plt.axhline(y=9000, color='red', linestyle='--', label='Límite Tarea (9000)') # Línea objetivo
    plt.title(f'Algoritmo Genético\nDistancia Final: {best_dist_ga:.2f}')
    plt.xlabel('Generaciones')
    plt.ylabel('Distancia Total')
    plt.legend()
    plt.grid(True)
    
    # Gráfica de convergencia para ACO
    plt.subplot(1, 2, 2)
    plt.plot(aco.history_best_distances, color='purple')
    plt.axhline(y=9000, color='red', linestyle='--', label='Límite Tarea (9000)') # Línea objetivo
    plt.title(f'Optimización Colonia Hormigas\nDistancia Final: {best_dist_aco:.2f}')
    plt.xlabel('Iteraciones')
    plt.ylabel('Distancia Total')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show() # Muestra los resultados visuales finales
