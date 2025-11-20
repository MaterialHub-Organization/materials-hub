# Load Testing con Locust - Materials Hub

Esta guía explica cómo realizar pruebas de carga (load testing) en Materials Hub usando Locust.

## 📖 ¿Qué es Locust?

Locust es una herramienta de load testing que simula miles de usuarios concurrentes accediendo a tu aplicación para:
- 📊 Medir rendimiento bajo carga
- 🔍 Identificar cuellos de botella
- 💪 Determinar capacidad máxima
- ⚡ Optimizar tiempos de respuesta

---

## 🚀 Instalación

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar Locust
pip install locust

# Verificar instalación
locust --version
```

---

## 📁 Estructura

```
tests/locust/
├── __init__.py
├── locustfile.py      # Escenarios de carga
└── README.md          # Esta guía
```

---

## 🎯 Tipos de Usuarios Simulados

### 1. **PublicUser** (Peso: 50)
Usuario anónimo navegando el sitio público.

**Acciones:**
- Ver homepage (5x)
- Explorar datasets (3x)
- Buscar datasets (2x)
- Ver detalle de dataset (1x)
- Ver página de registro/login (1x)

### 2. **AuthenticatedUser** (Peso: 30)
Usuario autenticado usando la aplicación.

**Acciones:**
- Ver homepage (5x)
- Ver perfil (4x)
- Explorar datasets (3x)
- Buscar datasets (2x)
- Ver propios datasets (1x)

### 3. **DatasetUploader** (Peso: 15)
Usuario subiendo y gestionando datasets (operaciones pesadas).

**Acciones:**
- Ver formulario de carga (3x)
- Ver mis datasets (2x)
- Ver detalle de dataset (1x)

### 4. **APIUser** (Peso: 5)
Cliente API haciendo peticiones programáticas.

**Acciones:**
- Listar datasets (5x)
- Obtener dataset específico (3x)
- Buscar datasets (2x)

### 5. **StressTestUser** (Uso específico)
Usuario de stress test con peticiones muy rápidas.

---

## 🏃 Ejecutar Tests

### Modo Web UI (Recomendado para empezar)

```bash
# Ejecutar con interfaz web
locust -f tests/locust/locustfile.py --host=http://localhost:5000

# Abrir navegador en: http://localhost:8089

# Configurar en la UI:
# - Number of users: 100
# - Spawn rate: 10 (usuarios/segundo)
# - Host: http://localhost:5000
```

### Modo Headless (Sin interfaz)

```bash
# Test básico: 50 usuarios, 5 usuarios/seg, durante 1 minuto
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 50 \
       --spawn-rate 5 \
       --run-time 1m \
       --headless

# Test de carga media: 200 usuarios durante 5 minutos
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 200 \
       --spawn-rate 20 \
       --run-time 5m \
       --headless

# Test de carga alta: 500 usuarios durante 10 minutos
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 500 \
       --spawn-rate 50 \
       --run-time 10m \
       --headless
```

### Ejecutar Usuario Específico

```bash
# Solo usuarios públicos
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       PublicUser

# Solo stress test
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       StressTestUser \
       --users 100 \
       --spawn-rate 20 \
       --run-time 30s \
       --headless
```

### Generar Reportes

```bash
# Generar reporte HTML
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 100 \
       --spawn-rate 10 \
       --run-time 2m \
       --headless \
       --html reports/locust_report_$(date +%Y%m%d_%H%M%S).html

# Generar CSV
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 100 \
       --spawn-rate 10 \
       --run-time 2m \
       --headless \
       --csv reports/locust_stats
