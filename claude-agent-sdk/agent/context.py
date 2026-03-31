from contextvars import ContextVar

from agent.deps import CaseyDeps

casey_deps_var: ContextVar[CaseyDeps] = ContextVar("casey_deps")
