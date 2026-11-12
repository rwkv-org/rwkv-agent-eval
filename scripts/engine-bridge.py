#!/usr/bin/env python3
"""Expose a loopback-only inference engine to task containers.

The Pi and DSH backends run the agent inside the task container, so the engine
must be reachable from there (Harbor's terminus-2 calls it from the host). When
the engine is bound to 127.0.0.1 and restarting it is not an option, relay a
docker-bridge port to it:

    scripts/engine-bridge.py 172.17.0.1:28411 127.0.0.1:18411

Then run with --ak rwkv_url=http://127.0.0.1:18411 --ak container_url=http://172.17.0.1:28411.
Plain byte relay on one host (no TLS, no rewriting); the engine's own
--password still applies. Listens only on the address given.
"""
import asyncio
import sys


async def pipe(reader, writer):
    try:
        while data := await reader.read(1 << 16):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def main(listen, target):
    lhost, lport = listen.rsplit(':', 1)
    thost, tport = target.rsplit(':', 1)

    async def handle(cr, cw):
        try:
            tr, tw = await asyncio.open_connection(thost, int(tport))
        except OSError:
            cw.close()
            return
        await asyncio.gather(pipe(cr, tw), pipe(tr, cw))

    server = await asyncio.start_server(handle, lhost, int(lport), backlog=256)
    print(f'relay {listen} -> {target}', flush=True)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
