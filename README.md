# Localizacion cubana para Odoo 19

Nueva localizacion cubana, desarrollada desde cero para Odoo 19 y publicada
bajo AGPL-3. El proyecto no depende de localizaciones de terceros.

## Estado

La fase F0 proporciona los datos maestros y modelos comunes:

- perfil cubano de contactos y companias;
- NIT sobre el campo fiscal estandar `vat` de Odoo;
- tipificacion de persona natural (carne de identidad) y persona juridica
  (NIT, REEUP, Registro Mercantil, licencia/RCC);
- provincias y municipios segun la DPA;
- moneda oficial CUP;
- Clasificador Nacional de Actividades Economicas (CNAE);
- registro importable del Directorio de Unidades Institucionales y
  Establecimientos (DUINE);
- directorio institucional y de sucursales bancarias.

La fase F1 incorpora `l10n_cu_account`, con el plan contable empresarial de la
Resolucion 494/2016 y variantes para empresas estatales y entidades privadas,
y `l10n_cu_account_menu`, con la aplicacion Contabilidad separada de
Facturacion (plan contable, diarios, asientos y asistente de cierre anual
contra la cuenta 999 Resultado).
La automatizacion tributaria, los informes financieros, la nomina y la
contabilidad gubernamental pertenecen a fases posteriores.

La variante de idioma Espanol de Cuba (`es_CU`) esta planeada y documentada en
`docs/`, pendiente de una fase posterior.

## Instalacion de desarrollo

El modulo esta montado en el contenedor Odoo 19 mediante
`/mnt/extra-addons/l10n-cuba-reborn`. Para instalarlo en una base nueva:

```bash
docker exec odoo-web-1 odoo -d cuba_gob -i l10n_cu_base \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons/l10n-cuba-reborn \
  --db_host=db --db_user=odoo --db_password=odoo --without-demo --stop-after-init
```

## Fuentes de datos

- Division Politico-Administrativa de Cuba: 16 provincias/municipio especial
  y 168 municipios.
- CNAE: clasificador publicado por la Oficina Nacional de Estadistica e
  Informacion (ONEI).
- DUINE: esquema del fichero oficial `duine-agosto-2026.xlsx`. Las entidades
  no se incluyen en el repositorio porque el directorio se actualiza cada mes;
  se importan desde la publicacion vigente de ONEI.
- Bancos: el modelo permite mantener instituciones y sucursales. No se copia
  el directorio heredado de 585 sucursales porque contiene duplicados y datos
  de contacto sin fecha de vigencia.

## Licencia

AGPL-3.0-only. Consulte `LICENSE`.
