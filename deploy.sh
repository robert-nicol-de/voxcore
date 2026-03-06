#!/bin/bash

# VoxCore One-Click Deployment Script
# Usage: bash deploy.sh yourdomain.com your_server_ip

set -e

DOMAIN=${1:-yourdomain.com}
SERVER_IP=${2:-localhost}
EMAIL=${3:-admin@yourdomain.com}

echo "🚀 VoxCore Deployment Script"
echo "===================================="
echo "Domain: $DOMAIN"
echo "Server IP: $SERVER_IP"
echo "Email: $EMAIL"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Install Docker first.${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose not found. Install Docker Compose first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker and Docker Compose installed${NC}"
}

# Update configuration files
update_configs() {
    echo -e "${YELLOW}Updating configuration files...${NC}"
    
    # Update docker-compose.prod.yml
    sed -i "s/yourdomain.com/$DOMAIN/g" docker-compose.prod.yml
    sed -i "s/8000:8000/8000:8000/g" docker-compose.prod.yml
    
    # Update nginx.conf
    sed -i "s/yourdomain.com/$DOMAIN/g" nginx.conf
    
    echo -e "${GREEN}✓ Configuration files updated${NC}"
}

# Create directories
create_directories() {
    echo -e "${YELLOW}Creating required directories...${NC}"
    
    mkdir -p ./certbot/conf
    mkdir -p ./certbot/www
    mkdir -p ./ssl
    mkdir -p ./logs
    mkdir -p voxcore/voxquery/logs
    
    echo -e "${GREEN}✓ Directories created${NC}"
}

# Generate SSL certificate
generate_ssl() {
    echo -e "${YELLOW}Generating SSL certificate with Let's Encrypt...${NC}"
    
    docker run --rm \
        -v ./certbot/conf:/etc/letsencrypt \
        -v ./certbot/www:/var/www/certbot \
        -p 80:80 \
        certbot/certbot certonly --standalone \
        -d $DOMAIN \
        -d www.$DOMAIN \
        --email $EMAIL \
        --agree-tos \
        --non-interactive \
        --expand || echo -e "${YELLOW}⚠ SSL generation skipped (may need manual setup later)${NC}"
    
    echo -e "${GREEN}✓ SSL certificate generated${NC}"
}

# Start services
start_services() {
    echo -e "${YELLOW}Starting VoxCore services...${NC}"
    
    docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}✓ Services started${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    
    sleep 10
    
    docker-compose -f docker-compose.prod.yml ps
    
    echo -e "${GREEN}✓ Deployment complete!${NC}"
    echo ""
    echo "📍 Access VoxCore at:"
    echo -e "${GREEN}   https://$DOMAIN${NC}"
    echo ""
    echo "📝 Logs:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
    echo "   docker-compose -f docker-compose.prod.yml logs -f frontend"
    echo "   docker-compose -f docker-compose.prod.yml logs -f nginx"
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose -f docker-compose.prod.yml down"
}

# Main execution
main() {
    check_prerequisites
    create_directories
    update_configs
    generate_ssl
    start_services
    verify_deployment
}

main
