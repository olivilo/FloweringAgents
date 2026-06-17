# NOTE: superseded — the actual server code now lives in:
#   src/floweringagents_mcp/server.py
#
# This restructuring was needed for correct PyPI packaging (src-layout).
# This file is kept only so old references don't 404; it simply re-exports
# from the real location. New code should import from floweringagents_mcp.

from floweringagents_mcp.server import mcp, main  # noqa: F401

if __name__ == "__main__":
    main()
