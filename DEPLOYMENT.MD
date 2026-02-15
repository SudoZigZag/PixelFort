# PixelFort Deployment Guide

## Prerequisites

- Docker and Docker Compose installed
- ARM64 architecture (Raspberry Pi 5, Apple Silicon, etc.)
- At least 1GB free disk space

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/pixelfort.git
cd pixelfort
```

### 2. Configure Environment
```bash
# Copy production environment template
cp .env.production.example .env

# Edit configuration
vim .env

# Set ENVIRONMENT=production
# Adjust API_PORT if needed
# Set LOG_LEVEL=WARNING or ERROR
```

### 3. Deploy
```bash
./deploy.sh
```

That's it! Your photo NAS is running.

## Verify Deployment

### Check Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

Should show `healthy` status.

### Test API
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

## Usage

### Upload Photo
```bash
curl -X POST http://localhost:8000/photos/upload \
  -F "file=@/path/to/photo.jpg" \
  -F "user_id=1"
```

### List Photos
```bash
curl http://localhost:8000/photos
```

### Download Photo
```bash
curl http://localhost:8000/photos/1/download -o photo.jpg
```

### API Documentation
Open browser: `http://localhost:8000/docs`

## Management

### Stop Service
```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Service
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update Deployment
```bash
git pull
./deploy.sh
```

### Backup Data
```bash
# Backup database and photos
tar -czf pixelfort-backup-$(date +%Y%m%d).tar.gz storage/
```

### Restore Data
```bash
tar -xzf pixelfort-backup-20260214.tar.gz
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check if port is in use
lsof -i :8000
```

### Database errors
```bash
# Recreate database
rm storage/db/pixelfort.db
docker-compose -f docker-compose.prod.yml run --rm api python -m api.init_db
```

### Out of disk space
```bash
# Clean old images
docker system prune -a
```

## Production Checklist

- [ ] Set ENVIRONMENT=production in .env
- [ ] Set LOG_LEVEL=WARNING or ERROR
- [ ] API_RELOAD=false
- [ ] Configure firewall (allow only port 8000)
- [ ] Set up regular backups
- [ ] Monitor disk space
- [ ] Add authentication (future feature)

## Security Notes

⚠️ **Current limitations:**
- No authentication - anyone can upload/download
- No HTTPS - data sent unencrypted
- No rate limiting

**Recommended for:**
- Home network (behind firewall)
- Trusted users only
- Local network deployment

**NOT recommended for:**
- Public internet exposure
- Untrusted networks
- Production without authentication

## Next Steps

Future enhancements:
- Add user authentication (JWT tokens)
- Add HTTPS/TLS support
- Add rate limiting
- Add user quotas
- Add image thumbnails
- Add EXIF metadata extraction