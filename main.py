import pygame
import sys
import random
import textwrap

pygame.init()

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Dimensiones de la pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600

# Configuración de la pantalla
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption('Juego de Penales')

# Cargar sonidos
sonido_aficion = pygame.mixer.Sound("aficion.wav")
sonido_atajada = pygame.mixer.Sound("atajada.wav")
sonido_gol = pygame.mixer.Sound("gol.wav")

# Reproducir sonido de fondo en bucle
sonido_aficion.play(-1)

# Cargar imágenes
fondo_campo = pygame.image.load("campoJuego.png")
arco_porteria = pygame.image.load("arcoPorteria.png")

# Tamaño del jugador
tamaño_jugador = (110, 268)  # Tamaño del jugador

# Cargar y escalar imágenes del jugador
sprites_jugador = [
    pygame.image.load("JugadorListoParaRematar.png"),
    pygame.image.load("JugadorPosicionRemate.png"),
    pygame.image.load("JugadorRematando.png"),
    pygame.image.load("JugadorRemate.png")
]

for i in range(len(sprites_jugador)):
    sprites_jugador[i] = pygame.transform.scale(sprites_jugador[i], tamaño_jugador)

# Calcular el tamaño de la pelota como el 50% del tamaño del jugador
tamaño_pelota_inicial = (int(tamaño_jugador[0] * 0.5), int(tamaño_jugador[0] * 0.5))

# Asegurarse de que la pelota sea redonda (ancho y alto iguales)
tamaño_pelota_inicial = (tamaño_pelota_inicial[0], tamaño_pelota_inicial[0])

# Cargar y escalar la pelota
imagen_pelota_original = pygame.image.load("balon.png")
imagen_pelota_original = pygame.transform.scale(imagen_pelota_original, tamaño_pelota_inicial)

# Tamaño actual de la pelota (se irá modificando)
tamaño_pelota = tamaño_pelota_inicial[:]
imagen_pelota = imagen_pelota_original.copy()

# Tamaño del perro
tamaño_perro = (84, 105)   # Tamaño del perro

# Cargar imágenes del perro
imagen_perro_espera = pygame.image.load("borderCollieEspera.png")
imagen_perro_salto_izquierda = pygame.image.load("borderCollieSaltoIzquierda.png")
imagen_perro_lanzandose_izquierda = pygame.image.load("borderCollieLanzandoseIzquierda.png")
imagen_perro_salto_derecha = pygame.image.load("borderCollieSaltoDerecha.png")
imagen_perro_lanzandose_derecha = pygame.image.load("borderCollieLanzandoseDerecha.png")

# Escalar todas las imágenes del perro al mismo tamaño
imagenes_perro = [
    imagen_perro_espera,
    imagen_perro_salto_izquierda,
    imagen_perro_lanzandose_izquierda,
    imagen_perro_salto_derecha,
    imagen_perro_lanzandose_derecha
]

for i in range(len(imagenes_perro)):
    imagenes_perro[i] = pygame.transform.scale(imagenes_perro[i], tamaño_perro)

# Reasignar imágenes escaladas
imagen_perro_espera = imagenes_perro[0]
imagen_perro_salto_izquierda = imagenes_perro[1]
imagen_perro_lanzandose_izquierda = imagenes_perro[2]
imagen_perro_salto_derecha = imagenes_perro[3]
imagen_perro_lanzandose_derecha = imagenes_perro[4]

# Posiciones iniciales
jugador_x = 300
jugador_y = ALTO_PANTALLA - tamaño_jugador[1]

# Función para posicionar la pelota
def posicionar_pelota():
    global pelota_x, pelota_y, tamaño_pelota, imagen_pelota
    tamaño_pelota = tamaño_pelota_inicial[:]
    imagen_pelota = pygame.transform.scale(imagen_pelota_original, tamaño_pelota)
    pelota_x = jugador_x - (tamaño_jugador[0] * -0.85)
    pelota_y = jugador_y + tamaño_jugador[1] - (tamaño_jugador[1] * 0.10) - tamaño_pelota[1]

posicionar_pelota()

pelota_velocidad_x = 0
pelota_velocidad_y = 0 

# Posición inicial del perro
arco_x = 160
arco_y = 50
arco_ancho = 468
arco_alto = 208

