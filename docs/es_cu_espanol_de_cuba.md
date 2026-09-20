# Espanol de Cuba (es_CU) en Odoo — roadmap diferido

Estado: **planeado, no implementado**. Este documento recoge el plan para
crear la variante de idioma cubana en Odoo 19. No se ejecuto para no ampliar
el alcance de F0.

## Mecanica de Odoo 19

- El idioma de la interfaz lo selecciona un registro `res.lang` activo. No
  existe `es_CU` por defecto; hay que crearlo.
- Las traducciones por modulo viven en `i18n/<code>.po`. Sin `.po` para
  `es_CU`, Odoo muestra el texto fuente (ingles): no hereda de `es_ES`.
- Odoo descarga idiomas con `--load-language`, pero su plataforma de
  traducciones no publica `es_CU`; al solicitarlo solo se crearia el registro.

## Plan de implementacion

1. **Datos**: registro `res.lang` con `code='es_CU'`, nombre
   "Espanol (Cuba)" / "Spanish (Cuba)", activo, para que aparezca en
   Preferencias.
2. **Seed desde es_ES**: script de realce (post-install/gestion) que clona en
   la base las traducciones `es_ES -> es_CU`, de modo que toda la interfaz
   salga en espanol y no en ingles. Verificar previamente el modelo interno de
   traducciones de Odoo 19 (sucesor de `ir.translation`) y usar su API durante
   la ejecucion.
3. **Cuberismos**: `i18n/es_CU.po` con los terminos propios de la
   localizacion (ej. factura, recibo, guia de despacho, municipio, provincia;
   lista de terminos contables cubanos a confirmar) aplicados sobre el seed.
4. **Activacion**: marcar `es_CU` como idioma del usuario admin y validar la
   interfaz, informes y traducciones del modulo en la base `cuba_gob`.

## Notas

- No modifica el comportamiento del modulo; es un trabajo de idioma y
  traduccion.
- Se implementa en una fase posterior, no en F0.