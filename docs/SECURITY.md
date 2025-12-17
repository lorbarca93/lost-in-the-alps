# Security & Hosting Guide (Static Sites)

This project is served as static assets (GitHub Pages/Netlify). Apply these controls when deploying:

## HTTP Security Headers
Add a `_headers` file (Netlify) or equivalent reverse-proxy config with:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; script-src 'self' https://unpkg.com https://cdn.jsdelivr.net https://api.mapbox.com; style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://api.mapbox.com; img-src 'self' data: https://api.mapbox.com https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://*.opentopomap.org https://*.tile-cyclosm.openstreetmap.fr https://*.tile.openstreetmap.fr https://server.arcgisonline.com; connect-src 'self' https://api.mapbox.com https://tile.openstreetmap.org https://*.tile.openstreetmap.org https://*.opentopomap.org https://*.tile-cyclosm.openstreetmap.fr https://*.tile.openstreetmap.fr https://server.arcgisonline.com; object-src 'none'
```

## HTTPS Enforcement
- Netlify: `_redirects` line `http://* https://:splat 301!`
- GitHub Pages: enable “Enforce HTTPS” in repo settings.

## Subresource Integrity (SRI)
- Keep SRI on CDN assets (Leaflet/MarkerCluster). Add integrity+crossorigin for any new CDN scripts/styles.

## External Links
- Use `rel="noopener noreferrer"` on all external anchors. Meteoblue and Mapbox links already include it.

## Mapbox Token
- Token is **not bundled**. Users must set it in the browser console:  
  `localStorage.setItem('mapbox_token', 'pk.xxxxxx')`

## CSP Domain Allowlist
- Tiles: `*.tile.openstreetmap.org`, `api.mapbox.com`, `*.opentopomap.org`, `*.tile-cyclosm.openstreetmap.fr`, `*.tile.openstreetmap.fr`, `server.arcgisonline.com`
- Scripts/Styles: `unpkg.com`, `cdn.jsdelivr.net`, `api.mapbox.com`

## Privacy & Analytics
- GA is gated by consent (`web/js/cookie-consent.js`). Set a real `GA_ID` only if you use GA.

## Input Validation & Sanitization
- All database inputs are validated for type and length
- Text inputs limited to 100KB to prevent DoS attacks
- URLs validated and dangerous protocols blocked (javascript:, data:, vbscript:, etc.)
- XSS patterns removed from all text inputs (script tags, event handlers, etc.)
- See `src/data_cleaner.py` for implementation details

## Error Handling
- Errors logged internally but don't expose sensitive information
- Database constraint violations handled gracefully
- No stack traces or internal details exposed to users

## Security.txt
- Security contact information available at `.security.txt`
- Follows RFC 9116 standard for security.txt
- **Note**: Update contact email before deployment

## Reporting
- Open a security issue with minimal detail; share PoCs privately with maintainers
- For responsible disclosure, see `.security.txt` or email security contact
- See `docs/SECURITY_IMPROVEMENTS.md` for detailed security documentation 