perro_x = arco_x + (arco_ancho // 2) - (tamaño_perro[0] // 2)
perro_y = arco_y + arco_alto - tamaño_perro[1]

perro_velocidad_x = 0
perro_direccion = None
perro_lanzado = False

# Variables para la animación del jugador
jugador_frame = 0
animation_started = False
animation_index = 0
animation_time = 0
animation_delay = 200  # milisegundos entre frames

# Variables para controlar el remate
remate_iniciado = False
remate_realizado = False

# Área de gol
offset_x = (arco_ancho - 440) // 2
offset_y = (arco_alto - 191) // 2

area_gol = pygame.Rect(arco_x + offset_x, arco_y + offset_y, 440, 191)

# Umbrales para definir las zonas de remate
left_threshold = area_gol.left + area_gol.width / 3
right_threshold = area_gol.left + 2 * area_gol.width / 3

# Variables para aprendizaje del perro
shots_left = 1
shots_center = 1
shots_right = 1

# Variables del juego
gol = False

# Variable para acumular el desplazamiento de dirección
direction_offset = 0
max_offset = (area_gol.width / 2) - 10

# Inicializar el tiempo anterior
last_time = pygame.time.get_ticks()

# Variables para medir el tiempo de carga del remate
space_pressed_time = None
max_charge_time = 1000  # 1000 milisegundos (1 segundo)
exceeded_charge = False

# Variable para indicar si la pelota ha rebotado
pelota_rebotada = False

# Variables para el sistema de niveles
nivel = 1
intentos = 0
goles = 0
goles_minimos = 3  # Mínimo de goles para el nivel 1
tiempo_nivel = 120  # 120 segundos (2 minutos)
tiempo_restante = tiempo_nivel * 1000  # Convertir a milisegundos
inicio_nivel = pygame.time.get_ticks()
nivel_completado = False
juego_terminado = False

# Variables para pausar el juego
pausado = False

# Inicializar el reloj antes de llamar a la función
reloj = pygame.time.Clock()

# Texto de bienvenida
texto_bienvenida = [
    "¡Bienvenido a los lanzamientos de penales! Prepárate, porque nuestro guardián de la portería, Oblack, hará todo lo posible por detener cada uno de tus remates. ¿Estás listo para enfrentar al mejor? ¡Demuéstralo en el campo!",
    "",
    "Instrucciones del juego:",
    "",
    "- Espacio: Remata. Cuanto más tiempo mantengas presionada la barra espaciadora, mayor será la potencia del disparo.",
    "- Flechas ← →: Controla la dirección de tu penal.",
    "- P: Pausar el juego.",
    "- Enter: Reanudar el juego después de la pausa.",
    "",
    "Tienes 120 segundos para marcar la mayor cantidad de goles posibles, dependiendo del nivel en el que te encuentres.",
    "",
    "Presiona Enter para continuar...",
    "",
    "¿Podrás superar el desafío? ¡Vamos a descubrirlo!"
]

# Función para envolver el texto
def dibujar_texto_envoltura(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    line_spacing = -2

    # Obtener las líneas de texto
    font_height = font.size("Tg")[1]
    lines = []
    for texto in text:
        texto_lineas = textwrap.wrap(texto, width=60)
        lines.extend(texto_lineas)
        lines.append("")  # Añadir línea vacía entre párrafos

    for line in lines:
        if line == "":
            y += font_height + line_spacing  # Añadir espacio entre párrafos
            continue
        if y + font_height > rect.bottom:
            break
        if bkg:
            image = font.render(line, 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(line, aa, color)

        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing

# Mostrar pantalla de bienvenida
def mostrar_pantalla_bienvenida():
    pantalla.fill(NEGRO)

    # Calcular tamaño de fuente dinámicamente
    font_size = 24  # Tamaño base
    max_height = ALTO_PANTALLA - 100  # Espacio vertical disponible
    max_width = ANCHO_PANTALLA - 100  # Espacio horizontal disponible

    # Crear fuente
    font_bienvenida = pygame.font.Font(None, font_size)

    # Calcular altura total del texto
    font_height = font_bienvenida.size("Tg")[1]
    total_lines = sum([len(textwrap.wrap(linea, width=60)) + 1 for linea in texto_bienvenida])  # +1 para líneas vacías
    total_height = total_lines * (font_height - 2)

    # Ajustar tamaño de fuente si es necesario
    while total_height > max_height:
        font_size -= 1
        font_bienvenida = pygame.font.Font(None, font_size)
        font_height = font_bienvenida.size("Tg")[1]
        total_height = total_lines * (font_height - 2)

    rect_texto = pygame.Rect(50, 50, ANCHO_PANTALLA - 100, ALTO_PANTALLA - 100)
    dibujar_texto_envoltura(pantalla, texto_bienvenida, BLANCO, rect_texto, font_bienvenida)

    pygame.display.flip()
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando = False
        reloj.tick(60)

mostrar_pantalla_bienvenida()

# Ciclo principal del juego
while True:
    if not pausado:
        pantalla.fill(NEGRO)
        pantalla.blit(fondo_campo, (0, 0))
        pantalla.blit(arco_porteria, (arco_x, arco_y))

        # Calcular tiempo restante
        tiempo_transcurrido = pygame.time.get_ticks() - inicio_nivel
        tiempo_restante = (tiempo_nivel * 1000) - tiempo_transcurrido

        # Mostrar tiempo restante y goles en pantalla
        font_info = pygame.font.Font(None, 36)
        texto_tiempo = font_info.render(f"Tiempo restante: {int(tiempo_restante / 1000)} s", True, BLANCO)
        texto_goles = font_info.render(f"Goles: {goles}/{goles_minimos}", True, BLANCO)
        texto_nivel = font_info.render(f"Nivel: {nivel}", True, BLANCO)
        pantalla.blit(texto_tiempo, (10, 10))
        pantalla.blit(texto_goles, (10, 50))
        pantalla.blit(texto_nivel, (10, 90))

        # Si el tiempo se ha agotado
        if tiempo_restante <= 0 and not nivel_completado and not juego_terminado:
            intentos += 1
            if intentos < 3:
                # Reiniciar nivel
                goles = 0
                inicio_nivel = pygame.time.get_ticks()
                mensaje_intento = ["Primer intento", "Segundo intento", "Último intento"][intentos - 1]
                font_mensaje = pygame.font.Font(None, 74)
                texto_mensaje = font_mensaje.render(mensaje_intento, True, BLANCO)
                pantalla.blit(texto_mensaje, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 50))
                pygame.display.flip()
                pygame.time.wait(2000)
            else:
                # Reiniciar juego
                nivel = 1
                goles_minimos = 3
                intentos = 0
                goles = 0
                inicio_nivel = pygame.time.get_ticks()
                font_mensaje = pygame.font.Font(None, 74)
                texto_mensaje = font_mensaje.render("¡Has perdido!", True, BLANCO)
                pantalla.blit(texto_mensaje, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 50))
                pygame.display.flip()
                pygame.time.wait(3000)
            # Reiniciar variables del nivel
            posicionar_pelota()
            pelota_velocidad_x = pelota_velocidad_y = 0
            gol = False
            perro_lanzado = False
            perro_direccion = None
            direction_offset = 0
            perro_x = arco_x + (arco_ancho // 2) - (tamaño_perro[0] // 2)
            perro_velocidad_x = 0
            remate_iniciado = remate_realizado = False
            jugador_frame = animation_index = 0
            animation_started = False
            space_pressed_time = None
            exceeded_charge = False
            pelota_rebotada = False

        # Obtener el tiempo actual y calcular delta_time
        current_time = pygame.time.get_ticks()
        delta_time = current_time - last_time
        last_time = current_time

        teclas = pygame.key.get_pressed()

        # Ajustar direction_offset antes del remate
        if not remate_iniciado and not remate_realizado and not nivel_completado and not juego_terminado:
            if teclas[pygame.K_LEFT]:
                direction_offset -= (delta_time / 1000) * 400  # 400 píxeles por segundo a la izquierda
            if teclas[pygame.K_RIGHT]:
                direction_offset += (delta_time / 1000) * 400  # 400 píxeles por segundo a la derecha

            # Limitar direction_offset al máximo permitido
            if direction_offset < -max_offset:
                direction_offset = -max_offset
            elif direction_offset > max_offset:
                direction_offset = max_offset

        # Animación del jugador
        if animation_started:
            current_time = pygame.time.get_ticks()
            if current_time - animation_time >= animation_delay:
                animation_time = current_time
                jugador_frame = animation_index
                animation_index += 1
                if animation_index >= len(sprites_jugador):
                    animation_started = False
                    jugador_frame = 0
                    remate_realizado = True
                    remate_iniciado = False
                    # Iniciar movimiento de la pelota
                    target_x = area_gol.centerx + direction_offset
                    if exceeded_charge:
                        target_y = area_gol.top - 10
                    else:
                        target_y = area_gol.top + 10
                    # Calcular la velocidad basada en el tiempo de carga
                    velocidad = (charge_time / max_charge_time) * 4000  # Velocidad máxima de 4000 píxeles por segundo
                    if velocidad < 100:
                        velocidad = 100
                    # Calcular el vector dirección
                    dx = target_x - pelota_x
                    dy = target_y - pelota_y
                    distancia = (dx**2 + dy**2) ** 0.5
                    if distancia != 0:
                        pelota_velocidad_x = (dx / distancia) * velocidad
                        pelota_velocidad_y = (dy / distancia) * velocidad
                    else:
                        pelota_velocidad_x = 0
                        pelota_velocidad_y = -velocidad
                    # Calcular el tiempo que tardará la pelota en llegar al objetivo
                    tiempo_balon = distancia / velocidad
                    # Ajustar la decisión del perro basándose en la dirección real del remate
                    # Actualizar las probabilidades con suavizado de Laplace
                    total_shots = shots_left + shots_center + shots_right
                    prob_left = (shots_left + 1) / (total_shots + 3)
                    prob_center = (shots_center + 1) / (total_shots + 3)
                    prob_right = (shots_right + 1) / (total_shots + 3)
                    # Determinar la zona real del remate
                    if target_x < left_threshold:
                        real_shot_zone = "izquierda"
                    elif target_x > right_threshold:
                        real_shot_zone = "derecha"
                    else:
                        real_shot_zone = "centro"
                    # Ajustar la decisión del perro
                    if random.random() < 0.7:  # 70% de probabilidad de seguir la estadística
                        perro_direccion = real_shot_zone
                    else:
                        # 30% de probabilidad de elegir al azar basado en las probabilidades aprendidas
                        random_value = random.random()
                        if random_value < prob_left:
                            perro_direccion = "izquierda"
                        elif random_value < prob_left + prob_center:
                            perro_direccion = "centro"
                        else:
                            perro_direccion = "derecha"
                    # Calcular la posición objetivo del perro
                    if perro_direccion == "izquierda":
                        perro_target_x = arco_x
                    elif perro_direccion == "derecha":
                        perro_target_x = arco_x + arco_ancho - tamaño_perro[0]
                    else:
                        perro_target_x = arco_x + (arco_ancho // 2) - (tamaño_perro[0] // 2)
                    # Calcular la velocidad del perro para llegar a su posición objetivo
                    dx_perro = perro_target_x - perro_x
                    if tiempo_balon > 0:
                        perro_velocidad_x = dx_perro / tiempo_balon
                    else:
                        perro_velocidad_x = 0
                else:
                    jugador_frame = animation_index
        else:
            jugador_frame = 0

        # Movimiento de la pelota después del remate
        if remate_realizado:
            # Calcular desplazamiento basado en delta_time
            desplazamiento_x = pelota_velocidad_x * (delta_time / 1000)
            desplazamiento_y = pelota_velocidad_y * (delta_time / 1000)
            pelota_x += desplazamiento_x
            pelota_y += desplazamiento_y

            # Si es gol, la pelota continúa disminuyendo de tamaño hasta llegar a la parte inferior del arco
            if gol:
                # Continuar disminuyendo el tamaño de la pelota en un 1% cada frame
                tamaño_pelota = (int(tamaño_pelota[0] * 0.99), int(tamaño_pelota[1] * 0.99))
                if tamaño_pelota[0] < 5:
                    tamaño_pelota = (5, 5)  # Tamaño mínimo
                imagen_pelota = pygame.transform.scale(imagen_pelota_original, tamaño_pelota)

            # Si la pelota fue atajada y rebotó, aumentar su tamaño conforme regresa
            if pelota_rebotada and not gol:
                # Incrementar el tamaño de la pelota en un 1% cada frame
                tamaño_pelota = (int(tamaño_pelota[0] * 1.01), int(tamaño_pelota[1] * 1.01))
                if tamaño_pelota[0] > tamaño_pelota_inicial[0]:
                    tamaño_pelota = tamaño_pelota_inicial
                imagen_pelota = pygame.transform.scale(imagen_pelota_original, tamaño_pelota)

            # Movimiento del perro
            if perro_lanzado:
                desplazamiento_perro_x = perro_velocidad_x * (delta_time / 1000)
                perro_x += desplazamiento_perro_x
                # Limitar el movimiento del perro dentro del arco
                if perro_x < arco_x:
                    perro_x = arco_x
                    perro_velocidad_x = 0
                elif perro_x > arco_x + arco_ancho - tamaño_perro[0]:
                    perro_x = arco_x + arco_ancho - tamaño_perro[0]
                    perro_velocidad_x = 0
                # Animación del perro
                if perro_velocidad_x < 0:
                    pantalla.blit(imagen_perro_lanzandose_izquierda, (perro_x, perro_y))
                elif perro_velocidad_x > 0:
                    pantalla.blit(imagen_perro_lanzandose_derecha, (perro_x, perro_y))
                else:
                    pantalla.blit(imagen_perro_espera, (perro_x, perro_y))
            else:
                pantalla.blit(imagen_perro_espera, (perro_x, perro_y))

            # Dibujar el jugador antes de verificar colisiones para que no desaparezca
            pantalla.blit(sprites_jugador[0], (jugador_x, jugador_y))

            # Dibujar la pelota
            pantalla.blit(imagen_pelota, (pelota_x, pelota_y))

            # Detectar colisión con el perro
            rect_pelota = pygame.Rect(pelota_x, pelota_y, tamaño_pelota[0], tamaño_pelota[1])
            rect_perro = pygame.Rect(perro_x, perro_y, tamaño_perro[0], tamaño_perro[1])

            if rect_pelota.colliderect(rect_perro) and not pelota_rebotada:
                # El perro ataja la pelota
                # Efecto de rebote
                pelota_velocidad_x = -pelota_velocidad_x * 0.5  # Invertir y reducir velocidad
                pelota_velocidad_y = -pelota_velocidad_y * 0.5

                pelota_rebotada = True  # Indicar que la pelota ha rebotado

                # Reproducir sonido de atajada
                sonido_atajada.play()

                # Actualizar aprendizaje
                if target_x < left_threshold:
                    shots_left += 1
                elif target_x > right_threshold:
                    shots_right += 1
                else:
                    shots_center += 1

                # No mostrar "¡Atajado!" inmediatamente, lo haremos después del rebote

            elif area_gol.colliderect(rect_pelota) and not pelota_rebotada:
                gol = True
                pelota_velocidad_x = pelota_velocidad_y = 0
                pantalla.blit(imagen_pelota, (pelota_x, pelota_y))
                font = pygame.font.Font(None, 74)
                texto_gol = font.render("¡Gol!", True, BLANCO)
                pantalla.blit(texto_gol, (350, 250))

                # Reproducir sonido de gol
                sonido_gol.play()

                pygame.display.flip()
                pygame.time.wait(1000)

                # Actualizar aprendizaje
                if target_x < left_threshold:
                    shots_left += 1
                elif target_x > right_threshold:
                    shots_right += 1
                else:
                    shots_center += 1

                # Incrementar contador de goles
                goles += 1

                # Verificar si se ha completado el nivel
                if goles >= goles_minimos:
                    nivel_completado = True
                    font_mensaje = pygame.font.Font(None, 74)
                    texto_nivel_completado = font_mensaje.render("¡Nivel completado!", True, BLANCO)
                    pantalla.blit(texto_nivel_completado, (ANCHO_PANTALLA // 2 - 200, ALTO_PANTALLA // 2 - 50))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    # Preparar para el siguiente nivel
                    nivel += 1
                    goles_minimos += 1  # Aumentar el mínimo de goles en 1
                    intentos = 0
                    goles = 0
                    inicio_nivel = pygame.time.get_ticks()
                    nivel_completado = False

                # Reiniciar variables después de mostrar el mensaje
                jugador_y = ALTO_PANTALLA - tamaño_jugador[1]
                posicionar_pelota()
                pelota_velocidad_x = pelota_velocidad_y = 0
                gol = False
                perro_lanzado = False
                perro_direccion = None
                direction_offset = 0
                perro_x = arco_x + (arco_ancho // 2) - (tamaño_perro[0] // 2)
                perro_velocidad_x = 0
                remate_iniciado = remate_realizado = False
                jugador_frame = animation_index = 0
                animation_started = False
                space_pressed_time = None
                exceeded_charge = False
                pelota_rebotada = False  # Por si acaso

            # Verificar si la pelota salió fuera de los límites
            elif pelota_y < -30 or pelota_y > ALTO_PANTALLA + 30 or pelota_x < -30 or pelota_x > ANCHO_PANTALLA + 30:
                # La pelota salió fuera, reiniciar el juego
                pelota_velocidad_x = pelota_velocidad_y = 0

                # Mostrar "¡Atajado!" después del rebote y antes de reiniciar
                if pelota_rebotada:
                    pantalla.blit(imagen_pelota, (pelota_x, pelota_y))
                    font = pygame.font.Font(None, 74)
                    texto_ataj = font.render("¡Atajado!", True, BLANCO)
                    pantalla.blit(texto_ataj, (350, 250))

                    # Reproducir sonido de atajada
                    sonido_atajada.play()

                    pygame.display.flip()
                    pygame.time.wait(1000)

                # Reiniciar variables después de mostrar el mensaje
                jugador_y = ALTO_PANTALLA - tamaño_jugador[1]
                posicionar_pelota()
                pelota_velocidad_x = pelota_velocidad_y = 0
                gol = False
                perro_lanzado = False
                perro_direccion = None
                direction_offset = 0
                perro_x = arco_x + (arco_ancho // 2) - (tamaño_perro[0] // 2)
                perro_velocidad_x = 0
                remate_iniciado = remate_realizado = False
                jugador_frame = animation_index = 0
                animation_started = False
                space_pressed_time = None
                exceeded_charge = False
                pelota_rebotada = False

        else:
            # Dibujar el jugador
            pantalla.blit(sprites_jugador[jugador_frame], (jugador_x, jugador_y))

            # Dibujar la pelota
            pantalla.blit(imagen_pelota, (pelota_x, pelota_y))

            pantalla.blit(imagen_perro_espera, (perro_x, perro_y))

    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Pausar y reanudar el juego
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_p:
                pausado = True
            elif evento.key == pygame.K_RETURN and pausado:
                pausado = False
                # Ajustar inicio_nivel para que el tiempo no avance durante la pausa
                inicio_nivel += pygame.time.get_ticks() - current_time
            elif evento.key == pygame.K_SPACE and not remate_iniciado and not remate_realizado and not nivel_completado and not juego_terminado and not pausado:
                space_pressed_time = pygame.time.get_ticks()
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_SPACE and not remate_iniciado and not remate_realizado and not nivel_completado and not juego_terminado and not pausado:
                remate_iniciado = True
                animation_started = True
                animation_index = 1
                animation_time = pygame.time.get_ticks()
                # Calcular el tiempo que se mantuvo presionada la tecla Espacio
                charge_time = pygame.time.get_ticks() - space_pressed_time
                if charge_time > max_charge_time:
                    charge_time = max_charge_time
                    exceeded_charge = True
                else:
                    exceeded_charge = False
                # Reducir el tamaño de la pelota en un 10%
                tamaño_pelota = (int(tamaño_pelota[0] * 0.9), int(tamaño_pelota[1] * 0.9))
                imagen_pelota = pygame.transform.scale(imagen_pelota_original, tamaño_pelota)
                # Decidir dirección del perro basada en las probabilidades aprendidas
                total_shots = shots_left + shots_center + shots_right
                prob_left = shots_left / total_shots
                prob_center = shots_center / total_shots
                prob_right = shots_right / total_shots
                random_value = random.random()
                if random_value < prob_left:
                    perro_direccion = "izquierda"
                elif random_value < prob_left + prob_center:
                    perro_direccion = "centro"
                else:
                    perro_direccion = "derecha"
                perro_lanzado = True

    # Mostrar pantalla de pausa
    if pausado:
        font_pausa = pygame.font.Font(None, 74)
        texto_pausa = font_pausa.render("Juego en pausa", True, BLANCO)
        pantalla.blit(texto_pausa, (ANCHO_PANTALLA // 2 - 150, ALTO_PANTALLA // 2 - 50))
        pygame.display.flip()

    # Actualizar la pantalla
    if not pausado:
        pygame.display.flip()
    reloj.tick(60)
