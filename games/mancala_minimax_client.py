"""Mancala bot: client for the course game server that chooses moves with Minimax.

Based on the client skeleton provided in the DVA340 (Artificial Intelligence) course at
Mälardalen University; the AI logic (evaluation, Minimax search and move selection) is my own.
Usage: start the Mancala server first, then this client and an opponent bot.
"""

import socket
import numpy as np
import time
from multiprocessing.pool import ThreadPool
import os
from datetime import date

# Función heurística: evalúa qué tan bueno es el tablero calculando la diferencia de puntos.
def evaluate_board(boardGame, player):
    if player == 1:
        return boardGame[6] - boardGame[13] # Puntos J1 - Puntos J2
    else:
        return boardGame[13] - boardGame[6] # Puntos J2 - Puntos J1

# Algoritmo Minimax para predecir y elegir los mejores movimientos futuros
def minimax(boardGame, depth: int, is_maximazing: bool, currentTurn: int, myPlayer: int):

    # Caso base: si llegamos a la profundidad límite, devolvemos la evaluación del tablero actual
    if depth == 0:
        return evaluate_board(boardGame, myPlayer)

    # Buscamos todos los movimientos válidos en las 6 casillas posibles
    moves = []
    for move in range(1, 7):
        if correctPlay(move, boardGame, currentTurn) == 1:
            moves.append(move)

    # Si no hay más movimientos posibles, el juego terminó: devolvemos la puntuación final
    if len(moves) == 0:
        return evaluate_board(boardGame, myPlayer)

    # Lógica de Maximización (Turno de nuestro bot)
    if is_maximazing:
        best_score = -float('inf') # Empezamos con el peor escenario posible

        # Simulamos cada movimiento en una copia del tablero
        for move in moves:
            copy_to_simulate_play = list(boardGame)
            result = play(currentTurn, move, copy_to_simulate_play)

            # Si el movimiento es válido, llamamos recursivamente a minimax
            if result is not None:
                newBoardGame, newPlayerTurn = result
                maximizing_turn = (newPlayerTurn == myPlayer) # ¿Sigue siendo nuestro turno?
                score = minimax(newBoardGame, depth-1, maximizing_turn, newPlayerTurn, myPlayer)
                best_score = max(best_score, score) # Nos quedamos con la jugada que nos dé más puntos

        return best_score

    # Lógica de Minimización (Turno del oponente)
    else:
        worst_score = float('inf') # Empezamos asumiendo que el rival jugará perfecto

        # Simulamos los movimientos del oponente
        for move in moves:
            copy_to_simulate_play = list(boardGame)
            result = play(currentTurn, move, copy_to_simulate_play)

            if result is not None:
                newBoardGame, newPlayerTurn = result
                maximizing_turn = (newPlayerTurn == myPlayer)
                score = minimax(newBoardGame, depth-1, maximizing_turn, newPlayerTurn, myPlayer)
                worst_score = min(worst_score, score) # El rival elegirá la opción que nos deje con menos puntos

        return worst_score


# Función principal que decide qué movimiento hará el bot en este turno
def decide_move(boardIn, playerTurnIn):

    best_score = -float('inf')
    best_move = 1

    # Evaluamos las 6 opciones iniciales
    for move in range(1, 7):

        # Verificamos que se puedan tomar piedras de esa casilla
        if correctPlay(move, boardIn, playerTurnIn) == 1:

            # Creamos una copia para simular el movimiento sin afectar el tablero real
            copy_to_simulate_play = list(boardIn)
            result = play(playerTurnIn, move, copy_to_simulate_play)

            # Usamos Minimax (con profundidad 2) para ver las consecuencias futuras del movimiento
            if result is not None:
                newBoardGame, newPlayerTurn = result
                maximizing_turn = (newPlayerTurn == playerTurnIn)

                # Ejecutamos el árbol de búsqueda Minimax
                score = minimax(newBoardGame, 2, maximizing_turn, newPlayerTurn, playerTurnIn)

                # Actualizamos nuestra decisión si encontramos una jugada mejor
                if score > best_score:
                    best_score = score
                    best_move = move

    return str(best_move), "Mi_Super_Bot" # Devuelve el movimiento elegido y el nombre del bot


