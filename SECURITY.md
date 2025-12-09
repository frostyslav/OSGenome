# Security Policy

## Overview

OSGenome handles sensitive genetic data. This document outlines security measures and best practices.

## Security Features Implemented

### 1. Input Validation
- **File uploads**: Size limits (16MB), type validation, filename sanitization
- **Base64 data**: Validation before decoding, size checks
- **Genetic data**: Format validation, allele validation, rsid format checks
- **Path traversal protection**: All file paths sanitized using `secure_filename()`

### 2. Rate Limiting
- **SNPedia crawler**: 1 second delay between requests
- **Retry logic**: Exponential backoff on failures
- **Request timeouts**: 30 second timeout on HTTP requests
- **Batch processing**: Intermediate saves every 10 requests

### 3. Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy`: Restricts resource loading

### 4. Session Security
- Secure session cookies (HTTPS only in production)
- HttpOnly cookies (prevents XSS access)
- SameSite cookies (CSRF protection)
- Secret key from environment variable

### 5. Error Handling
- No sensitive data in error messages
- Proper logging without exposing user data
- Graceful degradation on failures

### 6. Data Privacy
- All data processed locally
- No external data transmission (except SNPedia API)
- No data persistence beyond user control

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

**Required for production:**
- `SECRET_KEY`: Strong random key (use `python -c "import os; print(os.urandom(32).hex())"`)
- `FLASK_ENV=production`
- `FLASK_DEBUG=false`

### File Permissions

Ensure proper file permissions:
```bash
chmod 600 .env
chmod 700 SNPedia/data/
```

## Best Practices

### For Users

1. **Never share your raw genetic data files**
2. **Use strong SECRET_KEY in production**
3. **Run behind HTTPS in production** (use nginx/Apache as reverse proxy)
4. **Keep dependencies updated**: `pip install -U -r requirements.txt`
5. **Review logs regularly** for suspicious activity
6. **Backup your data** before processing

### For Developers

1. **Never commit `.env` files** (already in `.gitignore`)
2. **Validate all user inputs**
3. **Use parameterized queries** if adding database support
4. **Keep dependencies minimal** and audited
5. **Run security scanners**: `pip install safety && safety check`
6. **Follow OWASP guidelines**

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email the maintainer directly (check README for contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Checklist for Deployment

- [ ] Set strong `SECRET_KEY` environment variable
- [ ] Set `FLASK_ENV=production`
- [ ] Disable debug mode (`FLASK_DEBUG=false`)
- [ ] Use HTTPS (configure reverse proxy)
- [ ] Set proper file permissions
- [ ] Configure firewall rules
- [ ] Enable logging and monitoring
- [ ] Regular dependency updates
- [ ] Backup strategy in place
- [ ] Review CORS settings
- [ ] Test rate limiting

## Known Limitations

1. **In-memory rate limiting**: Resets on restart (consider Redis for production)
2. **No authentication**: Assumes single-user local deployment
3. **No database encryption**: Data stored as JSON files
4. **CSP allows unsafe-inline**: Required for Kendo UI (consider refactoring)

## Updates

This security policy is reviewed and updated regularly. Last update: December 2, 2025

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)
