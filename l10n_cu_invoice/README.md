# Cuba - Factura

Factura cubana sobre el motor de Facturación de Odoo 19 (F2a).

## Contenido

- Validaciones al publicar, solo para compañías cubanas:
  - el emisor debe tener NIT;
  - el receptor debe tener NIT (persona jurídica) o carné de identidad
    (persona natural).
- Reporte impreso con bloque del emisor (NIT y REEUP), carné de identidad
  del receptor junto al NIT y nota de conservación tributaria.
- La numeración usa la secuencia estándar por diario de Odoo; configure el
  prefijo del diario según el consecutivo interno de la entidad.

## Nota legal

La búsqueda realizada no localizó una norma única vigente que fije el modelo
de factura; los campos exigidos (NIT, consecutivo, fecha, detalle, impuestos,
moneda) corresponden a la práctica comercial y fiscal cubana y deben
validarse contra las disposiciones vigentes del MFP y la ONAT antes de su uso
productivo.
