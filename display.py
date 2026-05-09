


def print_results(data: dict) -> None:
    total = data.get("total", 0)
    items = data.get("elementList", [])

    print(f"Total de resultados: {total}")
    print(f"A mostrar {len(items)} imoveis:\n")
    print("-" * 55)

    for prop in items:
        print(f"Tipo     : {prop.get('propertyType', 'N/A').capitalize()}")
        print(f"arrendar/comprar    : {prop.get('operation', 'N/A')}")
        print(f"Preco    : {prop.get('price', 'N/A')} EUR")
        print(f"Tamanho  : {prop.get('size', 'N/A')} m2")
        print(f"Quartos  : {prop.get('rooms', 'N/A')}")
        print(f"Morada   : {prop.get('address', 'N/A')}, {prop.get('municipality', '')}")
        print(f"URL      : {prop.get('url', 'N/A')}")
        print("-" * 55)




def inspect_photos(data: dict) -> None:
    items = data.get("elementList", [])

    print("=" * 60)
    print("INSPECAO DE FOTOS POR IMOVEL")
    print("=" * 60)

    for i, prop in enumerate(items, 1):
        print(f"\nImovel #{i} — {prop.get('propertyCode')}")
        print(f"  numPhotos  : {prop.get('numPhotos', 'N/A')}")
        print(f"  thumbnail  : {prop.get('thumbnail', 'N/A')}")
        print(f"  url        : {prop.get('url', 'N/A')}")

        # Mostra todos os campos que contenham "photo", "image", "pic" ou "media"
        outros = {
            k: v for k, v in prop.items()
            if any(x in k.lower() for x in ["photo", "image", "pic", "media", "thumb", "video", "tour"])
        }
        if outros:
            print(f"  Outros campos relacionados com media:")
            for k, v in outros.items():
                print(f"    {k}: {v}")

    print("\n" + "=" * 60)
    print("CAMPOS DISPONIVEIS NO PRIMEIRO IMOVEL (todos):")
    print("=" * 60)
    if items:
        for k, v in items[0].items():
            print(f"  {k}: {v}")