"""Lector MJPEG adaptado de Proyecto5/scripts/capturar_esp32.py. Ver PROCEDENCIA.md."""
from __future__ import annotations
import argparse
import http.client
import socket
import threading
import time
from collections import deque
from contextlib import suppress
from urllib.parse import urlsplit

def anchored_clock():
    wall, monotonic = time.time_ns(), time.monotonic_ns()
    return lambda: wall + time.monotonic_ns() - monotonic

def stream_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or not parsed.hostname
        or parsed.port != 81
        or parsed.path != "/stream"
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise argparse.ArgumentTypeError("Usar solo http://<IP>:81/stream, sin credenciales")
    return value


class JpegParser:
    """Extrae JPEG aunque los límites MJPEG lleguen partidos entre lecturas."""

    def __init__(self):
        self.buffer = bytearray()

    def feed(self, chunk: bytes) -> list[bytes]:
        self.buffer.extend(chunk)
        frames = []
        while True:
            start = self.buffer.find(b"\xff\xd8")
            if start < 0:
                self.buffer[:] = self.buffer[-1:]
                break
            if start:
                del self.buffer[:start]
            end = self.buffer.find(b"\xff\xd9", 2)
            if end < 0:
                if len(self.buffer) > 8 * 1024 * 1024:
                    raise ValueError("JPEG incompleto mayor a 8 MiB")
                break
            frames.append(bytes(self.buffer[: end + 2]))
            del self.buffer[: end + 2]
        return frames


class StreamReader:
    """Un lector en segundo plano; conserva solo el cuadro más reciente."""

    def __init__(self, response):
        self.response = response
        self.latest = None
        self.error = None
        self.guard = threading.Lock()
        self.stop = threading.Event()
        self.clock = anchored_clock()
        self.thread = threading.Thread(target=self.run, daemon=True)

    def run(self):
        parser = JpegParser()
        try:
            while not self.stop.is_set():
                chunk = self.response.read1(4096)
                if self.stop.is_set():
                    break
                if not chunk:
                    raise OSError("El stream se cerró")
                for data in parser.feed(chunk):
                    with self.guard:
                        self.latest = (data, self.clock(), time.monotonic())
        except (OSError, ValueError, http.client.HTTPException) as exc:
            if not self.stop.is_set():
                self.error = str(exc)
        finally:
            # Solo el lector cierra HTTP: nunca mientras otro hilo está en read1.
            try:
                self.response.close()
            except (OSError, ValueError, http.client.HTTPException) as exc:
                if not self.stop.is_set():
                    self.error = self.error or f"Error al cerrar HTTP: {exc}"

    def close(self):
        self.stop.set()
        self.thread.join(timeout=6)
        if self.thread.is_alive():
            # La respuesta sigue siendo propiedad del lector; no cerrarla desde aquí.
            raise OSError("El lector MJPEG no terminó en 6 s; conexión pendiente de cierre")

    def snapshot(self):
        with self.guard:
            return self.latest



