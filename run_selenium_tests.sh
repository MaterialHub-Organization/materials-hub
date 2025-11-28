#!/bin/bash
# Script to run Selenium tests with Flask app running in background
# This script starts the Flask app in testing mode and runs Selenium tests

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configurando entorno para tests de Selenium ===${NC}"

# Activate virtual environment
echo -e "${YELLOW}Activando entorno virtual...${NC}"
source venv/bin/activate

# Configure webdriver-manager to use only local cached drivers
export WDM_LOCAL=1

# Check if Flask app is already running on port 5000
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Advertencia: Flask ya está ejecutándose en el puerto 5000${NC}"
    echo -e "${YELLOW}Se usará la instancia existente para los tests${NC}"
    FLASK_WAS_RUNNING=true
else
    FLASK_WAS_RUNNING=false

    # Create temporary PID file
    PIDFILE="/tmp/flask_selenium_test.pid"

    # Start Flask app in background for testing
    echo -e "${YELLOW}Iniciando Flask app en modo testing...${NC}"
    export FLASK_ENV=testing
    export WORKING_DIR=""  # Empty for local development

    # Start Flask in background and save PID
    python start_test_server.py > /tmp/flask_test.log 2>&1 &
    FLASK_PID=$!
    echo $FLASK_PID > $PIDFILE

    echo -e "${GREEN}Flask app iniciado con PID: $FLASK_PID${NC}"
    echo -e "${YELLOW}Esperando 10 segundos para que Flask inicie completamente...${NC}"
    sleep 10

    # Check if Flask is running
    if ! ps -p $FLASK_PID > /dev/null; then
        echo -e "${RED}Error: Flask no pudo iniciarse. Revisa /tmp/flask_test.log${NC}"
        cat /tmp/flask_test.log
        exit 1
    fi

    # Verify Flask is responding
    if ! curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo -e "${RED}Error: Flask no responde en localhost:5000${NC}"
        kill $FLASK_PID 2>/dev/null || true
        rm -f $PIDFILE
        exit 1
    fi

    echo -e "${GREEN}Flask app está listo y respondiendo en http://localhost:5000${NC}"
fi

# Cleanup function to stop Flask when script exits
cleanup() {
    if [ "$FLASK_WAS_RUNNING" = false ]; then
        echo -e "\n${YELLOW}Deteniendo Flask app...${NC}"
        if [ -f "$PIDFILE" ]; then
            FLASK_PID=$(cat $PIDFILE)
            if ps -p $FLASK_PID > /dev/null 2>&1; then
                kill $FLASK_PID 2>/dev/null || true
                echo -e "${GREEN}Flask app detenido${NC}"
            fi
            rm -f $PIDFILE
        fi
    else
        echo -e "\n${YELLOW}Flask app estaba ejecutándose antes - dejándolo activo${NC}"
    fi
}

# Register cleanup function to run on exit
trap cleanup EXIT INT TERM

# Run Selenium tests
echo -e "${GREEN}=== Ejecutando tests de Selenium ===${NC}"
echo ""

# Run pytest with selenium marker
pytest -m selenium -v

echo ""
echo -e "${GREEN}=== Tests de Selenium completados ===${NC}"
