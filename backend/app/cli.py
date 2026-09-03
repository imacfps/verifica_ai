"""Comandos administrativos locais — sem endpoint HTTP de admin (fora de escopo).

Uso:
    python -m app.cli create-api-key --name "Cliente X"
"""

import argparse
import asyncio
import sys

from app.db.session import AsyncSessionLocal
from app.services.api_clients_service import create_client


async def _create_api_key(name: str) -> None:
    async with AsyncSessionLocal() as db:
        client, raw_key = await create_client(db, name)

    print(f"Cliente criado: {client.name} (id={client.id})")
    print("Chave de API (mostrada uma única vez — guarde agora):")
    print(f"  {raw_key}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create-api-key", help="Emite uma nova chave de API")
    create_parser.add_argument("--name", required=True, help="Nome/identificação do cliente")

    args = parser.parse_args()

    if args.command == "create-api-key":
        asyncio.run(_create_api_key(args.name))

    return 0


if __name__ == "__main__":
    sys.exit(main())
