# Guía de Testing - Materials Hub

Esta guía explica la estrategia de testing completa del proyecto Materials Hub.

## 📚 Tabla de Contenidos

1. [Tipos de Tests](#tipos-de-tests)
2. [Ejecutar Tests](#ejecutar-tests)
3. [Test Coverage](#test-coverage)
4. [Estructura de Tests](#estructura-de-tests)
5. [Mejores Prácticas](#mejores-prácticas)

---

## 🧪 Tipos de Tests

### 1. Unit Tests (Tests Unitarios)
**Ubicación:** `app/modules/*/tests/test_unit.py`

**Qué testean:** Funciones y métodos individuales de forma aislada.

**Características:**
- ✅ Rápidos (< 100ms por test)
- ✅ Sin dependencias externas (usan mocks)
- ✅ No requieren base de datos
- ✅ Aislados y predecibles

**Ejemplo:**
```bash
# Ejecutar solo unit tests
pytest -m unit

# Ejecutar unit tests de un módulo específico
pytest app/modules/zenodo/tests/test_unit.py
```

### 2. Integration Tests (Tests de Integración)
**Ubicación:** `app/modules/*/tests/test_integration.py`

**Qué testean:** Interacción entre múltiples componentes (servicios, repositorios, base de datos).

**Características:**
- ⏱️ Más lentos (100ms - 1s por test)
- 🗄️ Requieren base de datos de test
- 🔗 Prueban flujos completos
- 💾 Usan datos reales en DB de test

**Ejemplo:**
```bash
# Ejecutar solo integration tests
pytest -m integration

# Ejecutar integration tests de autenticación
pytest app/modules/auth/tests/test_integration.py
```

### 3. GUI Tests / E2E (Tests de Interfaz con Selenium)
**Ubicación:** `app/modules/*/tests/test_selenium.py`

**Qué testean:** Interfaz de usuario completa en navegador real.

**Características:**
- 🐌 Muy lentos (varios segundos por test)
- 🌐 Requieren navegador (Chrome/Firefox)
- 🖱️ Simulan interacción de usuario real
- �� Pueden tomar capturas de pantalla

**Ejemplo:**
```bash
# Ejecutar solo tests de Selenium
pytest -m selenium

# Ejecutar con navegador visible (no headless)
pytest -m selenium --headed
```

### 4. Load Tests (Tests de Carga con Locust)
**Ubicación:** `tests/locust/`

**Qué testean:** Rendimiento y capacidad del sistema bajo carga.

**Características:**
- 📊 Miden rendimiento
- 👥 Simulan múltiples usuarios concurrentes
- ⏱️ Miden tiempo de respuesta
- 💪 Encuentran cuellos de botella

**Ejemplo:**
```bash
# Ejecutar load tests
locust -f tests/locust/locustfile.py --host=http://localhost:5000

# Abrir interfaz web de Locust
# → http://localhost:8089
```

---

## 🚀 Ejecutar Tests

### Comandos Básicos

```bash
# Ejecutar TODOS los tests
pytest

# Ejecutar con verbose output
pytest -v

# Ejecutar tests de un módulo específico
pytest app/modules/auth/tests/

# Ejecutar un archivo de test específico
pytest app/modules/dataset/tests/test_unit.py

# Ejecutar una función de test específica
pytest app/modules/auth/tests/test_unit.py::test_login_success

# Ejecutar tests que coincidan con un patrón
pytest -k "login"
```

### Por Tipo de Test

```bash
# Solo unit tests (rápidos)
pytest -m unit

# Solo integration tests
pytest -m integration

# Solo Selenium tests
pytest -m selenium

# Excluir Selenium tests (más común)
pytest -m "not selenium"

# Tests rápidos (unit + algunos integration)
pytest -m "unit or fast"

# Smoke tests (funcionalidad crítica)
pytest -m smoke
```

### Opciones Útiles

```bash
# Detener en primer fallo
pytest -x

# Ejecutar último test que falló
pytest --lf

# Ejecutar tests fallidos primero
pytest --ff

# Ejecutar en paralelo (más rápido)
pytest -n auto

# Mostrar print statements
pytest -s

# Mostrar variables locales en fallos
pytest --showlocals

# Modo verbose con duración de tests
pytest -v --durations=10
```

---

## 📊 Test Coverage

### Generar Reporte de Coverage

```bash
# Ejecutar tests con coverage
pytest --cov=app --cov=rosemary --cov=core

# Generar reporte HTML
pytest --cov=app --cov-report=html

# Abrir reporte en navegador
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Generar reporte XML (para CI/CD)
pytest --cov=app --cov-report=xml

# Mostrar líneas no cubiertas
pytest --cov=app --cov-report=term-missing
```

### Coverage por Módulo

```bash
# Coverage de módulo específico
pytest app/modules/auth/tests/ --cov=app.modules.auth

# Coverage mínimo requerido (falla si < 70%)
pytest --cov=app --cov-fail-under=70
```

### Interpretar Resultados

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
app/modules/auth/services.py           45      3    93%   23, 45-46
app/modules/dataset/models.py          78      0   100%
app/modules/zenodo/services.py        120     25    79%   45-52, 89-95
------------------------------------------------------------------
TOTAL                                 243     28    88%
```

- **Stmts**: Líneas de código
- **Miss**: Líneas no ejecutadas por tests
- **Cover**: Porcentaje de cobertura
- **Missing**: Números de línea no cubiertos

---

## 📁 Estructura de Tests

```
materials-hub/
├── app/
│   └── modules/
│       ├── auth/
│       │   └── tests/
│       │       ├── __init__.py
│       │       ├── test_unit.py           # Unit tests
│       │       ├── test_integration.py    # Integration tests
│       │       └── test_selenium.py       # GUI tests
│       ├── dataset/
│       │   └── tests/
│       │       ├── test_unit.py
│       │       └── test_integration.py
│       ├── explore/
│       │   └── tests/
│       │       └── test_unit.py
│       └── zenodo/
│           └── tests/
│               └── test_unit.py
├── tests/
│   ├── locust/
│   │   ├── locustfile.py              # Load tests
│   │   └── README.md
│   └── README.md (este archivo)
├── pytest.ini                          # Configuración de pytest
├── .coveragerc                         # Configuración de coverage
└── htmlcov/                            # Reportes de coverage (generado)
```

---

## ✅ Mejores Prácticas

### 1. Nomenclatura

```python
# ✅ BUENO
def test_login_success_redirects_to_home():
    """Test that successful login redirects to home page"""
    pass

def test_create_dataset_with_invalid_title_raises_error():
    """Test that creating dataset with invalid title raises ValidationError"""
    pass

# ❌ MALO
def test1():
    pass

def test_stuff():
    pass
```

### 2. Estructura de Tests (Arrange-Act-Assert)

```python
def test_user_creation():
    # Arrange - Preparar datos
    email = "test@example.com"
    password = "secure123"

    # Act - Ejecutar acción
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    # Assert - Verificar resultado
    assert user.id is not None
    assert user.email == email

    # Cleanup - Limpiar
    db.session.delete(user)
    db.session.commit()
```

### 3. Usar Fixtures

```python
@pytest.fixture
def sample_user():
    """Fixture que crea un usuario de prueba"""
    user = User(email="fixture@example.com", password="test123")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

def test_with_fixture(sample_user):
    """Test que usa el fixture"""
    assert sample_user.email == "fixture@example.com"
```

### 4. Mocking para Unit Tests

```python
from unittest.mock import Mock, patch

@patch('app.modules.zenodo.services.requests.get')
def test_zenodo_connection(mock_get):
    """Test con mock para evitar llamadas HTTP reales"""
    # Configurar mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Ejecutar test
    service = ZenodoService()
    result = service.test_connection()

    # Verificar
    assert result is True
    mock_get.assert_called_once()
```

### 5. Markers para Categorizar

```python
@pytest.mark.unit
def test_fast_unit_test():
    """Test rápido unitario"""
    pass

@pytest.mark.integration
def test_database_integration():
    """Test de integración con DB"""
    pass

@pytest.mark.slow
def test_complex_operation():
    """Test que toma varios segundos"""
    pass

@pytest.mark.smoke
def test_critical_functionality():
    """Test de funcionalidad crítica"""
    pass
```

### 6. Parametrización

```python
@pytest.mark.parametrize("email,password,expected", [
    ("test@example.com", "valid123", True),
    ("bad@example.com", "wrong", False),
    ("", "password", False),
    ("test@example.com", "", False),
])
def test_login_scenarios(email, password, expected):
    """Test múltiples escenarios de login"""
    result = authenticate(email, password)
    assert result == expected
```

---

## 🎯 Objetivos de Coverage

| Módulo | Coverage Mínimo | Coverage Ideal |
|--------|----------------|----------------|
| Servicios | 80% | 95% |
| Repositorios | 75% | 90% |
| Modelos | 70% | 85% |
| Routes | 60% | 80% |
| Forms | 50% | 70% |
| **TOTAL** | **70%** | **85%** |

---

## 🐛 Debugging Tests

```bash
# Ejecutar con debugger (pdb)
pytest --pdb

# Pausar en primer fallo
pytest -x --pdb

# Ejecutar con ipdb (mejor que pdb)
pip install ipdb
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb

# Ver print statements y logging
pytest -s --log-cli-level=DEBUG
```

---

## 🔧 Configuración CI/CD

Los tests se ejecutan automáticamente en GitHub Actions:

```yaml
# .github/workflows/CI_pytest.yml
- name: Run Tests with Coverage
  run: |
    pytest --cov=app --cov-report=xml --cov-report=term-missing

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Locust Documentation](https://docs.locust.io/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)

---

**Última actualización:** 2025-01-20
**Maintainer:** Materials Hub Team
