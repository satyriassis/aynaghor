#!/usr/bin/env bash
# Recovery and backup script for AYNAGH0R / KH4NK1 system
# Usage: ./recover.sh [backup|restore|status]

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="aynaghor_backup_${TIMESTAMP}.tar.gz"
WORKSPACE_DIR="workspace"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to stop all services
stop_services() {
    log "Stopping all Docker services..."
    docker compose -f KH4NK1/docker-compose.yml down 2>/dev/null || true
    docker compose -f KH4NK1/docker-compose.yml -f KH4NK1/docker-compose.aynaghor.yml down 2>/dev/null || true
    log "Services stopped successfully"
}

# Function to start all services
start_services() {
    log "Starting KH4NK1 agent service..."
    docker compose -f KH4NK1/docker-compose.yml up -d --build

    log "Waiting for agent to be healthy..."
    sleep 10

    # Check if agent is responding
    if curl -s http://localhost:3000/status > /dev/null; then
        log "Agent is healthy"
    else
        warn "Agent may not be fully started yet"
    fi

    log "Starting AYNAGH0R application service..."
    docker compose -f KH4NK1/docker-compose.yml -f KH4NK1/docker-compose.aynaghor.yml up -d --build

    log "All services started successfully"
}

# Function to backup workspace
backup_workspace() {
    if [ ! -d "$WORKSPACE_DIR" ]; then
        warn "Workspace directory not found. Creating empty backup."
        tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" --files-from /dev/null
        return
    fi

    log "Creating backup of workspace directory..."
    tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" "$WORKSPACE_DIR/"
    log "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}"

    # Keep only last 5 backups
    log "Cleaning up old backups (keeping last 5)..."
    cd "$BACKUP_DIR"
    ls -t aynaghor_backup_*.tar.gz | tail -n +6 | xargs -r rm -f
    cd ..
}

# Function to restore workspace
restore_workspace() {
    local backup_file="$1"

    if [ -z "$backup_file" ]; then
        # Find the most recent backup
        backup_file=$(ls -t "$BACKUP_DIR"/aynaghor_backup_*.tar.gz 2>/dev/null | head -n1)
        if [ -z "$backup_file" ]; then
            error "No backup files found in $BACKUP_DIR"
        fi
    fi

    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
    fi

    log "Restoring from backup: $backup_file"

    # Remove existing workspace if it exists
    if [ -d "$WORKSPACE_DIR" ]; then
        log "Removing existing workspace directory..."
        rm -rf "$WORKSPACE_DIR"
    fi

    # Extract backup
    tar -xzf "$backup_file"
    log "Workspace restored successfully"
}

# Function to check system status
check_status() {
    log "Checking system status..."

    # Check Docker containers
    echo "Docker Containers:"
    docker compose -f KH4NK1/docker-compose.yml ps 2>/dev/null || echo "  No agent containers running"
    docker compose -f KH4NK1/docker-compose.yml -f KH4NK1/docker-compose.aynaghor.yml ps 2>/dev/null || echo "  No application containers running"

    # Check agent health
    echo "Agent Health:"
    if curl -s http://localhost:3000/status 2>/dev/null; then
        echo "  Agent is responding at http://localhost:3000"
    else
        echo "  Agent is not responding at http://localhost:3000"
    fi

    # Check application health
    echo "Application Health:"
    if curl -s http://localhost:8501 2>/dev/null; then
        echo "  Application is responding at http://localhost:8501"
    else
        echo "  Application is not responding at http://localhost:8501"
    fi

    # Check workspace
    echo "Workspace Status:"
    if [ -d "$WORKSPACE_DIR/aynaghor" ]; then
        echo "  AYNAGH0R workspace exists"
        if [ -f "$WORKSPACE_DIR/aynaghor/ui/app.py" ]; then
            echo "  Streamlit UI present"
        fi
        if [ -f "$WORKSPACE_DIR/aynaghor/core/engine.py" ]; then
            echo "  Core engine present"
        fi
    else
        echo "  AYNAGH0R workspace not found"
    fi

    # List available backups
    echo "Available Backups:"
    if ls "$BACKUP_DIR"/aynaghor_backup_*.tar.gz 2>/dev/null; then
        echo "  $(ls -1 "$BACKUP_DIR"/aynaghor_backup_*.tar.gz 2>/dev/null | wc -l) backup(s) available"
    else
        echo "  No backups found"
    fi
}

# Main script logic
case "${1:-}" in
    "backup")
        log "Starting backup procedure..."
        stop_services
        backup_workspace
        start_services
        log "Backup procedure completed successfully"
        ;;
    "restore")
        log "Starting restore procedure..."
        stop_services
        restore_workspace "$2"
        start_services
        log "Restore procedure completed successfully"
        ;;
    "status")
        check_status
        ;;
    *)
        echo "Usage: $0 {backup|restore|status} [backup_file]"
        echo ""
        echo "Commands:"
        echo "  backup          - Backup workspace and restart services"
        echo "  restore [file]  - Restore from most recent backup or specified file"
        echo "  status          - Show system status and health information"
        echo ""
        echo "Examples:"
        echo "  $0 backup                    # Backup and restart"
        echo "  $0 restore                   # Restore from latest backup"
        echo "  $0 restore backups/file.tar  # Restore from specific file"
        echo "  $0 status                    # Show system status"
        exit 1
        ;;
esac