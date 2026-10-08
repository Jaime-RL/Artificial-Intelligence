import numpy as np
import pandas as pd
import time




# --- DATA PREPARATION ---

def preparar_datos(ruta_archivo):
    # Cargar el dataset
    dataset = pd.read_csv(ruta_archivo).values
    
    # Mezclar los datos aleatoriamente
    np.random.shuffle(dataset)
    
    # Separar X (píxeles) e Y (etiquetas)
    Y = dataset[:, 0]
    X = dataset[:, 1:] 
    
    # Normalizar los píxeles al rango [0, 1]
    X = X / 255.0
    
    # Índices para la división (70% Train, 10% Val, 20% Test)
    total_filas = X.shape[0]
    limite_train = int(total_filas * 0.70)
    limite_val = limite_train + int(total_filas * 0.10)
    
    # Dividir los conjuntos
    X_train, Y_train = X[:limite_train], Y[:limite_train]
    X_val, Y_val = X[limite_train:limite_val], Y[limite_train:limite_val]
    X_test, Y_test = X[limite_val:], Y[limite_val:]
    
    return X_train, Y_train, X_val, Y_val, X_test, Y_test




# --- ACTIVATION FUNCTIONS ---

def sigmoid(x):
    x_seguro = np.clip(x, -500, 500)
    return 1.0 / (1.0 + np.exp(-x_seguro))

def sigmoid_derivative(x):
    return x * (1.0 - x)





# --- THE NEURAL NETWORK ---

class NeuralNetwork:
    
    
    def __init__(self, hidden_nodes=64):
        self.input_nodes = 784
        self.hidden_nodes = hidden_nodes
        self.output_nodes = 10
        
        # Conexiones de la Capa de Entrada a la Capa Oculta
        self.weights_input_to_hidden = np.random.rand(self.input_nodes, self.hidden_nodes) - 0.5
        self.bias_hidden = np.random.rand(1, self.hidden_nodes) - 0.5
        
        # Conexiones de la Capa Oculta a la Capa de Salida
        self.weights_hidden_to_output = np.random.rand(self.hidden_nodes, self.output_nodes) - 0.5
        self.bias_output = np.random.rand(1, self.output_nodes) - 0.5


    def forward(self, inputs):
        
        # --- CAPA OCULTA ---
        self.hidden_sum = np.dot(inputs, self.weights_input_to_hidden) + self.bias_hidden
        self.hidden_activation = sigmoid(self.hidden_sum)
        
        # --- CAPA DE SALIDA ---
        self.output_sum = np.dot(self.hidden_activation, self.weights_hidden_to_output) + self.bias_output
        
        # Softmax
        exp_values = np.exp(self.output_sum - np.max(self.output_sum, axis=1, keepdims=True))
        self.predictions = exp_values / np.sum(exp_values, axis=1, keepdims=True)
        
        return self.predictions
            
            
    def backward(self, inputs, targets, learning_rate):
        
        m = inputs.shape[0] 
        
        # Error capa de salida
        output_error = targets - self.predictions
        
        # Derivada capa oculta
        sigmoid_derivative = self.hidden_activation * (1.0 - self.hidden_activation)
        
        # Propagamos hacia atrás
        error_propagated = np.dot(output_error, self.weights_hidden_to_output.T)
        
        # Error final capa oculta
        hidden_error = sigmoid_derivative * error_propagated

        # Ajuste del learning rate
        learning_rate = learning_rate / m

        # --- ACTUALIZACIÓN  ---
        self.weights_hidden_to_output += learning_rate * np.dot(self.hidden_activation.T, output_error)
        self.bias_output += learning_rate * np.sum(output_error, axis=0, keepdims=True)

        self.weights_input_to_hidden += learning_rate * np.dot(inputs.T, hidden_error)
        self.bias_hidden += learning_rate * np.sum(hidden_error, axis=0, keepdims=True)        
        

    def train(self, inputs, targets, epochs, learning_rate):
        for epoch in range(epochs):
            predictions = self.forward(inputs)
            
            self.backward(inputs, targets, learning_rate) 
            
            if epoch % 100 == 0:
                error = np.mean(np.square(targets - predictions))
                
                # Calcular la precisión durante el entrenamiento
                predicciones_etiquetas = np.argmax(predictions, axis=1)
                etiquetas_reales = np.argmax(targets, axis=1)
                precision = np.mean(predicciones_etiquetas == etiquetas_reales) * 100
                
                print(f"Época {epoch} - Error: {error:.4f} - Precisión: {precision:.2f}%")





# --- FUNCIONES AUXILIARES ---

def one_hot_encoding(Y, num_clases=10):
    one_hot = np.zeros((Y.size, num_clases))
    one_hot[np.arange(Y.size), Y.astype(int)] = 1
    return one_hot

def calcular_precision(predicciones, etiquetas_reales):
    predicciones_etiquetas = np.argmax(predicciones, axis=1)
    precision = np.mean(predicciones_etiquetas == etiquetas_reales) * 100
    return precision






# --- EJECUCIÓN DEL PROGRAMA ---

if __name__ == "__main__":
    print("1. Cargando y preparando los datos...")
    X_train, Y_train, X_val, Y_val, X_test, Y_test = preparar_datos('Assignment5.csv')

    print("2. Aplicando One-Hot Encoding a las etiquetas de entrenamiento...")
    Y_train_encoded = one_hot_encoding(Y_train)

    print("3. Inicializando la Red Neuronal...")
    red = NeuralNetwork(hidden_nodes=128) 

    print("4. Entrenando la red... ")
    inicio = time.time() 
    
    epocas = 1500
    tasa_aprendizaje = 1.0 
    
    red.train(X_train, Y_train_encoded, epocas, tasa_aprendizaje)

    fin = time.time() 
    print(f"\nEl entrenamiento tardó: {(fin - inicio) / 60:.2f} minutos.")

    print("\n5. Evaluando en el conjunto de prueba (Test)...")
    predicciones_test = red.forward(X_test)
    precision_final = calcular_precision(predicciones_test, Y_test)

    print(f"Precisión final en el Test Set: {precision_final:.2f}%")