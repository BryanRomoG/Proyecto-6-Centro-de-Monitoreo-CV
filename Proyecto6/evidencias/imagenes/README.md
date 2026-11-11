# Imágenes vinculadas

Las capturas seleccionadas están junto a sus eventos en
`../escenarios/<normal|baja-confianza>/<run_id>/images/`.
`image_ref` es relativo a cada paquete de escenario y `image_sha256` comprueba los bytes.
Son PNG sin pérdida de la entrada decodificada, sin cajas dibujadas ni scores incrustados.
No hay expiración automática. Las capturas locales no seleccionadas quedan en
`../../data/runtime/images/` y se excluyen de Git, sin borrarse.
