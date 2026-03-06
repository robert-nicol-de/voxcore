# VoxCore Domain Setup Guide

## DNS Configuration

### Option A: A Record (Direct IP)
```
Type:  A
Name:  yourdomain.com (or @ for root)
Value: YOUR_SERVER_IP_ADDRESS
TTL:   3600
```

### Option B: CNAME Record (For subdomains)
```
Type:  CNAME  
Name:  api.yourdomain.com
Value: yourdomain.com
TTL:   3600
```

### Recommended Setup:
```
yourdomain.com      A       YOUR_SERVER_IP          (Points to your server)
www.yourdomain.com  CNAME   yourdomain.com          (Points to root domain)
api.yourdomain.com  CNAME   yourdomain.com          (Optional: alternate API endpoint)
mail.yourdomain.com MX      YOUR_MAIL_SERVER        (If using email)
```

### Nameservers (if using external DNS provider)
Point domain to your DNS provider's nameservers:
```
ns1.yourdnsprovider.com
ns2.yourdnsprovider.com
ns3.yourdnsprovider.com
ns4.yourdnsprovider.com
```

---

## Verify Domain is Connected
```bash
# Check DNS resolution
nslookup yourdomain.com

# or
dig yourdomain.com

# Expected output: Shows your server's IP address
```

---

## SSL Certificate Setup (Let's Encrypt)

### On Your Server:

```bash
# 1. Install Certbot
sudo apt-get update
sudo apt-get install certbot

# 2. Generate SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 3. Certificates will be stored in:
# /etc/letsencrypt/live/yourdomain.com/

# 4. Set up auto-renewal (runs daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# 5. Verify renewal works
sudo certbot renew --dry-run
```

### Or with Docker (easier):
```bash
# Certbot will auto-run with docker setup
docker run --rm --name certbot \
  -v /your/path/certbot/conf:/etc/letsencrypt \
  -v /your/path/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com
```

---

## Deployment on Server

```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Clone VoxCore repo
cd /opt
git clone <YOUR_REPO> voxcore
cd voxcore

# 3. Update configuration
# Edit docker-compose.prod.yml:
#   - Replace yourdomain.com with your actual domain
#   - Update SQL Server credentials
#   - Update VITE_API_URL

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. View logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx

# 6. Verify running
docker-compose -f docker-compose.prod.yml ps
```

---

## Common DNS Providers

| Provider | Setup Time | Cost | Notes |
|----------|-----------|------|-------|
| Cloudflare | 5 min | Free | DDoS protection, CDN |
| Route 53 (AWS) | 10 min | $0.50/month | Integrated with AWS |
| NameCheap | 5 min | Free-$1/mo | Simple, reliable |
| GoDaddy | 10 min | $12/yr | Popular, good support |
| DigitalOcean | 5 min | Free | If hosting on DigitalOcean |

---

## Troubleshooting

### Domain not resolving?
```bash
# Clear DNS cache on your machine
# Windows:
ipconfig /flushdns

# Mac:
sudo dscacheutil -flushcache

# Linux:
sudo systemctl restart systemd-resolved
```

### SSL certificate issues?
```bash
# Check certificate status
sudo openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# View Nginx error log
docker logs voxcore-nginx
```

### Nginx not routing correctly?
```bash
# Reload Nginx config (no downtime)
docker-compose exec nginx nginx -s reload

# Check Nginx config syntax
docker-compose exec nginx nginx -t
```

---

## Application URLs After Setup

| Component | URL |
|-----------|-----|
| Frontend | https://yourdomain.com |
| Backend API | https://yourdomain.com/api |
| API Docs | https://yourdomain.com/api/docs |

---

## Security Checklist

- [ ] DNS configured and resolving
- [ ] SSL certificate installed (/etc/letsencrypt/live/)
- [ ] Nginx reverse proxy running
- [ ] CORS headers enabled
- [ ] Firewall allowing 80 (HTTP) and 443 (HTTPS)
- [ ] SQL Server credentials updated
- [ ] Rate limiting enabled
- [ ] Regular backups configured
- [ ] Monitoring/logging set up
- [ ] Auto SSL renewal scheduled

---

## Next Steps

1. **Get a domain** (GoDaddy, NameCheap, etc.)
2. **Rent a server** (DigitalOcean, AWS, Linode, etc.) with Docker installed
3. **Update DNS** records to point to your server IP
4. **Clone & configure** VoxCore on the server
5. **Run** `docker-compose -f docker-compose.prod.yml up -d`
6. **Visit** https://yourdomain.com

That's it! VoxCore is now live on your domain.