# Lógica oficial del juego de Mancala (distribución de piedras)
def play(playerTurn: int, playerMove: int, boardGame):
    if not correctPlay(playerMove, boardGame, playerTurn):
        print("Illegal move! break")
        return

    # Determina el índice de inicio basado en el jugador (0-5 para P1, 7-12 para P2)
    idx = playerMove -1 + (playerTurn-1)*7

    # Toma las piedras y vacía el hueco
    numStones:int  = boardGame[idx]
    boardGame[idx] = 0
    hand:int = numStones

    # Reparte las piedras una por una
    while hand > 0:
        idx = (idx +1) % 14
        # Salta la base de puntuación del oponente
        if idx == 13 - 7*(playerTurn-1):
            continue
        boardGame[idx] += 1
        hand -= 1

    # Regla de turno extra: si la última piedra cae en tu propia base de puntos
    nextTurn = 3 - playerTurn
    if idx == 6 + 7*(playerTurn-1):
        nextTurn = playerTurn

    # Regla de captura: si la última piedra cae en un hueco propio vacío, capturas las del oponente
    if boardGame[idx] == 1 and idx in range((playerTurn-1)*7,6+(playerTurn-1)*7):
        boardGame[idx] -= 1 # Quitas tu piedra
        boardGame[6+(playerTurn-1)*7] += 1 # La sumas a tu puntuación
        boardGame[6+(playerTurn-1)*7] += boardGame[12 - idx] # Sumas las piedras robadas al rival
        boardGame[12 - idx] = 0 # Vacías el hueco del rival

    return (boardGame, nextTurn)

# Verifica que el movimiento sea válido (casilla del 1 al 6 y que no esté vacía)
def correctPlay(playerMove:int, board, playerTurn):
    correct = 0
    if playerMove in range(1,7) and board[playerMove-1 + (playerTurn-1)*7] > 0:
        correct = 1
    return correct

# Utilidad para contar la puntuación relativa del jugador 1
def countScorePlayer1(boardGame):
    (p1s, p2s) = countPoints(boardGame)
    return int(p1s - p2s)

# Utilidad para obtener las bases de puntuación de ambos jugadores
def countPoints(boardGame):
    return (boardGame[6], boardGame[13])


# --- SECCIÓN DE COMUNICACIÓN POR SOCKETS ---
# Recibe mensajes del servidor
def receive(socket):
    msg = ''.encode()
    try:
        data = socket.recv(1024)
        msg += data
    except:
        pass
    return msg.decode()

# Envía mensajes al servidor
def send(socket, msg):
    socket.sendall(msg.encode())


# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL (CLIENTE)
# ==========================================
if __name__ == "__main__":
    startTime = date(2020, 11, 9)
    playerName = 'Jaime'
    host = '127.0.0.1'
    port = 30000
    s = socket.socket()
    pool = ThreadPool(processes=1)
    gameEnd = False
    MAX_RESPONSE_TIME = 20
    print('The player: ' + playerName + ' starts!')
    s.connect((host, port))
    print('The player: ' + playerName + ' connected!')
    while not gameEnd:
        async_result = pool.apply_async(receive, (s,))
        startTime = time.time()
        currentTime = 0
        received = 0
        data = []
        while received == 0 and currentTime < MAX_RESPONSE_TIME:
            time.sleep(0.01)
            if async_result.ready():
                data = async_result.get()
                received = 1
            currentTime = time.time() - startTime
        if received == 0:
            print('No response in ' + str(MAX_RESPONSE_TIME) + ' sec')
            gameEnd = 1
        if data == 'N':
            send(s, playerName)
        if data == 'E':
            gameEnd = 1
        if len(data) > 1:
            board = [0] * 14
            playerTurn = int(data[0])
            i = 0
            j = 1
            while i <= 13:
                board[i] = int(data[j]) * 10 + int(data[j + 1])
                i += 1
                j += 2
            (move, botname) = decide_move(board, playerTurn)
            send(s, move)
