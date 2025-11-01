🧩 Sistema Distribuido Cliente-Servidor con Python

Este proyecto implementa un sistema distribuido sencillo en Python que simula el envío, distribución y procesamiento de tareas entre clientes, un servidor y varios workers (hilos).

Permite que múltiples clientes envíen tareas al servidor por medio de sockets TCP, y que éstas sean procesadas de forma concurrente por un pool de hilos (workers).
Cada resultado se devuelve automáticamente al cliente correspondiente.

🚀 Características principales

Arquitectura cliente-servidor distribuida.

Comunicación por sockets TCP.

Manejo concurrente de clientes y tareas con hilos (threading).

Cola de tareas y resultados gestionada internamente.

Ejemplo de procesamiento: operación "square" (cuadrado de un número).

Código simple, funcional y 100% ejecutable.

Compatible con Python 3.8+.

🧠 Arquitectura general
flowchart LR
    A[Clientes (CLI)] --> B[Servidor principal]
    B --> C1[Worker 1 (hilo)]
    B --> C2[Worker 2 (hilo)]
    B --> C3[Worker 3 (hilo)]
    C1 -->|resultados| B
    C2 -->|resultados| B
    C3 -->|resultados| B
    B -->|envía resultados| A


Cliente: envía una tarea al servidor (por ejemplo, calcular el cuadrado de un número).

Servidor: recibe las tareas, las asigna a una cola y las distribuye entre los workers.

Workers: ejecutan la tarea y devuelven el resultado al servidor.

Servidor → Cliente: retorna el resultado final.

📁 Estructura del proyecto
pfo3_cliente_servidor/
└── sistema_distribuido/
    ├── servidor/
    │   └── server.py
    └── cliente/
        └── client.py

⚙️ Requisitos previos

Python 3.8 o superior

Librerías estándar (no requiere instalación de dependencias externas)

Recomendado: Visual Studio Code o cualquier IDE con terminal

▶️ Cómo ejecutar el sistema
1️⃣ Iniciar el servidor

En una terminal (ubicado en la raíz del proyecto):

python sistema_distribuido/servidor/server.py


Verás en la consola:

[server] listening on 0.0.0.0:5000
[server] 4 worker threads started
[dispatcher] started


El servidor queda esperando clientes.

2️⃣ Ejecutar el cliente

Abrí otra terminal (dejá el servidor corriendo) y ejecutá:

python sistema_distribuido/cliente/client.py


El programa pedirá un payload (dato o JSON).
Podés ingresar:

{"op": "square", "n": 5}


Resultado esperado:

[client] tarea encolada id=2f83c9a9-...
Esperando resultado...
[client] resultado recibido: 25

💡 Ejemplo rápido sin input manual

También podés ejecutar el cliente pasando la tarea directamente como argumento:

python sistema_distribuido/cliente/client.py "{\"op\": \"square\", \"n\": 7}"


Resultado:

[client] tarea encolada id=xxxx
Esperando resultado...
[client] resultado recibido: 49

🔧 Configuración opcional

Podés modificar las constantes en la parte superior de los archivos:

HOST: dirección IP del servidor (por defecto "127.0.0.1" o "0.0.0.0")

PORT: puerto TCP usado (por defecto 5000)

WORKER_COUNT: cantidad de hilos de procesamiento

RECV_TIMEOUT: tiempo máximo de espera del cliente

📜 Ejemplo de flujo completo

1️⃣ Iniciás el servidor (server.py).
2️⃣ El cliente se conecta y envía {"op": "square", "n": 4}.
3️⃣ El servidor asigna un task_id y la encola.
4️⃣ Un worker procesa la tarea (4 * 4 = 16).
5️⃣ El servidor devuelve {"task_id": "...", "result": 16} al cliente.
6️⃣ El cliente imprime el resultado y finaliza.

🧩 Extensiones posibles

Este proyecto se puede ampliar fácilmente para:

Guardar resultados en una base de datos (SQLite, PostgreSQL, etc.).

Distribuir workers en varios equipos.

Incorporar una cola de mensajes real (RabbitMQ o Redis).

Agregar balanceador de carga (Nginx o HAProxy).

👨‍💻 Autor

Proyecto educativo desarrollado para Redes y Sistemas Distribuidos.
Creado por: Romina Imbarrato
Año: 2025