```

---

## 📊 Interpretar Resultados

### Métricas Principales

```
Type     Name                    # reqs    # fails  Avg  Min  Max  Median  req/s
------------------------------------------------------------------------
GET      /                       1000      0        45   12   234  38      16.7
GET      /explore                750       0        89   23   456  67      12.5
GET      /explore?query=test     500       2        156  34   890  120     8.3
POST     /login                  200       0        234  89   567  201     3.3
------------------------------------------------------------------------
Total                            2450      2        89   12   890  56      40.8
```

**Columnas:**
- **# reqs**: Número total de peticiones
- **# fails**: Peticiones fallidas
- **Avg**: Tiempo promedio de respuesta (ms)
- **Min/Max**: Tiempo mínimo/máximo
- **Median**: Mediana del tiempo de respuesta
- **req/s**: Peticiones por segundo

### ✅ Qué Buscar (Good)

- ✅ Avg < 200ms (páginas rápidas)
- ✅ Avg < 500ms (páginas normales)
- ✅ # fails = 0 (sin errores)
- ✅ req/s alto y estable

### ⚠️ Señales de Problemas

- ❌ Avg > 1000ms (demasiado lento)
- ❌ # fails > 0 (errores bajo carga)
- ❌ Max >> Avg (inconsistencia)
- ❌ req/s decrece con más usuarios

---

## 🎯 Escenarios de Testing

### 1. Baseline Test (Línea Base)
**Objetivo:** Establecer rendimiento normal

```bash
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 10 \
       --spawn-rate 2 \
       --run-time 5m \
       --headless
```

**Éxito:** Avg < 200ms, 0 errores

### 2. Load Test (Carga Normal)
**Objetivo:** Simular tráfico esperado

```bash
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 100 \
       --spawn-rate 10 \
       --run-time 10m \
       --headless
```

**Éxito:** Avg < 500ms, < 1% errores

### 3. Stress Test (Estrés)
**Objetivo:** Encontrar punto de quiebre

```bash
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 500 \
       --spawn-rate 50 \
       --run-time 10m \
       --headless
```

**Éxito:** Sistema no colapsa, errores controlados

### 4. Spike Test (Picos)
**Objetivo:** Manejar aumentos súbitos

```bash
# Subir rápidamente a 200 usuarios
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 200 \
       --spawn-rate 100 \
       --run-time 2m \
       --headless
```

**Éxito:** Recuperación rápida tras pico

### 5. Endurance Test (Resistencia)
**Objetivo:** Estabilidad a largo plazo

```bash
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 50 \
       --spawn-rate 5 \
       --run-time 1h \
       --headless
```

**Éxito:** Rendimiento estable, sin memory leaks

---

## 🔧 Antes de Ejecutar

### 1. Preparar Entorno

```bash
# Limpiar base de datos de test
rosemary db:reset --yes

# Seed con datos de prueba
rosemary db:seed --yes

# Verificar aplicación corriendo
curl http://localhost:5000
```

### 2. Configurar Credenciales

Asegúrate de que existe el usuario de test:
```python
# Email: test@example.com
# Password: test1234
```

### 3. Recursos del Sistema

```bash
# Monitorear durante el test
# Terminal 1: Ejecutar aplicación
flask run

# Terminal 2: Ejecutar Locust
locust -f tests/locust/locustfile.py --host=http://localhost:5000

# Terminal 3: Monitorear recursos
htop  # o 'top' en Linux/Mac
```

---

## 📈 Optimizaciones Basadas en Resultados

### Si Homepage es Lento (Avg > 500ms)
- Implementar cache (Flask-Caching)
- Optimizar queries de base de datos
- Usar CDN para assets estáticos

### Si Búsquedas son Lentas
- Añadir índices en base de datos
- Implementar búsqueda con Elasticsearch
- Cache de resultados frecuentes

### Si Login es Lento
- Revisar hashing de passwords
- Optimizar queries de usuario
- Implementar rate limiting

### Si hay Memory Leaks
- Revisar cierre de conexiones DB
- Verificar cleanup de sesiones
- Perfilar con memory_profiler

---

## 🚨 Troubleshooting

### Error: "Connection refused"
```bash
# Verificar que Flask está corriendo
flask run

# Verificar puerto correcto
netstat -an | grep 5000
```

### Error: "Too many open files"
```bash
# Aumentar límite de archivos (Linux/Mac)
ulimit -n 10000
```

### Test muy lento
```bash
# Reducir usuarios o spawn rate
locust -f tests/locust/locustfile.py \
       --host=http://localhost:5000 \
       --users 10 \
       --spawn-rate 2
```

---

## 📚 Recursos

- [Locust Documentation](https://docs.locust.io/)
- [Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [Performance Testing Guide](https://www.thoughtworks.com/insights/articles/performance-testing)

---

**Última actualización:** 2025-01-20
**Maintainer:** Materials Hub Team