class ReconnectingStream(StreamReader):
    """Un solo hilo posee conexión y respuesta, incluso durante las reconexiones."""

    def __init__(self, url, initial_wait=10.0, frame_wait=10.0, retry_delay=2.0):
        super().__init__(None)
        self.url = urlsplit(stream_url(url))
        self.initial_wait = initial_wait
        self.frame_wait = frame_wait
        self.retry_delay = retry_delay
        self.state = "CONECTANDO"
        self.messages = deque()
        self.transport = None
        self.last_jpeg = None

    def notify(self, state, message=None):
        with self.guard:
            self.state = state
            if message:
                self.messages.append(message)

    def drain_messages(self):
        with self.guard:
            messages = list(self.messages)
            self.messages.clear()
            return messages

    def is_current(self, stamp, maximum_age, now):
        with self.guard:
            return (
                not self.stop.is_set()
                and self.state == "EN VIVO"
                and self.latest is not None
                and self.latest[1] == stamp
                and now - self.latest[2] <= maximum_age
            )

    def run(self):
        while not self.stop.is_set():
            connection = None
            response = None
            phase = "conexión HTTP"
            self.notify("CONECTANDO")
            try:
                connection = http.client.HTTPConnection(
                    self.url.hostname, self.url.port, timeout=self.initial_wait
                )
                connection.connect()
                transport = connection.sock
                with self.guard:
                    self.transport = transport
                if self.stop.is_set():
                    break
                connection.request(
                    "GET", self.url.path, headers={"Accept": "multipart/x-mixed-replace"}
                )
                response = connection.getresponse()
                if response.status != 200:
                    raise OSError(f"HTTP {response.status} {response.reason}")
                if (
                    "multipart/x-mixed-replace"
                    not in response.getheader("Content-Type", "").lower()
                ):
                    raise ValueError("La respuesta no es un stream MJPEG multipart")
                phase = "primer cuadro MJPEG"
                self.notify("ESPERANDO VIDEO")
                started = time.monotonic()
                last_new = None
                parser = JpegParser()
                while not self.stop.is_set():
                    now = time.monotonic()
                    deadline = (
                        started + self.initial_wait
                        if last_new is None
                        else last_new + self.frame_wait
                    )
                    remaining = deadline - now
                    if remaining <= 0:
                        raise TimeoutError(
                            f"Sin cuadros JPEG distintos durante "
                            f"{self.initial_wait if last_new is None else self.frame_wait:g} s"
                        )
                    # El timeout se aplica a la lectura pendiente; no exige un JPEG cada 2 s.
                    transport.settimeout(remaining)
                    chunk = response.read1(4096)
                    if self.stop.is_set():
                        break
                    if not chunk:
                        raise OSError("El stream se cerró")
                    for data in parser.feed(chunk):
                        # Un JPEG idéntico no renueva su fecha ni descongela la captura.
                        if data == self.last_jpeg:
                            continue
                        now = time.monotonic()
                        with self.guard:
                            if self.stop.is_set():
                                break
                            self.latest = (data, self.clock(), now)
                            self.last_jpeg = data
                        if last_new is None:
                            self.notify("EN VIVO", "INFO: video disponible; captura habilitada")
                        last_new = now
                        phase = "lectura continua MJPEG"
            except (OSError, ValueError, http.client.HTTPException) as exc:
                if not self.stop.is_set():
                    hint = (
                        "Comprobar IP, Wi-Fi y puerto 81."
                        if phase == "conexión HTTP"
                        else "Cerrar otros clientes y la página de controles; "
                        "un cliente ocupado es una posibilidad, no un diagnóstico confirmado."
                    )
                    self.notify(
                        "RECONECTANDO",
                        f"ADVERTENCIA [{phase}]: {exc}. "
                        f"{hint} Reintento en {self.retry_delay:g} s; capturas bloqueadas.",
                    )
            except Exception as exc:
                # Un fallo de programación es fatal y se informa al visor, no se reintenta.
                self.error = f"{type(exc).__name__}: {exc}"
                return
            finally:
                with self.guard:
                    self.latest = None
                    self.transport = None
                # Solo este hilo cierra los objetos HTTP, una vez que terminó read1.
                for resource in (response, connection):
                    if resource is not None:
                        try:
                            resource.close()
                        except (OSError, ValueError, http.client.HTTPException) as exc:
                            if not self.stop.is_set():
                                self.notify("RECONECTANDO", f"ADVERTENCIA [cierre HTTP]: {exc}")
            if self.stop.wait(self.retry_delay):
                break
        self.notify("DETENIDO")

    def close(self):
        self.stop.set()
        with self.guard:
            transport = self.transport
            self.latest = None
        if transport is not None:
            with suppress(OSError):
                # Desbloquea read1 sin invalidar concurrentemente el objeto HTTPResponse.
                transport.shutdown(socket.SHUT_RDWR)
        self.thread.join(timeout=self.initial_wait + 1)
        if self.thread.is_alive():
            raise OSError("El lector MJPEG sigue esperando la conexión HTTP; cierre pendiente")

