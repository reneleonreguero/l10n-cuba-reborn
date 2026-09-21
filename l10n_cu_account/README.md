# Cuba - Contabilidad

Localizacion contable para Odoo 19 basada exclusivamente en la Resolucion
494/2016 del Ministerio de Finanzas y Precios, publicada en la Gaceta Oficial
No. 39 Extraordinaria de 5 de diciembre de 2016.

## Plantillas

- `cu_494_common`: base empresarial compartida, no visible en el selector.
- `cu_494_public`: empresa estatal, con Patrimonio Neto.
- `cu_494_private`: mipyme y cooperativa, con Capital Contable.

Las cuentas nominales especiales para empresas de seguro (`50.3` y `50.4`)
no se incluyen porque reutilizan los codigos de `50.1` y `50.2`. Requieren una
plantilla independiente.

## Rangos oficiales

Cuando la Resolucion publica un rango, por ejemplo `101 a 108`, la plantilla
crea una cuenta operativa con el primer codigo (`101`). Los demas codigos del
rango quedan disponibles para los desgloses internos de cada entidad.

Cuando el Nomenclador publica subcuentas obligatorias, se crean usando el
primer codigo del rango. Por ejemplo, `135.0020` corresponde a Cuentas por
Cobrar a Corto Plazo - Fuera del Organo u Organismo.

## Tributos

Los impuestos calculables en factura estan implementados:

- I. Ventas 10% (minorista, base beneficio bruto) e I. Ventas 2%
  (mayorista), con contrapartida en 440.0001;
- Retención IS 5% en compras a personas naturales (TCP), con contrapartida
  en 440.0005, de aplicación manual;
- Exento 0% neutro como impuesto de compra por defecto;
- Posición fiscal de ventas mayoristas no gravadas (I. Ventas a 0%).

No se crean como impuestos de factura las obligaciones con base anual, de
nomina o de cierre (IUE, Seguridad Social, Fuerza de Trabajo): esas van por
asientos de liquidación en una fase posterior.

## Fuente

- Gaceta Oficial: https://www.gacetaoficial.gob.cu/sites/default/files/goc-2016-ex39.pdf
- SHA-256 del PDF utilizado: `f558bb5d52719516a7a7e94f177aa5d1d1207daced939d3e453e89643c6ede2e`

Los CSV se regeneran con:

```bash
pdftotext -layout goc-2016-ex39.pdf goc39.txt
python3 tools/generate_res_494.py goc39.txt data/template
```
